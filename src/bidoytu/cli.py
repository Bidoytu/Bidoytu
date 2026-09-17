"""Launch the Electron desktop from a source checkout without importing Qt."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    electron = root / "node_modules/electron/cli.js"
    node = shutil.which("node")
    if not node or not electron.exists() or not (root / "desktop/dist/index.html").exists():
        print("Bidoytu 2 uses the Electron desktop. From a source checkout, run:\n"
              "  npm install\n  npm run build\n  npm start\n\n"
              "For the optional Qt interface: pip install 'bidoytu[legacy]' then bidoytu-legacy.",
              file=sys.stderr)
        return 1
    return subprocess.call([node, str(electron), str(root)], cwd=root)
