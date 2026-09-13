"""Bidoytu - an intercepting HTTP proxy tool.

Base architecture:
    - Proxy/MITM engine: mitmproxy (DumpMaster) running in a QThread.
    - Desktop UI: PySide6 (Qt for Python).
    - Storage: SQLite (WAL) + on-disk body file store, exposed to the UI via
      a custom QAbstractTableModel.
"""

__version__ = "0.1.0"
__app_name__ = "Bidoytu"
