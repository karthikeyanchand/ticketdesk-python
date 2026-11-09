from __future__ import annotations

from sqlalchemy.orm import Session

from ..models import Comment, Role, User
from ..repositories.misc import CommentRepository
from ..schemas.ticket import CommentCreate
from . import notification_service, ticket_service, webhook_service


def add_comment(db: Session, user: User, ticket_id: int, data: CommentCreate) -> Comment:
    ticket = ticket_service.get_ticket(db, user, ticket_id)
    internal = data.internal and user.role != Role.CUSTOMER
    comment = CommentRepository(db).add(Comment(ticket_id=ticket.id, author_id=user.id,
                                                body=data.body, internal=internal))
    if not internal:
        notification_service.notify_ticket_participants(db, ticket, comment)
        webhook_service.enqueue_event(db, ticket.org_id, "comment.created",
                                      {"ticket_id": ticket.id, "comment_id": comment.id})
    return comment


def list_comments(db: Session, user: User, ticket_id: int) -> list[Comment]:
    ticket = ticket_service.get_ticket(db, user, ticket_id)
    return CommentRepository(db).for_ticket(ticket.id, include_internal=user.role != Role.CUSTOMER)
