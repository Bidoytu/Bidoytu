# Contributing to Bidoytu

Thank you for helping improve Bidoytu. Contributions should be focused,
reproducible, and safe to review.

## Branches and pull requests

Staging is the integration branch for day-to-day development. Create feature
branches from it and open pull requests back into it:

    git switch staging
    git pull --ff-only origin staging
    git switch -c feature/short-description

Keep main release-ready. The existing CI workflow publishes builds only for
pushes to main and version tags; changes pushed to staging do not create
releases.

Use clear, focused commits. Pull requests should explain what changed, why it
changed, how it was tested, and any security or compatibility considerations.

## Local setup

Requires Python 3.11 or newer.

    python -m venv .venv
    .venv\Scripts\Activate.ps1
    python -m pip install -e ".[dev]"

Run the application with bidoytu or python -m bidoytu.

## Checks

Run these before opening a pull request:

    python -m compileall -q src
    python scripts/smoke_test.py

Run the relevant live check when changing proxy, interception, response
decoding, Repeater, port handling, or CA behavior:

| Script | Coverage |
| --- | --- |
| proxy_live_test.py | Proxy captures a request and response |
| intercept_live_test.py | Interception forward/drop behavior |
| intercept_response_live_test.py | Forwarded response appears in Intercept |
| repeater_live_test.py | Repeater sends and displays a response |
| gzip_decode_test.py | Compressed response decoding |
| port_conflict_test.py | Clean handling of a busy port |
| ca_export_test.py | CA generation and public-only export |

The checks run headlessly with QT_QPA_PLATFORM=offscreen. Live checks need
network access.

## Design rules

- Keep PySide6 imports inside src/bidoytu/ui/.
- Keep proxy, networking, and storage layers independent of Qt.
- Use Qt signals for cross-thread results and loop.call_soon_threadsafe for
  calls into the proxy loop.
- Never modify wire data during display formatting.
- Never log, export, or commit a CA private key or captured secrets.
- Preserve the default 127.0.0.1 bind unless a change is deliberate and
  documented.

## Security issues

Do not open a public issue for a suspected vulnerability. Follow SECURITY.md
instead.

## License

By contributing, you agree that your contribution is provided under the MIT
License.
