from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class SignupRequest(BaseModel):
    org_name: str = Field(min_length=2, max_length=120)
    org_slug: str = Field(pattern=r"^[a-z0-9-]{3,60}$")
    email: EmailStr
    password: str = Field(min_length=10)
    full_name: str = ""


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=10)
