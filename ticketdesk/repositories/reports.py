"""Reporting queries. These are hand-written SQL for performance on large orgs."""
from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session

_SLA_QUERY = """
SELECT u.full_name AS assignee,
       COUNT(*) AS open_tickets,
       SUM(CASE WHEN t.priority = 'URGENT' THEN 1 ELSE 0 END) AS urgent_tickets,
       MAX(julianday('now') - julianday(t.created_at)) AS oldest_open_days
FROM tickets t
LEFT JOIN users u ON u.id = t.assignee_id
WHERE t.org_id = :org_id AND t.status IN ('OPEN', 'PENDING')
GROUP BY u.full_name
ORDER BY {order_by}
"""


class ReportRepository:
    def __init__(self, db: Session):
        self.db = db

    def sla_by_assignee(self, org_id: int, order_by: str) -> list[dict]:
        rows = self.db.execute(text(_SLA_QUERY.format(order_by=order_by)), {"org_id": org_id})
        return [dict(r._mapping) for r in rows]

    def tickets_per_day(self, org_id: int, days: int) -> list[dict]:
        rows = self.db.execute(
            text(
                "SELECT date(created_at) AS day, COUNT(*) AS created FROM tickets "
                "WHERE org_id = :org_id AND created_at >= date('now', :window) "
                "GROUP BY day ORDER BY day"
            ),
            {"org_id": org_id, "window": f"-{int(days)} days"},
        )
        return [dict(r._mapping) for r in rows]
