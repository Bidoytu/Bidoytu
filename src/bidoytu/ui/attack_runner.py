"""Drives an Intruder attack: iterate jobs, send them, collect results.

The runner is a small :class:`~PySide6.QtCore.QObject` state machine that owns
the flow of an attack:

* pulls :class:`~bidoytu.net.attack.AttackJob` items from a generator,
* keeps up to ``concurrency`` requests in flight through the shared
  :class:`~bidoytu.net.async_sender.AsyncHttpSender`,
* marshals each :class:`HttpResult` back onto the Qt UI thread (the sender's
  callback fires on its own thread),
* applies grep-match / grep-extract to each response,
* emits a :class:`ResultRow` per completed request and progress updates,
* supports pause / resume / stop.

Keeping this separate from the tab widget keeps the UI file focused on layout
and lets the run logic be reasoned about on its own.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterator, List, Optional

from PySide6.QtCore import QObject, Signal, Slot

from bidoytu.http_utils import host_from_headers_or_url, parse_request_text
from bidoytu.net.async_sender import AsyncHttpSender, HttpResult, SendHandle
from bidoytu.net.attack import AttackJob


@dataclass(slots=True)
class GrepConfig:
    """How to derive match/extract columns from each response."""

    match_pattern: str = ""     # regex; response flagged if it matches
    match_is_regex: bool = True
    extract_pattern: str = ""   # regex; first group (or whole match) extracted
    search_headers: bool = True


@dataclass(slots=True)
class ResultRow:
    """One completed request in the results table."""

    index: int
    payloads: List[str]
    request_text: str
    status_code: Optional[int] = None
    reason: str = ""
    length: int = 0
    duration_ms: float = 0.0
    error: str = ""
    matched: bool = False
    extracted: str = ""
    # Kept for the detail view (rendered lazily on selection).
    response_start_line: str = ""
    response_headers: str = ""
    response_body: bytes = b""
    response_content_type: str = ""


def _compile(pattern: str, is_regex: bool) -> Optional[re.Pattern]:
    if not pattern:
        return None
    try:
        return re.compile(pattern if is_regex else re.escape(pattern),
                          re.IGNORECASE)
    except re.error:
        return None


class AttackRunner(QObject):
    """Runs one attack, emitting a :class:`ResultRow` per completed request."""

    row_ready = Signal(object)       # ResultRow (UI thread)
    progress = Signal(int, int)      # (completed, total or -1 if unknown)
    finished = Signal()              # attack ended (done, stopped, or errored)

    # Internal: HttpResult marshalled from the sender thread to the UI thread.
    _result_ready = Signal(object, object)  # (AttackJob, HttpResult)

    def __init__(self, sender: AsyncHttpSender, *, concurrency: int = 10,
                 verify_tls: bool = False, follow_redirects: bool = False,
                 fallback_scheme: str = "http", fallback_host: str = "",
                 fallback_port: int = 80, grep: Optional[GrepConfig] = None,
                 parent=None) -> None:
        super().__init__(parent)
        self._sender = sender
        self._concurrency = max(1, concurrency)
        self._verify = verify_tls
        self._follow = follow_redirects
        self._scheme = fallback_scheme
        self._host = fallback_host
        self._port = fallback_port
        self._grep = grep or GrepConfig()
        self._match_re = _compile(self._grep.match_pattern, self._grep.match_is_regex)
        self._extract_re = _compile(self._grep.extract_pattern, True)

        self._jobs: Optional[Iterator[AttackJob]] = None
        self._total = -1
        self._in_flight = 0
        self._completed = 0
        self._exhausted = False
        self._paused = False
        self._stopped = False
        self._handles: list[SendHandle] = []

        self._result_ready.connect(self._on_result)

    # -- control --------------------------------------------------------------

    def start(self, jobs: Iterator[AttackJob], total: int = -1) -> None:
        self._jobs = jobs
        self._total = total
        self._completed = 0
        self._in_flight = 0
        self._exhausted = False
        self._paused = False
        self._stopped = False
        self.progress.emit(0, self._total)
        self._pump()

    def pause(self) -> None:
        self._paused = True

    def resume(self) -> None:
        if not self._paused:
            return
        self._paused = False
        self._pump()

    def is_paused(self) -> bool:
        return self._paused

    def stop(self) -> None:
        self._stopped = True
        for handle in list(self._handles):
            handle.cancel()
        # If nothing is in flight, we're done immediately.
        if self._in_flight == 0:
            self.finished.emit()

    # -- pump -----------------------------------------------------------------

    def _pump(self) -> None:
        """Launch requests until we hit the concurrency cap or run out."""
        if self._stopped or self._paused or self._jobs is None:
            return
        while self._in_flight < self._concurrency and not self._exhausted:
            try:
                job = next(self._jobs)
            except StopIteration:
                self._exhausted = True
                break
            self._launch(job)
        if self._exhausted and self._in_flight == 0:
            self.finished.emit()

    def _launch(self, job: AttackJob) -> None:
        parsed = parse_request_text(job.request_text)
        scheme, host, port, path = host_from_headers_or_url(
            parsed, self._host, self._scheme, self._port
        )
        if not host:
            # Can't send: report a synthetic failure and keep going.
            row = ResultRow(index=job.index, payloads=job.payloads,
                            request_text=job.request_text, error="no host")
            self._completed += 1
            self.row_ready.emit(row)
            self.progress.emit(self._completed, self._total)
            return
        default_ports = {"http": 80, "https": 443}
        netloc = host if port == default_ports.get(scheme) else f"{host}:{port}"
        url = f"{scheme}://{netloc}{path}"

        self._in_flight += 1
        handle = self._sender.send(
            parsed.method, url, parsed.headers, parsed.body,
            lambda result, j=job: self._result_ready.emit(j, result),
            verify=self._verify, follow_redirects=self._follow,
        )
        if handle is not None:
            self._handles.append(handle)

    @Slot(object, object)
    def _on_result(self, job: AttackJob, result: HttpResult) -> None:
        self._in_flight = max(0, self._in_flight - 1)
        # Drop finished handles so cancel() stays cheap.
        self._handles = [h for h in self._handles if not h.cancelled]

        row = self._row_from(job, result)
        self._completed += 1
        self.row_ready.emit(row)
        self.progress.emit(self._completed, self._total)

        if self._stopped:
            if self._in_flight == 0:
                self.finished.emit()
            return
        # Keep the pipe full.
        self._pump()

    def _row_from(self, job: AttackJob, result: HttpResult) -> ResultRow:
        row = ResultRow(index=job.index, payloads=job.payloads,
                        request_text=job.request_text)
        if result.cancelled:
            row.error = "cancelled"
            return row
        if not result.ok:
            row.error = result.error
            return row
        row.status_code = result.status_code
        row.reason = result.reason
        row.length = len(result.body)
        row.duration_ms = result.duration_ms
        row.response_start_line = (
            f"{result.http_version or 'HTTP/1.1'} "
            f"{result.status_code} {result.reason}".strip()
        )
        row.response_headers = result.headers_text
        row.response_body = result.body

        # grep-match / grep-extract over headers+body (respect search_headers).
        haystack = result.body.decode("utf-8", errors="replace")
        if self._grep.search_headers:
            haystack = result.headers_text + "\r\n\r\n" + haystack
        if self._match_re is not None:
            row.matched = self._match_re.search(haystack) is not None
        if self._extract_re is not None:
            m = self._extract_re.search(haystack)
            if m:
                row.extracted = m.group(1) if m.groups() else m.group(0)
        return row
