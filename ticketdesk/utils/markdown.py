"""A deliberately tiny markdown subset for ticket comments: paragraphs, **bold**, `code` and links."""
from __future__ import annotations

import re

_BOLD = re.compile(r"\*\*(.+?)\*\*")
_CODE = re.compile(r"`([^`]+)`")
_LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")


def render(text: str) -> str:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    html = []
    for p in paragraphs:
        p = _BOLD.sub(r"<strong>\1</strong>", p)
        p = _CODE.sub(r"<code>\1</code>", p)
        p = _LINK.sub(r'<a href="\2" rel="nofollow">\1</a>', p)
        html.append(f"<p>{p.replace(chr(10), '<br>')}</p>")
    return "\n".join(html)
