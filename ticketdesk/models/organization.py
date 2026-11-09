from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from .mixins import TimestampMixin


class Organization(TimestampMixin, Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    slug: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    plan: Mapped[str] = mapped_column(String(20), default="starter")

    users = relationship("User", back_populates="organization")
