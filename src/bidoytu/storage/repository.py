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
    notes                TEXT NOT NULL DEFAULT '',
    scope                INTEGER NOT NULL DEFAULT 1,
    tool                 TEXT NOT NULL DEFAULT 'Proxy',
    bookmarked           INTEGER NOT NULL DEFAULT 0,
    interesting          INTEGER NOT NULL DEFAULT 0,
    color                TEXT NOT NULL DEFAULT '',
    duplicate_of         INTEGER
);
CREATE INDEX IF NOT EXISTS idx_flows_host ON flows(host);
CREATE INDEX IF NOT EXISTS idx_flows_started_at ON flows(started_at);
CREATE INDEX IF NOT EXISTS idx_flows_duplicate ON flows(duplicate_of);
CREATE INDEX IF NOT EXISTS idx_flows_duplicate_lookup
    ON flows(method, host, path, request_body_size, response_body_size, id);
CREATE TABLE IF NOT EXISTS saved_filters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    query TEXT NOT NULL DEFAULT '',
    created_at REAL NOT NULL DEFAULT (strftime('%s','now'))
);
"""

# Columns in a fixed order shared by insert/update/select mapping.
_COLUMNS = (
    "flow_id", "method", "scheme", "host", "port", "path", "http_version",
    "request_headers", "request_body_inline", "request_body_path",
    "request_body_size", "status_code", "reason", "response_headers",
    "response_body_inline", "response_body_path", "response_body_size",
    "content_type", "started_at", "completed_at", "tags", "notes",
    "scope", "tool", "bookmarked", "interesting", "color", "duplicate_of",
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
        # Keep SQLite from queueing indefinitely under concurrent proxy/UI
        # access.  The page cache is bounded so a large history cannot consume
        # unbounded process memory, while WAL/NORMAL keeps writes lightweight.
        conn = sqlite3.connect(
            str(self._db_path), check_same_thread=False,
            timeout=5.0, cached_statements=128,
        )
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize(self, conn: sqlite3.Connection) -> None:
        self._configure(conn)
        conn.executescript(_SCHEMA)
        # Migrate databases created before advanced history existed.
        existing = {row[1] for row in conn.execute("PRAGMA table_info(flows)")}
        for name, definition in (
            ("scope", "INTEGER NOT NULL DEFAULT 1"),
            ("tool", "TEXT NOT NULL DEFAULT 'Proxy'"),
            ("bookmarked", "INTEGER NOT NULL DEFAULT 0"),
            ("interesting", "INTEGER NOT NULL DEFAULT 0"),
            ("color", "TEXT NOT NULL DEFAULT ''"),
            ("duplicate_of", "INTEGER"),
        ):
            if name not in existing:
                conn.execute(f"ALTER TABLE flows ADD COLUMN {name} {definition}")
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
        cur.execute("PRAGMA busy_timeout=5000;")
        cur.execute("PRAGMA cache_size=-8192;")
        cur.execute("PRAGMA temp_store=MEMORY;")
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

    def update_scopes(self, records: Iterable[FlowRecord]) -> None:
        """Persist scope changes in one transaction.

        Scope rules can affect thousands of captured flows.  Updating each
        row through :meth:`update` used to commit once per record, which kept
        the UI thread busy long after a user edited a scope rule.
        """
        values = [(int(record.scope), record.flow_id) for record in records]
        if not values:
            return
        self._conn.executemany(
            "UPDATE flows SET scope = ? WHERE flow_id = ?", values,
        )
        self._conn.commit()

    def update_metadata(self, record: FlowRecord) -> None:
        """Persist fields edited from the history UI without rewriting bodies."""
        self._conn.execute(
            "UPDATE flows SET tags = ?, notes = ?, bookmarked = ?, interesting = ?, "
            "color = ? WHERE flow_id = ?",
            (record.tags, record.notes, int(record.bookmarked),
             int(record.interesting), record.color, record.flow_id),
        )
        self._conn.commit()

    def upsert(self, record: FlowRecord) -> int:
        """Insert if new, otherwise update. Returns the row id."""
        # One SQLite statement handles both request/response events.  This
        # removes a SELECT and avoids a race between the existence check and
        # the write when another connection is reading the history.
        values = [getattr(record, col) for col in _COLUMNS]
        placeholders = ", ".join("?" for _ in _COLUMNS)
        cols = ", ".join(_COLUMNS)
        assignments = ", ".join(
            f"{col} = excluded.{col}" for col in _COLUMNS if col != "flow_id"
        )
        row = self._conn.execute(
            f"INSERT INTO flows ({cols}) VALUES ({placeholders}) "
            f"ON CONFLICT(flow_id) DO UPDATE SET {assignments} RETURNING id",
            values,
        ).fetchone()
        self._conn.commit()
        record.id = int(row["id"])
        return record.id

    def clear(self) -> None:
        self._conn.execute("DELETE FROM flows")
        self._conn.commit()

    def cleanup(self, max_rows: int | None = None, max_age_days: int | None = None) -> int:
        """Apply retention limits and reclaim SQLite space. Returns deleted rows."""
        clauses, args = [], []
        if max_age_days is not None and max_age_days > 0:
            clauses.append("started_at < strftime('%s','now') - ? * 86400")
            args.append(int(max_age_days))
        if max_rows is not None and max_rows >= 0:
            clauses.append("id NOT IN (SELECT id FROM flows ORDER BY id DESC LIMIT ?)")
            args.append(int(max_rows))
        deleted = 0
        if not clauses:
            return 0
        cur = self._conn.execute("DELETE FROM flows WHERE " + " OR ".join(clauses), args)
        deleted = cur.rowcount
        self._conn.commit()
        self._conn.execute("PRAGMA optimize")
        self._conn.execute("VACUUM")
        return max(0, deleted)

    def mark_duplicate(self, record: FlowRecord) -> int | None:
        """Link a request to the oldest identical request/response fingerprint."""
        row = self._conn.execute(
            "SELECT id FROM flows WHERE id != ? AND method = ? AND host = ? AND path = ? "
            "AND request_body_size = ? AND response_body_size = ? ORDER BY id LIMIT 1",
            (record.id or -1, record.method, record.host, record.path,
             record.request_body_size, record.response_body_size),
        ).fetchone()
        if row:
            record.duplicate_of = int(row["id"])
            self._conn.execute("UPDATE flows SET duplicate_of=? WHERE id=?", (record.duplicate_of, record.id))
            self._conn.commit()
            return record.duplicate_of
        return None

    def save_filter(self, name: str, query: str) -> None:
        self._conn.execute("INSERT INTO saved_filters(name, query) VALUES(?, ?) "
                           "ON CONFLICT(name) DO UPDATE SET query=excluded.query", (name, query))
        self._conn.commit()

    def list_saved_filters(self) -> list[tuple[str, str]]:
        return [(r["name"], r["query"]) for r in self._conn.execute(
            "SELECT name, query FROM saved_filters ORDER BY name")]

    def delete_saved_filter(self, name: str) -> None:
        self._conn.execute("DELETE FROM saved_filters WHERE name=?", (name,))
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

    def list_summaries(self, limit: Optional[int] = None) -> list[FlowRecord]:
        """Return history metadata without materializing request/response BLOBs.

        The history and site-map tables only need metadata.  Bodies are loaded
        on selection through :meth:`body`, avoiding a large startup/scope-edit
        pause for workspaces containing many responses.
        """
        columns = ", ".join(
            "NULL AS request_body_inline" if column == "request_body_inline" else
            "NULL AS response_body_inline" if column == "response_body_inline" else
            column
            for column in ("id",) + _COLUMNS
        )
        sql = f"SELECT {columns} FROM flows ORDER BY id ASC"
        if limit is not None:
            sql += f" LIMIT {int(limit)}"
        return [self._row_to_record(row) for row in self._conn.execute(sql)]

    def body(self, row_id: int, response: bool) -> bytes | None:
        """Load an inline body only when a detail view asks for it."""
        column = "response_body_inline" if response else "request_body_inline"
        row = self._conn.execute(
            f"SELECT {column} AS body FROM flows WHERE id = ?", (row_id,)
        ).fetchone()
        return bytes(row["body"]) if row is not None and row["body"] is not None else None

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
            scope=bool(row["scope"]),
            tool=row["tool"],
            bookmarked=bool(row["bookmarked"]),
            interesting=bool(row["interesting"]),
            color=row["color"],
            duplicate_of=row["duplicate_of"],
        )

    def close(self) -> None:
        self._conn.close()
