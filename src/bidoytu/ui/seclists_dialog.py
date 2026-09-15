"""A popup for browsing and loading SecLists wordlists on demand.

Opened from the Intruder payload editor's "Load SecLists" button, this dialog:

* lists every wordlist in the SecLists repository, grouped by directory;
* surfaces already-downloaded lists in a "Downloaded" group pinned to the top;
* downloads the selected list on demand (only what the user wants); and
* returns the chosen list's contents so the caller can drop it straight into a
  payload set - no manual download-then-import step.

All network work (fetching the index, downloading a list) happens on daemon
worker threads. Results are marshalled back to the UI thread through private Qt
signals, mirroring the pattern used by the Collaborator tab.
"""
from __future__ import annotations

import threading

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from bidoytu.net.seclists import SecListsRepository, WordlistEntry

# Roles for stashing data on tree items.
_PATH_ROLE = Qt.UserRole
_IS_LIST_ROLE = Qt.UserRole + 1

_DOWNLOADED_GROUP = "Downloaded"


def _human_size(size: int) -> str:
    """Render a byte count as a short human-readable string."""
    if size <= 0:
        return ""
    units = ["B", "KB", "MB", "GB"]
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.0f} {unit}" if unit == "B" else f"{value:.1f} {unit}"
        value /= 1024
    return f"{size} B"


class SecListsDialog(QDialog):
    """Browse the SecLists repository and pick a wordlist to load."""

    # Private signals marshal worker-thread results back onto the UI thread.
    _index_ready = Signal(object, str)     # list[WordlistEntry], error
    _download_ready = Signal(str, str, str)  # path, content, error

    def __init__(self, repo: SecListsRepository | None = None, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Load from SecLists")
        self.resize(640, 560)

        self._repo = repo or SecListsRepository()
        self._entries: list[WordlistEntry] = []
        # Set by the caller after the dialog is accepted.
        self.selected_content: str | None = None
        self.selected_path: str | None = None

        self._index_ready.connect(self._on_index_ready)
        self._download_ready.connect(self._on_download_ready)

        self._build_ui()
        self._start_fetch_index()

    # -- UI -------------------------------------------------------------------

    def _build_ui(self) -> None:
        self._status = QLabel("Loading wordlist index from SecLists...")
        self._status.setWordWrap(True)

        self._filter = QLineEdit()
        self._filter.setPlaceholderText("Filter wordlists by name or path...")
        self._filter.textChanged.connect(self._apply_filter)
        self._filter.setClearButtonEnabled(True)

        self._tree = QTreeWidget()
        self._tree.setHeaderLabels(["Wordlist", "Size"])
        self._tree.setColumnWidth(0, 440)
        self._tree.setAlternatingRowColors(True)
        self._tree.itemSelectionChanged.connect(self._on_selection_changed)
        self._tree.itemDoubleClicked.connect(self._on_double_click)

        self._refresh_btn = QPushButton("Refresh")
        self._refresh_btn.setToolTip("Re-fetch the wordlist index from GitHub")
        self._refresh_btn.clicked.connect(self._start_fetch_index)

        self._buttons = QDialogButtonBox()
        self._load_btn = self._buttons.addButton(
            "Load", QDialogButtonBox.AcceptRole
        )
        self._buttons.addButton(QDialogButtonBox.Cancel)
        self._load_btn.setEnabled(False)
        self._buttons.accepted.connect(self._on_load_clicked)
        self._buttons.rejected.connect(self.reject)

        top_row = QHBoxLayout()
        top_row.addWidget(self._filter, 1)
        top_row.addWidget(self._refresh_btn)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)
        layout.addLayout(top_row)
        layout.addWidget(self._tree, 1)
        layout.addWidget(self._status)
        layout.addWidget(self._buttons)

    # -- index fetch ----------------------------------------------------------

    def _start_fetch_index(self) -> None:
        self._set_busy(True, "Loading wordlist index from SecLists...")
        self._tree.clear()

        def _work() -> None:
            try:
                entries = self._repo.fetch_index()
                self._index_ready.emit(entries, "")
            except Exception as exc:  # network / HTTP / parse errors
                self._index_ready.emit([], str(exc))

        threading.Thread(target=_work, daemon=True).start()

    def _on_index_ready(self, entries: list[WordlistEntry], error: str) -> None:
        self._set_busy(False)
        if error:
            self._status.setText(
                f"Could not load the SecLists index: {error}\n"
                "Check your connection and try Refresh."
            )
            return
        self._entries = list(entries)
        self._populate_tree()
        downloaded = len(self._repo.downloaded_paths())
        self._status.setText(
            f"{len(self._entries)} wordlists available - {downloaded} downloaded. "
            "Double-click or select a list and press Load."
        )

    # -- tree population ------------------------------------------------------

    def _populate_tree(self) -> None:
        self._tree.clear()
        needle = self._filter.text().strip().lower()

        downloaded = set(self._repo.downloaded_paths())

        # A "Downloaded" group pinned to the top for instant reuse.
        if downloaded:
            dl_root = self._make_group_item(_DOWNLOADED_GROUP)
            for path in sorted(downloaded, key=str.lower):
                if needle and needle not in path.lower():
                    continue
                size = self._repo.local_path(path).stat().st_size
                self._add_list_item(dl_root, path, size, already=True)
            dl_root.setExpanded(bool(needle))
            if dl_root.childCount() == 0:
                index = self._tree.indexOfTopLevelItem(dl_root)
                self._tree.takeTopLevelItem(index)

        # Group the remaining repository entries by their directory.
        groups: dict[str, list[WordlistEntry]] = {}
        for entry in self._entries:
            if needle and needle not in entry.path.lower():
                continue
            groups.setdefault(entry.directory or "(root)", []).append(entry)

        for directory in sorted(groups, key=str.lower):
            group_item = self._make_group_item(directory)
            for entry in groups[directory]:
                self._add_list_item(
                    group_item, entry.path, entry.size,
                    already=entry.path in downloaded,
                )
            group_item.setExpanded(bool(needle))

    def _make_group_item(self, label: str) -> QTreeWidgetItem:
        item = QTreeWidgetItem(self._tree, [label, ""])
        item.setData(0, _IS_LIST_ROLE, False)
        item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
        font = item.font(0)
        font.setBold(True)
        item.setFont(0, font)
        return item

    def _add_list_item(
        self, parent: QTreeWidgetItem, path: str, size: int, *, already: bool
    ) -> None:
        name = path.rsplit("/", 1)[-1]
        label = f"{name}  \u2713" if already else name
        item = QTreeWidgetItem(parent, [label, _human_size(size)])
        item.setData(0, _PATH_ROLE, path)
        item.setData(0, _IS_LIST_ROLE, True)
        tip = path + ("  (downloaded)" if already else "")
        item.setToolTip(0, tip)

    def _apply_filter(self) -> None:
        if self._entries:
            self._populate_tree()

    # -- selection / load -----------------------------------------------------

    def _selected_path(self) -> str | None:
        items = self._tree.selectedItems()
        if not items:
            return None
        item = items[0]
        if not item.data(0, _IS_LIST_ROLE):
            return None
        return item.data(0, _PATH_ROLE)

    def _on_selection_changed(self) -> None:
        self._load_btn.setEnabled(self._selected_path() is not None)

    def _on_double_click(self, item: QTreeWidgetItem, _column: int) -> None:
        if item.data(0, _IS_LIST_ROLE):
            self._on_load_clicked()

    def _on_load_clicked(self) -> None:
        path = self._selected_path()
        if path is None:
            return
        already = self._repo.is_downloaded(path)
        verb = "Loading" if already else "Downloading"
        self._set_busy(True, f"{verb} {path}...")

        def _work() -> None:
            try:
                content = self._repo.read_text(path)
                self._download_ready.emit(path, content, "")
            except Exception as exc:  # network / HTTP / IO errors
                self._download_ready.emit(path, "", str(exc))

        threading.Thread(target=_work, daemon=True).start()

    def _on_download_ready(self, path: str, content: str, error: str) -> None:
        self._set_busy(False)
        if error:
            self._status.setText(f"Could not download {path}: {error}")
            return
        self.selected_path = path
        self.selected_content = content
        self.accept()

    # -- helpers --------------------------------------------------------------

    def _set_busy(self, busy: bool, message: str | None = None) -> None:
        self._refresh_btn.setEnabled(not busy)
        self._filter.setEnabled(not busy)
        self._tree.setEnabled(not busy)
        self._load_btn.setEnabled(not busy and self._selected_path() is not None)
        if message is not None:
            self._status.setText(message)
