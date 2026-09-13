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

from typing import Callable, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMenu,
    QPushButton,
    QSplitter,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from bidoytu.http_utils import build_request_text
from bidoytu.storage.models import FlowRecord
from bidoytu.ui.body_format import content_type_from_headers
from bidoytu.ui.intercept_activity_model import InterceptActivityModel
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

        # The flow currently loaded in the editor (selected in the table).
        self._current: Optional[FlowRecord] = None
        # Flows we have forwarded and are awaiting a response for, so we can
        # display the response when it arrives.
        self._awaiting_response: dict[str, FlowRecord] = {}
        # The flow whose response is currently shown on the right.
        self._shown_flow_id: Optional[str] = None
        # Edited request text kept per pending flow, so switching selection
        # between paused requests preserves in-progress edits.
        self._edits: dict[str, str] = {}

        self._toggle_btn = QPushButton("Intercept is off")
        self._toggle_btn.setCheckable(True)
        self._toggle_btn.toggled.connect(self._on_toggle)

        self._forward_btn = QPushButton("Forward")
        self._drop_btn = QPushButton("Drop")
        self._forward_all_btn = QPushButton("Forward All")
        self._drop_all_btn = QPushButton("Drop All")
        self._forward_btn.clicked.connect(self._on_forward_clicked)
        self._drop_btn.clicked.connect(self._on_drop_clicked)
        self._forward_all_btn.clicked.connect(self._on_forward_all)
        self._drop_all_btn.clicked.connect(self._on_drop_all)

        self._status = QLabel("No intercepted requests.")

        controls = QHBoxLayout()
        controls.addWidget(self._toggle_btn)
        controls.addWidget(self._forward_btn)
        controls.addWidget(self._drop_btn)
        controls.addWidget(self._forward_all_btn)
        controls.addWidget(self._drop_all_btn)
        controls.addStretch(1)
        controls.addWidget(self._status)

        # Activity log of intercepted traffic (requests as they pause, responses
        # as they return). The table is the source of truth for pending flows.
        self._activity_model = InterceptActivityModel(self)
        self._activity_table = QTableView()
        self._activity_table.setModel(self._activity_model)
        self._activity_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._activity_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self._activity_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._activity_table.verticalHeader().setVisible(False)
        self._activity_table.selectionModel().selectionChanged.connect(
            self._on_activity_selection
        )
        self._configure_activity_columns()
        # Now that the model exists, initialize the action buttons.
        self._set_action_buttons_enabled(False)

        # Request (editable) + response (read-only) side by side.
        self._editor = MessageView(read_only=False)
        self._editor.setContextMenuPolicy(Qt.CustomContextMenu)
        self._editor.customContextMenuRequested.connect(self._on_context_menu)
        self._response_view = MessageView(read_only=True)

        msg_splitter = QSplitter(Qt.Horizontal)
        msg_splitter.addWidget(self._pane("Request", self._editor))
        msg_splitter.addWidget(self._pane("Response", self._response_view))
        msg_splitter.setSizes([600, 600])

        outer = QSplitter(Qt.Vertical)
        outer.addWidget(self._pane("Intercepted traffic", self._activity_table))
        outer.addWidget(msg_splitter)
        outer.setSizes([220, 480])

        layout = QVBoxLayout(self)
        layout.addLayout(controls)
        layout.addWidget(outer)

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

    def _configure_activity_columns(self) -> None:
        """Size the activity table so URL stretches and the rest stay compact.

        Columns (from InterceptActivityModel.COLUMNS):
        0 Time, 1 Type, 2 Direction, 3 Method, 4 URL, 5 Status, 6 Length.
        """
        header = self._activity_table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setMinimumSectionSize(36)
        widths = {
            0: 76,    # Time
            1: 120,   # Type (MIME)
            2: 78,    # Direction
            3: 68,    # Method
            5: 58,    # Status
            6: 72,    # Length
        }
        stretch_col = 4  # URL
        for col in range(self._activity_model.columnCount()):
            if col == stretch_col:
                header.setSectionResizeMode(col, QHeaderView.Stretch)
            else:
                header.setSectionResizeMode(col, QHeaderView.Interactive)
                header.resizeSection(col, widths.get(col, 80))
        self._activity_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # Show a vertical scrollbar when the row count exceeds the visible area.
        self._activity_table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Rows as tall as the text, no extra padding.
        vheader = self._activity_table.verticalHeader()
        row_h = self._activity_table.fontMetrics().height() + 2
        vheader.setSectionResizeMode(QHeaderView.Fixed)
        vheader.setDefaultSectionSize(row_h)
        vheader.setMinimumSectionSize(row_h)

    # -- intercept toggle -----------------------------------------------------

    def _on_toggle(self, checked: bool) -> None:
        self._toggle_btn.setText("Intercept is on" if checked else "Intercept is off")
        if self.on_toggle_intercept:
            self.on_toggle_intercept(checked)

    def is_intercepting(self) -> bool:
        return self._toggle_btn.isChecked()

    # -- incoming paused flows ------------------------------------------------

    def enqueue(self, record: FlowRecord) -> None:
        """A flow was paused by the proxy; add it to the table."""
        row = self._activity_model.add_request(record)
        self._activity_table.scrollToBottom()
        # Auto-select the first paused request when nothing is being edited yet.
        if self._current is None:
            self._activity_table.selectRow(row)
        self._update_status()

    def _on_activity_selection(self) -> None:
        """The user picked a row in the activity table; show that flow."""
        indexes = self._activity_table.selectionModel().selectedRows()
        if not indexes:
            return
        # Preserve any in-progress edit on the flow we're leaving.
        self._stash_current_edit()
        row = indexes[0].row()
        record = self._activity_model.record_at(row)
        if record is None:
            return
        pending = self._activity_model.is_pending(row)
        self._show(record, pending)

    def _show(self, record: FlowRecord, pending: bool) -> None:
        self._current = record if pending else None
        # Restore any in-progress edit for a pending flow, else rebuild text.
        if pending and record.flow_id in self._edits:
            text = self._edits[record.flow_id]
        else:
            text = build_request_text(
                record.method, record.path, record.http_version,
                record.request_headers, record.request_body_inline,
                host=record.host, port=record.port, scheme=record.scheme,
            )
        self._editor.setPlainText(text)
        self._editor.setReadOnly(not pending)
        self._shown_flow_id = record.flow_id
        # Response pane: show a stored response if we have one for this flow.
        self._response_view.clear_message()
        self._set_action_buttons_enabled(pending)
        self._update_status()

    def _stash_current_edit(self) -> None:
        """Remember the editor text for the currently selected pending flow."""
        if self._current is not None:
            self._edits[self._current.flow_id] = self._editor.toPlainText()

    def _select_next_pending(self) -> None:
        """Select the first still-pending request, or clear the editor."""
        row = self._activity_model.first_pending_row()
        if row is not None:
            self._activity_table.selectRow(row)
        else:
            self._current = None
            self._editor.clear()
            self._set_action_buttons_enabled(False)
            self._update_status()

    # -- response correlation -------------------------------------------------

    def on_response(self, record: FlowRecord) -> None:
        """A response arrived. If we forwarded this flow from the intercept
        panel, show its response in the Response pane."""
        if record.flow_id not in self._awaiting_response:
            return
        self._awaiting_response.pop(record.flow_id, None)
        # Paint it when this forwarded flow is the one whose response we're
        # showing (set at forward time), or nothing else has taken the pane.
        if self._shown_flow_id in (record.flow_id, None):
            self._shown_flow_id = record.flow_id
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
        record = self._current
        flow_id = record.flow_id
        edited = self._editor.toPlainText()
        # Remember we're expecting this flow's response so we can show it.
        self._awaiting_response[flow_id] = record
        self._shown_flow_id = flow_id
        if self.on_forward:
            self.on_forward(flow_id, edited)
        self._edits.pop(flow_id, None)
        # Remove the resolved request from the table; keep the request text in
        # the editor (read-only) so the response lands next to it.
        self._current = None
        self._activity_model.remove_flow(flow_id)
        self._editor.setReadOnly(True)
        self._set_action_buttons_enabled(False)
        self._update_status()

    def _on_drop_clicked(self) -> None:
        if self._current is None:
            return
        flow_id = self._current.flow_id
        if self.on_drop:
            self.on_drop(flow_id)
        self._edits.pop(flow_id, None)
        self._awaiting_response.pop(flow_id, None)
        self._current = None
        self._activity_model.remove_flow(flow_id)
        # Drops have no response; move on to the next pending request.
        self._response_view.clear_message()
        self._select_next_pending()

    def _on_forward_all(self) -> None:
        """Forward every still-pending flow. The selected one uses its edited
        text; the rest are forwarded as captured. Rows are removed as resolved."""
        self._stash_current_edit()
        for flow_id in self._activity_model.pending_flow_ids():
            edited = self._edits.get(flow_id)
            if self.on_forward:
                self.on_forward(flow_id, edited)
            self._awaiting_response[flow_id] = self._activity_model_record(flow_id)
            self._activity_model.remove_flow(flow_id)
        self._edits.clear()
        # Nothing left to edit; leave the response pane for whichever forwarded
        # flow's response was last shown.
        self._current = None
        self._editor.setReadOnly(True)
        self._set_action_buttons_enabled(False)
        self._update_status()

    def _on_drop_all(self) -> None:
        """Drop every still-pending flow and remove their rows."""
        for flow_id in self._activity_model.pending_flow_ids():
            if self.on_drop:
                self.on_drop(flow_id)
            self._awaiting_response.pop(flow_id, None)
            self._activity_model.remove_flow(flow_id)
        self._edits.clear()
        self._current = None
        self._editor.clear()
        self._response_view.clear_message()
        self._set_action_buttons_enabled(False)
        self._update_status()

    def _activity_model_record(self, flow_id: str):
        """Find the FlowRecord for a flow_id currently in the table."""
        for i in range(self._activity_model.rowCount()):
            rec = self._activity_model.record_at(i)
            if rec is not None and rec.flow_id == flow_id:
                return rec
        return None

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
        # Forward/Drop act on the selected pending flow.
        self._forward_btn.setEnabled(enabled)
        self._drop_btn.setEnabled(enabled)
        # Forward All / Drop All are enabled whenever anything is still pending.
        has_pending = bool(self._activity_model.pending_flow_ids())
        self._forward_all_btn.setEnabled(has_pending)
        self._drop_all_btn.setEnabled(has_pending)

    def _update_status(self) -> None:
        pending = self._activity_model.pending_flow_ids()
        if not pending:
            self._status.setText("No pending requests.")
            return
        if self._current is not None:
            self._status.setText(
                f"Editing: {self._current.method} "
                f"{self._current.host}{self._current.path}  "
                f"({len(pending)} pending)"
            )
        else:
            self._status.setText(f"{len(pending)} pending request(s).")
