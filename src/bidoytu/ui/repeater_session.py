"""A single Repeater session: one editable request + its response.

Bundles the per-request features that make Repeater a real iterative testing
tool:

* send / cancel with in-flight state
* Ctrl+Enter to send; Ctrl+R to duplicate the request into a new tab
* per-send history you can step back/forward through
* a response metadata bar (color-coded status, size, time)
* follow-redirects and TLS-verify toggles
* auto Content-Length update on send
* find bars over request and response
* response render modes (Pretty / Raw / Hex)
* soft-wrap toggle
* copy the current request as a cURL command

The :class:`RepeaterTab` container holds one of these per open tab.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from shlex import quote

from PySide6.QtCore import Qt, QSize, Signal, Slot
from PySide6.QtGui import (
    QAction,
    QActionGroup,
    QGuiApplication,
    QKeySequence,
    QShortcut,
)
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMenu,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from bidoytu.http_utils import (
    build_request_text,
    host_from_headers_or_url,
    parse_request_text,
)
from bidoytu.net.async_sender import AsyncHttpSender, HttpResult, SendHandle
from bidoytu.storage.models import FlowRecord
from bidoytu.ui.body_format import content_type_from_headers
from bidoytu.ui.find_bar import FindBar
from bidoytu.ui.message_view import RENDER_MODES, MessageView
from bidoytu.ui.theme import ui_icon


@dataclass(slots=True)
class HistoryEntry:
    """A request that was sent and (optionally) the response it produced."""

    request_text: str
    response_start_line: str = ""
    response_headers: str = ""
    response_body: bytes | None = None
    response_content_type: str = ""
    status_code: int | None = None
    duration_ms: float = 0.0
    error: str = ""


@dataclass(slots=True)
class SessionState:
    """Serializable snapshot of a session (for persistence)."""

    name: str = "Request"
    scheme: str = "http"
    host: str = ""
    port: int = 80
    request_text: str = ""
    follow_redirects: bool = False
    verify_tls: bool = False


class RepeaterSession(QWidget):
    """One request/response pane with full Repeater controls."""

    title_changed = Signal(str)  # emitted when the derived tab title changes
    duplicate_requested = Signal()  # Ctrl+R: clone this request into a new tab
    result_delivered = Signal(object)  # HttpResult, after on_result finishes
    send_to_repeater = Signal(object)  # FlowRecord (right-click)
    send_to_intruder = Signal(object)  # FlowRecord (right-click)
    new_requested = Signal()  # "+ New" button: ask the container for a new tab
    clear_all_requested = Signal()  # "Clear all" button: ask the container
    _result_ready = Signal(object)  # HttpResult, marshalled to the UI thread

    def __init__(self, sender: AsyncHttpSender, name: str = "Request",
                 parent=None) -> None:
        super().__init__(parent)
        self._sender = sender
        self._name = name
        self._scheme = "http"
        self._host = ""
        self._port = 80

        self._handle: SendHandle | None = None
        self._history: list[HistoryEntry] = []
        self._history_index = -1
        # Optional provider that returns a fresh Collaborator (OAST) payload
        # hostname, or None if unavailable. Set by the container so the request
        # editor's context menu can insert a payload at the cursor.
        self.payload_provider = None  # Callable[[], Optional[str]] | None

        self._build_ui()
        self._wire_shortcuts()
        # The sender invokes our callback on its own thread; bounce through a
        # queued signal so on_result runs on the Qt UI thread.
        self._result_ready.connect(self.on_result)

    # -- UI construction ------------------------------------------------------

    def _build_ui(self) -> None:
        # Top control row. Send is a split button: the main part sends the
        # current tab; the dropdown arrow (shown only when this tab belongs to
        # a group) offers group-send modes, matching Burp's grouped Repeater.
        self._send_btn = QToolButton()
        self._send_btn.setText("Send")
        self._send_btn.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self._send_btn.setPopupMode(QToolButton.MenuButtonPopup)
        self._send_btn.clicked.connect(self._on_send_or_cancel)
        # Give Send a comfortable width so it doesn't look cramped next to the
        # nav arrows, and reads as the primary action of the row.
        self._send_btn.setMinimumWidth(96)
        # Whether the editor currently holds a sendable request. When False the
        # button stays visible (and its dropdown still opens to *show* the group
        # options) but neither the button nor the menu options do anything, and
        # it is styled with the disabled cue (surface_alt) via a dynamic prop.
        self._has_request = False
        self._apply_send_disabled_style()
        # Group-send menu; populated by the container via set_group_send_actions.
        # _active_send_mode: None => send current tab; else a callable to run.
        # _send_label: current text for the Send button (reflects the mode).
        self._group_menu: QMenu | None = None
        self._active_send_mode = None
        self._send_label = "Send"
        self._selected_send_label = "Send"
        self._update_send_menu()

        # History navigation uses painted icons rather than font glyphs. A
        # fixed width keeps the controls square in every build.
        self._prev_btn = QPushButton()
        self._prev_btn.setIcon(ui_icon("left"))
        self._prev_btn.setIconSize(QSize(18, 18))
        self._prev_btn.setToolTip("Previous request in history")
        self._prev_btn.setFixedWidth(34)
        self._prev_btn.clicked.connect(lambda: self._navigate_history(-1))
        self._prev_btn.setEnabled(False)

        self._next_btn = QPushButton()
        self._next_btn.setIcon(ui_icon("right"))
        self._next_btn.setIconSize(QSize(18, 18))
        self._next_btn.setToolTip("Next request in history")
        self._next_btn.setFixedWidth(34)
        self._next_btn.clicked.connect(lambda: self._navigate_history(1))
        self._next_btn.setEnabled(False)

        self._history_label = QLabel("")
        self._history_label.setStyleSheet("color: gray;")

        # Status/target label. A long "Sending to <url>" string must never
        # drive the layout width: an unconstrained QLabel reports its full text
        # width as its minimum, which would push the whole window's minimum
        # width to thousands of pixels (Qt then floods "Unable to set geometry"
        # and the splitter panes collapse). We let it shrink freely and elide
        # the middle of the text so the target stays readable at any width.
        self._target_full_text = "No request loaded"
        self._target_label = QLabel(self._target_full_text)
        # Fixed width keeps the left cluster a stable size, so the centred
        # "+ New / Clear all" pair stays put and the label never overruns them.
        # Text is elided to fit; the full string is on the tooltip.
        self._target_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self._target_label.setFixedWidth(220)

        self._follow_redirects = QCheckBox("Follow redirects")
        self._verify_tls = QCheckBox("Verify TLS")

        self._curl_btn = QPushButton("Copy as cURL")
        self._curl_btn.clicked.connect(self._copy_as_curl)

        # Container-level actions, shown centered in this controls row. They
        # don't act on this session directly; they ask the RepeaterTab to open
        # a new tab / clear all tabs (wired up by the container).
        self._new_btn = QPushButton("+ New")
        self._new_btn.setToolTip("Open an empty request")
        self._new_btn.setCursor(Qt.PointingHandCursor)
        self._new_btn.clicked.connect(self.new_requested.emit)

        self._clear_all_btn = QPushButton("Clear all")
        self._clear_all_btn.setToolTip("Close every request tab and remove all groups")
        self._clear_all_btn.setCursor(Qt.PointingHandCursor)
        self._clear_all_btn.clicked.connect(self.clear_all_requested.emit)

        # Match every button in this controls row to the height of the
        # prev/next nav arrows, so the row reads as one consistent band
        # regardless of per-widget content (icon vs text vs tool button).
        nav_height = self._prev_btn.sizeHint().height()
        for _btn in (
            self._send_btn, self._next_btn, self._curl_btn,
            self._new_btn, self._clear_all_btn,
        ):
            _btn.setFixedHeight(nav_height)

        # The controls row has three clusters. To keep "+ New / Clear all"
        # centered with respect to the whole tab (not merely the gap between
        # the left and right clusters), all three clusters share one grid cell:
        # the left cluster is left-aligned, the right cluster right-aligned, and
        # the center pair is aligned to the true horizontal centre of the full
        # width. That decouples the centre from the differing side widths.
        left = QWidget()
        left_row = QHBoxLayout(left)
        left_row.setContentsMargins(0, 0, 0, 0)
        left_row.addWidget(self._send_btn)
        left_row.addWidget(self._prev_btn)
        left_row.addWidget(self._next_btn)
        left_row.addWidget(self._history_label)
        left_row.addSpacing(12)
        left_row.addWidget(self._target_label)

        center = QWidget()
        center_row = QHBoxLayout(center)
        center_row.setContentsMargins(0, 0, 0, 0)
        center_row.addWidget(self._new_btn)
        center_row.addWidget(self._clear_all_btn)

        right = QWidget()
        right_row = QHBoxLayout(right)
        right_row.setContentsMargins(0, 0, 0, 0)
        right_row.addWidget(self._follow_redirects)
        right_row.addWidget(self._verify_tls)
        right_row.addWidget(self._curl_btn)

        controls = QGridLayout()
        controls.setContentsMargins(0, 0, 0, 0)
        controls.addWidget(left, 0, 0, Qt.AlignLeft)
        controls.addWidget(center, 0, 0, Qt.AlignHCenter)
        controls.addWidget(right, 0, 0, Qt.AlignRight)

        # Request pane.
        self._request_edit = MessageView(read_only=False)
        self._request_edit.setContextMenuPolicy(Qt.CustomContextMenu)
        self._request_edit.customContextMenuRequested.connect(self._on_context_menu)
        self._request_find = FindBar(self._request_edit)
        request_pane = self._pane(
            "Request", self._request_edit, self._request_find,
            extra_controls=self._request_pane_controls(),
        )

        # Response pane.
        self._response_view = MessageView(read_only=True)
        self._response_find = FindBar(self._response_view)
        response_pane = self._pane(
            "Response", self._response_view, self._response_find,
            extra_controls=self._response_pane_controls(),
        )

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(request_pane)
        splitter.addWidget(response_pane)
        splitter.setSizes([600, 600])

        # Response metadata bar.
        self._meta_status = QLabel("")
        self._meta_size = QLabel("")
        self._meta_time = QLabel("")
        meta = QHBoxLayout()
        meta.setContentsMargins(4, 0, 4, 0)
        meta.addWidget(QLabel("Status:"))
        meta.addWidget(self._meta_status)
        meta.addSpacing(16)
        meta.addWidget(QLabel("Size:"))
        meta.addWidget(self._meta_size)
        meta.addSpacing(16)
        meta.addWidget(QLabel("Time:"))
        meta.addWidget(self._meta_time)
        meta.addStretch(1)

        layout = QVBoxLayout(self)
        layout.addLayout(controls)
        layout.addWidget(splitter, 1)
        layout.addLayout(meta)

    def _set_target_text(self, text: str) -> None:
        """Set the status/target label, eliding to fit the current width.

        Stores the full text so it can be re-elided when the pane is resized,
        and shown in full via tooltip.
        """
        self._target_full_text = text
        self._target_label.setToolTip(text)
        self._elide_target_text()

    def _elide_target_text(self) -> None:
        metrics = self._target_label.fontMetrics()
        avail = max(0, self._target_label.width())
        if avail <= 0:
            # Not laid out yet; show the raw text (its Ignored size policy keeps
            # it from forcing the window wider).
            self._target_label.setText(self._target_full_text)
            return
        elided = metrics.elidedText(self._target_full_text, Qt.ElideMiddle, avail)
        self._target_label.setText(elided)

    def resizeEvent(self, event) -> None:  # noqa: N802 (Qt override)
        super().resizeEvent(event)
        self._elide_target_text()

    def _request_pane_controls(self) -> QWidget:
        bar = QWidget()
        h = QHBoxLayout(bar)
        h.setContentsMargins(0, 0, 0, 0)

        self._req_wrap = QCheckBox("Wrap")
        self._req_wrap.setChecked(True)
        self._req_wrap.stateChanged.connect(
            lambda s: self._request_edit.set_soft_wrap(bool(s))
        )
        cl_btn = QPushButton("Update Content-Length")
        cl_btn.setToolTip("Recompute the Content-Length header from the body")
        cl_btn.clicked.connect(self._update_content_length)

        h.addStretch(1)
        h.addWidget(cl_btn)
        h.addWidget(self._req_wrap)
        return bar

    def _response_pane_controls(self) -> QWidget:
        bar = QWidget()
        h = QHBoxLayout(bar)
        h.setContentsMargins(0, 0, 0, 0)

        self._mode_combo = QComboBox()
        self._mode_combo.addItems(list(RENDER_MODES))
        self._mode_combo.currentTextChanged.connect(
            self._response_view.set_render_mode
        )

        self._resp_wrap = QCheckBox("Wrap")
        self._resp_wrap.setChecked(True)
        self._resp_wrap.stateChanged.connect(
            lambda s: self._response_view.set_soft_wrap(bool(s))
        )

        h.addStretch(1)
        h.addWidget(QLabel("View:"))
        h.addWidget(self._mode_combo)
        h.addWidget(self._resp_wrap)
        return bar

    @staticmethod
    def _pane(title: str, view: MessageView, find_bar: FindBar,
              extra_controls: QWidget | None = None) -> QWidget:
        container = QWidget()
        v = QVBoxLayout(container)
        v.setContentsMargins(0, 0, 0, 0)

        header = QHBoxLayout()
        label = QLabel(title)
        label.setStyleSheet("font-weight: bold; padding: 4px;")
        header.addWidget(label)
        if extra_controls is not None:
            header.addWidget(extra_controls, 1)
        v.addLayout(header)
        v.addWidget(find_bar)
        v.addWidget(view, 1)
        return container

    def _wire_shortcuts(self) -> None:
        # Ctrl+Enter / Ctrl+Return / Ctrl+Space send the current request.
        for seq in ("Ctrl+Return", "Ctrl+Enter", "Ctrl+Space"):
            sc = QShortcut(QKeySequence(seq), self)
            sc.activated.connect(self._on_send_shortcut)
        # Ctrl+R duplicates this request into a new tab (handled by container).
        dup_sc = QShortcut(QKeySequence("Ctrl+R"), self)
        dup_sc.activated.connect(self.duplicate_requested.emit)
        # Ctrl+I sends the current request to the Intruder.
        intruder_sc = QShortcut(QKeySequence("Ctrl+I"), self)
        intruder_sc.activated.connect(self._send_to_intruder_shortcut)
        # Ctrl+F focuses the find bar of whichever view has focus.
        find_sc = QShortcut(QKeySequence.Find, self)
        find_sc.activated.connect(self._activate_find)

    def _send_to_intruder_shortcut(self) -> None:
        record = self._current_as_record()
        if record is not None:
            self.send_to_intruder.emit(record)

    # -- loading --------------------------------------------------------------

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
        self._set_target_text(f"{self._scheme}://{self._host}:{self._port}")
        self._set_has_request(True)
        self._set_name_from_request()

    def load_state(self, state: SessionState) -> None:
        self._name = state.name
        self._scheme = state.scheme
        self._host = state.host
        self._port = state.port
        self._request_edit.setPlainText(state.request_text)
        self._follow_redirects.setChecked(state.follow_redirects)
        self._verify_tls.setChecked(state.verify_tls)
        self._response_view.clear_message()
        self._set_target_text(f"{self._scheme}://{self._host}:{self._port}")
        self._set_has_request(bool(state.request_text.strip()))
        self.title_changed.emit(self._name)

    def to_state(self) -> SessionState:
        return SessionState(
            name=self._name,
            scheme=self._scheme,
            host=self._host,
            port=self._port,
            request_text=self._request_edit.toPlainText(),
            follow_redirects=self._follow_redirects.isChecked(),
            verify_tls=self._verify_tls.isChecked(),
        )

    def name(self) -> str:
        return self._name

    def is_empty(self) -> bool:
        """True if this is a pristine session: no request text and no history."""
        return (
            not self._request_edit.toPlainText().strip()
            and not self._history
        )

    def _set_name_from_request(self) -> None:
        parsed = parse_request_text(self._request_edit.toPlainText())
        path = parsed.path.split("?", 1)[0]
        short = path if len(path) <= 24 else path[:21] + "..."
        self._name = f"{parsed.method} {short}".strip() or "Request"
        self.title_changed.emit(self._name)

    # -- sending / cancelling -------------------------------------------------

    @Slot()
    def _on_send_shortcut(self) -> None:
        # Ctrl+Space always sends the current tab, regardless of the selected
        # group-send mode (matches Burp).
        if self._has_request and self._handle is None:
            self._send()

    # -- group-send menu (driven by the container) ----------------------------

    def set_group_send_actions(self, actions: list[tuple[str, object]] | None) -> None:
        """Install (or clear) the dropdown's group-send options.

        ``actions`` is a list of ``(label, callable)`` pairs, or ``None`` when
        this tab is not in a group (which hides the dropdown arrow entirely).

        The menu items are *selectable modes* (radio style), matching Burp:
        clicking one selects it (checkmark) and makes the main Send button use
        it; it does not fire the send. "Send (current tab)" is the default.
        """
        if not actions:
            # No group: clear everything and fall back to single-tab send.
            self._group_menu = None
            self._active_send_mode = None
            self._selected_send_label = "Send"
            self._send_label = "Send"
            if self._handle is None:
                self._send_btn.setText("Send")
            self._update_send_menu()
            return

        # Remember the previously selected option (by label) so a menu rebuild
        # -- which happens on any tab/group change -- doesn't silently reset the
        # user's choice back to "current tab".
        previously = getattr(self, "_selected_send_label", "Send")

        menu = QMenu(self)
        header = QAction("Group send options", menu)
        header.setEnabled(False)
        menu.addAction(header)

        group = QActionGroup(menu)
        group.setExclusive(True)

        # Default selectable mode: send only the current tab.
        current = QAction("Send (current tab)", menu)
        current.setCheckable(True)
        current.setShortcut(QKeySequence("Ctrl+Space"))
        current.triggered.connect(lambda: self._select_send_mode(None, "Send"))
        group.addAction(current)
        menu.addAction(current)
        menu.addSeparator()

        restored = False
        for label, fn in actions:
            act = QAction(label, menu)
            act.setCheckable(True)
            act.triggered.connect(
                lambda _checked=False, f=fn, lbl=label: self._select_send_mode(f, lbl)
            )
            group.addAction(act)
            menu.addAction(act)
            if label == previously:
                act.setChecked(True)
                # Re-bind the active mode to the matching callable.
                self._active_send_mode = fn
                self._send_label = label
                restored = True

        if not restored:
            # Previous selection is gone (or was "current tab"): default.
            current.setChecked(True)
            self._active_send_mode = None
            self._send_label = "Send"

        self._selected_send_label = self._send_label
        if self._handle is None:
            self._send_btn.setText(self._send_label)
        self._send_btn.setToolTip(self._send_label)
        self._group_menu = menu
        self._update_send_menu()

    def _select_send_mode(self, mode, label: str) -> None:
        """Record which send mode the split button runs, and show it on the button."""
        self._active_send_mode = mode
        # Reflect the chosen option on the Send button so the user sees what it
        # will do. The full option label is shown in front.
        self._send_label = label
        self._selected_send_label = label
        if self._handle is None:  # don't clobber a "Cancel" label mid-flight
            self._send_btn.setText(label)
        self._send_btn.setToolTip(label)

    def _update_send_menu(self) -> None:
        # A QToolButton only shows the dropdown arrow when it has a menu.
        self._send_btn.setMenu(self._group_menu)
        self._sync_menu_enabled()

    def _set_has_request(self, has: bool) -> None:
        """Enable/disable the Send action while keeping the button visible.

        We deliberately do NOT call setEnabled(False): a disabled QToolButton
        won't open its menu, and the request is for the dropdown to still show
        its options. Instead we track the state ourselves, gate the actual send,
        grey out the individual menu options, and paint the disabled cue.
        """
        self._has_request = bool(has)
        self._apply_send_disabled_style()
        self._sync_menu_enabled()

    def _apply_send_disabled_style(self) -> None:
        """Paint the Send button with the disabled cue when it has no request.

        Uses a dynamic Qt property (``inactive``) that the stylesheet targets,
        so the fill comes from the theme's ``surface_alt`` token (#e4e5f1 in
        light mode, #252a33 in dark) rather than a hard-coded colour.
        """
        self._send_btn.setProperty("inactive", not self._has_request)
        # Re-polish so the property change takes effect immediately.
        self._send_btn.style().unpolish(self._send_btn)
        self._send_btn.style().polish(self._send_btn)

    def _sync_menu_enabled(self) -> None:
        """Grey out the dropdown's options when there is no request to send."""
        if self._group_menu is None:
            return
        for act in self._group_menu.actions():
            if act.isSeparator():
                continue
            # Keep the non-interactive header greyed regardless; other options
            # follow the request state.
            if act.text() == "Group send options":
                act.setEnabled(False)
            else:
                act.setEnabled(self._has_request)

    def send_now(self, fresh_client: bool = False) -> None:
        """Public entry point for the container to send this tab's request."""
        if self._handle is None:
            self._send(fresh_client=fresh_client)

    def is_busy(self) -> bool:
        return self._handle is not None

    @Slot()
    def _on_send_or_cancel(self) -> None:
        if self._handle is not None:
            self._handle.cancel()
            self._set_target_text("Cancelling...")
            return
        # No sendable request yet: the button is a visible-but-inert cue.
        if not self._has_request:
            return
        # If a group send mode is selected in the dropdown, run that; otherwise
        # send just this tab.
        if self._active_send_mode is not None:
            self._active_send_mode()
        else:
            self._send()

    def _send(self, fresh_client: bool = False) -> None:
        parsed = parse_request_text(self._request_edit.toPlainText())
        scheme, host, port, path = host_from_headers_or_url(
            parsed, self._host, self._scheme, self._port
        )
        if not host:
            self._response_view.setPlainText(
                "Cannot send: no host (add a Host header)."
            )
            # Report a synthetic failure so group sequences can advance.
            self.result_delivered.emit(HttpResult(ok=False, error="no host"))
            return
        default_ports = {"http": 80, "https": 443}
        netloc = host if port == default_ports.get(scheme) else f"{host}:{port}"
        url = f"{scheme}://{netloc}{path}"

        self._set_name_from_request()
        self._send_btn.setText("Cancel")
        self._set_target_text(f"Sending to {url} ...")
        self._handle = self._sender.send(
            parsed.method, url, parsed.headers, parsed.body,
            lambda result: self._result_ready.emit(result),
            verify=self._verify_tls.isChecked(),
            follow_redirects=self._follow_redirects.isChecked(),
            fresh_client=fresh_client,
        )

    @Slot(object)
    def on_result(self, result: HttpResult) -> None:
        self._handle = None
        self._send_btn.setText(self._send_label)
        self._set_has_request(True)

        if result.cancelled:
            self._set_target_text("Cancelled")
            self._meta_status.setText("cancelled")
            self._meta_status.setStyleSheet("color: orange;")
        elif not result.ok:
            self._response_view.setPlainText(f"Error: {result.error}")
            self._set_target_text("Request failed")
            self._meta_status.setText("error")
            self._meta_status.setStyleSheet("color: #c0392b;")
            self._record_history(result, ok=False)
        else:
            version = result.http_version or "HTTP/1.1"
            status_line = f"{version} {result.status_code} {result.reason}".strip()
            ct = content_type_from_headers(result.headers_text)
            self._response_view.show_message(
                status_line, result.headers_text, result.body, ct
            )
            self._update_meta(result)
            self._set_target_text(f"Done in {result.duration_ms:.0f} ms")
            self._record_history(result, ok=True)

        # Notify listeners (e.g. group sequential send) that this send finished.
        self.result_delivered.emit(result)

    def _update_meta(self, result: HttpResult) -> None:
        code = result.status_code or 0
        self._meta_status.setText(f"{code} {result.reason}".strip())
        self._meta_status.setStyleSheet(
            f"font-weight: bold; color: {self._status_color(code)};"
        )
        self._meta_size.setText(self._human_size(len(result.body)))
        self._meta_time.setText(f"{result.duration_ms:.0f} ms")

    @staticmethod
    def _status_color(code: int) -> str:
        if 200 <= code < 300:
            return "#2ecc71"  # green
        if 300 <= code < 400:
            return "#3498db"  # blue
        if 400 <= code < 500:
            return "#e67e22"  # orange
        if code >= 500:
            return "#c0392b"  # red
        return "gray"

    @staticmethod
    def _human_size(n: int) -> str:
        size = float(n)
        for unit in ("B", "KB", "MB", "GB"):
            if size < 1024 or unit == "GB":
                return f"{int(size)} {unit}" if unit == "B" else f"{size:.1f} {unit}"
            size /= 1024
        return f"{n} B"

    # -- history --------------------------------------------------------------

    def _record_history(self, result: HttpResult, ok: bool) -> None:
        entry = HistoryEntry(
            request_text=self._request_edit.toPlainText(),
            error="" if ok else result.error,
        )
        if ok:
            version = result.http_version or "HTTP/1.1"
            entry.response_start_line = (
                f"{version} {result.status_code} {result.reason}".strip()
            )
            entry.response_headers = result.headers_text
            entry.response_body = result.body
            entry.response_content_type = content_type_from_headers(
                result.headers_text
            )
            entry.status_code = result.status_code
            entry.duration_ms = result.duration_ms
        self._history.append(entry)
        self._history_index = len(self._history) - 1
        self._refresh_history_controls()

    def _navigate_history(self, delta: int) -> None:
        if not self._history:
            return
        new_index = self._history_index + delta
        if not (0 <= new_index < len(self._history)):
            return
        self._history_index = new_index
        entry = self._history[new_index]
        self._request_edit.setPlainText(entry.request_text)
        if entry.error:
            self._response_view.setPlainText(f"Error: {entry.error}")
        elif entry.response_start_line:
            self._response_view.show_message(
                entry.response_start_line, entry.response_headers,
                entry.response_body, entry.response_content_type,
            )
        else:
            self._response_view.clear_message()
        self._refresh_history_controls()

    def _refresh_history_controls(self) -> None:
        total = len(self._history)
        self._prev_btn.setEnabled(self._history_index > 0)
        self._next_btn.setEnabled(0 <= self._history_index < total - 1)
        if total:
            self._history_label.setText(f"{self._history_index + 1}/{total}")
        else:
            self._history_label.setText("")

    # -- content-length -------------------------------------------------------

    def _update_content_length(self) -> None:
        parsed = parse_request_text(self._request_edit.toPlainText())
        body_len = len(parsed.body)
        headers = [(k, v) for k, v in parsed.headers
                   if k.lower() != "content-length"]
        if body_len > 0:
            headers.append(("Content-Length", str(body_len)))
        rebuilt = build_request_text(
            parsed.method, parsed.path, parsed.http_version,
            "\r\n".join(f"{k}: {v}" for k, v in headers),
            parsed.body,
        )
        self._request_edit.setPlainText(rebuilt)

    # -- copy as curl ---------------------------------------------------------

    def _copy_as_curl(self) -> None:
        parsed = parse_request_text(self._request_edit.toPlainText())
        scheme, host, port, path = host_from_headers_or_url(
            parsed, self._host, self._scheme, self._port
        )
        default_ports = {"http": 80, "https": 443}
        netloc = host if port == default_ports.get(scheme) else f"{host}:{port}"
        url = f"{scheme}://{netloc}{path}"

        parts = ["curl", "-X", parsed.method, quote(url)]
        for k, v in parsed.headers:
            if k.lower() == "content-length":
                continue
            parts += ["-H", quote(f"{k}: {v}")]
        if parsed.body:
            body_text = parsed.body.decode("utf-8", errors="replace")
            parts += ["--data-binary", quote(body_text)]
        if self._follow_redirects.isChecked():
            parts.append("-L")
        if not self._verify_tls.isChecked():
            parts.append("-k")

        command = " ".join(parts)
        QGuiApplication.clipboard().setText(command)
        self._set_target_text("Copied cURL to clipboard")

    # -- find -----------------------------------------------------------------

    def _activate_find(self) -> None:
        # Route Ctrl+F to whichever view currently has focus; default request.
        if self._response_view.hasFocus():
            self._response_find.activate()
        else:
            self._request_find.activate()

    # -- context menu / send-to ----------------------------------------------

    def _on_context_menu(self, pos) -> None:
        record = self._current_as_record()
        menu = QMenu(self)
        act_rep = menu.addAction("Send to Repeater")
        act_int = menu.addAction("Send to Intruder\tCtrl+I")
        act_rep.setEnabled(record is not None)
        act_int.setEnabled(record is not None)
        act_oast = None
        if self.payload_provider is not None:
            menu.addSeparator()
            act_oast = menu.addAction("Insert Collaborator payload")
        chosen = menu.exec(self._request_edit.viewport().mapToGlobal(pos))
        if chosen is not None and chosen == act_oast:
            self._insert_collaborator_payload()
            return
        if record is None:
            return
        if chosen == act_rep:
            self.send_to_repeater.emit(record)
        elif chosen == act_int:
            self.send_to_intruder.emit(record)

    def _insert_collaborator_payload(self) -> None:
        """Ask the provider for a payload and insert it at the cursor."""
        if self.payload_provider is None:
            return
        host = self.payload_provider()
        if host:
            self._request_edit.insertPlainText(host)

    def _current_as_record(self) -> FlowRecord | None:
        """Build a FlowRecord from the current (edited) request text."""
        text = self._request_edit.toPlainText()
        if not text.strip():
            return None
        parsed = parse_request_text(text)
        return FlowRecord(
            flow_id="",
            method=parsed.method,
            scheme=self._scheme,
            host=self._host,
            port=self._port,
            path=parsed.path,
            http_version=parsed.http_version,
            request_headers="\r\n".join(f"{k}: {v}" for k, v in parsed.headers),
            request_body_inline=parsed.body or None,
            request_body_size=len(parsed.body),
        )
