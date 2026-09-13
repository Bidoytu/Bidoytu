"""Raw HTTP message viewer/editor (headers + body) with highlighting.

Soft wrap is on by default so long header values and body lines wrap to the
widget width instead of forcing horizontal scrolling. It can be toggled.

The widget can be read-only (Proxy history) or editable (Repeater / Intercept),
and can serialize its current text back into (start_line, headers, body) parts.

For read-only response display it remembers the last shown message so the body
can be re-rendered in different modes (Pretty / Raw / Hex) without a re-fetch.
"""
from __future__ import annotations

from typing import Callable

from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import QMenu, QPlainTextEdit, QSizePolicy, QWidget

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


class _LineNumberArea(QWidget):
    """Gutter widget that paints line numbers for its owning MessageView."""

    def __init__(self, editor: "MessageView") -> None:
        super().__init__(editor)
        self._editor = editor

    def sizeHint(self) -> QSize:  # noqa: N802 (Qt override)
        return QSize(self._editor.line_number_area_width(), 0)

    def paintEvent(self, event) -> None:  # noqa: N802 (Qt override)
        self._editor.paint_line_numbers(event)


class MessageView(QPlainTextEdit):
    """A monospace, syntax-highlighted view of a raw HTTP request/response."""

    def __init__(self, parent=None, read_only: bool = True,
                 highlighter_factory=None) -> None:
        super().__init__(parent)
        self.setReadOnly(read_only)
        # Extra context-menu actions contributed by the owning view, e.g.
        # "Send to Repeater/Intruder". Each entry is (label, callback, enabled_fn).
        self._extra_actions: list[tuple[str, Callable[[], None], Callable[[], bool]]] = []
        # Soft wrap: wrap long lines at the widget's right edge.
        self.setLineWrapMode(QPlainTextEdit.WidgetWidth)
        # Let the widget shrink freely: without this, a very long unwrapped line
        # (e.g. a huge request URL) makes QPlainTextEdit report a content-sized
        # minimumSizeHint that propagates up through the splitters and forces the
        # whole window wider. Ignoring the horizontal hint keeps the layout
        # driven by the splitter, and soft wrap reflows the text to fit.
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Expanding)
        self.setMinimumWidth(0)
        font = QFont("Consolas")
        font.setStyleHint(QFont.Monospace)
        font.setPointSize(10)
        self.setFont(font)
        # A caller can supply a different highlighter (e.g. the Intruder
        # template uses one that also colours §payload§ positions). It must
        # accept the QTextDocument as its only argument.
        factory = highlighter_factory or HttpHighlighter
        self._highlighter = factory(self.document())

        # Remembered parts of the last shown message (for mode switching).
        self._last_start_line: str = ""
        self._last_headers: str = ""
        self._last_body: bytes | None = None
        self._last_content_type: str = ""
        self._mode: str = MODE_PRETTY

        # Line-number gutter.
        self._line_number_area = _LineNumberArea(self)
        self.blockCountChanged.connect(lambda _: self._update_line_number_area_width())
        self.updateRequest.connect(self._update_line_number_area)
        self._update_line_number_area_width()

    def minimumSizeHint(self) -> QSize:  # noqa: N802 (Qt override)
        # Pin the minimum width small so a long unwrapped line can never force
        # the containing splitter/window to grow horizontally. Height keeps the
        # base class's hint so vertical sizing is unaffected.
        base = super().minimumSizeHint()
        return QSize(0, base.height())

    def sizeHint(self) -> QSize:  # noqa: N802 (Qt override)
        # Provide a modest preferred width instead of a content-driven one.
        base = super().sizeHint()
        return QSize(200, base.height())

    # -- line number gutter ---------------------------------------------------

    def line_number_area_width(self) -> int:
        digits = max(2, len(str(max(1, self.blockCount()))))
        return 10 + self.fontMetrics().horizontalAdvance("9") * digits

    def _update_line_number_area_width(self) -> None:
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def _update_line_number_area(self, rect: QRect, dy: int) -> None:
        if dy:
            self._line_number_area.scroll(0, dy)
        else:
            self._line_number_area.update(
                0, rect.y(), self._line_number_area.width(), rect.height()
            )
        if rect.contains(self.viewport().rect()):
            self._update_line_number_area_width()

    def resizeEvent(self, event) -> None:  # noqa: N802 (Qt override)
        super().resizeEvent(event)
        cr = self.contentsRect()
        self._line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )

    def paint_line_numbers(self, event) -> None:
        painter = QPainter(self._line_number_area)
        painter.fillRect(event.rect(), self.palette().alternateBase().color())

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())
        pen_color = self.palette().mid().color()
        width = self._line_number_area.width() - 4

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                painter.setPen(pen_color)
                painter.drawText(
                    0, top, width, self.fontMetrics().height(),
                    int(Qt.AlignRight | Qt.AlignVCenter), str(block_number + 1),
                )
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1

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

    def set_theme(self, mode: str) -> None:
        """Re-color the syntax highlighter for a new theme mode."""
        self._highlighter.set_mode(mode)

    # -- context menu ---------------------------------------------------------

    def add_context_action(
        self,
        label: str,
        callback: Callable[[], None],
        enabled_fn: Callable[[], bool] | None = None,
    ) -> None:
        """Register an extra action shown in the right-click menu.

        The action is appended below the standard edit actions (Copy/Paste/...),
        so existing editing behaviour is preserved. ``enabled_fn`` (optional)
        decides whether the action is enabled when the menu opens.
        """
        self._extra_actions.append((label, callback, enabled_fn or (lambda: True)))

    def contextMenuEvent(self, event) -> None:  # noqa: N802 (Qt override)
        menu = self.createStandardContextMenu()
        if self._extra_actions:
            menu.addSeparator()
            for label, callback, enabled_fn in self._extra_actions:
                action = menu.addAction(label)
                action.setEnabled(bool(enabled_fn()))
                action.triggered.connect(callback)
        menu.exec(event.globalPos())
