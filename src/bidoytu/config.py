"""Application configuration and filesystem paths.

Everything the app writes (SQLite DB, large request/response bodies) lives under
a single data directory so it is easy to locate, back up, or clear.
"""
from __future__ import annotations

import json
import os
import re
from functools import lru_cache
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
    """Listen and target-scope settings for the mitmproxy engine."""

    listen_host: str = "127.0.0.1"
    listen_port: int = 8080
    http2: bool = True
    # Browser interception should remain usable with sites that publish an
    # incomplete legacy chain. The setting is visible in Proxy Settings so
    # strict upstream verification can be restored when required.
    ssl_insecure: bool = True
    include_scope: list[str] = field(default_factory=list)
    exclude_scope: list[str] = field(default_factory=list)
    include_paths: list[str] = field(default_factory=list)
    exclude_paths: list[str] = field(default_factory=list)
    include_regex: list[str] = field(default_factory=list)
    exclude_regex: list[str] = field(default_factory=list)
    sitemaps: list[str] = field(default_factory=list)


def _normalise_scope_entry(value: str) -> str:
    """Return a host-pattern suitable for scope matching.

    Scope entries are intentionally host-only.  Be forgiving of values pasted
    from a browser or Burp export by removing a scheme, path, and port before
    storing the pattern.
    """
    value = value.strip().lower()
    if not value:
        return ""
    if "://" in value:
        value = value.split("://", 1)[1]
    value = value.split("/", 1)[0]
    if value.startswith("*."):
        value = value[2:]
    if value.startswith("."):
        value = value[1:]
    if value.count(":") == 1:
        value = value.rsplit(":", 1)[0]
    return value.strip(".")


@lru_cache(maxsize=512)
def _cached_normalise_scope_entry(value: str) -> str:
    """Cache normalized scope values used for every captured request."""
    return _normalise_scope_entry(value)


@lru_cache(maxsize=256)
def _cached_scope_regex(pattern: str):
    """Compile scope regexes once; invalid expressions remain non-matching."""
    try:
        return re.compile(pattern, re.IGNORECASE)
    except re.error:
        return None


def host_matches_scope(
    host: str, include_scope: list[str] | tuple[str, ...],
    exclude_scope: list[str] | tuple[str, ...], path: str = "/",
    include_paths: list[str] | tuple[str, ...] = (),
    exclude_paths: list[str] | tuple[str, ...] = (),
    include_regex: list[str] | tuple[str, ...] = (),
    exclude_regex: list[str] | tuple[str, ...] = (),
) -> bool:
    """Return whether *host* is in the configured target scope.

    A host entry matches the host itself and all of its subdomains, so
    ``example.com`` covers ``api.example.com``.  Exclusions always win.  With
    no include entries everything is included unless explicitly excluded.
    """
    candidate = _cached_normalise_scope_entry(str(host))
    if not candidate:
        return False

    def matches(pattern: str) -> bool:
        normalised = _cached_normalise_scope_entry(str(pattern))
        return bool(normalised) and (
            candidate == normalised or candidate.endswith("." + normalised)
        )

    include_patterns = [pattern for pattern in include_scope if str(pattern).strip()]
    exclude_patterns = [pattern for pattern in exclude_scope if str(pattern).strip()]
    if any(matches(pattern) for pattern in exclude_patterns):
        return False
    if include_patterns and not any(matches(pattern) for pattern in include_patterns):
        return False

    request_path = path or "/"
    if any(request_path.startswith(str(pattern).strip()) for pattern in exclude_paths if str(pattern).strip()):
        return False
    if include_paths and not any(request_path.startswith(str(pattern).strip()) for pattern in include_paths if str(pattern).strip()):
        return False

    def regex_matches(pattern: str) -> bool:
        compiled = _cached_scope_regex(str(pattern))
        return bool(compiled and compiled.search(f"{candidate}{request_path}"))

    if any(regex_matches(pattern) for pattern in exclude_regex if str(pattern).strip()):
        return False
    return not include_regex or any(regex_matches(pattern) for pattern in include_regex if str(pattern).strip())


# Free, public Interactsh servers operated by ProjectDiscovery. They are tried
# in order at registration time; the first that accepts the registration wins.
# Users can add their own (self-hosted) server in the Collaborator tab.
DEFAULT_OAST_SERVERS = (
    "oast.pro",
    "oast.live",
    "oast.site",
    "oast.online",
    "oast.fun",
    "oast.me",
)


@dataclass(slots=True)
class CollaboratorConfig:
    """Settings for the Collaborator (out-of-band interaction) feature.

    Attributes:
        servers: Ordered list of Interactsh server hostnames to try when
            registering. The first entry is treated as the preferred server.
        token: Optional ``Authorization`` token for protected / self-hosted
            servers (leave empty for the public ones).
        poll_interval_secs: How often to poll the server for new interactions.
    """

    servers: list[str] = field(default_factory=lambda: list(DEFAULT_OAST_SERVERS))
    token: str = ""
    poll_interval_secs: int = 10
    allow_http_fallback: bool = False
    max_interactions: int = 10000


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
    ca_dir: Path | None = None
    proxy: ProxyConfig = field(default_factory=ProxyConfig)
    collaborator: CollaboratorConfig = field(default_factory=CollaboratorConfig)
    body_inline_limit: int = 64 * 1024  # 64 KiB
    history_max_rows: int = 0  # 0 means unlimited
    history_max_age_days: int = 0  # 0 means unlimited

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
    def intruder_attack_path(self) -> Path:
        """JSON file holding the last Intruder attack config across restarts."""
        return self.data_dir / "intruder_attack.json"

    @property
    def proxy_scope_path(self) -> Path:
        """JSON file holding the Target scope for this workspace."""
        return self.data_dir / "proxy_scope.json"

    @property
    def collaborator_state_path(self) -> Path:
        """JSON file holding Collaborator session state across restarts.

        Stores the active Interactsh session (server, correlation id, keys),
        generated payloads, and captured interactions so a running OAST session
        can be resumed after a restart.
        """
        return self.data_dir / "collaborator.json"

    @property
    def confdir(self) -> Path:
        """Directory where mitmproxy stores its generated CA and certs.

        We keep it under Bidoytu's data dir (instead of the default
        ``~/.mitmproxy``) so the CA is predictable and easy to export.
        """
        # The CA belongs to the Bidoytu installation, not an individual
        # workspace. This keeps browser trust stable across sessions.
        return self.ca_dir or (self.data_dir / "ca")

    @property
    def ca_cert_pem(self) -> Path:
        """PEM-encoded CA certificate (for Firefox, curl, most Linux tools)."""
        return self.confdir / "mitmproxy-ca-cert.pem"

    @property
    def ca_cert_cer(self) -> Path:
        """DER/.cer CA certificate (convenient for the Windows cert store)."""
        return self.confdir / "mitmproxy-ca-cert.cer"

    @property
    def browser_profiles_dir(self) -> Path:
        """Profiles used by Browser Integration launches."""
        return self.data_dir / "browser-profiles"

    def ensure_dirs(self) -> None:
        """Create the data, body, and CA directories if they do not exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.bodies_dir.mkdir(parents=True, exist_ok=True)
        self.confdir.mkdir(parents=True, exist_ok=True)
        self.browser_profiles_dir.mkdir(parents=True, exist_ok=True)

    def load_proxy_scope(self) -> None:
        """Restore Target scope, tolerating files from older versions."""
        try:
            data = json.loads(self.proxy_scope_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        if not isinstance(data, dict):
            return
        for key in ("include_scope", "exclude_scope", "include_paths", "exclude_paths",
                    "include_regex", "exclude_regex", "sitemaps"):
            values = data.get(key, [])
            if isinstance(values, list):
                setattr(
                    self.proxy,
                    key,
                    [str(value) for value in values if str(value).strip()],
                )

    def save_proxy_scope(self) -> None:
        """Persist the current Target scope inside the active workspace."""
        self.proxy_scope_path.write_text(
            json.dumps(
                {
                    "include_scope": self.proxy.include_scope,
                    "exclude_scope": self.proxy.exclude_scope,
                    "include_paths": self.proxy.include_paths,
                    "exclude_paths": self.proxy.exclude_paths,
                    "include_regex": self.proxy.include_regex,
                    "exclude_regex": self.proxy.exclude_regex,
                    "sitemaps": self.proxy.sitemaps,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
