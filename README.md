# Bidoytu

An intercepting HTTP proxy tool for inspecting, modifying, and replaying web
traffic, built in Python. This repository currently contains the **base
architecture** only - a working skeleton you can run and build on.

## Architecture

| Concern | Choice |
| --- | --- |
| Language | Python 3.11+ |
| Proxy / MITM engine | [mitmproxy](https://mitmproxy.org) used as a library (`DumpMaster`) |
| Desktop UI | [PySide6](https://doc.qt.io/qtforpython/) (Qt for Python) |
| Request/response editor | `QPlainTextEdit` + custom `QSyntaxHighlighter` |
| Database | SQLite via stdlib `sqlite3`, WAL mode, custom `QAbstractTableModel` |
| Large bodies | Stored as content-addressed files, referenced by path (not BLOBs) |
| Concurrency | `QThread` hosts mitmproxy on its own asyncio loop; UI updated via signals |
| Packaging | PyInstaller (dev), Nuitka (release) |

### A note on the editor widget

QScintilla is a Riverbank project bound to PyQt and has **no official PySide6
binding** (licensing/ABI incompatibility). To keep the whole app on the
official PySide6 binding, the base uses `QPlainTextEdit` + a custom
`QSyntaxHighlighter`. This is isolated in `ui/message_view.py` and
`ui/highlighter.py`, so it can be swapped for a QScintilla or Monaco-in-
QWebEngineView approach later without touching the rest of the app.

## Features (base)

- **Top-level tabs:** Proxy, Repeater, Intruder.
- **Proxy tab** with two sub-tabs:
  - *HTTP History* - live traffic table + request/response detail.
  - *Intercept* - pause in-flight requests; edit the raw request; **Forward**
    or **Drop**; a toggle turns interception on/off. Requests queue while one
    is held.
- **Repeater** - load a request (from history), edit it, resend via an async
  `httpx` client, and view the response.
- **Intruder** - skeleton: request template with `§payload§` markers + payload
  list. The attack runner is the documented next step.
- **Send to Repeater (Ctrl+R) / Send to Intruder (Ctrl+I)** via right-click on a
  history row (or the keyboard shortcut when the table is focused). The Intercept
  request editor has the same right-click actions.
- **Soft wrap** on all request/response views, toggleable per detail view.
- **Pretty-printed bodies** - JSON, XML/HTML, and URL-encoded forms are
  formatted for display (raw request text stays verbatim for editing).
- **Configurable listen host/port** from the Proxy tab.
- **CA certificate export** for trusting HTTPS interception (Proxy tab →
  *CA Certificate*).

## Project layout

```
src/bidoytu/
  app.py               # entry point (QApplication + MainWindow)
  __main__.py          # python -m bidoytu
  config.py            # paths + proxy/app configuration
  http_utils.py        # parse/build raw HTTP text <-> parts
  proxy/
    engine.py          # ProxyEngine: QThread hosting mitmproxy DumpMaster
    capture_addon.py   # flow -> FlowRecord mapping + interception (pause/forward/drop)
  net/
    async_sender.py    # AsyncHttpSender: httpx.AsyncClient on its own loop/thread
  storage/
    models.py          # FlowRecord dataclass (framework-free)
    repository.py      # SQLite (WAL) CRUD
    body_store.py      # content-addressed large-body file store
  ui/
    main_window.py     # top-level QTabWidget + wiring
    proxy_tab.py       # proxy controls + HTTP History / Intercept sub-tabs
    history_view.py    # traffic table + detail + send-to context menu/shortcuts
    intercept_view.py  # intercept queue, editor, forward/drop
    repeater_tab.py    # editable request + send + response
    intruder_tab.py    # skeleton (template + payloads)
    detail_view.py     # reusable request|response viewer + soft-wrap toggle
    flow_table_model.py# custom QAbstractTableModel for history
    message_view.py    # raw HTTP view/editor (soft wrap + pretty print)
    highlighter.py     # HTTP QSyntaxHighlighter
    body_format.py     # content-type-aware body pretty-printer
    ca_dialog.py       # export/install the proxy CA certificate
packaging/
  bidoytu.spec         # PyInstaller (dev)
  build_release.md     # Nuitka (release) instructions
scripts/               # headless smoke + live verification tests
```

### Data flow

```
Browser ─▶ mitmproxy (proxy thread, asyncio loop)
                │  CaptureAddon maps flow -> FlowRecord
                ▼
        ProxyEngine.flow_captured  (Qt signal, queued to UI thread)
                ▼
        MainWindow._on_flow_captured
                ├─▶ FlowRepository.upsert  (SQLite, big bodies -> BodyStore)
                └─▶ FlowTableModel.upsert_record  (history table updates live)
```

## Getting started

```powershell
# 1. Create a virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# 2. Install
pip install -e .

# 3. Run
bidoytu
# or: python -m bidoytu
```

Click **Start Proxy** on the Proxy tab. It listens on `127.0.0.1:8080` by
default (host and port are editable). Point a browser or tool at that proxy and
captured traffic appears in the history table; select a row to view the raw
request/response.

> **Intercepting HTTPS.** Browsers will reject the proxy's on-the-fly
> certificates (e.g. Firefox's `MOZILLA_PKIX_ERROR_MITM_DETECTED`) until you
> trust its CA. Start the proxy once (the CA is generated on first run under
> `<data_dir>/ca/`), then click **CA Certificate** on the Proxy tab to export
> the cert and follow the install instructions. Only trust this CA on machines
> you control, and remove it when you're done. Bidoytu only ever exports the
> public certificate, never the CA private key.

## Building

- **Development:** `pyinstaller packaging/bidoytu.spec`
- **Release:** see `packaging/build_release.md` (Nuitka)

## Status / next steps

Base architecture with a working Proxy (history + interception) and Repeater.
Natural next features:

- Intruder attack runner - iterate payloads through `AsyncHttpSender` and
  collect results in a table (positions parsing for `§...§` markers).
- Response interception (currently only requests are paused).
- Scope filtering, search, and column sorting/filtering on the history view.
- Match/replace rules and a saved project format.

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, the
testing workflow, and coding conventions, and [CONTRIBUTORS.md](CONTRIBUTORS.md)
for the list of people who have helped. To report a vulnerability, see
[SECURITY.md](SECURITY.md).

## Legal / responsible use

Bidoytu is an intercepting proxy intended for testing systems **you own or are
explicitly authorized to test**. Intercepting traffic or installing a MITM CA on
machines or networks without permission may be illegal. You are responsible for
how you use it.

## License

MIT - see [LICENSE](LICENSE).
