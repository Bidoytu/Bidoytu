# Bidoytu

<p align="center">
  <img src="bidoytu-long.png" alt="Bidoytu" width="720">
</p>

<p align="center">A focused desktop HTTP interception and testing workspace for authorized security work.</p>

<p align="center">
  <a href="https://github.com/Bidoytu/Bidoytu/actions/workflows/main.yml"><img src="https://github.com/Bidoytu/Bidoytu/actions/workflows/main.yml/badge.svg?branch=main" alt="Release CI"></a>
  <a href="https://github.com/Bidoytu/Bidoytu/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT License"></a>
</p>

Bidoytu is a Python desktop application for inspecting, modifying, and
replaying HTTP traffic through a local mitmproxy engine. It combines live
history, request interception, Repeater workflows, and an extensible Intruder
foundation in one PySide6 interface.

## Highlights

- Local HTTP/HTTPS proxy with editable interception and forward/drop controls.
- Traffic history backed by SQLite with content-addressed storage for large
  bodies.
- Repeater requests powered by an asynchronous httpx client.
- Display-only formatting for JSON, XML/HTML, and URL-encoded bodies.
- Public CA certificate export for HTTPS interception on machines you control.
- Windows and Linux packaging through GitHub Actions.

## Requirements

- Python 3.11 or newer
- Windows or Linux

## Quick start

    python -m venv .venv
    .venv\Scripts\Activate.ps1
    python -m pip install -e .
    bidoytu

Alternatively, run python -m bidoytu.

Start the proxy from the Proxy tab. The default listener is 127.0.0.1:8080.
To inspect HTTPS traffic, start the proxy once, export the public CA
certificate from the UI, and trust it only on a machine you own or are
authorized to administer.

## Architecture

| Layer | Responsibility |
| --- | --- |
| ui/ | PySide6 windows, tabs, editors, views, and Qt signal wiring |
| proxy/ | mitmproxy engine, flow capture, and interception control |
| net/ | Async HTTP sending for Repeater and Intruder workflows |
| storage/ | SQLite history, flow models, and large-body file storage |
| http_utils.py | Raw HTTP parsing, rebuilding, and display helpers |
| scripts/ | Headless smoke checks and focused live verification |

Qt is intentionally isolated to ui/. The proxy, networking, and storage layers
communicate through framework-independent models and thread-safe signals.

## Development workflow

Development work is integrated through staging:

    git switch staging
    git pull --ff-only origin staging
    git switch -c feature/short-description

Open pull requests against staging. Keep main reserved for reviewed,
release-ready changes. The release workflow runs on pushes to main, on version
tags, and through manual dispatch; pushes to staging do not publish releases.

See CONTRIBUTING.md for checks and pull-request expectations.

## Verification

    python -m compileall -q src
    python scripts/smoke_test.py

Run the relevant live scripts from scripts/ when changing proxy, interception,
Repeater, compression, port, or CA behavior. They require network access and
use QT_QPA_PLATFORM=offscreen.

## Packaging and releases

CI builds Windows and Linux artifacts with PyInstaller. Versioned releases are
created from v* tags, and tagged releases are also published to PyPI through
Trusted Publishing. See packaging/build_release.md for the complete release
procedure.

## Responsible use

Use Bidoytu only against systems and traffic you own or are explicitly
authorized to test. Installing a MITM CA or intercepting traffic without
permission may be illegal. See SECURITY.md for security reporting and
data-handling guidance.

## License

Bidoytu is released under the MIT License.
