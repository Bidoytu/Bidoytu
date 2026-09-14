"""SQLite persistence for captured flows.

Uses the stdlib ``sqlite3`` module directly (no QSqlDatabase) so the storage
layer stays independent of Qt and can be unit-tested in isolation. WAL mode is
enabled for better read/write concurrency between the proxy thread (writes) and
the UI thread (reads).

Threading note: a single sqlite3 connection is not safe to share across
threads. Each thread that needs DB access should own its own repository
instance (SQLite handles cross-connection coordination via WAL + locking).
"""
from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional

from bidoytu.storage.models import FlowRecord

_SCHEMA = """
CREATE TABLE IF NOT EXISTS flows (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    flow_id              TEXT NOT NULL UNIQUE,
    method               TEXT NOT NULL DEFAULT '',
    scheme               TEXT NOT NULL DEFAULT '',
    host                 TEXT NOT NULL DEFAULT '',
    port                 INTEGER NOT NULL DEFAULT 0,
    path                 TEXT NOT NULL DEFAULT '',
    http_version         TEXT NOT NULL DEFAULT '',
    request_headers      TEXT NOT NULL DEFAULT '',
    request_body_inline  BLOB,
    request_body_path    TEXT,
    request_body_size    INTEGER NOT NULL DEFAULT 0,
    status_code          INTEGER,
    reason               TEXT NOT NULL DEFAULT '',
    response_headers     TEXT NOT NULL DEFAULT '',
    response_body_inline BLOB,
    response_body_path   TEXT,
    response_body_size   INTEGER NOT NULL DEFAULT 0,
    content_type         TEXT NOT NULL DEFAULT '',
    started_at           REAL NOT NULL DEFAULT 0,
    completed_at         REAL,
    tags                 TEXT NOT NULL DEFAULT '',
    notes                TEXT NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_flows_host ON flows(host);
CREATE INDEX IF NOT EXISTS idx_flows_started_at ON flows(started_at);
"""

# Columns in a fixed order shared by insert/update/select mapping.
_COLUMNS = (
    "flow_id", "method", "scheme", "host", "port", "path", "http_version",
    "request_headers", "request_body_inline", "request_body_path",
    "request_body_size", "status_code", "reason", "response_headers",
    "response_body_inline", "response_body_path", "response_body_size",
    "content_type", "started_at", "completed_at", "tags", "notes",
)


class FlowRepository:
    """CRUD access to the ``flows`` table."""

    def __init__(self, db_path: Path) -> None:
        self._db_path = Path(db_path)
        self.recovered_from: Optional[Path] = None
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = self._open_or_recover()

    def _open_or_recover(self) -> sqlite3.Connection:
        """Open and validate the database, recovering from SQLite corruption.

        A damaged database must not prevent the application from starting. The
        original file is moved aside (rather than deleted) before a new empty
        database is created, so it remains available for manual salvage.
        """
        conn: sqlite3.Connection | None = None
        try:
            conn = self._connect()
            self._initialize(conn)
            return conn
        except sqlite3.DatabaseError:
            # Close the failed connection before moving the database on
            # Windows, where an open handle prevents rename/replace.
            if conn is not None:
                conn.close()

            backup_path = self._quarantine_corrupt_database()
            conn = self._connect()
            self._initialize(conn)
            # Keep this information available to callers/debuggers without
            # making startup dependent on a logging configuration.
            self.recovered_from = backup_path
            return conn

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self._db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize(self, conn: sqlite3.Connection) -> None:
        self._configure(conn)
        conn.executescript(_SCHEMA)
        conn.commit()
        result = conn.execute("PRAGMA quick_check").fetchone()
        if result is None or result[0] != "ok":
            raise sqlite3.DatabaseError(
                f"SQLite integrity check failed: {result[0] if result else 'no result'}"
            )

    def _quarantine_corrupt_database(self) -> Path:
        """Move the corrupt database and SQLite sidecars to a safe backup."""
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = self._db_path.with_name(f"{self._db_path.name}.corrupt-{stamp}")
        suffix = 1
        while backup.exists():
            backup = self._db_path.with_name(
                f"{self._db_path.name}.corrupt-{stamp}-{suffix}"
            )
            suffix += 1

        if self._db_path.exists():
            self._db_path.replace(backup)
        for sidecar in (
            self._db_path.with_name(self._db_path.name + "-wal"),
            self._db_path.with_name(self._db_path.name + "-shm"),
        ):
            if sidecar.exists():
                sidecar.replace(backup.with_name(backup.name + sidecar.suffix))
        return backup

    @staticmethod
    def _configure(conn: sqlite3.Connection) -> None:
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("PRAGMA synchronous=NORMAL;")
        cur.execute("PRAGMA foreign_keys=ON;")
        cur.close()

    # -- writes ---------------------------------------------------------------

    def insert(self, record: FlowRecord) -> int:
        """Insert a new flow and return its assigned primary key."""
        values = [getattr(record, col) for col in _COLUMNS]
        placeholders = ", ".join("?" for _ in _COLUMNS)
        cols = ", ".join(_COLUMNS)
        cur = self._conn.execute(
            f"INSERT INTO flows ({cols}) VALUES ({placeholders})", values
        )
        self._conn.commit()
        record.id = int(cur.lastrowid)
        return record.id

    def update(self, record: FlowRecord) -> None:
        """Update an existing flow (matched by ``flow_id``)."""
        assignments = ", ".join(f"{col} = ?" for col in _COLUMNS)
        values = [getattr(record, col) for col in _COLUMNS]
        values.append(record.flow_id)
        self._conn.execute(
            f"UPDATE flows SET {assignments} WHERE flow_id = ?", values
        )
        self._conn.commit()

    def upsert(self, record: FlowRecord) -> int:
        """Insert if new, otherwise update. Returns the row id."""
        existing = self.get_by_flow_id(record.flow_id)
        if existing is None:
            return self.insert(record)
        record.id = existing.id
        self.update(record)
        return record.id

    def clear(self) -> None:
        self._conn.execute("DELETE FROM flows")
        self._conn.commit()

    # -- reads ----------------------------------------------------------------

    def count(self) -> int:
        row = self._conn.execute("SELECT COUNT(*) AS c FROM flows").fetchone()
        return int(row["c"])

    def get(self, row_id: int) -> Optional[FlowRecord]:
        row = self._conn.execute(
            "SELECT * FROM flows WHERE id = ?", (row_id,)
        ).fetchone()
        return self._row_to_record(row) if row else None

    def get_by_flow_id(self, flow_id: str) -> Optional[FlowRecord]:
        row = self._conn.execute(
            "SELECT * FROM flows WHERE flow_id = ?", (flow_id,)
        ).fetchone()
        return self._row_to_record(row) if row else None

    def list_all(self, limit: Optional[int] = None) -> list[FlowRecord]:
        sql = "SELECT * FROM flows ORDER BY id ASC"
        if limit is not None:
            sql += f" LIMIT {int(limit)}"
        rows = self._conn.execute(sql).fetchall()
        return [self._row_to_record(r) for r in rows]

    def iter_all(self) -> Iterable[FlowRecord]:
        for row in self._conn.execute("SELECT * FROM flows ORDER BY id ASC"):
            yield self._row_to_record(row)

    # -- helpers --------------------------------------------------------------

    @staticmethod
    def _row_to_record(row: sqlite3.Row) -> FlowRecord:
        return FlowRecord(
            id=row["id"],
            flow_id=row["flow_id"],
            method=row["method"],
            scheme=row["scheme"],
            host=row["host"],
            port=row["port"],
            path=row["path"],
            http_version=row["http_version"],
            request_headers=row["request_headers"],
            request_body_inline=row["request_body_inline"],
            request_body_path=row["request_body_path"],
            request_body_size=row["request_body_size"],
            status_code=row["status_code"],
            reason=row["reason"],
            response_headers=row["response_headers"],
            response_body_inline=row["response_body_inline"],
            response_body_path=row["response_body_path"],
            response_body_size=row["response_body_size"],
            content_type=row["content_type"],
            started_at=row["started_at"],
            completed_at=row["completed_at"],
            tags=row["tags"],
            notes=row["notes"],
        )

    def close(self) -> None:
        self._conn.close()
