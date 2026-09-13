"""Helpers for converting between raw HTTP text and structured parts.

Used by Repeater (edit a raw request, then send it) and the Intercept panel
(edit a paused request before forwarding).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from urllib.parse import urlsplit


@dataclass(slots=True)
class ParsedRequest:
    method: str = "GET"
    path: str = "/"
    http_version: str = "HTTP/1.1"
    headers: list[tuple[str, str]] = field(default_factory=list)
    body: bytes = b""

    def header(self, name: str, default: str = "") -> str:
        low = name.lower()
        for k, v in self.headers:
            if k.lower() == low:
                return v
        return default


def build_request_text(method: str, path: str, http_version: str,
                        headers: str, body: bytes | None) -> str:
    """Assemble a raw HTTP request string from parts.

    Produces the request line, the header block, a blank line, and then the
    body. The blank line is always present so the header/body boundary can be
    re-parsed by :func:`parse_request_text` even when there is no body.
    """
    start = f"{method} {path} {http_version}".strip()
    head_lines = [start]
    if headers:
        head_lines.append(headers)
    # Join the request line + headers, then terminate the header block with a
    # blank line (CRLFCRLF) before appending any body.
    text = "\r\n".join(head_lines) + "\r\n\r\n"
    if body:
        text += body.decode("utf-8", errors="replace")
    return text


def parse_request_text(text: str) -> ParsedRequest:
    """Parse raw HTTP request text into a :class:`ParsedRequest`.

    Tolerant of both CRLF and LF line endings. The header/body boundary is the
    first blank line.
    """
    normalized = text.replace("\r\n", "\n")
    if "\n\n" in normalized:
        head, _, body_str = normalized.partition("\n\n")
    else:
        head, body_str = normalized, ""

    lines = head.split("\n")
    request_line = lines[0].strip() if lines else ""
    tokens = request_line.split()
    method = tokens[0] if len(tokens) >= 1 else "GET"
    path = tokens[1] if len(tokens) >= 2 else "/"
    http_version = tokens[2] if len(tokens) >= 3 else "HTTP/1.1"

    headers: list[tuple[str, str]] = []
    for line in lines[1:]:
        if not line.strip():
            continue
        if ":" in line:
            k, _, v = line.partition(":")
            headers.append((k.strip(), v.strip()))

    return ParsedRequest(
        method=method,
        path=path,
        http_version=http_version,
        headers=headers,
        body=body_str.encode("utf-8"),
    )


def absolute_url(scheme: str, host: str, port: int, path: str) -> str:
    """Reconstruct an absolute URL from flow parts (path may be absolute)."""
    if path.startswith("http://") or path.startswith("https://"):
        return path
    default_ports = {"http": 80, "https": 443}
    netloc = host
    if port and port != default_ports.get(scheme):
        netloc = f"{host}:{port}"
    if not path.startswith("/"):
        path = "/" + path
    return f"{scheme}://{netloc}{path}"


def host_from_headers_or_url(parsed: ParsedRequest, fallback_host: str,
                             fallback_scheme: str, fallback_port: int) -> tuple[str, str, int, str]:
    """Determine (scheme, host, port, path) for sending a parsed request.

    Prefers an absolute request-target; otherwise uses the Host header; finally
    falls back to the values supplied (e.g. from the original captured flow).
    """
    path = parsed.path
    if path.startswith("http://") or path.startswith("https://"):
        sp = urlsplit(path)
        scheme = sp.scheme
        host = sp.hostname or fallback_host
        port = sp.port or (443 if scheme == "https" else 80)
        new_path = sp.path or "/"
        if sp.query:
            new_path += "?" + sp.query
        return scheme, host, port, new_path

    host_header = parsed.header("host")
    if host_header:
        if ":" in host_header:
            h, _, p = host_header.partition(":")
            try:
                return fallback_scheme, h, int(p), path
            except ValueError:
                return fallback_scheme, h, fallback_port, path
        return fallback_scheme, host_header, fallback_port, path

    return fallback_scheme, fallback_host, fallback_port, path
