"""Proxy tab: proxy start/stop controls + HTTP History / Intercept sub-tabs.

The proxy settings (listen host/port, start/stop, CA certificate export) live
in a popup menu opened from a "Settings" button pinned to the far right of the
sub-tab bar, so the main area stays uncluttered.
"""
from __future__ import annotations

from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
    QWidgetAction,
)

from bidoytu.ui.flow_table_model import FlowTableModel
from bidoytu.ui.history_view import HistoryView
from bidoytu.ui.intercept_view import InterceptView


class ProxyTab(QWidget):
    """Container widget for everything under the top-level "Proxy" tab."""

    def __init__(self, model: FlowTableModel, parent=None) -> None:
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

        # Sub-tabs.
        self.history = HistoryView(model)
        self.intercept = InterceptView()
        self.sub_tabs = QTabWidget()
        self.sub_tabs.addTab(self.history, "HTTP History")
        self.sub_tabs.addTab(self.intercept, "Intercept")

        # Proxy settings live in a popup opened from a button on the far right
        # of the tab bar (same row as the HTTP History / Intercept tabs).
        self._settings_menu = self._build_settings_menu()
        self.settings_btn = QPushButton("Proxy Settings")
        self.settings_btn.setToolTip("Listen address, start/stop, CA certificate")
        self.settings_btn.setMenu(self._settings_menu)
        self.settings_btn.setMinimumSize(150, 32)
        # Nudge the button up a few pixels so it sits slightly above the tab row.
        self._corner = QWidget()
        corner_layout = QVBoxLayout(self._corner)
        corner_layout.setContentsMargins(0, 0, 4, 6)
        corner_layout.addWidget(self.settings_btn)
        self.sub_tabs.setCornerWidget(self._corner)

        layout = QVBoxLayout(self)
        layout.addWidget(self.sub_tabs)

    # -- settings menu --------------------------------------------------------

    def _build_settings_menu(self) -> QMenu:
        menu = QMenu(self)

        panel = QWidget(menu)
        grid = QGridLayout(panel)
        grid.setContentsMargins(10, 10, 10, 10)

        grid.addWidget(QLabel("Host:"), 0, 0)
        grid.addWidget(self.host_edit, 0, 1)
        grid.addWidget(QLabel("Port:"), 1, 0)
        grid.addWidget(self.port_edit, 1, 1)

        btn_row = QHBoxLayout()
        btn_row.addWidget(self.toggle_btn)
        btn_row.addWidget(self.ca_btn)
        grid.addLayout(btn_row, 2, 0, 1, 2)

        action = QWidgetAction(menu)
        action.setDefaultWidget(panel)
        menu.addAction(action)
        return menu

    @property
    def clear_btn(self) -> QPushButton:
        """The Clear History button now lives in the Intercept control row.

        Exposed here so existing wiring (MainWindow) keeps working unchanged.
        """
        return self.intercept.clear_history_btn

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
