"""Single-owner SQLite worker, paged metadata queries, and lazy body previews."""
from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from functools import partial

from bidoytu.config import AppConfig, host_matches_scope
from bidoytu.http_utils import build_request_text, build_response_text
from bidoytu.storage.advanced_history import FilterSpec, matches
from bidoytu.storage.body_store import BodyStore
from bidoytu.storage.models import FlowRecord
from bidoytu.storage.repository import FlowRepository

PREVIEW_LIMIT = 256 * 1024

_BINARY_RESPONSE_TYPES = (
    "image/", "video/", "audio/", "font/", "application/wasm",
    "application/octet-stream", "application/pdf", "application/zip",
    "application/gzip", "application/x-7z-compressed", "application/x-rar-compressed",
)
_BINARY_RESPONSE_EXTENSIONS = frozenset({
    "avif", "bmp", "gif", "ico", "jpeg", "jpg", "png", "svgz", "webp",
    "avi", "m4v", "mkv", "mov", "mp4", "mpeg", "mpg", "ogv", "webm",
    "flac", "m4a", "mp3", "ogg", "wav", "woff", "woff2", "ttf", "otf",
})


def _binary_response(record: FlowRecord) -> bool:
    mime = record.mime_type.casefold()
    return mime.startswith(_BINARY_RESPONSE_TYPES) or record.extension.casefold() in _BINARY_RESPONSE_EXTENSIONS


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

    def history(self, query: str, offset: int, limit: int, scope: bool,
                bookmarked: bool, spec: FilterSpec | None = None,
                sort_by: str = "id", sort_direction: str = "desc"):
        """Return a newest-first page of history matching all active filters.

        The structured :class:`FilterSpec` is evaluated against metadata-only
        summaries (bodies stay on disk), so advanced filters never materialize
        request or response payloads.
        """
        if spec is None:
            spec = FilterSpec(search=query, in_scope_only=scope, bookmarked_only=bookmarked)
        elif query or scope or bookmarked:
            spec = replace(
                spec,
                search=spec.search or query,
                in_scope_only=spec.in_scope_only or scope,
                bookmarked_only=spec.bookmarked_only or bookmarked,
            )
        records = self.repo.list_summaries()
        proxy_scope = self.config.proxy
        scope_configured = any((proxy_scope.include_scope, proxy_scope.exclude_scope,
                                proxy_scope.include_paths, proxy_scope.exclude_paths,
                                proxy_scope.include_regex, proxy_scope.exclude_regex))
        matched = []
        for record in records:
            # Re-evaluate against the current scope configuration so history
            # captured before a scope change (or before scope was persisted
            # correctly) does not leak into the In-scope view.
            if spec.in_scope_only and scope_configured:
                current_scope = host_matches_scope(
                    record.host, tuple(proxy_scope.include_scope),
                    tuple(proxy_scope.exclude_scope), record.path,
                    tuple(proxy_scope.include_paths), tuple(proxy_scope.exclude_paths),
                    tuple(proxy_scope.include_regex), tuple(proxy_scope.exclude_regex),
                )
                record = replace(record, scope=current_scope)
            if matches(record, spec):
                matched.append(record)
        sort_fields = {
            "id": lambda record: record.id,
            "method": lambda record: record.method.casefold(),
            "host": lambda record: record.host.casefold(),
            "path": lambda record: record.path.casefold(),
            "status": lambda record: record.status_code,
            "size": lambda record: record.response_body_size,
            "time": lambda record: record.duration_ms,
        }
        key = sort_fields.get(sort_by, sort_fields["id"])
        descending = sort_direction != "asc"
        present = [record for record in matched if key(record) is not None]
        missing = [record for record in matched if key(record) is None]
        present.sort(key=key, reverse=descending)
        matched = present + missing
        return {"items": [summary(record) for record in matched[offset:offset + limit]],
                "total": len(matched), "unfiltered": len(records)}

    def clear_history(self):
        self.repo.clear()

    def detail(self, flow_id: str):
        record = self.repo.get_by_flow_id(flow_id)
        if record is None:
            raise ValueError("Traffic item no longer exists")
        bodies = {}
        truncated = False
        binary = False
        for side in ("request", "response"):
            body = getattr(record, f"{side}_body_inline") or b""
            if side == "response" and _binary_response(record):
                binary = True
                bodies[side] = b""
                continue
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
        response_text = build_response_text(record.http_version, record.status_code,
            record.reason, record.response_headers, bodies["response"]) if record.status_code else ""
        if _binary_response(record) and record.status_code:
            response_text += f"<{record.response_body_size} bytes>"
        return {**summary(record), "request": build_request_text(
            record.method, record.path, record.http_version, record.request_headers,
            bodies["request"], record.host, record.port, record.scheme),
            "response": response_text,
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
