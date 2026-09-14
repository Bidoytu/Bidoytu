"""Startup picker for local Bidoytu workspaces."""
from __future__ import annotations

from pathlib import Path
import zipfile

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QFileDialog, QGroupBox, QHBoxLayout, QInputDialog, QLabel,
    QListWidget, QListWidgetItem, QMessageBox, QPushButton, QVBoxLayout,
)

from bidoytu.workspace import Workspace, WorkspaceManager


class WorkspaceDialog(QDialog):
    """Choose, create, import, or export local workspaces before app startup."""

    def __init__(self, manager: WorkspaceManager, parent=None) -> None:
        super().__init__(parent)
        self._manager = manager
        self.workspace: Workspace | None = None
        self.setWindowTitle("Open session")
        self.setMinimumSize(620, 430)

        title = QLabel("Sessions")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        hint = QLabel(
            "Sessions are stored only on this computer. A new session starts "
            "with no history, logs, requests, or saved tool state."
        )
        hint.setWordWrap(True)
        self._list = QListWidget()
        self._list.itemDoubleClicked.connect(lambda _item: self._open_selected())
        self._list.currentItemChanged.connect(lambda *_: self._update_actions())
        self._new = QPushButton("+  New session")
        self._open = QPushButton("Open session")
        self._delete = QPushButton("Delete selected")
        self._clear_all = QPushButton("Clear all other sessions")
        self._import = QPushButton("Import archive...")
        self._export = QPushButton("Export all sessions...")
        self._cancel = QPushButton("Exit")
        self._new.clicked.connect(self._new_session)
        self._open.clicked.connect(self._open_selected)
        self._delete.clicked.connect(self._delete_selected)
        self._clear_all.clicked.connect(self._clear_sessions)
        self._import.clicked.connect(self._import_sessions)
        self._export.clicked.connect(self._export_sessions)
        self._cancel.clicked.connect(self.reject)

        library_actions = QHBoxLayout()
        library_actions.addWidget(self._new)
        library_actions.addWidget(self._import)
        library_actions.addWidget(self._export)

        library = QVBoxLayout()
        library.addWidget(self._list, 1)
        library.addLayout(library_actions)

        selected_group = QGroupBox("Selected session")
        selected_actions = QVBoxLayout(selected_group)
        self._selection_hint = QLabel("Choose a session to open or manage it.")
        self._selection_hint.setWordWrap(True)
        selected_actions.addWidget(self._selection_hint)
        selected_actions.addWidget(self._open)
        selected_actions.addWidget(self._delete)
        selected_actions.addStretch(1)
        selected_actions.addWidget(self._clear_all)

        content = QHBoxLayout()
        content.addLayout(library, 3)
        content.addWidget(selected_group, 2)

        footer = QHBoxLayout()
        footer.addStretch(1)
        footer.addWidget(self._cancel)
        layout = QVBoxLayout(self)
        layout.addWidget(title)
        layout.addWidget(hint)
        layout.addLayout(content, 1)
        layout.addLayout(footer)
        self._refresh()

    def _refresh(self) -> None:
        self._list.clear()
        for workspace in self._manager.list():
            item = QListWidgetItem(workspace.name)
            item.setData(Qt.UserRole, workspace)
            item.setToolTip(f"Created {workspace.created_at}\nLast used {workspace.updated_at}")
            self._list.addItem(item)
        if self._list.count():
            self._list.setCurrentRow(0)
        self._update_actions()

    def _update_actions(self) -> None:
        item = self._list.currentItem()
        has_selection = item is not None
        workspace = item.data(Qt.UserRole) if item is not None else None
        can_delete = bool(workspace and not workspace.is_protected)
        has_deletable = any(
            not self._list.item(index).data(Qt.UserRole).is_protected
            for index in range(self._list.count())
        )
        self._open.setEnabled(has_selection)
        self._delete.setEnabled(can_delete)
        self._clear_all.setEnabled(has_deletable)
        self._export.setEnabled(self._list.count() > 0)
        if workspace is None:
            self._selection_hint.setText("Choose a session to open or manage it.")
        elif workspace.is_protected:
            self._selection_hint.setText(
                "Previous session is protected so your pre-workspace data is always recoverable."
            )
        else:
            self._selection_hint.setText(
                "Open it to continue, or delete it permanently from this computer."
            )

    def _new_session(self) -> None:
        name, accepted = QInputDialog.getText(self, "New session", "Session name:")
        if not accepted:
            return
        self.workspace = self._manager.create(name)
        self.accept()

    def _open_selected(self) -> None:
        item = self._list.currentItem()
        if item is None:
            return
        self.workspace = item.data(Qt.UserRole)
        self.accept()

    def _delete_selected(self) -> None:
        item = self._list.currentItem()
        if item is None:
            return
        workspace = item.data(Qt.UserRole)
        if workspace.is_protected:
            return
        answer = QMessageBox.question(
            self,
            "Delete session",
            f"Delete '{workspace.name}' and all of its history, requests, "
            "bodies, and saved tool state? This cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return
        self._manager.discard(workspace)
        self._refresh()

    def _clear_sessions(self) -> None:
        count = self._list.count()
        if count == 0:
            return
        answer = QMessageBox.question(
            self,
            "Clear all other sessions",
            f"Delete all deletable sessions (up to {count} total), including their "
            "histories, requests, bodies, and saved tool state? 'Previous session' "
            "will be kept as a protected recovery workspace. This cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return
        self._manager.clear_all()
        self._refresh()

    def _import_sessions(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            self, "Import sessions", "", "Bidoytu sessions (*.bidoytu.zip *.zip)"
        )
        if not filename:
            return
        try:
            imported = self._manager.import_all(Path(filename))
        except (OSError, ValueError, zipfile.BadZipFile) as exc:
            QMessageBox.warning(self, "Import failed", str(exc))
            return
        self._refresh()
        QMessageBox.information(
            self, "Sessions imported", f"Imported {len(imported)} session(s)."
        )

    def _export_sessions(self) -> None:
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export all sessions", "bidoytu-sessions.bidoytu.zip",
            "Bidoytu sessions (*.bidoytu.zip)"
        )
        if not filename:
            return
        path = Path(filename)
        if path.suffix.lower() != ".zip":
            path = path.with_suffix(".bidoytu.zip")
        try:
            self._manager.export_all(path)
        except OSError as exc:
            QMessageBox.warning(self, "Export failed", str(exc))
            return
        QMessageBox.information(self, "Sessions exported", f"Saved to {path.name}.")
