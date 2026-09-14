"""Main application window.

Top-level layout is a QTabWidget with four tabs:
    - Proxy        : proxy controls + HTTP History / Intercept sub-tabs
    - Repeater     : edit and resend requests
    - Intruder     : automated fuzzing (positions, payloads, attack runner)
    - Collaborator : out-of-band (OAST) interaction listener via Interactsh

The window owns the ProxyEngine, the storage objects, and the shared async
HTTP sender, and wires proxy signals to persistence, the history model, and the
intercept panel.
"""
from __future__ import annotations

from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtGui import QActionGroup, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QMessageBox,
    QTabWidget,
)

from bidoytu import __app_name__
from bidoytu.config import AppConfig
from bidoytu.resources import logo_path
from bidoytu.net.async_sender import AsyncHttpSender
from bidoytu.proxy.engine import ProxyEngine
from bidoytu.storage.body_store import BodyStore
from bidoytu.storage.models import FlowRecord
from bidoytu.storage.repository import FlowRepository
from bidoytu.net.interactsh import InteractshError
from bidoytu.ui.collaborator_tab import CollaboratorTab
from bidoytu.ui.flow_table_model import FlowTableModel
from bidoytu.ui.intruder_tab import IntruderTab
from bidoytu.ui.message_view import MessageView
from bidoytu.ui.proxy_tab import ProxyTab
from bidoytu.ui.repeater_tab import RepeaterTab
from bidoytu.ui.theme import DARK, LIGHT, apply_theme, current_mode, save_theme
from bidoytu.workspace import Workspace, WorkspaceManager


class MainWindow(QMainWindow):
    def __init__(
        self,
        config: AppConfig,
        workspace: Workspace | None = None,
        workspace_manager: WorkspaceManager | None = None,
    ) -> None:
        super().__init__()
        self._config = config
        self._workspace = workspace
        self._workspace_manager = workspace_manager
        self._config.ensure_dirs()
        self._config.load_proxy_scope()

        self._repo = FlowRepository(config.db_path)
        self._body_store = BodyStore(config.bodies_dir)
        self._engine = ProxyEngine(config.proxy, confdir=str(config.confdir))
        self._sender = AsyncHttpSender()
        self._sender.start()

        # Name alone in the title bar; the logo is set as the window icon.
        title = __app_name__
        if workspace is not None:
            title = f"{__app_name__} — {workspace.name}"
        self.setWindowTitle(title)
        self._logo = QIcon(str(logo_path()))
        if not self._logo.isNull():
            self.setWindowIcon(self._logo)
        self.resize(1300, 850)

        self._model = FlowTableModel(self)

        # Top-level tabs.
        self._tabs = QTabWidget()
        self._proxy_tab = ProxyTab(
            self._model,
            include_scope=config.proxy.include_scope,
            exclude_scope=config.proxy.exclude_scope,
        )
        # Reflect the configured defaults in the address inputs.
        self._proxy_tab.host_edit.setText(config.proxy.listen_host)
        self._proxy_tab.set_port(config.proxy.listen_port)
        self._proxy_running = False
        self._repeater_tab = RepeaterTab(self._sender)
        self._intruder_tab = IntruderTab(self._sender)
        self._collaborator_tab = CollaboratorTab(self._sender, config.collaborator)
        self._tabs.addTab(self._proxy_tab, "Proxy")
        self._tabs.addTab(self._repeater_tab, "Repeater")
        self._tabs.addTab(self._intruder_tab, "Intruder")
        self._collab_tab_index = self._tabs.addTab(
            self._collaborator_tab, "Collaborator"
        )
        self.setCentralWidget(self._tabs)

        # Let Repeater/Intruder request editors insert a fresh Collaborator
        # payload from their right-click menu.
        self._repeater_tab.payload_provider = self._collaborator_payload
        self._intruder_tab.payload_provider = self._collaborator_payload

        self._build_menu()
        self._wire()
        self._load_history()
        # Restore any Repeater sessions from the previous run.
        self._repeater_tab.restore_sessions(self._config.repeater_sessions_path)
        # Restore the last Intruder attack configuration.
        self._intruder_tab.restore_state(self._config.intruder_attack_path)
        # Restore the Collaborator session (re-registers with the server).
        self._collaborator_tab.restore_state(self._config.collaborator_state_path)

        # Start the proxy automatically once the UI is up. Deferred to the event
        # loop so the window is shown first and any port-in-use dialog has a
        # visible parent to attach to.
        QTimer.singleShot(0, self._on_start)

    # -- menu / theme ---------------------------------------------------------

    def _build_menu(self) -> None:
        self._build_branding()

        session_menu = self.menuBar().addMenu("&Session")
        export_sessions = session_menu.addAction("Export all sessions...")
        export_sessions.triggered.connect(self._export_sessions)

        view_menu = self.menuBar().addMenu("&View")
        theme_menu = view_menu.addMenu("Theme")

        group = QActionGroup(self)
        group.setExclusive(True)

        self._light_action = theme_menu.addAction("Light")
        self._dark_action = theme_menu.addAction("Dark")
        for action, mode in ((self._light_action, LIGHT), (self._dark_action, DARK)):
            action.setCheckable(True)
            group.addAction(action)
            action.triggered.connect(lambda _=False, m=mode: self._set_theme(m))

        active = current_mode()
        self._light_action.setChecked(active == LIGHT)
        self._dark_action.setChecked(active == DARK)

    def _build_branding(self) -> None:
        """Pin the logo to the top-left of the menu bar."""
        menubar = self.menuBar()
        self._logo_label = QLabel(menubar)
        if not self._logo.isNull():
            self._logo_label.setPixmap(self._logo.pixmap(20, 20))
        self._logo_label.setContentsMargins(6, 0, 6, 0)
        menubar.setCornerWidget(self._logo_label, Qt.TopLeftCorner)

    def _set_theme(self, mode: str) -> None:
        app = QApplication.instance()
        if app is not None:
            apply_theme(app, mode)
        save_theme(mode)
        # Re-color every raw-message highlighter to match the new mode.
        for view in self.findChildren(MessageView):
            view.set_theme(mode)

    def _export_sessions(self) -> None:
        """Export every locally saved session to one portable archive."""
        if self._workspace_manager is None:
            return
        from pathlib import Path
        from PySide6.QtWidgets import QFileDialog

        filename, _ = QFileDialog.getSaveFileName(
            self, "Export all sessions", "bidoytu-sessions.bidoytu.zip",
            "Bidoytu sessions (*.bidoytu.zip)",
        )
        if not filename:
            return
        path = Path(filename)
        if path.suffix.lower() != ".zip":
            path = path.with_suffix(".bidoytu.zip")
        try:
            self._save_workspace_state()
            self._workspace_manager.export_all(path)
        except OSError as exc:
            QMessageBox.warning(self, "Export failed", str(exc))
            return
        QMessageBox.information(self, "Sessions exported", f"Saved to {path.name}.")

    def _save_workspace_state(self) -> None:
        """Flush state that lives in widgets rather than the flow repository."""
        self._config.save_proxy_scope()
        self._repeater_tab.save_sessions(self._config.repeater_sessions_path)
        self._intruder_tab.save_state(self._config.intruder_attack_path)
        self._collaborator_tab.save_state(self._config.collaborator_state_path)

    # -- wiring ---------------------------------------------------------------

    def _wire(self) -> None:
        # Proxy controls. One button toggles start/stop.
        self._proxy_tab.toggle_btn.clicked.connect(self._on_toggle_proxy)
        self._proxy_tab.clear_btn.clicked.connect(self._on_clear)
        self._proxy_tab.ca_btn.clicked.connect(self._on_show_ca)
        self._proxy_tab.scope_changed.connect(self._on_scope_changed)

        # Engine signals.
        self._engine.flow_captured.connect(self._on_flow_captured)
        self._engine.flow_intercepted.connect(self._on_flow_intercepted)
        self._engine.response_intercepted.connect(self._on_response_intercepted)
        self._engine.started_ok.connect(self._on_started)
        self._engine.stopped.connect(self._on_stopped)
        self._engine.error.connect(self._on_error)

        # History body provider + send-to actions.
        self._proxy_tab.history.body_provider = self._body_of
        self._proxy_tab.history.send_to_repeater.connect(self._send_to_repeater)
        self._proxy_tab.history.send_to_intruder.connect(self._send_to_intruder)

        # Intercept panel callbacks.
        self._proxy_tab.intercept.on_toggle_intercept = self._engine.set_intercept_enabled
        self._proxy_tab.intercept.on_forward = self._engine.forward
        self._proxy_tab.intercept.on_drop = self._engine.drop
        # Response interception: global toggle, per-flow arm, and resolving
        # paused responses (forward/drop).
        self._proxy_tab.intercept.on_toggle_intercept_responses = (
            self._engine.set_intercept_responses
        )
        self._proxy_tab.intercept.on_intercept_response_for = (
            self._engine.intercept_response_for
        )
        self._proxy_tab.intercept.on_forward_response = self._engine.forward_response
        self._proxy_tab.intercept.on_drop_response = self._engine.drop_response
        # Send-to from the intercept panel too.
        self._proxy_tab.intercept.send_to_repeater.connect(self._send_to_repeater)
        self._proxy_tab.intercept.send_to_intruder.connect(self._send_to_intruder)

        # Send-to from a Repeater/Intruder request's right-click menu.
        self._repeater_tab.send_to_repeater.connect(self._send_to_repeater)
        self._repeater_tab.send_to_intruder.connect(self._send_to_intruder)
        self._intruder_tab.send_to_repeater.connect(self._send_to_repeater)
        self._intruder_tab.send_to_intruder.connect(self._send_to_intruder)

        # Badge the Collaborator tab when new out-of-band interactions arrive
        # (unless it is already the active tab). Clear the badge on switch to it.
        self._collaborator_tab.interactions_received.connect(
            self._on_collaborator_interactions
        )
        self._tabs.currentChanged.connect(self._on_tab_changed)

    # -- proxy control --------------------------------------------------------

    @Slot()
    def _on_toggle_proxy(self) -> None:
        if self._proxy_running:
            self._on_stop()
        else:
            self._on_start()

    def _on_start(self) -> None:
        # Apply the host/port chosen in the UI before starting. The engine
        # reads these fields when it binds, so updating them here is enough.
        self._config.proxy.listen_host = self._proxy_tab.listen_host()
        self._config.proxy.listen_port = self._proxy_tab.listen_port()
        self._proxy_tab.set_status("Starting proxy...")
        # Disable the toggle until we hear back (started/error).
        self._proxy_tab.toggle_btn.setEnabled(False)
        self._engine.start()

    @Slot(list, list)
    def _on_scope_changed(self, include_scope: list[str],
                          exclude_scope: list[str]) -> None:
        self._config.proxy.include_scope = list(include_scope)
        self._config.proxy.exclude_scope = list(exclude_scope)
        self._engine.set_scope(include_scope, exclude_scope)

    def _on_stop(self) -> None:
        self._proxy_tab.set_status("Stopping proxy...")
        self._proxy_tab.toggle_btn.setEnabled(False)
        self._engine.stop()

    @Slot(str, int)
    def _on_started(self, host: str, port: int) -> None:
        self._proxy_running = True
        self._proxy_tab.set_status(f"Proxy listening on {host}:{port}")
        self._proxy_tab.set_running(True)

    @Slot()
    def _on_stopped(self) -> None:
        self._proxy_running = False
        self._proxy_tab.set_status("Proxy stopped")
        self._proxy_tab.set_running(False)

    @Slot(str)
    def _on_error(self, message: str) -> None:
        self._proxy_running = False
        self._proxy_tab.set_status(f"Proxy error: {message}")
        self._proxy_tab.set_running(False)
        # A busy listen port is the common, recoverable failure. Show a clear,
        # actionable dialog that tells the user the port is taken and lets them
        # change it and retry, or open the proxy settings to pick a new one.
        if "in use" in message.lower():
            self._show_port_in_use_dialog()
            return
        QMessageBox.critical(self, "Proxy error", message)

    def _show_port_in_use_dialog(self) -> None:
        host = self._proxy_tab.listen_host()
        port = self._proxy_tab.listen_port()
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Warning)
        box.setWindowTitle("Port already in use")
        box.setText(f"Port {port} on {host} is already in use.")
        box.setInformativeText(
            "Another program (possibly another Bidoytu instance) is already "
            "listening on this port.\n\n"
            "Close whatever is using the port, or change the port and try again."
        )
        change_btn = box.addButton("Change Port...", QMessageBox.AcceptRole)
        retry_btn = box.addButton("Retry", QMessageBox.ActionRole)
        box.addButton("Cancel", QMessageBox.RejectRole)
        box.setDefaultButton(change_btn)
        box.exec()
        clicked = box.clickedButton()
        if clicked is change_btn:
            # Surface the proxy settings popup so the user can edit the port.
            self._proxy_tab.settings_btn.showMenu()
        elif clicked is retry_btn:
            self._on_start()

    # -- flow handling --------------------------------------------------------

    @Slot(object, bool)
    def _on_flow_captured(self, record: FlowRecord, is_response: bool) -> None:
        # Show responses for intercepted flows BEFORE persisting: _persist may
        # offload a large response body to the file store and null the inline
        # copy, so the panel must read it while it is still present.
        if is_response:
            self._proxy_tab.intercept.on_response(record)
        self._persist(record)
        self._model.upsert_record(record)

    @Slot(object)
    def _on_flow_intercepted(self, record: FlowRecord) -> None:
        self._proxy_tab.intercept.enqueue(record)

    @Slot(object)
    def _on_response_intercepted(self, record: FlowRecord) -> None:
        self._proxy_tab.intercept.enqueue_response(record)

    def _persist(self, record: FlowRecord) -> None:
        limit = self._config.body_inline_limit
        if record.request_body_inline and len(record.request_body_inline) > limit:
            record.request_body_path = self._body_store.store(record.request_body_inline)
            record.request_body_inline = None
        if record.response_body_inline and len(record.response_body_inline) > limit:
            record.response_body_path = self._body_store.store(record.response_body_inline)
            record.response_body_inline = None
        self._repo.upsert(record)

    def _load_history(self) -> None:
        self._model.load_records(self._repo.list_all())

    @Slot()
    def _on_show_ca(self) -> None:
        from bidoytu.ui.ca_dialog import CaCertDialog

        dialog = CaCertDialog(
            self._config.ca_cert_pem, self._config.ca_cert_cer, self
        )
        dialog.exec()

    @Slot()
    def _on_clear(self) -> None:
        self._repo.clear()
        self._model.clear()
        self._proxy_tab.history.clear_detail()

    def _body_of(self, record: FlowRecord, response: bool) -> bytes | None:
        inline = record.response_body_inline if response else record.request_body_inline
        path = record.response_body_path if response else record.request_body_path
        if inline is not None:
            return inline
        if path and self._body_store.exists(path):
            return self._body_store.load(path)
        return None

    # -- send-to actions ------------------------------------------------------

    @Slot(object)
    def _send_to_repeater(self, record: FlowRecord) -> None:
        # Ensure the request body is materialized for editing.
        self._hydrate_request_body(record)
        self._repeater_tab.load_from_record(record)
        self._tabs.setCurrentWidget(self._repeater_tab)

    @Slot(object)
    def _send_to_intruder(self, record: FlowRecord) -> None:
        self._hydrate_request_body(record)
        self._intruder_tab.load_from_record(record)
        self._tabs.setCurrentWidget(self._intruder_tab)

    # -- collaborator ---------------------------------------------------------

    def _collaborator_payload(self):
        """Return a fresh Collaborator payload host, or None if unavailable.

        Called by Repeater/Intruder request editors when the user picks
        "Insert Collaborator payload". Prompts to register if the session isn't
        set up yet.
        """
        if not self._collaborator_tab.is_registered:
            QMessageBox.information(
                self, "Collaborator not registered",
                "Open the Collaborator tab and register with an Interactsh "
                "server before inserting a payload.",
            )
            return None
        try:
            return self._collaborator_tab.take_payload_for("inserted into request")
        except InteractshError as exc:
            QMessageBox.warning(self, "Payload error", str(exc))
            return None

    @Slot(int)
    def _on_collaborator_interactions(self, count: int) -> None:
        # Only badge when the user isn't already looking at the tab.
        if self._tabs.currentIndex() != self._collab_tab_index:
            base = "Collaborator"
            current = self._tabs.tabText(self._collab_tab_index)
            # Accumulate the count shown in the badge.
            shown = 0
            if current.endswith(")") and "(" in current:
                try:
                    shown = int(current[current.rindex("(") + 1:-1])
                except ValueError:
                    shown = 0
            self._tabs.setTabText(
                self._collab_tab_index, f"{base} ({shown + count})"
            )

    @Slot(int)
    def _on_tab_changed(self, index: int) -> None:
        if index == self._collab_tab_index:
            self._tabs.setTabText(self._collab_tab_index, "Collaborator")

    def _hydrate_request_body(self, record: FlowRecord) -> None:
        """Load a file-backed request body inline so editors can show it."""
        if record.request_body_inline is None and record.request_body_path:
            if self._body_store.exists(record.request_body_path):
                record.request_body_inline = self._body_store.load(record.request_body_path)

    # -- shutdown -------------------------------------------------------------

    def closeEvent(self, event) -> None:
        discard = False
        if self._workspace is not None and self._workspace_manager is not None:
            choice = QMessageBox(self)
            choice.setIcon(QMessageBox.Question)
            choice.setWindowTitle("Close session")
            choice.setText(f"What would you like to do with '{self._workspace.name}'?")
            choice.setInformativeText(
                "Save keeps this session locally. Discard permanently removes its "
                "history, requests, bodies, and saved tool state."
            )
            save_button = choice.addButton("Save session", QMessageBox.AcceptRole)
            discard_button = choice.addButton("Discard session", QMessageBox.DestructiveRole)
            cancel_button = choice.addButton(QMessageBox.Cancel)
            choice.setDefaultButton(save_button)
            choice.exec()
            if choice.clickedButton() is None or choice.clickedButton() is cancel_button:
                event.ignore()
                return
            discard = choice.clickedButton() is discard_button

        if not discard:
            self._save_workspace_state()
        self._collaborator_tab.shutdown()
        if self._engine.isRunning():
            self._engine.stop()
        self._sender.stop()
        self._repo.close()
        if discard and self._workspace is not None and self._workspace_manager is not None:
            self._workspace_manager.discard(self._workspace)
        elif self._workspace is not None and self._workspace_manager is not None:
            self._workspace_manager.touch(self._workspace)
        super().closeEvent(event)
