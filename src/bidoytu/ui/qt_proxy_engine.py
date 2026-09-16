"""Runs mitmproxy inside a dedicated QThread.

Design:
    - mitmproxy is asyncio-based, so the proxy needs its own event loop.
    - Qt owns the main thread's loop, so we cannot run mitmproxy there.
    - We create a QThread, start a fresh asyncio event loop inside ``run()``,
      and drive a mitmproxy ``DumpMaster`` on that loop.
    - Captured/intercepted flows are marshalled back to the UI as Qt signals
      (Qt queues cross-thread signals automatically).
    - Control calls from the UI (enable intercept, forward, drop) are pushed
      onto the proxy loop with ``loop.call_soon_threadsafe`` so the addon's
      asyncio state is only ever touched on its own loop.

Lifecycle:
    start()  -> spins up thread + loop + DumpMaster
    stop()   -> asks the master to shut down and joins the thread
"""
from __future__ import annotations

import asyncio
from typing import Optional

from PySide6.QtCore import QThread, Signal

from bidoytu.config import ProxyConfig
from bidoytu.proxy.capture_addon import CaptureAddon
from bidoytu.storage.models import FlowRecord


class ProxyEngine(QThread):
    """QThread that hosts a mitmproxy DumpMaster on its own asyncio loop."""

    flow_captured = Signal(object, bool)  # (FlowRecord, is_response)
    flow_intercepted = Signal(object)     # (FlowRecord) request paused, awaiting decision
    response_intercepted = Signal(object)  # (FlowRecord) response paused, awaiting decision
    started_ok = Signal(str, int)         # (host, port)
    stopped = Signal()
    error = Signal(str)

    def __init__(self, config: ProxyConfig, confdir: Optional[str] = None,
                 parent=None) -> None:
        super().__init__(parent)
        self._config = config
        # Directory mitmproxy uses for its CA/cert storage. Keeping it under
        # Bidoytu's data dir makes the CA predictable and exportable.
        self._confdir = confdir
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._master = None
        self._addon: Optional[CaptureAddon] = None
        self._intercept_enabled = False
        self._intercept_responses = False
        self._include_scope = tuple(config.include_scope)
        self._exclude_scope = tuple(config.exclude_scope)
        self._scope_options = tuple(getattr(config, name, ()) for name in (
            "include_paths", "exclude_paths", "include_regex", "exclude_regex"))

    # -- QThread entry point --------------------------------------------------

    def run(self) -> None:
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(self._serve())
        except SystemExit as exc:
            # mitmproxy's errorcheck addon calls sys.exit() when a startup error
            # is logged (most commonly: the listen port is already in use).
            # SystemExit is a BaseException, so it would otherwise escape the
            # thread and crash the app. Convert it to a friendly error signal.
            self.error.emit(
                f"Proxy failed to start on "
                f"{self._config.listen_host}:{self._config.listen_port}. "
                f"The port may already be in use."
            )
        except BaseException as exc:  # noqa: BLE001 - keep the thread from crashing
            self.error.emit(str(exc) or exc.__class__.__name__)
        finally:
            loop = self._loop
            try:
                if loop is not None:
                    # DumpMaster closes its listener as run() returns, but the
                    # asyncio accept task can still be pending on Windows.
                    # Cancel and drain those tasks before closing the loop so
                    # the socket is released before a subsequent start().
                    pending = [task for task in asyncio.all_tasks(loop)
                               if not task.done()]
                    for task in pending:
                        task.cancel()
                    if pending:
                        loop.run_until_complete(
                            asyncio.gather(*pending, return_exceptions=True)
                        )
                    loop.run_until_complete(loop.shutdown_asyncgens())
            except Exception:
                pass
            finally:
                if loop is not None:
                    loop.close()
                self._loop = None
                self._master = None
                self._addon = None
                self.stopped.emit()

    def _port_available(self) -> bool:
        """Check the listen port is free before handing off to mitmproxy.

        Failing fast here gives a clean error instead of letting mitmproxy's
        errorcheck addon call sys.exit() (which also writes to stderr, unsafe
        in a windowed build without a console).
        """
        import socket

        # NB: do NOT set SO_REUSEADDR here. On Windows it allows binding a port
        # that another socket already holds, which would make this check pass
        # incorrectly. A plain bind reflects real availability.
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind((self._config.listen_host, self._config.listen_port))
                return True
            except OSError:
                return False

    async def _serve(self) -> None:
        from mitmproxy.options import Options
        from mitmproxy.tools.dump import DumpMaster

        if not self._port_available():
            self.error.emit(
                f"Cannot start proxy: {self._config.listen_host}:"
                f"{self._config.listen_port} is already in use. "
                f"Close whatever is using it or change the port."
            )
            return

        options = Options(
            listen_host=self._config.listen_host,
            listen_port=self._config.listen_port,
            http2=self._config.http2,
            ssl_insecure=self._config.ssl_insecure,
        )
        if self._confdir:
            # Set where mitmproxy generates/reads its CA and leaf certs.
            options.confdir = self._confdir
        self._master = DumpMaster(options, with_termlog=False, with_dumper=False)
        self._addon = CaptureAddon(
            self._emit_flow,
            self._emit_intercept,
            self._emit_response_intercept,
            self._include_scope,
            self._exclude_scope,
            *self._scope_options,
        )
        # Apply any intercept state requested before the loop existed.
        self._addon.set_intercept_enabled(self._intercept_enabled)
        self._addon.set_intercept_responses(self._intercept_responses)
        self._master.addons.add(self._addon)

        # Emit started_ok only once servers are actually up (mitmproxy fires the
        # "running" hook after setup_servers succeeds), so the UI status is
        # accurate even if startup fails after this point.
        engine = self

        class _ReadyAddon:
            def running(self) -> None:
                engine.started_ok.emit(
                    engine._config.listen_host, engine._config.listen_port
                )

        self._master.addons.add(_ReadyAddon())
        await self._master.run()

    # -- flow forwarding (proxy loop -> UI) -----------------------------------

    def _emit_flow(self, record: FlowRecord, is_response: bool) -> None:
        self.flow_captured.emit(record, is_response)

    def _emit_intercept(self, record: FlowRecord) -> None:
        self.flow_intercepted.emit(record)

    def _emit_response_intercept(self, record: FlowRecord) -> None:
        self.response_intercepted.emit(record)

    # -- interception control (UI -> proxy loop) ------------------------------

    def set_intercept_enabled(self, enabled: bool) -> None:
        self._intercept_enabled = enabled
        loop, addon = self._loop, self._addon
        if loop is not None and addon is not None:
            loop.call_soon_threadsafe(addon.set_intercept_enabled, enabled)

    def set_scope(self, include_scope: list[str], exclude_scope: list[str],
                  include_paths: list[str] | None = None,
                  exclude_paths: list[str] | None = None,
                  include_regex: list[str] | None = None,
                  exclude_regex: list[str] | None = None) -> None:
        """Update target scope immediately, including while the proxy runs."""
        self._include_scope = tuple(include_scope)
        self._exclude_scope = tuple(exclude_scope)
        self._scope_options = tuple(tuple(values or ()) for values in (
            include_paths, exclude_paths, include_regex, exclude_regex))
        loop, addon = self._loop, self._addon
        if loop is not None and addon is not None:
            loop.call_soon_threadsafe(
                addon.set_scope, self._include_scope, self._exclude_scope,
                *self._scope_options
            )

    def is_intercept_enabled(self) -> bool:
        return self._intercept_enabled

    def set_intercept_responses(self, enabled: bool) -> None:
        """Toggle the global 'intercept responses' behavior."""
        self._intercept_responses = enabled
        loop, addon = self._loop, self._addon
        if loop is not None and addon is not None:
            loop.call_soon_threadsafe(addon.set_intercept_responses, enabled)

    def intercept_response_for(self, flow_id: str) -> None:
        """Arm a one-shot response intercept for a single flow."""
        loop, addon = self._loop, self._addon
        if loop is not None and addon is not None:
            loop.call_soon_threadsafe(addon.intercept_response_for, flow_id)

    def forward(self, flow_id: str, edited_text: Optional[str] = None) -> None:
        """Forward a paused request, optionally with edited raw request text."""
        loop, addon = self._loop, self._addon
        if loop is not None and addon is not None:
            loop.call_soon_threadsafe(addon.resolve, flow_id, False, edited_text)

    def drop(self, flow_id: str) -> None:
        """Drop a paused request."""
        loop, addon = self._loop, self._addon
        if loop is not None and addon is not None:
            loop.call_soon_threadsafe(addon.resolve, flow_id, True, None)

    def forward_response(self, flow_id: str, edited_text: Optional[str] = None) -> None:
        """Forward a paused response, optionally with edited raw response text."""
        loop, addon = self._loop, self._addon
        if loop is not None and addon is not None:
            loop.call_soon_threadsafe(addon.resolve_response, flow_id, False, edited_text)

    def drop_response(self, flow_id: str) -> None:
        """Drop a paused response."""
        loop, addon = self._loop, self._addon
        if loop is not None and addon is not None:
            loop.call_soon_threadsafe(addon.resolve_response, flow_id, True, None)

    # -- control --------------------------------------------------------------

    def stop(self) -> None:
        loop, master = self._loop, self._master
        if loop is not None and master is not None:
            loop.call_soon_threadsafe(master.shutdown)
        # Do not return until the listener thread has completed its cleanup.
        # This makes an immediate stop -> start on the same port safe.
        if self.isRunning():
            self.wait(10000)
