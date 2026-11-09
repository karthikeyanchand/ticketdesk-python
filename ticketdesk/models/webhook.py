from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base
from .mixins import TimestampMixin


class Webhook(TimestampMixin, Base):
    __tablename__ = "webhooks"

    id: Mapped[int] = mapped_column(primary_key=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), index=True)
    url: Mapped[str] = mapped_column(String(500))
    event: Mapped[str] = mapped_column(String(50))
    signing_secret: Mapped[str] = mapped_column(String(100))
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class WebhookDelivery(TimestampMixin, Base):
    __tablename__ = "webhook_deliveries"

    id: Mapped[int] = mapped_column(primary_key=True)
    webhook_id: Mapped[int] = mapped_column(ForeignKey("webhooks.id"), index=True)
    event: Mapped[str] = mapped_column(String(50))
    payload: Mapped[str] = mapped_column(Text)
    status_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    response_excerpt: Mapped[str] = mapped_column(Text, default="")
    delivered: Mapped[bool] = mapped_column(Boolean, default=False)
