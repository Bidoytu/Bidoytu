"""Custom QAbstractTableModel backing the traffic history view.

We use a hand-written model (instead of QSqlTableModel) so we control exactly
how :class:`~bidoytu.storage.models.FlowRecord` objects map to columns, and so
the model can be fed incrementally from the proxy thread via signals without
re-querying the database on every packet.

The model keeps an in-memory list of records for fast display. The database
remains the source of truth for persistence; the list mirrors what the user is
currently viewing.
"""
from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QColor

from bidoytu.storage.models import FlowRecord
from bidoytu.storage.advanced_history import FilterSpec, matches


class FlowTableModel(QAbstractTableModel):
    COLUMNS = [
        "#", "Method", "Host", "Path", "Ext", "Status",
        "Type", "Length", "Cookies", "Time (ms)",
    ]

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._rows: list[FlowRecord] = []
        self._all_rows: list[FlowRecord] = []
        self._filter = FilterSpec()
        self._index_by_flow_id: dict[str, int] = {}
        self._all_index_by_flow_id: dict[str, int] = {}

    # -- Qt model interface ---------------------------------------------------

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._rows)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self.COLUMNS)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self.COLUMNS[section]
        return section + 1

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return None
        record = self._rows[index.row()]
        if role == Qt.DisplayRole:
            return self._display(record, index.column())
        if role == Qt.BackgroundRole and record.color:
            color = QColor(record.color)
            color.setAlpha(55)
            return color
        if role == Qt.TextAlignmentRole and index.column() in (0, 5, 7, 9):
            return int(Qt.AlignRight | Qt.AlignVCenter)
        return None

    def _display(self, r: FlowRecord, col: int) -> str:
        if col == 0:
            marker = "★ " if r.bookmarked else ("! " if r.interesting else "")
            return marker + str(r.id if r.id is not None else "")
        if col == 1:
            return r.method
        if col == 2:
            return r.host
        if col == 3:
            return r.path
        if col == 4:
            return r.extension
        if col == 5:
            return str(r.status_code) if r.status_code is not None else ""
        if col == 6:
            return r.mime_type
        if col == 7:
            return str(r.response_body_size)
        if col == 8:
            return r.cookies
        if col == 9:
            d = r.duration_ms
            return f"{d:.0f}" if d is not None else ""
        return ""

    # -- data mutation --------------------------------------------------------

    def record_at(self, row: int) -> Optional[FlowRecord]:
        if 0 <= row < len(self._rows):
            return self._rows[row]
        return None

    def upsert_record(self, record: FlowRecord) -> None:
        """Add a new record, or update an existing one in place.

        Called from the UI thread in response to proxy signals.
        """
        source_index = self._all_index_by_flow_id.get(record.flow_id)
        if source_index is None:
            self._all_index_by_flow_id[record.flow_id] = len(self._all_rows)
            self._all_rows.append(record)
            if matches(record, self._filter):
                row = len(self._rows)
                self.beginInsertRows(QModelIndex(), row, row)
                self._rows.append(record)
                self._index_by_flow_id[record.flow_id] = row
                self.endInsertRows()
            return

        self._all_rows[source_index] = record
        visible_index = self._index_by_flow_id.get(record.flow_id)
        visible = matches(record, self._filter)
        if visible_index is not None and visible:
            self._rows[visible_index] = record
            first = self.index(visible_index, 0)
            last = self.index(visible_index, len(self.COLUMNS) - 1)
            self.dataChanged.emit(first, last)
        elif visible_index is not None:
            self.beginRemoveRows(QModelIndex(), visible_index, visible_index)
            self._rows.pop(visible_index)
            self.endRemoveRows()
            self._index_by_flow_id = {r.flow_id: i for i, r in enumerate(self._rows)}
        elif visible:
            row = len(self._rows)
            self.beginInsertRows(QModelIndex(), row, row)
            self._rows.append(record)
            self._index_by_flow_id[record.flow_id] = row
            self.endInsertRows()

    def load_records(self, records: list[FlowRecord]) -> None:
        """Replace all rows (e.g. when loading history from the database)."""
        self.beginResetModel()
        self._all_rows = list(records)
        self._rows = list(records)
        self._all_index_by_flow_id = {
            r.flow_id: i for i, r in enumerate(self._all_rows)
        }
        self._index_by_flow_id = {
            r.flow_id: i for i, r in enumerate(self._rows)
        }
        self.endResetModel()

    def clear(self) -> None:
        self.beginResetModel()
        self._rows.clear()
        self._all_rows.clear()
        self._index_by_flow_id.clear()
        self._all_index_by_flow_id.clear()
        self.endResetModel()

    def apply_filter(self, spec: FilterSpec) -> None:
        self._filter = spec
        self.beginResetModel()
        self._rows = [r for r in self._all_rows if matches(r, spec)]
        self._index_by_flow_id = {r.flow_id: i for i, r in enumerate(self._rows)}
        self.endResetModel()

    def all_records(self) -> list[FlowRecord]:
        return list(self._all_rows)

    def visible_records(self) -> list[FlowRecord]:
        return list(self._rows)

    def sort(self, column: int, order: Qt.SortOrder = Qt.AscendingOrder) -> None:
        """Sort the source rows while keeping the active History filter applied."""
        key_names = ("id", "method", "host", "path", "extension", "status_code",
                     "mime_type", "response_body_size", "cookies", "duration_ms")
        if not 0 <= column < len(key_names):
            return
        key_name = key_names[column]
        def key(record: FlowRecord):
            value = getattr(record, key_name)
            return (value is None, value if value is not None else "")
        self._all_rows.sort(key=key, reverse=order == Qt.DescendingOrder)
        self._all_index_by_flow_id = {r.flow_id: i for i, r in enumerate(self._all_rows)}
        self.apply_filter(self._filter)
