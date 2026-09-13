"""Verify the capture addon stores DECODED bodies (gzip is undone).

Routes a request through the engine to an endpoint that responds gzipped, and
asserts the captured response body is valid decoded text, not raw gzip bytes.
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
engine = ProxyEngine(ProxyConfig(listen_host="127.0.0.1", listen_port=8901))


def on_captured(record, is_response):
    if is_response and record.status_code is not None:
        captured.append(record)
        engine.stop()


def on_started(host, port):
    import threading, httpx

    def worker():
        try:
            # httpbin /gzip returns a gzip-encoded JSON body.
            httpx.get(
                "http://httpbin.org/gzip",
                proxy="http://127.0.0.1:8901",
                headers={"Accept-Encoding": "gzip"},
                timeout=15,
            )
        except Exception as exc:
            print(f"  request error: {exc}")
    threading.Thread(target=worker, daemon=True).start()


engine.flow_captured.connect(on_captured)
engine.started_ok.connect(on_started)
engine.error.connect(lambda m: (print("ENGINE ERROR", m), app.quit()))
engine.stopped.connect(app.quit)

engine.start()
QTimer.singleShot(30000, lambda: (print("  TIMEOUT"), engine.stop(), app.quit()))
app.exec()

if not captured:
    print("GZIP TEST FAILED: nothing captured")
    sys.exit(1)

rec = captured[0]
body = rec.response_body_inline or b""
print(f"  content-type: {rec.content_type}")
print(f"  body starts: {body[:40]!r}")

# Decoded httpbin gzip response is JSON containing '"gzipped": true'.
is_text = body.lstrip().startswith(b"{") and b"gzipped" in body
print("GZIP DECODE TEST PASSED" if is_text else "GZIP DECODE TEST FAILED")
sys.exit(0 if is_text else 1)
