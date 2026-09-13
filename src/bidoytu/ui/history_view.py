"""HTTP history: the traffic table plus a request/response detail view.

Emits a signal when a row is selected (so the owner can populate detail) and
exposes a context menu with "Send to Repeater/Intruder" actions.
"""
from __future__ import annotations

from PySide6.QtCore import QModelIndex, Qt, Signal, Slot
from PySide6.QtGui import QAction, QColor, QKeySequence, QPalette
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

        self._table = QTableView()
        self._table.setModel(model)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SingleSelection)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # Keep full-row selection, but only paint the highlight on the "#" column.
        # Make the view's own selection highlight transparent so neither the
        # native style nor the active stylesheet paints a row-wide blue band;
        # the delegate draws the "#" cell highlight explicitly instead.
        self._table.setItemDelegate(HistoryItemDelegate(self._table))
        pal = self._table.palette()
        pal.setColor(QPalette.Highlight, QColor(0, 0, 0, 0))
        pal.setColor(QPalette.HighlightedText, pal.color(QPalette.Text))
        self._table.setPalette(pal)
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

        # Pin the last column to the right edge (enabled AFTER per-section modes,
        # which would otherwise clear this flag). It always fills to the table's
        # right border, so dragging the divider before it resizes that column
        # in-bounds instead of pushing its right edge off-screen.
        header.setStretchLastSection(True)

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
        min_w = max(header.minimumSectionSize(), 120)
        others = sum(
            header.sectionSize(c)
            for c in range(self._model.columnCount())
            if c != self._PATH_COL
        )
        header.resizeSection(self._PATH_COL, max(min_w, viewport_w - others))

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
