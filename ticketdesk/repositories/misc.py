"""Repositories for the smaller tables."""
from __future__ import annotations

from sqlalchemy import select

from ..models import (ApiKey, Attachment, AuditLog, Comment, EmailTemplate, PasswordReset,
                      Webhook, WebhookDelivery)
from .base import Repository


class CommentRepository(Repository[Comment]):
    model = Comment

    def for_ticket(self, ticket_id: int, include_internal: bool) -> list[Comment]:
        stmt = select(Comment).where(Comment.ticket_id == ticket_id)
        if not include_internal:
            stmt = stmt.where(Comment.internal.is_(False))
        return list(self.db.scalars(stmt.order_by(Comment.id)))


class AttachmentRepository(Repository[Attachment]):
    model = Attachment


class WebhookRepository(Repository[Webhook]):
    model = Webhook

    def active_for_event(self, org_id: int, event: str) -> list[Webhook]:
        stmt = select(Webhook).where(Webhook.org_id == org_id, Webhook.event == event, Webhook.active.is_(True))
        return list(self.db.scalars(stmt))

    def for_org(self, org_id: int) -> list[Webhook]:
        return list(self.db.scalars(select(Webhook).where(Webhook.org_id == org_id)))


class DeliveryRepository(Repository[WebhookDelivery]):
    model = WebhookDelivery

    def pending(self, limit: int = 100) -> list[WebhookDelivery]:
        stmt = select(WebhookDelivery).where(WebhookDelivery.delivered.is_(False)).limit(limit)
        return list(self.db.scalars(stmt))


class TemplateRepository(Repository[EmailTemplate]):
    model = EmailTemplate

    def by_name(self, org_id: int, name: str) -> EmailTemplate | None:
        stmt = select(EmailTemplate).where(EmailTemplate.org_id == org_id, EmailTemplate.name == name)
        return self.db.scalars(stmt).first()


class ResetRepository(Repository[PasswordReset]):
    model = PasswordReset

    def by_token(self, token: str) -> PasswordReset | None:
        return self.db.scalars(select(PasswordReset).where(PasswordReset.token == token)).first()


class ApiKeyRepository(Repository[ApiKey]):
    model = ApiKey


class AuditRepository(Repository[AuditLog]):
    model = AuditLog

    def record(self, org_id: int, actor_id: int | None, action: str, target: str = "", detail: str = "") -> None:
        self.db.add(AuditLog(org_id=org_id, actor_id=actor_id, action=action, target=target, detail=detail))
        self.db.commit()
