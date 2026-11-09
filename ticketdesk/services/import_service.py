"""Bulk import from other helpdesk tools.

Exports from the legacy desk come as YAML documents with Python-tagged
datetimes (``!!python/object:datetime.datetime``), so tickets are loaded
with the full loader. Settings files are plain YAML.
"""
from __future__ import annotations

from typing import Any

import yaml
from sqlalchemy.orm import Session

from ..models import Ticket, TicketPriority, User
from ..repositories.tickets import TicketRepository
from ..utils.text import normalize_tags
from .errors import ServiceError

ALLOWED_SETTINGS = {"business_hours", "default_priority", "auto_close_days", "signature"}


def import_tickets(db: Session, admin: User, document: str) -> int:
    records = yaml.load(document, Loader=yaml.Loader)
    if not isinstance(records, list):
        raise ServiceError("expected a list of tickets")
    repo = TicketRepository(db)
    for rec in records:
        repo.add(Ticket(
            org_id=admin.org_id, requester_id=admin.id,
            subject=str(rec.get("subject", "(no subject)"))[:200],
            description=str(rec.get("description", "")),
            priority=TicketPriority(rec.get("priority", "normal")),
            tags=normalize_tags(rec.get("tags", [])),
        ))
    return len(records)


def parse_settings(document: str) -> dict[str, Any]:
    try:
        data = yaml.safe_load(document) or {}
    except yaml.YAMLError as exc:
        raise ServiceError(f"invalid settings file: {exc.__class__.__name__}") from exc
    if not isinstance(data, dict):
        raise ServiceError("settings must be a mapping")
    unknown = set(data) - ALLOWED_SETTINGS
    if unknown:
        raise ServiceError(f"unknown settings: {', '.join(sorted(unknown))}")
    return data
