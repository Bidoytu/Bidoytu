"""Reusable side-by-side request/response viewer.

Used by the Proxy history, the Intercept panel, and the Repeater tab. Provides
a soft-wrap toggle that applies to both panes. The request pane can be made
editable (Repeater / Intercept) or read-only (history).
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from bidoytu.storage.models import FlowRecord
from bidoytu.ui.body_format import content_type_from_headers
from bidoytu.ui.message_view import MessageView


class DetailView(QWidget):
    """Two MessageViews (request | response) with a shared soft-wrap toggle."""

    def __init__(self, parent=None, editable_request: bool = False) -> None:
        super().__init__(parent)
        self.request_view = MessageView(read_only=not editable_request)
        self.response_view = MessageView(read_only=True)

        self._wrap_toggle = QCheckBox("Soft wrap")
        self._wrap_toggle.setChecked(True)
        self._wrap_toggle.toggled.connect(self._on_wrap_toggled)

        header = QHBoxLayout()
        header.setContentsMargins(4, 2, 4, 2)
        header.addStretch(1)
        header.addWidget(self._wrap_toggle)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self._pane("Request", self.request_view))
        splitter.addWidget(self._pane("Response", self.response_view))
        splitter.setSizes([600, 600])

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(header)
        layout.addWidget(splitter)

    @staticmethod
    def _pane(title: str, widget: QWidget) -> QWidget:
        container = QWidget()
        v = QVBoxLayout(container)
        v.setContentsMargins(0, 0, 0, 0)
        label = QLabel(title)
        label.setStyleSheet("font-weight: bold; padding: 4px;")
        v.addWidget(label)
        v.addWidget(widget)
        return container

    def _on_wrap_toggled(self, enabled: bool) -> None:
        self.request_view.set_soft_wrap(enabled)
        self.response_view.set_soft_wrap(enabled)

    # -- populate -------------------------------------------------------------

    def show_request(self, record: FlowRecord, body: bytes | None) -> None:
        req_line = f"{record.method} {record.path} {record.http_version}".strip()
        ct = content_type_from_headers(record.request_headers)
        self.request_view.show_message(req_line, record.request_headers, body, ct)

    def show_response(self, record: FlowRecord, body: bytes | None) -> None:
        if record.status_code is None:
            self.response_view.clear_message()
            return
        status_line = f"{record.http_version} {record.status_code} {record.reason}".strip()
        ct = record.content_type or content_type_from_headers(record.response_headers)
        self.response_view.show_message(status_line, record.response_headers, body, ct)

    def clear(self) -> None:
        self.request_view.clear_message()
        self.response_view.clear_message()
