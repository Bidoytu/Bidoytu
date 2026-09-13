"""Intruder tab: a container of independent attack sessions.

Each "Send to Intruder" opens a new closable, renamable tab backed by an
:class:`~bidoytu.ui.intruder_session.IntruderSession`. You can switch between
tabs and configure or run each attack independently - the same tabbed model the
Repeater uses for requests.

The container itself is thin: it owns the tab strip, a "+ New" button, and the
persistence glue (save/restore every open session across restarts). All the
attack logic lives in :class:`IntruderSession`.
"""
from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtWidgets import (
    QHBoxLayout,
    QInputDialog,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from bidoytu.net.async_sender import AsyncHttpSender
from bidoytu.storage.models import FlowRecord
from bidoytu.ui.intruder_session import IntruderSession


class IntruderTab(QWidget):
    """Holds multiple :class:`IntruderSession` instances in a tab strip."""

    def __init__(self, sender: AsyncHttpSender, parent=None) -> None:
        super().__init__(parent)
        self._sender = sender

        self._tabs = QTabWidget()
        self._tabs.setTabsClosable(True)
        self._tabs.setMovable(True)
        self._tabs.setDocumentMode(True)
        self._tabs.tabCloseRequested.connect(self._close_tab)
        # Double-clicking a tab renames it.
        self._tabs.tabBarDoubleClicked.connect(self._rename_tab)

        new_btn = QPushButton("+ New")
        new_btn.setToolTip("Open an empty Intruder attack")
        new_btn.setMaximumWidth(70)
        new_btn.clicked.connect(lambda: self._new_session())

        top = QHBoxLayout()
        top.addWidget(new_btn)
        top.addStretch(1)

        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(self._tabs, 1)

    # -- session management ---------------------------------------------------

    def _new_session(self, name: str = "Intruder") -> IntruderSession:
        session = IntruderSession(self._sender, name=name)
        index = self._tabs.addTab(session, name)
        session.title_changed.connect(
            lambda title, s=session: self._on_title_changed(s, title)
        )
        self._tabs.setCurrentIndex(index)
        return session

    def _on_title_changed(self, session: IntruderSession, title: str) -> None:
        idx = self._tabs.indexOf(session)
        if idx >= 0:
            self._tabs.setTabText(idx, title)

    def _close_tab(self, index: int) -> None:
        widget = self._tabs.widget(index)
        if widget is None:
            return
        self._tabs.removeTab(index)
        widget.deleteLater()

    def _rename_tab(self, index: int) -> None:
        if index < 0:
            return
        current = self._tabs.tabText(index)
        new_name, ok = QInputDialog.getText(
            self, "Rename tab", "Tab name:", text=current
        )
        if ok and new_name.strip():
            self._tabs.setTabText(index, new_name.strip())

    def _current_session(self) -> IntruderSession | None:
        widget = self._tabs.currentWidget()
        return widget if isinstance(widget, IntruderSession) else None

    # -- public API (used by MainWindow) --------------------------------------

    def load_from_record(self, record: FlowRecord) -> None:
        """Open a new session tab populated from a captured flow."""
        session = self._new_session()
        session.load_from_record(record)

    # -- persistence ----------------------------------------------------------

    def save_state(self, path: Path) -> None:
        """Write every open session to ``path`` as JSON (list of snapshots)."""
        sessions = []
        for i in range(self._tabs.count()):
            widget = self._tabs.widget(i)
            if isinstance(widget, IntruderSession):
                sessions.append(widget.to_state())
        payload = {"sessions": sessions}
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except OSError:
            pass

    def restore_state(self, path: Path) -> None:
        """Recreate the sessions saved by :meth:`save_state`.

        Accepts both the multi-session format ``{"sessions": [...]}`` and the
        older single-attack format (a bare snapshot dict) for backward
        compatibility.
        """
        try:
            raw = path.read_text(encoding="utf-8")
        except OSError:
            return
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            return

        if isinstance(payload, dict) and "sessions" in payload:
            snapshots = payload.get("sessions", [])
        elif isinstance(payload, dict):
            # Legacy single-attack file.
            snapshots = [payload]
        else:
            snapshots = []

        for snapshot in snapshots:
            if not isinstance(snapshot, dict):
                continue
            name = snapshot.get("name", "Intruder")
            session = self._new_session(name=name)
            session.load_state(snapshot)
