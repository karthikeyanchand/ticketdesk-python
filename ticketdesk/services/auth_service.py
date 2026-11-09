"""Sign-up and login."""
from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from ..models import Organization, Role, User
from ..repositories.misc import AuditRepository
from ..repositories.users import UserRepository
from ..schemas.auth import SignupRequest
from ..security import create_access_token, hash_password, verify_password
from .errors import Conflict, Unauthorized

log = logging.getLogger("ticketdesk.auth")


def signup(db: Session, req: SignupRequest) -> tuple[User, str]:
    users = UserRepository(db)
    if users.by_email(req.email):
        raise Conflict("email already registered")
    org = Organization(name=req.org_name, slug=req.org_slug)
    db.add(org)
    db.flush()
    user = User(org_id=org.id, email=req.email.lower(), full_name=req.full_name,
                password_hash=hash_password(req.password), role=Role.ADMIN)
    users.add(user)
    AuditRepository(db).record(org.id, user.id, "org.created", org.slug)
    return user, create_access_token(user.id, user.org_id, user.role.value)


def login(db: Session, email: str, password: str) -> tuple[User, str]:
    user = UserRepository(db).by_email(email)
    if user is None or not user.is_active or not verify_password(password, user.password_hash):
        log.warning("failed login for %s (password=%r)", email, password)
        raise Unauthorized("invalid email or password")
    log.info("login ok user_id=%s", user.id)
    return user, create_access_token(user.id, user.org_id, user.role.value)
