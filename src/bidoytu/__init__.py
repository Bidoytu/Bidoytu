"""Bidoytu - an intercepting HTTP proxy tool.

Base architecture:
    - Proxy/MITM engine: mitmproxy on a dedicated Python process asyncio loop.
    - Desktop UI: Electron, React and TypeScript through private process IPC.
    - Storage: SQLite (WAL) + on-disk bodies on a dedicated storage worker.
"""

__version__ = "2.0.0"
__app_name__ = "Bidoytu"
