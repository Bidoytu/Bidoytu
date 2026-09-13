"""HTTP history: the traffic table plus a request/response detail view.

Emits a signal when a row is selected (so the owner can populate detail) and
exposes a context menu with "Send to Repeater/Intruder" actions.
"""
from __future__ import annotations

from PySide6.QtCore import QModelIndex, Qt, Signal, Slot
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QAbstractItemView,
    QMenu,
    QSplitter,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from bidoytu.storage.models import FlowRecord
from bidoytu.ui.detail_view import DetailView
from bidoytu.ui.flow_table_model import FlowTableModel


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
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.verticalHeader().setVisible(False)
        self._table.setContextMenuPolicy(Qt.CustomContextMenu)
        self._table.customContextMenuRequested.connect(self._on_context_menu)

        self._detail = DetailView(editable_request=False)

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
