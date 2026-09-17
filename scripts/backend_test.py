"""Local integration tests for the headless engine; no public targets or Qt."""
from __future__ import annotations

import asyncio
import gzip
import json
import socket
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import httpx
from bidoytu.backend.service import ApplicationService
from bidoytu.storage.models import FlowRecord


class BackendTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        # TemporaryDirectory.name is a string; normalize it once at the test
        # boundary so all backend paths remain pathlib.Path objects.
        self.data_dir = Path(self.temp.name).expanduser().resolve()
        self.events = []
        async def emit(event):
            self.events.append(event)
        self.service = ApplicationService(self.data_dir, emit)
        await self.service.open()
        # The desktop backend auto-starts the default listener. Stop it here so
        # these focused tests can choose their own ports explicitly.
        await self.service.proxy.stop()
        self.origin = await asyncio.start_server(self.respond, "127.0.0.1", 0)
        self.origin_port = self.origin.sockets[0].getsockname()[1]

    async def asyncTearDown(self):
        await self.service.close()
        self.origin.close()
        await self.origin.wait_closed()
        self.temp.cleanup()

    async def respond(self, reader, writer):
        try:
            header = await reader.readuntil(b"\r\n\r\n")
            path = header.split(b" ")[1].decode()
            body = json.dumps({"path": path, "engine": "python"}).encode()
            encoding = b""
            if path == "/gzip":
                body = gzip.compress(body)
                encoding = b"Content-Encoding: gzip\r\n"
            writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n" + encoding +
                         f"Content-Length: {len(body)}\r\nConnection: close\r\n\r\n".encode() + body)
            await writer.drain()
        finally:
            writer.close()
            await writer.wait_closed()

    async def wait_for(self, predicate):
        async with asyncio.timeout(10):
            while not predicate():
                await asyncio.sleep(0.02)

    def free_port(self):
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            return sock.getsockname()[1]

    def replay_params(self, path="/"):
        return {"url": f"http://127.0.0.1:{self.origin_port}",
                "request": f"GET {path} HTTP/1.1\r\nHost: 127.0.0.1:{self.origin_port}\r\n\r\n"}

    async def test_replay_storage_search_bookmark_and_decoder(self):
        result = await self.service.dispatch("repeater.send", self.replay_params("/hello?q=world"))
        self.assertEqual(result["status_code"], 200)
        self.assertIn('/hello?q=world', result["response"])
        listing = await self.service.dispatch("history.list", {"query": "hello"})
        self.assertEqual(listing["total"], 1)
        self.assertNotIn("request", listing["items"][0])
        await self.service.dispatch("history.metadata", {"flow_id": result["flow_id"], "bookmarked": True, "notes": "Evidence"})
        self.assertEqual((await self.service.dispatch("history.list", {"bookmarked": True}))["total"], 1)
        self.assertEqual(await self.service.dispatch("decoder.transform", {"operation": "base64.decode", "text": "aGVsbG8="}), "hello")
        with self.assertRaises(ValueError):
            await self.service.dispatch("decoder.transform", {"operation": "exec"})

    async def test_proxy_capture_edit_forward_response_drop_and_restart(self):
        port = self.free_port()
        await self.service.dispatch("proxy.start", {"port": port})
        self.assertTrue(self.service.state()["running"])
        async with httpx.AsyncClient(proxy=f"http://127.0.0.1:{port}", trust_env=False, timeout=10) as client:
            response = await client.get(f"http://127.0.0.1:{self.origin_port}/gzip")
            self.assertEqual(response.status_code, 200)
            await self.service.queue.join()
            listing = await self.service.dispatch("history.list", {})
            detail = await self.service.dispatch("history.detail", {"flow_id": listing["items"][0]["flow_id"]})
            self.assertIn('"engine": "python"', detail["response"])

            await self.service.dispatch("proxy.intercept", {"enabled": True, "responses": True})
            request = asyncio.create_task(client.get(f"http://127.0.0.1:{self.origin_port}/before"))
            await self.wait_for(lambda: self.service.pending)
            flow_id = next(iter(self.service.pending))
            self.assertFalse(request.done())
            await self.service.dispatch("proxy.resolve", {"flow_id": flow_id, "edited_text": self.replay_params("/after")["request"]})
            await self.wait_for(lambda: self.service.pending.get(flow_id, {}).get("phase") == "response")
            response_detail = await self.service.dispatch("history.detail", {"flow_id": flow_id})
            self.assertIn('/after', response_detail["response"])
            await self.service.dispatch("proxy.resolve", {"flow_id": flow_id, "edited_text": "HTTP/1.1 201 Created\r\nContent-Type: text/plain\r\nContent-Length: 6\r\n\r\nedited"})
            response = await request
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.text, "edited")
            request = asyncio.create_task(client.get(f"http://127.0.0.1:{self.origin_port}/drop"))
            await self.wait_for(lambda: self.service.pending)
            await self.service.dispatch("proxy.resolve", {"flow_id": next(iter(self.service.pending)), "drop": True})
            with self.assertRaises(httpx.HTTPError):
                await request
        await self.service.dispatch("proxy.stop", {})
        await self.service.dispatch("proxy.start", {"port": port})
        self.assertTrue(self.service.state()["running"])

    async def test_scope_audit_and_payload_run(self):
        await self.service.dispatch("scope.save", {"include": ["127.0.0.1"], "exclude": ["excluded.invalid"]})
        await self.service.dispatch("audit.toggle", {"enabled": True})
        await self.service.dispatch("intruder.start", {**self.replay_params("/?q=§payload§"), "payloads": ["one", "two"]})
        await self.wait_for(lambda: self.service.job_state == "complete")
        results = await self.service.dispatch("intruder.results", {})
        self.assertEqual(len(results["items"]), 2)
        self.assertTrue(all(row["status_code"] == 200 for row in results["items"]))
        record = FlowRecord(flow_id="audit", scheme="http", host="127.0.0.1", method="GET", path="/", status_code=200,
                            response_headers="Content-Type: text/html", response_body_inline=b"<html>test</html>", scope=True)
        self.service.capture(record, True)
        await self.service.queue.join()
        self.assertTrue(await self.service.dispatch("audit.list", {}))
        self.assertIn("127.0.0.1", self.service.config.proxy_scope_path.read_text())

    async def test_advanced_history_filters(self):
        records = [
            FlowRecord(flow_id="f1", method="GET", scheme="http", host="a.example", path="/index.html",
                       status_code=200, content_type="text/html", response_body_size=1000,
                       response_headers="X-Tag: alpha", scope=True),
            FlowRecord(flow_id="f2", method="POST", scheme="http", host="b.example", path="/api/users?id=1",
                       status_code=404, content_type="application/json", response_body_size=5000, scope=False),
            FlowRecord(flow_id="f3", method="GET", scheme="http", host="cdn.example", path="/logo.png",
                       status_code=200, content_type="image/png", response_body_size=900000, scope=True),
        ]
        for record in records:
            await self.service.storage.call(self.service.storage.save, record)

        async def total(filters, query=""):
            listing = await self.service.dispatch("history.list", {"query": query, "filter": filters})
            return listing["total"]

        self.assertEqual(await total({"status_classes": ["4xx"]}), 1)
        self.assertEqual(await total({"mime_types": ["images"]}), 1)
        self.assertEqual(await total({"size": ">1000"}), 2)
        self.assertEqual(await total({"hide_extensions": "png"}), 2)
        self.assertEqual(await total({"show_extensions": "html"}), 1)
        self.assertEqual(await total({"in_scope_only": True}), 2)
        self.assertEqual(await total({"method": "POST"}), 1)
        self.assertEqual(await total({"path": "api"}), 1)
        self.assertEqual(await total({"parameterized_only": True}), 1)
        self.assertEqual(await total({"host": "example", "notes_only": True}), 0)
        self.assertEqual(await total({"regex": True}, query=r"users\?id=\d"), 1)
        self.assertEqual(await total({"negative_search": True}, query="cdn"), 2)
        # Unknown keys are ignored rather than raising.
        self.assertEqual(await total({"bogus": "x"}), 3)
        listing = await self.service.dispatch("history.list", {"bookmarked": True})
        self.assertEqual(listing["total"], 0)

    async def test_lazy_preview_pagination_validation_and_no_qt(self):
        self.assertFalse(any(key.startswith("PySide6") for key in sys.modules))
        for index in range(3):
            record = FlowRecord(flow_id=f"large-{index}", host="example.test", method="GET", path=f"/{index}",
                response_body_inline=b"x" * 300000, response_body_size=300000, status_code=200)
            await self.service.storage.call(self.service.storage.save, record)
        page = await self.service.dispatch("history.list", {"limit": 1, "offset": 1})
        self.assertEqual(page["total"], 3)
        self.assertEqual(page["items"][0]["path"], "/1")
        detail = await self.service.dispatch("history.detail", {"flow_id": "large-1"})
        self.assertTrue(detail["truncated"])
        self.assertLess(len(detail["response"]), 263000)
        binary = FlowRecord(flow_id="binary", response_body_inline=b"\xff\x00", status_code=200)
        await self.service.storage.call(self.service.storage.save, binary)
        self.assertTrue((await self.service.dispatch("history.detail", {"flow_id": "binary"}))["binary"])
        with self.assertRaises(ValueError):
            await self.service.dispatch("proxy.start", {"port": 80})
        with self.assertRaises(ValueError):
            await self.service.dispatch("repeater.send", {"url": "file:///etc/passwd", "request": "GET / HTTP/1.1"})
        with self.assertRaises(ValueError):
            await self.service.dispatch("shell.exec", {})

    async def test_port_conflict_is_recoverable(self):
        with socket.socket() as occupied:
            occupied.bind(("127.0.0.1", 0))
            occupied.listen()
            with self.assertRaisesRegex(ValueError, "already in use"):
                await self.service.dispatch("proxy.start", {"port": occupied.getsockname()[1]})
            self.assertFalse(self.service.state()["running"])
        await self.service.dispatch("proxy.start", {"port": self.free_port()})
        self.assertTrue(self.service.state()["running"])
        certificate = await self.service.dispatch("certificate.read", {})
        self.assertIn("BEGIN CERTIFICATE", certificate)
        self.assertNotIn("PRIVATE KEY", certificate)


if __name__ == "__main__":
    unittest.main(verbosity=2)
