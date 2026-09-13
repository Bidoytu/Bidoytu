"""Table model + filter proxy for Intruder attack results.

:class:`IntruderResultsModel` holds one :class:`~bidoytu.ui.attack_runner.ResultRow`
per completed request and maps it to sortable columns. Numeric columns sort
numerically (via ``Qt.UserRole``) so "Length" and "Status" order correctly
rather than lexically. Status cells are color-coded like the Repeater.

:class:`ResultFilterProxy` filters rows by status code, minimum length, "only
matched", and a free-text needle over the payload / extracted columns.
"""
from __future__ import annotations

from typing import Optional

from PySide6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    QSortFilterProxyModel,
    Qt,
)
from PySide6.QtGui import QColor

from bidoytu.ui.attack_runner import ResultRow

# Column indices.
COL_INDEX = 0
COL_PAYLOAD = 1
COL_STATUS = 2
COL_LENGTH = 3
COL_TIME = 4
COL_MATCH = 5
COL_EXTRACT = 6
COL_ERROR = 7


def status_color(code: Optional[int]) -> str:
    if code is None:
        return "gray"
    if 200 <= code < 300:
        return "#2ecc71"
    if 300 <= code < 400:
        return "#3498db"
    if 400 <= code < 500:
        return "#e67e22"
    if code >= 500:
        return "#c0392b"
    return "gray"


class IntruderResultsModel(QAbstractTableModel):
    COLUMNS = ["#", "Payload", "Status", "Length", "Time (ms)",
               "Match", "Extracted", "Error"]

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._rows: list[ResultRow] = []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._rows)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self.COLUMNS)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self.COLUMNS[section]
        return section + 1

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return None
        row = self._rows[index.row()]
        col = index.column()
        if role == Qt.DisplayRole:
            return self._display(row, col)
        if role == Qt.UserRole:
            # Numeric sort key for the numeric columns.
            if col == COL_INDEX:
                return row.index
            if col == COL_STATUS:
                return row.status_code or 0
            if col == COL_LENGTH:
                return row.length
            if col == COL_TIME:
                return row.duration_ms
            return self._display(row, col)
        if role == Qt.ForegroundRole and col == COL_STATUS:
            return QColor(status_color(row.status_code))
        if role == Qt.TextAlignmentRole and col in (COL_INDEX, COL_STATUS, COL_LENGTH, COL_TIME):
            return int(Qt.AlignRight | Qt.AlignVCenter)
        return None

    @staticmethod
    def _display(row: ResultRow, col: int) -> str:
        if col == COL_INDEX:
            return str(row.index + 1)
        if col == COL_PAYLOAD:
            return " | ".join(row.payloads)
        if col == COL_STATUS:
            if row.status_code is None:
                return ""
            return f"{row.status_code} {row.reason}".strip()
        if col == COL_LENGTH:
            return str(row.length)
        if col == COL_TIME:
            return f"{row.duration_ms:.0f}" if row.duration_ms else ""
        if col == COL_MATCH:
            return "\u2714" if row.matched else ""
        if col == COL_EXTRACT:
            return row.extracted
        if col == COL_ERROR:
            return row.error
        return ""

    # -- mutation -------------------------------------------------------------

    def add_row(self, row: ResultRow) -> None:
        pos = len(self._rows)
        self.beginInsertRows(QModelIndex(), pos, pos)
        self._rows.append(row)
        self.endInsertRows()

    def row_at(self, source_row: int) -> Optional[ResultRow]:
        if 0 <= source_row < len(self._rows):
            return self._rows[source_row]
        return None

    def all_rows(self) -> list[ResultRow]:
        return list(self._rows)

    def clear(self) -> None:
        self.beginResetModel()
        self._rows.clear()
        self.endResetModel()


class ResultFilterProxy(QSortFilterProxyModel):
    """Filter results by status, min length, matched-only, and a text needle."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setSortRole(Qt.UserRole)
        self._status_prefix = ""   # "2", "4", "5", or "" for all
        self._min_length = 0
        self._matched_only = False
        self._needle = ""

    def set_status_prefix(self, prefix: str) -> None:
        self._status_prefix = prefix
        self.invalidateFilter()

    def set_min_length(self, value: int) -> None:
        self._min_length = value
        self.invalidateFilter()

    def set_matched_only(self, on: bool) -> None:
        self._matched_only = on
        self.invalidateFilter()

    def set_needle(self, needle: str) -> None:
        self._needle = needle.lower()
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, parent: QModelIndex) -> bool:
        model = self.sourceModel()
        row = model.row_at(source_row)
        if row is None:
            return True
        if self._status_prefix:
            code = row.status_code
            if code is None or not str(code).startswith(self._status_prefix):
                return False
        if self._min_length and row.length < self._min_length:
            return False
        if self._matched_only and not row.matched:
            return False
        if self._needle:
            hay = (" | ".join(row.payloads) + " " + row.extracted).lower()
            if self._needle not in hay:
                return False
        return True
