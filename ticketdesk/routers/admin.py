"""Organization administration: users, webhooks, email templates, API keys, import/export."""
from fastapi import APIRouter, Body, Depends, Response
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user, require_admin
from ..models import EmailTemplate, User
from ..repositories.misc import TemplateRepository, WebhookRepository
from ..repositories.users import UserRepository
from ..schemas.admin import (ApiKeyCreate, ApiKeyCreated, EmailTemplateIn, EmailTemplateOut,
                             TemplatePreviewRequest, WebhookCreate, WebhookOut)
from ..schemas.user import AdminUserUpdate, UserCreate, UserOut
from ..services import (api_key_service, export_service, import_service, notification_service, user_service,
                        webhook_service)
from ..services.errors import NotFound

router = APIRouter(prefix="/admin", tags=["admin"])


# ---- users ---------------------------------------------------------------
@router.get("/users", response_model=list[UserOut])
def list_users(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    return UserRepository(db).list_for_org(admin.org_id)


@router.post("/users", response_model=UserOut, status_code=201)
def create_user(data: UserCreate, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    return user_service.create_user(db, admin, data)


@router.patch("/users/{user_id}", response_model=UserOut)
def update_user(user_id: int, changes: AdminUserUpdate, admin: User = Depends(require_admin),
                db: Session = Depends(get_db)):
    return user_service.admin_update_user(db, admin, user_id, changes)


@router.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_service.delete_user(db, user, user_id)
    return Response(status_code=204)


# ---- webhooks ------------------------------------------------------------
@router.get("/webhooks", response_model=list[WebhookOut])
def list_webhooks(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    return WebhookRepository(db).for_org(admin.org_id)


@router.post("/webhooks", response_model=WebhookOut, status_code=201)
def create_webhook(data: WebhookCreate, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    return webhook_service.register(db, admin, data.url, data.event)


@router.delete("/webhooks/{webhook_id}", status_code=204)
def delete_webhook(webhook_id: int, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    webhook_service.remove(db, admin, webhook_id)
    return Response(status_code=204)


# ---- email templates -----------------------------------------------------
@router.put("/email-templates", response_model=EmailTemplateOut)
def upsert_template(data: EmailTemplateIn, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    repo = TemplateRepository(db)
    tpl = repo.by_name(admin.org_id, data.name)
    if tpl is None:
        return repo.add(EmailTemplate(org_id=admin.org_id, **data.model_dump()))
    tpl.subject, tpl.body = data.subject, data.body
    return repo.save(tpl)


@router.post("/email-templates/preview")
def preview_template(req: TemplatePreviewRequest, admin: User = Depends(require_admin),
                     db: Session = Depends(get_db)):
    rendered = notification_service.render_org_template(db, admin.org_id, req.name,
                                                        **notification_service.sample_context())
    if rendered is None:
        raise NotFound("no template with that name")
    return {"subject": rendered[0], "body": rendered[1]}


# ---- API keys ------------------------------------------------------------
@router.post("/api-keys", response_model=ApiKeyCreated, status_code=201)
def create_api_key(data: ApiKeyCreate, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    key, full = api_key_service.create_key(db, admin, data.name)
    return ApiKeyCreated(id=key.id, name=key.name, key=full)


# ---- import / export -----------------------------------------------------
@router.post("/import/tickets")
def import_tickets(document: str = Body(..., media_type="application/x-yaml"),
                   admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    return {"imported": import_service.import_tickets(db, admin, document)}


@router.post("/import/settings")
def import_settings(document: str = Body(..., media_type="application/x-yaml"),
                    admin: User = Depends(require_admin)):
    return {"settings": import_service.parse_settings(document)}


@router.get("/export/tickets.csv", response_class=PlainTextResponse)
def export_tickets(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    return PlainTextResponse(export_service.export_tickets_csv(db, admin), media_type="text/csv",
                             headers={"Content-Disposition": 'attachment; filename="tickets.csv"'})
