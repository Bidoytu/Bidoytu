"""mitmproxy addon: maps flows to FlowRecords and supports interception.

Two responsibilities:
    1. Capture - every request and completed response is mapped to a
       framework-free ``FlowRecord`` and handed to a callback (forwarded to Qt
       as a signal by :class:`ProxyEngine`).
    2. Intercept - when interception is enabled, the ``request`` hook pauses the
       flow on the proxy's asyncio loop until the UI decides to forward (with
       possible edits) or drop it.

Pausing works by awaiting an ``asyncio.Event`` inside the hook. mitmproxy runs
hooks as coroutines, so awaiting here suspends just this flow while the proxy
keeps serving others. The UI thread signals the decision via
``ProxyEngine`` using ``loop.call_soon_threadsafe`` so the Event is set on the
correct loop.

Keeping this addon free of Qt imports means the proxy loop never touches Qt
objects directly.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Callable, Optional

from mitmproxy import http

from bidoytu.storage.models import FlowRecord

# (record, is_response) -> None
FlowCallback = Callable[[FlowRecord, bool], None]
# (record) -> None  - a flow has been paused and awaits a decision
InterceptCallback = Callable[[FlowRecord], None]


@dataclass(slots=True)
class _PendingFlow:
    """State for a single intercepted (paused) flow."""

    flow: http.HTTPFlow
    event: asyncio.Event = field(default_factory=asyncio.Event)
    drop: bool = False
    edited_text: Optional[str] = None  # raw request text if the user edited it


class CaptureAddon:
    """Emits FlowRecords and optionally pauses flows for interception."""

    def __init__(self, on_flow: FlowCallback, on_intercept: InterceptCallback) -> None:
        self._on_flow = on_flow
        self._on_intercept = on_intercept
        self._intercept_enabled = False
        self._pending: dict[str, _PendingFlow] = {}

    # -- interception control (called on the proxy loop) ----------------------

    def set_intercept_enabled(self, enabled: bool) -> None:
        self._intercept_enabled = enabled
        # When turning interception off, release anything currently paused.
        if not enabled:
            for pending in list(self._pending.values()):
                pending.event.set()

    def resolve(self, flow_id: str, drop: bool, edited_text: Optional[str]) -> None:
        """Apply a UI decision to a paused flow. Runs on the proxy loop."""
        pending = self._pending.get(flow_id)
        if pending is None:
            return
        pending.drop = drop
        pending.edited_text = edited_text
        pending.event.set()

    # -- mitmproxy hooks ------------------------------------------------------

    async def request(self, flow: http.HTTPFlow) -> None:
        # Always surface the request to the history first.
        self._on_flow(self._record_from_request(flow), False)

        if not self._intercept_enabled:
            return

        pending = _PendingFlow(flow=flow)
        self._pending[flow.id] = pending
        # Notify the UI that a flow is paused and waiting.
        self._on_intercept(self._record_from_request(flow))
        try:
            await pending.event.wait()
        finally:
            self._pending.pop(flow.id, None)

        if pending.drop:
            flow.kill()
            return
        if pending.edited_text is not None:
            self._apply_edited_request(flow, pending.edited_text)

    def response(self, flow: http.HTTPFlow) -> None:
        record = self._record_from_request(flow)
        self._apply_response(record, flow)
        self._on_flow(record, True)

    # -- edit application -----------------------------------------------------

    @staticmethod
    def _apply_edited_request(flow: http.HTTPFlow, text: str) -> None:
        """Rewrite a flow's request from edited raw text before forwarding."""
        from bidoytu.http_utils import parse_request_text

        parsed = parse_request_text(text)
        req = flow.request
        req.method = parsed.method
        req.path = parsed.path
        # Replace headers wholesale to reflect edits/removals.
        req.headers.clear()
        for k, v in parsed.headers:
            req.headers.add(k, v)
        req.content = parsed.body

    # -- mapping helpers ------------------------------------------------------

    @staticmethod
    def _record_from_request(flow: http.HTTPFlow) -> FlowRecord:
        req = flow.request
        body = CaptureAddon._decoded_body(req)
        return FlowRecord(
            flow_id=flow.id,
            method=req.method,
            scheme=req.scheme,
            host=req.pretty_host,
            port=req.port,
            path=req.path,
            http_version=req.http_version,
            request_headers=CaptureAddon._headers_to_text(req.headers),
            request_body_inline=body or None,
            request_body_size=len(body),
            started_at=flow.timestamp_created or 0.0,
        )

    @staticmethod
    def _apply_response(record: FlowRecord, flow: http.HTTPFlow) -> None:
        resp = flow.response
        if resp is None:
            return
        body = CaptureAddon._decoded_body(resp)
        record.status_code = resp.status_code
        record.reason = resp.reason or ""
        record.response_headers = CaptureAddon._headers_to_text(resp.headers)
        record.response_body_inline = body or None
        record.response_body_size = len(body)
        record.content_type = resp.headers.get("content-type", "")
        record.completed_at = resp.timestamp_end or None

    @staticmethod
    def _decoded_body(message) -> bytes:
        """Return the decoded (decompressed) body; fall back to raw bytes."""
        try:
            body = message.content
        except Exception:
            body = None
        if body is None:
            body = message.raw_content or b""
        return body

    @staticmethod
    def _headers_to_text(headers) -> str:
        return "\r\n".join(f"{k}: {v}" for k, v in headers.items())
