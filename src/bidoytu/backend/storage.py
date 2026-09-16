"""Single-owner SQLite worker, paged metadata queries, and lazy body previews."""
from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from bidoytu.config import AppConfig
from bidoytu.http_utils import build_request_text, build_response_text
from bidoytu.storage.body_store import BodyStore
from bidoytu.storage.models import FlowRecord
from bidoytu.storage.repository import FlowRepository

PREVIEW_LIMIT = 256 * 1024


def summary(record: FlowRecord) -> dict:
    fields = ("id", "flow_id", "method", "scheme", "host", "port", "path",
              "status_code", "content_type", "response_body_size", "started_at",
              "scope", "bookmarked", "notes", "tool")
    return {**{key: getattr(record, key) for key in fields},
            "url": record.url, "duration_ms": record.duration_ms}


class Storage:
    """Every connection access runs on the same executor thread."""

    def __init__(self, config: AppConfig):
        self.config = config
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="storage")

    async def call(self, fn, *args):
        return await asyncio.get_running_loop().run_in_executor(
            self.executor, partial(fn, *args))

    async def open(self):
        def initialize():
            self.repo = FlowRepository(self.config.db_path)
            self.bodies = BodyStore(self.config.bodies_dir)
        await self.call(initialize)

    def save(self, record: FlowRecord):
        for side in ("request", "response"):
            body = getattr(record, f"{side}_body_inline")
            if body and len(body) > 64 * 1024:
                setattr(record, f"{side}_body_path", self.bodies.store(body))
                setattr(record, f"{side}_body_inline", None)
        self.repo.upsert(record)

    def history(self, query: str, offset: int, limit: int, scope: bool, bookmarked: bool):
        where, args = ["1=1"], []
        if query:
            where.append("(host LIKE ? OR path LIKE ? OR method LIKE ? OR CAST(status_code AS TEXT) LIKE ?)")
            args.extend([f"%{query}%"] * 4)
        if scope:
            where.append("scope=1")
        if bookmarked:
            where.append("bookmarked=1")
        clause = " AND ".join(where)
        # Projection deliberately excludes bodies AND large header blocks.
        columns = "id,flow_id,method,scheme,host,port,path,status_code,content_type,response_body_size,started_at,completed_at,scope,bookmarked,notes,tool"
        rows = self.repo._conn.execute(
            f"SELECT {columns} FROM flows WHERE {clause} ORDER BY id DESC LIMIT ? OFFSET ?",
            (*args, limit, offset)).fetchall()
        count = self.repo._conn.execute(f"SELECT COUNT(*) FROM flows WHERE {clause}", args).fetchone()[0]
        return {"items": [summary(FlowRecord(**dict(row))) for row in rows], "total": count}

    def detail(self, flow_id: str):
        record = self.repo.get_by_flow_id(flow_id)
        if record is None:
            raise ValueError("Traffic item no longer exists")
        bodies = {}
        truncated = False
        binary = False
        for side in ("request", "response"):
            body = getattr(record, f"{side}_body_inline") or b""
            path = getattr(record, f"{side}_body_path")
            if path:
                # Validate persisted paths before reading potentially imported data.
                root = self.config.bodies_dir.resolve()
                target = (root / path).resolve()
                if not target.is_relative_to(root):
                    raise ValueError("Invalid body path")
                with target.open("rb") as handle:
                    body = handle.read(PREVIEW_LIMIT + 1)
            truncated |= len(body) > PREVIEW_LIMIT
            try:
                body.decode("utf-8")
                binary |= b"\x00" in body
            except UnicodeDecodeError:
                binary = True
            bodies[side] = body[:PREVIEW_LIMIT]
        return {**summary(record), "request": build_request_text(
            record.method, record.path, record.http_version, record.request_headers,
            bodies["request"], record.host, record.port, record.scheme),
            "response": build_response_text(record.http_version, record.status_code,
                record.reason, record.response_headers, bodies["response"]) if record.status_code else "",
            "truncated": truncated, "binary": binary}

    def metadata(self, flow_id: str, bookmarked: bool, notes: str):
        record = self.repo.get_by_flow_id(flow_id)
        if record is None:
            raise ValueError("Traffic item no longer exists")
        record.bookmarked, record.notes = bookmarked, notes
        self.repo.update_metadata(record)

    async def close(self):
        await self.call(self.repo.close)
        self.executor.shutdown(wait=True)
