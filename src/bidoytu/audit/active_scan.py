"""Bounded active verification worker for the Live Audit tab.

The worker is deliberately independent from Qt, mitmproxy, and the UI. It
accepts only in-scope safe-method requests and sends a small number of
controlled probes. It is not a general-purpose exploit engine.
"""
from __future__ import annotations

import queue
import re
import threading
import uuid
from dataclasses import dataclass, replace
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from bidoytu.audit.service import AuditIssue, Evidence, Severity
from bidoytu.storage.models import FlowRecord


@dataclass(slots=True)
class ActiveScanResult:
    """A finding produced by an active, safe-method verification probe."""

    issue: AuditIssue


def _request_headers(record: FlowRecord) -> dict[str, str]:
    headers: dict[str, str] = {}
    for line in record.request_headers.splitlines():
        if ":" in line:
            name, value = line.split(":", 1)
            if name.strip().lower() not in {"host", "content-length", "connection"}:
                headers[name.strip()] = value.strip()
    return headers


def _record_response(record: FlowRecord, response, body: bytes) -> FlowRecord:
    return replace(
        record, status_code=response.status_code, reason=response.reason_phrase,
        http_version=response.http_version,
        response_headers="\r\n".join(f"{k}: {v}" for k, v in response.headers.items()),
        response_body_inline=body, response_body_size=len(body),
        content_type=response.headers.get("content-type", ""),
    )


class ActiveScanWorker:
    """Single background worker with bounded safe active verification."""

    SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})
    MAX_BODY = 2 * 1024 * 1024

    def __init__(self, on_result) -> None:
        self._on_result = on_result
        self._queue: queue.Queue[FlowRecord | None] = queue.Queue(maxsize=1000)
        self._thread: threading.Thread | None = None
        self._enabled = False
        self._lock = threading.Lock()
        self.skipped_state_changing = 0

    @property
    def enabled(self) -> bool:
        with self._lock:
            return self._enabled

    def set_enabled(self, enabled: bool) -> None:
        with self._lock:
            self._enabled = enabled
        if enabled:
            self.start()

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._run, name="bidoytu-active-audit", daemon=True)
        self._thread.start()

    def submit(self, record: FlowRecord) -> bool:
        if not self.enabled or not record.scope:
            return False
        if record.method.upper() not in self.SAFE_METHODS:
            self.skipped_state_changing += 1
            return False
        try:
            self._queue.put_nowait(record)
            return True
        except queue.Full:
            return False

    def _run(self) -> None:
        while True:
            record = self._queue.get()
            if record is None:
                return
            try:
                self._scan(record)
            except Exception:
                # A target/network failure is not itself a vulnerability and
                # must never terminate the live-audit worker.
                continue

    def _scan(self, record: FlowRecord) -> None:
        import httpx

        parsed = urlsplit(record.url)
        params = parse_qsl(parsed.query, keep_blank_values=True)
        if not params or parsed.scheme not in {"http", "https"}:
            return
        headers = _request_headers(record)
        timeout = httpx.Timeout(10.0, connect=5.0)
        with httpx.Client(verify=False, follow_redirects=False, timeout=timeout) as client:
            for index, (name, value) in enumerate(params):
                marker = f"bidoytu-audit-{uuid.uuid4().hex[:10]}"
                probe_params = list(params)
                probe_params[index] = (name, marker)
                probe_url = urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(probe_params), ""))
                response = client.request(record.method, probe_url, headers=headers)
                body = response.content[: self.MAX_BODY]
                if marker.encode() in body:
                    evidence = Evidence("response", marker)
                    scanned = _record_response(record, response, body)
                    self._emit(AuditIssue(
                        "Reflected input requires XSS verification", Severity.MEDIUM, "Tentative",
                        "A unique value placed in a URL parameter was returned in the response. The reflection context must be reviewed before classifying this as XSS.",
                        "Contextually encode untrusted output. Confirm the exact HTML/attribute/script context with a controlled authorized test.",
                        scanned, (evidence,),
                    ))

                # A single quote is a diagnostic input, not an exploit payload.
                quote_params = list(params)
                quote_params[index] = (name, value + "'")
                quote_url = urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(quote_params), ""))
                quote_response = client.request(record.method, quote_url, headers=headers)
                quote_body = quote_response.content[: self.MAX_BODY].decode("utf-8", errors="replace")
                sql_error = re.search(
                    r"(?:sql syntax.*mysql|mysql_fetch|postgresql.*error|ora-\d{4,5}|sqlite exception|odbc sql|unclosed quotation mark|sqlstate\[)",
                    quote_body, re.IGNORECASE,
                )
                if sql_error:
                    scanned = _record_response(record, quote_response, quote_response.content[: self.MAX_BODY])
                    self._emit(AuditIssue(
                        "Potential SQL injection error response", Severity.MEDIUM, "Tentative",
                        "Adding a diagnostic quote to a safe-method URL parameter produced a database error signature.",
                        "Use parameterized queries and generic client-facing errors. Re-test with an approved verification plan.",
                        scanned, (Evidence("response", sql_error.group(0)),),
                    ))

    def _emit(self, issue: AuditIssue) -> None:
        self._on_result(ActiveScanResult(issue))

    def stop(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            self._queue.put(None)
            self._thread.join(timeout=5)
        self._thread = None
