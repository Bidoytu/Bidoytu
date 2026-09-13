"""Pretty-print HTTP bodies for display.

Given raw body bytes and (optionally) a content-type, return a human-readable
string:

* JSON            -> re-indented (2 spaces).
* XML             -> reformatted via minidom.
* HTML            -> reformatted with a lenient, dependency-free parser that
                     tolerates real-world markup (void tags, DOCTYPE, comments,
                     inline <script>/<style>, unquoted attributes, ...).
* JavaScript / CSS -> brace-and-statement aware indentation.
* URL-encoded form -> one ``key = value`` per line.

Anything we can't confidently format is returned as decoded text unchanged.
Binary payloads are summarized. The formatting is for *display only*; it never
changes what gets sent.
"""
from __future__ import annotations

import json
from html.parser import HTMLParser
from urllib.parse import parse_qsl
from xml.dom import minidom

_TEXTUAL_HINTS = (
    "json", "xml", "html", "javascript", "css", "text", "urlencoded", "csv",
    "ecmascript",
)

# HTML "void" elements that never have a closing tag.
_VOID_TAGS = frozenset({
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
    "meta", "param", "source", "track", "wbr",
})

# Elements whose text content should be preserved verbatim (not re-indented as
# markup). We still indent the surrounding tags.
_RAW_TEXT_TAGS = frozenset({"script", "style", "pre", "textarea"})

# Elements with optional end tags that are implicitly closed by a following
# sibling of the same (or a related) kind. This keeps lists / tables / <p>
# from nesting deeper and deeper when the source omits closing tags.
_IMPLICIT_CLOSE = {
    "li": {"li"},
    "dt": {"dt", "dd"},
    "dd": {"dt", "dd"},
    "option": {"option"},
    "p": {"p"},
    "tr": {"tr"},
    "td": {"td", "th"},
    "th": {"td", "th"},
    "thead": {"tbody", "tfoot"},
    "tbody": {"tbody", "tfoot"},
}

# Inline elements: keep them on the same line as their text where reasonable so
# prose doesn't explode into one word per line.
_INLINE_TAGS = frozenset({
    "a", "abbr", "b", "bdi", "bdo", "cite", "code", "data", "dfn", "em", "i",
    "kbd", "mark", "q", "s", "samp", "small", "span", "strong", "sub", "sup",
    "time", "u", "var",
})


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
        if "html" in ct or _sniff_html(text):
            return _format_html(text)
        if "xml" in ct:
            return _format_xml(text)
        if "javascript" in ct or "ecmascript" in ct:
            return _format_js(text)
        if "css" in ct:
            return _format_css(text)
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


# -- sniffers ----------------------------------------------------------------

def _sniff_json(text: str) -> bool:
    s = text.lstrip()
    return s[:1] in ("{", "[")


def _sniff_html(text: str) -> bool:
    s = text.lstrip().lower()
    if s.startswith("<!doctype html") or s.startswith("<html"):
        return True
    # Common opening tags that indicate HTML rather than generic XML.
    return any(tag in s[:512] for tag in ("<head", "<body", "<div", "<span",
                                          "<title", "<meta", "<script"))


# -- formatters --------------------------------------------------------------

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


class _HTMLPretty(HTMLParser):
    """Lenient HTML pretty-printer built on the stdlib parser.

    Emits nicely indented markup. It tolerates malformed / real-world HTML
    because :class:`HTMLParser` does not enforce well-formedness. Raw-text
    elements (``script``/``style``/``pre``/``textarea``) keep their content
    verbatim; inline elements are collapsed onto one line with their text.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self._lines: list[str] = []
        self._depth = 0
        self._raw_tag: str | None = None
        self._raw_buf: list[str] = []
        self._pending_text: list[str] = []
        # Stack of currently-open (non-void) element names.
        self._stack: list[str] = []

    # -- helpers ----------------------------------------------------------
    def _indent(self) -> str:
        return "  " * self._depth

    def _flush_text(self) -> None:
        text = "".join(self._pending_text).strip()
        self._pending_text.clear()
        if text:
            # Collapse internal runs of whitespace for readability.
            collapsed = " ".join(text.split())
            self._lines.append(self._indent() + collapsed)

    def _emit(self, line: str) -> None:
        self._lines.append(self._indent() + line)

    # -- HTMLParser overrides --------------------------------------------
    def _implicit_close(self, tag: str) -> None:
        """Close a preceding sibling with an optional end tag, if applicable."""
        if not self._stack:
            return
        top = self._stack[-1]
        closers = _IMPLICIT_CLOSE.get(top)
        if closers and tag in closers:
            self._flush_text()
            self._stack.pop()
            self._depth = max(0, self._depth - 1)
            self._emit(f"</{top}>")

    def handle_starttag(self, tag, attrs):
        if self._raw_tag is not None:
            self._raw_buf.append(self.get_starttag_text() or f"<{tag}>")
            return
        self._implicit_close(tag)
        self._flush_text()
        attr_str = "".join(
            f' {k}="{v}"' if v is not None else f" {k}" for k, v in attrs
        )
        opening = f"<{tag}{attr_str}>"
        if tag in _VOID_TAGS:
            self._emit(opening)
            return
        if tag in _RAW_TEXT_TAGS:
            self._emit(opening)
            self._depth += 1
            self._raw_tag = tag
            self._raw_buf = []
            return
        self._emit(opening)
        self._depth += 1
        self._stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        # Self-closing tag like <br/> or <img .../>.
        if self._raw_tag is not None:
            self._raw_buf.append(self.get_starttag_text() or f"<{tag}/>")
            return
        self._flush_text()
        attr_str = "".join(
            f' {k}="{v}"' if v is not None else f" {k}" for k, v in attrs
        )
        self._emit(f"<{tag}{attr_str} />")

    def handle_endtag(self, tag):
        if self._raw_tag is not None:
            if tag == self._raw_tag:
                # Emit the buffered raw content (pretty-printing embedded JS/CSS
                # where possible), then close.
                self._emit_raw_content(self._raw_tag)
                self._raw_tag = None
                self._raw_buf = []
                self._depth = max(0, self._depth - 1)
                if self._stack and self._stack[-1] == tag:
                    self._stack.pop()
                self._emit(f"</{tag}>")
            else:
                self._raw_buf.append(f"</{tag}>")
            return
        if tag in _VOID_TAGS:
            return  # no closing tag expected
        self._flush_text()
        # Close any implicitly-open optional-end tags sitting above this one
        # (e.g. an open <li> when we hit </ul>).
        if tag in self._stack:
            while self._stack and self._stack[-1] != tag:
                inner = self._stack.pop()
                self._depth = max(0, self._depth - 1)
                self._emit(f"</{inner}>")
            if self._stack:
                self._stack.pop()
            self._depth = max(0, self._depth - 1)
            self._emit(f"</{tag}>")
        else:
            # Stray close tag with no matching open; emit at current depth.
            self._emit(f"</{tag}>")

    def _emit_raw_content(self, tag: str) -> None:
        raw = "".join(self._raw_buf).strip("\n")
        if not raw.strip():
            return
        pretty = None
        try:
            if tag == "script":
                pretty = _format_js(raw)
            elif tag == "style":
                pretty = _format_css(raw)
        except Exception:
            pretty = None
        for ln in (pretty if pretty is not None else raw).splitlines():
            self._lines.append(self._indent() + ln.rstrip())

    def handle_data(self, data):
        if self._raw_tag is not None:
            self._raw_buf.append(data)
            return
        self._pending_text.append(data)

    def handle_entityref(self, name):
        if self._raw_tag is not None:
            self._raw_buf.append(f"&{name};")
        else:
            self._pending_text.append(f"&{name};")

    def handle_charref(self, name):
        if self._raw_tag is not None:
            self._raw_buf.append(f"&#{name};")
        else:
            self._pending_text.append(f"&#{name};")

    def handle_comment(self, data):
        if self._raw_tag is not None:
            self._raw_buf.append(f"<!--{data}-->")
            return
        self._flush_text()
        self._emit(f"<!--{data.strip()}-->")

    def handle_decl(self, decl):
        self._flush_text()
        self._emit(f"<!{decl}>")

    def result(self) -> str:
        self._flush_text()
        return "\n".join(self._lines)


def _format_html(text: str) -> str:
    parser = _HTMLPretty()
    parser.feed(text)
    parser.close()
    out = parser.result().strip()
    return out or text


def _format_js(text: str) -> str:
    """Indent JavaScript by braces/brackets and break on ``;``.

    A pragmatic, string/comment-aware reformatter. It does not parse JS; it
    just makes minified code readable, which is all we need for display.
    """
    return _format_c_like(text)


def _format_css(text: str) -> str:
    """Indent CSS rules by braces; one declaration per line."""
    return _format_c_like(text, semicolon_breaks=True)


def _format_c_like(text: str, semicolon_breaks: bool = True) -> str:
    out: list[str] = []
    line: list[str] = []
    depth = 0
    i = 0
    n = len(text)
    in_str: str | None = None
    indent = "  "

    def newline() -> None:
        out.append(indent * depth + "".join(line).strip())
        line.clear()

    while i < n:
        ch = text[i]
        nxt = text[i + 1] if i + 1 < n else ""

        # String literals: copy verbatim.
        if in_str is not None:
            line.append(ch)
            if ch == "\\" and nxt:
                line.append(nxt)
                i += 2
                continue
            if ch == in_str:
                in_str = None
            i += 1
            continue
        if ch in ("'", '"', "`"):
            in_str = ch
            line.append(ch)
            i += 1
            continue

        # Line comment.
        if ch == "/" and nxt == "/":
            j = text.find("\n", i)
            if j == -1:
                j = n
            line.append(text[i:j])
            newline()
            i = j + 1
            continue
        # Block comment.
        if ch == "/" and nxt == "*":
            j = text.find("*/", i)
            j = (j + 2) if j != -1 else n
            if "".join(line).strip():
                newline()
            for cl in text[i:j].splitlines():
                out.append(indent * depth + cl.strip())
            i = j
            continue

        if ch == "{":
            line.append(" {")
            newline()
            depth += 1
            i += 1
            # Skip following whitespace.
            while i < n and text[i] in " \t\r\n":
                i += 1
            continue
        if ch == "}":
            if "".join(line).strip():
                newline()
            depth = max(0, depth - 1)
            line.append("}")
            newline()
            i += 1
            while i < n and text[i] in " \t\r\n":
                i += 1
            continue
        if ch == ";" and semicolon_breaks:
            line.append(";")
            newline()
            i += 1
            while i < n and text[i] in " \t\r\n":
                i += 1
            continue
        if ch in "\r\n":
            i += 1
            continue

        line.append(ch)
        i += 1

    if "".join(line).strip():
        newline()
    # Drop empty lines produced by consecutive separators.
    return "\n".join(ln for ln in out if ln.strip() != "")
