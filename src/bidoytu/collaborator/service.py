"""Stateful OAST/Collaborator service used by the desktop backend.

Owns the active :class:`InteractshClient`, a background polling task, the list
of interactions received so far, and the list of generated callback domains.
It notifies the application when new interactions arrive so the desktop UI can
re-fetch, mirroring the ``LiveAuditService`` pattern used elsewhere.
"""
from __future__ import annotations

import asyncio
import time
from typing import Awaitable, Callable

from .client import InteractshClient, InteractshError

# Public Interactsh servers operators can pick from in the dropdown. These are
# the projectdiscovery-operated OAST endpoints; a custom server can also be
# supplied by the caller.
OAST_SERVERS: list[str] = [
    "oast.pro",
    "oast.live",
    "oast.site",
    "oast.online",
    "oast.fun",
    "oast.me",
]

# Cap retained interactions/domains so an unattended session cannot grow
# without bound.
MAX_INTERACTIONS = 2000
MAX_DOMAINS = 500
POLL_INTERVAL = 5.0


class CollaboratorService:
    """Manages a single Interactsh registration and its polling loop."""

    def __init__(self, changed: Callable[[], None], verify_tls: bool = True):
        self._changed = changed
        self._verify_tls = verify_tls
        self._client: InteractshClient | None = None
        self._poller: asyncio.Task | None = None
        self._lock = asyncio.Lock()
        self.server: str = ""
        self.domains: list[dict] = []
        self.interactions: list[dict] = []
        self.error: str = ""
        self.last_poll: float | None = None
        self._counter = 0

    @property
    def active(self) -> bool:
        return self._client is not None and self._client.registered

    def status(self) -> dict:
        return {
            "active": self.active,
            "server": self.server,
            "domains": list(self.domains),
            "interaction_count": len(self.interactions),
            "poll_interval": POLL_INTERVAL,
            "last_poll": self.last_poll,
            "error": self.error,
        }

    async def register(self, server: str, token: str = "") -> dict:
        """Register with ``server`` and start the polling loop.

        Any previous session is torn down first so only one is ever live.
        """
        server = (server or "").strip()
        if not server:
            raise InteractshError("Choose an OAST server first")
        token = (token or "").strip()
        if len(token) > 512:
            raise InteractshError("Auth token is too long")
        async with self._lock:
            await self._teardown()
            client = InteractshClient(server=server, token=token, verify_tls=self._verify_tls)
            await client.register()
            self._client = client
            self.server = client.host
            self.domains = []
            self.interactions = []
            self.error = ""
            self.last_poll = None
            self._counter = 0
            # Hand out one domain immediately so the operator has something to
            # paste as soon as registration succeeds.
            self._add_domain(client.new_domain())
            self._poller = asyncio.create_task(self._poll_loop(client))
        self._changed()
        return self.status()

    def generate_domain(self) -> dict:
        """Return a fresh unique callback domain for the active session."""
        if not self._client or not self._client.registered:
            raise InteractshError("Register with an OAST server before generating a domain")
        entry = self._add_domain(self._client.new_domain())
        self._changed()
        return entry

    def _add_domain(self, domain: str) -> dict:
        self._counter += 1
        entry = {
            "id": self._counter,
            "domain": domain,
            "created_at": time.time(),
            "hits": 0,
        }
        self.domains.insert(0, entry)
        del self.domains[MAX_DOMAINS:]
        return entry

    async def poll_now(self) -> dict:
        """Poll the server immediately instead of waiting for the interval.

        Returns the updated status so the caller can refresh right away.
        """
        client = self._client
        if not client or not client.registered:
            raise InteractshError("Register with an OAST server before polling")
        try:
            found = await client.poll()
            self.error = ""
        except InteractshError as exc:
            self.error = str(exc)
            self._changed()
            raise
        self.last_poll = time.time()
        if found:
            self._ingest(found)
        self._changed()
        return {"received": len(found), "status": self.status()}

    async def _poll_loop(self, client: InteractshClient) -> None:
        while True:
            await asyncio.sleep(POLL_INTERVAL)
            if client is not self._client:
                return
            try:
                found = await client.poll()
                self.error = ""
            except InteractshError as exc:
                self.error = str(exc)
                self._changed()
                continue
            except asyncio.CancelledError:
                raise
            self.last_poll = time.time()
            if found:
                self._ingest(found)
            self._changed()

    def _ingest(self, found: list) -> None:
        seen = {item["unique_id"] for item in self.interactions if item.get("unique_id")}
        for interaction in found:
            record = interaction.to_dict()
            uid = record.get("unique_id")
            if uid and uid in seen:
                continue
            if uid:
                seen.add(uid)
            record["received_at"] = time.time()
            self.interactions.insert(0, record)
            # Attribute the hit to the domain that matches the full id, if any.
            full = (record.get("full_id") or "").lower()
            for entry in self.domains:
                if full and full.startswith(entry["domain"].split(".")[0].lower()):
                    entry["hits"] += 1
                    break
        del self.interactions[MAX_INTERACTIONS:]

    def clear(self) -> None:
        self.interactions = []
        for entry in self.domains:
            entry["hits"] = 0
        self._changed()

    async def _teardown(self) -> None:
        if self._poller:
            self._poller.cancel()
            try:
                await self._poller
            except asyncio.CancelledError:
                pass
            self._poller = None
        if self._client:
            try:
                await self._client.deregister()
            except Exception:
                pass
            self._client = None
        self.server = ""

    async def stop(self) -> dict:
        async with self._lock:
            await self._teardown()
            self.error = ""
        self._changed()
        return self.status()

    async def close(self) -> None:
        """Shutdown hook: release the session without emitting UI updates."""
        async with self._lock:
            await self._teardown()
