"""Browse and fetch wordlists from the SecLists project on demand.

`SecLists <https://github.com/danielmiessler/SecLists>`_ is a large collection
of security wordlists. Cloning the whole repository is wasteful when a user only
wants one or two lists, so this module lets the UI:

* list every wordlist in the repository (one cheap GitHub API call), grouped by
  its directory, without downloading any content;
* download a single wordlist on demand into a local, shared cache; and
* report which lists have already been downloaded so they can be surfaced first.

Downloaded lists live under a machine-wide cache directory (shared across
workspaces) so a list fetched once is instantly reusable everywhere. Everything
here is synchronous and network calls are expected to run on a worker thread -
the Qt dialog owns the threading and marshals results back to the UI.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

# The repository is browsed through the Git "trees" API (a single recursive
# call returns every path) and individual files are pulled from the raw CDN.
_OWNER = "danielmiessler"
_REPO = "SecLists"
_DEFAULT_REF = "master"
_TREE_API = "https://api.github.com/repos/{owner}/{repo}/git/trees/{ref}?recursive=1"
_RAW_URL = "https://raw.githubusercontent.com/{owner}/{repo}/{ref}/{path}"

# Only surface files that are plausibly usable as payload lists. SecLists holds
# a lot of supporting material (images, scripts, PDFs) we do not want to list.
_LIST_SUFFIXES = (".txt", ".lst", ".list", ".csv", ".json", ".dic", ".fuzz")

# Be polite / avoid pathological UI: skip files larger than this in the browser
# (they are still downloadable if selected, this only trims the initial listing).
_MAX_LISTED_BYTES = 64 * 1024 * 1024  # 64 MiB

_USER_AGENT = "Bidoytu-SecLists-Browser"
_HTTP_TIMEOUT = 30.0


@dataclass(slots=True, frozen=True)
class WordlistEntry:
    """A single wordlist available in the SecLists repository.

    Attributes:
        path: Repository-relative path, e.g. ``Passwords/darkweb2017-top100.txt``.
        size: File size in bytes as reported by the tree API (0 if unknown).
    """

    path: str
    size: int = 0

    @property
    def name(self) -> str:
        """The file name without its directory."""
        return self.path.rsplit("/", 1)[-1]

    @property
    def directory(self) -> str:
        """The containing directory path (``""`` for a top-level file)."""
        return self.path.rsplit("/", 1)[0] if "/" in self.path else ""


def default_cache_dir() -> Path:
    """Return the shared, machine-wide directory for downloaded wordlists.

    Wordlists are not workspace-specific, so they are cached once per machine
    (next to the app's data directory) and reused across every workspace.
    """
    if os.name == "nt":  # Windows
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        return Path(base) / "Bidoytu" / "seclists"
    xdg = os.environ.get("XDG_DATA_HOME")
    if xdg:
        return Path(xdg) / "bidoytu" / "seclists"
    return Path.home() / ".local" / "share" / "bidoytu" / "seclists"


class SecListsRepository:
    """Read-only view over the SecLists repo plus a local download cache."""

    def __init__(self, cache_dir: Path | None = None, ref: str = _DEFAULT_REF) -> None:
        self.cache_dir = Path(cache_dir) if cache_dir else default_cache_dir()
        self.ref = ref

    # -- remote listing -------------------------------------------------------

    def fetch_index(self) -> list[WordlistEntry]:
        """Return every wordlist in the repository (no file content fetched).

        Makes a single recursive Git-trees API request. Raises on network or
        HTTP errors so the caller can surface a message.
        """
        import httpx

        url = _TREE_API.format(owner=_OWNER, repo=_REPO, ref=self.ref)
        headers = {"User-Agent": _USER_AGENT, "Accept": "application/vnd.github+json"}
        # An optional token lifts GitHub's low anonymous rate limit.
        token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"

        with httpx.Client(timeout=_HTTP_TIMEOUT, follow_redirects=True) as client:
            resp = client.get(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        entries: list[WordlistEntry] = []
        for node in data.get("tree", []):
            if node.get("type") != "blob":
                continue
            path = node.get("path", "")
            if not path or not self._is_wordlist(path):
                continue
            size = int(node.get("size", 0) or 0)
            if size and size > _MAX_LISTED_BYTES:
                continue
            entries.append(WordlistEntry(path=path, size=size))
        entries.sort(key=lambda e: e.path.lower())
        return entries

    @staticmethod
    def _is_wordlist(path: str) -> bool:
        lower = path.lower()
        # Skip repo metadata / docs that happen to be .txt.
        if lower.endswith("readme.txt") or lower.startswith(".github/"):
            return False
        return lower.endswith(_LIST_SUFFIXES)

    # -- local cache ----------------------------------------------------------

    def local_path(self, path: str) -> Path:
        """Where a given repository path is (or would be) cached locally."""
        # Preserve the repo's directory layout so names never collide.
        return self.cache_dir.joinpath(*path.split("/"))

    def is_downloaded(self, path: str) -> bool:
        """Whether the wordlist at *path* already exists in the local cache."""
        local = self.local_path(path)
        return local.is_file() and local.stat().st_size >= 0

    def downloaded_paths(self) -> list[str]:
        """Return repo-relative paths of every wordlist already cached locally."""
        if not self.cache_dir.is_dir():
            return []
        found: list[str] = []
        for file_path in self.cache_dir.rglob("*"):
            if file_path.is_file():
                rel = file_path.relative_to(self.cache_dir).as_posix()
                found.append(rel)
        found.sort(key=str.lower)
        return found

    def download(self, path: str, *, force: bool = False) -> Path:
        """Download the wordlist at *path* into the cache and return its path.

        If the file is already cached and *force* is false, the network is not
        touched. Raises on network or HTTP errors.
        """
        import httpx

        local = self.local_path(path)
        if local.is_file() and not force:
            return local

        url = _RAW_URL.format(owner=_OWNER, repo=_REPO, ref=self.ref, path=path)
        headers = {"User-Agent": _USER_AGENT}
        local.parent.mkdir(parents=True, exist_ok=True)
        tmp = local.with_suffix(local.suffix + ".part")
        with httpx.Client(timeout=_HTTP_TIMEOUT, follow_redirects=True) as client:
            with client.stream("GET", url, headers=headers) as resp:
                resp.raise_for_status()
                with tmp.open("wb") as fh:
                    for chunk in resp.iter_bytes(chunk_size=64 * 1024):
                        fh.write(chunk)
        tmp.replace(local)
        return local

    def read_text(self, path: str) -> str:
        """Return the cached wordlist's contents, downloading it if necessary."""
        local = self.download(path)
        return local.read_text(encoding="utf-8", errors="replace")
