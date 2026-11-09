"""Email notifications.

System templates ship with the app (``ticketdesk/templates/email``). Each
organization can override them from the admin console; overrides are stored in
the ``email_templates`` table and rendered with the same variables.
"""
from __future__ import annotations

import logging
from typing import Any

from jinja2 import Environment, PackageLoader, Template, select_autoescape
from sqlalchemy.orm import Session

from ..models import Comment, Ticket
from ..repositories.misc import TemplateRepository

log = logging.getLogger("ticketdesk.notify")

_system_env = Environment(
    loader=PackageLoader("ticketdesk", "templates/email"),
    autoescape=select_autoescape(["html"]),
)

OUTBOX: list[dict[str, str]] = []  # replaced by an SMTP sender in production


def send_email(to: str, subject: str, body: str) -> None:
    OUTBOX.append({"to": to, "subject": subject, "body": body})
    log.info("queued email to=%s subject=%r", to, subject)


def render_system_template(name: str, **context: Any) -> str:
    return _system_env.get_template(f"{name}.txt").render(**context)


def render_org_template(db: Session, org_id: int, name: str, **context: Any) -> tuple[str, str] | None:
    override = TemplateRepository(db).by_name(org_id, name)
    if override is None:
        return None
    return Template(override.subject).render(**context), Template(override.body).render(**context)


def sample_context() -> dict[str, Any]:
    return {"ticket": {"id": 1042, "subject": "Printer on fire", "status": "open"},
            "comment": {"body": "Have you tried turning it off and on again?"},
            "recipient": {"full_name": "Sam Example"}}


def notify_ticket_participants(db: Session, ticket: Ticket, comment: Comment) -> None:
    recipients = {u for u in (ticket.requester, ticket.assignee) if u and u.id != comment.author_id}
    for user in recipients:
        ctx = {"ticket": ticket, "comment": comment, "recipient": user}
        rendered = render_org_template(db, ticket.org_id, "comment_added", **ctx)
        if rendered is None:
            rendered = (f"[#{ticket.id}] New reply: {ticket.subject}",
                        render_system_template("comment_added", **ctx))
        send_email(user.email, *rendered)
