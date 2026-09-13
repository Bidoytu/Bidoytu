"""Dialog for exporting and installing the proxy's CA certificate.

To intercept HTTPS, mitmproxy signs certificates with its own CA. Browsers
correctly reject this until the CA is trusted, which is exactly the
MOZILLA_PKIX_ERROR_MITM_DETECTED / NET::ERR_CERT_AUTHORITY_INVALID a user sees.
This dialog lets the user save the CA certificate and shows how to install it.

Only the public CA certificate is ever exported here - never the CA private
key (``mitmproxy-ca.pem``), which would let anyone mint trusted certificates.
"""
from __future__ import annotations

import shutil
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
)

_INSTRUCTIONS = """\
To intercept HTTPS traffic, install this CA certificate as a trusted authority.
Only install it on machines you control, and remove it when you're done - while
trusted, this CA can sign certificates for any site.

Firefox (uses its own trust store):
  Settings > Privacy & Security > Certificates > View Certificates >
  Authorities > Import > select the .pem file > trust for websites.

Windows (system store, used by Chrome/Edge):
  Double-click the .cer file > Install Certificate > Local Machine >
  "Place all certificates in the following store" >
  Trusted Root Certification Authorities.

macOS:
  Open the .pem in Keychain Access (System keychain) > set to "Always Trust".

Linux (CLI tools / Chrome):
  Copy the .pem into the system trust store (e.g. /usr/local/share/ca-certificates
  as .crt) and run update-ca-certificates.
"""


class CaCertDialog(QDialog):
    """Shows CA status, an export button, and install instructions."""

    def __init__(self, pem_path: Path, cer_path: Path, parent=None) -> None:
        super().__init__(parent)
        self._pem_path = Path(pem_path)
        self._cer_path = Path(cer_path)

        self.setWindowTitle("Proxy CA Certificate")
        self.resize(640, 480)

        self._status = QLabel()
        self._status.setWordWrap(True)

        instructions = QPlainTextEdit()
        instructions.setReadOnly(True)
        instructions.setPlainText(_INSTRUCTIONS)

        self._export_pem_btn = QPushButton("Save .pem (Firefox / Linux / macOS)")
        self._export_cer_btn = QPushButton("Save .cer (Windows)")
        self._export_pem_btn.clicked.connect(lambda: self._export(self._pem_path, "pem"))
        self._export_cer_btn.clicked.connect(lambda: self._export(self._cer_path, "cer"))

        buttons = QHBoxLayout()
        buttons.addWidget(self._export_pem_btn)
        buttons.addWidget(self._export_cer_btn)
        buttons.addStretch(1)

        layout = QVBoxLayout(self)
        layout.addWidget(self._status)
        layout.addLayout(buttons)
        layout.addWidget(QLabel("How to install:"))
        layout.addWidget(instructions)

        self._refresh_status()

    def _ca_ready(self) -> bool:
        return self._pem_path.exists()

    def _refresh_status(self) -> None:
        if self._ca_ready():
            self._status.setText(
                f"CA certificate is ready.\nLocation: {self._pem_path}"
            )
            self._export_pem_btn.setEnabled(True)
            self._export_cer_btn.setEnabled(self._cer_path.exists())
        else:
            self._status.setText(
                "The CA certificate hasn't been generated yet. "
                "Start the proxy once - mitmproxy creates the CA on first run - "
                "then reopen this dialog to export it."
            )
            self._export_pem_btn.setEnabled(False)
            self._export_cer_btn.setEnabled(False)

    def _export(self, source: Path, kind: str) -> None:
        if not source.exists():
            QMessageBox.warning(
                self, "Not available yet",
                "Start the proxy once so the CA certificate is generated, "
                "then try again.",
            )
            self._refresh_status()
            return
        default_name = f"bidoytu-ca-cert.{kind}"
        filt = "PEM certificate (*.pem)" if kind == "pem" else "Certificate (*.cer)"
        dest, _ = QFileDialog.getSaveFileName(
            self, "Save CA certificate", default_name, filt
        )
        if not dest:
            return
        try:
            shutil.copyfile(source, dest)
        except OSError as exc:
            QMessageBox.critical(self, "Export failed", str(exc))
            return
        QMessageBox.information(
            self, "Saved",
            f"CA certificate saved to:\n{dest}\n\n"
            "Install it as a trusted root authority (see the instructions).",
        )
