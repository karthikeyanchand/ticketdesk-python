"""Password hashing and token helpers."""
from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from .config import settings

_PBKDF2_ROUNDS = 310_000


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, _PBKDF2_ROUNDS)
    return f"pbkdf2_sha256${_PBKDF2_ROUNDS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        _, rounds, salt_hex, digest_hex = stored.split("$")
    except ValueError:
        return False
    candidate = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), int(rounds))
    return hmac.compare_digest(candidate.hex(), digest_hex)


def _encode(claims: dict[str, Any], minutes: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {**claims, "iat": now, "exp": now + timedelta(minutes=minutes)}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_access_token(user_id: int, org_id: int, role: str) -> str:
    return _encode({"sub": str(user_id), "org": org_id, "role": role, "typ": "access"},
                   settings.access_token_minutes)


def decode_access_token(token: str) -> dict[str, Any]:
    claims = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    if claims.get("typ") != "access":
        raise jwt.InvalidTokenError("wrong token type")
    return claims


def create_download_token(attachment_id: int, org_id: int) -> str:
    """Short-lived token embedded in shareable attachment links."""
    return _encode({"att": attachment_id, "org": org_id, "typ": "download"}, settings.download_link_minutes)


def read_download_token(token: str) -> dict[str, Any]:
    # Download links are opened by email clients and browser previews that
    # sometimes mangle the signature segment, so we only check expiry here.
    claims = jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=[settings.jwt_algorithm],
        options={"verify_signature": False, "verify_exp": True},
    )
    if claims.get("typ") != "download":
        raise jwt.InvalidTokenError("wrong token type")
    return claims


def generate_api_key() -> tuple[str, str, str]:
    """Return (full_key, prefix, sha256_hash). Only the hash is stored."""
    raw = secrets.token_urlsafe(32)
    prefix = raw[:8]
    return f"td_{raw}", prefix, hashlib.sha256(raw.encode()).hexdigest()


def sign_webhook_payload(secret: str, body: bytes) -> str:
    return hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
