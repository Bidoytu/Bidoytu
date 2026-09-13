"""Locators for bundled resources (icons, images).

Resources live under ``bidoytu/assets`` so they ship with the package. When
frozen by PyInstaller the same relative layout is preserved (the spec bundles
the assets dir), so :func:`asset_path` resolves correctly in both cases.
"""
from __future__ import annotations

import sys
from pathlib import Path


def _assets_dir() -> Path:
    # When frozen, PyInstaller unpacks data files under ``sys._MEIPASS``.
    base = getattr(sys, "_MEIPASS", None)
    if base:
        return Path(base) / "bidoytu" / "assets"
    return Path(__file__).resolve().parent / "assets"


def asset_path(name: str) -> Path:
    """Return the absolute path to a bundled asset by file name."""
    return _assets_dir() / name


def logo_path() -> Path:
    """Absolute path to the application logo."""
    return asset_path("logo.png")
