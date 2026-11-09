"""Runtime configuration, read from environment variables."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    app_name: str = "TicketDesk"
    environment: str = field(default_factory=lambda: os.getenv("TICKETDESK_ENV", "development"))
    database_url: str = field(
        default_factory=lambda: os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'data' / 'ticketdesk.db'}")
    )
    storage_dir: Path = field(
        default_factory=lambda: Path(os.getenv("STORAGE_DIR", str(BASE_DIR / "data" / "attachments")))
    )
    export_dir: Path = field(
        default_factory=lambda: Path(os.getenv("EXPORT_DIR", str(BASE_DIR / "data" / "exports")))
    )
    jwt_secret: str = field(default_factory=lambda: os.getenv("JWT_SECRET", "ticketdesk-dev-secret"))
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = field(default_factory=lambda: int(os.getenv("ACCESS_TOKEN_MINUTES", "60")))
    download_link_minutes: int = 15
    max_upload_bytes: int = 10 * 1024 * 1024
    webhook_timeout_seconds: float = 5.0
    virus_scan_enabled: bool = field(default_factory=lambda: _env_bool("VIRUS_SCAN_ENABLED", False))
    public_base_url: str = field(default_factory=lambda: os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:8000"))


settings = Settings()
