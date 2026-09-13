"""Pretty-print HTTP bodies for display.

Given raw body bytes and (optionally) a content-type, return a human-readable
string. JSON is re-indented, XML/HTML is reformatted, and URL-encoded forms are
expanded one pair per line. Anything we can't confidently format is returned as
decoded text unchanged. Binary payloads are summarized.

The formatting is for *display only*; it never changes what gets sent.
"""
from __future__ import annotations

import json
from urllib.parse import parse_qsl
from xml.dom import minidom

_TEXTUAL_HINTS = (
    "json", "xml", "html", "javascript", "css", "text", "urlencoded", "csv",
)


def _looks_textual(content_type: str, data: bytes) -> bool:
    ct = content_type.lower()
    if any(h in ct for h in _TEXTUAL_HINTS):
        return True
    if ct:
        return False
    # No content-type: sniff for NUL bytes as a binary signal.
    return b"\x00" not in data[:1024]


def format_body(data: bytes | None, content_type: str = "") -> str:
    """Return a pretty, display-ready string for a body."""
    if not data:
        return ""

    if not _looks_textual(content_type, data):
        return f"<{len(data)} bytes of binary data>"

    text = data.decode("utf-8", errors="replace")
    ct = content_type.lower()

    try:
        if "json" in ct or _sniff_json(text):
            return _format_json(text)
        if "xml" in ct or "html" in ct:
            return _format_xml(text)
        if "urlencoded" in ct:
            return _format_form(text)
    except Exception:
        # Never let formatting break the view; fall back to raw text.
        return text

    return text


def content_type_from_headers(headers_text: str) -> str:
    """Extract the Content-Type value from a raw header block (case-insensitive)."""
    for line in headers_text.splitlines():
        if ":" in line:
            name, _, value = line.partition(":")
            if name.strip().lower() == "content-type":
                return value.strip()
    return ""


def _sniff_json(text: str) -> bool:
    s = text.lstrip()
    return s[:1] in ("{", "[")


def _format_json(text: str) -> str:
    obj = json.loads(text)
    return json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=False)


def _format_xml(text: str) -> str:
    parsed = minidom.parseString(text)
    pretty = parsed.toprettyxml(indent="  ")
    # minidom adds blank lines; collapse them.
    lines = [ln for ln in pretty.splitlines() if ln.strip()]
    return "\n".join(lines)


def _format_form(text: str) -> str:
    pairs = parse_qsl(text, keep_blank_values=True)
    if not pairs:
        return text
    return "\n".join(f"{k} = {v}" for k, v in pairs)
