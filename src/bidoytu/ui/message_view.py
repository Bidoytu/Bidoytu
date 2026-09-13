"""Raw HTTP message viewer/editor (headers + body) with highlighting.

Soft wrap is on by default so long header values and body lines wrap to the
widget width instead of forcing horizontal scrolling. It can be toggled.

The widget can be read-only (Proxy history) or editable (Repeater / Intercept),
and can serialize its current text back into (start_line, headers, body) parts.

For read-only response display it remembers the last shown message so the body
can be re-rendered in different modes (Pretty / Raw / Hex) without a re-fetch.
"""
from __future__ import annotations

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QPlainTextEdit

from bidoytu.ui.body_format import format_body
from bidoytu.ui.highlighter import HttpHighlighter

# Render modes for the message body.
MODE_PRETTY = "Pretty"
MODE_RAW = "Raw"
MODE_HEX = "Hex"
RENDER_MODES = (MODE_PRETTY, MODE_RAW, MODE_HEX)


def hex_dump(data: bytes, width: int = 16) -> str:
    """Return a classic offset / hex / ASCII hex dump of ``data``."""
    if not data:
        return ""
    lines: list[str] = []
    for offset in range(0, len(data), width):
        chunk = data[offset:offset + width]
        hex_part = " ".join(f"{b:02x}" for b in chunk)
        hex_part = hex_part.ljust(width * 3 - 1)
        ascii_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        lines.append(f"{offset:08x}  {hex_part}  {ascii_part}")
    return "\n".join(lines)


class MessageView(QPlainTextEdit):
    """A monospace, syntax-highlighted view of a raw HTTP request/response."""

    def __init__(self, parent=None, read_only: bool = True) -> None:
        super().__init__(parent)
        self.setReadOnly(read_only)
        # Soft wrap: wrap long lines at the widget's right edge.
        self.setLineWrapMode(QPlainTextEdit.WidgetWidth)
        font = QFont("Consolas")
        font.setStyleHint(QFont.Monospace)
        font.setPointSize(10)
        self.setFont(font)
        self._highlighter = HttpHighlighter(self.document())

        # Remembered parts of the last shown message (for mode switching).
        self._last_start_line: str = ""
        self._last_headers: str = ""
        self._last_body: bytes | None = None
        self._last_content_type: str = ""
        self._mode: str = MODE_PRETTY

    def set_soft_wrap(self, enabled: bool) -> None:
        self.setLineWrapMode(
            QPlainTextEdit.WidgetWidth if enabled else QPlainTextEdit.NoWrap
        )

    def soft_wrap_enabled(self) -> bool:
        return self.lineWrapMode() == QPlainTextEdit.WidgetWidth

    def render_mode(self) -> str:
        return self._mode

    def set_render_mode(self, mode: str) -> None:
        """Switch how the remembered body is rendered and re-display it."""
        if mode not in RENDER_MODES:
            return
        self._mode = mode
        if self._last_start_line or self._last_headers or self._last_body:
            self._render()

    def show_message(self, start_line: str, headers: str, body: bytes | None,
                     content_type: str = "", pretty: bool = True) -> None:
        self._last_start_line = start_line
        self._last_headers = headers
        self._last_body = body
        self._last_content_type = content_type
        if not pretty and self._mode == MODE_PRETTY:
            self._mode = MODE_RAW
        self._render()

    def _render(self) -> None:
        parts = [self._last_start_line, self._last_headers, ""]
        text = "\r\n".join(p for p in parts if p is not None)
        body = self._last_body
        if body:
            if self._mode == MODE_PRETTY:
                text += format_body(body, self._last_content_type)
            elif self._mode == MODE_HEX:
                text += hex_dump(body)
            else:  # MODE_RAW
                text += body.decode("utf-8", errors="replace")
        self.setPlainText(text)

    def last_body(self) -> bytes | None:
        return self._last_body

    def raw_text(self) -> str:
        """Return the full editor contents as text (for editable views)."""
        return self.toPlainText()

    def clear_message(self) -> None:
        self._last_start_line = ""
        self._last_headers = ""
        self._last_body = None
        self._last_content_type = ""
        self.clear()
