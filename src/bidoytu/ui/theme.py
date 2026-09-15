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
    - Light mode uses an off-white "paper" background (#fafafa) with soft
      lavender-grey surfaces (#e4e5f1) and dark-indigo text (#484b6a), sharing
      the same indigo accent so both modes feel like the same product.
Controls get rounded corners, comfortable padding, and subtle hover/pressed
states so the UI reads as calm and modern.
"""
from __future__ import annotations

import hashlib
import os
import tempfile

from PySide6.QtCore import QBuffer, QByteArray, QPointF, QSettings, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPalette, QPen, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QProxyStyle,
    QStyle,
    QStyleOptionViewItem,
)

LIGHT = "light"
DARK = "dark"

_SETTINGS_ORG = "Bidoytu"
_SETTINGS_APP = "Bidoytu"
_SETTINGS_KEY = "ui/theme"

# The mode currently applied to the app. Widgets created after apply_theme()
# (e.g. syntax highlighters) read this to pick matching colors.
_current_mode = DARK

# Temp directory that holds the generated icon PNGs (created lazily).
_ICON_DIR: str | None = None

# Shared accent used across both modes so the product feels cohesive.
ACCENT = "#5865f2"        # blurple
ACCENT_HOVER = "#4752c4"
ACCENT_PRESSED = "#3c45a5"


def current_mode() -> str:
    """Return the theme mode currently applied to the application."""
    return _current_mode


# -- shared color tokens ------------------------------------------------------

# A small, named token set per mode. Keeping these in one place lets the
# stylesheets, the tab bar chips, and the highlighter stay in sync.
_TOKENS = {
    DARK: {
        "window":      "#202225",   # tertiary bg — sidebars, deepest layer
        "surface":     "#2f3136",   # secondary bg — channel list, panels
        "surface_alt": "#36393f",   # primary bg — main chat/content area
        "elevated":    "#18191c",   # popouts, modals — Discord's darkest layer
        "base":        "#40444b",   # message input / editor fields
        "base_alt":    "#2f3136",
        "border":      "#26282c",   # Discord barely uses visible borders
        "border_soft": "#1e1f22",
        "text":        "#dcddde",   # Discord's primary text (not pure white)
        "text_muted":  "#96989d",   # secondary/muted text
        "text_faint":  "#72767d",   # timestamps, faint labels
        "accent": ACCENT,
    },
    LIGHT: {
        "window": "#fafafa",
        "surface": "#ffffff",
        "surface_alt": "#e4e5f1",
        "elevated": "#ffffff",
        "base": "#ffffff",
        "base_alt": "#e4e5f1",
        "border": "#d2d3db",
        "border_soft": "#e4e5f1",
        "text": "#484b6a",
        "text_muted": "#484b6a",
        "text_faint": "#484b6a",
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


def _blend(fg: str, bg: str, alpha: float) -> str:
    """Blend ``fg`` over ``bg`` by ``alpha`` (0..1) and return a hex string.

    Used to derive a soft, muted selection colour: the accent mixed heavily into
    the surface so a filled selection reads as a gentle tint rather than a
    bright solid band, while staying fully opaque (so it works even where Qt
    ignores alpha on palette brushes).
    """
    f = QColor(fg)
    b = QColor(bg)
    r = round(f.red() * alpha + b.red() * (1 - alpha))
    g = round(f.green() * alpha + b.green() * (1 - alpha))
    bl = round(f.blue() * alpha + b.blue() * (1 - alpha))
    return QColor(r, g, bl).name()


# Muted selection fill for the palette Highlight (used by Fusion to fill
# selected rows, text selection, dropdowns...). A soft tint of the accent, not
# the bright solid blue.
_HIGHLIGHT_BG = {
    DARK: _blend(ACCENT, _TOKENS[DARK]["surface"], 0.38),
    LIGHT: _blend(ACCENT, _TOKENS[LIGHT]["surface"], 0.30),
}
# Text colour to use on top of that muted highlight, kept readable rather than
# forcing white on a light-ish tint.
_HIGHLIGHT_TEXT = {DARK: "#ffffff", LIGHT: _TOKENS[LIGHT]["text"]}


def highlight_bg(mode: str) -> str:
    return _HIGHLIGHT_BG.get(mode, _HIGHLIGHT_BG[DARK])


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
    # Muted selection fill (soft tint of the accent) so Fusion doesn't paint a
    # bright solid-blue band over selected rows / text.
    mode = LIGHT if t is _TOKENS[LIGHT] else DARK
    p.setColor(QPalette.Highlight, QColor(highlight_bg(mode)))
    p.setColor(QPalette.HighlightedText, QColor(_HIGHLIGHT_TEXT[mode]))
    # Selection colour when the widget is not focused: keep it identical so the
    # row doesn't flash a different (often brighter) inactive-highlight colour.
    p.setColor(QPalette.Inactive, QPalette.Highlight, QColor(highlight_bg(mode)))
    p.setColor(QPalette.Inactive, QPalette.HighlightedText, QColor(_HIGHLIGHT_TEXT[mode]))
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

# Tiny icons rendered to PNG data: URIs with QPainter. We deliberately do NOT
# use SVG here: the Qt SVG image plugin (qsvg) is not guaranteed to be present
# (it is missing in some PySide6 wheels / frozen builds), and when it is absent
# every ``image: url(data:image/svg+xml,...)`` silently renders as *nothing* --
# which is exactly what made checkboxes and combo/spin arrows appear blank.
# PNG decoding is always available, so these icons render everywhere.


def _icon_dir() -> str:
    """A stable per-session directory where icon PNGs are written."""
    global _ICON_DIR
    if _ICON_DIR is None:
        _ICON_DIR = tempfile.mkdtemp(prefix="bidoytu-icons-")
    return _ICON_DIR


def _pixmap_uri(pixmap: QPixmap) -> str:
    """Write ``pixmap`` to a PNG file and return a stylesheet ``url("...")``.

    We use a real file on disk rather than a ``data:`` URI: Qt's *stylesheet*
    ``url()`` resolver does not reliably decode ``data:`` URIs across all
    platforms (it works under the offscreen platform but can render nothing on
    native Windows), whereas a plain file path always works. The PNG bytes are
    content-hashed so identical icons share one file and repeated theme applies
    don't pile up files.
    """
    data = QByteArray()
    buffer = QBuffer(data)
    buffer.open(QBuffer.WriteOnly)
    pixmap.save(buffer, "PNG")
    buffer.close()
    raw = bytes(data)

    digest = hashlib.sha1(raw).hexdigest()[:16]
    path = os.path.join(_icon_dir(), f"{digest}.png")
    if not os.path.exists(path):
        with open(path, "wb") as fh:
            fh.write(raw)
    # Qt stylesheets want forward slashes even on Windows.
    return 'url("' + path.replace("\\", "/") + '")'


# Supersample factor: icons are painted at SCALE times their logical size for
# crisp anti-aliased edges, then the stylesheet scales them back down via the
# sub-control width/height. We do NOT set a device-pixel-ratio on the pixmap:
# doing so makes Qt treat it as high-DPI and, combined with the painter scale,
# collapses thin strokes to nothing (that was the invisible-arrow bug).
_ICON_SCALE = 4


def _blank_pixmap(w: int, h: int) -> QPixmap:
    """A transparent pixmap sized ``w``x``h`` logical pixels, supersampled."""
    px = QPixmap(w * _ICON_SCALE, h * _ICON_SCALE)
    px.fill(Qt.transparent)
    return px


def _check_icon(fill: str, tick: str = "#ffffff") -> str:
    """A filled, rounded checkbox tile with a tick.

    Setting ``image:`` on ``QCheckBox::indicator`` replaces the whole indicator
    rendering (background/border are ignored), so the accent tile must be part
    of the icon itself, with the tick drawn on top.
    """
    size = 16
    px = _blank_pixmap(size, size)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing, True)
    p.scale(_ICON_SCALE, _ICON_SCALE)
    p.setPen(Qt.NoPen)
    p.setBrush(QColor(fill))
    p.drawRoundedRect(0, 0, size, size, 4, 4)
    pen = QPen(QColor(tick))
    pen.setWidthF(2)
    pen.setCapStyle(Qt.RoundCap)
    pen.setJoinStyle(Qt.RoundJoin)
    p.setPen(pen)
    path = QPainterPath(QPointF(3.5, 8.4))
    path.lineTo(6.5, 11.4)
    path.lineTo(12.5, 4.6)
    p.drawPath(path)
    p.end()
    return _pixmap_uri(px)


def _chevron_icon(color: str, *, up: bool) -> str:
    """A small up/down chevron used by combo boxes, spin boxes and menus."""
    size = 12
    px = _blank_pixmap(size, size)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing, True)
    p.scale(_ICON_SCALE, _ICON_SCALE)
    pen = QPen(QColor(color))
    pen.setWidthF(1.8)
    pen.setCapStyle(Qt.RoundCap)
    pen.setJoinStyle(Qt.RoundJoin)
    p.setPen(pen)
    if up:
        path = QPainterPath(QPointF(2.5, 7.5))
        path.lineTo(6, 4)
        path.lineTo(9.5, 7.5)
    else:
        path = QPainterPath(QPointF(2.5, 4.5))
        path.lineTo(6, 8)
        path.lineTo(9.5, 4.5)
    p.drawPath(path)
    p.end()
    return _pixmap_uri(px)


def _chevron_down_icon(color: str) -> str:
    return _chevron_icon(color, up=False)


def _chevron_up_icon(color: str) -> str:
    return _chevron_icon(color, up=True)


def _close_icon(color: str, bg: str | None = None) -> str:
    """A crisp "x" glyph for tab close buttons.

    When ``bg`` is given, a rounded background tile is drawn behind the glyph
    (used for the hover state so the button reads as a real, clickable pill).
    """
    size = 16
    px = _blank_pixmap(size, size)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing, True)
    p.scale(_ICON_SCALE, _ICON_SCALE)
    if bg is not None:
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(bg))
        p.drawRoundedRect(0, 0, size, size, 4, 4)
    pen = QPen(QColor(color))
    pen.setWidthF(1.6)
    pen.setCapStyle(Qt.RoundCap)
    m = 5  # margin: leaves a balanced 6px glyph centered in the 16px tile
    p.setPen(pen)
    p.drawLine(QPointF(m, m), QPointF(size - m, size - m))
    p.drawLine(QPointF(size - m, m), QPointF(m, size - m))
    p.end()
    return _pixmap_uri(px)


def ui_icon(name: str, color: str | None = None) -> QIcon:
    """Return a font-independent icon for compact UI controls."""
    t = tokens(current_mode())
    normal = color or t["text"]
    active = t["accent"]
    disabled = t["text_faint"]

    def make(stroke: str) -> QPixmap:
        size = 18
        px = _blank_pixmap(size, size)
        p = QPainter(px)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.scale(_ICON_SCALE, _ICON_SCALE)
        pen = QPen(QColor(stroke))
        pen.setWidthF(1.8)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        p.setPen(pen)
        lines = {
            "left": ((11.5, 3.5, 5.5, 9), (5.5, 9, 11.5, 14.5)),
            "right": ((6.5, 3.5, 12.5, 9), (12.5, 9, 6.5, 14.5)),
            "up": ((3.5, 11.5, 9, 5.5), (9, 5.5, 14.5, 11.5)),
            "down": ((3.5, 6.5, 9, 12.5), (9, 12.5, 14.5, 6.5)),
            "close": ((5, 5, 13, 13), (13, 5, 5, 13)),
        }
        try:
            icon_lines = lines[name]
        except KeyError as exc:
            raise ValueError(f"Unknown UI icon: {name}") from exc
        for x1, y1, x2, y2 in icon_lines:
            p.drawLine(QPointF(x1, y1), QPointF(x2, y2))
        p.end()
        return px

    result = QIcon()
    result.addPixmap(make(normal), QIcon.Normal, QIcon.Off)
    result.addPixmap(make(active), QIcon.Active, QIcon.Off)
    result.addPixmap(make(disabled), QIcon.Disabled, QIcon.Off)
    return result


def _build_qss(t: dict[str, str]) -> str:
    """Compose a stylesheet from a mode's token set."""
    check = _check_icon(ACCENT)
    check_hover = _check_icon(ACCENT_HOVER)
    # Use the full-strength text colour for arrows so they read clearly against
    # the button fill (text_muted was too faint to see).
    chevron_down = _chevron_down_icon(t["text"])
    chevron_down_hi = _chevron_down_icon(t["accent"])
    chevron_down_faint = _chevron_down_icon(t["text_faint"])
    chevron_up = _chevron_up_icon(t["text"])
    close_icon = _close_icon(t["text_muted"])
    close_icon_hover = _close_icon("#ffffff", bg="#d9534f")
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
QTabBar::close-button {{
    /* Our own crisp "x" glyph (PNG, not the style default) with a red pill on
       hover, matching the Repeater chip close buttons. */
    image: {close_icon};
    subcontrol-position: right;
    margin: 3px 4px 3px 2px;
    width: 16px;
    height: 16px;
}}
QTabBar::close-button:hover {{
    image: {close_icon_hover};
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
}}

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
/* Text inputs (single-line) keep a subtle accent ring on focus, but the
   large message editors (request/response panes) get no focus border at all. */
QLineEdit:focus, QSpinBox:focus {{
    border: 1px solid {t['accent']};
}}
QPlainTextEdit:focus, QTextEdit:focus {{
    border: 1px solid {t['border_soft']};
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
QPushButton::menu-indicator {{
    image: {chevron_down};
    subcontrol-origin: padding;
    subcontrol-position: center right;
    width: 12px;
    height: 12px;
    right: 7px;
}}
QPushButton::menu-indicator:pressed {{ image: {chevron_down_hi}; }}
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
    background-color: {t['surface_alt']};
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

/* -- Checkboxes / radios ------------------------------------------------- */
QCheckBox, QRadioButton {{ spacing: 7px; background: transparent; }}
QCheckBox::indicator, QRadioButton::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {t['border']};
    background: {t['base']};
}}
QCheckBox::indicator {{ border-radius: 4px; }}
QRadioButton::indicator {{ border-radius: 9px; }}
QCheckBox::indicator:hover, QRadioButton::indicator:hover {{
    border: 1px solid {t['accent']};
}}
QCheckBox::indicator:checked {{
    /* image replaces the whole indicator, so the accent tile + tick are baked
       into the SVG. border stays for a crisp edge. */
    border: 1px solid {t['accent']};
    image: {check};
}}
QCheckBox::indicator:checked:hover {{
    border: 1px solid {ACCENT_HOVER};
    image: {check_hover};
}}
QRadioButton::indicator:checked {{
    background: {t['accent']};
    border: 4px solid {t['base']};
}}
QCheckBox::indicator:indeterminate {{
    background: {t['accent']};
    border: 1px solid {t['accent']};
}}
QCheckBox:disabled, QRadioButton:disabled {{ color: {t['text_faint']}; }}

/* -- Combo boxes --------------------------------------------------------- */
QComboBox {{
    background-color: {t['base']};
    color: {t['text']};
    border: 1px solid {t['border']};
    border-radius: 6px;
    padding: 5px 8px;
    padding-right: 26px;
}}
QComboBox:hover {{ border: 1px solid {t['accent']}; }}
QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: center right;
    width: 22px;
    border: none;
    background: transparent;
}}
QComboBox::down-arrow {{
    image: {chevron_down};
    width: 12px;
    height: 12px;
    margin-right: 8px;
}}
QComboBox::down-arrow:hover {{ image: {chevron_down_hi}; }}
QComboBox::down-arrow:on {{ image: {chevron_up}; }}
QComboBox QAbstractItemView {{
    background-color: {t['elevated']};
    color: {t['text']};
    border: 1px solid {t['border']};
    selection-background-color: {t['accent']};
    selection-color: #ffffff;
    outline: 0;
}}

/* -- Spin boxes ---------------------------------------------------------- */
QSpinBox, QDoubleSpinBox {{
    background-color: {t['base']};
    color: {t['text']};
    border: 1px solid {t['border']};
    border-radius: 6px;
    padding: 4px 6px;
    padding-right: 20px;
}}
QSpinBox:focus, QDoubleSpinBox:focus {{ border: 1px solid {t['accent']}; }}
QSpinBox::up-button, QDoubleSpinBox::up-button {{
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 18px;
    border-left: 1px solid {t['border_soft']};
    background: {t['surface_alt']};
    border-top-right-radius: 6px;
}}
QSpinBox::down-button, QDoubleSpinBox::down-button {{
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 18px;
    border-left: 1px solid {t['border_soft']};
    background: {t['surface_alt']};
    border-bottom-right-radius: 6px;
}}
QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
    background: {t['elevated']};
}}
QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{
    image: {chevron_up};
    width: 11px;
    height: 11px;
}}
QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{
    image: {chevron_down};
    width: 11px;
    height: 11px;
}}

/* -- Tool buttons (e.g. Repeater "Send" with dropdown) ------------------- */
QToolButton {{
    background-color: {t['surface']};
    color: {t['text']};
    border: 1px solid {t['border']};
    border-radius: 7px;
    /* Extra right padding (~ the 18px menu-button width) so the label sits
       optically centred over the whole button rather than being pushed left
       by the dropdown arrow section. */
    padding: 6px 30px 6px 12px;
    font-weight: 600;
}}
QToolButton:hover {{ background-color: {t['surface_alt']}; border: 1px solid {t['accent']}; }}
QToolButton:pressed {{ background-color: {ACCENT_PRESSED}; color: #ffffff; }}
QToolButton:disabled {{ color: {t['text_faint']}; background-color: {t['surface_alt']}; border: 1px solid {t['border_soft']}; }}
QToolButton::menu-button:disabled {{ background-color: {t['surface_alt']}; border-left: 1px solid {t['border_soft']}; }}
QToolButton::menu-arrow:disabled {{ image: {chevron_down_faint}; }}
/* Inactive Send button: visible but inert (no request yet). Painted with the
   disabled cue while the widget stays enabled so its dropdown still opens. */
QToolButton[inactive="true"] {{
    color: {t['text_faint']};
    background-color: {t['surface_alt']};
    border: 1px solid {t['border_soft']};
}}
QToolButton[inactive="true"]:hover {{
    background-color: {t['surface_alt']};
    border: 1px solid {t['border_soft']};
}}
QToolButton[inactive="true"]::menu-button {{
    background-color: {t['surface_alt']};
    border-left: 1px solid {t['border_soft']};
}}
QToolButton[inactive="true"]::menu-arrow {{ image: {chevron_down_faint}; }}
QToolButton::menu-button {{
    border-left: 1px solid {t['border_soft']};
    width: 18px;
    border-top-right-radius: 7px;
    border-bottom-right-radius: 7px;
}}
QToolButton::menu-arrow {{
    image: {chevron_down};
    width: 11px;
    height: 11px;
}}
QToolButton::menu-arrow:hover {{ image: {chevron_down_hi}; }}

/* -- Progress bar -------------------------------------------------------- */
QProgressBar {{
    background-color: {t['surface_alt']};
    border: 1px solid {t['border_soft']};
    border-radius: 6px;
    text-align: center;
    color: {t['text']};
    height: 16px;
}}
QProgressBar::chunk {{
    background-color: {t['accent']};
    border-radius: 5px;
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
/* Keep the handle invisible even on hover/press: no bright accent bar between
   the request/response panes while dragging. The cursor already changes to the
   resize arrow, so the handle stays discoverable without the blue highlight. */
QSplitter::handle {{ background: transparent; }}
QSplitter::handle:hover {{ background: transparent; }}
QSplitter::handle:pressed {{ background: transparent; }}
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


# The stylesheets are built lazily (and cached) rather than at import time:
# composing them renders QPixmap-based icons, which requires a live
# QApplication. apply_theme() is always called after the app is created.
_QSS_CACHE: dict[str, str] = {}


def _qss_for(mode: str) -> str:
    cached = _QSS_CACHE.get(mode)
    if cached is None:
        cached = _build_qss(_TOKENS.get(mode, _TOKENS[DARK]))
        _QSS_CACHE[mode] = cached
    return cached


class _NoFocusRectStyle(QProxyStyle):
    """Application style that suppresses the item-view focus rectangle globally.

    The dotted/coloured focus outline drawn on the current cell of a view is
    emitted by the *style*, not by item delegates, so it survives delegate-level
    ``State_HasFocus`` stripping in some platform styles (notably the Windows
    Vista style, which paints the focus frame as part of ``CE_ItemViewItem``).

    Installing this as the application base style means Qt's stylesheet style
    wraps *this* proxy, so the suppression stays in the paint chain even with a
    global stylesheet applied. Two hooks cover the styles that differ:

    * ``PE_FrameFocusRect`` - skipped entirely.
    * ``CE_ItemViewItem`` - the ``State_HasFocus`` flag is cleared before the
      base style draws the item, so no focus frame is painted.
    """

    def drawPrimitive(self, element, option, painter, widget=None) -> None:  # noqa: N802
        if element == QStyle.PE_FrameFocusRect:
            return
        super().drawPrimitive(element, option, painter, widget)

    def drawControl(self, element, option, painter, widget=None) -> None:  # noqa: N802
        if element == QStyle.CE_ItemViewItem and isinstance(
            option, QStyleOptionViewItem
        ):
            option = QStyleOptionViewItem(option)
            option.state &= ~QStyle.State_HasFocus
        super().drawControl(element, option, painter, widget)


# Guard so we only wrap the base style once, even if apply_theme runs repeatedly
# (e.g. when the user switches themes at runtime).
_focus_style_installed = False


def apply_theme(app: QApplication, mode: str) -> None:
    """Apply ``mode`` ('light' or 'dark') to the whole application."""
    global _current_mode, _focus_style_installed
    _current_mode = LIGHT if mode == LIGHT else DARK

    # Force the Fusion base style (once). The native Windows style paints item
    # selection and focus with the OS accent colour (the stray pink line the
    # user saw), which we cannot fully override. Fusion is drawn entirely by Qt
    # from OUR palette + stylesheet, so no Windows theme colour can leak in.
    # We wrap it in the focus-rect-suppressing proxy so no cell focus frame is
    # drawn either. Installed before the stylesheet so the stylesheet style
    # wraps this proxy.
    if not _focus_style_installed:
        from PySide6.QtWidgets import QStyleFactory

        fusion = QStyleFactory.create("Fusion")
        base = fusion if fusion is not None else app.style()
        app.setStyle(_NoFocusRectStyle(base))
        _focus_style_installed = True

    if _current_mode == LIGHT:
        app.setPalette(_light_palette())
        app.setStyleSheet(_qss_for(LIGHT))
    else:
        app.setPalette(_dark_palette())
        app.setStyleSheet(_qss_for(DARK))


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
