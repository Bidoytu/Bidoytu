"""Table model for the Intercept tab's activity log.

Each intercepted request becomes a row when the proxy pauses it. Rows carry the
underlying :class:`FlowRecord` and a ``pending`` flag (still awaiting a
forward/drop decision). When a response comes back, a separate response row is
appended so the user sees the full stream.

Columns:

    Time | Type | Direction | Method | URL | Status | Length

The model is the source of truth for which paused requests are still pending,
so the panel can drive the editor from the current selection and resolve
individual or all pending flows.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from bidoytu.storage.models import FlowRecord

REQUEST = "Request"
RESPONSE = "Response"


@dataclass(slots=True)
class ActivityRow:
    when: float               # unix epoch seconds
    direction: str            # "Request" | "Response"
    record: FlowRecord        # underlying flow
    pending: bool = False     # paused request awaiting a decision
    resolved: str = ""        # "forwarded" | "dropped" | "" (for request rows)

    # Cached display bits derived from the record.
    method: str = ""
    url: str = ""
    mime: str = ""
    status: str = ""
    length: int = 0


class InterceptActivityModel(QAbstractTableModel):
    COLUMNS = ["Time", "Type", "Direction", "Method", "URL", "Status", "Length"]

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._rows: list[ActivityRow] = []

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
        row = self._rows[index.row()]
        if role == Qt.DisplayRole:
            return self._display(row, index.column())
        if role == Qt.TextAlignmentRole and index.column() in (5, 6):
            return int(Qt.AlignRight | Qt.AlignVCenter)
        return None

    def _display(self, r: ActivityRow, col: int) -> str:
        if col == 0:
            return time.strftime("%H:%M:%S", time.localtime(r.when))
        if col == 1:
            return r.mime
        if col == 2:
            return r.direction
        if col == 3:
            return r.method
        if col == 4:
            return r.url
        if col == 5:
            return r.status
        if col == 6:
            return str(r.length) if r.length else ""
        return ""

    # -- mutation -------------------------------------------------------------

    def _append(self, row: ActivityRow) -> int:
        pos = len(self._rows)
        self.beginInsertRows(QModelIndex(), pos, pos)
        self._rows.append(row)
        self.endInsertRows()
        return pos

    def add_request(self, record: FlowRecord) -> int:
        """Log a paused (pending) request. Returns its row index."""
        return self._append(ActivityRow(
            when=record.started_at or time.time(),
            direction=REQUEST,
            record=record,
            pending=True,
            method=record.method,
            url=record.url,
            mime="",
            status="",
            length=record.request_body_size,
        ))

    def add_response(self, record: FlowRecord) -> int:
        """Log a paused (pending) response. Returns its row index."""
        status = str(record.status_code) if record.status_code else ""
        return self._append(ActivityRow(
            when=record.completed_at or time.time(),
            direction=RESPONSE,
            record=record,
            pending=True,
            method=record.method,
            url=record.url,
            mime=record.content_type or "",
            status=status,
            length=record.response_body_size,
        ))

    def row_at(self, row: int) -> Optional[ActivityRow]:
        if 0 <= row < len(self._rows):
            return self._rows[row]
        return None

    def record_at(self, row: int) -> Optional[FlowRecord]:
        r = self.row_at(row)
        return r.record if r is not None else None

    def is_pending(self, row: int) -> bool:
        """True if the row is a still-pending request or response."""
        r = self.row_at(row)
        return bool(r and r.pending)

    def direction_at(self, row: int) -> str:
        r = self.row_at(row)
        return r.direction if r is not None else ""

    def is_pending_request(self, row: int) -> bool:
        r = self.row_at(row)
        return bool(r and r.direction == REQUEST and r.pending)

    def is_pending_response(self, row: int) -> bool:
        r = self.row_at(row)
        return bool(r and r.direction == RESPONSE and r.pending)

    def pending_flow_ids(self) -> list[str]:
        """Flow ids of all still-pending requests, in arrival order."""
        return [r.record.flow_id for r in self._rows
                if r.direction == REQUEST and r.pending]

    def pending_response_flow_ids(self) -> list[str]:
        """Flow ids of all still-pending responses, in arrival order."""
        return [r.record.flow_id for r in self._rows
                if r.direction == RESPONSE and r.pending]

    def has_any_pending(self) -> bool:
        return any(r.pending for r in self._rows)

    def first_pending_row(self) -> Optional[int]:
        """First still-pending row, whether request or response."""
        for i, r in enumerate(self._rows):
            if r.pending:
                return i
        return None

    def remove_flow(self, flow_id: str) -> None:
        """Remove the row(s) for ``flow_id`` from the table."""
        for i in range(len(self._rows) - 1, -1, -1):
            if self._rows[i].record.flow_id == flow_id:
                self.beginRemoveRows(QModelIndex(), i, i)
                self._rows.pop(i)
                self.endRemoveRows()

    def remove_row(self, row: int) -> None:
        """Remove a single row by index."""
        if 0 <= row < len(self._rows):
            self.beginRemoveRows(QModelIndex(), row, row)
            self._rows.pop(row)
            self.endRemoveRows()

    def row_index_for(self, flow_id: str, direction: str) -> Optional[int]:
        """Row index of the (flow_id, direction) pair, or None."""
        for i, r in enumerate(self._rows):
            if r.record.flow_id == flow_id and r.direction == direction:
                return i
        return None

    def clear(self) -> None:
        self.beginResetModel()
        self._rows.clear()
        self.endResetModel()
