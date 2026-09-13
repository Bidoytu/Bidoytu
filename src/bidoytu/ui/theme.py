"""Application theming: light and dark modes.

Provides two things:
    - ``apply_theme(app, mode)``: sets a Qt palette + stylesheet on the whole
      QApplication so every widget follows the chosen mode.
    - ``highlight_colors(mode)``: the color set the HTTP syntax highlighter
      uses, so request/response text stays legible in either mode.

The chosen mode is persisted with :class:`~PySide6.QtCore.QSettings` so it
survives restarts.
"""
from __future__ import annotations

from PySide6.QtCore import QSettings
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

LIGHT = "light"
DARK = "dark"

_SETTINGS_ORG = "Bidoytu"
_SETTINGS_APP = "Bidoytu"
_SETTINGS_KEY = "ui/theme"

# The mode currently applied to the app. Widgets created after apply_theme()
# (e.g. syntax highlighters) read this to pick matching colors.
_current_mode = DARK


def current_mode() -> str:
    """Return the theme mode currently applied to the application."""
    return _current_mode


# -- highlighter palettes -----------------------------------------------------

# Colors chosen for good contrast against each mode's editor background.
_HIGHLIGHT = {
    DARK: {
        "method": "#4aa3ff",
        "header_name": "#9d86ff",
        "header_value": "#3ec07a",
        "status": "#ff6b6b",
    },
    LIGHT: {
        "method": "#0a5fd0",
        "header_name": "#6f42c1",
        "header_value": "#137a3f",
        "status": "#c02b2b",
    },
}


def highlight_colors(mode: str) -> dict[str, str]:
    """Return the highlighter color set for ``mode`` (falls back to dark)."""
    return _HIGHLIGHT.get(mode, _HIGHLIGHT[DARK])


# Row-selection highlight, used by the history table delegate for column 0.
_SELECTION = {DARK: "#2f6fed", LIGHT: "#2f6fed"}
_SELECTION_TEXT = {DARK: "#ffffff", LIGHT: "#ffffff"}


def selection_color(mode: str) -> str:
    return _SELECTION.get(mode, _SELECTION[DARK])


def selection_text_color(mode: str) -> str:
    return _SELECTION_TEXT.get(mode, _SELECTION_TEXT[DARK])


# -- Qt palettes --------------------------------------------------------------


def _dark_palette() -> QPalette:
    p = QPalette()
    window = QColor("#2b2b2b")
    base = QColor("#1e1e1e")
    alt_base = QColor("#262626")
    text = QColor("#e6e6e6")
    disabled = QColor("#7a7a7a")
    highlight = QColor("#2f6fed")

    p.setColor(QPalette.Window, window)
    p.setColor(QPalette.WindowText, text)
    p.setColor(QPalette.Base, base)
    p.setColor(QPalette.AlternateBase, alt_base)
    p.setColor(QPalette.ToolTipBase, QColor("#3a3a3a"))
    p.setColor(QPalette.ToolTipText, text)
    p.setColor(QPalette.Text, text)
    p.setColor(QPalette.Button, window)
    p.setColor(QPalette.ButtonText, text)
    p.setColor(QPalette.BrightText, QColor("#ff5555"))
    p.setColor(QPalette.Link, QColor("#4aa3ff"))
    p.setColor(QPalette.Highlight, highlight)
    p.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    p.setColor(QPalette.PlaceholderText, disabled)

    p.setColor(QPalette.Disabled, QPalette.Text, disabled)
    p.setColor(QPalette.Disabled, QPalette.ButtonText, disabled)
    p.setColor(QPalette.Disabled, QPalette.WindowText, disabled)
    return p


def _light_palette() -> QPalette:
    p = QPalette()
    window = QColor("#f2f2f2")
    base = QColor("#ffffff")
    alt_base = QColor("#f5f6f8")
    text = QColor("#1b1b1b")
    disabled = QColor("#9a9a9a")
    highlight = QColor("#2f6fed")

    p.setColor(QPalette.Window, window)
    p.setColor(QPalette.WindowText, text)
    p.setColor(QPalette.Base, base)
    p.setColor(QPalette.AlternateBase, alt_base)
    p.setColor(QPalette.ToolTipBase, QColor("#ffffdc"))
    p.setColor(QPalette.ToolTipText, text)
    p.setColor(QPalette.Text, text)
    p.setColor(QPalette.Button, window)
    p.setColor(QPalette.ButtonText, text)
    p.setColor(QPalette.BrightText, QColor("#c02b2b"))
    p.setColor(QPalette.Link, QColor("#0a5fd0"))
    p.setColor(QPalette.Highlight, highlight)
    p.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    p.setColor(QPalette.PlaceholderText, disabled)

    p.setColor(QPalette.Disabled, QPalette.Text, disabled)
    p.setColor(QPalette.Disabled, QPalette.ButtonText, disabled)
    p.setColor(QPalette.Disabled, QPalette.WindowText, disabled)
    return p


# -- stylesheets --------------------------------------------------------------

_DARK_QSS = """
QToolTip { color: #e6e6e6; background-color: #3a3a3a; border: 1px solid #555; }
QTabWidget::pane { border: 1px solid #3c3c3c; }
QTabBar::tab {
    background: #2b2b2b; color: #cfcfcf; padding: 6px 14px; border: 1px solid #3c3c3c;
    border-bottom: none;
}
QTabBar::tab:selected { background: #1e1e1e; color: #ffffff; }
QHeaderView::section {
    background-color: #333333; color: #e6e6e6; padding: 4px;
    border: none; border-right: 1px solid #3c3c3c; border-bottom: 1px solid #3c3c3c;
}
QTableView {
    background-color: #1e1e1e; alternate-background-color: #262626;
    gridline-color: #3c3c3c; outline: 0;
}
QTableView::item { border: none; }
QTableView::item:selected { background: transparent; color: #e6e6e6; }
QTableView::item:focus { background: transparent; border: none; }
QPlainTextEdit, QLineEdit, QSpinBox { background-color: #1e1e1e; color: #e6e6e6; border: 1px solid #3c3c3c; }
QPushButton { background-color: #3a3a3a; color: #e6e6e6; border: 1px solid #4a4a4a; padding: 4px 10px; border-radius: 3px; }
QPushButton:hover { background-color: #454545; }
QPushButton:pressed { background-color: #2f6fed; color: #ffffff; }
QPushButton:disabled { color: #7a7a7a; background-color: #2e2e2e; }
QMenu { background-color: #2b2b2b; color: #e6e6e6; border: 1px solid #3c3c3c; }
QMenu::item:selected { background-color: #2f6fed; color: #ffffff; }
QMenuBar { background-color: #2b2b2b; color: #e6e6e6; }
QMenuBar::item:selected { background-color: #3a3a3a; }
"""

_LIGHT_QSS = """
QToolTip { color: #1b1b1b; background-color: #ffffdc; border: 1px solid #c9c9c9; }
QTabWidget::pane { border: 1px solid #cfcfcf; }
QTabBar::tab {
    background: #e8e8e8; color: #333333; padding: 6px 14px; border: 1px solid #cfcfcf;
    border-bottom: none;
}
QTabBar::tab:selected { background: #ffffff; color: #000000; }
QHeaderView::section {
    background-color: #e9eaed; color: #1b1b1b; padding: 4px;
    border: none; border-right: 1px solid #d5d5d5; border-bottom: 1px solid #d5d5d5;
}
QTableView {
    background-color: #ffffff; alternate-background-color: #f5f6f8;
    gridline-color: #e0e0e0; outline: 0;
}
QTableView::item { border: none; }
QTableView::item:selected { background: transparent; color: #1b1b1b; }
QTableView::item:focus { background: transparent; border: none; }
QPlainTextEdit, QLineEdit, QSpinBox { background-color: #ffffff; color: #1b1b1b; border: 1px solid #c9c9c9; }
QPushButton { background-color: #f0f0f0; color: #1b1b1b; border: 1px solid #c2c2c2; padding: 4px 10px; border-radius: 3px; }
QPushButton:hover { background-color: #e6e6e6; }
QPushButton:pressed { background-color: #2f6fed; color: #ffffff; }
QPushButton:disabled { color: #9a9a9a; background-color: #ececec; }
QMenu { background-color: #ffffff; color: #1b1b1b; border: 1px solid #c9c9c9; }
QMenu::item:selected { background-color: #2f6fed; color: #ffffff; }
QMenuBar { background-color: #f2f2f2; color: #1b1b1b; }
QMenuBar::item:selected { background-color: #e0e0e0; }
"""


def apply_theme(app: QApplication, mode: str) -> None:
    """Apply ``mode`` ('light' or 'dark') to the whole application."""
    global _current_mode
    _current_mode = LIGHT if mode == LIGHT else DARK
    if _current_mode == LIGHT:
        app.setPalette(_light_palette())
        app.setStyleSheet(_LIGHT_QSS)
    else:
        app.setPalette(_dark_palette())
        app.setStyleSheet(_DARK_QSS)


# -- persistence --------------------------------------------------------------


def load_theme() -> str:
    """Return the persisted theme, defaulting to dark."""
    settings = QSettings(_SETTINGS_ORG, _SETTINGS_APP)
    mode = settings.value(_SETTINGS_KEY, DARK)
    return LIGHT if str(mode).lower() == LIGHT else DARK


def save_theme(mode: str) -> None:
    """Persist the chosen theme."""
    settings = QSettings(_SETTINGS_ORG, _SETTINGS_APP)
    settings.setValue(_SETTINGS_KEY, LIGHT if mode == LIGHT else DARK)
