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
        """Size columns so everything fits without a horizontal scrollbar.

        Host and Path grow to share the leftover width; the remaining columns
        get compact fixed widths. Column order (from FlowTableModel.COLUMNS):
        0 #, 1 Method, 2 Host, 3 Path, 4 Ext, 5 Status, 6 Type, 7 Length,
        8 Cookies, 9 Time (ms).
        """
        header = self._table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setMinimumSectionSize(36)

        # Path stretches to absorb spare width (it's usually the longest value);
        # Host gets a generous interactive default. Everything else is compact.
        # Column indices follow FlowTableModel.COLUMNS.
        interactive_widths = {
            0: 44,    # #        (smaller, per request)
            1: 66,    # Method
            2: 220,   # Host     (bigger default, per request)
            4: 54,    # Ext
            5: 58,    # Status
            6: 130,   # Type (MIME)
            7: 72,    # Length
            8: 160,   # Cookies
            9: 76,    # Time (ms)
        }
        stretch_col = 3  # Path

        for col in range(self._model.columnCount()):
            if col == stretch_col:
                header.setSectionResizeMode(col, QHeaderView.Stretch)
            else:
                header.setSectionResizeMode(col, QHeaderView.Interactive)
                header.resizeSection(col, interactive_widths.get(col, 80))

        # No horizontal scrollbar; Path reflows to fit whatever room is left.
        self._table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Rows as tall as the text, no extra padding.
        vheader = self._table.verticalHeader()
        row_h = self._table.fontMetrics().height() + 2
        vheader.setSectionResizeMode(QHeaderView.Fixed)
        vheader.setDefaultSectionSize(row_h)
        vheader.setMinimumSectionSize(row_h)

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
