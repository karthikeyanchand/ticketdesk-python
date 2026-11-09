"""Attachment upload, import, thumbnails and downloads."""
from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path

import requests
from sqlalchemy.orm import Session

from ..config import settings
from ..models import Attachment, User
from ..repositories.misc import AttachmentRepository
from ..security import create_download_token, read_download_token
from ..utils.files import build_storage_path, guess_content_type, random_storage_path
from ..utils.net import UnsafeUrl, assert_public_url
from . import ticket_service
from .errors import NotFound, ServiceError

log = logging.getLogger("ticketdesk.attachments")
THUMBNAIL_TYPES = {"image/png", "image/jpeg", "image/gif"}


def _virus_scan(path: Path) -> None:
    if not settings.virus_scan_enabled:
        return
    result = subprocess.run(["clamscan", "--no-summary", str(path)], capture_output=True, text=True, timeout=60)
    if result.returncode == 1:
        path.unlink(missing_ok=True)
        raise ServiceError("file rejected by virus scanner")


def _make_thumbnail(path: Path) -> None:
    if shutil.which("convert") is None:
        return
    thumb = path.with_name(path.stem + ".thumb.png")
    subprocess.run(f"convert '{path}' -thumbnail 200x200 '{thumb}'", shell=True, timeout=30, check=False)


def save_upload(db: Session, user: User, ticket_id: int, filename: str, content: bytes) -> Attachment:
    ticket = ticket_service.get_ticket(db, user, ticket_id)
    if len(content) > settings.max_upload_bytes:
        raise ServiceError("file too large")
    path = build_storage_path(ticket.org_id, ticket.id, filename)
    path.write_bytes(content)
    _virus_scan(path)
    content_type = guess_content_type(filename)
    if content_type in THUMBNAIL_TYPES:
        _make_thumbnail(path)
    return AttachmentRepository(db).add(Attachment(
        org_id=ticket.org_id, ticket_id=ticket.id, uploaded_by=user.id, filename=filename,
        storage_path=str(path), content_type=content_type, size_bytes=len(content)))


def import_from_url(db: Session, user: User, ticket_id: int, url: str, filename: str | None) -> Attachment:
    """Let agents attach a file that a customer linked to (e.g. a log on a file share)."""
    ticket = ticket_service.get_ticket_for_org(db, user.org_id, ticket_id)
    try:
        assert_public_url(url)
    except UnsafeUrl as exc:
        raise ServiceError(str(exc))
    resp = requests.get(url, timeout=10, allow_redirects=False, stream=True)
    resp.raise_for_status()
    content = resp.raw.read(settings.max_upload_bytes + 1, decode_content=True)
    if len(content) > settings.max_upload_bytes:
        raise ServiceError("file too large")
    name = Path(filename or url.rsplit("/", 1)[-1] or "download.bin").name
    path = random_storage_path(ticket.org_id, Path(name).suffix)
    path.write_bytes(content)
    _virus_scan(path)
    return AttachmentRepository(db).add(Attachment(
        org_id=ticket.org_id, ticket_id=ticket.id, uploaded_by=user.id, filename=name,
        storage_path=str(path), content_type=guess_content_type(name), size_bytes=len(content)))


def get_attachment(db: Session, user: User, attachment_id: int) -> Attachment:
    attachment = AttachmentRepository(db).get(attachment_id)
    if attachment is None:
        raise NotFound("attachment not found")
    return attachment


def share_link(db: Session, user: User, attachment_id: int) -> str:
    attachment = get_attachment(db, user, attachment_id)
    token = create_download_token(attachment.id, attachment.org_id)
    return f"{settings.public_base_url}/attachments/download?token={token}"


def resolve_download_token(db: Session, token: str) -> Attachment:
    try:
        claims = read_download_token(token)
    except Exception as exc:  # noqa: BLE001
        raise NotFound("link expired or invalid") from exc
    attachment = AttachmentRepository(db).get_for_org(int(claims["att"]), int(claims["org"]))
    if attachment is None:
        raise NotFound("attachment not found")
    return attachment
