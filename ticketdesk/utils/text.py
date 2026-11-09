from __future__ import annotations

import re

_TAG_SPLIT = re.compile(r"[,\s]+")


def normalize_tags(tags: list[str]) -> str:
    cleaned = sorted({t.strip().lower() for t in tags if t.strip()})
    return ",".join(cleaned)[:300]


def parse_tags(raw: str) -> list[str]:
    return [t for t in _TAG_SPLIT.split(raw or "") if t]


def excerpt(text: str, length: int = 140) -> str:
    text = " ".join(text.split())
    return text if len(text) <= length else text[: length - 1] + "…"
