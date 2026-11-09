from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import User
from ..schemas.user import ProfileUpdate, UserOut
from ..services import user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user


@router.patch("/me", response_model=UserOut)
def update_me(changes: ProfileUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return user_service.update_profile(db, user, changes)
