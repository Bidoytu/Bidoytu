"""A small find bar that searches within a QPlainTextEdit.

Reusable over any :class:`~PySide6.QtWidgets.QPlainTextEdit` (e.g. the request
editor or response viewer). Supports next/previous navigation, case-sensitive
matching, and wrap-around. The bar hides itself on Escape and reveals + focuses
its input via :meth:`activate`.
"""
from __future__ import annotations

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QKeyEvent, QTextCursor, QTextDocument
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QWidget,
)
from bidoytu.ui.theme import ui_icon


class FindBar(QWidget):
    """Incremental find controls bound to a target text edit."""

    def __init__(self, target: QPlainTextEdit, parent=None) -> None:
        super().__init__(parent)
        self._target = target

        self._input = QLineEdit()
        self._input.setPlaceholderText("Find")
        self._input.textChanged.connect(lambda _: self._find(forward=True, incremental=True))
        self._input.returnPressed.connect(lambda: self._find(forward=True))

        self._case = QCheckBox("Aa")
        self._case.setToolTip("Case sensitive")
        self._case.stateChanged.connect(lambda _: self._find(forward=True, incremental=True))

        self._status = QLabel("")
        self._status.setStyleSheet("color: gray;")

        prev_btn = QPushButton()
        prev_btn.setIcon(ui_icon("up"))
        prev_btn.setIconSize(QSize(18, 18))
        prev_btn.setToolTip("Previous (Shift+Enter)")
        prev_btn.setMaximumWidth(28)
        prev_btn.clicked.connect(lambda: self._find(forward=False))

        next_btn = QPushButton()
        next_btn.setIcon(ui_icon("down"))
        next_btn.setIconSize(QSize(18, 18))
        next_btn.setToolTip("Next (Enter)")
        next_btn.setMaximumWidth(28)
        next_btn.clicked.connect(lambda: self._find(forward=True))

        close_btn = QPushButton()
        close_btn.setIcon(ui_icon("close"))
        close_btn.setIconSize(QSize(18, 18))
        close_btn.setMaximumWidth(28)
        close_btn.clicked.connect(self.hide)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.addWidget(QLabel("Find:"))
        layout.addWidget(self._input, 1)
        layout.addWidget(self._case)
        layout.addWidget(prev_btn)
        layout.addWidget(next_btn)
        layout.addWidget(self._status)
        layout.addWidget(close_btn)

        self.hide()

    def activate(self) -> None:
        """Reveal the bar, seed it with any selected text, and focus input."""
        selected = self._target.textCursor().selectedText()
        if selected:
            self._input.setText(selected)
        self.show()
        self._input.setFocus()
        self._input.selectAll()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Escape:
            self.hide()
            self._target.setFocus()
            return
        super().keyPressEvent(event)

    def _flags(self, forward: bool) -> QTextDocument.FindFlags:
        flags = QTextDocument.FindFlags()
        if not forward:
            flags |= QTextDocument.FindBackward
        if self._case.isChecked():
            flags |= QTextDocument.FindCaseSensitively
        return flags

    def _find(self, forward: bool, incremental: bool = False) -> None:
        needle = self._input.text()
        if not needle:
            self._status.setText("")
            self._input.setStyleSheet("")
            return

        # For incremental search, start from the current selection start so the
        # match set doesn't jump forward while typing.
        if incremental:
            cursor = self._target.textCursor()
            cursor.setPosition(cursor.selectionStart())
            self._target.setTextCursor(cursor)

        found = self._target.find(needle, self._flags(forward))
        if not found:
            # Wrap around: reset the cursor to the document edge and retry.
            cursor = self._target.textCursor()
            cursor.movePosition(
                QTextCursor.Start if forward else QTextCursor.End
            )
            self._target.setTextCursor(cursor)
            found = self._target.find(needle, self._flags(forward))

        if found:
            self._status.setText("")
            self._input.setStyleSheet("")
        else:
            self._status.setText("no match")
            self._input.setStyleSheet("background: #5a2a2a;")
