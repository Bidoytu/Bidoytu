"""Application entry point.

Creates the Qt application, builds the main window, and starts the event loop.
The proxy is not started automatically; the user starts it from the toolbar.
"""
from __future__ import annotations

import os
import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from bidoytu import __app_name__
from bidoytu.config import AppConfig
from bidoytu.resources import logo_path
from bidoytu.ui.main_window import MainWindow
from bidoytu.ui.theme import apply_theme, load_theme


def _set_windows_app_id() -> None:
    """Give Windows an explicit AppUserModelID so the taskbar uses our icon.

    Without this, a Python-hosted app is grouped under python.exe and shows the
    interpreter's icon on the taskbar instead of the window icon.
    """
    if os.name != "nt":
        return
    try:
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            f"{__app_name__}.{__app_name__}"
        )
    except Exception:
        # Non-fatal: the app still runs, just without the custom taskbar group.
        pass


def main() -> int:
    _set_windows_app_id()

    app = QApplication(sys.argv)
    app.setApplicationName(__app_name__)
    app.setOrganizationName(__app_name__)

    # Application/taskbar icon.
    icon = QIcon(str(logo_path()))
    if not icon.isNull():
        app.setWindowIcon(icon)

    # Apply the persisted theme (defaults to dark) before building widgets so
    # highlighters pick up matching colors from the start.
    apply_theme(app, load_theme())

    config = AppConfig()
    window = MainWindow(config)
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
