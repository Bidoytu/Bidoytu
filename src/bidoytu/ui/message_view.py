"""Raw HTTP message viewer/editor (headers + body) with highlighting.

Soft wrap is on by default so long header values and body lines wrap to the
widget width instead of forcing horizontal scrolling. It can be toggled.

The widget can be read-only (Proxy history) or editable (Repeater / Intercept),
and can serialize its current text back into (start_line, headers, body) parts.
"""
from __future__ import annotations

from typing import Callable

from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import QMenu, QPlainTextEdit, QWidget

from bidoytu.ui.body_format import format_body
from bidoytu.ui.highlighter import HttpHighlighter


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

    def __init__(self, parent=None, read_only: bool = True) -> None:
        super().__init__(parent)
        self.setReadOnly(read_only)
        # Extra context-menu actions contributed by the owning view, e.g.
        # "Send to Repeater/Intruder". Each entry is (label, callback, enabled_fn).
        self._extra_actions: list[tuple[str, Callable[[], None], Callable[[], bool]]] = []
        # Soft wrap: wrap long lines at the widget's right edge.
        self.setLineWrapMode(QPlainTextEdit.WidgetWidth)
        font = QFont("Consolas")
        font.setStyleHint(QFont.Monospace)
        font.setPointSize(10)
        self.setFont(font)
        self._highlighter = HttpHighlighter(self.document())

        # Line-number gutter.
        self._line_number_area = _LineNumberArea(self)
        self.blockCountChanged.connect(lambda _: self._update_line_number_area_width())
        self.updateRequest.connect(self._update_line_number_area)
        self._update_line_number_area_width()

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
