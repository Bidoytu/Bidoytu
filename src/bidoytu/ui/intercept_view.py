"""Intercept panel: pause, edit, and forward/drop in-flight requests.

When interception is on, the proxy pauses each request and emits it here. The
panel shows one paused flow at a time (others queue). The user can:
    - edit the raw request text, then Forward (edits applied) or Drop it;
    - after forwarding, see the response for that flow (correlated by flow_id);
    - right-click the request to Send to Repeater / Intruder.

The panel does not touch the proxy loop directly; it calls back into the owner
(MainWindow) which drives :class:`ProxyEngine`.
"""
from __future__ import annotations

from collections import deque
from typing import Callable, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMenu,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from bidoytu.http_utils import build_request_text
from bidoytu.storage.models import FlowRecord
from bidoytu.ui.body_format import content_type_from_headers
from bidoytu.ui.message_view import MessageView


class InterceptView(QWidget):
    """UI for reviewing and resolving intercepted requests + their responses."""

    send_to_repeater = Signal(object)  # FlowRecord
    send_to_intruder = Signal(object)  # FlowRecord

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        # Callbacks wired by the owner.
        self.on_toggle_intercept: Optional[Callable[[bool], None]] = None
        self.on_forward: Optional[Callable[[str, str], None]] = None  # (flow_id, edited_text)
        self.on_drop: Optional[Callable[[str], None]] = None          # (flow_id)

        self._queue: deque[FlowRecord] = deque()
        self._current: Optional[FlowRecord] = None
        # Flows we have forwarded and are awaiting a response for, so we can
        # display the response when it arrives.
        self._awaiting_response: dict[str, FlowRecord] = {}
        # The flow whose response is currently shown on the right.
        self._shown_flow_id: Optional[str] = None

        self._toggle_btn = QPushButton("Intercept is off")
        self._toggle_btn.setCheckable(True)
        self._toggle_btn.toggled.connect(self._on_toggle)

        self._forward_btn = QPushButton("Forward")
        self._drop_btn = QPushButton("Drop")
        self._forward_btn.clicked.connect(self._on_forward_clicked)
        self._drop_btn.clicked.connect(self._on_drop_clicked)
        self._set_action_buttons_enabled(False)

        self._status = QLabel("No intercepted requests.")

        controls = QHBoxLayout()
        controls.addWidget(self._toggle_btn)
        controls.addWidget(self._forward_btn)
        controls.addWidget(self._drop_btn)
        controls.addStretch(1)
        controls.addWidget(self._status)

        # Request (editable) + response (read-only) side by side.
        self._editor = MessageView(read_only=False)
        self._editor.setContextMenuPolicy(Qt.CustomContextMenu)
        self._editor.customContextMenuRequested.connect(self._on_context_menu)
        self._response_view = MessageView(read_only=True)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self._pane("Request (editable)", self._editor))
        splitter.addWidget(self._pane("Response", self._response_view))
        splitter.setSizes([600, 600])

        layout = QVBoxLayout(self)
        layout.addLayout(controls)
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

    # -- intercept toggle -----------------------------------------------------

    def _on_toggle(self, checked: bool) -> None:
        self._toggle_btn.setText("Intercept is on" if checked else "Intercept is off")
        if self.on_toggle_intercept:
            self.on_toggle_intercept(checked)

    def is_intercepting(self) -> bool:
        return self._toggle_btn.isChecked()

    # -- incoming paused flows ------------------------------------------------

    def enqueue(self, record: FlowRecord) -> None:
        """A flow was paused by the proxy; show it or queue it."""
        if self._current is None:
            self._show(record)
        else:
            self._queue.append(record)
            self._update_status()

    def _show(self, record: FlowRecord) -> None:
        self._current = record
        text = build_request_text(
            record.method, record.path, record.http_version,
            record.request_headers, record.request_body_inline,
        )
        self._editor.setPlainText(text)
        self._response_view.clear_message()
        self._shown_flow_id = record.flow_id
        self._set_action_buttons_enabled(True)
        self._update_status()

    def _advance(self) -> None:
        self._current = None
        self._editor.clear()
        self._set_action_buttons_enabled(False)
        if self._queue:
            self._show(self._queue.popleft())
        else:
            self._update_status()

    # -- response correlation -------------------------------------------------

    def on_response(self, record: FlowRecord) -> None:
        """A response arrived for a flow. If we forwarded it from here (and it
        is the one currently displayed), show the response."""
        if record.flow_id not in self._awaiting_response:
            return
        self._awaiting_response.pop(record.flow_id, None)
        # Only paint it if this flow is the one on screen (or nothing is shown).
        if self._shown_flow_id in (record.flow_id, None):
            body = record.response_body_inline
            status_line = (
                f"{record.http_version} {record.status_code} {record.reason}".strip()
            )
            ct = record.content_type or content_type_from_headers(record.response_headers)
            self._response_view.show_message(status_line, record.response_headers, body, ct)

    # -- forward / drop -------------------------------------------------------

    def _on_forward_clicked(self) -> None:
        if self._current is None:
            return
        flow_id = self._current.flow_id
        edited = self._editor.toPlainText()
        # Remember we're expecting this flow's response so we can show it.
        self._awaiting_response[flow_id] = self._current
        self._shown_flow_id = flow_id
        if self.on_forward:
            self.on_forward(flow_id, edited)
        self._advance_keep_response()

    def _on_drop_clicked(self) -> None:
        if self._current is None:
            return
        flow_id = self._current.flow_id
        if self.on_drop:
            self.on_drop(flow_id)
        self._advance()

    def _advance_keep_response(self) -> None:
        """Like _advance, but keep the response pane (awaiting a response)."""
        self._current = None
        self._editor.clear()
        self._set_action_buttons_enabled(False)
        if self._queue:
            # Showing the next request clears the response pane; that's fine,
            # the just-forwarded response will still populate if it is quick.
            self._show(self._queue.popleft())
        else:
            self._update_status()

    # -- context menu / send-to -----------------------------------------------

    def _on_context_menu(self, pos) -> None:
        record = self._current_as_record()
        menu = QMenu(self)
        act_rep = menu.addAction("Send to Repeater\tCtrl+R")
        act_int = menu.addAction("Send to Intruder\tCtrl+I")
        # Disable when there is nothing to send.
        act_rep.setEnabled(record is not None)
        act_int.setEnabled(record is not None)
        chosen = menu.exec(self._editor.viewport().mapToGlobal(pos))
        if record is None:
            return
        if chosen == act_rep:
            self.send_to_repeater.emit(record)
        elif chosen == act_int:
            self.send_to_intruder.emit(record)

    def _current_as_record(self) -> Optional[FlowRecord]:
        """Build a FlowRecord from the (possibly edited) request in the editor.

        Uses the current intercepted flow for origin (scheme/host/port), and
        the edited text for method/path/headers/body.
        """
        if self._current is None:
            return None
        from bidoytu.http_utils import parse_request_text

        parsed = parse_request_text(self._editor.toPlainText())
        base = self._current
        return FlowRecord(
            flow_id=base.flow_id,
            method=parsed.method,
            scheme=base.scheme,
            host=base.host,
            port=base.port,
            path=parsed.path,
            http_version=parsed.http_version,
            request_headers="\r\n".join(f"{k}: {v}" for k, v in parsed.headers),
            request_body_inline=parsed.body or None,
            request_body_size=len(parsed.body),
        )

    # -- helpers --------------------------------------------------------------

    def _set_action_buttons_enabled(self, enabled: bool) -> None:
        self._forward_btn.setEnabled(enabled)
        self._drop_btn.setEnabled(enabled)

    def _update_status(self) -> None:
        if self._current is None:
            self._status.setText("No intercepted requests.")
        else:
            pending = len(self._queue)
            extra = f" (+{pending} queued)" if pending else ""
            self._status.setText(
                f"Intercepted: {self._current.method} "
                f"{self._current.host}{self._current.path}{extra}"
            )
