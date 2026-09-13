"""Application configuration and filesystem paths.

Everything the app writes (SQLite DB, large request/response bodies) lives under
a single data directory so it is easy to locate, back up, or clear.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _default_data_dir() -> Path:
    """Return a per-user, per-OS data directory for Bidoytu."""
    if os.name == "nt":  # Windows
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        return Path(base) / "Bidoytu"
    # macOS / Linux
    xdg = os.environ.get("XDG_DATA_HOME")
    if xdg:
        return Path(xdg) / "bidoytu"
    return Path.home() / ".local" / "share" / "bidoytu"


@dataclass(slots=True)
class ProxyConfig:
    """Listen settings for the mitmproxy engine."""

    listen_host: str = "127.0.0.1"
    listen_port: int = 8080
    http2: bool = True


@dataclass(slots=True)
class AppConfig:
    """Top-level runtime configuration.

    Attributes:
        data_dir: Root directory for all persisted state.
        proxy: Proxy listen configuration.
        body_inline_limit: Bodies at or below this size (bytes) are stored
            inline in SQLite; larger bodies are written to the file store and
            referenced by path.
    """

    data_dir: Path = field(default_factory=_default_data_dir)
    proxy: ProxyConfig = field(default_factory=ProxyConfig)
    body_inline_limit: int = 64 * 1024  # 64 KiB

    @property
    def db_path(self) -> Path:
        return self.data_dir / "bidoytu.db"

    @property
    def bodies_dir(self) -> Path:
        return self.data_dir / "bodies"

    @property
    def repeater_sessions_path(self) -> Path:
        """JSON file holding persisted Repeater sessions across restarts."""
        return self.data_dir / "repeater_sessions.json"

    @property
    def confdir(self) -> Path:
        """Directory where mitmproxy stores its generated CA and certs.

        We keep it under Bidoytu's data dir (instead of the default
        ``~/.mitmproxy``) so the CA is predictable and easy to export.
        """
        return self.data_dir / "ca"

    @property
    def ca_cert_pem(self) -> Path:
        """PEM-encoded CA certificate (for Firefox, curl, most Linux tools)."""
        return self.confdir / "mitmproxy-ca-cert.pem"

    @property
    def ca_cert_cer(self) -> Path:
        """DER/.cer CA certificate (convenient for the Windows cert store)."""
        return self.confdir / "mitmproxy-ca-cert.cer"

    def ensure_dirs(self) -> None:
        """Create the data, body, and CA directories if they do not exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.bodies_dir.mkdir(parents=True, exist_ok=True)
        self.confdir.mkdir(parents=True, exist_ok=True)
