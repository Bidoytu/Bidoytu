"""Bundle a Qt-free Python sidecar for electron-builder's extraResources."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    subprocess.run([
        sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--onedir",
        "--name", "bidoytu-backend", "--distpath", str(root / "build/backend"),
        "--workpath", str(root / "build/pyinstaller"), "--specpath", str(root / "build"),
        "--paths", str(root / "src"), "--collect-all", "mitmproxy",
        "--collect-all", "mitmproxy_rs", "--collect-data", "certifi",
        "--collect-data", "publicsuffix2", "--exclude-module", "PySide6",
        "--exclude-module", "PyQt6", "--exclude-module", "tkinter",
        str(root / "packaging/backend_entry.py"),
    ], cwd=root, check=True)


if __name__ == "__main__":
    main()
