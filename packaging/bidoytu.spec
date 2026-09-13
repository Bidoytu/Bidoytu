# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for development builds.

Build from the project root with:
    pyinstaller packaging/bidoytu.spec

mitmproxy ships data files and has several hidden imports; ``collect_all``
gathers them so the frozen app can start the proxy.
"""
from PyInstaller.utils.hooks import collect_all

datas = [
    # Bundle app assets (logo) preserving the bidoytu/assets layout so
    # bidoytu.resources.asset_path() resolves them under sys._MEIPASS.
    ("../src/bidoytu/assets", "bidoytu/assets"),
]
binaries = []
hiddenimports = []

# mitmproxy loads many submodules dynamically, so collect everything for it.
d, b, h = collect_all("mitmproxy")
datas += d
binaries += b
hiddenimports += h

# The app only uses QtCore / QtGui / QtWidgets. ``collect_all("PySide6")``
# would drag in the entire Qt stack (WebEngine/Chromium ~300 MB, QML/Quick,
# Charts, 3D, Multimedia, ...), bloating the build to ~740 MB. Exclude the
# unused Qt modules so PyInstaller only bundles what's actually imported.
# The pyside6 PyInstaller hook still handles the Qt plugins we need.
excludes = [
    # Chromium-based web view: by far the biggest single contributor.
    "PySide6.QtWebEngineCore",
    "PySide6.QtWebEngineWidgets",
    "PySide6.QtWebEngineQuick",
    "PySide6.QtWebChannel",
    "PySide6.QtWebSockets",
    "PySide6.QtWebView",
    # QML / Quick stack (not used; app is pure QtWidgets).
    "PySide6.QtQml",
    "PySide6.QtQuick",
    "PySide6.QtQuick3D",
    "PySide6.QtQuickWidgets",
    "PySide6.QtQuickControls2",
    # 3D, multimedia, charts, datavis, sensors, and other unused modules.
    "PySide6.Qt3DCore",
    "PySide6.Qt3DRender",
    "PySide6.Qt3DInput",
    "PySide6.Qt3DLogic",
    "PySide6.Qt3DAnimation",
    "PySide6.Qt3DExtras",
    "PySide6.QtMultimedia",
    "PySide6.QtMultimediaWidgets",
    "PySide6.QtCharts",
    "PySide6.QtDataVisualization",
    "PySide6.QtGraphs",
    "PySide6.QtSensors",
    "PySide6.QtPositioning",
    "PySide6.QtLocation",
    "PySide6.QtBluetooth",
    "PySide6.QtNfc",
    "PySide6.QtSerialPort",
    "PySide6.QtSerialBus",
    "PySide6.QtDesigner",
    "PySide6.QtHelp",
    "PySide6.QtTest",
    "PySide6.QtSql",
    "PySide6.QtPdf",
    "PySide6.QtPdfWidgets",
    "PySide6.QtSvgWidgets",
    "PySide6.QtOpenGL",
    "PySide6.QtOpenGLWidgets",
    # numpy/scipy are pulled in transitively but unused by the app.
    "numpy",
    "scipy",
    "PIL",
]


a = Analysis(
    ["../src/bidoytu/__main__.py"],
    pathex=["../src"],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=excludes,
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
    icon="../src/bidoytu/assets/logo.png",
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    name="bidoytu",
)
