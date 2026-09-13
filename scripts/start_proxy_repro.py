"""Reproduce the 'start proxy crashes' path using the real MainWindow.

Builds the actual window, clicks Start Proxy, waits for started/error, sends a
request, then quits. Prints any engine error or exception.
"""
import os
import sys
import threading
import traceback
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from bidoytu.config import AppConfig
from bidoytu.ui.main_window import MainWindow

app = QApplication.instance() or QApplication([])

import tempfile
tmp = tempfile.mkdtemp()
cfg = AppConfig(data_dir=Path(tmp))
cfg.proxy.listen_port = 8911

win = MainWindow(cfg)
win.show()

log = {"started": False, "error": None, "captured": 0}

win._engine.started_ok.connect(lambda h, p: log.__setitem__("started", True))
win._engine.error.connect(lambda m: log.__setitem__("error", m))
win._engine.flow_captured.connect(lambda r, isr: log.__setitem__("captured", log["captured"] + 1))


def send():
    def worker():
        import httpx
        try:
            httpx.get("http://example.com/", proxy="http://127.0.0.1:8911", timeout=10)
        except Exception as exc:
            print("  client error:", exc)
    threading.Thread(target=worker, daemon=True).start()


def after_start():
    print(f"  started={log['started']} error={log['error']}")
    if log["started"]:
        send()
    QTimer.singleShot(8000, finish)


def finish():
    print(f"  captured={log['captured']} error={log['error']}")
    win.close()
    app.quit()


# Click Start the way the UI does.
QTimer.singleShot(500, win._proxy_tab.start_btn.click)
QTimer.singleShot(3000, after_start)

try:
    app.exec()
except Exception:
    traceback.print_exc()

if log["error"]:
    print("REPRO: ENGINE ERROR ->", log["error"])
    sys.exit(1)
print("REPRO: no engine error")
