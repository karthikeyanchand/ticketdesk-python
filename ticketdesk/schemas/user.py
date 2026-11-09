from pydantic import BaseModel, ConfigDict, EmailStr, Field

from ..models import Role


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    org_id: int
    email: EmailStr
    full_name: str
    role: Role
    is_active: bool
    timezone: str


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = ""
    password: str = Field(min_length=10)
    role: Role = Role.CUSTOMER


class ProfileUpdate(BaseModel):
    """Fields a user may change on their own profile.

    Unknown keys are kept so that newer clients can send preference fields
    (e.g. ``locale``) before the API formally supports them.
    """

    model_config = ConfigDict(extra="allow")

    full_name: str | None = None
    timezone: str | None = None
    signature: str | None = None


class AdminUserUpdate(BaseModel):
    full_name: str | None = None
    role: Role | None = None
    is_active: bool | None = None
