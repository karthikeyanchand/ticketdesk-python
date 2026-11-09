from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base
from .mixins import TimestampMixin


class EmailTemplate(TimestampMixin, Base):
    """Per-organization customisation of notification emails."""

    __tablename__ = "email_templates"
    __table_args__ = (UniqueConstraint("org_id", "name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), index=True)
    name: Mapped[str] = mapped_column(String(60))
    subject: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text)
