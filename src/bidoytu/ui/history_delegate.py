"""Item delegate for the HTTP history table.

This delegate paints every cell itself and never calls the base
``QStyledItemDelegate.paint``. Delegating to the style is what let the native
Windows style (or the stylesheet style) draw its own selection background and a
coloured focus/selection frame on each cell -- the "pink ticks" at the column
boundaries. By fully self-painting, no style code runs per cell, so nothing but
what we draw here can appear.

Selection is shown as a soft, low-alpha wash across the row plus a slim accent
bar on the left edge of the first column. Text is drawn with the model's own
alignment and the palette text colour.
"""
from __future__ import annotations

from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QStyle, QStyledItemDelegate

from bidoytu.ui.theme import current_mode, highlight_bg, selection_color

# Width of the slim accent stripe on the left edge of a selected row.
_ACCENT_BAR = 3
# Horizontal text padding inside a cell.
_TEXT_PAD = 6


def _selection_fill(mode: str) -> QColor:
    """A soft, muted tint of the accent used to fill the selected row.

    Uses the shared pre-blended highlight colour (opaque) so the fill matches
    the rest of the app's selection colour and never renders as bright solid
    blue.
    """
    return QColor(highlight_bg(mode))


class HistoryItemDelegate(QStyledItemDelegate):
    """Fully self-painted cells: soft row wash + slim accent bar, no style frame."""

    def paint(self, painter, option, index) -> None:
        selected = bool(option.state & QStyle.State_Selected)
        rect = option.rect
        mode = current_mode()

        painter.save()
        painter.setClipRect(rect)

        # 1) Base background. The view already fills the viewport with the
        #    base/alt-base colours, so we only add the soft wash on selection.
        if selected:
            painter.fillRect(rect, _selection_fill(mode))

        # 2) Slim accent stripe on the left edge of the first column.
        if selected and index.column() == 0:
            painter.fillRect(
                rect.left(), rect.top(), _ACCENT_BAR, rect.height(),
                QColor(selection_color(mode)),
            )

        # 3) Cell text, using the model's alignment and the palette text colour.
        text = index.data(Qt.DisplayRole)
        if text:
            align = index.data(Qt.TextAlignmentRole)
            align = Qt.Alignment(align) if align else (Qt.AlignLeft | Qt.AlignVCenter)
            if not (align & Qt.AlignVCenter):
                align |= Qt.AlignVCenter

            left_pad = _TEXT_PAD
            if index.column() == 0:
                left_pad += _ACCENT_BAR
            text_rect = QRect(
                rect.left() + left_pad, rect.top(),
                rect.width() - left_pad - _TEXT_PAD, rect.height(),
            )

            painter.setPen(option.palette.text().color())
            metrics = painter.fontMetrics()
            elided = metrics.elidedText(str(text), Qt.ElideRight, text_rect.width())
            painter.drawText(text_rect, int(align), elided)

        painter.restore()
