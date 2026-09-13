"""Raw HTTP message viewer/editor (headers + body) with highlighting.

Soft wrap is on by default so long header values and body lines wrap to the
widget width instead of forcing horizontal scrolling. It can be toggled.

The widget can be read-only (Proxy history) or editable (Repeater / Intercept),
and can serialize its current text back into (start_line, headers, body) parts.
"""
from __future__ import annotations

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QPlainTextEdit

from bidoytu.ui.body_format import format_body
from bidoytu.ui.highlighter import HttpHighlighter


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

    def set_soft_wrap(self, enabled: bool) -> None:
        self.setLineWrapMode(
            QPlainTextEdit.WidgetWidth if enabled else QPlainTextEdit.NoWrap
        )

    def soft_wrap_enabled(self) -> bool:
        return self.lineWrapMode() == QPlainTextEdit.WidgetWidth

    def show_message(self, start_line: str, headers: str, body: bytes | None,
                     content_type: str = "", pretty: bool = True) -> None:
        parts = [start_line, headers, ""]
        text = "\r\n".join(p for p in parts if p is not None)
        if body:
            if pretty:
                # Content-type aware pretty print (JSON/XML/HTML/form).
                text += format_body(body, content_type)
            else:
                text += body.decode("utf-8", errors="replace")
        self.setPlainText(text)

    def raw_text(self) -> str:
        """Return the full editor contents as text (for editable views)."""
        return self.toPlainText()

    def clear_message(self) -> None:
        self.clear()
