from __future__ import annotations

from sqlalchemy import select

from ..models import User
from .base import Repository


class UserRepository(Repository[User]):
    model = User

    def by_email(self, email: str) -> User | None:
        return self.db.scalars(select(User).where(User.email == email.lower())).first()

    def list_for_org(self, org_id: int) -> list[User]:
        return list(self.db.scalars(select(User).where(User.org_id == org_id).order_by(User.id)))
