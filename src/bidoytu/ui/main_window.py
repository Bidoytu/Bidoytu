"""Main application window.

Top-level layout is a QTabWidget with three tabs:
    - Proxy    : proxy controls + HTTP History / Intercept sub-tabs
    - Repeater : edit and resend requests
    - Intruder : (skeleton) request template + payloads

The window owns the ProxyEngine, the storage objects, and the shared async
HTTP sender, and wires proxy signals to persistence, the history model, and the
intercept panel.
"""
from __future__ import annotations

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QMainWindow, QMessageBox, QTabWidget

from bidoytu.config import AppConfig
from bidoytu.net.async_sender import AsyncHttpSender
from bidoytu.proxy.engine import ProxyEngine
from bidoytu.storage.body_store import BodyStore
from bidoytu.storage.models import FlowRecord
from bidoytu.storage.repository import FlowRepository
from bidoytu.ui.flow_table_model import FlowTableModel
from bidoytu.ui.intruder_tab import IntruderTab
from bidoytu.ui.proxy_tab import ProxyTab
from bidoytu.ui.repeater_tab import RepeaterTab


class MainWindow(QMainWindow):
    def __init__(self, config: AppConfig) -> None:
        super().__init__()
        self._config = config
        self._config.ensure_dirs()

        self._repo = FlowRepository(config.db_path)
        self._body_store = BodyStore(config.bodies_dir)
        self._engine = ProxyEngine(config.proxy, confdir=str(config.confdir))
        self._sender = AsyncHttpSender()
        self._sender.start()

        self.setWindowTitle("Bidoytu - Intercepting Proxy")
        self.resize(1300, 850)

        self._model = FlowTableModel(self)

        # Top-level tabs.
        self._tabs = QTabWidget()
        self._proxy_tab = ProxyTab(self._model)
        # Reflect the configured defaults in the address inputs.
        self._proxy_tab.host_edit.setText(config.proxy.listen_host)
        self._proxy_tab.port_spin.setValue(config.proxy.listen_port)
        self._repeater_tab = RepeaterTab(self._sender)
        self._intruder_tab = IntruderTab(self._sender)
        self._tabs.addTab(self._proxy_tab, "Proxy")
        self._tabs.addTab(self._repeater_tab, "Repeater")
        self._tabs.addTab(self._intruder_tab, "Intruder")
        self.setCentralWidget(self._tabs)

        self._wire()
        self._load_history()
        # Restore any Repeater sessions from the previous run.
        self._repeater_tab.restore_sessions(self._config.repeater_sessions_path)

    # -- wiring ---------------------------------------------------------------

    def _wire(self) -> None:
        # Proxy controls.
        self._proxy_tab.start_btn.clicked.connect(self._on_start)
        self._proxy_tab.stop_btn.clicked.connect(self._on_stop)
        self._proxy_tab.clear_btn.clicked.connect(self._on_clear)
        self._proxy_tab.ca_btn.clicked.connect(self._on_show_ca)

        # Engine signals.
        self._engine.flow_captured.connect(self._on_flow_captured)
        self._engine.flow_intercepted.connect(self._on_flow_intercepted)
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
        # Send-to from the intercept panel too.
        self._proxy_tab.intercept.send_to_repeater.connect(self._send_to_repeater)
        self._proxy_tab.intercept.send_to_intruder.connect(self._send_to_intruder)

    # -- proxy control --------------------------------------------------------

    @Slot()
    def _on_start(self) -> None:
        # Apply the host/port chosen in the UI before starting. The engine
        # reads these fields when it binds, so updating them here is enough.
        self._config.proxy.listen_host = self._proxy_tab.listen_host()
        self._config.proxy.listen_port = self._proxy_tab.listen_port()
        self._proxy_tab.set_status("Starting proxy...")
        self._proxy_tab.start_btn.setEnabled(False)
        self._engine.start()

    @Slot()
    def _on_stop(self) -> None:
        self._proxy_tab.set_status("Stopping proxy...")
        self._proxy_tab.stop_btn.setEnabled(False)
        self._engine.stop()

    @Slot(str, int)
    def _on_started(self, host: str, port: int) -> None:
        self._proxy_tab.set_status(f"Proxy listening on {host}:{port}")
        self._proxy_tab.set_running(True)

    @Slot()
    def _on_stopped(self) -> None:
        self._proxy_tab.set_status("Proxy stopped")
        self._proxy_tab.set_running(False)

    @Slot(str)
    def _on_error(self, message: str) -> None:
        self._proxy_tab.set_status(f"Proxy error: {message}")
        self._proxy_tab.set_running(False)
        QMessageBox.critical(self, "Proxy error", message)

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

    def _hydrate_request_body(self, record: FlowRecord) -> None:
        """Load a file-backed request body inline so editors can show it."""
        if record.request_body_inline is None and record.request_body_path:
            if self._body_store.exists(record.request_body_path):
                record.request_body_inline = self._body_store.load(record.request_body_path)

    # -- shutdown -------------------------------------------------------------

    def closeEvent(self, event) -> None:
        # Persist open Repeater sessions before tearing anything down.
        self._repeater_tab.save_sessions(self._config.repeater_sessions_path)
        if self._engine.isRunning():
            self._engine.stop()
        self._sender.stop()
        self._repo.close()
        super().closeEvent(event)
