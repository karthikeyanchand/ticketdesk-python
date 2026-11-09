"""Outgoing webhooks: registration and event queueing.

Delivery happens asynchronously in ``ticketdesk.workers.dispatcher``.
"""
from __future__ import annotations

import json
import secrets
from typing import Any

from sqlalchemy.orm import Session

from ..models import User, Webhook, WebhookDelivery
from ..repositories.misc import DeliveryRepository, WebhookRepository
from ..utils.net import looks_external
from .errors import NotFound, ServiceError


def register(db: Session, admin: User, url: str, event: str) -> Webhook:
    if not looks_external(url):
        raise ServiceError("webhook URL must be a public http(s) address")
    hook = Webhook(org_id=admin.org_id, url=url, event=event, signing_secret=secrets.token_hex(24))
    return WebhookRepository(db).add(hook)


def remove(db: Session, admin: User, webhook_id: int) -> None:
    repo = WebhookRepository(db)
    hook = repo.get_for_org(webhook_id, admin.org_id)
    if hook is None:
        raise NotFound("webhook not found")
    repo.delete(hook)


def enqueue_event(db: Session, org_id: int, event: str, payload: dict[str, Any]) -> int:
    deliveries = DeliveryRepository(db)
    hooks = WebhookRepository(db).active_for_event(org_id, event)
    for hook in hooks:
        deliveries.db.add(WebhookDelivery(webhook_id=hook.id, event=event,
                                          payload=json.dumps({"event": event, "data": payload})))
    db.commit()
    return len(hooks)


def recent_deliveries(db: Session, admin: User, webhook_id: int) -> list[WebhookDelivery]:
    hook = WebhookRepository(db).get_for_org(webhook_id, admin.org_id)
    if hook is None:
        raise NotFound("webhook not found")
    return (db.query(WebhookDelivery).filter(WebhookDelivery.webhook_id == hook.id)
            .order_by(WebhookDelivery.id.desc()).limit(20).all())
