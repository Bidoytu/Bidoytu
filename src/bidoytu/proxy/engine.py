"""Async mitmproxy lifecycle owned by the Python application loop."""
from __future__ import annotations

import asyncio
import socket
from typing import Callable

from bidoytu.config import AppConfig
from bidoytu.proxy.capture_addon import CaptureAddon


class ProxyService:
    def __init__(self, config: AppConfig, capture: Callable, intercept: Callable,
                 changed: Callable) -> None:
        self.config = config
        self.capture = capture
        self.intercept = intercept
        self.changed = changed
        self.master = None
        self.addon: CaptureAddon | None = None
        self.task: asyncio.Task | None = None
        self.running = False
        self.enabled = False
        self.responses = False
        self.error = ""
        self.lock = asyncio.Lock()

    async def start(self, port: int, verify_tls: bool) -> None:
        async with self.lock:
            if self.task and not self.task.done():
                raise ValueError("Proxy is already running")
            from mitmproxy.options import Options
            from mitmproxy.tools.dump import DumpMaster

            with socket.socket() as probe:
                probe.bind(("127.0.0.1", port))
            self.config.proxy.listen_port = port
            self.config.proxy.ssl_insecure = not verify_tls
            self.error = ""
            ready = asyncio.Event()
            service = self

            class Ready:
                def running(self):
                    service.running = True
                    ready.set()
                    service.changed()

            self.master = DumpMaster(Options(
                listen_host="127.0.0.1", listen_port=port, http2=True,
                ssl_insecure=not verify_tls, confdir=str(self.config.confdir),
            ), with_termlog=False, with_dumper=False)
            self.master.options.update(body_size_limit="32m")
            scope = self.config.proxy
            self.addon = CaptureAddon(
                self.capture, lambda r: self.intercept(r, "request"),
                lambda r: self.intercept(r, "response"),
                scope.include_scope, scope.exclude_scope,
                scope.include_paths, scope.exclude_paths,
                scope.include_regex, scope.exclude_regex,
            )
            self.addon.set_intercept_enabled(self.enabled)
            self.addon.set_intercept_responses(self.responses)
            self.master.addons.add(self.addon, Ready())

            async def serve():
                try:
                    await self.master.run()
                except (Exception, SystemExit) as exc:
                    self.error = str(exc) or "Proxy failed to start"
                finally:
                    # Master.run does not close listeners when sharing a long-lived
                    # loop. Explicitly release them before announcing stopped.
                    if server := self.master.addons.get("proxyserver"):
                        await server.servers.update([])
                        handlers = list(server.connections.values())
                        connection_tasks = []
                        for handler in handlers:
                            for transport in list(handler.transports.values()):
                                if transport.handler:
                                    connection_tasks.append(transport.handler)
                                    transport.handler.cancel()
                        await asyncio.gather(*connection_tasks, return_exceptions=True)
                    self.running = False
                    ready.set()
                    self.changed()

            self.task = asyncio.create_task(serve())
            try:
                await asyncio.wait_for(ready.wait(), 15)
                if not self.running:
                    raise RuntimeError(self.error or "Proxy stopped during startup")
            except BaseException:
                if self.master:
                    self.master.shutdown()
                await asyncio.gather(self.task, return_exceptions=True)
                raise

    async def stop(self) -> None:
        async with self.lock:
            if self.addon:
                self.addon.set_intercept_enabled(False)
            if self.master:
                self.master.shutdown()
            if self.task:
                await asyncio.wait_for(asyncio.shield(self.task), 10)
            self.addon = self.master = None
            self.task = None
            self.running = False
            self.changed()
