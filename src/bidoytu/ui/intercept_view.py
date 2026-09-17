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
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMenu,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from bidoytu.http_utils import build_request_text, build_response_text
from bidoytu.storage.models import FlowRecord
from bidoytu.ui.body_format import content_type_from_headers
from bidoytu.ui.intercept_activity_model import (
    REQUEST,
    RESPONSE,
    InterceptActivityModel,
)
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
        # Response interception callbacks.
        self.on_toggle_intercept_responses: Optional[Callable[[bool], None]] = None
        self.on_intercept_response_for: Optional[Callable[[str], None]] = None  # (flow_id)
        self.on_forward_response: Optional[Callable[[str, str], None]] = None   # (flow_id, edited_text)
        self.on_drop_response: Optional[Callable[[str], None]] = None           # (flow_id)

        # The flow currently loaded in the editor (selected in the table).
        self._current: Optional[FlowRecord] = None
        # Whether the current selection is a paused request or a paused response.
        # One of REQUEST / RESPONSE / "" (nothing editable).
        self._current_kind: str = ""
        # Flows we have forwarded and are awaiting a response for, so we can
        # display the response when it arrives.
        self._awaiting_response: dict[str, FlowRecord] = {}
        # The flow whose response is currently shown on the right.
        self._shown_flow_id: Optional[str] = None
        # Edited request text kept per pending flow, so switching selection
        # between paused requests preserves in-progress edits.
        self._edits: dict[str, str] = {}
        # Edited response text kept per pending response flow.
        self._response_edits: dict[str, str] = {}

        # Re-entrancy guard: our own resizeSection() calls emit sectionResized
        # again, which would recurse into the handler. Set while we adjust URL.
        self._resizing_guard = False

        self._toggle_btn = QPushButton("Intercept is off")
        self._toggle_btn.setCheckable(True)
        self._toggle_btn.toggled.connect(self._on_toggle)

        # Global "intercept responses" switch (Burp/Caido style). When checked,
        # every response is paused for review, not just requests.
        self._intercept_responses_cb = QCheckBox("Intercept responses")
        self._intercept_responses_cb.setToolTip(
            "Pause and review every response, not just requests."
        )
        self._intercept_responses_cb.toggled.connect(self._on_toggle_responses)

        self._forward_btn = QPushButton("Forward")
        self._drop_btn = QPushButton("Drop")
        self._forward_all_btn = QPushButton("Forward All")
        self._drop_all_btn = QPushButton("Drop All")
        self._forward_btn.clicked.connect(self._on_forward_clicked)
        self._drop_btn.clicked.connect(self._on_drop_clicked)
        self._forward_all_btn.clicked.connect(self._on_forward_all)
        self._drop_all_btn.clicked.connect(self._on_drop_all)

        # Clears the HTTP history; wired by the owner (MainWindow). Lives in
        # this control row alongside the forward/drop actions.
        self.clear_history_btn = QPushButton("Clear History")

        self._status = QLabel("No intercepted requests.")
        # Don't let a long status string (it can include a big URL) force the
        # window wider. The label reports its full text as its minimum width by
        # default, so pin the horizontal policy to Ignored and let it shrink.
        self._status.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        self._status.setMinimumWidth(0)
        self._status.setTextInteractionFlags(Qt.TextSelectableByMouse)

        controls = QHBoxLayout()
        controls.addWidget(self._toggle_btn)
        controls.addWidget(self._intercept_responses_cb)
        controls.addWidget(self._forward_btn)
        controls.addWidget(self._drop_btn)
        controls.addWidget(self._forward_all_btn)
        controls.addWidget(self._drop_all_btn)
        controls.addWidget(self.clear_history_btn)
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

        # Request (editable) + response (editable while a response is paused)
        # side by side.
        self._editor = MessageView(read_only=False)
        self._editor.setContextMenuPolicy(Qt.CustomContextMenu)
        self._editor.customContextMenuRequested.connect(self._on_context_menu)
        self._response_view = MessageView(read_only=True)
        self._response_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self._response_view.customContextMenuRequested.connect(self._on_context_menu)

        # Keyboard shortcuts: Ctrl+R -> Repeater, Ctrl+I -> Intruder.
        self._add_shortcut("Ctrl+R", self._emit_send_to_repeater)
        self._add_shortcut("Ctrl+I", self._emit_send_to_intruder)

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
        v.setContentsMargins(0, 4, 0, 0)
        label = QLabel(title)
        label.setStyleSheet("font-weight: bold; padding: 4px;")
        v.addWidget(label)
        v.addWidget(widget)
        return container

    _URL_COL = 4
    _URL_MIN_WIDTH = 120  # URL's floor when it's the one absorbing/being dragged.

    def _configure_activity_columns(self) -> None:
        """Size the activity table so URL fills the leftover width, while every
        column divider stays freely draggable.

        Columns (from InterceptActivityModel.COLUMNS):
        0 Time, 1 Type, 2 Direction, 3 Method, 4 URL, 5 Status, 6 Length.

        Every column uses Interactive resize mode. We deliberately avoid
        QHeaderView.Stretch on URL: a stretch section has no draggable right
        edge and greedily reabsorbs space, which makes dragging any divider
        after it feel inverted. Instead URL is given the leftover viewport width
        via :meth:`_fit_url_column`, and divider drags compensate the immediate
        neighbor via :meth:`_on_activity_section_resized`.
        """
        header = self._activity_table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setMinimumSectionSize(36)
        self._activity_default_widths = {
            0: 76,    # Time
            1: 120,   # Type (MIME)
            2: 78,    # Direction
            3: 68,    # Method
            4: 300,   # URL (initial; recomputed to fill leftover width)
            5: 58,    # Status
            6: 72,    # Length
        }
        for col in range(self._activity_model.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.Interactive)
            header.resizeSection(col, self._activity_default_widths.get(col, 80))

        # URL (index 4) is the flexible column: divider drags compensate the
        # immediate neighbor, keeping the visual change local to the two columns
        # touching the dragged divider.
        header.sectionResized.connect(self._on_activity_section_resized)

        self._activity_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # Show a vertical scrollbar when the row count exceeds the visible area.
        self._activity_table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Rows as tall as the text, no extra padding.
        vheader = self._activity_table.verticalHeader()
        row_h = self._activity_table.fontMetrics().height() + 2
        vheader.setSectionResizeMode(QHeaderView.Fixed)
        vheader.setDefaultSectionSize(row_h)
        vheader.setMinimumSectionSize(row_h)

    def _on_activity_section_resized(self, logical_index: int, old_size: int, new_size: int) -> None:
        """Whenever a column is resized, compensate its immediate right neighbor
        (or left neighbor, if this is the last column) by the opposite delta, so
        the total row width stays invariant and the visual change stays local to
        the two columns touching the dragged divider - not some distant column.

        URL gets no special treatment as a "sink"; it's just floored like any
        neighbor would be, whether it's the column being dragged or the column
        absorbing the delta.
        """
        if self._resizing_guard:
            return

        header = self._activity_table.horizontalHeader()
        last_col = self._activity_model.columnCount() - 1

        # Direct drag on URL's own edge: floor it before doing anything else.
        if logical_index == self._URL_COL and new_size < self._URL_MIN_WIDTH:
            self._resizing_guard = True
            try:
                header.resizeSection(self._URL_COL, old_size)
            finally:
                self._resizing_guard = False
            return

        delta = new_size - old_size
        if delta == 0:
            return

        # The divider being dragged sits between logical_index and its right
        # neighbor (standard Qt convention) - except for the last column, which
        # has no right neighbor, so it borrows from the left instead.
        neighbor = logical_index + 1 if logical_index < last_col else logical_index - 1
        neighbor_min = (
            self._URL_MIN_WIDTH if neighbor == self._URL_COL
            else header.minimumSectionSize()
        )
        new_neighbor_w = header.sectionSize(neighbor) - delta

        self._resizing_guard = True
        try:
            if new_neighbor_w < neighbor_min:
                # Neighbor has no slack left - reject the drag, snap back.
                header.resizeSection(logical_index, old_size)
            else:
                header.resizeSection(neighbor, new_neighbor_w)
        finally:
            self._resizing_guard = False

    def _fit_url_column(self) -> None:
        """Reflow the URL column to absorb the viewport's leftover width.

        URL is the flexible column: it fills whatever space the other columns
        don't use, so the total always matches the viewport and nothing spills
        out of bounds when the panel shrinks. URL keeps a draggable right edge
        (it's Interactive, not Stretch); it just re-fills on the next resize.
        """
        header = self._activity_table.horizontalHeader()
        viewport_w = self._activity_table.viewport().width()
        if viewport_w <= 0:
            return
        min_w = max(header.minimumSectionSize(), self._URL_MIN_WIDTH)
        others = sum(
            header.sectionSize(c)
            for c in range(self._activity_model.columnCount())
            if c != self._URL_COL
        )
        self._resizing_guard = True
        try:
            header.resizeSection(self._URL_COL, max(min_w, viewport_w - others))
        finally:
            self._resizing_guard = False

    def showEvent(self, event) -> None:  # noqa: N802 (Qt override)
        super().showEvent(event)
        self._fit_url_column()

    def resizeEvent(self, event) -> None:  # noqa: N802 (Qt override)
        super().resizeEvent(event)
        # URL reflows to keep the row width == viewport, so nothing overflows.
        self._fit_url_column()

    # -- intercept toggle -----------------------------------------------------

    def _on_toggle(self, checked: bool) -> None:
        self._toggle_btn.setText("Intercept is on" if checked else "Intercept is off")
        # When turning off, forward anything still paused (with edits) and clear
        # the table before disabling interception, so the selected flow's edits
        # aren't dropped by the addon releasing paused flows unedited.
        if not checked:
            self._forward_pending_and_clear()
        if self.on_toggle_intercept:
            self.on_toggle_intercept(checked)

    def _on_toggle_responses(self, checked: bool) -> None:
        if self.on_toggle_intercept_responses:
            self.on_toggle_intercept_responses(checked)

    def _forward_pending_and_clear(self) -> None:
        """Forward every still-pending flow, then reset the panel.

        Called when interception is switched off: no requests should stay
        paused, and the activity log starts fresh. The selected flow keeps its
        in-progress edit; the rest are forwarded as captured.
        """
        self._stash_current_edit()
        for flow_id in self._activity_model.pending_flow_ids():
            if self.on_forward:
                self.on_forward(flow_id, self._edits.get(flow_id))
        for flow_id in self._activity_model.pending_response_flow_ids():
            if self.on_forward_response:
                self.on_forward_response(flow_id, self._response_edits.get(flow_id))
        # Wipe all per-flow UI state and the activity table.
        self._edits.clear()
        self._response_edits.clear()
        self._awaiting_response.clear()
        self._current = None
        self._current_kind = ""
        self._shown_flow_id = None
        self._activity_model.clear()
        self._editor.clear()
        self._editor.setReadOnly(True)
        self._response_view.clear_message()
        self._response_view.setReadOnly(True)
        self._set_action_buttons_enabled(False)
        self._update_status()

    def is_intercepting(self) -> bool:
        return self._toggle_btn.isChecked()

    # -- incoming paused flows ------------------------------------------------

    def enqueue(self, record: FlowRecord) -> None:
        """A request was paused by the proxy; add it to the table."""
        row = self._activity_model.add_request(record)
        self._activity_table.scrollToBottom()
        # Auto-select the first paused item when nothing is being edited yet.
        if self._current is None:
            self._activity_table.selectRow(row)
        self._update_status()

    def enqueue_response(self, record: FlowRecord) -> None:
        """A response was paused by the proxy; add it to the table."""
        row = self._activity_model.add_response(record)
        self._activity_table.scrollToBottom()
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
        if self._activity_model.is_pending_response(row):
            self._show_response(record)
        else:
            pending = self._activity_model.is_pending_request(row)
            self._show(record, pending)

    def _show(self, record: FlowRecord, pending: bool) -> None:
        """Show a request (editable when pending) in the Request pane."""
        self._current = record if pending else None
        self._current_kind = REQUEST if pending else ""
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
        # Response pane: nothing to edit for a request selection.
        self._response_view.clear_message()
        self._response_view.setReadOnly(True)
        self._set_action_buttons_enabled(pending)
        self._update_status()

    def _show_response(self, record: FlowRecord) -> None:
        """Show a paused response: request read-only on the left, editable
        response on the right."""
        self._current = record
        self._current_kind = RESPONSE
        # Left pane: the original request, read-only for reference.
        req_text = build_request_text(
            record.method, record.path, record.http_version,
            record.request_headers, record.request_body_inline,
            host=record.host, port=record.port, scheme=record.scheme,
        )
        self._editor.setPlainText(req_text)
        self._editor.setReadOnly(True)
        # Right pane: the editable raw response.
        if record.flow_id in self._response_edits:
            resp_text = self._response_edits[record.flow_id]
        else:
            resp_text = build_response_text(
                record.http_version, record.status_code, record.reason,
                record.response_headers, record.response_body_inline,
            )
        self._response_view.setReadOnly(False)
        self._response_view.setPlainText(resp_text)
        self._shown_flow_id = record.flow_id
        self._set_action_buttons_enabled(True)
        self._update_status()

    def _stash_current_edit(self) -> None:
        """Remember the editor text for the currently selected pending flow."""
        if self._current is None:
            return
        if self._current_kind == RESPONSE:
            self._response_edits[self._current.flow_id] = self._response_view.toPlainText()
        elif self._current_kind == REQUEST:
            self._edits[self._current.flow_id] = self._editor.toPlainText()

    def _select_next_pending(self) -> None:
        """Select the first still-pending item (request or response), or clear."""
        row = self._activity_model.first_pending_row()
        if row is not None:
            # Update the selection UI, then drive the editor directly. We don't
            # rely solely on the selectionChanged signal because selecting a row
            # that is already the current index emits nothing (e.g. after the
            # row above it was removed and it shifted into the selected index).
            self._activity_table.selectRow(row)
            record = self._activity_model.record_at(row)
            if record is not None:
                if self._activity_model.is_pending_response(row):
                    self._show_response(record)
                else:
                    self._show(record, self._activity_model.is_pending_request(row))
        else:
            self._current = None
            self._current_kind = ""
            self._editor.clear()
            self._editor.setReadOnly(True)
            self._response_view.clear_message()
            self._response_view.setReadOnly(True)
            self._set_action_buttons_enabled(False)
            self._update_status()

    # -- response correlation -------------------------------------------------

    def on_response(self, record: FlowRecord) -> None:
        """A response arrived. If we forwarded this flow from the intercept
        panel, show its response in the Response pane."""
        if record.flow_id not in self._awaiting_response:
            return
        self._awaiting_response.pop(record.flow_id, None)
        # Don't clobber the pane if the user is actively editing a paused
        # response for the same flow.
        if self._current_kind == RESPONSE and self._current is not None \
                and self._current.flow_id == record.flow_id:
            return
        # Paint it when this forwarded flow is the one whose response we're
        # showing (set at forward time), or nothing else has taken the pane.
        if self._shown_flow_id in (record.flow_id, None):
            self._shown_flow_id = record.flow_id
            self._response_view.setReadOnly(True)
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
        if self._current_kind == RESPONSE:
            self._forward_current_response()
        else:
            self._forward_current_request()
        # Advance to the next pending item immediately (Burp/Caido behavior).
        self._select_next_pending()

    def _forward_current_request(self) -> None:
        record = self._current
        flow_id = record.flow_id
        edited = self._editor.toPlainText()
        # Remember we're expecting this flow's response so we can show it.
        self._awaiting_response[flow_id] = record
        self._shown_flow_id = flow_id
        if self.on_forward:
            self.on_forward(flow_id, edited)
        self._edits.pop(flow_id, None)
        # Remove the resolved request row from the table.
        row = self._activity_model.row_index_for(flow_id, REQUEST)
        if row is not None:
            self._activity_model.remove_row(row)
        self._current = None
        self._current_kind = ""

    def _forward_current_response(self) -> None:
        flow_id = self._current.flow_id
        edited = self._response_view.toPlainText()
        if self.on_forward_response:
            self.on_forward_response(flow_id, edited)
        self._response_edits.pop(flow_id, None)
        self._awaiting_response.pop(flow_id, None)
        row = self._activity_model.row_index_for(flow_id, RESPONSE)
        if row is not None:
            self._activity_model.remove_row(row)
        self._current = None
        self._current_kind = ""

    def _on_drop_clicked(self) -> None:
        if self._current is None:
            return
        flow_id = self._current.flow_id
        if self._current_kind == RESPONSE:
            if self.on_drop_response:
                self.on_drop_response(flow_id)
            self._response_edits.pop(flow_id, None)
            row = self._activity_model.row_index_for(flow_id, RESPONSE)
        else:
            if self.on_drop:
                self.on_drop(flow_id)
            self._edits.pop(flow_id, None)
            row = self._activity_model.row_index_for(flow_id, REQUEST)
        self._awaiting_response.pop(flow_id, None)
        if row is not None:
            self._activity_model.remove_row(row)
        self._current = None
        self._current_kind = ""
        # Move on to the next pending item immediately.
        self._select_next_pending()

    def _on_forward_all(self) -> None:
        """Forward every still-pending request and response. The selected one
        uses its edited text; the rest are forwarded as captured."""
        self._stash_current_edit()
        for flow_id in self._activity_model.pending_flow_ids():
            edited = self._edits.get(flow_id)
            if self.on_forward:
                self.on_forward(flow_id, edited)
            rec = self._activity_model_record(flow_id, REQUEST)
            if rec is not None:
                self._awaiting_response[flow_id] = rec
        for flow_id in self._activity_model.pending_response_flow_ids():
            if self.on_forward_response:
                self.on_forward_response(flow_id, self._response_edits.get(flow_id))
        # Remove all resolved rows.
        for flow_id in list(self._activity_model.pending_flow_ids()):
            self._activity_model.remove_flow(flow_id)
        for flow_id in list(self._activity_model.pending_response_flow_ids()):
            self._activity_model.remove_flow(flow_id)
        self._edits.clear()
        self._response_edits.clear()
        self._current = None
        self._current_kind = ""
        self._editor.setReadOnly(True)
        self._response_view.setReadOnly(True)
        self._set_action_buttons_enabled(False)
        self._update_status()

    def _on_drop_all(self) -> None:
        """Drop every still-pending request and response, and remove their rows."""
        for flow_id in self._activity_model.pending_flow_ids():
            if self.on_drop:
                self.on_drop(flow_id)
            self._awaiting_response.pop(flow_id, None)
        for flow_id in self._activity_model.pending_response_flow_ids():
            if self.on_drop_response:
                self.on_drop_response(flow_id)
            self._awaiting_response.pop(flow_id, None)
        for flow_id in list(self._activity_model.pending_flow_ids()):
            self._activity_model.remove_flow(flow_id)
        for flow_id in list(self._activity_model.pending_response_flow_ids()):
            self._activity_model.remove_flow(flow_id)
        self._edits.clear()
        self._response_edits.clear()
        self._current = None
        self._current_kind = ""
        self._editor.clear()
        self._editor.setReadOnly(True)
        self._response_view.clear_message()
        self._response_view.setReadOnly(True)
        self._set_action_buttons_enabled(False)
        self._update_status()

    def _activity_model_record(self, flow_id: str, direction: Optional[str] = None):
        """Find the FlowRecord for a flow_id (optionally filtered by direction)
        currently in the table."""
        for i in range(self._activity_model.rowCount()):
            rec = self._activity_model.record_at(i)
            if rec is not None and rec.flow_id == flow_id:
                if direction is None or self._activity_model.direction_at(i) == direction:
                    return rec
        return None

    # -- context menu / send-to -----------------------------------------------

    def _add_shortcut(self, seq: str, handler) -> None:
        action = QAction(self)
        action.setShortcut(QKeySequence(seq))
        action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        action.triggered.connect(handler)
        self.addAction(action)

    def _emit_send_to_repeater(self) -> None:
        record = self._current_as_record()
        if record is not None:
            self.send_to_repeater.emit(record)

    def _emit_send_to_intruder(self) -> None:
        record = self._current_as_record()
        if record is not None:
            self.send_to_intruder.emit(record)

    def _on_context_menu(self, pos) -> None:
        record = self._current_as_record()
        menu = QMenu(self)
        # Only offered for a paused request: arm a one-shot response intercept
        # so this specific flow's response gets paused for review, even when the
        # global "Intercept responses" switch is off (Burp's behavior).
        act_resp: Optional[object] = None
        if self._current_kind == REQUEST and self._current is not None:
            act_resp = menu.addAction("Intercept response to this request")
            menu.addSeparator()
        act_rep = menu.addAction("Send to Repeater\tCtrl+R")
        act_int = menu.addAction("Send to Intruder\tCtrl+I")
        # Disable when there is nothing to send.
        act_rep.setEnabled(record is not None)
        act_int.setEnabled(record is not None)
        # Determine which view triggered the menu so the popup appears at the
        # correct screen position.
        sender = self.sender()
        if sender is not None and hasattr(sender, "viewport"):
            global_pos = sender.viewport().mapToGlobal(pos)
        else:
            global_pos = self._editor.viewport().mapToGlobal(pos)
        chosen = menu.exec(global_pos)
        if act_resp is not None and chosen == act_resp:
            self._arm_response_intercept()
            return
        if record is None:
            return
        if chosen == act_rep:
            self.send_to_repeater.emit(record)
        elif chosen == act_int:
            self.send_to_intruder.emit(record)

    def _arm_response_intercept(self) -> None:
        """Arm a one-shot response intercept for the current paused request,
        then forward the request so its response comes back paused."""
        if self._current is None or self._current_kind != REQUEST:
            return
        flow_id = self._current.flow_id
        if self.on_intercept_response_for:
            self.on_intercept_response_for(flow_id)
        # Forward the request now so the response will be produced and paused.
        self._forward_current_request()
        self._select_next_pending()

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
        # Forward/Drop act on the selected pending item (request or response).
        self._forward_btn.setEnabled(enabled)
        self._drop_btn.setEnabled(enabled)
        # Forward All / Drop All are enabled whenever anything is still pending.
        has_pending = self._activity_model.has_any_pending()
        self._forward_all_btn.setEnabled(has_pending)
        self._drop_all_btn.setEnabled(has_pending)

    def _update_status(self) -> None:
        reqs = self._activity_model.pending_flow_ids()
        resps = self._activity_model.pending_response_flow_ids()
        total = len(reqs) + len(resps)
        if total == 0:
            self._status.setText("No pending requests.")
            return
        if self._current is not None:
            kind = "response" if self._current_kind == RESPONSE else "request"
            target = f"{self._current.host}{self._current.path}"
            if len(target) > 80:
                target = target[:77] + "..."
            self._status.setText(
                f"Editing {kind}: {self._current.method} {target}  "
                f"({total} pending)"
            )
        else:
            self._status.setText(f"{total} pending item(s).")
