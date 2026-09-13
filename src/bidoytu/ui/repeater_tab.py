"""Repeater tab: edit a request and resend it, viewing the response.

Each request "loaded" here keeps the origin scheme/host/port from the source
flow so the raw editor only needs the request line + headers. Sending goes
through the shared :class:`AsyncHttpSender`.
"""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from bidoytu.http_utils import (
    build_request_text,
    host_from_headers_or_url,
    parse_request_text,
)
from bidoytu.net.async_sender import AsyncHttpSender, HttpResult
from bidoytu.storage.models import FlowRecord
from bidoytu.ui.message_view import MessageView


class RepeaterTab(QWidget):
    """A single-pane Repeater (one request/response at a time)."""

    _result_ready = Signal(object)  # HttpResult, marshalled to the UI thread

    def __init__(self, sender: AsyncHttpSender, parent=None) -> None:
        super().__init__(parent)
        self._sender = sender
        # Origin used to resolve relative request targets.
        self._scheme = "http"
        self._host = ""
        self._port = 80

        self._target_label = QLabel("No request loaded")
        self._send_btn = QPushButton("Send")
        self._send_btn.clicked.connect(self._on_send)
        self._send_btn.setEnabled(False)

        controls = QHBoxLayout()
        controls.addWidget(self._send_btn)
        controls.addSpacing(12)
        controls.addWidget(self._target_label)
        controls.addStretch(1)

        self._request_edit = MessageView(read_only=False)
        self._response_view = MessageView(read_only=True)
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self._pane("Request", self._request_edit))
        splitter.addWidget(self._pane("Response", self._response_view))
        splitter.setSizes([600, 600])

        layout = QVBoxLayout(self)
        layout.addLayout(controls)
        layout.addWidget(splitter)

        self._result_ready.connect(self._on_result)

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

    # -- loading a request ----------------------------------------------------

    def load_from_record(self, record: FlowRecord) -> None:
        self._scheme = record.scheme or "http"
        self._host = record.host
        self._port = record.port or (443 if self._scheme == "https" else 80)
        text = build_request_text(
            record.method, record.path, record.http_version,
            record.request_headers, record.request_body_inline,
        )
        self._request_edit.setPlainText(text)
        self._response_view.clear_message()
        self._target_label.setText(f"{self._scheme}://{self._host}:{self._port}")
        self._send_btn.setEnabled(True)

    # -- sending --------------------------------------------------------------

    @Slot()
    def _on_send(self) -> None:
        parsed = parse_request_text(self._request_edit.toPlainText())
        scheme, host, port, path = host_from_headers_or_url(
            parsed, self._host, self._scheme, self._port
        )
        if not host:
            self._response_view.setPlainText("Cannot send: no host (add a Host header).")
            return
        default_ports = {"http": 80, "https": 443}
        netloc = host if port == default_ports.get(scheme) else f"{host}:{port}"
        url = f"{scheme}://{netloc}{path}"

        self._send_btn.setEnabled(False)
        self._target_label.setText(f"Sending to {url} ...")
        self._sender.send(
            parsed.method, url, parsed.headers, parsed.body,
            lambda result: self._result_ready.emit(result),
        )

    @Slot(object)
    def _on_result(self, result: HttpResult) -> None:
        self._send_btn.setEnabled(True)
        if not result.ok:
            self._response_view.setPlainText(f"Error: {result.error}")
            self._target_label.setText("Request failed")
            return
        version = result.http_version or "HTTP/1.1"
        status_line = f"{version} {result.status_code} {result.reason}".strip()
        from bidoytu.ui.body_format import content_type_from_headers
        ct = content_type_from_headers(result.headers_text)
        self._response_view.show_message(status_line, result.headers_text, result.body, ct)
        self._target_label.setText(f"Done in {result.duration_ms:.0f} ms")
