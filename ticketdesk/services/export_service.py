"""CSV export of tickets for spreadsheet users."""
from __future__ import annotations

import csv
import io

from sqlalchemy.orm import Session

from ..models import User
from ..repositories.tickets import TicketRepository

COLUMNS = ["id", "subject", "status", "priority", "requester", "assignee", "tags", "created_at"]


def export_tickets_csv(db: Session, user: User) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(COLUMNS)
    for t in TicketRepository(db).list_for_org(user.org_id, limit=10_000):
        writer.writerow([
            t.id,
            t.subject,
            t.status.value,
            t.priority.value,
            t.requester.email if t.requester else "",
            t.assignee.email if t.assignee else "",
            t.tags,
            t.created_at.isoformat(),
        ])
    return buf.getvalue()
