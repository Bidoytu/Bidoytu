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

from bidoytu.config import host_matches_scope
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
    edited_text: Optional[str] = None  # raw request/response text if edited


class CaptureAddon:
    """Emits FlowRecords and optionally pauses flows for interception."""

    def __init__(self, on_flow: FlowCallback, on_intercept: InterceptCallback,
                 on_intercept_response: Optional[InterceptCallback] = None,
                 include_scope: tuple[str, ...] = (),
                 exclude_scope: tuple[str, ...] = (),
                 include_paths: tuple[str, ...] = (),
                 exclude_paths: tuple[str, ...] = (),
                 include_regex: tuple[str, ...] = (),
                 exclude_regex: tuple[str, ...] = ()) -> None:
        self._on_flow = on_flow
        self._on_intercept = on_intercept
        # Separate callback for paused responses so the UI can distinguish them
        # from paused requests. Falls back to the request callback if unset.
        self._on_intercept_response = on_intercept_response or on_intercept
        self._intercept_enabled = False
        # Global "intercept responses" toggle (Burp/Caido style): when on, every
        # response is paused for review.
        self._intercept_responses = False
        self._include_scope = include_scope
        self._exclude_scope = exclude_scope
        self._include_paths = include_paths
        self._exclude_paths = exclude_paths
        self._include_regex = include_regex
        self._exclude_regex = exclude_regex
        # Flow ids the user explicitly asked to intercept the response for
        # (Burp's "Response to this request"), even when the global toggle is
        # off. One-shot: consumed when the response is paused.
        self._response_watch: set[str] = set()
        # Paused requests keyed by flow id.
        self._pending: dict[str, _PendingFlow] = {}
        # Paused responses keyed by flow id.
        self._pending_responses: dict[str, _PendingFlow] = {}

    # -- interception control (called on the proxy loop) ----------------------

    def set_scope(self, include_scope: tuple[str, ...],
                  exclude_scope: tuple[str, ...],
                  include_paths: tuple[str, ...] = (),
                  exclude_paths: tuple[str, ...] = (),
                  include_regex: tuple[str, ...] = (),
                  exclude_regex: tuple[str, ...] = ()) -> None:
        """Replace the active target scope on the proxy event loop."""
        self._include_scope = include_scope
        self._exclude_scope = exclude_scope
        self._include_paths = include_paths
        self._exclude_paths = exclude_paths
        self._include_regex = include_regex
        self._exclude_regex = exclude_regex

    def _flow_in_scope(self, flow: http.HTTPFlow) -> bool:
        host = getattr(flow.request, "pretty_host", "") or getattr(
            flow.request, "host", ""
        )
        return host_matches_scope(
            host, self._include_scope, self._exclude_scope,
            getattr(flow.request, "path", "/"), self._include_paths,
            self._exclude_paths, self._include_regex, self._exclude_regex,
        )

    def set_intercept_enabled(self, enabled: bool) -> None:
        self._intercept_enabled = enabled
        # When turning interception off, release anything currently paused
        # (both requests and responses).
        if not enabled:
            for pending in list(self._pending.values()):
                pending.event.set()
            for pending in list(self._pending_responses.values()):
                pending.event.set()

    def set_intercept_responses(self, enabled: bool) -> None:
        """Global toggle: pause every response for review when enabled."""
        self._intercept_responses = enabled

    def intercept_response_for(self, flow_id: str) -> None:
        """Arm a one-shot response intercept for a single flow (Burp's
        "Response to this request"), independent of the global toggle."""
        self._response_watch.add(flow_id)

    def resolve(self, flow_id: str, drop: bool, edited_text: Optional[str]) -> None:
        """Apply a UI decision to a paused request. Runs on the proxy loop."""
        pending = self._pending.get(flow_id)
        if pending is None:
            return
        pending.drop = drop
        pending.edited_text = edited_text
        pending.event.set()

    def resolve_response(self, flow_id: str, drop: bool,
                         edited_text: Optional[str]) -> None:
        """Apply a UI decision to a paused response. Runs on the proxy loop."""
        pending = self._pending_responses.get(flow_id)
        if pending is None:
            return
        pending.drop = drop
        pending.edited_text = edited_text
        pending.event.set()

    # -- mitmproxy hooks ------------------------------------------------------

    async def request(self, flow: http.HTTPFlow) -> None:
        # History keeps both in-scope and out-of-scope traffic so the History
        # filter can distinguish them. Only in-scope traffic is eligible for
        # interception and editing.
        in_scope = self._flow_in_scope(flow)
        record = self._record_from_request(flow)
        self._on_flow(record, False)

        if not in_scope or not self._intercept_enabled:
            return

        pending = _PendingFlow(flow=flow)
        self._pending[flow.id] = pending
        # Notify the UI that a flow is paused and waiting.
        self._on_intercept(record)
        try:
            await pending.event.wait()
        finally:
            self._pending.pop(flow.id, None)

        if pending.drop:
            flow.kill()
            return
        if pending.edited_text is not None:
            self._apply_edited_request(flow, pending.edited_text)

    async def response(self, flow: http.HTTPFlow) -> None:
        armed = flow.id in self._response_watch
        self._response_watch.discard(flow.id)
        in_scope = self._flow_in_scope(flow)
        # Decide whether this response should be paused: interception must be on
        # AND either the global response toggle is set or this flow was armed
        # via "intercept response to this request".
        should_pause = in_scope and self._intercept_enabled and (
            self._intercept_responses or armed
        )

        record = self._record_from_request(flow)
        self._apply_response(record, flow)

        if should_pause:
            pending = _PendingFlow(flow=flow)
            self._pending_responses[flow.id] = pending
            self._on_intercept_response(record)
            try:
                await pending.event.wait()
            finally:
                self._pending_responses.pop(flow.id, None)

            if pending.drop:
                flow.kill()
                return
            if pending.edited_text is not None:
                self._apply_edited_response(flow, pending.edited_text)

        # Refresh the same record after a possible UI edit and surface it.
        if should_pause and pending.edited_text is not None:
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

    @staticmethod
    def _apply_edited_response(flow: http.HTTPFlow, text: str) -> None:
        """Rewrite a flow's response from edited raw text before forwarding."""
        from bidoytu.http_utils import parse_response_text

        parsed = parse_response_text(text)
        resp = flow.response
        if resp is None:
            return
        resp.status_code = parsed.status_code
        if parsed.reason:
            resp.reason = parsed.reason
        # Replace headers wholesale to reflect edits/removals.
        resp.headers.clear()
        for k, v in parsed.headers:
            resp.headers.add(k, v)
        resp.content = parsed.body

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
