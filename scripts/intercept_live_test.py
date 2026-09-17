"""Live test: interception pauses a request, and forward/drop resolve it.

Scenario:
    1. Start engine, enable intercept.
    2. Send request #1 through the proxy -> expect flow_intercepted, then forward
       it and expect a captured response.
    3. Send request #2 -> expect flow_intercepted, then drop it and expect NO
       successful response (client sees a killed connection).
"""
import os
import sys
import threading
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from PySide6.QtCore import QCoreApplication, QTimer
from bidoytu.config import ProxyConfig
from bidoytu.ui.qt_proxy_engine import ProxyEngine

PORT = 8907
app = QCoreApplication(sys.argv)
engine = ProxyEngine(ProxyConfig(listen_host="127.0.0.1", listen_port=PORT))

state = {"phase": "forward", "intercepted": [], "forward_ok": False,
         "drop_ok": None, "responses": 0}


def send(path, result_key):
    def worker():
        import httpx
        try:
            r = httpx.get(f"http://example.com{path}",
                          proxy=f"http://127.0.0.1:{PORT}", timeout=15)
            state[result_key] = r.status_code
        except Exception as exc:
            state[result_key] = f"error:{type(exc).__name__}"
    threading.Thread(target=worker, daemon=True).start()


def on_started(host, port):
    engine.set_intercept_enabled(True)
    send("/forward-me", "forward_status")


def on_intercepted(record):
    state["intercepted"].append(record.flow_id)
    if state["phase"] == "forward":
        engine.forward(record.flow_id, None)  # forward unmodified
    else:
        engine.drop(record.flow_id)
        # Give the drop a moment, then finish.
        QTimer.singleShot(2000, finish)


def on_captured(record, is_response):
    if is_response and record.status_code is not None:
        state["responses"] += 1
        if state["phase"] == "forward":
            state["forward_ok"] = True
            # Move to drop phase.
            state["phase"] = "drop"
            send("/drop-me", "drop_status")


def finish():
    engine.stop()


engine.started_ok.connect(on_started)
engine.flow_intercepted.connect(on_intercepted)
engine.flow_captured.connect(on_captured)
engine.error.connect(lambda m: (print("ENGINE ERROR", m), app.quit()))
engine.stopped.connect(app.quit)

engine.start()
QTimer.singleShot(40000, lambda: (print("  TIMEOUT"), engine.stop(), app.quit()))
app.exec()

print(f"  intercepted flows: {len(state['intercepted'])}")
print(f"  forward produced response: {state['forward_ok']}")
print(f"  forward client status: {state.get('forward_status')}")
print(f"  drop client status: {state.get('drop_status')}")

# Success: at least 2 flows intercepted, forward yielded a real response,
# and the dropped request did NOT yield a 2xx/3xx (client saw an error/no resp).
ds = state.get("drop_status")
drop_blocked = isinstance(ds, str) and ds.startswith("error")
ok = (len(state["intercepted"]) >= 2 and state["forward_ok"] and drop_blocked)
print("INTERCEPT LIVE TEST PASSED" if ok else "INTERCEPT LIVE TEST FAILED")
sys.exit(0 if ok else 1)
