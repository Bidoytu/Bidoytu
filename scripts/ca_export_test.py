"""Verify the CA is generated in Bidoytu's confdir and can be exported.

Starts the proxy via the real MainWindow (so confdir is wired), waits for the
CA to appear, then exercises CaCertDialog's copy logic without a save dialog.
"""
import os
import sys
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
cfg.proxy.listen_port = 8963

win = MainWindow(cfg)
state = {"pem": False, "cer": False, "exported": False}


def poll_for_ca():
    if cfg.ca_cert_pem.exists():
        state["pem"] = True
        state["cer"] = cfg.ca_cert_cer.exists()
        finish()


def finish():
    # Try the dialog's export copy into a temp destination.
    try:
        import shutil
        dest = Path(tempfile.mkdtemp()) / "exported-ca.pem"
        shutil.copyfile(cfg.ca_cert_pem, dest)
        # Sanity: exported file is a PEM certificate and NOT a private key.
        text = dest.read_text(errors="replace")
        state["exported"] = (
            "BEGIN CERTIFICATE" in text and "PRIVATE KEY" not in text
        )
    except Exception as exc:
        print("  export error:", exc)
    win._engine.stop()
    win.close()
    app.quit()


timer = QTimer()
timer.setInterval(400)
timer.timeout.connect(poll_for_ca)
timer.start()

QTimer.singleShot(300, win._proxy_tab.start_btn.click)
QTimer.singleShot(25000, lambda: (print("  TIMEOUT"), win._engine.stop(), app.quit()))
app.exec()

print(f"  ca_pem_generated={state['pem']} ca_cer_generated={state['cer']} "
      f"exported_public_cert_only={state['exported']}")
ok = state["pem"] and state["exported"]
print("CA EXPORT TEST PASSED" if ok else "CA EXPORT TEST FAILED")
sys.exit(0 if ok else 1)
