"""Application theming: light and dark modes.

Provides two things:
    - ``apply_theme(app, mode)``: sets a Qt palette + stylesheet on the whole
      QApplication so every widget follows the chosen mode.
    - ``highlight_colors(mode)``: the color set the HTTP syntax highlighter
      uses, so request/response text stays legible in either mode.

The chosen mode is persisted with :class:`~PySide6.QtCore.QSettings` so it
survives restarts.

Design language
---------------
The palette aims for a soft, professional feel rather than harsh pure-black /
pure-white contrast:
    - Dark mode uses a cool slate background (#1b1e24 family) with a muted
      indigo accent and gentle borders.
    - Light mode uses an off-white "paper" background (#f6f7f9 family) with the
      same indigo accent, so both modes feel like the same product.
Controls get rounded corners, comfortable padding, and subtle hover/pressed
states so the UI reads as calm and modern.
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

# Shared accent used across both modes so the product feels cohesive.
ACCENT = "#5b8def"        # soft indigo-blue
ACCENT_HOVER = "#6f9cf2"
ACCENT_PRESSED = "#4a7bd8"


def current_mode() -> str:
    """Return the theme mode currently applied to the application."""
    return _current_mode


# -- shared color tokens ------------------------------------------------------

# A small, named token set per mode. Keeping these in one place lets the
# stylesheets, the tab bar chips, and the highlighter stay in sync.
_TOKENS = {
    DARK: {
        "window": "#1b1e24",
        "surface": "#20242c",
        "surface_alt": "#252a33",
        "elevated": "#2a2f3a",
        "base": "#181b21",
        "base_alt": "#1e222a",
        "border": "#333a45",
        "border_soft": "#2a3039",
        "text": "#e4e7ec",
        "text_muted": "#9aa2b1",
        "text_faint": "#6b7280",
        "accent": ACCENT,
    },
    LIGHT: {
        "window": "#f6f7f9",
        "surface": "#ffffff",
        "surface_alt": "#eef1f5",
        "elevated": "#ffffff",
        "base": "#ffffff",
        "base_alt": "#f4f6f8",
        "border": "#d8dee6",
        "border_soft": "#e5e9ef",
        "text": "#1f2430",
        "text_muted": "#5b6472",
        "text_faint": "#98a1b0",
        "accent": ACCENT,
    },
}


def tokens(mode: str) -> dict[str, str]:
    """Return the named color tokens for ``mode`` (falls back to dark)."""
    return _TOKENS.get(mode, _TOKENS[DARK])


# -- highlighter palettes -----------------------------------------------------

# Colors chosen for good contrast against each mode's editor background.
_HIGHLIGHT = {
    DARK: {
        "method": "#6cb2ff",
        "header_name": "#b39dff",
        "header_value": "#5fd39a",
        "status": "#ff8a8a",
    },
    LIGHT: {
        "method": "#2065d8",
        "header_name": "#7b4fd0",
        "header_value": "#1c8a52",
        "status": "#cf3b3b",
    },
}


def highlight_colors(mode: str) -> dict[str, str]:
    """Return the highlighter color set for ``mode`` (falls back to dark)."""
    return _HIGHLIGHT.get(mode, _HIGHLIGHT[DARK])


# Row-selection highlight, used by the history table delegate for column 0.
_SELECTION = {DARK: ACCENT, LIGHT: ACCENT}
_SELECTION_TEXT = {DARK: "#ffffff", LIGHT: "#ffffff"}


def selection_color(mode: str) -> str:
    return _SELECTION.get(mode, _SELECTION[DARK])


def selection_text_color(mode: str) -> str:
    return _SELECTION_TEXT.get(mode, _SELECTION_TEXT[DARK])


# -- Qt palettes --------------------------------------------------------------


def _palette_from_tokens(t: dict[str, str]) -> QPalette:
    p = QPalette()
    text = QColor(t["text"])
    disabled = QColor(t["text_faint"])

    p.setColor(QPalette.Window, QColor(t["window"]))
    p.setColor(QPalette.WindowText, text)
    p.setColor(QPalette.Base, QColor(t["base"]))
    p.setColor(QPalette.AlternateBase, QColor(t["base_alt"]))
    p.setColor(QPalette.ToolTipBase, QColor(t["elevated"]))
    p.setColor(QPalette.ToolTipText, text)
    p.setColor(QPalette.Text, text)
    p.setColor(QPalette.Button, QColor(t["surface"]))
    p.setColor(QPalette.ButtonText, text)
    p.setColor(QPalette.BrightText, QColor("#ff6b6b"))
    p.setColor(QPalette.Link, QColor(t["accent"]))
    p.setColor(QPalette.Highlight, QColor(t["accent"]))
    p.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    p.setColor(QPalette.PlaceholderText, QColor(t["text_faint"]))
    # Used by the message-view line-number gutter pen.
    p.setColor(QPalette.Mid, QColor(t["text_faint"]))

    p.setColor(QPalette.Disabled, QPalette.Text, disabled)
    p.setColor(QPalette.Disabled, QPalette.ButtonText, disabled)
    p.setColor(QPalette.Disabled, QPalette.WindowText, disabled)
    return p


def _dark_palette() -> QPalette:
    return _palette_from_tokens(_TOKENS[DARK])


def _light_palette() -> QPalette:
    return _palette_from_tokens(_TOKENS[LIGHT])


# -- stylesheets --------------------------------------------------------------


def _build_qss(t: dict[str, str]) -> str:
    """Compose a stylesheet from a mode's token set."""
    return f"""
* {{
    font-size: 13px;
}}

QWidget {{
    background-color: {t['window']};
    color: {t['text']};
}}

QToolTip {{
    color: {t['text']};
    background-color: {t['elevated']};
    border: 1px solid {t['border']};
    border-radius: 6px;
    padding: 5px 8px;
}}

/* -- Tabs ---------------------------------------------------------------- */
QTabWidget::pane {{
    border: 1px solid {t['border_soft']};
    border-radius: 8px;
    top: -1px;
    background-color: {t['surface']};
}}
QTabBar {{
    qproperty-drawBase: 0;
    background: transparent;
}}
QTabBar::tab {{
    background: transparent;
    color: {t['text_muted']};
    padding: 8px 18px;
    margin-right: 2px;
    border: 1px solid transparent;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
}}
QTabBar::tab:hover {{
    color: {t['text']};
    background: {t['surface_alt']};
}}
QTabBar::tab:selected {{
    color: {t['text']};
    background: {t['surface']};
    border: 1px solid {t['border_soft']};
    border-bottom: 2px solid {t['accent']};
}}

/* -- Table / headers ----------------------------------------------------- */
QHeaderView::section {{
    background-color: {t['surface_alt']};
    color: {t['text_muted']};
    padding: 6px 8px;
    border: none;
    border-right: 1px solid {t['border_soft']};
    border-bottom: 1px solid {t['border']};
    font-weight: 600;
}}
QHeaderView::section:hover {{
    color: {t['text']};
}}
QTableView {{
    background-color: {t['base']};
    alternate-background-color: {t['base_alt']};
    gridline-color: {t['border_soft']};
    border: 1px solid {t['border_soft']};
    border-radius: 8px;
    outline: 0;
    selection-background-color: {t['accent']};
    selection-color: #ffffff;
}}
QTableView::item {{
    border: none;
    padding: 2px 4px;
}}
QTableView::item:selected {{ background: transparent; color: {t['text']}; }}
QTableView::item:focus {{ background: transparent; border: none; }}

/* -- Text inputs / editors ---------------------------------------------- */
QPlainTextEdit, QTextEdit {{
    background-color: {t['base']};
    color: {t['text']};
    border: 1px solid {t['border_soft']};
    border-radius: 8px;
    padding: 4px;
    selection-background-color: {t['accent']};
    selection-color: #ffffff;
}}
QLineEdit, QSpinBox {{
    background-color: {t['base']};
    color: {t['text']};
    border: 1px solid {t['border']};
    border-radius: 6px;
    padding: 5px 8px;
    selection-background-color: {t['accent']};
    selection-color: #ffffff;
}}
QLineEdit:focus, QSpinBox:focus, QPlainTextEdit:focus, QTextEdit:focus {{
    border: 1px solid {t['accent']};
}}
QLineEdit:disabled, QSpinBox:disabled {{
    color: {t['text_faint']};
    background-color: {t['surface_alt']};
}}

/* -- Buttons ------------------------------------------------------------- */
QPushButton {{
    background-color: {t['surface']};
    color: {t['text']};
    border: 1px solid {t['border']};
    padding: 6px 14px;
    border-radius: 7px;
    font-weight: 600;
}}
QPushButton:hover {{
    background-color: {t['surface_alt']};
    border: 1px solid {t['accent']};
}}
QPushButton:pressed {{
    background-color: {ACCENT_PRESSED};
    color: #ffffff;
    border: 1px solid {ACCENT_PRESSED};
}}
QPushButton:disabled {{
    color: {t['text_faint']};
    background-color: {t['surface']};
    border: 1px solid {t['border_soft']};
}}
QPushButton:default {{
    background-color: {t['accent']};
    color: #ffffff;
    border: 1px solid {t['accent']};
}}
QPushButton:default:hover {{
    background-color: {ACCENT_HOVER};
    border: 1px solid {ACCENT_HOVER};
}}

/* -- Checkboxes / combos ------------------------------------------------- */
QCheckBox, QRadioButton {{ spacing: 6px; }}
QComboBox {{
    background-color: {t['base']};
    color: {t['text']};
    border: 1px solid {t['border']};
    border-radius: 6px;
    padding: 5px 8px;
}}
QComboBox:hover {{ border: 1px solid {t['accent']}; }}
QComboBox QAbstractItemView {{
    background-color: {t['elevated']};
    color: {t['text']};
    border: 1px solid {t['border']};
    selection-background-color: {t['accent']};
    selection-color: #ffffff;
    outline: 0;
}}

/* -- Menus --------------------------------------------------------------- */
QMenu {{
    background-color: {t['elevated']};
    color: {t['text']};
    border: 1px solid {t['border']};
    border-radius: 8px;
    padding: 4px;
}}
QMenu::item {{
    padding: 6px 22px;
    border-radius: 5px;
}}
QMenu::item:selected {{ background-color: {t['accent']}; color: #ffffff; }}
QMenu::separator {{
    height: 1px;
    background: {t['border_soft']};
    margin: 4px 8px;
}}
QMenuBar {{
    background-color: {t['window']};
    color: {t['text']};
    border-bottom: 1px solid {t['border_soft']};
}}
QMenuBar::item {{
    padding: 6px 12px;
    background: transparent;
    border-radius: 6px;
}}
QMenuBar::item:selected {{ background-color: {t['surface_alt']}; }}

/* -- Splitter ------------------------------------------------------------ */
QSplitter::handle {{ background: transparent; }}
QSplitter::handle:hover {{ background: {t['accent']}; }}
QSplitter::handle:horizontal {{ width: 6px; }}
QSplitter::handle:vertical {{ height: 6px; }}

/* -- Scrollbars ---------------------------------------------------------- */
QScrollBar:vertical {{
    background: transparent;
    width: 12px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {t['border']};
    min-height: 28px;
    border-radius: 6px;
    margin: 2px;
}}
QScrollBar::handle:vertical:hover {{ background: {t['text_faint']}; }}
QScrollBar:horizontal {{
    background: transparent;
    height: 12px;
    margin: 0;
}}
QScrollBar::handle:horizontal {{
    background: {t['border']};
    min-width: 28px;
    border-radius: 6px;
    margin: 2px;
}}
QScrollBar::handle:horizontal:hover {{ background: {t['text_faint']}; }}
QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}

/* -- Misc ---------------------------------------------------------------- */
QLabel {{ background: transparent; }}
QGroupBox {{
    border: 1px solid {t['border_soft']};
    border-radius: 8px;
    margin-top: 10px;
    padding-top: 8px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
    color: {t['text_muted']};
}}
"""


_DARK_QSS = _build_qss(_TOKENS[DARK])
_LIGHT_QSS = _build_qss(_TOKENS[LIGHT])


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
