from __future__ import annotations

from sqlalchemy.orm import Session

from ..models import Role, Ticket, User
from ..repositories.tickets import TicketRepository


def search_tickets(db: Session, user: User, query: str) -> list[Ticket]:
    query = query.strip()
    if len(query) < 2:
        return []
    results = TicketRepository(db).search(user.org_id, query)
    if user.role == Role.CUSTOMER:
        results = [t for t in results if t.requester_id == user.id]
    return results
