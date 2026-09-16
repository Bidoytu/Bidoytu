"""Proxy tab: proxy controls and HTTP History / Intercept tabs.

The proxy settings (listen host/port, start/stop, CA certificate export) live
in a popup menu opened from a "Settings" button pinned to the far right of the
sub-tab bar, so the main area stays uncluttered.
"""
from __future__ import annotations

from PySide6.QtCore import Signal, QPoint
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (
    QCheckBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QFrame,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from bidoytu.ui.flow_table_model import FlowTableModel
from bidoytu.ui.history_view import HistoryView
from bidoytu.ui.intercept_view import InterceptView


class ProxyTab(QWidget):
    """Container widget for everything under the top-level "Proxy" tab."""

    clear_history_requested = Signal()  # emitted on confirmed Clear History
    browser_integration_requested = Signal()

    def __init__(self, model: FlowTableModel, parent=None,
                 include_scope: list[str] | None = None,
                 exclude_scope: list[str] | None = None,
                 ssl_insecure: bool = False) -> None:
        super().__init__(parent)

        # Listen address inputs.
        self.host_edit = QLineEdit("127.0.0.1")
        self.host_edit.setFixedWidth(140)
        self.host_edit.setToolTip("Interface the proxy listens on")

        # Plain numeric port input (no up/down steppers).
        self.port_edit = QLineEdit("8080")
        self.port_edit.setValidator(QIntValidator(1, 65535, self))
        self.port_edit.setFixedWidth(140)
        self.port_edit.setToolTip("Port the proxy listens on")

        # Proxy engine controls. A single button toggles start/stop.
        self.toggle_btn = QPushButton("Start Proxy")
        self.ca_btn = QPushButton("CA Certificate")
        self.ca_btn.setToolTip(
            "Export the CA certificate to trust so HTTPS interception works"
        )
        self.browser_btn = QPushButton("Open Browser...")
        self.browser_btn.setToolTip("Detect and launch an installed browser through this proxy")
        self.ssl_insecure_check = QCheckBox("Allow invalid upstream TLS certificates")
        self.ssl_insecure_check.setChecked(ssl_insecure)
        self.ssl_insecure_check.setToolTip(
            "Work around broken/expired upstream certificate chains. Use only for authorized testing."
        )

        # Sub-tabs.
        self.history = HistoryView(model)
        self.intercept = InterceptView()
        self.sub_tabs = QTabWidget()
        self.sub_tabs.addTab(self.history, "HTTP History")
        self.sub_tabs.addTab(self.intercept, "Intercept")

        # Clear HTTP History button, placed to the LEFT of Proxy Settings in
        # the tab-bar corner. Clicking it pops up a confirmation dialog so
        # history isn't wiped by accident (see _on_clear_history_clicked).
        self.clear_history_btn = QPushButton("Clear History")
        self.clear_history_btn.setToolTip("Clear all captured HTTP history")
        self.clear_history_btn.setMinimumSize(120, 28)
        self.clear_history_btn.clicked.connect(self._on_clear_history_clicked)

        # Proxy settings live in a popup opened from a button on the far right
        # of the tab bar (same row as the HTTP History / Intercept tabs).
        self._settings_popup = self._build_settings_popup()
        self.settings_btn = QPushButton("Proxy Settings")
        self.settings_btn.setToolTip("Listen address, start/stop, CA certificate")
        self.settings_btn.clicked.connect(self._toggle_settings_popup)
        self.settings_btn.setMinimumSize(150, 30)
        # Corner holds [Clear History] [Proxy Settings]. A slightly larger top
        # margin lowers the whole cluster so it no longer crowds the top edge.
        self._corner = QWidget()
        corner_layout = QHBoxLayout(self._corner)
        corner_layout.setContentsMargins(4, 2, 4, 4)
        corner_layout.setSpacing(6)
        corner_layout.addWidget(self.clear_history_btn)
        corner_layout.addWidget(self.settings_btn)
        self.sub_tabs.setCornerWidget(self._corner)

        layout = QVBoxLayout(self)
        layout.addWidget(self.sub_tabs)

    # -- settings menu --------------------------------------------------------

    def _build_settings_popup(self) -> QFrame:
        panel = QFrame(self)
        panel.setFrameShape(QFrame.StyledPanel)
        panel.setFrameShadow(QFrame.Raised)
        panel.setStyleSheet(
            "QFrame { background: palette(base); border: 1px solid #9aa4b2; "
            "border-radius: 6px; }"
        )
        panel.setMinimumWidth(370)
        grid = QGridLayout(panel)
        grid.setContentsMargins(10, 10, 10, 10)

        grid.addWidget(QLabel("Host:"), 0, 0)
        grid.addWidget(self.host_edit, 0, 1)
        grid.addWidget(QLabel("Port:"), 1, 0)
        grid.addWidget(self.port_edit, 1, 1)
        grid.addWidget(self.ssl_insecure_check, 2, 0, 1, 2)

        btn_row = QHBoxLayout()
        btn_row.addWidget(self.toggle_btn)
        btn_row.addWidget(self.ca_btn)
        btn_row.addWidget(self.browser_btn)
        grid.addLayout(btn_row, 3, 0, 1, 2)

        self.browser_btn.clicked.connect(self.browser_integration_requested.emit)
        panel.hide()
        return panel

    def _toggle_settings_popup(self) -> None:
        """Show the settings panel as an in-window child widget."""
        popup = self._settings_popup
        if popup.isVisible():
            popup.hide()
            return
        popup.adjustSize()
        origin = self.settings_btn.mapTo(self, QPoint(0, self.settings_btn.height()))
        x = max(0, min(origin.x(), self.width() - popup.width()))
        y = max(0, min(origin.y(), self.height() - popup.height()))
        popup.move(x, y)
        popup.raise_()
        popup.show()

    @property
    def clear_btn(self) -> QPushButton:
        """The Clear History button now lives in the Intercept control row.

        Exposed here so existing wiring (MainWindow) keeps working unchanged.
        """
        return self.intercept.clear_history_btn

    # -- clear history (two-click confirm) ------------------------------------

    def _on_clear_history_clicked(self) -> None:
        """Ask for confirmation in a popup before wiping the capture history.

        This guards against wiping the whole capture history on a stray click.
        """
        answer = QMessageBox.question(
            self,
            "Clear HTTP history",
            "Clear all captured HTTP history? This cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer == QMessageBox.Yes:
            self.clear_history_requested.emit()

    # -- listen address -------------------------------------------------------

    def listen_host(self) -> str:
        host = self.host_edit.text().strip()
        return host or "127.0.0.1"

    def listen_port(self) -> int:
        text = self.port_edit.text().strip()
        try:
            port = int(text)
        except ValueError:
            return 8080
        return port if 1 <= port <= 65535 else 8080

    def set_port(self, port: int) -> None:
        self.port_edit.setText(str(port))

    def set_status(self, text: str) -> None:
        """Surface a detailed transient message (e.g. "Starting...", errors)
        on the settings button tooltip."""
        self.settings_btn.setToolTip(text)

    def set_running(self, running: bool) -> None:
        # Single toggle button reflects the current state.
        self.toggle_btn.setText("Stop Proxy" if running else "Start Proxy")
        self.toggle_btn.setEnabled(True)
        # Lock the address inputs while the proxy is running.
        self.host_edit.setEnabled(not running)
        self.port_edit.setEnabled(not running)
