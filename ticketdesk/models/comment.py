from sqlalchemy import Boolean, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from .mixins import TimestampMixin


class Comment(TimestampMixin, Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"), index=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    body: Mapped[str] = mapped_column(Text)
    internal: Mapped[bool] = mapped_column(Boolean, default=False)

    ticket = relationship("Ticket", back_populates="comments")
    author = relationship("User")
