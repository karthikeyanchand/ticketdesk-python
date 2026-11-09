from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user, require_staff
from ..models import TicketStatus, User
from ..schemas.ticket import CommentCreate, CommentOut, TicketCreate, TicketOut, TicketUpdate
from ..services import comment_service, search_service, ticket_service
from ..utils.pagination import Page

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("", response_model=list[TicketOut])
def list_tickets(status: TicketStatus | None = None, page: Page = Depends(),
                 user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ticket_service.list_tickets(db, user, status, page.limit, page.offset)


@router.post("", response_model=TicketOut, status_code=201)
def create_ticket(data: TicketCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ticket_service.create_ticket(db, user, data)


@router.get("/search", response_model=list[TicketOut])
def search(q: str = Query(min_length=2, max_length=100), user: User = Depends(get_current_user),
           db: Session = Depends(get_db)):
    return search_service.search_tickets(db, user, q)


@router.get("/{ticket_id}", response_model=TicketOut)
def get_ticket(ticket_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ticket_service.get_ticket(db, user, ticket_id)


@router.patch("/{ticket_id}", response_model=TicketOut)
def update_ticket(ticket_id: int, changes: TicketUpdate, user: User = Depends(require_staff),
                  db: Session = Depends(get_db)):
    return ticket_service.update_ticket(db, user, ticket_id, changes)


@router.get("/{ticket_id}/comments", response_model=list[CommentOut])
def list_comments(ticket_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return comment_service.list_comments(db, user, ticket_id)


@router.post("/{ticket_id}/comments", response_model=CommentOut, status_code=201)
def add_comment(ticket_id: int, data: CommentCreate, user: User = Depends(get_current_user),
                db: Session = Depends(get_db)):
    return comment_service.add_comment(db, user, ticket_id, data)
