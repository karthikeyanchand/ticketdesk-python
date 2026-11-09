from __future__ import annotations

from sqlalchemy.orm import Session

from ..models import User
from ..repositories.reports import ReportRepository

# Friendly sort names exposed in the UI, mapped to SQL expressions.
SORT_FIELDS = {
    "open": "open_tickets DESC",
    "urgent": "urgent_tickets DESC",
    "oldest": "oldest_open_days DESC",
    "name": "assignee ASC",
}


def sla_report(db: Session, user: User, sort: str = "open") -> list[dict]:
    # Fall back to the raw value so power users can pass e.g. "open_tickets ASC".
    order_by = SORT_FIELDS.get(sort, sort)
    return ReportRepository(db).sla_by_assignee(user.org_id, order_by)


def volume_report(db: Session, user: User, days: int = 30) -> list[dict]:
    return ReportRepository(db).tickets_per_day(user.org_id, max(1, min(days, 365)))
