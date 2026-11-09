"""FastAPI dependencies for authentication and authorization."""
from __future__ import annotations

from collections.abc import Callable

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .database import get_db
from .models import Role, User
from .security import decode_access_token

_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    if creds is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "missing bearer token")
    try:
        claims = decode_access_token(creds.credentials)
    except jwt.PyJWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid token")
    user = db.get(User, int(claims["sub"]))
    if user is None or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "inactive user")
    return user


def require_roles(*roles: Role) -> Callable[[User], User]:
    def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "insufficient role")
        return user

    return checker


require_staff = require_roles(Role.AGENT, Role.ADMIN)
require_admin = require_roles(Role.ADMIN)
