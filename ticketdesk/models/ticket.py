import enum
from typing import Optional

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from .mixins import TimestampMixin


class TicketStatus(str, enum.Enum):
    OPEN = "open"
    PENDING = "pending"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketPriority(str, enum.Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class Ticket(TimestampMixin, Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), index=True)
    subject: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[TicketStatus] = mapped_column(Enum(TicketStatus), default=TicketStatus.OPEN)
    priority: Mapped[TicketPriority] = mapped_column(Enum(TicketPriority), default=TicketPriority.NORMAL)
    requester_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    assignee_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    tags: Mapped[str] = mapped_column(String(300), default="")

    requester = relationship("User", foreign_keys=[requester_id])
    assignee = relationship("User", foreign_keys=[assignee_id])
    comments = relationship("Comment", back_populates="ticket", order_by="Comment.id")
    attachments = relationship("Attachment", back_populates="ticket")
