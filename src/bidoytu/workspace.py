"""Local, Burp-style workspace management.

Each workspace owns its SQLite history, body store, and tool state.  The
registry and archives intentionally use only local files; no account or remote
service is involved.
"""
from __future__ import annotations

import json
import shutil
import uuid
import zipfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


ARCHIVE_FORMAT = "bidoytu-workspaces"
ARCHIVE_VERSION = 1


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class Workspace:
    """A locally stored workspace available to open."""

    id: str
    name: str
    created_at: str
    updated_at: str
    protected: bool = False

    @property
    def is_protected(self) -> bool:
        """Whether this is the one-time legacy workspace kept as a safeguard."""
        # Name fallback protects installations migrated before this flag existed.
        return self.protected or self.name == "Previous session"


class WorkspaceManager:
    """Maintain the local workspace registry and portable ZIP archives."""

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = Path(data_dir)
        self.sessions_dir = self.data_dir / "sessions"
        self.registry_path = self.data_dir / "sessions.json"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self._migrate_legacy_data()

    def list(self) -> list[Workspace]:
        entries = self._read_registry()
        result: list[Workspace] = []
        for item in entries:
            try:
                workspace = Workspace(**item)
            except TypeError:
                continue
            if self.path_for(workspace).is_dir():
                result.append(workspace)
        return sorted(result, key=lambda item: item.updated_at, reverse=True)

    def create(self, name: str, *, protected: bool = False) -> Workspace:
        clean_name = name.strip() or "New session"
        stamp = _now()
        workspace = Workspace(
            id=uuid.uuid4().hex,
            name=clean_name,
            created_at=stamp,
            updated_at=stamp,
            protected=protected,
        )
        self.path_for(workspace).mkdir(parents=True, exist_ok=False)
        entries = self._read_registry()
        entries.append(asdict(workspace))
        self._write_registry(entries)
        return workspace

    def path_for(self, workspace: Workspace) -> Path:
        return self.sessions_dir / workspace.id

    def touch(self, workspace: Workspace) -> None:
        entries = self._read_registry()
        for entry in entries:
            if entry.get("id") == workspace.id:
                entry["updated_at"] = _now()
                workspace.updated_at = entry["updated_at"]
                self._write_registry(entries)
                return

    def discard(self, workspace: Workspace) -> None:
        """Remove a workspace and all of its locally stored data."""
        if workspace.is_protected:
            return
        path = self.path_for(workspace)
        if path.is_dir():
            shutil.rmtree(path)
        self._write_registry([
            entry for entry in self._read_registry()
            if entry.get("id") != workspace.id
        ])

    def clear_all(self) -> None:
        """Remove every deletable workspace while keeping the legacy recovery one."""
        entries = self._read_registry()
        kept: list[dict] = []
        for entry in entries:
            try:
                workspace = Workspace(**entry)
            except TypeError:
                continue
            if workspace.is_protected:
                kept.append(asdict(workspace))
                continue
            path = self.path_for(workspace)
            if path.is_dir():
                shutil.rmtree(path)
        self._write_registry(kept)

    def export_all(self, archive_path: Path) -> None:
        """Write every saved workspace to one portable ZIP archive."""
        archive_path = Path(archive_path)
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        manifest = {
            "format": ARCHIVE_FORMAT,
            "version": ARCHIVE_VERSION,
            "sessions": [asdict(workspace) for workspace in self.list()],
        }
        with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("manifest.json", json.dumps(manifest, indent=2))
            for workspace in self.list():
                root = self.path_for(workspace)
                for file_path in root.rglob("*"):
                    if file_path.is_file():
                        archive.write(
                            file_path,
                            Path("sessions") / workspace.id / file_path.relative_to(root),
                        )

    def import_all(self, archive_path: Path) -> list[Workspace]:
        """Merge all valid workspaces in a Bidoytu archive into this machine."""
        with zipfile.ZipFile(archive_path) as archive:
            try:
                manifest = json.loads(archive.read("manifest.json"))
            except (KeyError, json.JSONDecodeError) as exc:
                raise ValueError("This is not a valid Bidoytu workspace archive.") from exc
            if manifest.get("format") != ARCHIVE_FORMAT:
                raise ValueError("This archive is not a Bidoytu workspace export.")

            imported: list[Workspace] = []
            entries = self._read_registry()
            known_ids = {entry.get("id") for entry in entries}
            for item in manifest.get("sessions", []):
                try:
                    workspace = Workspace(**item)
                except TypeError:
                    continue
                # Preserve all sessions even when an archive was imported before.
                if workspace.id in known_ids or self.path_for(workspace).exists():
                    workspace.id = uuid.uuid4().hex
                    workspace.name = self._unique_name(workspace.name, entries)
                target = self.path_for(workspace)
                target.mkdir(parents=True, exist_ok=False)
                prefix = f"sessions/{item.get('id', '')}/"
                for member in archive.infolist():
                    if member.is_dir() or not member.filename.startswith(prefix):
                        continue
                    relative = Path(member.filename[len(prefix):])
                    if not relative.parts or relative.is_absolute() or ".." in relative.parts:
                        continue
                    destination = target / relative
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    with archive.open(member) as source, destination.open("wb") as output:
                        shutil.copyfileobj(source, output)
                entries.append(asdict(workspace))
                known_ids.add(workspace.id)
                imported.append(workspace)
            self._write_registry(entries)
            return imported

    def _read_registry(self) -> list[dict]:
        try:
            data = json.loads(self.registry_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        return data if isinstance(data, list) else []

    def _write_registry(self, entries: list[dict]) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        temp = self.registry_path.with_suffix(".tmp")
        temp.write_text(json.dumps(entries, indent=2), encoding="utf-8")
        temp.replace(self.registry_path)

    def _unique_name(self, name: str, entries: list[dict]) -> str:
        used = {str(entry.get("name", "")).casefold() for entry in entries}
        if name.casefold() not in used:
            return name
        index = 2
        while f"{name} ({index})".casefold() in used:
            index += 1
        return f"{name} ({index})"

    def _migrate_legacy_data(self) -> None:
        """Place a pre-workspace installation into one recoverable session."""
        if self.registry_path.exists():
            return
        legacy_names = (
            "bidoytu.db", "bidoytu.db-wal", "bidoytu.db-shm", "bodies",
            "repeater_sessions.json", "intruder_attack.json", "collaborator.json",
        )
        if not any((self.data_dir / name).exists() for name in legacy_names):
            return
        workspace = self.create("Previous session", protected=True)
        destination = self.path_for(workspace)
        for name in legacy_names:
            source = self.data_dir / name
            if source.exists():
                shutil.move(str(source), str(destination / name))
