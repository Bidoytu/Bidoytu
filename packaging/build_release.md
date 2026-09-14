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

Development changes should land in staging first. The workflow does not
publish releases for staging; promote only reviewed, release-ready changes
to main.

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
