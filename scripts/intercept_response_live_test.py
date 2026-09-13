"""Live: intercept a request via the real MainWindow, forward it, and confirm
the Intercept panel's response pane gets populated through the full pipeline."""
import os
import sys
import threading
import tempfile
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from bidoytu.config import AppConfig
from bidoytu.ui.main_window import MainWindow

app = QApplication.instance() or QApplication([])
cfg = AppConfig(data_dir=Path(tempfile.mkdtemp()))
cfg.proxy.listen_port = 8941

win = MainWindow(cfg)
intercept = win._proxy_tab.intercept
state = {"intercepted": False, "forwarded": False}


def send():
    def worker():
        import httpx
        try:
            httpx.get("http://example.com/", proxy="http://127.0.0.1:8941", timeout=15)
        except Exception as exc:
            print("  client error:", exc)
    threading.Thread(target=worker, daemon=True).start()


def on_started(host, port):
    # Turn interception on, then send a request.
    intercept._toggle_btn.setChecked(True)
    send()


def on_intercepted(record):
    state["intercepted"] = True
    # Forward it after a short delay (simulate the user clicking Forward).
    QTimer.singleShot(200, do_forward)


def do_forward():
    intercept._on_forward_clicked()
    state["forwarded"] = True


def check_done():
    resp = intercept._response_view.toPlainText()
    if resp.strip():
        print("  response pane populated:", resp.splitlines()[0])
        finish(True)


def finish(ok):
    win._engine.stop()
    win.close()
    app.quit()
    finish.ok = ok


finish.ok = False

win._engine.started_ok.connect(on_started)
win._engine.flow_intercepted.connect(on_intercepted)
# Poll the response pane after forwarding.
poll = QTimer()
poll.setInterval(500)
poll.timeout.connect(check_done)
poll.start()

QTimer.singleShot(300, win._proxy_tab.toggle_btn.click)
QTimer.singleShot(30000, lambda: (print("  TIMEOUT"), finish(False)))
app.exec()

ok = state["intercepted"] and state["forwarded"] and finish.ok
print(f"  intercepted={state['intercepted']} forwarded={state['forwarded']} shown={finish.ok}")
print("INTERCEPT RESPONSE LIVE TEST PASSED" if ok else "INTERCEPT RESPONSE LIVE TEST FAILED")
sys.exit(0 if ok else 1)
