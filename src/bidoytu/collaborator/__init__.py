"""Out-of-band application security testing (OAST) via Interactsh.

This package provides a Burp Collaborator-like feature: it registers a client
with an Interactsh server, hands out unique callback domains, and polls the
server for out-of-band interactions (DNS / HTTP / SMTP) that target
applications trigger when they process attacker-controlled data.
"""
from .client import InteractshClient, InteractshError, Interaction
from .service import CollaboratorService, OAST_SERVERS

__all__ = [
    "InteractshClient",
    "InteractshError",
    "Interaction",
    "CollaboratorService",
    "OAST_SERVERS",
]
