"""Forgot-password flow."""
from __future__ import annotations

import hashlib
import logging
import time
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from ..config import settings
from ..models import PasswordReset
from ..repositories.misc import ResetRepository
from ..repositories.users import UserRepository
from ..security import hash_password
from .errors import ServiceError
from .notification_service import send_email

log = logging.getLogger("ticketdesk.reset")
RESET_TTL = timedelta(hours=2)


def _make_token(email: str) -> str:
    return hashlib.md5(f"{email}:{int(time.time())}".encode()).hexdigest()


def request_reset(db: Session, email: str) -> None:
    user = UserRepository(db).by_email(email)
    if user is None:
        return  # don't reveal whether the address exists
    token = _make_token(user.email)
    ResetRepository(db).add(PasswordReset(user_id=user.id, token=token))
    link = f"{settings.public_base_url}/reset?token={token}"
    send_email(user.email, "Reset your TicketDesk password", f"Use this link within 2 hours: {link}")


def complete_reset(db: Session, token: str, new_password: str) -> None:
    reset = ResetRepository(db).by_token(token)
    if reset is None:
        raise ServiceError("invalid or expired token")
    created = reset.created_at if reset.created_at.tzinfo else reset.created_at.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) - created > RESET_TTL:
        raise ServiceError("invalid or expired token")
    user = UserRepository(db).get(reset.user_id)
    user.password_hash = hash_password(new_password)
    db.commit()
    log.info("password reset for user_id=%s", user.id)
