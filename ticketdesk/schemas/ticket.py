from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from ..models import TicketPriority, TicketStatus


class TicketCreate(BaseModel):
    subject: str = Field(min_length=3, max_length=200)
    description: str = ""
    priority: TicketPriority = TicketPriority.NORMAL
    tags: list[str] = []


class TicketUpdate(BaseModel):
    subject: str | None = None
    status: TicketStatus | None = None
    priority: TicketPriority | None = None
    assignee_id: int | None = None


class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    org_id: int
    subject: str
    description: str
    status: TicketStatus
    priority: TicketPriority
    requester_id: int
    assignee_id: int | None
    tags: str
    created_at: datetime


class CommentCreate(BaseModel):
    body: str = Field(min_length=1, max_length=20_000)
    internal: bool = False


class CommentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_id: int
    author_id: int
    body: str
    internal: bool
    created_at: datetime


class AttachmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_id: int
    filename: str
    content_type: str
    size_bytes: int


class AttachmentFromUrl(BaseModel):
    url: str
    filename: str | None = None
