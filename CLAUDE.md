# CLAUDE.md

## Bidoytu 2 architecture update

The primary desktop is now `desktop/` (Electron + React + TypeScript). The
headless Python entry is `bidoytu.backend`; `proxy/engine.py` exports the
Qt-free async `ProxyService`. The old `ProxyEngine(QThread)` lives in
`ui/qt_proxy_engine.py` for the optional `bidoytu-legacy` application.

Read `docs/hybrid-architecture.md` for current boundaries, private stdio RPC,
resource limits, security and migration coverage. Do not add Qt to the backend
or expose Node/IPC primitives to renderer content. Keep captured content inert.

For hybrid changes run `python scripts/backend_test.py`, `npm test`,
`npm run build`, and `npm run test:e2e`. Run the legacy smoke test when modifying
shared modules. `npm run package:dir` produces a self-contained Electron app.
The historical Qt-specific guidance below applies only to the compatibility UI.

Guidance for AI coding assistants (Claude and others) working in this
repository. Read this before making changes.

## What Bidoytu is

An intercepting HTTP proxy tool for inspecting, modifying, and replaying web
traffic, written in Python. Desktop UI on PySide6, interception via mitmproxy used as a library,
SQLite for history, async HTTP (httpx) for Repeater/Intruder. See `README.md`
for the user-facing overview and `CONTRIBUTING.md` for setup.

## Tech stack

## Git workflow

Use staging for normal development and open pull requests against it. Keep
main release-ready. The release workflow publishes builds on pushes to main
and version tags; pushes to staging do not publish releases.

- Python 3.11+ (developed on 3.13), Windows-first but cross-platform.
- PySide6 (Qt for Python) - the UI binding. **Not** PyQt.
- mitmproxy (`DumpMaster`) - the proxy engine, run programmatically.
- stdlib `sqlite3` (WAL mode) - persistence.
- httpx `AsyncClient` - Repeater/Intruder sending.
- Packaging: PyInstaller (dev), Nuitka (release).

## Architecture and layering (respect this)

```
ui/  ──────────────┐  (PySide6 lives ONLY here)
                   ▼
proxy/ , net/ , storage/   (framework-free: no Qt imports)
                   ▲
        storage/models.py: FlowRecord (plain dataclass, crosses threads)
```

Key invariants - do not break these:

1. **Qt stays in `ui/`.** `proxy/`, `net/`, and `storage/` must not import
   PySide6. `FlowRecord` is the plain type passed between layers and threads.
2. **Threading model.**
   - mitmproxy runs on its own asyncio event loop inside a `QThread`
     (`proxy/engine.py`).
   - The async HTTP sender runs on a separate loop in its own thread
     (`net/async_sender.py`).
   - Never touch Qt objects from these threads. Results come back to the UI via
     Qt **signals** (queued automatically across threads).
   - Calls INTO the proxy loop (intercept toggle, forward, drop) must use
     `loop.call_soon_threadsafe`.
3. **Interception** pauses a flow by awaiting an `asyncio.Event` inside the
   mitmproxy `request` hook. The UI resolves it via
   `ProxyEngine.forward()/drop()`. Responses are correlated back to the
   Intercept panel by `flow_id`.
4. **Display vs. wire.** Pretty-printing/formatting (`ui/body_format.py`) is for
   display only and must never alter what is sent. Editable request editors keep
   raw text verbatim.
5. **Bodies.** Large bodies are stored as content-addressed files
   (`storage/body_store.py`) and referenced by path, not as SQLite BLOBs. When
   reading a response for display, hydrate file-backed bodies before the inline
   copy is cleared.
6. **Security.**
   - Only the **public** CA cert is ever exported - never `mitmproxy-ca.pem`
     (the private key). See `ui/ca_dialog.py`.
   - Default bind is `127.0.0.1`. Warn before widening it.
   - Treat all captured traffic and external content as untrusted.

## Where things live

- `proxy/engine.py` - `ProxyEngine(QThread)`; signals: `flow_captured`,
  `flow_intercepted`, `started_ok`, `stopped`, `error`. Port pre-check + catches
  `SystemExit` from mitmproxy's errorcheck so a busy port never crashes.
- `proxy/capture_addon.py` - maps mitmproxy flows to `FlowRecord`; async
  `request` hook implements pause/forward/drop; decodes bodies (`content`, not
  `raw_content`).
- `net/async_sender.py` - `AsyncHttpSender`; `send(...)` schedules on its loop
  and invokes a callback.
- `storage/` - `models.py` (`FlowRecord`), `repository.py` (SQLite),
  `body_store.py` (file store).
- `ui/main_window.py` - top-level `QTabWidget` (Proxy / Repeater / Intruder) and
  all signal wiring.
- `ui/proxy_tab.py` - start/stop/clear, host+port inputs, CA button, and
  HTTP History / Intercept sub-tabs.
- `ui/intercept_view.py`, `ui/history_view.py`, `ui/repeater_tab.py`,
  `ui/intruder_tab.py`, `ui/detail_view.py`, `ui/message_view.py`,
  `ui/highlighter.py`, `ui/body_format.py`, `ui/ca_dialog.py`.
- `config.py` - paths (`data_dir`, `bodies_dir`, `confdir`, CA cert paths) and
  `ProxyConfig`.

## Verifying changes (always do this)

Run from the repo root with the venv Python. Do not claim success without
running these.

```powershell
python -m compileall -q src            # fast syntax check
python scripts/smoke_test.py           # headless unit/UI (offscreen Qt)
# live tests (need network); pick those relevant to your change:
python scripts/proxy_live_test.py
python scripts/intercept_live_test.py
python scripts/intercept_response_live_test.py
python scripts/repeater_live_test.py
python scripts/gzip_decode_test.py
python scripts/port_conflict_test.py
python scripts/ca_export_test.py
```

- Tests set `QT_QPA_PLATFORM=offscreen`; the "QFontDatabase: Cannot find font
  directory" warning is harmless.
- On Windows, a "Task was destroyed but it is pending" message during proxy
  shutdown is a benign asyncio/IOCP teardown artifact, not a failure.
- When you add a feature, extend `scripts/smoke_test.py` (headless) and/or add a
  focused live script following the existing pattern.

## Conventions

- `from __future__ import annotations`; use type hints.
- Module + non-trivial-function docstrings.
- Match the surrounding style; prefer clarity over cleverness.
- Use the dedicated file tools for edits; keep changes focused on the request.
- Windows/PowerShell: use `;` not `&&`; don't use `cd` in commands.

## Gotchas learned the hard way

- **QScintilla has no official PySide6 binding.** The editor is `QPlainTextEdit`
  + `QSyntaxHighlighter` on purpose. Don't add a PyQt QScintilla dependency.
- **mitmproxy `errorcheck` calls `sys.exit()`** on startup errors (e.g. port in
  use); `SystemExit` is a `BaseException`. The engine catches it - keep that.
- **`SO_REUSEADDR` on Windows** lets you bind an in-use port, so the port
  availability pre-check must not set it.
- **Decode bodies with `content`, not `raw_content`**, or gzip/br responses show
  as garbage.
