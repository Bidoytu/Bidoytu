"""Browser Integration dialog for launching browsers through Bidoytu."""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QFileInfo, QSize, Qt, Signal
from PySide6.QtWidgets import (
    QDialog, QDialogButtonBox, QFileIconProvider, QLabel, QListWidget,
    QListWidgetItem, QMessageBox, QVBoxLayout,
)

from bidoytu.browser_integration import BrowserInfo, discover_browsers, launch_browser


class BrowserIntegrationDialog(QDialog):
    browser_launched = Signal(object)

    def __init__(self, host: str, port: int, ca_cert: Path, profile_root: Path, parent=None) -> None:
        super().__init__(parent)
        self._host, self._port = host, port
        self._ca_cert, self._profile_root = Path(ca_cert), Path(profile_root)
        self._browsers: list[BrowserInfo] = discover_browsers()
        self.setWindowTitle("Browser Integration")
        self.resize(440, 330)

        intro = QLabel(
            "Select a browser to launch through Bidoytu.\n"
            "Proxy and CA configuration are applied automatically."
        )
        intro.setWordWrap(True)
        intro.setStyleSheet("color: #8f98a8; padding: 4px 0 8px 0;")
        self._list = QListWidget()
        self._list.setIconSize(QSize(40, 40))
        self._list.setSpacing(4)
        self._list.setUniformItemSizes(True)
        for browser in self._browsers:
            icon = QFileIconProvider().icon(QFileInfo(str(browser.executable)))
            item = QListWidgetItem(icon, browser.name)
            item.setSizeHint(QSize(0, 54))
            item.setData(256, browser)
            self._list.addItem(item)
        self._list.itemDoubleClicked.connect(lambda _: self._launch_selected())
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        self._launch_btn = buttons.addButton("Launch selected", QDialogButtonBox.AcceptRole)
        self._launch_btn.clicked.connect(self._launch_selected)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(intro)
        layout.addWidget(self._list)
        layout.addWidget(buttons)
        self._launch_btn.setEnabled(bool(self._browsers))
        if not self._browsers:
            empty = QListWidgetItem("No supported browser found")
            empty.setFlags(empty.flags() & ~Qt.ItemFlag.ItemIsEnabled)
            self._list.addItem(empty)

    def _launch_selected(self) -> None:
        item = self._list.currentItem()
        browser = item.data(256) if item else None
        if not isinstance(browser, BrowserInfo):
            return
        profile = self._profile_root / browser.name.lower().replace(" ", "-")
        try:
            process, _trust_method = launch_browser(
                browser, self._host, self._port, profile,
                self._ca_cert, self._ca_cert.with_suffix(".cer"),
            )
        except OSError as exc:
            QMessageBox.critical(
                self, "Browser launch blocked",
                "CA installation failed.\n\n"
                f"{exc}\n\n"
                f"PEM path: {self._ca_cert}\n"
                f"Windows certificate path: {self._ca_cert.with_suffix('.cer')}\n\n"
                "Start the proxy and retry so its CA certificate is generated.",
            )
            return
        self._launch_btn.setText(f"{browser.name} launched")
        self.browser_launched.emit(process)
