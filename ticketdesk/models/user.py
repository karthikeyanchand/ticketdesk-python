import enum

from sqlalchemy import Boolean, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from .mixins import TimestampMixin


class Role(str, enum.Enum):
    CUSTOMER = "customer"
    AGENT = "agent"
    ADMIN = "admin"


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(120), default="")
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.CUSTOMER)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    timezone: Mapped[str] = mapped_column(String(64), default="UTC")
    signature: Mapped[str] = mapped_column(String(500), default="")

    organization = relationship("Organization", back_populates="users")

    @property
    def is_staff(self) -> bool:
        return self.role in (Role.AGENT, Role.ADMIN)
