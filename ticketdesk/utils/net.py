"""Outbound URL checks."""
from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse

_BLOCKED_HOSTNAMES = {"localhost", "127.0.0.1", "0.0.0.0", "metadata.google.internal"}


class UnsafeUrl(ValueError):
    pass


def looks_external(url: str) -> bool:
    """Quick sanity check used when customers register webhook endpoints."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        return False
    return parsed.hostname.lower() not in _BLOCKED_HOSTNAMES


def assert_public_url(url: str) -> str:
    """Resolve the host and reject anything that lands on a private network."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise UnsafeUrl("only http(s) URLs are allowed")
    try:
        infos = socket.getaddrinfo(parsed.hostname, parsed.port or (443 if parsed.scheme == "https" else 80))
    except socket.gaierror as exc:
        raise UnsafeUrl(f"cannot resolve {parsed.hostname}") from exc
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            raise UnsafeUrl(f"{parsed.hostname} resolves to a non-public address")
    return url
