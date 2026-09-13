"""Intruder tab (skeleton).

Base scaffold only: it accepts a request template (via "Send to Intruder") and
lays out the pieces a full Intruder needs - a request template with payload
markers and a payload list. The attack runner (iterating payloads through the
shared AsyncHttpSender and collecting results) is intentionally left as the
next step so the base stays focused.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from bidoytu.http_utils import build_request_text
from bidoytu.net.async_sender import AsyncHttpSender
from bidoytu.storage.models import FlowRecord
from bidoytu.ui.message_view import MessageView


class IntruderTab(QWidget):
    """Skeleton Intruder: request template + payloads + (future) attack."""

    def __init__(self, sender: AsyncHttpSender, parent=None) -> None:
        super().__init__(parent)
        self._sender = sender
        self._scheme = "http"
        self._host = ""
        self._port = 80

        self._target_label = QLabel("No request loaded")
        self._start_btn = QPushButton("Start attack")
        self._start_btn.setEnabled(False)
        self._start_btn.setToolTip(
            "Attack execution is not implemented in the base yet. "
            "Mark payload positions with § markers and add payloads."
        )

        controls = QHBoxLayout()
        controls.addWidget(self._start_btn)
        controls.addSpacing(12)
        controls.addWidget(self._target_label)
        controls.addStretch(1)

        self._template = MessageView(read_only=False)

        self._payloads = QPlainTextEdit()
        self._payloads.setPlaceholderText("One payload per line...")

        payload_pane = QWidget()
        pv = QVBoxLayout(payload_pane)
        pv.setContentsMargins(0, 0, 0, 0)
        lbl = QLabel("Payloads")
        lbl.setStyleSheet("font-weight: bold; padding: 4px;")
        pv.addWidget(lbl)
        pv.addWidget(self._payloads)

        template_pane = QWidget()
        tv = QVBoxLayout(template_pane)
        tv.setContentsMargins(0, 0, 0, 0)
        tlbl = QLabel("Request template (mark positions with §payload§)")
        tlbl.setStyleSheet("font-weight: bold; padding: 4px;")
        tv.addWidget(tlbl)
        tv.addWidget(self._template)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(template_pane)
        splitter.addWidget(payload_pane)
        splitter.setSizes([750, 350])

        layout = QVBoxLayout(self)
        layout.addLayout(controls)
        layout.addWidget(splitter)

    def load_from_record(self, record: FlowRecord) -> None:
        self._scheme = record.scheme or "http"
        self._host = record.host
        self._port = record.port or (443 if self._scheme == "https" else 80)
        text = build_request_text(
            record.method, record.path, record.http_version,
            record.request_headers, record.request_body_inline,
            host=record.host, port=record.port, scheme=record.scheme,
        )
        self._template.setPlainText(text)
        self._target_label.setText(f"{self._scheme}://{self._host}:{self._port}")
