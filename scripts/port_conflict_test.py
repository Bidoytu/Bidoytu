"""Verify starting the proxy on an occupied port produces a clean error signal
(not a SystemExit/crash escaping the QThread)."""
import os
import socket
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from PySide6.QtCore import QCoreApplication, QTimer
from bidoytu.config import ProxyConfig
from bidoytu.proxy.engine import ProxyEngine

PORT = 8931
# Occupy the port so the proxy cannot bind it.
blocker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
blocker.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
blocker.bind(("127.0.0.1", PORT))
blocker.listen(1)

app = QCoreApplication(sys.argv)
engine = ProxyEngine(ProxyConfig(listen_host="127.0.0.1", listen_port=PORT))

state = {"error": None, "started": False}
engine.error.connect(lambda m: (state.__setitem__("error", m), engine.stop()))
engine.started_ok.connect(lambda h, p: state.__setitem__("started", True))
engine.stopped.connect(app.quit)

engine.start()
QTimer.singleShot(10000, lambda: (print("  TIMEOUT"), engine.stop(), app.quit()))
app.exec()
blocker.close()

print(f"  started={state['started']} error={state['error']!r}")
# The key assertion is: we get a clean error (no crash / no escaping SystemExit)
# and the proxy did not report itself as running.
ok = (not state["started"]) and state["error"] is not None and "use" in state["error"].lower()
print("PORT CONFLICT TEST PASSED" if ok else "PORT CONFLICT TEST FAILED")
sys.exit(0 if ok else 1)
