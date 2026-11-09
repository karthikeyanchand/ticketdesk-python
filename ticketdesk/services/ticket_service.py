"""Ticket lifecycle."""
from __future__ import annotations

from sqlalchemy.orm import Session

from ..models import Role, Ticket, TicketStatus, User
from ..repositories.misc import AuditRepository
from ..repositories.tickets import TicketRepository
from ..schemas.ticket import TicketCreate, TicketUpdate
from ..utils.text import normalize_tags
from . import webhook_service
from .errors import Forbidden, NotFound


def create_ticket(db: Session, user: User, data: TicketCreate) -> Ticket:
    ticket = Ticket(org_id=user.org_id, subject=data.subject, description=data.description,
                    priority=data.priority, requester_id=user.id, tags=normalize_tags(data.tags))
    TicketRepository(db).add(ticket)
    webhook_service.enqueue_event(db, user.org_id, "ticket.created", {"ticket_id": ticket.id,
                                                                       "subject": ticket.subject})
    return ticket


def list_tickets(db: Session, user: User, status: TicketStatus | None, limit: int, offset: int) -> list[Ticket]:
    requester = user.id if user.role == Role.CUSTOMER else None
    return TicketRepository(db).list_for_org(user.org_id, status=status, requester_id=requester,
                                             limit=limit, offset=offset)


def get_ticket(db: Session, user: User, ticket_id: int) -> Ticket:
    ticket = TicketRepository(db).get(ticket_id)
    if ticket is None:
        raise NotFound("ticket not found")
    if user.role == Role.CUSTOMER and ticket.requester_id != user.id:
        raise Forbidden("not your ticket")
    return ticket


def get_ticket_for_org(db: Session, org_id: int, ticket_id: int) -> Ticket:
    ticket = TicketRepository(db).get_for_org(ticket_id, org_id)
    if ticket is None:
        raise NotFound("ticket not found")
    return ticket


def update_ticket(db: Session, user: User, ticket_id: int, changes: TicketUpdate) -> Ticket:
    ticket = get_ticket(db, user, ticket_id)
    data = changes.model_dump(exclude_unset=True)
    if user.role == Role.CUSTOMER:
        # customers may only close or reopen their own tickets
        data = {k: v for k, v in data.items() if k == "status"}
    for field, value in data.items():
        setattr(ticket, field, value)
    TicketRepository(db).save(ticket)
    AuditRepository(db).record(user.org_id, user.id, "ticket.updated", str(ticket.id), ",".join(data))
    webhook_service.enqueue_event(db, ticket.org_id, "ticket.updated", {"ticket_id": ticket.id, **{
        k: str(v) for k, v in data.items()}})
    return ticket
