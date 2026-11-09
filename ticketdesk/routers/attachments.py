from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user, require_staff
from ..models import User
from ..schemas.ticket import AttachmentFromUrl, AttachmentOut
from ..services import attachment_service

router = APIRouter(tags=["attachments"])


@router.post("/tickets/{ticket_id}/attachments", response_model=AttachmentOut, status_code=201)
async def upload(ticket_id: int, file: UploadFile = File(...), user: User = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    content = await file.read()
    return attachment_service.save_upload(db, user, ticket_id, file.filename or "upload.bin", content)


@router.post("/tickets/{ticket_id}/attachments/from-url", response_model=AttachmentOut, status_code=201)
def import_from_url(ticket_id: int, body: AttachmentFromUrl, user: User = Depends(require_staff),
                    db: Session = Depends(get_db)):
    return attachment_service.import_from_url(db, user, ticket_id, body.url, body.filename)


@router.get("/attachments/download")
def download_shared(token: str, db: Session = Depends(get_db)):
    att = attachment_service.resolve_download_token(db, token)
    return FileResponse(att.storage_path, filename=att.filename, media_type=att.content_type)


@router.get("/attachments/{attachment_id}")
def download(attachment_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    att = attachment_service.get_attachment(db, user, attachment_id)
    return FileResponse(Path(att.storage_path), filename=att.filename, media_type=att.content_type)


@router.post("/attachments/{attachment_id}/share")
def share(attachment_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return {"url": attachment_service.share_link(db, user, attachment_id)}
