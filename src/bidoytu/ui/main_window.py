"""Main application window.

Top-level layout is a QTabWidget with six tabs:
    - Proxy        : proxy controls + HTTP History / Intercept sub-tabs
    - Target       : sitemap review + target scope configuration
    - Repeater     : edit and resend requests
    - Intruder     : automated fuzzing (positions, payloads, attack runner)
    - Collaborator : out-of-band (OAST) interaction listener via Interactsh
    - Live audit   : opt-in passive findings from captured proxy traffic

The window owns the ProxyEngine, the storage objects, and the shared async
HTTP sender, and wires proxy signals to persistence, the history model, and the
intercept panel.
"""
from __future__ import annotations

from dataclasses import replace

from PySide6.QtCore import QTimer, Signal, Slot
from PySide6.QtGui import QActionGroup, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QTabWidget,
)

from bidoytu import __app_name__
from bidoytu.config import AppConfig
from bidoytu.config import host_matches_scope
from bidoytu.resources import logo_path
from bidoytu.net.async_sender import AsyncHttpSender
from bidoytu.audit.service import LiveAuditService
from bidoytu.audit.active_scan import ActiveScanResult, ActiveScanWorker
from bidoytu.proxy.engine import ProxyEngine
from bidoytu.storage.body_store import BodyStore
from bidoytu.storage.models import FlowRecord
from bidoytu.storage.repository import FlowRepository
from bidoytu.net.interactsh import InteractshError
from bidoytu.ui.collaborator_tab import CollaboratorTab
from bidoytu.ui.audit_tab import LiveAuditTab
from bidoytu.ui.flow_table_model import FlowTableModel
from bidoytu.ui.intruder_tab import IntruderTab
from bidoytu.ui.message_view import MessageView
from bidoytu.ui.proxy_tab import ProxyTab
from bidoytu.ui.repeater_tab import RepeaterTab
from bidoytu.ui.target_tab import TargetTab
from bidoytu.ui.theme import DARK, LIGHT, apply_theme, current_mode, save_theme
from bidoytu.workspace import Workspace, WorkspaceManager


class MainWindow(QMainWindow):
    active_scan_result = Signal(object)

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
        self._repo.cleanup(
            config.history_max_rows or None,
            config.history_max_age_days or None,
        )
        self._body_store = BodyStore(config.bodies_dir)
        self._engine = ProxyEngine(config.proxy, confdir=str(config.confdir))
        self._sender = AsyncHttpSender()
        self._sender.start()
        self._audit_service = LiveAuditService()
        # Active workers emit through this Qt signal; the connected slot below
        # therefore always updates the issue model on the UI thread.
        self._active_scan = ActiveScanWorker(self.active_scan_result.emit)

        # Name alone in the title bar; the logo is set as the window icon.
        title = __app_name__
        if workspace is not None:
            title = f"{__app_name__} - {workspace.name}"
        self.setWindowTitle(title)
        self._logo = QIcon(str(logo_path()))
        if not self._logo.isNull():
            self.setWindowIcon(self._logo)
        self.resize(1300, 850)

        self._model = FlowTableModel(self)
        # Scope-table edits can emit repeatedly while text is being changed.
        # The proxy receives new rules immediately; history reclassification is
        # coalesced so it cannot freeze the event loop on every keystroke.
        self._scope_refresh_timer = QTimer(self)
        self._scope_refresh_timer.setSingleShot(True)
        self._scope_refresh_timer.setInterval(300)
        self._scope_refresh_timer.timeout.connect(self._refresh_history_scope)

        # Top-level tabs.
        self._tabs = QTabWidget()
        self._proxy_tab = ProxyTab(
            self._model,
            include_scope=config.proxy.include_scope,
            exclude_scope=config.proxy.exclude_scope,
            ssl_insecure=config.proxy.ssl_insecure,
        )
        self._target_tab = TargetTab(
            config.proxy.include_scope, config.proxy.exclude_scope,
            config.proxy.include_paths, config.proxy.exclude_paths,
            config.proxy.include_regex, config.proxy.exclude_regex,
            config.proxy.sitemaps,
        )
        # Reflect the configured defaults in the address inputs.
        self._proxy_tab.host_edit.setText(config.proxy.listen_host)
        self._proxy_tab.set_port(config.proxy.listen_port)
        self._proxy_running = False
        self._repeater_tab = RepeaterTab(self._sender)
        self._intruder_tab = IntruderTab(self._sender)
        self._collaborator_tab = CollaboratorTab(self._sender, config.collaborator)
        self._audit_tab = LiveAuditTab(self._audit_service)
        self._tabs.addTab(self._proxy_tab, "Proxy")
        self._target_tab_index = self._tabs.addTab(self._target_tab, "Target")
        self._tabs.addTab(self._repeater_tab, "Repeater")
        self._tabs.addTab(self._intruder_tab, "Intruder")
        self._collab_tab_index = self._tabs.addTab(
            self._collaborator_tab, "Collaborator"
        )
        self._tabs.addTab(self._audit_tab, "Live audit")
        self.setCentralWidget(self._tabs)

        # Let Repeater/Intruder request editors insert a fresh Collaborator
        # payload from their right-click menu.
        self._repeater_tab.payload_provider = self._collaborator_payload
        self._intruder_tab.payload_provider = self._collaborator_payload

        self._build_menu()
        self._wire()
        self._load_history()
        self._proxy_tab.history.set_saved_filters(self._repo.list_saved_filters())
        # Restore any Repeater sessions from the previous run.
        self._repeater_tab.restore_sessions(self._config.repeater_sessions_path)
        # Always show at least one (empty) request/response frame by default.
        self._repeater_tab.ensure_default_session()
        # Restore the last Intruder attack configuration.
        self._intruder_tab.restore_state(self._config.intruder_attack_path)
        # Always show at least one (empty) attack frame by default.
        self._intruder_tab.ensure_default_session()
        # Restore the Collaborator session (re-registers with the server).
        self._collaborator_tab.restore_state(self._config.collaborator_state_path)

        # Start the proxy automatically once the UI is up. Deferred to the event
        # loop so the window is shown first and any port-in-use dialog has a
        # visible parent to attach to.
        QTimer.singleShot(0, self._on_start)

    # -- menu / theme ---------------------------------------------------------

    def _build_menu(self) -> None:
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

        session_menu = self.menuBar().addMenu("&Session")
        export_sessions = session_menu.addAction("Export all sessions...")
        export_sessions.triggered.connect(self._export_sessions)

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
        # Tab-bar Clear History button (popup confirmation before it fires).
        self._proxy_tab.clear_history_requested.connect(self._on_clear)
        self._proxy_tab.ca_btn.clicked.connect(self._on_show_ca)
        self._proxy_tab.browser_integration_requested.connect(self._on_show_browser_integration)
        self._target_tab.scope_changed.connect(self._on_scope_changed)

        # Engine signals.
        self._engine.flow_captured.connect(self._on_flow_captured)
        self._engine.flow_intercepted.connect(self._on_flow_intercepted)
        self._engine.response_intercepted.connect(self._on_response_intercepted)
        self._engine.started_ok.connect(self._on_started)
        self._engine.stopped.connect(self._on_stopped)
        self._engine.error.connect(self._on_error)

        # History body provider + send-to actions.
        self._proxy_tab.history.body_provider = self._body_of
        self._audit_tab.body_provider = self._body_of
        self._audit_tab.active_changed.connect(self._on_active_audit_changed)
        self.active_scan_result.connect(self._on_active_scan_result)
        self._target_tab.set_body_provider(self._body_of)
        self._proxy_tab.history.send_to_repeater.connect(self._send_to_repeater)
        self._proxy_tab.history.send_to_intruder.connect(self._send_to_intruder)
        self._proxy_tab.history.metadata_changed.connect(self._on_history_metadata_changed)
        self._proxy_tab.history.save_filter_requested.connect(self._on_save_filter)
        self._proxy_tab.history.delete_filter_requested.connect(self._on_delete_saved_filter)

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
        if self._engine.isRunning():
            # A previous stop is still draining its asyncio listener.
            self._proxy_tab.set_status("Stopping proxy; please wait...")
            return
        # Apply the host/port chosen in the UI before starting. The engine
        # reads these fields when it binds, so updating them here is enough.
        self._config.proxy.listen_host = self._proxy_tab.listen_host()
        self._config.proxy.listen_port = self._proxy_tab.listen_port()
        self._config.proxy.ssl_insecure = self._proxy_tab.ssl_insecure_check.isChecked()
        self._proxy_tab.set_status("Starting proxy...")
        # Disable the toggle until we hear back (started/error).
        self._proxy_tab.toggle_btn.setEnabled(False)
        self._engine.start()

    @Slot(list, list, list, list, list, list, list)
    def _on_scope_changed(self, include_scope: list[str], exclude_scope: list[str],
                          include_paths: list[str], exclude_paths: list[str],
                          include_regex: list[str], exclude_regex: list[str],
                          sitemaps: list[str]) -> None:
        self._config.proxy.include_scope = list(include_scope)
        self._config.proxy.exclude_scope = list(exclude_scope)
        self._config.proxy.include_paths = list(include_paths)
        self._config.proxy.exclude_paths = list(exclude_paths)
        self._config.proxy.include_regex = list(include_regex)
        self._config.proxy.exclude_regex = list(exclude_regex)
        self._config.proxy.sitemaps = list(sitemaps)
        self._engine.set_scope(include_scope, exclude_scope, include_paths,
                                exclude_paths, include_regex, exclude_regex)
        self._scope_refresh_timer.start()

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
        # Scope is normally persisted below. Calculate it before the passive
        # audit too, so excluded traffic can never produce a live finding.
        record.scope = host_matches_scope(
            record.host, self._config.proxy.include_scope, self._config.proxy.exclude_scope,
            record.path, self._config.proxy.include_paths, self._config.proxy.exclude_paths,
            self._config.proxy.include_regex, self._config.proxy.exclude_regex,
        )
        audit_item, audit_issues = self._audit_service.analyze(record, is_response)
        if self._audit_service.enabled:
            self._audit_tab.add(audit_item, audit_issues)
        if not is_response:
            self._active_scan.submit(record)
        self._persist(record)
        # Keep the in-memory table and site map synchronized with the durable
        # history.  The repository is the source of truth across restarts, but
        # the live UI model must also receive each request/response event.
        # Bodies are loaded lazily from the body store/repository by the detail
        # view, so do not retain large payloads in the Qt model.
        summary = replace(record, request_body_inline=None, response_body_inline=None)
        self._model.upsert_record(summary)
        self._target_tab.add_record(summary, defer=True)

    @Slot(bool)
    def _on_active_audit_changed(self, enabled: bool) -> None:
        self._active_scan.set_enabled(enabled)
        if enabled:
            self._audit_tab._status.setText(
                "On — passive audit plus active verification for safe methods"
            )

    @Slot(object)
    def _on_active_scan_result(self, result: ActiveScanResult) -> None:
        """Marshal a worker finding back to the Qt-owned issue model."""
        self._audit_tab.add_active_issue(result.issue)

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
        self._repo.mark_duplicate(record)

    def _load_history(self) -> None:
        self._refresh_history_scope()

    def _refresh_history_scope(self) -> None:
        """Reclassify existing rows when target scope rules change."""
        records = self._model.all_records()
        if not records:
            records = self._repo.list_summaries()
            self._model.load_records(records)
            self._target_tab.set_records(records)
        changed = []
        for record in records:
            in_scope = host_matches_scope(
                record.host,
                self._config.proxy.include_scope,
                self._config.proxy.exclude_scope,
                record.path, self._config.proxy.include_paths,
                self._config.proxy.exclude_paths, self._config.proxy.include_regex,
                self._config.proxy.exclude_regex,
            )
            if record.scope != in_scope:
                record.scope = in_scope
                changed.append(record)
        self._repo.update_scopes(changed)
        if hasattr(self._proxy_tab, "history"):
            self._proxy_tab.history._apply_filters()

    @Slot()
    def _on_show_ca(self) -> None:
        from bidoytu.ui.ca_dialog import CaCertDialog

        dialog = CaCertDialog(
            self._config.ca_cert_pem, self._config.ca_cert_cer, self
        )
        dialog.exec()

    @Slot()
    def _on_show_browser_integration(self) -> None:
        from bidoytu.ui.browser_dialog import BrowserIntegrationDialog

        if not self._proxy_running:
            QMessageBox.warning(
                self, "Proxy is stopped",
                "Start the proxy before launching a browser through Bidoytu.",
            )
            return
        dialog = BrowserIntegrationDialog(
            self._config.proxy.listen_host,
            self._config.proxy.listen_port,
            self._config.ca_cert_pem,
            self._config.browser_profiles_dir,
            self,
        )
        dialog.browser_launched.connect(self._track_browser_process)
        dialog.exec()

    @Slot(object)
    def _track_browser_process(self, process) -> None:
        if not hasattr(self, "_browser_processes"):
            self._browser_processes = []
        self._browser_processes.append(process)

    @Slot()
    def _on_clear(self) -> None:
        self._repo.clear()
        self._model.clear()
        self._proxy_tab.history.clear_detail()
        self._audit_tab.clear()

    def _body_of(self, record: FlowRecord, response: bool) -> bytes | None:
        inline = record.response_body_inline if response else record.request_body_inline
        path = record.response_body_path if response else record.request_body_path
        if inline is not None:
            return inline
        if path and self._body_store.exists(path):
            return self._body_store.load(path)
        return self._repo.body(record.id, response) if record.id is not None else None

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

    @Slot(object)
    def _on_history_metadata_changed(self, record: FlowRecord) -> None:
        self._repo.update(record)
        self._model.upsert_record(record)

    @Slot(str, str)
    def _on_save_filter(self, name: str, query: str) -> None:
        self._repo.save_filter(name, query)
        self._proxy_tab.history.set_saved_filters(self._repo.list_saved_filters())

    @Slot(str)
    def _on_delete_saved_filter(self, name: str) -> None:
        self._repo.delete_saved_filter(name)
        self._proxy_tab.history.set_saved_filters(self._repo.list_saved_filters())

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
        self._target_tab.set_active(index == self._target_tab_index)
        if index == self._collab_tab_index:
            self._tabs.setTabText(self._collab_tab_index, "Collaborator")

    def _hydrate_request_body(self, record: FlowRecord) -> None:
        """Load a file-backed request body inline so editors can show it."""
        if record.request_body_inline is None and record.request_body_path:
            if self._body_store.exists(record.request_body_path):
                record.request_body_inline = self._body_store.load(record.request_body_path)
        elif record.request_body_inline is None and record.id is not None:
            record.request_body_inline = self._repo.body(record.id, response=False)

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
        self._active_scan.stop()
        from bidoytu.browser_integration import stop_browser

        for process in getattr(self, "_browser_processes", []):
            stop_browser(process)
        self._browser_processes = []
        if self._engine.isRunning():
            self._engine.stop()
        self._sender.stop()
        self._repo.close()
        if discard and self._workspace is not None and self._workspace_manager is not None:
            self._workspace_manager.discard(self._workspace)
        elif self._workspace is not None and self._workspace_manager is not None:
            self._workspace_manager.touch(self._workspace)
        super().closeEvent(event)
