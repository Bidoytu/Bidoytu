"""Search, HTTPQL-like filtering, duplicate detection and portable exports.

The parser deliberately supports a small, predictable subset of HTTPQL:
``field:value`` terms, quoted values, ``>``/``<`` comparisons, and ``and`` /
``or``. Bare words perform full-text search across the complete exchange.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Iterable

from bidoytu.http_utils import ensure_host_header
from bidoytu.storage.models import FlowRecord

_TERM = re.compile(r'''(?:([^\s:<>!=]+)\s*(?:(>=|<=|!=|=|>|<|:)\s*("[^"]*"|'[^']*'|[^\s]+))|("[^"]*"|'[^']*'|[^\s]+))''')


@dataclass
class FilterSpec:
    search: str = ""
    host: str = ""
    path: str = ""
    method: str = ""
    status: str = ""
    mime: str = ""
    size: str = ""
    time: str = ""
    scope: str = ""
    tool: str = ""
    query: str = ""
    in_scope_only: bool = False
    hide_without_responses: bool = False
    parameterized_only: bool = False
    mime_types: set[str] = field(default_factory=set)
    status_classes: set[str] = field(default_factory=set)
    regex: bool = False
    case_sensitive: bool = False
    negative_search: bool = False
    show_extensions: str = ""
    hide_extensions: str = ""
    notes_only: bool = False
    highlighted_only: bool = False
    listener_port: str = ""


def serialize_filter_spec(spec: FilterSpec) -> str:
    """Persist the complete filter state in the saved-filter query column."""
    data = {
        name: value for name, value in spec.__dict__.items()
        if name not in ("mime_types", "status_classes")
    }
    data["mime_types"] = sorted(spec.mime_types)
    data["status_classes"] = sorted(spec.status_classes)
    return json.dumps({"version": 1, "filter": data}, sort_keys=True)


def deserialize_filter_spec(payload: str) -> FilterSpec:
    """Load a saved filter, accepting legacy plain HTTPQL values."""
    try:
        parsed = json.loads(payload)
        data = parsed["filter"] if isinstance(parsed, dict) and "filter" in parsed else parsed
        if not isinstance(data, dict):
            raise ValueError
        allowed = set(FilterSpec.__dataclass_fields__)
        data = {key: value for key, value in data.items() if key in allowed}
        data["mime_types"] = set(data.get("mime_types", []))
        data["status_classes"] = set(data.get("status_classes", []))
        return FilterSpec(**data)
    except (ValueError, TypeError, KeyError, json.JSONDecodeError):
        return FilterSpec(query=payload.strip())


def _value(value: str) -> str:
    return value[1:-1] if len(value) > 1 and value[0] == value[-1] and value[0] in "\"'" else value


def _text(record: FlowRecord) -> str:
    parts = [record.method, record.url, record.host, record.path, record.request_headers,
             record.response_headers, record.tags, record.notes, record.tool]
    bodies = []
    for body in (record.request_body_inline, record.response_body_inline):
        if body:
            bodies.append(body.decode("utf-8", "replace"))
    return "\n".join(parts + bodies).lower()


def _field(record: FlowRecord, name: str):
    name = {"url": "url", "mime": "mime_type", "type": "mime_type",
            "status": "status_code", "size": "response_body_size",
            "time": "started_at", "scope": "scope", "tool": "tool"}.get(name, name)
    return getattr(record, name, "")


def _compare(actual, op: str, expected: str) -> bool:
    if actual is None:
        return False
    expected = _value(expected)
    if op in (":", "=") and re.fullmatch(r"[1-5]xx", expected.lower()):
        try:
            return int(actual) // 100 == int(expected[0])
        except (TypeError, ValueError):
            return False
    if op in (">", ">=", "<", "<="):
        try:
            a, b = float(actual), float(expected)
        except (TypeError, ValueError):
            return False
        return {">": a > b, ">=": a >= b, "<": a < b, "<=": a <= b}[op]
    left, right = str(actual).lower(), expected.lower()
    return (right in left) if op == ":" else ((left == right) if op == "=" else left != right)


def matches(record: FlowRecord, spec: FilterSpec) -> bool:
    """Return true when *record* matches all structured filters and query terms."""
    for name in ("host", "path", "method", "status", "mime", "size", "time", "scope", "tool"):
        value = getattr(spec, name)
        if value and not _compare(_field(record, name), ":", value):
            return False
    if spec.in_scope_only and not record.scope:
        return False
    if spec.hide_without_responses and record.status_code is None:
        return False
    if spec.parameterized_only and "?" not in record.path:
        return False
    if spec.mime_types:
        mime = record.mime_type.lower()
        bucket = ("html" if mime == "text/html" else
                  "script" if "javascript" in mime or "ecmascript" in mime else
                  "xml" if "xml" in mime else "css" if mime == "text/css" else
                  "images" if mime.startswith("image/") else
                  "flash" if "flash" in mime or "shockwave" in mime else
                  "other text" if mime.startswith("text/") else "other binary")
        if bucket not in {item.lower() for item in spec.mime_types}:
            return False
    if spec.status_classes:
        if record.status_code is None or f"{record.status_code // 100}xx" not in spec.status_classes:
            return False
    if spec.show_extensions and record.extension.lower() not in {
            item.strip().lower().lstrip(".") for item in spec.show_extensions.split(",") if item.strip()}:
        return False
    if spec.hide_extensions and record.extension.lower() in {
            item.strip().lower().lstrip(".") for item in spec.hide_extensions.split(",") if item.strip()}:
        return False
    if spec.notes_only and not record.notes.strip():
        return False
    if spec.highlighted_only and not (record.interesting or record.color):
        return False
    if spec.listener_port and str(record.port) != spec.listener_port.strip():
        return False
    if spec.search:
        haystack = _text(record)
        needle = spec.search if spec.case_sensitive else spec.search.lower()
        if spec.regex:
            try:
                found = re.search(spec.search, _text(record), 0 if spec.case_sensitive else re.I) is not None
            except re.error:
                found = False
        else:
            found = needle in haystack
        if spec.negative_search:
            found = not found
        if not found:
            return False
    if spec.query and not query_matches(record, spec.query):
        return False
    return True


def query_matches(record: FlowRecord, query: str) -> bool:
    """Evaluate HTTPQL-like terms. Terms are ANDed; ``or`` groups are supported."""
    groups = re.split(r"\s+or\s+", query, flags=re.I)
    for group in groups:
        terms = re.split(r"\s+and\s+", group, flags=re.I)
        okay = True
        for token in terms:
            token = token.strip()
            if not token:
                continue
            m = _TERM.fullmatch(token)
            if not m:
                okay = token.strip('"\'').lower() in _text(record)
                continue
            name, op, val, bare = m.groups()
            if bare:
                okay = _value(bare).lower() in _text(record)
            elif name.lower() in {"q", "search", "text"}:
                okay = _value(val).lower() in _text(record)
            else:
                okay = _compare(_field(record, name.lower()), op, val)
            if not okay:
                break
        if okay:
            return True
    return False


def fingerprint(record: FlowRecord, request_body: bytes | None = None, response_body: bytes | None = None) -> str:
    data = "\n".join((record.method, record.url, record.request_headers, record.response_headers)).encode()
    return hashlib.sha256(data + (request_body or b"") + (response_body or b"")).hexdigest()


def raw_request(record: FlowRecord, body: bytes | None = None) -> str:
    line = f"{record.method} {record.path} {record.http_version or 'HTTP/1.1'}"
    headers = ensure_host_header(record.request_headers, record.host, record.port, record.scheme)
    return line + "\r\n" + headers.rstrip("\r\n") + "\r\n\r\n" + (body or b"").decode("utf-8", "replace")


def raw_response(record: FlowRecord, body: bytes | None = None) -> str:
    line = f"{record.http_version or 'HTTP/1.1'} {record.status_code or 0} {record.reason}".rstrip()
    return line + "\r\n" + record.response_headers.rstrip("\r\n") + "\r\n\r\n" + (body or b"").decode("utf-8", "replace")


def curl_command(record: FlowRecord, body: bytes | None = None) -> str:
    import shlex
    args = ["curl", "-i", "-X", record.method, record.url]
    for line in record.request_headers.splitlines():
        if ":" in line:
            args += ["-H", line]
    if body:
        args += ["--data-raw", body.decode("utf-8", "replace")]
    return " ".join(shlex.quote(a) for a in args)


def export_records(records: Iterable[FlowRecord], fmt: str, body_provider=None) -> str:
    rows = list(records)
    fmt = fmt.lower()
    if fmt == "json":
        return json.dumps([record_dict(r) for r in rows], indent=2)
    if fmt == "csv":
        out = io.StringIO(); fields = ["id", "method", "url", "status", "mime", "size", "time", "scope", "tool", "tags", "notes"]
        writer = csv.DictWriter(out, fieldnames=fields); writer.writeheader()
        for r in rows: writer.writerow({"id": r.id, "method": r.method, "url": r.url, "status": r.status_code,
            "mime": r.mime_type, "size": r.response_body_size, "time": r.started_at, "scope": r.scope,
            "tool": r.tool, "tags": r.tags, "notes": r.notes})
        return out.getvalue()
    if fmt == "har":
        entries = []
        for r in rows:
            body = _body(r, False, body_provider)
            resp = _body(r, True, body_provider)
            entries.append({"startedDateTime": datetime.fromtimestamp(r.started_at or 0, timezone.utc).isoformat(),
                "time": r.duration_ms or 0, "request": {"method": r.method, "url": r.url, "httpVersion": r.http_version or "HTTP/1.1",
                    "headers": _headers(r.request_headers), "postData": {"text": (body or b"").decode("utf8", "replace")} if body else None},
                "response": {"status": r.status_code or 0, "statusText": r.reason, "httpVersion": r.http_version or "HTTP/1.1",
                    "headers": _headers(r.response_headers), "content": {"size": r.response_body_size, "mimeType": r.mime_type,
                    "text": (resp or b"").decode("utf8", "replace")}}})
        return json.dumps({"log": {"version": "1.2", "creator": {"name": "Bidoytu", "version": "1.0"}, "entries": entries}}, indent=2)
    if fmt in ("raw", "http"):
        return "\n\n".join(raw_request(r, _body(r, False, body_provider)) for r in rows)
    if fmt == "curl":
        return "\n".join(curl_command(r, _body(r, False, body_provider)) for r in rows)
    raise ValueError(f"Unsupported history export format: {fmt}")


def _headers(raw: str) -> list[dict[str, str]]:
    result = []
    for line in raw.splitlines():
        if ":" in line:
            k, v = line.split(":", 1); result.append({"name": k.strip(), "value": v.strip()})
    return result


def _body(record: FlowRecord, response: bool, provider=None) -> bytes | None:
    inline = record.response_body_inline if response else record.request_body_inline
    if inline is not None:
        return inline
    return provider(record, response) if provider else None


def record_dict(r: FlowRecord) -> dict:
    return {"id": r.id, "flow_id": r.flow_id, "method": r.method, "url": r.url, "host": r.host, "path": r.path,
            "status": r.status_code, "mime": r.mime_type, "size": r.response_body_size, "started_at": r.started_at,
            "completed_at": r.completed_at, "scope": r.scope, "tool": r.tool, "bookmarked": r.bookmarked,
            "interesting": r.interesting, "color": r.color, "tags": r.tags, "notes": r.notes, "duplicate_of": r.duplicate_of}
