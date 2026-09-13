"""Repeater tab: a container of independent request/response sessions.

Each "Send to Repeater" opens a new closable, renamable tab backed by a
:class:`~bidoytu.ui.repeater_session.RepeaterSession`. Tabs are shown in a
custom :class:`~bidoytu.ui.wrapping_tab_bar.WrappingTabBar` that wraps onto new
rows instead of scrolling, and can be organized into named, colored groups.

Grouping model:
    * A group owns an ordered list of member sessions.
    * The bar renders a colored group header (with an expand/collapse arrow)
      followed by that group's member tabs. Collapsing hides the members.
    * Ungrouped sessions render after all groups.

Tabs can be duplicated (Ctrl+R or the context menu); copies are named
``base (1)``, ``base (2)``, ... Sessions and groups persist to JSON.
"""
from __future__ import annotations

import base64
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from PySide6.QtWidgets import (
    QHBoxLayout,
    QInputDialog,
    QMenu,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from bidoytu.net.async_sender import AsyncHttpSender
from bidoytu.storage.models import FlowRecord
from bidoytu.ui.group_dialog import PALETTE, GroupDialog
from bidoytu.ui.repeater_session import RepeaterSession, SessionState
from bidoytu.ui.wrapping_tab_bar import WrappingTabBar


@dataclass(slots=True)
class Group:
    """A named, colored, collapsible collection of member sessions."""

    name: str
    color: str
    members: list = field(default_factory=list)  # list[RepeaterSession]
    collapsed: bool = False


class RepeaterTab(QWidget):
    """Holds multiple :class:`RepeaterSession` instances with a wrapping bar."""

    def __init__(self, sender: AsyncHttpSender, parent=None) -> None:
        super().__init__(parent)
        self._sender = sender

        # Ordered ungrouped sessions, groups (insertion order), and titles.
        self._ungrouped: list[RepeaterSession] = []
        self._groups: dict[str, Group] = {}
        self._membership: dict[RepeaterSession, str] = {}
        self._base_titles: dict[RepeaterSession, str] = {}
        self._current: RepeaterSession | None = None

        self._bar = WrappingTabBar()
        self._bar.tab_selected.connect(self._on_tab_selected)
        self._bar.tab_close_requested.connect(self._close_session)
        self._bar.tab_rename_requested.connect(self._rename_session)
        self._bar.tab_context_menu.connect(self._show_tab_menu)
        self._bar.group_context_menu.connect(self._show_group_menu)
        self._bar.group_toggled.connect(self._toggle_group)

        self._stack = QStackedWidget()

        new_btn = QPushButton("+ New")
        new_btn.setToolTip("Open an empty request")
        new_btn.setMaximumWidth(70)
        new_btn.clicked.connect(lambda: self._new_session())

        clear_btn = QPushButton("Clear all")
        clear_btn.setToolTip("Close every request tab and remove all groups")
        clear_btn.setMaximumWidth(80)
        clear_btn.clicked.connect(self._clear_all)

        top = QHBoxLayout()
        top.addWidget(new_btn)
        top.addWidget(clear_btn)
        top.addWidget(self._bar, 1)

        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(self._stack, 1)

    # -- session management ---------------------------------------------------

    def _new_session(self, name: str = "Request") -> RepeaterSession:
        session = RepeaterSession(self._sender, name=name)
        self._base_titles[session] = name
        self._ungrouped.append(session)
        self._stack.addWidget(session)
        session.title_changed.connect(
            lambda title, s=session: self._on_title_changed(s, title)
        )
        session.duplicate_requested.connect(
            lambda s=session: self._duplicate_session(s)
        )
        self._current = session
        self._rebuild_bar()
        self._stack.setCurrentWidget(session)
        return session

    def _on_title_changed(self, session: RepeaterSession, title: str) -> None:
        self._base_titles[session] = title
        self._rebuild_bar()

    def _on_tab_selected(self, session: RepeaterSession) -> None:
        self._current = session
        self._stack.setCurrentWidget(session)
        self._update_group_send_menu(session)

    def _update_group_send_menu(self, session: RepeaterSession) -> None:
        """Show group-send options on a session's Send dropdown iff it's grouped."""
        group_name = self._membership.get(session)
        if not group_name or group_name not in self._groups:
            session.set_group_send_actions(None)
            return
        actions = [
            ("Send group in sequence (single connection)",
             lambda g=group_name: self._send_group(g, mode="seq_single")),
            ("Send group in sequence (separate connections)",
             lambda g=group_name: self._send_group(g, mode="seq_separate")),
            ("Send group in parallel",
             lambda g=group_name: self._send_group(g, mode="parallel")),
        ]
        session.set_group_send_actions(actions)

    def _send_group(self, group_name: str, mode: str) -> None:
        group = self._groups.get(group_name)
        if group is None or not group.members:
            return
        members = list(group.members)
        if mode == "parallel":
            for session in members:
                session.send_now()
        elif mode in ("seq_single", "seq_separate"):
            fresh = (mode == "seq_separate")
            self._send_sequence(members, 0, fresh)

    def _send_sequence(self, members: list, index: int, fresh: bool) -> None:
        """Send group members one at a time, each after the previous finishes."""
        if index >= len(members):
            return
        session = members[index]

        def _after(_result, nxt=index + 1):
            # Advance to the next member once this one reports a result.
            session.result_delivered.disconnect(_after)
            self._send_sequence(members, nxt, fresh)

        session.result_delivered.connect(_after)
        session.send_now(fresh_client=fresh)

    def _close_session(self, session: RepeaterSession) -> None:
        # Detach from grouping / ordering bookkeeping.
        group_name = self._membership.pop(session, None)
        if group_name and group_name in self._groups:
            members = self._groups[group_name].members
            if session in members:
                members.remove(session)
        if session in self._ungrouped:
            self._ungrouped.remove(session)
        self._base_titles.pop(session, None)

        self._stack.removeWidget(session)
        session.deleteLater()
        if self._current is session:
            self._current = (
                self._stack.currentWidget()
                if self._stack.count() else None
            )
        self._rebuild_bar()

    def _rename_session(self, session: RepeaterSession) -> None:
        current = self._base_titles.get(session, "Request")
        new_name, ok = QInputDialog.getText(
            self, "Rename tab", "Tab name:", text=current
        )
        if ok and new_name.strip():
            self._base_titles[session] = new_name.strip()
            self._rebuild_bar()

    def _duplicate_session(self, session: RepeaterSession) -> None:
        """Clone a session's request into a new tab, named ``base (n)``."""
        state = session.to_state()
        base = self._base_titles.get(session, state.name)
        state.name = self._next_copy_name(base)
        clone = self._new_session(name=state.name)
        clone.load_state(state)

    def _next_copy_name(self, base: str) -> str:
        """Return ``base (n)`` with the smallest unused positive integer n."""
        # Strip an existing " (k)" suffix so copies of copies stay tidy.
        stem = re.sub(r"\s*\(\d+\)\s*$", "", base).strip() or base
        used = set()
        pattern = re.compile(r"^" + re.escape(stem) + r"\s*\((\d+)\)$")
        for title in self._base_titles.values():
            m = pattern.match(title.strip())
            if m:
                used.add(int(m.group(1)))
        n = 1
        while n in used:
            n += 1
        return f"{stem} ({n})"

    # -- grouping -------------------------------------------------------------

    def _all_sessions_in_order(self) -> list[RepeaterSession]:
        ordered: list[RepeaterSession] = []
        for group in self._groups.values():
            ordered.extend(group.members)
        ordered.extend(self._ungrouped)
        return ordered

    def _show_tab_menu(self, session: RepeaterSession, global_pos) -> None:
        menu = QMenu(self)
        add_action = menu.addAction("Add to group...")
        remove_action = None
        if session in self._membership:
            remove_action = menu.addAction("Remove from group")
        menu.addSeparator()
        dup_action = menu.addAction("Duplicate tab")
        rename_action = menu.addAction("Rename...")
        close_action = menu.addAction("Close tab")

        chosen = menu.exec(global_pos)
        if chosen is None:
            return
        if chosen == add_action:
            self._open_group_dialog(session)
        elif chosen == remove_action:
            self._remove_from_group(session)
        elif chosen == dup_action:
            self._duplicate_session(session)
        elif chosen == rename_action:
            self._rename_session(session)
        elif chosen == close_action:
            self._close_session(session)

    def _show_group_menu(self, group_name: str, global_pos) -> None:
        if group_name not in self._groups:
            return
        menu = QMenu(self)
        toggle_action = menu.addAction(
            "Expand" if self._groups[group_name].collapsed else "Collapse"
        )
        rename_action = menu.addAction("Rename group...")
        ungroup_action = menu.addAction("Ungroup (keep tabs)")
        menu.addSeparator()
        delete_action = menu.addAction("Delete group (and its tabs)")

        chosen = menu.exec(global_pos)
        if chosen is None:
            return
        if chosen == toggle_action:
            self._toggle_group(group_name)
        elif chosen == rename_action:
            self._rename_group(group_name)
        elif chosen == ungroup_action:
            self._ungroup(group_name)
        elif chosen == delete_action:
            self._delete_group(group_name)

    def _open_group_dialog(self, clicked: RepeaterSession) -> None:
        ordered = self._all_sessions_in_order()
        titles = [self._base_titles.get(s, "Request") for s in ordered]
        existing_group = self._membership.get(clicked, "")
        default_color = (
            self._groups[existing_group].color
            if existing_group in self._groups else PALETTE[len(self._groups) % len(PALETTE)]
        )
        preselected = [ordered.index(clicked)]
        if existing_group in self._groups:
            preselected = [ordered.index(s)
                           for s in self._groups[existing_group].members]

        dialog = GroupDialog(
            titles, preselected=preselected, name=existing_group,
            color=default_color, parent=self,
        )
        if not dialog.exec():
            return
        name = dialog.group_name()
        if not name:
            return
        color = dialog.color()
        selected = {ordered[i] for i in dialog.selected_indices()
                    if 0 <= i < len(ordered)}

        group = self._groups.get(name)
        if group is None:
            group = Group(name=name, color=color)
            self._groups[name] = group
        else:
            group.color = color

        # Assign selected sessions to this group; pull them from wherever they
        # were (ungrouped list or another group).
        for session in selected:
            self._detach_from_current_group(session)
            self._membership[session] = name
            if session not in group.members:
                group.members.append(session)

        # Sessions previously in this group but now deselected become ungrouped.
        for session in list(group.members):
            if session not in selected:
                group.members.remove(session)
                self._membership.pop(session, None)
                if session not in self._ungrouped:
                    self._ungrouped.append(session)

        self._rebuild_bar()

    def _detach_from_current_group(self, session: RepeaterSession) -> None:
        if session in self._ungrouped:
            self._ungrouped.remove(session)
        prev = self._membership.get(session)
        if prev and prev in self._groups and session in self._groups[prev].members:
            self._groups[prev].members.remove(session)

    def _remove_from_group(self, session: RepeaterSession) -> None:
        self._detach_from_current_group(session)
        self._membership.pop(session, None)
        if session not in self._ungrouped:
            self._ungrouped.append(session)
        self._rebuild_bar()

    def _toggle_group(self, group_name: str) -> None:
        group = self._groups.get(group_name)
        if group is None:
            return
        group.collapsed = not group.collapsed
        # If the current tab was just hidden, switch to a visible one.
        if group.collapsed and self._current in group.members:
            visible = self._first_visible_session()
            if visible is not None:
                self._current = visible
                self._stack.setCurrentWidget(visible)
        self._rebuild_bar()

    def _rename_group(self, group_name: str) -> None:
        new_name, ok = QInputDialog.getText(
            self, "Rename group", "Group name:", text=group_name
        )
        new_name = new_name.strip()
        if not ok or not new_name or new_name == group_name:
            return
        if new_name in self._groups:
            return  # avoid clobbering an existing group
        group = self._groups.pop(group_name)
        group.name = new_name
        # Rebuild dict preserving order.
        self._groups[new_name] = group
        for session in group.members:
            self._membership[session] = new_name
        self._rebuild_bar()

    def _ungroup(self, group_name: str) -> None:
        group = self._groups.pop(group_name, None)
        if group is None:
            return
        for session in group.members:
            self._membership.pop(session, None)
            if session not in self._ungrouped:
                self._ungrouped.append(session)
        self._rebuild_bar()

    def _delete_group(self, group_name: str) -> None:
        """Delete a group along with all request tabs it contains."""
        group = self._groups.get(group_name)
        if group is None:
            return
        count = len(group.members)
        confirm = QMessageBox.question(
            self,
            "Delete group",
            f"Delete group '{group_name}' and its {count} "
            f"tab{'s' if count != 1 else ''}? This cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return
        # Close every member session, then drop the group.
        for session in list(group.members):
            self._membership.pop(session, None)
            self._stack.removeWidget(session)
            session.deleteLater()
            if self._current is session:
                self._current = None
        self._groups.pop(group_name, None)
        if self._current is None:
            self._current = (
                self._stack.currentWidget() if self._stack.count() else None
            )
        self._rebuild_bar()

    def _clear_all(self) -> None:
        """Close every request tab and remove all groups."""
        total = self._stack.count()
        if total == 0:
            return
        confirm = QMessageBox.question(
            self,
            "Clear all requests",
            f"Close all {total} request tab{'s' if total != 1 else ''} "
            f"and remove every group? This cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return
        for session in self._all_sessions_in_order():
            self._stack.removeWidget(session)
            session.deleteLater()
        self._ungrouped.clear()
        self._groups.clear()
        self._membership.clear()
        self._base_titles.clear()
        self._current = None
        self._rebuild_bar()

    def _first_visible_session(self) -> RepeaterSession | None:
        for group in self._groups.values():
            if not group.collapsed and group.members:
                return group.members[0]
        if self._ungrouped:
            return self._ungrouped[0]
        return None

    # -- bar rendering --------------------------------------------------------

    def _rebuild_bar(self) -> None:
        chip_titles: dict[object, str] = {}
        chip_styles: dict[object, str] = {}
        for session in self._all_sessions_in_order():
            chip_titles[session] = self._base_titles.get(session, "Request")
            group_name = self._membership.get(session)
            if group_name and group_name in self._groups:
                color = self._groups[group_name].color
                chip_styles[session] = f"border-left: 4px solid {color};"
            else:
                chip_styles[session] = ""

        groups = [(g.name, g.color) for g in self._groups.values()]
        group_members = {g.name: list(g.members) for g in self._groups.values()}
        collapsed = {g.name for g in self._groups.values() if g.collapsed}

        self._bar.rebuild(
            order=list(self._ungrouped),
            chip_titles=chip_titles,
            chip_styles=chip_styles,
            groups=groups,
            group_members=group_members,
            collapsed=collapsed,
        )
        if self._current is not None:
            self._bar.set_current(self._current)
            # Keep the current tab's Send-dropdown in sync with its group state.
            self._update_group_send_menu(self._current)

    # -- public API (used by MainWindow) --------------------------------------

    def load_from_record(self, record: FlowRecord) -> None:
        """Open a new session tab populated from a captured flow."""
        session = self._new_session()
        session.load_from_record(record)

    # -- persistence ----------------------------------------------------------

    def save_sessions(self, path: Path) -> None:
        """Write all open sessions and their groups to ``path`` as JSON."""
        sessions = []
        for session in self._all_sessions_in_order():
            st = session.to_state()
            sessions.append({
                "name": self._base_titles.get(session, st.name),
                "scheme": st.scheme,
                "host": st.host,
                "port": st.port,
                "request_b64": base64.b64encode(
                    st.request_text.encode("utf-8")
                ).decode("ascii"),
                "follow_redirects": st.follow_redirects,
                "verify_tls": st.verify_tls,
                "group": self._membership.get(session, ""),
            })
        payload = {
            "sessions": sessions,
            "groups": [{"name": g.name, "color": g.color, "collapsed": g.collapsed}
                       for g in self._groups.values()],
        }
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except OSError:
            pass

    def restore_sessions(self, path: Path) -> None:
        """Recreate sessions and groups saved by :meth:`save_sessions`."""
        try:
            raw = path.read_text(encoding="utf-8")
        except OSError:
            return
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            return

        if isinstance(payload, list):  # legacy bare-list format
            sessions = payload
            groups = []
        else:
            sessions = payload.get("sessions", [])
            groups = payload.get("groups", [])

        for g in groups:
            name = g.get("name", "")
            if name and name not in self._groups:
                self._groups[name] = Group(
                    name=name, color=g.get("color", "#95a5a6"),
                    collapsed=bool(g.get("collapsed", False)),
                )

        for item in sessions:
            try:
                request_text = base64.b64decode(
                    item.get("request_b64", "")
                ).decode("utf-8", errors="replace")
            except Exception:
                request_text = ""
            state = SessionState(
                name=item.get("name", "Request"),
                scheme=item.get("scheme", "http"),
                host=item.get("host", ""),
                port=int(item.get("port", 80)),
                request_text=request_text,
                follow_redirects=bool(item.get("follow_redirects", False)),
                verify_tls=bool(item.get("verify_tls", False)),
            )
            session = self._new_session(name=state.name)
            session.load_state(state)
            group_name = item.get("group", "")
            if group_name and group_name in self._groups:
                # Move from ungrouped into its group.
                if session in self._ungrouped:
                    self._ungrouped.remove(session)
                self._membership[session] = group_name
                self._groups[group_name].members.append(session)
        self._rebuild_bar()
