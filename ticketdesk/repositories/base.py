"""Small generic repository helpers shared by the concrete repositories."""
from __future__ import annotations

from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import Base

ModelT = TypeVar("ModelT", bound=Base)


class Repository(Generic[ModelT]):
    model: type[ModelT]

    def __init__(self, db: Session):
        self.db = db

    def get(self, obj_id: int) -> ModelT | None:
        return self.db.get(self.model, obj_id)

    def get_for_org(self, obj_id: int, org_id: int) -> ModelT | None:
        stmt = select(self.model).where(self.model.id == obj_id, self.model.org_id == org_id)
        return self.db.scalars(stmt).first()

    def add(self, obj: ModelT) -> ModelT:
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def save(self, obj: ModelT) -> ModelT:
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, obj: ModelT) -> None:
        self.db.delete(obj)
        self.db.commit()
