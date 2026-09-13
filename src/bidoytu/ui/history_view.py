"""HTTP history: the traffic table plus a request/response detail view.

Emits a signal when a row is selected (so the owner can populate detail) and
exposes a context menu with "Send to Repeater/Intruder" actions.
"""
from __future__ import annotations

from PySide6.QtCore import QModelIndex, Qt, Signal, Slot
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QMenu,
    QSplitter,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from bidoytu.storage.models import FlowRecord
from bidoytu.ui.detail_view import DetailView
from bidoytu.ui.flow_table_model import FlowTableModel
from bidoytu.ui.history_delegate import HistoryItemDelegate


class HistoryView(QWidget):
    """Traffic table + detail, with send-to context actions."""

    send_to_repeater = Signal(object)  # FlowRecord
    send_to_intruder = Signal(object)  # FlowRecord
    body_provider = None  # set by owner: callable(record, response: bool) -> bytes|None

    def __init__(self, model: FlowTableModel, parent=None) -> None:
        super().__init__(parent)
        self._model = model
        # Re-entrancy guard: our own resizeSection() calls emit sectionResized
        # again, which would recurse into the handler. Set while we adjust Path.
        self._resizing_guard = False

        self._table = QTableView()
        self._table.setModel(model)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SingleSelection)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # The delegate fully self-paints every cell (soft wash + accent bar +
        # text) and never calls the base style, so no style-drawn selection
        # background or coloured focus/selection frame can appear.
        self._table.setItemDelegate(HistoryItemDelegate(self._table))
        # No gridlines: cleaner look, and removes any per-column boundary ticks.
        self._table.setShowGrid(False)
        # No focus rectangle regardless of platform style.
        self._table.setFocusPolicy(Qt.NoFocus)
        self._table.verticalHeader().setVisible(False)
        self._table.setContextMenuPolicy(Qt.CustomContextMenu)
        self._table.customContextMenuRequested.connect(self._on_context_menu)
        self._configure_columns()

        self._detail = DetailView(editable_request=False)
        # Right-clicking inside the request pane offers the same send-to actions
        # as the table row menu.
        self._detail.send_to_repeater.connect(self.send_to_repeater)
        self._detail.send_to_intruder.connect(self.send_to_intruder)

        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self._table)
        splitter.addWidget(self._detail)
        splitter.setSizes([350, 450])

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(splitter)

        self._table.selectionModel().selectionChanged.connect(self._on_selection)

        # Shortcuts active when the history table has focus.
        self._add_shortcut("Ctrl+R", self._emit_repeater)
        self._add_shortcut("Ctrl+I", self._emit_intruder)

    def _configure_columns(self) -> None:
        """Size columns so Path fills the leftover width initially, while every
        column divider stays freely draggable.

        Column order (from FlowTableModel.COLUMNS):
        0 #, 1 Method, 2 Host, 3 Path, 4 Ext, 5 Status, 6 Type, 7 Length,
        8 Cookies, 9 Time (ms).

        Every column uses Interactive resize mode. We deliberately avoid
        QHeaderView.Stretch on a middle column: a stretch section has no
        draggable right edge (so Path's right side can't be dragged), and it
        greedily reabsorbs space, which makes dragging any divider *after* it
        feel inverted. With all sections Interactive, Path is simply given the
        remaining viewport width once at layout time via :meth:`_fit_path_column`.
        """
        header = self._table.horizontalHeader()
        header.setMinimumSectionSize(36)

        # Compact defaults for everything except Path (index 3), which is sized
        # to fill the leftover space in _fit_path_column().
        self._default_widths = {
            0: 44,    # #
            1: 66,    # Method
            2: 220,   # Host
            3: 320,   # Path (initial; recomputed to fill leftover width)
            4: 54,    # Ext
            5: 58,    # Status
            6: 130,   # Type (MIME)
            7: 72,    # Length
            8: 160,   # Cookies
            9: 76,    # Time (ms)
        }

        for col in range(self._model.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.Interactive)
            header.resizeSection(col, self._default_widths.get(col, 80))

        # Path (index 3) is the single flexible column: it absorbs or releases
        # the delta whenever any other column is dragged, keeping the total row
        # width invariant. We deliberately do NOT use setStretchLastSection here
        # — a stretch-pinned last column would compete with Path for the same
        # slack and make dragging feel inverted.
        header.sectionResized.connect(self._on_section_resized)

        # No horizontal scrollbar: Path reflows so the row always fits the
        # viewport, so the table never scrolls a column out of bounds.
        self._table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Rows as tall as the text, no extra padding.
        vheader = self._table.verticalHeader()
        row_h = self._table.fontMetrics().height() + 2
        vheader.setSectionResizeMode(QHeaderView.Fixed)
        vheader.setDefaultSectionSize(row_h)
        vheader.setMinimumSectionSize(row_h)

    _PATH_COL = 3
    _PATH_MIN_WIDTH = 120  # Path's floor when it's the one absorbing/being dragged.

    def _on_section_resized(self, logical_index: int, old_size: int, new_size: int) -> None:
        """Whenever a column is resized, compensate its immediate right neighbor
        (or left neighbor, if this is the last column) by the opposite delta, so
        the total row width stays invariant and the visual change stays local to
        the two columns touching the dragged divider — not some distant column.

        Path gets no special treatment as a "sink" anymore; it's just floored
        like any neighbor would be, whether it's the column being dragged or the
        column absorbing the delta.
        """
        if self._resizing_guard:
            return

        header = self._table.horizontalHeader()
        last_col = self._model.columnCount() - 1

        # Direct drag on Path's own edge: floor it before doing anything else.
        if logical_index == self._PATH_COL and new_size < self._PATH_MIN_WIDTH:
            self._resizing_guard = True
            try:
                header.resizeSection(self._PATH_COL, old_size)
            finally:
                self._resizing_guard = False
            return

        delta = new_size - old_size
        if delta == 0:
            return

        # The divider being dragged sits between logical_index and its right
        # neighbor (standard Qt convention) — except for the last column, which
        # has no right neighbor, so it borrows from the left instead.
        neighbor = logical_index + 1 if logical_index < last_col else logical_index - 1
        neighbor_min = (
            self._PATH_MIN_WIDTH if neighbor == self._PATH_COL
            else header.minimumSectionSize()
        )
        new_neighbor_w = header.sectionSize(neighbor) - delta

        self._resizing_guard = True
        try:
            if new_neighbor_w < neighbor_min:
                # Neighbor has no slack left — reject the drag, snap back.
                header.resizeSection(logical_index, old_size)
            else:
                header.resizeSection(neighbor, new_neighbor_w)
        finally:
            self._resizing_guard = False

    def _fit_path_column(self) -> None:
        """Reflow the Path column to absorb the viewport's leftover width.

        Path is the flexible column: it fills whatever space the other columns
        don't use, so the total always matches the viewport. That keeps the
        stretch-pinned last column flush against the right edge and prevents any
        column from spilling out of bounds when the window shrinks. Path keeps a
        draggable right edge (it's Interactive, not Stretch), so the user can
        still resize it; it just re-fills on the next view resize.
        """
        header = self._table.horizontalHeader()
        viewport_w = self._table.viewport().width()
        if viewport_w <= 0:
            return
        min_w = max(header.minimumSectionSize(), self._PATH_MIN_WIDTH)
        others = sum(
            header.sectionSize(c)
            for c in range(self._model.columnCount())
            if c != self._PATH_COL
        )
        self._resizing_guard = True
        try:
            header.resizeSection(self._PATH_COL, max(min_w, viewport_w - others))
        finally:
            self._resizing_guard = False

    def showEvent(self, event) -> None:  # noqa: N802 (Qt override)
        super().showEvent(event)
        self._fit_path_column()

    def resizeEvent(self, event) -> None:  # noqa: N802 (Qt override)
        super().resizeEvent(event)
        # Path reflows to keep the row width == viewport, so the last column
        # stays pinned to the right and nothing overflows.
        self._fit_path_column()

    def _add_shortcut(self, seq: str, handler) -> None:
        action = QAction(self)
        action.setShortcut(QKeySequence(seq))
        action.triggered.connect(handler)
        self.addAction(action)

    def _selected_record(self) -> FlowRecord | None:
        indexes = self._table.selectionModel().selectedRows()
        if not indexes:
            return None
        return self._model.record_at(indexes[0].row())

    @Slot()
    def _on_selection(self) -> None:
        record = self._selected_record()
        if record is None:
            return
        req_body = self._get_body(record, response=False)
        self._detail.show_request(record, req_body)
        resp_body = self._get_body(record, response=True)
        self._detail.show_response(record, resp_body)

    def _get_body(self, record: FlowRecord, response: bool):
        if callable(self.body_provider):
            return self.body_provider(record, response)
        return (record.response_body_inline if response
                else record.request_body_inline)

    def _on_context_menu(self, pos) -> None:
        record = self._selected_record()
        if record is None:
            index: QModelIndex = self._table.indexAt(pos)
            if index.isValid():
                record = self._model.record_at(index.row())
        if record is None:
            return
        menu = QMenu(self)
        act_rep = menu.addAction("Send to Repeater\tCtrl+R")
        act_int = menu.addAction("Send to Intruder\tCtrl+I")
        chosen = menu.exec(self._table.viewport().mapToGlobal(pos))
        if chosen == act_rep:
            self.send_to_repeater.emit(record)
        elif chosen == act_int:
            self.send_to_intruder.emit(record)

    def _emit_repeater(self) -> None:
        record = self._selected_record()
        if record is not None:
            self.send_to_repeater.emit(record)

    def _emit_intruder(self) -> None:
        record = self._selected_record()
        if record is not None:
            self.send_to_intruder.emit(record)

    def clear_detail(self) -> None:
        self._detail.clear()
