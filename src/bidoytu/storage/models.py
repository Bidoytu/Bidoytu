"""Plain data structures passed between the proxy engine, storage, and UI.

These are intentionally framework-free (no Qt, no mitmproxy types) so they can
cross thread boundaries cheaply and be persisted without adaptation.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(slots=True)
class FlowRecord:
    """A single captured HTTP request/response exchange.

    Body payloads are represented in one of two ways depending on size:
        - inline: ``*_body_inline`` holds the bytes directly.
        - file:   ``*_body_path`` holds a path (relative to the body store)
                  and ``*_body_inline`` is ``None``.

    Exactly one of the two is set per body (or neither, when there is no body).
    """

    # Identity / correlation. ``flow_id`` is mitmproxy's flow uuid; ``id`` is
    # the SQLite primary key (assigned on insert).
    flow_id: str
    id: Optional[int] = None

    # Request line + metadata.
    method: str = ""
    scheme: str = ""
    host: str = ""
    port: int = 0
    path: str = ""
    http_version: str = ""
    request_headers: str = ""  # serialized (e.g. raw header block)
    request_body_inline: Optional[bytes] = None
    request_body_path: Optional[str] = None
    request_body_size: int = 0

    # Response metadata (populated once the response arrives).
    status_code: Optional[int] = None
    reason: str = ""
    response_headers: str = ""
    response_body_inline: Optional[bytes] = None
    response_body_path: Optional[str] = None
    response_body_size: int = 0
    content_type: str = ""

    # Timing (unix epoch seconds).
    started_at: float = 0.0
    completed_at: Optional[float] = None

    # Convenience.
    tags: str = ""
    notes: str = ""

    @property
    def url(self) -> str:
        if not self.host:
            return self.path
        netloc = self.host
        default_ports = {"http": 80, "https": 443}
        if self.port and self.port != default_ports.get(self.scheme):
            netloc = f"{self.host}:{self.port}"
        return f"{self.scheme}://{netloc}{self.path}"

    @property
    def duration_ms(self) -> Optional[float]:
        if self.completed_at is None or not self.started_at:
            return None
        return (self.completed_at - self.started_at) * 1000.0
