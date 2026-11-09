from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from .mixins import TimestampMixin


class Attachment(TimestampMixin, Base):
    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(primary_key=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), index=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"), index=True)
    uploaded_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    filename: Mapped[str] = mapped_column(String(255))
    storage_path: Mapped[str] = mapped_column(String(500))
    content_type: Mapped[str] = mapped_column(String(100), default="application/octet-stream")
    size_bytes: Mapped[int] = mapped_column(Integer, default=0)

    ticket = relationship("Ticket", back_populates="attachments")
