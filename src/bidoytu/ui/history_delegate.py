"""Item delegate for the HTTP history table.

Selection is shown as a thin border drawn around the whole selected row rather
than a filled highlight. Each cell paints the row's top and bottom edges; the
first cell adds the left edge and the last cell adds the right edge, so together
the cells form one continuous rectangle around the row.

No cell background is filled for selection, which avoids the blue fill/focus
artifacts that the active stylesheet would otherwise draw.
"""
from __future__ import annotations

from PySide6.QtGui import QColor, QPen
from PySide6.QtWidgets import QStyle, QStyledItemDelegate

from bidoytu.ui.theme import current_mode, selection_color

_BORDER_WIDTH = 2


class HistoryItemDelegate(QStyledItemDelegate):
    """Outlines the selected row with a border instead of filling it."""

    def initStyleOption(self, option, index) -> None:  # noqa: N802 (Qt override)
        super().initStyleOption(option, index)
        # Suppress the style's own selection background/focus decoration; the
        # selected row is indicated only by the border we draw in paint().
        option.state &= ~QStyle.State_Selected

    def paint(self, painter, option, index) -> None:
        # option.state still carries State_Selected here (initStyleOption, which
        # clears it, only runs inside super().paint()).
        selected = bool(option.state & QStyle.State_Selected)

        # Paint the normal (unselected) cell content first.
        super().paint(painter, option, index)

        if not selected:
            return

        rect = option.rect
        color = QColor(selection_color(current_mode()))
        pen = QPen(color)
        pen.setWidth(_BORDER_WIDTH)

        painter.save()
        painter.setPen(pen)
        # Nudge inward by half the pen width so the stroke stays inside the cell.
        half = _BORDER_WIDTH // 2
        top = rect.top() + half
        bottom = rect.bottom() - half
        left = rect.left()
        right = rect.right()

        # Top and bottom edges span every cell -> continuous horizontal lines.
        painter.drawLine(left, top, right, top)
        painter.drawLine(left, bottom, right, bottom)

        # Left edge only on the first column, right edge only on the last.
        last_col = index.model().columnCount() - 1
        if index.column() == 0:
            painter.drawLine(left + half, top, left + half, bottom)
        if index.column() == last_col:
            painter.drawLine(right - half, top, right - half, bottom)
        painter.restore()
