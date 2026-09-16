"""Application use cases shared by all desktop IPC commands."""
from __future__ import annotations

import asyncio
import base64
import copy
import json
import time
import uuid
from dataclasses import asdict
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

import httpx

from bidoytu.audit.service import LiveAuditService
from bidoytu.config import AppConfig, host_matches_scope
from bidoytu.http_utils import parse_request_text
from bidoytu.storage.models import FlowRecord
from bidoytu.proxy.engine import ProxyService
from .storage import Storage, summary


class ApplicationService:
    def __init__(self, data_dir: Path, emit):
        self.config = AppConfig(data_dir=data_dir)
        self.config.ensure_dirs()
        self.config.load_proxy_scope()
        self.storage = Storage(self.config)
        self.emit = emit
        self.proxy = ProxyService(self.config, self.capture, self.intercept, self.changed)
        self.pending: dict[str, dict] = {}
        self.queue: asyncio.Queue = asyncio.Queue(maxsize=512)
        self.queue_bytes = 0
        self.dropped = 0
        self.dirty = False
        self.audit = LiveAuditService()
        self.audit.set_enabled(False)
        self.audit_enabled = False
        self.findings: dict[str, dict] = {}
        self.clients: dict[bool, httpx.AsyncClient] = {}
        self.jobs: dict[str, asyncio.Task] = {}
        self.job_results: list[dict] = []
        self.job_state = "idle"
        self.error = ""
        self.network_slots = asyncio.Semaphore(8)

    async def open(self):
        await self.storage.open()
        self.writer = asyncio.create_task(self._persist())
        self.notifier = asyncio.create_task(self._notify())

    def changed(self):
        self.dirty = True

    def state(self):
        return {"protocol": 1, "running": self.proxy.running,
                "port": self.config.proxy.listen_port, "host": "127.0.0.1",
                "intercept": self.proxy.enabled, "responses": self.proxy.responses,
                "pending": list(self.pending.values()), "audit": self.audit_enabled,
                "findings": len(self.findings), "dropped": self.dropped,
                "queue_depth": self.queue.qsize(), "error": self.proxy.error or self.error,
                "data_dir": str(self.config.data_dir),
                "scope": {"include": self.config.proxy.include_scope,
                          "exclude": self.config.proxy.exclude_scope},
                "job_state": self.job_state}

    def capture(self, record: FlowRecord, response: bool):
        size = len(record.request_body_inline or b"") + len(record.response_body_inline or b"")
        if self.queue.full() or self.queue_bytes + size > 64 * 1024 * 1024:
            self.dropped += 1
            self.changed()
            return
        self.queue_bytes += size
        self.queue.put_nowait((copy.copy(record), response, size))

    def intercept(self, record: FlowRecord, phase: str):
        if phase == "response":
            self.capture(record, False)
        # Limit paused requests so an unattended UI cannot consume unbounded RAM.
        if len(self.pending) >= 100:
            resolver = self.proxy.addon.resolve if phase == "request" else self.proxy.addon.resolve_response
            resolver(record.flow_id, True, None)
            self.error = "Intercept queue reached 100 items; additional paused traffic was dropped."
        else:
            self.pending[record.flow_id] = {**summary(record), "phase": phase}
        self.changed()

    async def _persist(self):
        while True:
            record, response, size = await self.queue.get()
            try:
                if self.audit_enabled and record.scope and response:
                    _, issues = await self.storage.call(self.audit.analyze, record, response)
                    for issue in issues:
                        key = f"{record.host}:{issue.title}"
                        self.findings[key] = {"id": key, "flow_id": record.flow_id,
                            "title": issue.title, "severity": str(issue.severity),
                            "detail": issue.detail, "remediation": issue.remediation,
                            "url": record.url, "evidence": [asdict(e) for e in issue.evidence]}
                    while len(self.findings) > 2000:
                        self.findings.pop(next(iter(self.findings)))
                await self.storage.call(self.storage.save, record)
            except Exception as exc:
                self.error = f"Storage: {exc}"
            finally:
                self.queue_bytes -= size
                self.queue.task_done()
                self.changed()

    async def _notify(self):
        while True:
            await asyncio.sleep(0.2)
            if self.dirty:
                self.dirty = False
                await self.emit({"event": "changed", "data": self.state()})

    async def send(self, params: dict, tool="Repeater"):
        raw = str(params.get("request", ""))
        if not raw.strip() or len(raw) > 1024 * 1024:
            raise ValueError("Provide a request smaller than 1 MiB")
        parsed = parse_request_text(raw)
        target = urlsplit(str(params.get("url", "")))
        if target.scheme not in ("http", "https") or not target.hostname or target.username:
            raise ValueError("Target must be an HTTP or HTTPS URL without credentials")
        path = parsed.path
        if not path.startswith("/") or path.startswith("//"):
            raise ValueError("Request target must be an origin path starting with /")
        url = f"{target.scheme}://{target.netloc}{path}"
        verify = bool(params.get("verify_tls", True))
        client = self.clients.get(verify)
        if client is None:
            client = self.clients[verify] = httpx.AsyncClient(
                verify=verify, trust_env=False, timeout=30,
                limits=httpx.Limits(max_connections=16, max_keepalive_connections=8))
        headers = [(k, v) for k, v in parsed.headers if k.lower() not in
                   {"content-length", "connection", "transfer-encoding", "accept-encoding"}]
        record = FlowRecord(flow_id=str(uuid.uuid4()), method=parsed.method,
            scheme=target.scheme, host=target.hostname, port=target.port or (443 if target.scheme == "https" else 80),
            path=path, http_version=parsed.http_version,
            request_headers="\r\n".join(f"{k}: {v}" for k, v in headers),
            request_body_inline=parsed.body, request_body_size=len(parsed.body),
            started_at=time.time(), tool=tool)
        record.scope = host_matches_scope(record.host, self.config.proxy.include_scope, self.config.proxy.exclude_scope, record.path)
        async with self.network_slots:
            async with client.stream(parsed.method, url, headers=headers, content=parsed.body) as response:
                body = bytearray()
                async for chunk in response.aiter_bytes():
                    body.extend(chunk)
                    if len(body) > 32 * 1024 * 1024:
                        raise ValueError("Response exceeds the 32 MiB capture limit")
                record.status_code = response.status_code
                record.reason = response.reason_phrase
                record.http_version = response.http_version
                record.response_headers = "\r\n".join(f"{k}: {v}" for k, v in response.headers.multi_items())
                record.response_body_inline = bytes(body)
                record.response_body_size = len(body)
                record.content_type = response.headers.get("content-type", "")
                record.completed_at = time.time()
        await self.storage.call(self.storage.save, record)
        self.changed()
        return await self.storage.call(self.storage.detail, record.flow_id)

    async def _run_job(self, params: dict):
        self.job_state = "running"
        self.job_results = []
        self.changed()
        try:
            # Sequential execution deliberately provides predictable rate and cancellation.
            for index, payload in enumerate(params["payloads"]):
                request = params["request"].replace("§payload§", str(payload))
                try:
                    result = await self.send({**params, "request": request}, "Intruder")
                    self.job_results.append({"index": index + 1, "payload": payload, **summary_from_detail(result)})
                except Exception as exc:
                    self.job_results.append({"index": index + 1, "payload": payload, "error": str(exc)})
                self.changed()
                await asyncio.sleep(0.1)
            self.job_state = "complete"
        except asyncio.CancelledError:
            self.job_state = "cancelled"
        finally:
            self.changed()

    async def dispatch(self, method: str, p: dict):
        if method == "state":
            return self.state()
        if method == "workspace.load":
            path = self.config.data_dir / "desktop-session.json"
            try:
                return json.loads(await self.storage.call(path.read_text, "utf-8"))
            except (OSError, ValueError):
                return {}
        if method == "workspace.save":
            # Only this fixed workspace file is writable through session IPC.
            encoded = json.dumps(p, ensure_ascii=True)
            if len(encoded) > 1024 * 1024:
                raise ValueError("Workspace session exceeds 1 MiB; close unused request tabs")
            def save_session():
                path = self.config.data_dir / "desktop-session.json"
                temporary = path.with_suffix(".tmp")
                temporary.write_text(encoded, encoding="utf-8")
                temporary.replace(path)
            await self.storage.call(save_session)
            return True
        if method == "history.list":
            return await self.storage.call(self.storage.history, str(p.get("query", ""))[:512],
                max(0, int(p.get("offset", 0))), min(250, max(1, int(p.get("limit", 100)))),
                bool(p.get("scope")), bool(p.get("bookmarked")))
        if method == "history.detail":
            await self.queue.join()
            return await self.storage.call(self.storage.detail, str(p["flow_id"]))
        if method == "history.metadata":
            await self.storage.call(self.storage.metadata, str(p["flow_id"]), bool(p["bookmarked"]), str(p.get("notes", ""))[:10000])
            self.changed()
            return True
        if method == "proxy.start":
            port = int(p.get("port", 8080))
            if not 1024 <= port <= 65535:
                raise ValueError("Use a listener port between 1024 and 65535")
            await self.proxy.start(port, bool(p.get("verify_tls", True)))
            return self.state()
        if method == "proxy.stop":
            await self.proxy.stop()
            self.pending.clear()
            return self.state()
        if method == "proxy.intercept":
            self.proxy.enabled = bool(p["enabled"])
            self.proxy.responses = bool(p.get("responses", False))
            if self.proxy.addon:
                self.proxy.addon.set_intercept_responses(self.proxy.responses)
                self.proxy.addon.set_intercept_enabled(self.proxy.enabled)
            if not self.proxy.enabled:
                self.pending.clear()
            self.changed()
            return self.state()
        if method == "proxy.resolve":
            flow_id = str(p["flow_id"])
            item = self.pending.get(flow_id)
            if item is None or self.proxy.addon is None:
                raise ValueError("This interception is no longer pending")
            resolver = self.proxy.addon.resolve if item["phase"] == "request" else self.proxy.addon.resolve_response
            resolver(flow_id, bool(p.get("drop")), p.get("edited_text"))
            del self.pending[flow_id]
            self.changed()
            return self.state()
        if method == "scope.save":
            for key in ("include", "exclude"):
                values = p.get(key, [])
                if not isinstance(values, list) or len(values) > 200 or any(not isinstance(v, str) or len(v) > 253 for v in values):
                    raise ValueError("Scope must contain at most 200 host patterns")
                setattr(self.config.proxy, f"{key}_scope", values)
            await self.storage.call(self.config.save_proxy_scope)
            if self.proxy.addon:
                self.proxy.addon.set_scope(self.config.proxy.include_scope, self.config.proxy.exclude_scope)
            self.changed()
            return self.state()
        if method == "repeater.send":
            return await self.send(p)
        if method == "intruder.start":
            if self.job_state == "running":
                raise ValueError("An Intruder run is already active")
            payloads = p.get("payloads", [])
            if not isinstance(payloads, list) or not 1 <= len(payloads) <= 1000 or any(not isinstance(v, str) or len(v) > 4096 for v in payloads):
                raise ValueError("Provide 1–1000 text payloads, each up to 4096 characters")
            if "§payload§" not in str(p.get("request", "")):
                raise ValueError("Place §payload§ in the request template")
            self.job_state = "running"
            self.jobs["intruder"] = asyncio.create_task(self._run_job(p))
            return True
        if method == "intruder.results":
            return {"state": self.job_state, "items": self.job_results}
        if method == "intruder.cancel":
            if task := self.jobs.get("intruder"):
                task.cancel()
                await task
            return True
        if method == "audit.toggle":
            self.audit_enabled = bool(p["enabled"])
            await self.storage.call(self.audit.set_enabled, self.audit_enabled)
            self.changed()
            return self.state()
        if method == "audit.list":
            return list(self.findings.values())
        if method == "decoder.transform":
            value = str(p.get("text", ""))
            transforms = {
                "base64.encode": lambda: base64.b64encode(value.encode()).decode(),
                "base64.decode": lambda: base64.b64decode(value, validate=True).decode(),
                "url.encode": lambda: quote(value, safe=""), "url.decode": lambda: unquote(value),
                "json.format": lambda: json.dumps(json.loads(value), indent=2, ensure_ascii=False),
                "hex.encode": lambda: value.encode().hex(),
                "hex.decode": lambda: bytes.fromhex(value).decode(),
            }
            if p.get("operation") not in transforms:
                raise ValueError("Unknown transformation")
            return transforms[p["operation"]]()
        if method == "certificate.read":
            if not self.config.ca_cert_pem.exists():
                raise ValueError("Start the proxy once to generate its public CA certificate")
            return await self.storage.call(self.config.ca_cert_pem.read_text)
        raise ValueError(f"Unknown method: {method}")

    async def close(self):
        for task in self.jobs.values():
            task.cancel()
        await asyncio.gather(*self.jobs.values(), return_exceptions=True)
        await self.proxy.stop()
        await self.queue.join()
        self.writer.cancel()
        self.notifier.cancel()
        await asyncio.gather(self.writer, self.notifier, return_exceptions=True)
        await asyncio.gather(*(client.aclose() for client in self.clients.values()))
        await self.storage.close()


def summary_from_detail(value: dict):
    return {key: value[key] for key in ("flow_id", "status_code", "duration_ms", "response_body_size")}
