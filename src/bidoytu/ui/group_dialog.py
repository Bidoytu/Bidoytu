"""Dialog for adding Repeater request tabs to a named, colored group.

Presents a group-name field, a checkbox list of the currently open tabs (with a
"Select all" toggle), and a small palette of colors plus a custom color button.
On accept it exposes the chosen name, the selected tab indices, and the color.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QColorDialog,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# A small default palette of distinguishable group colors.
PALETTE = [
    "#e74c3c",  # red
    "#e67e22",  # orange
    "#f1c40f",  # yellow
    "#2ecc71",  # green
    "#1abc9c",  # teal
    "#3498db",  # blue
    "#9b59b6",  # purple
    "#95a5a6",  # gray
]


class GroupDialog(QDialog):
    """Collect a group name, member tabs, and a color."""

    def __init__(self, tab_titles: list[str], preselected: list[int] | None = None,
                 name: str = "", color: str = PALETTE[0], parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Add to group")
        self._color = color

        # Group name.
        self._name_edit = QLineEdit(name)
        self._name_edit.setPlaceholderText("Group name")

        # Tab checklist.
        self._list = QListWidget()
        preselected = set(preselected or [])
        for i, title in enumerate(tab_titles):
            item = QListWidgetItem(title)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(
                Qt.Checked if i in preselected else Qt.Unchecked
            )
            item.setData(Qt.UserRole, i)
            self._list.addItem(item)

        select_all_btn = QPushButton("Select all")
        select_all_btn.clicked.connect(self._toggle_select_all)

        # Color palette.
        self._swatch = QLabel()
        self._swatch.setFixedSize(24, 24)
        self._apply_swatch()
        palette_row = QHBoxLayout()
        palette_row.setContentsMargins(0, 0, 0, 0)
        for hex_color in PALETTE:
            btn = QPushButton()
            btn.setFixedSize(22, 22)
            btn.setStyleSheet(
                f"background: {hex_color}; border: 1px solid #333;"
            )
            btn.clicked.connect(lambda _=False, c=hex_color: self._set_color(c))
            palette_row.addWidget(btn)
        custom_btn = QPushButton("Custom...")
        custom_btn.clicked.connect(self._pick_custom_color)
        palette_row.addWidget(custom_btn)
        palette_row.addStretch(1)

        color_row = QHBoxLayout()
        color_row.addWidget(QLabel("Color:"))
        color_row.addWidget(self._swatch)
        color_wrap = QWidget()
        color_wrap.setLayout(palette_row)
        color_row.addWidget(color_wrap, 1)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Group name:"))
        layout.addWidget(self._name_edit)
        layout.addWidget(QLabel("Tabs in this group:"))
        layout.addWidget(self._list, 1)
        layout.addWidget(select_all_btn)
        layout.addLayout(color_row)
        layout.addWidget(buttons)
        self.resize(360, 420)

    # -- color helpers --------------------------------------------------------

    def _set_color(self, hex_color: str) -> None:
        self._color = hex_color
        self._apply_swatch()

    def _apply_swatch(self) -> None:
        self._swatch.setStyleSheet(
            f"background: {self._color}; border: 1px solid #333;"
        )

    def _pick_custom_color(self) -> None:
        chosen = QColorDialog.getColor(QColor(self._color), self, "Group color")
        if chosen.isValid():
            self._set_color(chosen.name())

    # -- selection helpers ----------------------------------------------------

    def _toggle_select_all(self) -> None:
        # If everything is already checked, clear; otherwise check all.
        all_checked = all(
            self._list.item(i).checkState() == Qt.Checked
            for i in range(self._list.count())
        )
        new_state = Qt.Unchecked if all_checked else Qt.Checked
        for i in range(self._list.count()):
            self._list.item(i).setCheckState(new_state)

    # -- results --------------------------------------------------------------

    def group_name(self) -> str:
        return self._name_edit.text().strip()

    def selected_indices(self) -> list[int]:
        result = []
        for i in range(self._list.count()):
            item = self._list.item(i)
            if item.checkState() == Qt.Checked:
                result.append(int(item.data(Qt.UserRole)))
        return result

    def color(self) -> str:
        return self._color
