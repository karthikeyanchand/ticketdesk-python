from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base
from .mixins import TimestampMixin


class PasswordReset(TimestampMixin, Base):
    __tablename__ = "password_resets"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    token: Mapped[str] = mapped_column(String(64), index=True)
    used: Mapped[bool] = mapped_column(Boolean, default=False)
