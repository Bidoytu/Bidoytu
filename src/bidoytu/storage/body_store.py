"""On-disk store for large request/response bodies.

Rather than storing large payloads as SQLite BLOBs (which bloats the DB file and
hurts query performance), bodies over a threshold are written to individual
files and referenced by a relative path. Files are content-addressed by a hash
so identical bodies are de-duplicated automatically.
"""
from __future__ import annotations

import hashlib
from pathlib import Path


class BodyStore:
    """Content-addressed file store for body payloads.

    Files are sharded into subdirectories by the first two hex characters of
    their SHA-256 digest to avoid huge flat directories.
    """

    def __init__(self, root: Path) -> None:
        self._root = Path(root)
        self._root.mkdir(parents=True, exist_ok=True)

    def store(self, data: bytes) -> str:
        """Write ``data`` to the store and return its relative path.

        Identical content maps to the same path, so repeated writes are cheap
        and idempotent.
        """
        digest = hashlib.sha256(data).hexdigest()
        rel = Path(digest[:2]) / digest[2:]
        abs_path = self._root / rel
        if not abs_path.exists():
            abs_path.parent.mkdir(parents=True, exist_ok=True)
            tmp = abs_path.with_suffix(".tmp")
            tmp.write_bytes(data)
            tmp.replace(abs_path)  # atomic on same filesystem
        return rel.as_posix()

    def load(self, rel_path: str) -> bytes:
        """Read body content previously returned by :meth:`store`."""
        return (self._root / rel_path).read_bytes()

    def exists(self, rel_path: str) -> bool:
        return (self._root / rel_path).exists()
