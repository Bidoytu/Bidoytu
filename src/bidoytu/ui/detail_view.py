"""Reusable side-by-side request/response viewer.

Used by the Proxy history, the Intercept panel, and the Repeater tab. Provides
a soft-wrap toggle that applies to both panes. The request pane can be made
editable (Repeater / Intercept) or read-only (history).
"""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from bidoytu.http_utils import ensure_host_header
from bidoytu.storage.models import FlowRecord
from bidoytu.ui.body_format import content_type_from_headers
from bidoytu.ui.message_view import MessageView


class DetailView(QWidget):
    """Two MessageViews (request | response) with a shared soft-wrap toggle."""

    send_to_repeater = Signal(object)  # FlowRecord
    send_to_intruder = Signal(object)  # FlowRecord

    def __init__(self, parent=None, editable_request: bool = False) -> None:
        super().__init__(parent)
        self.request_view = MessageView(read_only=not editable_request)
        self.response_view = MessageView(read_only=True)
        self._current: FlowRecord | None = None

        # Right-click on the request pane offers the same send-to actions as the
        # history table, so the context menu "works" inside the request tab.
        self.request_view.add_context_action(
            "Send to Repeater",
            self._emit_repeater,
            lambda: self._current is not None,
        )
        self.request_view.add_context_action(
            "Send to Intruder",
            self._emit_intruder,
            lambda: self._current is not None,
        )

        self._wrap_toggle = QCheckBox("Wrap")
        self._wrap_toggle.setChecked(True)
        self._wrap_toggle.toggled.connect(self._on_wrap_toggled)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self._pane("Request", self.request_view))
        # The soft-wrap toggle rides on the Response pane's title row, so it no
        # longer needs a dedicated line above the panes.
        splitter.addWidget(
            self._pane("Response", self.response_view, trailing=self._wrap_toggle)
        )
        splitter.setSizes([600, 600])

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(splitter)

    @staticmethod
    def _pane(title: str, widget: QWidget, trailing: QWidget | None = None) -> QWidget:
        container = QWidget()
        v = QVBoxLayout(container)
        v.setContentsMargins(0, 0, 0, 0)

        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 4, 0)
        label = QLabel(title)
        label.setStyleSheet("font-weight: bold; padding: 4px;")
        title_row.addWidget(label)
        title_row.addStretch(1)
        if trailing is not None:
            title_row.addWidget(trailing)

        v.addLayout(title_row)
        v.addWidget(widget)
        return container

    def _on_wrap_toggled(self, enabled: bool) -> None:
        self.request_view.set_soft_wrap(enabled)
        self.response_view.set_soft_wrap(enabled)

    def _emit_repeater(self) -> None:
        if self._current is not None:
            self.send_to_repeater.emit(self._current)

    def _emit_intruder(self) -> None:
        if self._current is not None:
            self.send_to_intruder.emit(self._current)

    # -- populate -------------------------------------------------------------

    def show_request(self, record: FlowRecord, body: bytes | None) -> None:
        self._current = record
        req_line = f"{record.method} {record.path} {record.http_version}".strip()
        headers = ensure_host_header(
            record.request_headers, record.host, record.port, record.scheme
        )
        ct = content_type_from_headers(headers)
        self.request_view.show_message(req_line, headers, body, ct)

    def show_response(self, record: FlowRecord, body: bytes | None) -> None:
        if record.status_code is None:
            self.response_view.clear_message()
            return
        status_line = f"{record.http_version} {record.status_code} {record.reason}".strip()
        ct = record.content_type or content_type_from_headers(record.response_headers)
        self.response_view.show_message(status_line, record.response_headers, body, ct)

    def clear(self) -> None:
        self._current = None
        self.request_view.clear_message()
        self.response_view.clear_message()
