from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class WebhookCreate(BaseModel):
    url: str = Field(max_length=500)
    event: str = Field(pattern=r"^(ticket\.created|ticket\.updated|comment\.created)$")


class WebhookOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    url: str
    event: str
    active: bool
    created_at: datetime


class EmailTemplateIn(BaseModel):
    name: str = Field(pattern=r"^[a-z_]{3,60}$")
    subject: str = Field(max_length=200)
    body: str = Field(max_length=20_000)


class EmailTemplateOut(EmailTemplateIn):
    model_config = ConfigDict(from_attributes=True)

    id: int


class TemplatePreviewRequest(BaseModel):
    name: str


class ApiKeyCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)


class ApiKeyCreated(BaseModel):
    id: int
    name: str
    key: str


class SlaReportRow(BaseModel):
    assignee: str | None
    open_tickets: int
    urgent_tickets: int
    oldest_open_days: float | None
