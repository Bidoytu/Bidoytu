# Building the hybrid desktop

Use Node 24 LTS and Python 3.11+ (3.13 tested locally). Build each target on its native operating system; the Python sidecar is platform-specific.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
npm ci
npm run package:dir
```

`package:dir` type-checks and compiles the renderer, bundles Python with PyInstaller, then runs electron-builder. The unpacked Windows app is `release/win-unpacked/Bidoytu.exe`. `npm run package` additionally creates the platform installer (NSIS on Windows, AppImage on Linux, DMG on macOS). End users do not need Python or Node installed. macOS configuration is supplied but has not been validated on this Windows host.

To test an unpacked Windows application using its bundled Python interpreter:

```powershell
$env:BIDOYTU_PACKAGED = (Resolve-Path release/win-unpacked/Bidoytu.exe).Path
npm run test:e2e
Remove-Item Env:BIDOYTU_PACKAGED
```

The existing GitHub release workflow now bundles the hybrid application on Windows and Linux. Feature branches and pull requests run checks without publishing. Existing `main` and version-tag release triggers are retained. Python distributions contain the backend and optional legacy UI; the Electron runtime is delivered in desktop artifacts, not the Python wheel.

Keep `package.json`, `pyproject.toml`, and `src/bidoytu/__init__.py` versions aligned. Supply signing credentials through the release environment for trusted distribution; a successful local build alone is not proof of a signed/notarized release. No signing secrets are stored in this repository. The older `packaging/bidoytu.spec` and `build_release.md` procedures describe Qt compatibility builds.
