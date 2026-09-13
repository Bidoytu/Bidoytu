"""Async HTTP sender for Repeater/Intruder.

Runs an ``httpx.AsyncClient`` on a dedicated asyncio event loop in its own
thread (separate from both the Qt UI thread and the mitmproxy proxy thread, per
the intended architecture). Callers submit a request and receive the result via
a callback marshalled back through a Qt signal by the widget that owns it.

Kept Qt-free; the owning widget wraps results in signals.
"""
from __future__ import annotations

import asyncio
import threading
import time
from dataclasses import dataclass
from typing import Callable, Optional


@dataclass(slots=True)
class HttpResult:
    ok: bool
    status_code: Optional[int] = None
    reason: str = ""
    http_version: str = ""
    headers_text: str = ""
    body: bytes = b""
    error: str = ""
    duration_ms: float = 0.0


ResultCallback = Callable[[HttpResult], None]


class AsyncHttpSender:
    """Owns a background event loop running an httpx.AsyncClient."""

    def __init__(self) -> None:
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._client = None
        self._ready = threading.Event()

    def start(self) -> None:
        if self._thread is not None:
            return
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        self._ready.wait(timeout=5)

    def _run(self) -> None:
        import httpx

        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._client = httpx.AsyncClient(verify=False, follow_redirects=False)
        self._ready.set()
        self._loop.run_forever()
        # Cleanup once the loop is stopped.
        self._loop.run_until_complete(self._client.aclose())
        self._loop.close()

    def send(self, method: str, url: str, headers: list[tuple[str, str]],
             body: bytes, callback: ResultCallback) -> None:
        """Schedule a request; ``callback`` is invoked on the sender thread."""
        if self._loop is None:
            callback(HttpResult(ok=False, error="sender not started"))
            return
        coro = self._do_send(method, url, headers, body, callback)
        asyncio.run_coroutine_threadsafe(coro, self._loop)

    async def _do_send(self, method: str, url: str,
                       headers: list[tuple[str, str]], body: bytes,
                       callback: ResultCallback) -> None:
        import httpx

        # Drop hop-by-hop / auto-managed headers so httpx sets them correctly.
        skip = {"content-length", "host", "connection", "accept-encoding"}
        send_headers = [(k, v) for k, v in headers if k.lower() not in skip]

        start = time.time()
        try:
            resp = await self._client.request(
                method, url, headers=send_headers,
                content=body or None, timeout=30,
            )
            headers_text = "\r\n".join(f"{k}: {v}" for k, v in resp.headers.items())
            result = HttpResult(
                ok=True,
                status_code=resp.status_code,
                reason=resp.reason_phrase,
                http_version=resp.http_version,
                headers_text=headers_text,
                body=resp.content,
                duration_ms=(time.time() - start) * 1000.0,
            )
        except Exception as exc:
            result = HttpResult(ok=False, error=str(exc),
                                duration_ms=(time.time() - start) * 1000.0)
        callback(result)

    def stop(self) -> None:
        if self._loop is not None:
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread is not None:
            self._thread.join(timeout=5)
            self._thread = None
