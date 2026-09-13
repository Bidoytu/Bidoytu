"""Live test: RepeaterTab.load_from_record + Send performs a real request."""
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from bidoytu.net.async_sender import AsyncHttpSender
from bidoytu.storage.models import FlowRecord
from bidoytu.ui.repeater_tab import RepeaterTab

app = QApplication.instance() or QApplication([])
sender = AsyncHttpSender()
sender.start()

rep = RepeaterTab(sender)
rec = FlowRecord(
    flow_id="r1", method="GET", scheme="http", host="example.com", port=80,
    path="/", http_version="HTTP/1.1",
    request_headers="Host: example.com\r\nUser-Agent: bidoytu-test",
)
rep.load_from_record(rec)

done = {"ok": False}
orig = rep._on_result
def wrapped(result):
    orig(result)
    done["ok"] = result.ok and result.status_code is not None
    print(f"  repeater response: ok={result.ok} status={result.status_code} "
          f"bytes={len(result.body)}")
    app.quit()
rep._on_result = wrapped
rep._result_ready.disconnect()
rep._result_ready.connect(rep._on_result)

rep._on_send()
QTimer.singleShot(30000, lambda: (print("  TIMEOUT"), app.quit()))
app.exec()
sender.stop()

print("REPEATER LIVE TEST PASSED" if done["ok"] else "REPEATER LIVE TEST FAILED")
sys.exit(0 if done["ok"] else 1)
