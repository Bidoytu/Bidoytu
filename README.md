# Bidoytu

<p align="center"><img src="bidoytu-long.png" alt="Bidoytu" width="720"></p>

A focused HTTP interception and testing workspace with an **Electron + React + TypeScript desktop** and an independent **Python network engine**.

Bidoytu 2 introduces a dark, compact workspace inspired by Burp Suite and Caido: live traffic history, resizable request/response inspectors, editable interception, persistent Repeater tabs, controlled payload runs, passive audit and decoding.

## Run the desktop

Requires Node 24 LTS and Python 3.11+.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e .
npm ci
npm run dev
```

For a compiled renderer:

```powershell
npm run build
npm start
```

Electron discovers `.venv` or `venv` automatically. Set `BIDOYTU_PYTHON` to use a different interpreter. `bidoytu` and `python -m bidoytu` also launch the compiled Electron desktop from a prepared source checkout.

A locally built standalone Windows application is available at `release/win-unpacked/Bidoytu.exe` after packaging. Packaged applications bundle Python and do not require a separate interpreter.

## Core workflows

- **HTTP history:** live metadata updates, server-side search, scope/bookmark filters, pagination, virtual rows and a resizable split inspector.
- **Intercept:** pause, edit, forward or drop requests and responses; bounded pending queue and explicit state.
- **Repeater:** independent editable request tabs, connection-pooled Python replay, timing and response inspection; saved tabs restore on launch.
- **Intruder:** replace `§payload§` with line-based payloads; sequential runs, cancellation and result inspection.
- **Target scope:** persistent include/exclude host rules applied to new traffic.
- **Live audit:** opt-in passive checks with captured evidence and remediation.
- **Decoder:** Base64, URL, hex and JSON transformations in Python.
- **Settings:** proxy port, upstream TLS verification, public CA export and capture health.

Start the proxy, then configure a dedicated testing browser to use `127.0.0.1:8080` for HTTP and HTTPS. For HTTPS interception, export the public CA from Settings and import it into that browser's certificate authorities. Quick start in the sidebar explains the steps. Upstream TLS verification defaults to enabled.

Keyboard shortcuts: **Ctrl/Cmd K** to search, **Ctrl/Cmd 1–4** to switch primary tools, and **Ctrl/Cmd Enter** to send in Repeater.

## Architecture

```text
React feature views
    → sandboxed preload bridge
    → Electron main process
    ⇄ private JSON-lines process pipes
Python application service
    → asyncio mitmproxy + pooled httpx
    → bounded capture queue
    → dedicated SQLite/body-storage worker
```

No local HTTP control API is exposed. Electron validates IPC callers and commands; captured content renders as inert text. The Python runtime does not import or require Qt. Large bodies load on selection; history carries metadata only; editors virtualize long messages.

See [architecture, protocol, limits and migration](docs/hybrid-architecture.md) for the full design and measured performance.

## Data and compatibility

The Electron app uses its own local default workspace under Electron's user-data directory. Set `BIDOYTU_DATA_DIR` before launch to choose a different workspace. Existing Qt workspaces are preserved; use a copy when migrating. Captured traffic and saved request tabs are local plaintext files.

The optional Qt application remains available for legacy features such as Collaborator, automatic browser integration, workspace archive/password management, advanced scope/filter editors, grouped Repeater sends and multi-position Intruder modes. Those features are **not yet exposed in Electron**.

```powershell
python -m pip install -e ".[legacy]"
bidoytu-legacy
```

The [legacy wiki](docs/index.md) documents these older workflows. The [hybrid architecture guide](docs/hybrid-architecture.md) is authoritative for the new desktop.

## Verify and package

```powershell
python scripts/backend_test.py
npm test
npm run build
npm run test:e2e
python scripts/backend_benchmark.py
```

With `.[legacy]` installed, `python scripts/smoke_test.py` verifies Qt compatibility.

```powershell
python -m pip install -e ".[dev]"
npm run package:dir
# Or create an installer:
npm run package
```

See [desktop build and release instructions](docs/electron-release.md). Local Windows source and packaged-app testing are separate from Linux/macOS release validation and signing.

## Contributing

Use feature branches and open pull requests against `staging`. Keep `main` release-ready; the existing main/tag publishing triggers remain in place. See [CONTRIBUTING.md](CONTRIBUTING.md).

Use Bidoytu only with systems and traffic you own or are authorized to test. See [SECURITY.md](SECURITY.md) for reporting and data handling.

MIT licensed.
