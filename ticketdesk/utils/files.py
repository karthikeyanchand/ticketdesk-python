"""Helpers for attachment storage on local disk."""
from __future__ import annotations

import mimetypes
import uuid
from pathlib import Path

from ..config import settings


def org_storage_dir(org_id: int) -> Path:
    path = settings.storage_dir / f"org_{org_id}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def build_storage_path(org_id: int, ticket_id: int, filename: str) -> Path:
    """Keep the customer's original filename so downloads look familiar."""
    folder = org_storage_dir(org_id) / f"ticket_{ticket_id}"
    folder.mkdir(parents=True, exist_ok=True)
    return folder / filename


def random_storage_path(org_id: int, suffix: str = "") -> Path:
    return org_storage_dir(org_id) / f"{uuid.uuid4().hex}{suffix}"


def guess_content_type(filename: str) -> str:
    return mimetypes.guess_type(filename)[0] or "application/octet-stream"
