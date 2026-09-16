"""Collaborator tab: out-of-band (OAST) interaction listener.

Bidoytu's equivalent of Burp Collaborator, backed by free public Interactsh
servers (or a self-hosted one). Workflow:

1. Pick a server and click **Register**. A unique payload is immediately shown
   and copied to the clipboard.
2. Paste the payload into a request
   (SSRF target, XSS sink, XXE SYSTEM url, log4shell ``${jndi:ldap://...}``,
   blind SQLi ``, etc.). Each payload is unique and correlates back here.
3. Click **New payload** whenever a fresh hostname is needed. Bidoytu polls the
   server on an interval; any DNS / HTTP / SMTP callback the
   target makes to a payload shows up in the interactions table with the raw
   request, source IP and timestamp.

Threading: the :class:`~bidoytu.net.interactsh.InteractshClient` performs all
network I/O through the shared :class:`AsyncHttpSender`, whose callbacks run on
the *sender* thread. This widget marshals every such callback onto the Qt UI
thread via private queued signals (:attr:`_poll_ready`, :attr:`_register_ready`)
before touching any widget - the same idiom Repeater uses.
"""
from __future__ import annotations

import base64
import ctypes
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, Signal, Slot
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QCheckBox,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QSplitter,
    QTableView,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from bidoytu.config import CollaboratorConfig
from bidoytu.net.async_sender import AsyncHttpSender
from bidoytu.ui.body_format import content_type_from_headers
from bidoytu.net.interactsh import (
    Interaction,
    InteractshClient,
    InteractshError,
    SessionInfo,
)
from bidoytu.ui.find_bar import FindBar
from bidoytu.ui.collaborator_model import (
    COL_INDEX,
    InteractionFilterProxy,
    InteractionsModel,
)
from bidoytu.ui.message_view import MessageView


class CollaboratorTab(QWidget):
    """Register with an Interactsh server, hand out payloads, show callbacks."""

    # Emitted when new interactions arrive so the window can badge the tab.
    interactions_received = Signal(int)  # count of new interactions
    # Emitted when the user asks to drop a fresh payload into a target.
    copy_payload_requested = Signal(str)  # the generated payload hostname

    # Private signals used to marshal sender-thread callbacks to the UI thread.
    _register_ready = Signal(bool, str)          # ok, server
    _poll_ready = Signal(object, str)            # list[Interaction], error
    _keepalive_ready = Signal(bool, str)

    def __init__(self, sender: AsyncHttpSender,
                 config: CollaboratorConfig, parent=None) -> None:
        super().__init__(parent)
        self._sender = sender
        self._config = config
        self._client = InteractshClient(sender)
        # Track payloads we've generated so callbacks can be labelled with the
        # exact payload (and any note about where it was used).
        self._payloads: list[dict] = []  # {"host":..., "note":...}
        self._seen_ids: set[str] = set()  # de-dupe interactions by unique-id
        self._auto_poll = False
        self._poll_in_flight = False
        self._keepalive_in_flight = False
        self._last_poll_at = ""

        self._model = InteractionsModel(self)
        self._proxy = InteractionFilterProxy(self)
        self._proxy.setSourceModel(self._model)

        self._register_ready.connect(self._on_registered)
        self._poll_ready.connect(self._on_polled)
        self._keepalive_ready.connect(self._on_keepalive_result)

        self._poll_timer = QTimer(self)
        self._poll_timer.timeout.connect(self._do_poll)
        self._keepalive_timer = QTimer(self)
        self._keepalive_timer.setInterval(45 * 1000)
        self._keepalive_timer.timeout.connect(self._do_keepalive)

        self._build_ui()
        self._refresh_controls()

    # -- UI construction ------------------------------------------------------

    def _build_ui(self) -> None:
        # Row 1: server selection + register/deregister + token.
        self._server_combo = QComboBox()
        self._server_combo.setEditable(True)
        self._server_combo.addItems(self._config.servers)
        self._server_combo.setToolTip(
            "Interactsh server to register with. Public servers are free; you "
            "can also enter your own self-hosted server."
        )

        self._token_edit = QLineEdit()
        self._token_edit.setPlaceholderText("Auth token (optional)")
        self._token_edit.setEchoMode(QLineEdit.Password)
        self._token_edit.setText(self._config.token)
        self._token_edit.setMaximumWidth(180)
        self._token_show_btn = QToolButton()
        self._token_show_btn.setCheckable(True)
        self._token_show_btn.setToolTip("Show or hide the authentication token")
        self._token_show_btn.setAccessibleName("Show or hide authentication token")
        self._token_show_btn.toggled.connect(
            self._set_token_visibility
        )
        self._set_token_visibility(False)

        self._http_fallback_check = QCheckBox("Allow HTTP fallback")
        self._http_fallback_check.setChecked(self._config.allow_http_fallback)
        self._http_fallback_check.setToolTip(
            "Allow insecure HTTP registration when HTTPS is unavailable. "
            "Use only with a trusted self-hosted server."
        )
        self._http_fallback_check.toggled.connect(
            lambda value: setattr(self._config, "allow_http_fallback", value)
        )

        self._register_btn = QPushButton("Register")
        self._register_btn.clicked.connect(self._on_register_clicked)

        self._status_label = QLabel("Not registered")
        self._status_label.setStyleSheet("color: gray;")

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Server:"))
        row1.addWidget(self._server_combo, 1)
        row1.addWidget(self._token_edit)
        row1.addWidget(self._token_show_btn)
        row1.addWidget(self._http_fallback_check)
        row1.addWidget(self._register_btn)
        row1.addWidget(self._status_label, 1)

        # Row 2: payload generation + copy.
        self._payload_edit = QLineEdit()
        self._payload_edit.setReadOnly(True)
        self._payload_edit.setPlaceholderText(
            "Register, then generate a payload to paste into a target"
        )
        self._payload_history = QComboBox()
        self._payload_history.setMinimumWidth(240)
        self._payload_history.setToolTip("Previously generated payloads")
        self._payload_history.currentTextChanged.connect(self._payload_edit.setText)

        self._generate_btn = QPushButton("New payload")
        self._generate_btn.clicked.connect(self._on_generate)
        self._copy_btn = QPushButton("Copy")
        self._copy_btn.setToolTip("Copy the payload to the clipboard")
        self._copy_btn.clicked.connect(self._on_copy)
        self._clear_payloads_btn = QPushButton("Clear payloads")
        self._clear_payloads_btn.setToolTip(
            "Remove all locally saved payloads from the history"
        )
        self._clear_payloads_btn.clicked.connect(self._on_clear_payloads)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Payload:"))
        row2.addWidget(self._payload_edit, 1)
        row2.addWidget(self._payload_history)
        row2.addWidget(self._copy_btn)
        row2.addWidget(self._clear_payloads_btn)
        row2.addWidget(self._generate_btn)

        # Row 3: polling controls + filter + export/clear.
        self._poll_btn = QPushButton("Start polling")
        self._poll_btn.setCheckable(True)
        self._poll_btn.clicked.connect(self._on_toggle_poll)

        self._poll_now_btn = QPushButton("Poll now")
        self._poll_now_btn.clicked.connect(self._do_poll)

        self._interval_spin = QSpinBox()
        self._interval_spin.setRange(2, 300)
        self._interval_spin.setValue(self._config.poll_interval_secs)
        self._interval_spin.setSuffix(" s")
        self._interval_spin.setToolTip("Polling interval")
        self._interval_spin.valueChanged.connect(self._on_interval_changed)

        self._proto_filter = QComboBox()
        self._proto_filter.addItems([
            "All", "DNS", "HTTP", "SMTP", "LDAP", "FTP", "SMB", "Responder"
        ])
        self._proto_filter.currentTextChanged.connect(self._on_proto_filter)

        self._search_edit = QLineEdit()
        self._search_edit.setPlaceholderText("Filter interactions...")
        self._search_edit.setMaximumWidth(200)
        self._search_edit.textChanged.connect(self._proxy.set_needle)

        self._export_btn = QPushButton("Export")
        self._export_btn.setToolTip("Export interactions to JSON or CSV")
        self._export_btn.clicked.connect(self._on_export)
        self._clear_btn = QPushButton("Clear")
        self._clear_btn.clicked.connect(self._on_clear)

        row3 = QHBoxLayout()
        row3.addWidget(self._poll_btn)
        row3.addWidget(self._poll_now_btn)
        row3.addWidget(QLabel("every"))
        row3.addWidget(self._interval_spin)
        row3.addWidget(QLabel("Type:"))
        row3.addWidget(self._proto_filter)
        row3.addWidget(self._search_edit)
        row3.addStretch(1)
        row3.addWidget(self._export_btn)
        row3.addWidget(self._clear_btn)

        # Interactions table.
        self._table = QTableView()
        self._table.setModel(self._proxy)
        self._table.setSortingEnabled(True)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SingleSelection)
        self._table.setContextMenuPolicy(Qt.CustomContextMenu)
        self._table.customContextMenuRequested.connect(self._on_table_menu)
        self._table.verticalHeader().setDefaultSectionSize(
            self.fontMetrics().height() + 4
        )
        self._table.verticalHeader().setVisible(False)
        header = self._table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.Interactive)
        for column, width in {
            0: 45, 1: 95, 2: 85, 3: 360, 4: 140, 5: 90,
        }.items():
            self._table.setColumnWidth(column, width)
        self._table.sortByColumn(COL_INDEX, Qt.AscendingOrder)
        sel = self._table.selectionModel()
        sel.currentRowChanged.connect(self._on_row_selected)

        # Detail: the callback's raw request and raw response, shown in two
        # panes side by side just like the Repeater's Request/Response views.
        self._request_view = MessageView(read_only=True)
        self._request_find = FindBar(self._request_view)
        request_pane = self._pane("Request", self._request_view, self._request_find)

        self._response_view = MessageView(read_only=True)
        self._response_find = FindBar(self._response_view)
        response_pane = self._pane(
            "Response", self._response_view, self._response_find
        )

        detail_split = QSplitter(Qt.Horizontal)
        detail_split.addWidget(request_pane)
        detail_split.addWidget(response_pane)
        detail_split.setSizes([600, 600])

        split = QSplitter()
        split.setOrientation(Qt.Vertical)
        split.addWidget(self._table)
        split.addWidget(detail_split)
        split.setStretchFactor(0, 2)
        split.setStretchFactor(1, 3)

        layout = QVBoxLayout(self)
        layout.addLayout(row1)
        layout.addLayout(row2)
        layout.addLayout(row3)
        layout.addWidget(split, 1)

    @staticmethod
    def _pane(title: str, view: MessageView, find_bar: FindBar) -> QWidget:
        """Build a titled pane (label + find bar + view), matching Repeater."""
        container = QWidget()
        v = QVBoxLayout(container)
        v.setContentsMargins(0, 0, 0, 0)
        label = QLabel(title)
        label.setStyleSheet("font-weight: bold; padding: 4px;")
        v.addWidget(label)
        v.addWidget(find_bar)
        v.addWidget(view, 1)
        return container

    # -- registration ---------------------------------------------------------

    def _on_register_clicked(self) -> None:
        if self._client.registered:
            self._deregister()
        else:
            self._register()

    def _register(self) -> None:
        # Put the chosen server first, then the remaining configured fallbacks.
        chosen = self._server_combo.currentText().strip()
        servers = [chosen] if chosen else []
        for s in self._config.servers:
            if s != chosen:
                servers.append(s)
        token = self._token_edit.text().strip()
        self._config.token = token
        if chosen and chosen not in self._config.servers:
            self._config.servers.insert(0, chosen)
        self._status_label.setText("Registering...")
        self._status_label.setStyleSheet("color: orange;")
        self._register_btn.setEnabled(False)
        self._client.register(
            servers, token,
            lambda ok, server: self._register_ready.emit(ok, server),
            allow_http_fallback=self._config.allow_http_fallback,
        )

    def _deregister(self) -> None:
        self._stop_polling()
        self._keepalive_timer.stop()
        self._client.deregister()
        self._status_label.setText("Not registered")
        self._status_label.setStyleSheet("color: gray;")
        self._refresh_controls()

    @Slot(bool, str)
    def _on_registered(self, ok: bool, server: str) -> None:
        self._register_btn.setEnabled(True)
        if ok:
            self._status_label.setText(f"Registered @ {server}")
            self._status_label.setStyleSheet("color: #2ecc71;")
            # Reflect the actually-used server in the combo.
            netloc = server.split("://", 1)[-1]
            if self._server_combo.currentText().strip() != netloc:
                self._server_combo.setEditText(netloc)
            # Begin polling automatically once registered.
            self._create_payload(copy_to_clipboard=True)
            self._start_polling()
        else:
            msg = server or "registration failed"
            self._status_label.setText(f"Registration failed: {msg}")
            self._status_label.setStyleSheet("color: #c0392b;")
        self._refresh_controls()

    # -- payloads -------------------------------------------------------------

    def _ensure_registered(self) -> bool:
        if self._client.registered:
            return True
        QMessageBox.information(
            self, "Not registered",
            "Register with an Interactsh server first.",
        )
        return False

    def _on_generate(self) -> None:
        self._create_payload(copy_to_clipboard=True)

    def _create_payload(self, *, copy_to_clipboard: bool = False,
                        note: str = "") -> str | None:
        if not self._ensure_registered():
            return None
        try:
            host = self._client.new_payload()
        except InteractshError as exc:
            QMessageBox.warning(self, "Payload error", str(exc))
            return None
        self._payloads.append({"host": host, "note": note})
        self._payload_history.addItem(host)
        self._payload_history.setCurrentText(host)
        self._payload_edit.setText(host)
        self._clear_payloads_btn.setEnabled(True)
        if copy_to_clipboard:
            self._copy_to_clipboard(host)
        return host

    def _on_copy(self) -> None:
        text = self._payload_edit.text().strip()
        if text:
            self._copy_to_clipboard(text)

    def _set_token_visibility(self, visible: bool) -> None:
        self._token_edit.setEchoMode(
            QLineEdit.Normal if visible else QLineEdit.Password
        )
        icon_name = "view-hidden" if visible else "view-visible"
        icon = QIcon.fromTheme(icon_name)
        if icon.isNull():
            # Windows commonly has no freedesktop icon theme. Use clear,
            # professional text rather than an ambiguous decorative glyph.
            self._token_show_btn.setIcon(QIcon())
            self._token_show_btn.setText("Hide" if visible else "Show")
        else:
            self._token_show_btn.setText("")
            self._token_show_btn.setIcon(icon)
        self._token_show_btn.setToolTip(
            "Hide authentication token" if visible else "Show authentication token"
        )

    def _on_clear_payloads(self) -> None:
        if not self._payloads:
            return
        choice = QMessageBox.question(
            self,
            "Clear payloads",
            "Remove all locally saved payloads from the history?\n\n"
            "Existing payloads may still receive callbacks, but they will no "
            "longer be labelled here.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if choice != QMessageBox.Yes:
            return
        self._payloads.clear()
        self._payload_history.clear()
        self._payload_edit.clear()
        self._clear_payloads_btn.setEnabled(False)
        self._status_label.setText("Payload history cleared")
        self._status_label.setStyleSheet("color: #3498db;")

    def _copy_to_clipboard(self, text: str) -> None:
        clip = QGuiApplication.clipboard()
        if clip is not None:
            clip.setText(text)
        self.copy_payload_requested.emit(text)

    # -- polling --------------------------------------------------------------

    def _on_toggle_poll(self) -> None:
        if self._poll_btn.isChecked():
            self._start_polling()
        else:
            self._stop_polling()

    def _start_polling(self) -> None:
        if not self._client.registered:
            self._poll_btn.setChecked(False)
            return
        self._auto_poll = True
        self._poll_btn.setChecked(True)
        self._poll_btn.setText("Stop polling")
        self._poll_timer.start(self._interval_spin.value() * 1000)
        self._keepalive_timer.start()
        self._do_poll()

    def _stop_polling(self) -> None:
        self._auto_poll = False
        self._poll_timer.stop()
        self._poll_btn.setChecked(False)
        self._poll_btn.setText("Start polling")

    def _on_interval_changed(self, value: int) -> None:
        self._config.poll_interval_secs = value
        if self._auto_poll:
            self._poll_timer.start(value * 1000)

    def _do_poll(self) -> None:
        if not self._client.registered or self._poll_in_flight:
            return
        self._poll_in_flight = True
        self._poll_now_btn.setEnabled(False)
        self._status_label.setText("Polling…")
        self._status_label.setStyleSheet("color: #3498db;")
        self._client.poll(
            lambda interactions, error: self._poll_ready.emit(interactions, error)
        )

    def _do_keepalive(self) -> None:
        if not self._client.registered or self._keepalive_in_flight:
            return
        self._keepalive_in_flight = True
        self._client.keep_alive(
            lambda ok, error: self._keepalive_ready.emit(ok, error)
        )

    def _on_keepalive_result(self, ok: bool, error: str) -> None:
        self._keepalive_in_flight = False
        if not ok:
            if not self._client.registered and self._auto_poll:
                self._stop_polling()
                self._status_label.setText("Session expired; re-registering…")
                self._register()
                return
            self._status_label.setText(f"Session keep-alive failed: {error}")
            self._status_label.setStyleSheet("color: #e67e22;")

    @Slot(object, str)
    def _on_polled(self, interactions: list, error: str) -> None:
        self._poll_in_flight = False
        self._poll_now_btn.setEnabled(self._client.registered)
        self._last_poll_at = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
        if error:
            # Keep polling but surface transient errors quietly in the status.
            self._status_label.setText(f"Poll error: {error}")
            self._status_label.setStyleSheet("color: #e67e22;")
            return
        new_count = 0
        for interaction in interactions:
            uid = _interaction_key(interaction)
            if uid in self._seen_ids:
                continue
            self._seen_ids.add(uid)
            label = self._label_for(interaction)
            self._model.add_interaction(interaction, payload_label=label)
            new_count += 1
        removed = self._model.trim_to(self._config.max_interactions)
        if removed:
            self._seen_ids = {
                _interaction_key(row.interaction) for row in self._model.all_rows()
            }
        if new_count:
            self._table.scrollToBottom()
            server = self._client.server.split("://", 1)[-1]
            self._status_label.setText(
                f"Registered @ {server} - {self._model.rowCount()} interaction(s)"
            )
            self._status_label.setStyleSheet("color: #2ecc71;")
            self.interactions_received.emit(new_count)
        else:
            server = self._client.server.split("://", 1)[-1]
            self._status_label.setText(
                f"Polling @ {server} - no new interactions (last poll {self._last_poll_at})"
            )
            self._status_label.setStyleSheet("color: #2ecc71;")

    def _label_for(self, interaction: Interaction) -> str:
        """Best-effort correlate an interaction back to a generated payload."""
        full = (interaction.full_id or "").lower()
        for entry in self._payloads:
            if not isinstance(entry, dict):
                continue
            host = str(entry.get("host", "")).lower()
            # full_id is the host that was hit; match on the unique nonce part.
            nonce = host.split(".", 1)[0]
            if nonce and nonce in full:
                note = entry.get("note", "")
                return f"{host}  ({note})" if note else host
        return interaction.full_id or interaction.unique_id

    # -- selection / detail ---------------------------------------------------

    @Slot()
    def _on_row_selected(self, current, _previous=None) -> None:
        if current is None or not current.isValid():
            self._clear_detail()
            return
        source = self._proxy.mapToSource(current)
        row = self._model.row_at(source.row())
        if row is None:
            self._clear_detail()
            return
        it = row.interaction

        # A short summary line prepended to the request pane.
        summary_bits = [
            f"{(it.protocol or '').upper()} from {it.remote_address}",
            f"at {it.timestamp}",
            f"id {it.full_id}",
        ]
        if it.q_type:
            summary_bits.append(f"q-type {it.q_type}")
        if it.smtp_from:
            summary_bits.append(f"smtp-from {it.smtp_from}")
        summary = "  |  ".join(b for b in summary_bits if b)

        # Request pane: the raw request the target sent to the payload host.
        # Split the HTTP message so any HTML/JS/JSON body is pretty-printed.
        self._show_raw(self._request_view, it.raw_request,
                       summary, "(no raw request captured)")

        # Response pane: what the server sent back (formatted the same way).
        self._show_raw(self._response_view, it.raw_response,
                       "", "(no response captured)")

    @staticmethod
    def _show_raw(view: MessageView, raw: str, summary: str,
                  empty_msg: str) -> None:
        """Render a raw HTTP message, pretty-printing its body by content-type.

        Splits ``raw`` into start line + headers + body so that an HTML / JS /
        JSON body is formatted (via MessageView's Pretty mode) instead of shown
        as one minified line. Non-HTTP payloads (e.g. a bare DNS record) are
        shown as-is.
        """
        if not raw or not raw.strip():
            view.show_message(summary, "", None)
            return
        start_line, headers_text, body = _split_http_message(raw)
        # Prepend the interaction summary above the start line when present.
        header_block = headers_text
        content_type = content_type_from_headers(headers_text)
        top = summary
        first = start_line
        if summary and first:
            top = f"{summary}\r\n{first}"
        elif first:
            top = first
        view.show_message(
            top, header_block, body.encode("utf-8", errors="replace"),
            content_type=content_type or "",
        )

    def _clear_detail(self) -> None:
        self._request_view.clear_message()
        self._response_view.clear_message()

    def _on_table_menu(self, pos) -> None:
        index = self._table.indexAt(pos)
        menu = QMenu(self)
        copy_id_action = menu.addAction("Copy full ID")
        copy_src_action = menu.addAction("Copy source IP")
        menu.addSeparator()
        clear_action = menu.addAction("Clear all interactions")
        copy_id_action.setEnabled(index.isValid())
        copy_src_action.setEnabled(index.isValid())

        chosen = menu.exec(self._table.viewport().mapToGlobal(pos))
        if chosen is None:
            return
        if chosen == clear_action:
            self._on_clear()
            return
        source = self._proxy.mapToSource(index)
        row = self._model.row_at(source.row())
        if row is None:
            return
        if chosen == copy_id_action:
            self._copy_to_clipboard(row.interaction.full_id)
        elif chosen == copy_src_action:
            self._copy_to_clipboard(row.interaction.remote_address)

    # -- filter / export / clear ---------------------------------------------

    def _on_proto_filter(self, text: str) -> None:
        self._proxy.set_protocol("" if text == "All" else text)

    def _on_clear(self) -> None:
        if self._model.rowCount() and QMessageBox.question(
            self, "Clear interactions", "Clear all captured interactions?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        ) != QMessageBox.Yes:
            return
        self._model.clear()
        self._seen_ids.clear()
        self._clear_detail()

    def _on_export(self) -> None:
        rows = self._model.all_rows()
        if not rows:
            QMessageBox.information(self, "Export", "No interactions to export.")
            return
        path_str, selected = QFileDialog.getSaveFileName(
            self, "Export interactions", "interactions.json",
            "JSON (*.json);;CSV (*.csv)",
        )
        if not path_str:
            return
        path = Path(path_str)
        try:
            if path.suffix.lower() == ".csv" or "csv" in selected.lower():
                self._export_csv(path, rows)
            else:
                self._export_json(path, rows)
        except OSError as exc:
            QMessageBox.warning(self, "Export failed", str(exc))
            return
        self._status_label.setText(f"Exported {len(rows)} interactions to {path.name}")

    @staticmethod
    def _export_json(path: Path, rows) -> None:
        data = []
        for r in rows:
            item = r.interaction.to_dict()
            item["payload_label"] = r.payload_label
            item["note"] = r.note
            data.append(item)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @staticmethod
    def _export_csv(path: Path, rows) -> None:
        import csv

        with path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(
                ["#", "timestamp", "protocol", "full-id", "source", "q-type",
                 "payload", "note", "raw-request", "raw-response"]
            )
            for r in rows:
                it = r.interaction
                writer.writerow([
                    r.index + 1, it.timestamp, it.protocol,
                    it.full_id, it.remote_address, it.q_type,
                    r.payload_label, r.note, it.raw_request, it.raw_response,
                ])

    def _refresh_controls(self) -> None:
        registered = self._client.registered
        self._register_btn.setText("Deregister" if registered else "Register")
        self._generate_btn.setEnabled(registered)
        self._copy_btn.setEnabled(registered)
        self._poll_btn.setEnabled(registered)
        self._poll_now_btn.setEnabled(registered)
        self._server_combo.setEnabled(not registered)
        self._token_edit.setEnabled(not registered)
        self._http_fallback_check.setEnabled(not registered)
        self._clear_payloads_btn.setEnabled(bool(self._payloads))

    # -- annotate a payload (used when inserting into Repeater/Intruder) ------

    def annotate_last_payload(self, note: str) -> None:
        """Attach a note (e.g. the target tab) to the most recent payload."""
        if self._payloads:
            self._payloads[-1]["note"] = note

    def take_payload_for(self, note: str) -> str:
        """Generate a payload, tag it with ``note``, and return the hostname.

        Used by MainWindow to insert a fresh Collaborator payload into a
        Repeater/Intruder request via the right-click menu. Raises
        :class:`InteractshError` if not registered.
        """
        host = self._client.new_payload()
        return self._create_payload(note=note)

    @property
    def is_registered(self) -> bool:
        return self._client.registered

    # -- persistence ----------------------------------------------------------

    def save_state(self, path: Path) -> None:
        """Persist the session, generated payloads, and interactions to JSON."""
        info = self._client.session_info()
        session = _session_to_dict(info) if info else None
        protected_session = _protect_session(session) if session else None
        payload = {
            "session": None if protected_session else session,
            "session_protected": protected_session,
            "payloads": self._payloads,
            "interactions": [
                {**r.interaction.to_dict(), "payload_label": r.payload_label, "note": r.note}
                for r in self._model.all_rows()
            ],
            "poll_interval": self._interval_spin.value(),
            "servers": self._config.servers,
            "allow_http_fallback": self._config.allow_http_fallback,
            "max_interactions": self._config.max_interactions,
        }
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except OSError:
            pass

    def restore_state(self, path: Path) -> None:
        """Restore a session saved by :meth:`save_state` and re-register it."""
        try:
            raw = path.read_text(encoding="utf-8")
        except OSError:
            return
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            return

        self._payloads = list(payload.get("payloads", []))
        self._payload_history.clear()
        for item in self._payloads:
            host = item.get("host", "") if isinstance(item, dict) else ""
            if host:
                self._payload_history.addItem(host)
        self._clear_payloads_btn.setEnabled(bool(self._payloads))
        saved_servers = payload.get("servers")
        if isinstance(saved_servers, list):
            self._config.servers = [str(s) for s in saved_servers if str(s).strip()]
            self._server_combo.clear()
            self._server_combo.addItems(self._config.servers)
        if "allow_http_fallback" in payload:
            self._config.allow_http_fallback = bool(payload["allow_http_fallback"])
            self._http_fallback_check.setChecked(self._config.allow_http_fallback)
        if "max_interactions" in payload:
            self._config.max_interactions = max(100, int(payload["max_interactions"]))
        for item in payload.get("interactions", []):
            try:
                interaction = Interaction.from_dict(item)
            except Exception:  # noqa: BLE001
                continue
            self._seen_ids.add(_interaction_key(interaction))
            self._model.add_interaction(
                interaction,
                payload_label=item.get("payload_label") or self._label_for(interaction),
                note=item.get("note", ""),
            )
        self._model.trim_to(self._config.max_interactions)
        interval = int(payload.get("poll_interval", self._config.poll_interval_secs))
        self._interval_spin.setValue(max(2, min(300, interval)))

        session = payload.get("session")
        if payload.get("session_protected"):
            try:
                session = _unprotect_session(payload["session_protected"])
            except (ValueError, OSError):
                self._status_label.setText("Could not decrypt saved Collaborator session")
                self._status_label.setStyleSheet("color: #c0392b;")
                return
        if session:
            info = _session_from_dict(session)
            self._status_label.setText("Restoring session...")
            self._status_label.setStyleSheet("color: orange;")
            self._client.restore(
                info, lambda ok, server: self._register_ready.emit(ok, server)
            )

    def shutdown(self) -> None:
        """Stop polling and deregister on application close (best-effort)."""
        self._stop_polling()
        self._keepalive_timer.stop()
        if self._client.registered:
            self._client.deregister()


def _split_http_message(raw: str) -> tuple[str, str, str]:
    """Split a raw HTTP message into (start_line, headers, body).

    Tolerant of both CRLF and LF separators. If there's no blank-line
    separator (e.g. a non-HTTP record), the whole thing is treated as the body
    so it still displays.
    """
    normalized = raw.replace("\r\n", "\n")
    # Find the header/body separator (first blank line).
    sep = normalized.find("\n\n")
    if sep == -1:
        head, body = normalized, ""
    else:
        head, body = normalized[:sep], normalized[sep + 2:]
    lines = head.split("\n")
    if not lines:
        return "", "", body
    start_line = lines[0]
    headers = "\r\n".join(lines[1:])
    return start_line, headers, body


def _interaction_key(interaction: Interaction) -> str:
    """Return a stable dedupe key, including records with empty IDs."""
    explicit = interaction.unique_id or interaction.full_id
    if explicit:
        return f"id:{explicit.lower()}"
    material = "\x1f".join((
        interaction.protocol, interaction.timestamp, interaction.remote_address,
        interaction.q_type, interaction.smtp_from,
        interaction.raw_request, interaction.raw_response,
    ))
    return "hash:" + hashlib.sha256(material.encode("utf-8", "replace")).hexdigest()


def _session_to_dict(info: SessionInfo) -> dict:
    return {
        "server": info.server,
        "correlation_id": info.correlation_id,
        "secret_key": info.secret_key,
        "private_key_b64": info.private_key_b64,
        "public_key_b64": info.public_key_b64,
        "token": info.token,
    }


def _session_from_dict(data: dict) -> SessionInfo:
    return SessionInfo(
        server=data.get("server", ""),
        correlation_id=data.get("correlation_id", ""),
        secret_key=data.get("secret_key", ""),
        private_key_b64=data.get("private_key_b64", ""),
        public_key_b64=data.get("public_key_b64", ""),
        token=data.get("token", ""),
    )


def _protect_session(value: dict) -> str | None:
    """Encrypt session keys with the current Windows user's DPAPI key."""
    if os.name != "nt":
        return None
    class _Blob(ctypes.Structure):
        _fields_ = [("cbData", ctypes.c_ulong),
                    ("pbData", ctypes.POINTER(ctypes.c_byte))]
    raw = json.dumps(value).encode("utf-8")
    source = ctypes.create_string_buffer(raw)
    source_blob = _Blob(len(raw), ctypes.cast(source, ctypes.POINTER(ctypes.c_byte)))
    result_blob = _Blob()
    api = ctypes.windll.crypt32.CryptProtectData
    api.argtypes = [ctypes.POINTER(_Blob), ctypes.c_wchar_p,
                    ctypes.POINTER(_Blob), ctypes.c_void_p, ctypes.c_void_p,
                    ctypes.c_ulong, ctypes.POINTER(_Blob)]
    api.restype = ctypes.c_bool
    if not api(ctypes.byref(source_blob), "Bidoytu Collaborator session",
               None, None, None, 0, ctypes.byref(result_blob)):
        return None
    try:
        return base64.b64encode(
            ctypes.string_at(result_blob.pbData, result_blob.cbData)
        ).decode("ascii")
    finally:
        ctypes.windll.kernel32.LocalFree(result_blob.pbData)


def _unprotect_session(encoded: str) -> dict:
    if os.name != "nt":
        raise ValueError("encrypted session requires Windows")
    class _Blob(ctypes.Structure):
        _fields_ = [("cbData", ctypes.c_ulong),
                    ("pbData", ctypes.POINTER(ctypes.c_byte))]
    raw = base64.b64decode(encoded)
    source = ctypes.create_string_buffer(raw)
    source_blob = _Blob(len(raw), ctypes.cast(source, ctypes.POINTER(ctypes.c_byte)))
    result_blob = _Blob()
    api = ctypes.windll.crypt32.CryptUnprotectData
    api.argtypes = [ctypes.POINTER(_Blob), ctypes.c_void_p,
                    ctypes.POINTER(_Blob), ctypes.c_void_p, ctypes.c_void_p,
                    ctypes.c_ulong, ctypes.POINTER(_Blob)]
    api.restype = ctypes.c_bool
    if not api(ctypes.byref(source_blob), None, None, None, None, 0,
               ctypes.byref(result_blob)):
        raise ValueError("DPAPI decryption failed")
    try:
        value = json.loads(
            ctypes.string_at(result_blob.pbData, result_blob.cbData).decode("utf-8")
        )
        if not isinstance(value, dict):
            raise ValueError("invalid encrypted session")
        return value
    finally:
        ctypes.windll.kernel32.LocalFree(result_blob.pbData)
