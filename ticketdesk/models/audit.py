from typing import Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base
from .mixins import TimestampMixin


class AuditLog(TimestampMixin, Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), index=True)
    actor_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(80))
    target: Mapped[str] = mapped_column(String(120), default="")
    detail: Mapped[str] = mapped_column(Text, default="")
