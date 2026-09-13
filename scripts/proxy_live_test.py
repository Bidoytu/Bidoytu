"""Live end-to-end test: start the ProxyEngine thread and route a real request
through it, asserting a FlowRecord is captured with a response.

Runs headless under a Qt event loop with a short timeout.
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from PySide6.QtCore import QCoreApplication, QTimer
from bidoytu.config import ProxyConfig
from bidoytu.proxy.engine import ProxyEngine

captured = []
app = QCoreApplication(sys.argv)
engine = ProxyEngine(ProxyConfig(listen_host="127.0.0.1", listen_port=8899))


def on_captured(record, is_response):
    captured.append((record, is_response))
    if is_response and record.status_code is not None:
        print(f"  captured {record.method} {record.host}{record.path} -> {record.status_code}")
        engine.stop()


def send_request():
    import threading
    import httpx

    def worker():
        try:
            httpx.get(
                "http://example.com/",
                proxy="http://127.0.0.1:8899",
                timeout=10,
            )
        except Exception as exc:
            print(f"  request error: {exc}")
    threading.Thread(target=worker, daemon=True).start()


def on_started(host, port):
    print(f"  proxy up on {host}:{port}, sending request...")
    send_request()


def on_error(msg):
    print(f"  ENGINE ERROR: {msg}")
    app.quit()


engine.flow_captured.connect(on_captured)
engine.started_ok.connect(on_started)
engine.error.connect(on_error)
engine.stopped.connect(app.quit)

engine.start()

# Safety timeout so the test never hangs CI.
QTimer.singleShot(25000, lambda: (print("  TIMEOUT"), engine.stop(), app.quit()))

app.exec()

ok = any(is_resp and r.status_code for r, is_resp in captured)
print("LIVE PROXY TEST PASSED" if ok else "LIVE PROXY TEST FAILED")
sys.exit(0 if ok else 1)
