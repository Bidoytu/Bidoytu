# Release builds (Nuitka)

Nuitka compiles the app to C for faster startup and better distribution.
Run from the project root.

## Windows

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

## Notes

- `--enable-plugin=pyside6` handles Qt plugin bundling.
- `--include-package=mitmproxy` is required because mitmproxy loads several
  submodules dynamically that Nuitka's static analysis can miss.
- First run compiles slowly; subsequent runs are cached.
- For development iteration, prefer PyInstaller (see `bidoytu.spec`).
