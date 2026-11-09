"""Server-rendered customer portal (browser pages, cookie session)."""
from pathlib import Path

import jwt
from fastapi import APIRouter, Cookie, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Role, User
from ..repositories.misc import CommentRepository
from ..security import decode_access_token
from ..services import ticket_service
from ..utils import markdown

router = APIRouter(prefix="/portal", tags=["portal"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))


def portal_user(td_session: str | None = Cookie(default=None), db: Session = Depends(get_db)) -> User:
    if not td_session:
        raise HTTPException(401, "please sign in")
    try:
        claims = decode_access_token(td_session)
    except jwt.PyJWTError:
        raise HTTPException(401, "session expired")
    user = db.get(User, int(claims["sub"]))
    if user is None or not user.is_active:
        raise HTTPException(401, "please sign in")
    return user


@router.get("/tickets/{ticket_id}", response_class=HTMLResponse)
def ticket_page(ticket_id: int, request: Request, user: User = Depends(portal_user), db: Session = Depends(get_db)):
    ticket = ticket_service.get_ticket_for_org(db, user.org_id, ticket_id)
    if user.role == Role.CUSTOMER and ticket.requester_id != user.id:
        raise HTTPException(404, "ticket not found")
    comments = CommentRepository(db).for_ticket(ticket.id, include_internal=user.role != Role.CUSTOMER)
    for c in comments:
        c.html = markdown.render(c.body)
    return templates.TemplateResponse(request, "portal/ticket.html", {"ticket": ticket, "comments": comments})
