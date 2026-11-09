from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..schemas.auth import (ForgotPasswordRequest, LoginRequest, ResetPasswordRequest, SignupRequest,
                            TokenResponse)
from ..services import auth_service, password_reset_service

router = APIRouter(prefix="/auth", tags=["auth"])
SESSION_COOKIE = "td_session"


def _set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        SESSION_COOKIE, token,
        max_age=settings.access_token_minutes * 60,
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax",
    )


@router.post("/signup", response_model=TokenResponse, status_code=201)
def signup(req: SignupRequest, response: Response, db: Session = Depends(get_db)):
    _, token = auth_service.signup(db, req)
    _set_session_cookie(response, token)
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, response: Response, db: Session = Depends(get_db)):
    _, token = auth_service.login(db, req.email, req.password)
    _set_session_cookie(response, token)
    return TokenResponse(access_token=token)


@router.post("/logout", status_code=204)
def logout(response: Response):
    response.delete_cookie(SESSION_COOKIE)


@router.post("/forgot-password", status_code=202)
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    password_reset_service.request_reset(db, req.email)
    return {"detail": "If that address exists, a reset link is on its way."}


@router.post("/reset-password", status_code=204)
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    password_reset_service.complete_reset(db, req.token, req.new_password)
