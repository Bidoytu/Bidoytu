"""Application entry point.

Creates the Qt application, builds the main window, and starts the event loop.
The proxy is not started automatically; the user starts it from the toolbar.
"""
from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from bidoytu import __app_name__
from bidoytu.config import AppConfig
from bidoytu.ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName(__app_name__)

    config = AppConfig()
    window = MainWindow(config)
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
