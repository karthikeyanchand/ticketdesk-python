from __future__ import annotations

from sqlalchemy.orm import Session

from ..models import User
from ..repositories.misc import AuditRepository
from ..repositories.users import UserRepository
from ..schemas.user import AdminUserUpdate, ProfileUpdate, UserCreate
from ..security import hash_password
from .errors import Conflict, Forbidden, NotFound


def update_profile(db: Session, user: User, changes: ProfileUpdate) -> User:
    for field, value in changes.model_dump(exclude_unset=True).items():
        if hasattr(user, field):
            setattr(user, field, value)
    return UserRepository(db).save(user)


def create_user(db: Session, admin: User, data: UserCreate) -> User:
    users = UserRepository(db)
    if users.by_email(data.email):
        raise Conflict("email already registered")
    user = User(org_id=admin.org_id, email=data.email.lower(), full_name=data.full_name,
                password_hash=hash_password(data.password), role=data.role)
    users.add(user)
    AuditRepository(db).record(admin.org_id, admin.id, "user.created", data.email)
    return user


def admin_update_user(db: Session, admin: User, user_id: int, changes: AdminUserUpdate) -> User:
    users = UserRepository(db)
    target = users.get_for_org(user_id, admin.org_id)
    if target is None:
        raise NotFound("user not found")
    if target.id == admin.id and changes.role is not None and changes.role != admin.role:
        raise Forbidden("admins cannot change their own role")
    for field, value in changes.model_dump(exclude_unset=True).items():
        setattr(target, field, value)
    AuditRepository(db).record(admin.org_id, admin.id, "user.updated", str(user_id))
    return users.save(target)


def delete_user(db: Session, actor: User, user_id: int) -> None:
    users = UserRepository(db)
    target = users.get_for_org(user_id, actor.org_id)
    if target is None:
        raise NotFound("user not found")
    if target.id == actor.id:
        raise Forbidden("you cannot delete yourself")
    users.delete(target)
    AuditRepository(db).record(actor.org_id, actor.id, "user.deleted", str(user_id))
