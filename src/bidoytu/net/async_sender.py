"""Async HTTP sender for Repeater/Intruder.

Runs an ``httpx.AsyncClient`` on a dedicated asyncio event loop in its own
thread (separate from both the Qt UI thread and the mitmproxy proxy thread, per
the intended architecture). Callers submit a request and receive the result via
a callback marshalled back through a Qt signal by the widget that owns it.

A single request may be cancelled through the :class:`SendHandle` returned by
:meth:`AsyncHttpSender.send`. Per-request TLS verification and redirect
following are supported via a small cache of clients keyed by those options.

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
    cancelled: bool = False


ResultCallback = Callable[[HttpResult], None]


class SendHandle:
    """A cancellable handle to an in-flight request.

    The handle wraps the ``concurrent.futures.Future`` produced by
    ``run_coroutine_threadsafe``. Calling :meth:`cancel` requests cancellation
    on the sender's event loop; the pending request's callback then receives an
    :class:`HttpResult` with ``cancelled=True``.
    """

    def __init__(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop
        self._task: Optional[asyncio.Task] = None
        self._cancelled = False

    def _bind(self, task: asyncio.Task) -> None:
        self._task = task
        if self._cancelled:
            # cancel() was called before the task was created.
            self._loop.call_soon_threadsafe(task.cancel)

    def cancel(self) -> None:
        self._cancelled = True
        task = self._task
        if task is not None:
            self._loop.call_soon_threadsafe(task.cancel)

    @property
    def cancelled(self) -> bool:
        return self._cancelled


class AsyncHttpSender:
    """Owns a background event loop running httpx.AsyncClient instances."""

    def __init__(self) -> None:
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        # Clients keyed by (verify, follow_redirects) so a single sender can
        # serve requests with different TLS/redirect behavior.
        self._clients: dict[tuple[bool, bool], object] = {}
        self._ready = threading.Event()

    def start(self) -> None:
        if self._thread is not None:
            return
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        self._ready.wait(timeout=5)

    def _run(self) -> None:
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._ready.set()
        self._loop.run_forever()
        # Cleanup once the loop is stopped: close every client we opened.
        for client in self._clients.values():
            try:
                self._loop.run_until_complete(client.aclose())
            except Exception:
                pass
        self._loop.close()

    def _client_for(self, verify: bool, follow_redirects: bool):
        import httpx

        key = (verify, follow_redirects)
        client = self._clients.get(key)
        if client is None:
            client = httpx.AsyncClient(verify=verify, follow_redirects=follow_redirects)
            self._clients[key] = client
        return client

    def send(self, method: str, url: str, headers: list[tuple[str, str]],
             body: bytes, callback: ResultCallback, *,
             verify: bool = False, follow_redirects: bool = False,
             fresh_client: bool = False) -> Optional[SendHandle]:
        """Schedule a request; ``callback`` is invoked on the sender thread.

        Returns a :class:`SendHandle` that can cancel the in-flight request, or
        ``None`` if the sender has not been started.

        When ``fresh_client`` is true, the request uses a brand-new client that
        is closed afterwards, guaranteeing a *separate connection* (used by the
        group "separate connections" send mode). Otherwise a pooled client is
        reused, which keeps connections alive between sends.
        """
        if self._loop is None:
            callback(HttpResult(ok=False, error="sender not started"))
            return None
        handle = SendHandle(self._loop)

        def _schedule() -> None:
            task = self._loop.create_task(
                self._do_send(method, url, headers, body, callback,
                              verify, follow_redirects, fresh_client)
            )
            handle._bind(task)

        self._loop.call_soon_threadsafe(_schedule)
        return handle

    async def _do_send(self, method: str, url: str,
                       headers: list[tuple[str, str]], body: bytes,
                       callback: ResultCallback, verify: bool,
                       follow_redirects: bool, fresh_client: bool = False) -> None:
        import httpx

        # Drop hop-by-hop / auto-managed headers so httpx sets them correctly.
        skip = {"content-length", "host", "connection", "accept-encoding"}
        send_headers = [(k, v) for k, v in headers if k.lower() not in skip]

        if fresh_client:
            client = httpx.AsyncClient(verify=verify, follow_redirects=follow_redirects)
        else:
            client = self._client_for(verify, follow_redirects)
        start = time.time()
        try:
            resp = await client.request(
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
        except asyncio.CancelledError:
            callback(HttpResult(ok=False, cancelled=True, error="cancelled",
                                duration_ms=(time.time() - start) * 1000.0))
            raise
        except Exception as exc:
            result = HttpResult(ok=False, error=str(exc),
                                duration_ms=(time.time() - start) * 1000.0)
        finally:
            if fresh_client:
                try:
                    await client.aclose()
                except Exception:
                    pass
        callback(result)

    def stop(self) -> None:
        if self._loop is not None:
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread is not None:
            self._thread.join(timeout=5)
            self._thread = None
