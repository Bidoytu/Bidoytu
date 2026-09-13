"""Table model + filter proxy for Collaborator (OAST) interactions.

:class:`InteractionsModel` holds one
:class:`~bidoytu.net.interactsh.Interaction` per received out-of-band callback
and maps it to sortable columns. The "#" and "Time" columns sort numerically /
chronologically (via ``Qt.UserRole``) rather than lexically. The protocol cell
is color-coded (DNS / HTTP / SMTP / LDAP) so hits are easy to scan, matching
the color-coded status cells used elsewhere in the app.

:class:`InteractionFilterProxy` filters rows by protocol and a free-text needle
over the payload / source / raw-request columns.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from PySide6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    QSortFilterProxyModel,
    Qt,
)
from PySide6.QtGui import QColor

from bidoytu.net.interactsh import Interaction

# Column indices.
COL_INDEX = 0
COL_TIME = 1
COL_PROTOCOL = 2
COL_PAYLOAD = 3
COL_SOURCE = 4
COL_QTYPE = 5


def protocol_color(protocol: str) -> str:
    """Return a hex color for an interaction protocol."""
    p = (protocol or "").lower()
    if p == "dns":
        return "#3498db"   # blue
    if p in ("http", "https"):
        return "#2ecc71"   # green
    if p == "smtp":
        return "#e67e22"   # orange
    if p in ("ldap", "ftp"):
        return "#9b59b6"   # purple
    return "#95a5a6"       # gray


@dataclass(slots=True)
class InteractionRow:
    """A received interaction plus the display metadata we derive from it."""

    interaction: Interaction
    index: int
    # The label shown for this hit's payload. When we can correlate the hit
    # back to a specific generated payload we show that; otherwise the full id.
    payload_label: str = ""
    # Optional note about what request/tool this payload was inserted into.
    note: str = ""


class InteractionsModel(QAbstractTableModel):
    COLUMNS = ["#", "Time", "Type", "Payload", "Source IP", "Query"]

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._rows: list[InteractionRow] = []

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
            # Numeric / chronological sort keys.
            if col == COL_INDEX:
                return row.index
            if col == COL_TIME:
                return row.interaction.timestamp
            return self._display(row, col)
        if role == Qt.ForegroundRole and col == COL_PROTOCOL:
            return QColor(protocol_color(row.interaction.protocol))
        if role == Qt.TextAlignmentRole and col == COL_INDEX:
            return int(Qt.AlignRight | Qt.AlignVCenter)
        return None

    @staticmethod
    def _display(row: InteractionRow, col: int) -> str:
        it = row.interaction
        if col == COL_INDEX:
            return str(row.index + 1)
        if col == COL_TIME:
            return _short_time(it.timestamp)
        if col == COL_PROTOCOL:
            return (it.protocol or "").upper()
        if col == COL_PAYLOAD:
            return row.payload_label or it.full_id or it.unique_id
        if col == COL_SOURCE:
            return it.remote_address
        if col == COL_QTYPE:
            return it.q_type
        return ""

    # -- mutation -------------------------------------------------------------

    def add_interaction(self, interaction: Interaction,
                        payload_label: str = "", note: str = "") -> InteractionRow:
        pos = len(self._rows)
        row = InteractionRow(
            interaction=interaction, index=pos,
            payload_label=payload_label, note=note,
        )
        self.beginInsertRows(QModelIndex(), pos, pos)
        self._rows.append(row)
        self.endInsertRows()
        return row

    def row_at(self, source_row: int) -> Optional[InteractionRow]:
        if 0 <= source_row < len(self._rows):
            return self._rows[source_row]
        return None

    def all_rows(self) -> list[InteractionRow]:
        return list(self._rows)

    def clear(self) -> None:
        self.beginResetModel()
        self._rows.clear()
        self.endResetModel()


def _short_time(iso_ts: str) -> str:
    """Render an ISO timestamp as HH:MM:SS, falling back to the raw string."""
    if not iso_ts:
        return ""
    # Typical form: 2026-09-13T12:34:56.789Z or with offset. Take the time part.
    t = iso_ts
    if "T" in t:
        t = t.split("T", 1)[1]
    # Trim timezone / fractional seconds.
    for sep in ("+", "Z", "."):
        if sep in t:
            t = t.split(sep, 1)[0]
    return t[:8] if t else iso_ts


class InteractionFilterProxy(QSortFilterProxyModel):
    """Filter interactions by protocol and a free-text needle."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setSortRole(Qt.UserRole)
        self._protocol = ""   # "", "dns", "http", "smtp", ...
        self._needle = ""

    def set_protocol(self, protocol: str) -> None:
        self._protocol = protocol.lower()
        self.invalidateFilter()

    def set_needle(self, needle: str) -> None:
        self._needle = needle.lower()
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, parent: QModelIndex) -> bool:
        model = self.sourceModel()
        row = model.row_at(source_row)
        if row is None:
            return True
        it = row.interaction
        if self._protocol:
            proto = (it.protocol or "").lower()
            if self._protocol == "http":
                if proto not in ("http", "https"):
                    return False
            elif proto != self._protocol:
                return False
        if self._needle:
            hay = " ".join([
                row.payload_label, it.full_id, it.unique_id,
                it.remote_address, it.raw_request, it.q_type,
            ]).lower()
            if self._needle not in hay:
                return False
        return True
