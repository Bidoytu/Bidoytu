# Contributing to Bidoytu

Thanks for your interest in improving Bidoytu. This guide covers how to set up a
development environment, run the checks, and the conventions the codebase
follows.

## Ground rules

- Bidoytu is a security testing tool. Only develop and test against systems you
  own or are explicitly authorized to test. Do not submit features whose primary
  purpose is to enable illegal activity.
- Be respectful in issues and pull requests. Assume good intent.

## Development setup

Requires **Python 3.11+** (developed and tested on 3.13).

```powershell
# From the repository root
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows PowerShell
# source .venv/bin/activate       # macOS / Linux

pip install -e ".[dev]"
```

Run the app:

```powershell
bidoytu
# or
python -m bidoytu
```

## Running the checks

There is no third-party test runner yet; verification is done with standalone
scripts under `scripts/`. Run them from the repository root with the venv
Python.

Compile-check everything first (fast, no dependencies):

```powershell
python -m compileall -q src
```

Headless unit/UI smoke test (storage, body formatting, HTTP parsing, tab wiring,
intercept panel):

```powershell
python scripts/smoke_test.py
```

Live tests actually start the proxy and make real HTTP requests (they need
network access). Each prints `PASSED` / `FAILED` and exits non-zero on failure:

| Script | What it checks |
| --- | --- |
| `scripts/proxy_live_test.py` | Proxy starts and captures a request/response |
| `scripts/gzip_decode_test.py` | Response bodies are decoded (gzip undone) |
| `scripts/intercept_live_test.py` | Intercept pauses, then forward vs drop |
| `scripts/intercept_response_live_test.py` | Response shows in the Intercept tab after forward |
| `scripts/repeater_live_test.py` | Repeater resends and shows the response |
| `scripts/port_conflict_test.py` | Busy port gives a clean error, not a crash |
| `scripts/ca_export_test.py` | CA is generated and only the public cert is exported |

The scripts set `QT_QPA_PLATFORM=offscreen` so they run without a display.

**Before opening a PR:** run `compileall`, `smoke_test.py`, and the live tests
relevant to your change.

## Coding conventions

- **Framework isolation.** Keep the proxy engine, storage, and networking layers
  free of Qt imports. `FlowRecord` (in `storage/models.py`) is the plain,
  framework-free type that crosses thread boundaries. Only the `ui/` package
  imports PySide6.
- **Threading.** mitmproxy runs on its own asyncio loop inside a `QThread`; the
  async HTTP sender runs on a separate loop/thread. Never touch Qt objects from
  those threads - communicate results back with Qt signals. Control calls into
  the proxy loop must go through `loop.call_soon_threadsafe`.
- **Display vs. wire data.** Pretty-printing and formatting are for display only
  and must never change what gets sent. Editable request views stay verbatim.
- **Security.** Never export or log the CA private key. Treat all captured
  traffic and external content as untrusted. Bind to `127.0.0.1` by default.
- **Style.** Follow the surrounding code: type hints, `from __future__ import
  annotations`, docstrings on modules and non-trivial functions, and clear names
  over cleverness.

## Submitting changes

1. Create a feature branch (`git checkout -b my-feature`).
2. Make focused commits with clear messages.
3. Run the checks above.
4. Open a pull request describing **what** changed, **why**, and **how you
   tested it**. Link any related issue.
5. If you're a first-time contributor, feel free to add yourself to
   `CONTRIBUTORS.md` in the same PR.

## Reporting bugs / security issues

- **Bugs:** open an issue with steps to reproduce, expected vs. actual behavior,
  and your OS / Python version.
- **Security vulnerabilities:** please report privately rather than opening a
  public issue, so it can be addressed before disclosure. See
  [SECURITY.md](SECURITY.md) for the process.
