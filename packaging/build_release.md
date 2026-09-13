# Building and releasing Bidoytu

Bidoytu ships as a self-contained desktop app for **Windows** and **Linux**,
built with PyInstaller from `packaging/bidoytu.spec`.

## How releases work (CI/CD)

Everything is automated in `.github/workflows/main.yml`. It builds Windows and
Linux in parallel and publishes to GitHub Releases. There are two paths:

| Trigger | Result |
| --- | --- |
| Push to `main` | Rolling **pre-release** tagged `latest`, overwritten each push. A single "download the current build" link. |
| Push a `v*` tag (e.g. `v1.0.0`) | A permanent, versioned release named "Bidoytu v1.0.0". Not a pre-release. |

You never build release artifacts by hand for distribution; the tag drives it.

## Cutting version 1.0.0

1. Make sure `main` is green and the version is bumped:
   - `pyproject.toml` -> `version = "1.0.0"`
   - `src/bidoytu/__init__.py` -> `__version__ = "1.0.0"`
2. Tag and push:

   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

3. The `Release` workflow runs, builds both OSes, and creates a
   **Bidoytu v1.0.0** release with two downloads:
   - `bidoytu-windows.zip`
   - `bidoytu-linux.zip`

4. Users unzip and run the `bidoytu` executable inside.

For later versions, bump the two version fields and push a new `vX.Y.Z` tag.

## Local builds (optional)

CI is the source of truth, but you can build locally to test.

### Prerequisites

```bash
pip install -e ".[dev]"
```

> **Windows note:** PySide6 ships very deep file paths. If `pip install` fails
> with an `OSError`/"No such file or directory" on a long PySide6 path, enable
> Windows long-path support once (admin PowerShell):
>
> ```powershell
> New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" `
>   -Name LongPathsEnabled -Value 1 -PropertyType DWORD -Force
> ```

### Build (Windows or Linux)

```bash
python -m PyInstaller packaging/bidoytu.spec --noconfirm
```

Output lands in `dist/bidoytu/` (the `bidoytu` executable plus an `_internal`
folder). On Linux, install the Qt/xcb system libraries first (see the
`Install Linux system libraries` step in the workflow for the exact list).

## Why the build is ~160 MB and not ~740 MB

The spec deliberately does **not** use `collect_all("PySide6")`. That would
bundle the entire Qt stack, and the single biggest piece is **QtWebEngine**, a
full embedded Chromium (~300 MB) that this app never uses. The spec instead
excludes the Qt modules the app doesn't import (WebEngine, QML/Quick, 3D,
Multimedia, Charts, SQL, PDF, OpenGL, plus stray `numpy`/`scipy`/`PIL`), since
Bidoytu only uses `QtCore`, `QtGui`, and `QtWidgets`.

If you add a feature that needs one of those modules (e.g. an embedded web
view), remove the matching entry from the `excludes` list in
`packaging/bidoytu.spec`.

## Notes

- `collect_all("mitmproxy")` is kept because mitmproxy loads several submodules
  dynamically that PyInstaller's static analysis can miss.
- The PySide6 PyInstaller hook still bundles the Qt platform plugins the app
  needs, even with the excludes in place.
- For faster startup / single-file distribution you can also compile with
  Nuitka; see the Nuitka section below.

## Nuitka (alternative compiler)

Nuitka compiles to C for faster startup. Run from the project root.

```powershell
python -m nuitka `
  --standalone `
  --enable-plugin=pyside6 `
  --include-package=mitmproxy `
  --include-package=bidoytu `
  --output-dir=dist-release `
  --windows-console-mode=disable `
  src/bidoytu/__main__.py
```

First run compiles slowly; subsequent runs are cached.

## Publishing to PyPI (`pip install bidoytu`)

The package is published to PyPI automatically when you push a `v*` tag, via
the `publish-pypi` job in `.github/workflows/main.yml`. It uses **PyPI Trusted
Publishing (OIDC)**, so there is **no API token or secret** stored in the repo.

### One-time setup on PyPI

Do this once, before the first tagged release:

1. Create a PyPI account at https://pypi.org and verify the email.
2. Reserve the project name by adding a **pending trusted publisher** (this lets
   the first automated upload create the project):
   - PyPI -> your account -> **Publishing** -> **Add a pending publisher**.
   - Fill in:
     - PyPI Project Name: `bidoytu`
     - Owner: `Bidoytu`
     - Repository name: `Bidoytu`
     - Workflow name: `main.yml`
     - Environment name: `pypi`
3. In the GitHub repo, create an **Environment** named `pypi`
   (Settings -> Environments -> New environment). No secrets are needed; this
   just matches the `environment: pypi` in the workflow and lets you add
   approval protection later if you want.

After that, every `v*` tag builds the sdist + wheel and publishes to PyPI.

### Releasing a new version to PyPI

Same flow as the desktop release - the tag drives both:

```bash
# bump version in pyproject.toml AND src/bidoytu/__init__.py to e.g. 1.1.0
git commit -am "Release v1.1.0"
git push origin main
git tag -a v1.1.0 -m "Bidoytu v1.1.0"
git push origin v1.1.0
```

The `publish-pypi` job first checks the tag matches the `pyproject.toml`
version (failing fast if not), then uploads. PyPI **rejects re-uploading an
existing version**, so always bump the version for each release.

### Build / check the package locally

```bash
pip install -e ".[dev]"   # includes build + twine
python -m build           # writes dist/*.whl and dist/*.tar.gz
python -m twine check dist/*
```

To try the whole flow without touching the real index, publish to
**TestPyPI** first (https://test.pypi.org) by adding a matching trusted
publisher there and pointing the action at it with
`with: { repository-url: https://test.pypi.org/legacy/ }`.
