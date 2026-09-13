"""Proxy tab: proxy start/stop controls + HTTP History / Intercept sub-tabs."""
from __future__ import annotations

from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
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

    def __init__(self, model: FlowTableModel, parent=None) -> None:
        super().__init__(parent)

        # Listen address inputs.
        self.host_edit = QLineEdit("127.0.0.1")
        self.host_edit.setFixedWidth(120)
        self.host_edit.setToolTip("Interface the proxy listens on")

        # Plain numeric port input (no up/down steppers).
        self.port_edit = QLineEdit("8080")
        self.port_edit.setValidator(QIntValidator(1, 65535, self))
        self.port_edit.setFixedWidth(80)
        self.port_edit.setToolTip("Port the proxy listens on")

        # Proxy engine controls. A single button toggles start/stop.
        self.toggle_btn = QPushButton("Start Proxy")
        self.clear_btn = QPushButton("Clear History")
        self.ca_btn = QPushButton("CA Certificate")
        self.ca_btn.setToolTip(
            "Export the CA certificate to trust so HTTPS interception works"
        )
        self.status_label = QLabel("Proxy stopped")

        controls = QHBoxLayout()
        controls.addWidget(QLabel("Host:"))
        controls.addWidget(self.host_edit)
        controls.addWidget(QLabel("Port:"))
        controls.addWidget(self.port_edit)
        controls.addSpacing(12)
        controls.addWidget(self.toggle_btn)
        controls.addWidget(self.clear_btn)
        controls.addWidget(self.ca_btn)
        controls.addSpacing(16)
        controls.addWidget(self.status_label)
        controls.addStretch(1)

        # Sub-tabs.
        self.history = HistoryView(model)
        self.intercept = InterceptView()
        self.sub_tabs = QTabWidget()
        self.sub_tabs.addTab(self.history, "HTTP History")
        self.sub_tabs.addTab(self.intercept, "Intercept")

        layout = QVBoxLayout(self)
        layout.addLayout(controls)
        layout.addWidget(self.sub_tabs)

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
        self.status_label.setText(text)

    def set_running(self, running: bool) -> None:
        # Single toggle button reflects the current state.
        self.toggle_btn.setText("Stop Proxy" if running else "Start Proxy")
        self.toggle_btn.setEnabled(True)
        # Lock the address inputs while the proxy is running.
        self.host_edit.setEnabled(not running)
        self.port_edit.setEnabled(not running)
