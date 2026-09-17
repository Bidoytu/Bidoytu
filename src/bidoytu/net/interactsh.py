"""Interactsh (OAST) client for the Collaborator feature.

This is a small, Qt-free implementation of the `Interactsh
<https://github.com/projectdiscovery/interactsh>`_ protocol used by Burp's
Collaborator equivalent. It lets Bidoytu detect *out-of-band* interactions
(blind SSRF, blind XSS, blind SQLi, XXE, log4shell, etc.) by handing out unique
payload hostnames and polling a public (or self-hosted) Interactsh server for
any DNS / HTTP / SMTP callbacks those hostnames trigger.

Design notes
------------
* All network I/O goes through the shared :class:`AsyncHttpSender` (httpx on a
  background event loop), so the client stays consistent with Repeater /
  Intruder and never blocks the Qt UI thread. The sender's callbacks run on the
  sender thread, so the *UI* layer (CollaboratorTab) is responsible for
  marshalling results back to the UI thread via a queued signal.
* Cryptography is done locally with ``cryptography``:
  - Register uploads an RSA-2048 public key.
  - Poll returns AES keys wrapped with RSA-OAEP(SHA-256) plus AES-256-CFB
    ciphertext (IV = first 16 bytes). We unwrap + decrypt each record.
* Correlation IDs are XID strings (the server parses them as XIDs), generated
  locally so we don't need the ``epyxid`` dependency.

The protocol details mirror the reference clients from ProjectDiscovery and
theori-io/python-interactsh.
"""
from __future__ import annotations

import base64
import json
import os
import secrets
import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable, Optional
from urllib.parse import urlencode, urlsplit

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from bidoytu.net.async_sender import AsyncHttpSender, HttpResult

CORRELATION_ID_LENGTH = 20
NONCE_LENGTH = 13

# XID uses a base32-hex-like alphabet ("Crockford"-ish, lowercase, digits 0-9
# then a-v). A raw XID is 12 bytes encoded to 20 chars.
_XID_ENCODING = "0123456789abcdefghijklmnopqrstuv"


def generate_xid() -> str:
    """Return a 20-char XID string.

    XID layout: 4-byte time, 3-byte machine id, 2-byte pid, 3-byte counter.
    The server only needs a syntactically valid, unique XID, so we fill the
    machine/pid/counter with random bytes rather than real values.
    """
    raw = bytearray(12)
    now = int(time.time())
    raw[0] = (now >> 24) & 0xFF
    raw[1] = (now >> 16) & 0xFF
    raw[2] = (now >> 8) & 0xFF
    raw[3] = now & 0xFF
    raw[4:12] = secrets.token_bytes(8)
    return _encode_xid(bytes(raw))


def _encode_xid(raw: bytes) -> str:
    """Encode 12 raw bytes into the 20-char XID base32 representation."""
    enc = _XID_ENCODING
    b = raw
    return (
        enc[b[0] >> 3]
        + enc[((b[0] << 2) | (b[1] >> 6)) & 0x1F]
        + enc[(b[1] >> 1) & 0x1F]
        + enc[((b[1] << 4) | (b[2] >> 4)) & 0x1F]
        + enc[((b[2] << 1) | (b[3] >> 7)) & 0x1F]
        + enc[(b[3] >> 2) & 0x1F]
        + enc[((b[3] << 3) | (b[4] >> 5)) & 0x1F]
        + enc[b[4] & 0x1F]
        + enc[b[5] >> 3]
        + enc[((b[5] << 2) | (b[6] >> 6)) & 0x1F]
        + enc[(b[6] >> 1) & 0x1F]
        + enc[((b[6] << 4) | (b[7] >> 4)) & 0x1F]
        + enc[((b[7] << 1) | (b[8] >> 7)) & 0x1F]
        + enc[(b[8] >> 2) & 0x1F]
        + enc[((b[8] << 3) | (b[9] >> 5)) & 0x1F]
        + enc[b[9] & 0x1F]
        + enc[b[10] >> 3]
        + enc[((b[10] << 2) | (b[11] >> 6)) & 0x1F]
        + enc[(b[11] >> 1) & 0x1F]
        + enc[(b[11] << 4) & 0x1F]
    )


@dataclass(slots=True)
class Interaction:
    """A single out-of-band interaction reported by the server."""

    protocol: str = ""
    unique_id: str = ""
    full_id: str = ""
    q_type: str = ""
    raw_request: str = ""
    raw_response: str = ""
    smtp_from: str = ""
    remote_address: str = ""
    timestamp: str = ""

    @classmethod
    def from_json(cls, text: str) -> "Interaction":
        data = json.loads(text)
        return cls(
            protocol=data.get("protocol", "") or "",
            unique_id=data.get("unique-id", "") or "",
            full_id=data.get("full-id", "") or "",
            q_type=data.get("q-type", "") or "",
            raw_request=data.get("raw-request", "") or "",
            raw_response=data.get("raw-response", "") or "",
            smtp_from=data.get("smtp-from", "") or "",
            remote_address=data.get("remote-address", "") or "",
            timestamp=data.get("timestamp", "") or _now_iso(),
        )

    def to_dict(self) -> dict:
        return {
            "protocol": self.protocol,
            "unique-id": self.unique_id,
            "full-id": self.full_id,
            "q-type": self.q_type,
            "raw-request": self.raw_request,
            "raw-response": self.raw_response,
            "smtp-from": self.smtp_from,
            "remote-address": self.remote_address,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Interaction":
        return cls(
            protocol=data.get("protocol", ""),
            unique_id=data.get("unique-id", ""),
            full_id=data.get("full-id", ""),
            q_type=data.get("q-type", ""),
            raw_request=data.get("raw-request", ""),
            raw_response=data.get("raw-response", ""),
            smtp_from=data.get("smtp-from", ""),
            remote_address=data.get("remote-address", ""),
            timestamp=data.get("timestamp", ""),
        )


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class SessionInfo:
    """Everything needed to resume / persist a registered session."""

    server: str = ""            # e.g. "https://oast.pro"
    correlation_id: str = ""
    secret_key: str = ""
    private_key_b64: str = ""   # base64 DER PKCS8
    public_key_b64: str = ""    # base64 PEM SubjectPublicKeyInfo
    token: str = ""


class InteractshError(Exception):
    """Raised for registration / polling / crypto failures."""


class InteractshClient:
    """Register with, generate payloads for, and poll an Interactsh server.

    The client is deliberately callback-based to match :class:`AsyncHttpSender`.
    Register and poll take completion callbacks that fire on the *sender*
    thread; higher layers marshal to the UI thread.
    """

    def __init__(self, sender: AsyncHttpSender) -> None:
        self._sender = sender
        self._private_key: Optional[rsa.RSAPrivateKey] = None
        self._public_key_b64 = ""
        self._server = ""          # full base URL incl. scheme, no trailing /
        self._correlation_id = ""
        self._secret = ""
        self._token = ""
        self._registered = False
        self._lock = threading.Lock()

    # -- state ---------------------------------------------------------------

    @property
    def registered(self) -> bool:
        return self._registered

    @property
    def server(self) -> str:
        return self._server

    @property
    def correlation_id(self) -> str:
        return self._correlation_id

    def session_info(self) -> Optional[SessionInfo]:
        if not self._registered or self._private_key is None:
            return None
        der = self._private_key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        return SessionInfo(
            server=self._server,
            correlation_id=self._correlation_id,
            secret_key=self._secret,
            private_key_b64=base64.b64encode(der).decode("ascii"),
            public_key_b64=self._public_key_b64,
            token=self._token,
        )

    # -- registration --------------------------------------------------------

    def register(
        self,
        servers: list[str],
        token: str,
        on_done: Callable[[bool, str], None],
        *,
        allow_http_fallback: bool = True,
    ) -> None:
        """Generate a keypair and register against the first working server.

        ``servers`` is an ordered list of hostnames or URLs; each is tried in
        turn (HTTPS, then HTTP fallback). ``on_done(ok, message)`` fires on the
        sender thread when registration finishes (or all servers fail).
        """
        self._private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=default_backend()
        )
        pub_pem = self._private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        self._public_key_b64 = base64.b64encode(pub_pem).decode("ascii")
        self._correlation_id = generate_xid()[:CORRELATION_ID_LENGTH]
        self._secret = str(uuid.uuid4())
        self._token = token or ""

        # Build the ordered list of candidate base URLs (https first, then an
        # http fallback for each host that was given without a scheme).
        candidates: list[str] = []
        for entry in servers:
            entry = entry.strip()
            if not entry:
                continue
            if entry.startswith(("http://", "https://")):
                candidates.append(entry.rstrip("/"))
            else:
                candidates.append(f"https://{entry}".rstrip("/"))
                if allow_http_fallback:
                    candidates.append(f"http://{entry}".rstrip("/"))

        if not candidates:
            on_done(False, "No Interactsh servers configured")
            return

        payload = json.dumps({
            "public-key": self._public_key_b64,
            "secret-key": self._secret,
            "correlation-id": self._correlation_id,
        }).encode("utf-8")

        self._try_register(candidates, 0, payload, on_done, [])

    def _try_register(
        self,
        candidates: list[str],
        index: int,
        payload: bytes,
        on_done: Callable[[bool, str], None],
        failures: list[str],
    ) -> None:
        if index >= len(candidates):
            detail = "; ".join(failures[-3:])
            message = "Could not register with any Interactsh server"
            if detail:
                message += f": {detail}"
            on_done(False, message)
            return
        base = candidates[index]
        headers = [("Content-Type", "application/json")]
        if self._token:
            headers.append(("Authorization", self._token))

        def _cb(result: HttpResult, base=base) -> None:
            ok, done, detail = self._handle_register_result(base, result)
            if done:
                on_done(ok, base if ok else detail)
                return
            failures.append(f"{base}: {detail}")
            # Try the next candidate.
            self._try_register(candidates, index + 1, payload, on_done, failures)

        self._sender.send(
            "POST", f"{base}/register", headers, payload, _cb,
            verify=base.startswith("https://"), follow_redirects=False,
        )

    def _handle_register_result(
        self, base: str, result: HttpResult
    ) -> tuple[bool, bool, str]:
        """Return ``(ok, done, detail)`` for one registration attempt."""
        if not result.ok:
            return (False, False, result.error or "network error")
        if result.status_code == 401:
            # Auth failure is terminal; more servers won't help with this token.
            return (False, True, f"{base} returned HTTP 401 (authentication failed)")
        if result.status_code != 200:
            return (False, False, f"HTTP {result.status_code}")
        try:
            data = json.loads(result.body.decode("utf-8", errors="replace"))
        except (ValueError, UnicodeError):
            return (False, False, "invalid JSON response")
        if data.get("message") == "registration successful":
            with self._lock:
                self._server = base
                self._registered = True
            return (True, True, "registration successful")
        return (False, False, str(data.get("message") or "unexpected registration response"))

    def keep_alive(self, on_done: Callable[[bool, str], None]) -> None:
        """Refresh the server-side session without generating a new identity."""
        if not self._registered or not self._server:
            on_done(False, "not registered")
            return
        payload = json.dumps({
            "public-key": self._public_key_b64,
            "secret-key": self._secret,
            "correlation-id": self._correlation_id,
        }).encode("utf-8")
        headers = [("Content-Type", "application/json")]
        if self._token:
            headers.append(("Authorization", self._token))

        def _cb(result: HttpResult) -> None:
            if not result.ok:
                on_done(False, result.error or "keep-alive failed")
            elif result.status_code == 401:
                with self._lock:
                    self._registered = False
                on_done(False, "authentication failed")
            elif result.status_code not in (200, 400):
                if result.status_code == 404:
                    with self._lock:
                        self._registered = False
                on_done(False, f"keep-alive returned {result.status_code}")
            else:
                on_done(True, "")

        self._sender.send(
            "POST", f"{self._server}/register", headers, payload, _cb,
            verify=self._server.startswith("https://"), follow_redirects=False,
        )

    def restore(self, info: SessionInfo, on_done: Callable[[bool, str], None]) -> None:
        """Restore a persisted session and re-register to keep it alive."""
        try:
            der = base64.b64decode(info.private_key_b64)
            key = serialization.load_der_private_key(
                der, password=None, backend=default_backend()
            )
            if not isinstance(key, rsa.RSAPrivateKey):
                raise InteractshError("stored key is not RSA")
            self._private_key = key
        except Exception as exc:  # noqa: BLE001 - corrupt state is non-fatal
            on_done(False, f"Could not restore session: {exc}")
            return

        self._public_key_b64 = info.public_key_b64
        self._correlation_id = info.correlation_id
        self._secret = info.secret_key
        self._token = info.token or ""
        self._server = info.server.rstrip("/")

        payload = json.dumps({
            "public-key": self._public_key_b64,
            "secret-key": self._secret,
            "correlation-id": self._correlation_id,
        }).encode("utf-8")
        headers = [("Content-Type", "application/json")]
        if self._token:
            headers.append(("Authorization", self._token))

        def _cb(result: HttpResult) -> None:
            # Even if re-register fails (session may already be active), we keep
            # the restored identity so polling can continue.
            ok = result.ok and result.status_code in (200, 400)
            with self._lock:
                self._registered = True
            on_done(ok, self._server)

        if self._server:
            self._sender.send(
                "POST", f"{self._server}/register", headers, payload, _cb,
                verify=self._server.startswith("https://"),
                follow_redirects=False,
            )
        else:
            on_done(False, "")

    # -- payloads ------------------------------------------------------------

    def new_payload(self) -> str:
        """Return a fresh unique payload hostname for this session.

        Format: ``<correlation-id><base32-nonce>.<server-netloc>``. Each call
        yields a distinct hostname you can drop into a request; any callback to
        it correlates back to this session.
        """
        if not self._registered or not self._server:
            raise InteractshError("client is not registered")
        nonce = (
            base64.b32encode(os.urandom(NONCE_LENGTH))
            .decode("ascii").lower().rstrip("=")[:NONCE_LENGTH]
        )
        hostname = urlsplit(self._server).hostname
        if not hostname:
            raise InteractshError("registered server has no valid hostname")
        return f"{self._correlation_id}{nonce}.{hostname}"

    # -- polling -------------------------------------------------------------

    def poll(self, on_done: Callable[[list[Interaction], str], None]) -> None:
        """Poll the server once. ``on_done(interactions, error)`` on sender thread."""
        if not self._registered or not self._server:
            on_done([], "not registered")
            return
        query = urlencode({"id": self._correlation_id, "secret": self._secret})
        url = f"{self._server}/poll?{query}"
        headers: list[tuple[str, str]] = []
        if self._token:
            headers.append(("Authorization", self._token))

        def _cb(result: HttpResult) -> None:
            if not result.ok:
                on_done([], result.error or "poll failed")
                return
            if result.status_code == 401:
                on_done([], "authentication failed")
                return
            if result.status_code != 200:
                on_done([], f"poll returned {result.status_code}")
                return
            try:
                interactions = self._parse_poll(result.body)
            except Exception as exc:  # noqa: BLE001
                on_done([], f"decode error: {exc}")
                return
            on_done(interactions, "")

        self._sender.send(
            "GET", url, headers, b"", _cb,
            verify=self._server.startswith("https://"), follow_redirects=False,
        )

    def _parse_poll(self, body: bytes) -> list[Interaction]:
        payload = json.loads(body.decode("utf-8", errors="replace"))
        interactions: list[Interaction] = []
        aes_key_b64 = payload.get("aes_key", "")
        for item in payload.get("data") or []:
            try:
                plaintext = self._decrypt(aes_key_b64, item)
                interactions.append(Interaction.from_json(plaintext.decode("utf-8")))
            except Exception:  # noqa: BLE001 - skip undecryptable records
                continue
        # "extra" and "tlddata" are plaintext JSON records.
        for key in ("extra", "tlddata"):
            for item in payload.get(key) or []:
                try:
                    interactions.append(Interaction.from_json(item))
                except Exception:  # noqa: BLE001
                    continue
        return interactions

    def _decrypt(self, aes_key_b64: str, message_b64: str) -> bytes:
        if self._private_key is None:
            raise InteractshError("no private key")
        encrypted_key = base64.b64decode(aes_key_b64)
        aes_key = self._private_key.decrypt(
            encrypted_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        ciphertext = base64.b64decode(message_b64)
        if len(ciphertext) < 16:
            raise InteractshError("ciphertext too short")
        # The Interactsh server encrypts records with AES-256-CTR, using the
        # first 16 bytes of the payload as the initial counter (IV) and the
        # remainder as the ciphertext stream. (Some older reference clients
        # document CFB, but the live public servers use CTR.)
        iv, actual = ciphertext[:16], ciphertext[16:]
        cipher = Cipher(
            algorithms.AES(aes_key), modes.CTR(iv), backend=default_backend()
        )
        decryptor = cipher.decryptor()
        return decryptor.update(actual) + decryptor.finalize()

    # -- teardown ------------------------------------------------------------

    def deregister(self, on_done: Optional[Callable[[bool], None]] = None) -> None:
        """Deregister from the server. Best-effort; failures are ignored."""
        if not self._registered or not self._server:
            if on_done:
                on_done(False)
            return
        payload = json.dumps({
            "correlation-id": self._correlation_id,
            "secret-key": self._secret,
        }).encode("utf-8")
        headers = [("Content-Type", "application/json")]
        if self._token:
            headers.append(("Authorization", self._token))

        server = self._server
        with self._lock:
            self._registered = False

        def _cb(result: HttpResult) -> None:
            if on_done:
                on_done(result.ok and result.status_code == 200)

        self._sender.send(
            "POST", f"{server}/deregister", headers, payload, _cb,
            verify=server.startswith("https://"), follow_redirects=False,
        )
