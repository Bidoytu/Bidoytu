"""Application entry point.

Creates the Qt application, builds the main window, and starts the event loop.
The proxy starts automatically once the window is shown; if the listen port is
already in use, the window prompts the user to change the port or retry.
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
from bidoytu.ui.workspace_dialog import WorkspaceDialog
from bidoytu.workspace import WorkspaceManager


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

    # Pick a local workspace before constructing any storage-backed widget.
    # This guarantees that a new session cannot inherit history or tool state.
    base_config = AppConfig()
    manager = WorkspaceManager(base_config.data_dir)
    picker = WorkspaceDialog(manager)
    if not icon.isNull():
        picker.setWindowIcon(icon)
    if picker.exec() != WorkspaceDialog.Accepted or picker.workspace is None:
        return 0

    workspace = picker.workspace
    config = AppConfig(data_dir=manager.path_for(workspace))
    window = MainWindow(config, workspace=workspace, workspace_manager=manager)
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
