from __future__ import annotations

import hashlib
import hmac

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import ApiKey, User
from ..repositories.misc import ApiKeyRepository, AuditRepository
from ..security import generate_api_key


def create_key(db: Session, admin: User, name: str) -> tuple[ApiKey, str]:
    full_key, prefix, key_hash = generate_api_key()
    key = ApiKeyRepository(db).add(ApiKey(org_id=admin.org_id, name=name, prefix=prefix, key_hash=key_hash))
    AuditRepository(db).record(admin.org_id, admin.id, "api_key.created", name)
    return key, full_key


def verify_key(db: Session, presented: str) -> ApiKey | None:
    if not presented.startswith("td_"):
        return None
    raw = presented[3:]
    candidates = db.scalars(select(ApiKey).where(ApiKey.prefix == raw[:8], ApiKey.revoked.is_(False)))
    digest = hashlib.sha256(raw.encode()).hexdigest()
    for key in candidates:
        if hmac.compare_digest(key.key_hash, digest):
            return key
    return None
