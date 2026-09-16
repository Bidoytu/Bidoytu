"""Qt table models for the passive live-audit view."""
from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QColor

from bidoytu.audit.service import AuditIssue, AuditItem, Severity

SEVERITY_COLORS = {
    Severity.INFORMATIONAL: "#6b7280",  # grey
    Severity.LOW: "#2563eb",            # blue
    Severity.MEDIUM: "#d97706",         # orange
    Severity.CRITICAL: "#dc2626",       # red
}


class AuditItemModel(QAbstractTableModel):
    COLUMNS = ("Method", "Host", "Path", "Status")

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.rows: list[AuditItem] = []

    def rowCount(self, parent=QModelIndex()):  # noqa: N802
        return 0 if parent.isValid() else len(self.rows)

    def columnCount(self, parent=QModelIndex()):  # noqa: N802
        return 0 if parent.isValid() else len(self.COLUMNS)

    def headerData(self, section, orientation, role=Qt.DisplayRole):  # noqa: N802
        return self.COLUMNS[section] if role == Qt.DisplayRole and orientation == Qt.Horizontal else None

    def data(self, index, role=Qt.DisplayRole):  # noqa: N802
        if not index.isValid() or role != Qt.DisplayRole:
            return None
        item = self.rows[index.row()]
        return (item.method, item.host, item.path, str(item.status or ""))[index.column()]

    def add(self, item: AuditItem) -> None:
        if any(old.flow_id == item.flow_id for old in self.rows):
            return
        row = len(self.rows)
        self.beginInsertRows(QModelIndex(), row, row)
        self.rows.append(item)
        self.endInsertRows()

    def sort(self, column: int, order: Qt.SortOrder = Qt.AscendingOrder) -> None:  # noqa: N802
        """Sort the audit-item rows when a header is clicked."""
        if not 0 <= column < len(self.COLUMNS):
            return
        keys = (
            lambda row: row.method.casefold(),
            lambda row: row.host.casefold(),
            lambda row: row.path.casefold(),
            lambda row: (row.status is None, row.status if row.status is not None else -1),
        )
        self.layoutAboutToBeChanged.emit()
        self.rows.sort(key=keys[column], reverse=order == Qt.DescendingOrder)
        self.layoutChanged.emit()

    def clear(self) -> None:
        self.beginResetModel(); self.rows.clear(); self.endResetModel()


class AuditIssueModel(QAbstractTableModel):
    COLUMNS = ("Severity", "Issue type", "Host", "Path", "Confidence")

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.rows: list[AuditIssue] = []

    def rowCount(self, parent=QModelIndex()):  # noqa: N802
        return 0 if parent.isValid() else len(self.rows)

    def columnCount(self, parent=QModelIndex()):  # noqa: N802
        return 0 if parent.isValid() else len(self.COLUMNS)

    def headerData(self, section, orientation, role=Qt.DisplayRole):  # noqa: N802
        return self.COLUMNS[section] if role == Qt.DisplayRole and orientation == Qt.Horizontal else None

    def data(self, index, role=Qt.DisplayRole):  # noqa: N802
        if not index.isValid():
            return None
        issue = self.rows[index.row()]
        if role == Qt.DisplayRole:
            return (issue.severity, issue.title, issue.record.host, issue.record.path, issue.confidence)[index.column()]
        if role == Qt.ForegroundRole and index.column() == 0:
            return QColor(SEVERITY_COLORS[issue.severity])
        return None

    def add_many(self, issues: list[AuditIssue]) -> None:
        if not issues:
            return
        first = len(self.rows); last = first + len(issues) - 1
        self.beginInsertRows(QModelIndex(), first, last)
        self.rows.extend(issues)
        self.endInsertRows()

    def sort(self, column: int, order: Qt.SortOrder = Qt.AscendingOrder) -> None:  # noqa: N802
        """Sort findings by the selected column, with severity ranked."""
        if not 0 <= column < len(self.COLUMNS):
            return
        severity_rank = {
            Severity.INFORMATIONAL: 0,
            Severity.LOW: 1,
            Severity.MEDIUM: 2,
            Severity.CRITICAL: 3,
        }
        keys = (
            lambda issue: severity_rank.get(issue.severity, -1),
            lambda issue: issue.title.casefold(),
            lambda issue: issue.record.host.casefold(),
            lambda issue: issue.record.path.casefold(),
            lambda issue: issue.confidence.casefold(),
        )
        self.layoutAboutToBeChanged.emit()
        self.rows.sort(key=keys[column], reverse=order == Qt.DescendingOrder)
        self.layoutChanged.emit()

    def issue_at(self, row: int) -> AuditIssue | None:
        return self.rows[row] if 0 <= row < len(self.rows) else None

    def clear(self) -> None:
        self.beginResetModel(); self.rows.clear(); self.endResetModel()
