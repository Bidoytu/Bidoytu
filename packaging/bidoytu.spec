# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for development builds.

Build from the project root with:
    pyinstaller packaging/bidoytu.spec

mitmproxy ships data files and has several hidden imports; ``collect_all``
gathers them so the frozen app can start the proxy.
"""
from PyInstaller.utils.hooks import collect_all

datas = []
binaries = []
hiddenimports = []

for pkg in ("mitmproxy", "PySide6"):
    d, b, h = collect_all(pkg)
    datas += d
    binaries += b
    hiddenimports += h


a = Analysis(
    ["../src/bidoytu/__main__.py"],
    pathex=["../src"],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="bidoytu",
    console=False,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    name="bidoytu",
)
