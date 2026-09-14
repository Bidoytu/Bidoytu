"""Proxy tab: Target scope, proxy controls, and HTTP History / Intercept tabs.

The proxy settings (listen host/port, start/stop, CA certificate export) live
in a popup menu opened from a "Settings" button pinned to the far right of the
sub-tab bar, so the main area stays uncluttered.
"""
from __future__ import annotations

import re

from PySide6.QtCore import QTimer, QSize, Signal
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (
    QAbstractItemView,
    QGroupBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMenu,
    QPushButton,
    QStyle,
    QTabWidget,
    QVBoxLayout,
    QWidget,
    QWidgetAction,
)

from bidoytu.ui.flow_table_model import FlowTableModel
from bidoytu.ui.history_view import HistoryView
from bidoytu.ui.intercept_view import InterceptView


class _ScopeList(QWidget):
    """Editable list of host patterns used by the Target scope panel."""

    changed = Signal()

    def __init__(self, title: str, placeholder: str, parent=None) -> None:
        super().__init__(parent)
        self._title = QLabel(title)
        self._title.setStyleSheet("font-weight: 600;")
        self.entry_edit = QLineEdit()
        self.entry_edit.setPlaceholderText(placeholder)
        self.entry_edit.returnPressed.connect(self._add_entries)

        self.add_btn = QPushButton("Add")
        self.add_btn.clicked.connect(self._add_entries)
        add_row = QHBoxLayout()
        add_row.setContentsMargins(0, 0, 0, 0)
        add_row.addWidget(self.entry_edit, 1)
        add_row.addWidget(self.add_btn)

        self.entries = QListWidget()
        self.entries.setSelectionMode(QAbstractItemView.SingleSelection)
        self.entries.setMinimumHeight(72)
        self.entries.setToolTip(
            "A domain also matches its subdomains; for example, example.com "
            "matches api.example.com."
        )

        self.remove_btn = QPushButton("Remove selected")
        self.remove_btn.clicked.connect(self._remove_selected)
        self.remove_btn.setEnabled(False)
        self.entries.itemSelectionChanged.connect(
            lambda: self.remove_btn.setEnabled(bool(self.entries.selectedItems()))
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        layout.addWidget(self._title)
        layout.addLayout(add_row)
        layout.addWidget(self.entries)
        layout.addWidget(self.remove_btn)

    def _add_entries(self) -> None:
        raw = self.entry_edit.text().strip()
        if not raw:
            return
        existing = {
            self.entries.item(i).text().casefold()
            for i in range(self.entries.count())
        }
        for value in re.split(r"[,;\s]+", raw):
            value = value.strip().strip(".")
            if value and value.casefold() not in existing:
                self.entries.addItem(value)
                existing.add(value.casefold())
        self.entry_edit.clear()
        self.changed.emit()

    def _remove_selected(self) -> None:
        for item in self.entries.selectedItems():
            self.entries.takeItem(self.entries.row(item))
        self.changed.emit()

    def values(self) -> list[str]:
        return [self.entries.item(i).text() for i in range(self.entries.count())]

    def set_values(self, values: list[str]) -> None:
        self.entries.clear()
        for value in values:
            if str(value).strip():
                self.entries.addItem(str(value).strip())


class ProxyTab(QWidget):
    """Container widget for everything under the top-level "Proxy" tab."""

    scope_changed = Signal(list, list)
    clear_history_requested = Signal()  # emitted on confirmed Clear History

    def __init__(self, model: FlowTableModel, parent=None,
                 include_scope: list[str] | None = None,
                 exclude_scope: list[str] | None = None) -> None:
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

        # Burp-style Target panel.  It stays visible beside the proxy views so
        # the active scope is always easy to inspect and edit.
        self.target_panel = self._build_target_panel()
        self._target_panel_width = 310
        self._target_collapsed = False
        self.target_panel.setFixedWidth(self._target_panel_width)

        # Clear HTTP History button, placed to the LEFT of Proxy Settings in
        # the tab-bar corner. Requires a second click to confirm so history
        # isn't wiped by accident (see _on_clear_history_clicked).
        self.clear_history_btn = QPushButton("Clear History")
        self.clear_history_btn.setToolTip("Clear all captured HTTP history")
        self.clear_history_btn.setMinimumSize(120, 28)
        self._clear_armed = False
        self.clear_history_btn.clicked.connect(self._on_clear_history_clicked)

        # Proxy settings live in a popup opened from a button on the far right
        # of the tab bar (same row as the HTTP History / Intercept tabs).
        self._settings_menu = self._build_settings_menu()
        self.settings_btn = QPushButton("Proxy Settings")
        self.settings_btn.setToolTip("Listen address, start/stop, CA certificate")
        self.settings_btn.setMenu(self._settings_menu)
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
        content = QHBoxLayout()
        content.setSpacing(10)
        content.addWidget(self.target_panel, 0)
        content.addWidget(self.sub_tabs, 1)
        layout.addLayout(content)

        self.set_scope(include_scope or [], exclude_scope or [])

    def _build_target_panel(self) -> QWidget:
        panel = QWidget()
        outer = QVBoxLayout(panel)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(8)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        self._target_title = QLabel("Target")
        self._target_title.setStyleSheet("font-size: 16px; font-weight: 700;")
        header.addWidget(self._target_title)
        header.addStretch(1)

        self.target_toggle_btn = QPushButton()
        self.target_toggle_btn.setFixedSize(30, 28)
        self.target_toggle_btn.setIconSize(QSize(18, 18))
        self._set_target_toggle_icon(QStyle.SP_ArrowLeft)
        self.target_toggle_btn.setToolTip("Minimize Target panel")
        self.target_toggle_btn.setAccessibleName("Minimize Target panel")
        self.target_toggle_btn.clicked.connect(self._toggle_target_panel)
        header.addWidget(self.target_toggle_btn)
        outer.addLayout(header)

        self.scope_group = QGroupBox("Scope")
        scope_layout = QVBoxLayout(self.scope_group)
        scope_layout.setContentsMargins(10, 12, 10, 10)
        scope_layout.setSpacing(10)

        description = QLabel(
            "Define the domains and subdomains that belong to this target. "
            "Exclusions take precedence over inclusions."
        )
        description.setWordWrap(True)
        description.setStyleSheet("color: #8f98a8;")
        scope_layout.addWidget(description)

        self.include_scope_list = _ScopeList(
            "Include in scope", "example.com or *.example.com", self.scope_group
        )
        self.exclude_scope_list = _ScopeList(
            "Exclude from scope", "cdn.example.com", self.scope_group
        )
        self.include_scope_list.changed.connect(self._emit_scope_changed)
        self.exclude_scope_list.changed.connect(self._emit_scope_changed)
        scope_layout.addWidget(self.include_scope_list)
        scope_layout.addWidget(self.exclude_scope_list)
        outer.addWidget(self.scope_group)
        outer.addStretch(1)
        return panel

    def _toggle_target_panel(self) -> None:
        """Collapse the Target panel to an arrow, or restore its full width."""
        if not self._target_collapsed:
            self._target_collapsed = True
            self._target_title.hide()
            self.scope_group.hide()
            self.target_panel.setFixedWidth(36)
            self._set_target_toggle_icon(QStyle.SP_ArrowRight)
            self.target_toggle_btn.setToolTip("Expand Target panel")
            self.target_toggle_btn.setAccessibleName("Expand Target panel")
        else:
            self._target_collapsed = False
            self._target_title.show()
            self.scope_group.show()
            self.target_panel.setFixedWidth(self._target_panel_width)
            self._set_target_toggle_icon(QStyle.SP_ArrowLeft)
            self.target_toggle_btn.setToolTip("Minimize Target panel")
            self.target_toggle_btn.setAccessibleName("Minimize Target panel")

    def _set_target_toggle_icon(self, standard_icon: QStyle.StandardPixmap) -> None:
        """Use Qt's native arrow icon so the control does not depend on fonts."""
        self.target_toggle_btn.setIcon(
            self.target_toggle_btn.style().standardIcon(standard_icon)
        )

    def _emit_scope_changed(self) -> None:
        self.scope_changed.emit(self.include_scope(), self.exclude_scope())

    def include_scope(self) -> list[str]:
        return self.include_scope_list.values()

    def exclude_scope(self) -> list[str]:
        return self.exclude_scope_list.values()

    def set_scope(self, include_scope: list[str], exclude_scope: list[str]) -> None:
        self.include_scope_list.set_values(include_scope)
        self.exclude_scope_list.set_values(exclude_scope)

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

    # -- clear history (two-click confirm) ------------------------------------

    def _on_clear_history_clicked(self) -> None:
        """First click arms the button; a second click within 3s confirms.

        This guards against wiping the whole capture history on a stray click.
        """
        if not self._clear_armed:
            self._arm_clear()
            return
        self._disarm_clear()
        self.clear_history_requested.emit()

    def _arm_clear(self) -> None:
        self._clear_armed = True
        self.clear_history_btn.setText("Confirm Clear?")
        self.clear_history_btn.setToolTip("Click again to clear all HTTP history")
        # Auto-disarm if the user doesn't confirm shortly.
        QTimer.singleShot(3000, self._disarm_clear)

    def _disarm_clear(self) -> None:
        if not self._clear_armed:
            return
        self._clear_armed = False
        self.clear_history_btn.setText("Clear History")
        self.clear_history_btn.setToolTip("Clear all captured HTTP history")

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
