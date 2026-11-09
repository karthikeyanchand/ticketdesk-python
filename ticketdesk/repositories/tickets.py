from __future__ import annotations

from sqlalchemy import func, select

from ..models import Ticket, TicketStatus
from .base import Repository


class TicketRepository(Repository[Ticket]):
    model = Ticket

    def list_for_org(
        self,
        org_id: int,
        *,
        status: TicketStatus | None = None,
        requester_id: int | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Ticket]:
        stmt = select(Ticket).where(Ticket.org_id == org_id)
        if status is not None:
            stmt = stmt.where(Ticket.status == status)
        if requester_id is not None:
            stmt = stmt.where(Ticket.requester_id == requester_id)
        stmt = stmt.order_by(Ticket.id.desc()).limit(limit).offset(offset)
        return list(self.db.scalars(stmt))

    def count_open(self, org_id: int) -> int:
        stmt = select(func.count()).select_from(Ticket).where(
            Ticket.org_id == org_id, Ticket.status.in_([TicketStatus.OPEN, TicketStatus.PENDING])
        )
        return self.db.scalar(stmt) or 0

    def search(self, org_id: int, term: str, limit: int = 25) -> list[Ticket]:
        pattern = f"%{term}%"
        stmt = (
            select(Ticket)
            .where(Ticket.org_id == org_id)
            .where(Ticket.subject.ilike(pattern) | Ticket.description.ilike(pattern))
            .order_by(Ticket.id.desc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt))
