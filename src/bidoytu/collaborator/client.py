"""A dependency-light async Interactsh protocol client.

Implements the subset of the Interactsh client protocol Bidoytu needs to offer
a Burp Collaborator-like feature:

* ``register``  -> POST ``/register`` with an RSA public key so the server can
  encrypt interaction payloads back to us.
* ``poll``      -> GET  ``/poll?id=<correlation>&secret=<secret>`` and decrypt
  each returned interaction (AES-256-CFB session key, itself RSA-OAEP-SHA256
  encrypted with our public key).
* ``deregister``-> POST ``/deregister`` to release the session on the server.

Callback domains follow the Interactsh scheme
``<correlation-id><nonce>.<server-host>``. The correlation id is the stable
per-session prefix; the nonce makes each handed-out domain unique so the
operator can tell interactions apart.

Only ``httpx`` and ``cryptography`` are used, both of which the project already
depends on, so no new third-party requirement is introduced.
"""
from __future__ import annotations

import base64
import json
import os
import random
import string
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from urllib.parse import urlsplit

import httpx
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# The Interactsh server expects a correlation id of exactly this length and a
# nonce of this length appended to it. These match the projectdiscovery
# defaults; the server parses the leading `CORRELATION_ID_LENGTH` characters of
# every hostname to route an interaction back to the owning session.
CORRELATION_ID_LENGTH = 20
NONCE_LENGTH = 13
_ID_ALPHABET = string.ascii_lowercase + string.digits


class InteractshError(Exception):
    """Raised for any registration, polling, or crypto failure."""


@dataclass(slots=True)
class Interaction:
    """A single out-of-band interaction reported by the server."""

    protocol: str
    unique_id: str
    full_id: str
    remote_address: str
    timestamp: str
    q_type: str | None = None
    raw_request: str | None = None
    raw_response: str | None = None
    smtp_from: str | None = None

    @classmethod
    def from_payload(cls, payload: dict) -> "Interaction":
        raw_ts = payload.get("timestamp")
        try:
            timestamp = _normalise_timestamp(raw_ts) if raw_ts else _now_iso()
        except (ValueError, TypeError):
            timestamp = _now_iso()
        return cls(
            protocol=str(payload.get("protocol", "")),
            unique_id=str(payload.get("unique-id", "")),
            full_id=str(payload.get("full-id", "")),
            remote_address=str(payload.get("remote-address", "")),
            timestamp=timestamp,
            q_type=payload.get("q-type"),
            raw_request=payload.get("raw-request"),
            raw_response=payload.get("raw-response"),
            smtp_from=payload.get("smtp-from"),
        )

    def to_dict(self) -> dict:
        return {
            "protocol": self.protocol,
            "unique_id": self.unique_id,
            "full_id": self.full_id,
            "remote_address": self.remote_address,
            "timestamp": self.timestamp,
            "q_type": self.q_type,
            "raw_request": self.raw_request,
            "raw_response": self.raw_response,
            "smtp_from": self.smtp_from,
        }


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalise_timestamp(value: str) -> str:
    # Server timestamps carry nanosecond precision and a trailing Z that older
    # Pythons cannot parse; trim to microseconds and normalise the zone suffix.
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    if "." in text:
        head, _, tail = text.partition(".")
        frac = tail
        offset = ""
        for marker in ("+", "-"):
            idx = tail.find(marker)
            if idx > 0:
                frac, offset = tail[:idx], tail[idx:]
                break
        frac = frac[:6]
        text = f"{head}.{frac}{offset}"
    return datetime.fromisoformat(text).astimezone(timezone.utc).isoformat()


def _generate_correlation_id() -> str:
    return "".join(random.choices(_ID_ALPHABET, k=CORRELATION_ID_LENGTH))


def _generate_nonce() -> str:
    raw = base64.b32encode(os.urandom(NONCE_LENGTH)).decode("ascii").lower().rstrip("=")
    return raw[:NONCE_LENGTH]


@dataclass
class InteractshClient:
    """Async client bound to a single Interactsh server registration."""

    server: str
    token: str = ""
    verify_tls: bool = True
    correlation_id: str = field(default_factory=_generate_correlation_id)
    secret_key: str = field(default_factory=lambda: str(uuid.uuid4()))
    registered: bool = False

    def __post_init__(self) -> None:
        self._private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=default_backend()
        )
        parsed = urlsplit(self.server if "://" in self.server else f"https://{self.server}")
        if parsed.scheme not in ("http", "https") or not parsed.hostname:
            raise InteractshError("Invalid OAST server URL")
        self._scheme = parsed.scheme
        self._host = parsed.netloc
        self._base = f"{parsed.scheme}://{parsed.netloc}"
        self._client = httpx.AsyncClient(
            verify=self.verify_tls,
            trust_env=False,
            timeout=15,
            headers={"User-Agent": "Bidoytu-Collaborator/1.0"},
            limits=httpx.Limits(max_connections=4, max_keepalive_connections=2),
        )

    @property
    def host(self) -> str:
        return self._host

    def _public_key_b64(self) -> str:
        pem = self._private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        return base64.b64encode(pem).decode("ascii")

    def _auth_headers(self) -> dict[str, str]:
        return {"Authorization": self.token} if self.token else {}

    async def register(self) -> None:
        """Register our public key so the server can encrypt interactions."""
        payload = {
            "public-key": self._public_key_b64(),
            "secret-key": self.secret_key,
            "correlation-id": self.correlation_id,
        }
        try:
            response = await self._client.post(
                f"{self._base}/register",
                content=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json", **self._auth_headers()},
            )
        except httpx.HTTPError as exc:
            raise InteractshError(f"Could not reach OAST server: {exc}") from exc
        if response.status_code == 401:
            raise InteractshError("The OAST server rejected the auth token")
        if response.status_code != 200:
            raise InteractshError(
                f"OAST registration failed ({response.status_code}): {response.text[:200]}"
            )
        try:
            message = response.json().get("message", "")
        except ValueError:
            message = ""
        if message != "registration successful":
            raise InteractshError("OAST server did not confirm registration")
        self.registered = True

    def new_domain(self) -> str:
        """Return a fresh unique callback domain for this session."""
        return f"{self.correlation_id}{_generate_nonce()}.{self._host}"

    def new_url(self, secure: bool = True) -> str:
        scheme = "https" if secure else "http"
        return f"{scheme}://{self.new_domain()}"

    async def poll(self) -> list[Interaction]:
        """Fetch and decrypt any interactions the server has queued."""
        if not self.registered:
            return []
        url = f"{self._base}/poll?id={self.correlation_id}&secret={self.secret_key}"
        try:
            response = await self._client.get(url, headers=self._auth_headers())
        except httpx.HTTPError as exc:
            raise InteractshError(f"Could not poll OAST server: {exc}") from exc
        if response.status_code == 401:
            raise InteractshError("Authentication failed while polling OAST server")
        if response.status_code != 200:
            raise InteractshError(
                f"OAST poll failed ({response.status_code}): {response.text[:200]}"
            )
        try:
            body = response.json()
        except ValueError as exc:
            raise InteractshError("OAST server returned a malformed poll response") from exc

        interactions: list[Interaction] = []
        aes_key = body.get("aes_key")
        for encrypted in body.get("data") or []:
            if not aes_key:
                continue
            try:
                plaintext = self._decrypt(aes_key, encrypted)
                interactions.append(Interaction.from_payload(json.loads(plaintext)))
            except (InteractshError, ValueError):
                # Skip a single corrupt record rather than dropping the batch.
                continue
        # `extra` and `tlddata` records arrive as plain JSON, not encrypted.
        for plain in (body.get("extra") or []) + (body.get("tlddata") or []):
            try:
                interactions.append(Interaction.from_payload(json.loads(plain)))
            except ValueError:
                continue
        return interactions

    def _decrypt(self, aes_key_b64: str, message_b64: str) -> bytes:
        try:
            aes_key = self._private_key.decrypt(
                base64.b64decode(aes_key_b64),
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )
            ciphertext = base64.b64decode(message_b64)
            if len(ciphertext) < 16:
                raise InteractshError("OAST ciphertext is too short")
            # Interactsh servers prepend a 16-byte IV and encrypt the payload
            # with AES-256-CTR (the server uses cipher.NewCTR). The first block
            # decrypts under CFB too, which is why a CFB reader appears to work
            # until the payload spills past 16 bytes.
            iv, body = ciphertext[:16], ciphertext[16:]
            decryptor = Cipher(
                algorithms.AES(aes_key), modes.CTR(iv), backend=default_backend()
            ).decryptor()
            return decryptor.update(body) + decryptor.finalize()
        except (ValueError, TypeError) as exc:
            raise InteractshError(f"Failed to decrypt interaction: {exc}") from exc

    async def deregister(self) -> None:
        """Release the session on the server. Best effort."""
        if not self.registered:
            await self._client.aclose()
            return
        payload = {"correlation-id": self.correlation_id, "secret-key": self.secret_key}
        try:
            await self._client.post(
                f"{self._base}/deregister",
                content=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json", **self._auth_headers()},
            )
        except httpx.HTTPError:
            pass
        finally:
            self.registered = False
            await self._client.aclose()
