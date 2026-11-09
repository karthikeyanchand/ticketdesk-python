from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base
from .mixins import TimestampMixin


class ApiKey(TimestampMixin, Base):
    __tablename__ = "api_keys"

    id: Mapped[int] = mapped_column(primary_key=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), index=True)
    name: Mapped[str] = mapped_column(String(80))
    prefix: Mapped[str] = mapped_column(String(12), index=True)
    key_hash: Mapped[str] = mapped_column(String(128))
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
