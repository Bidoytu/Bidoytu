"""A wrapping, group-aware tab bar built from individual chip widgets.

Unlike ``QTabBar``, this bar lays its tabs out with a :class:`FlowLayout`, so
chips wrap onto new rows when they reach the right edge instead of scrolling.
It also renders *group headers*: a group owns a set of tabs, shows a colored
chip with an expand/collapse arrow, and hides its member chips when collapsed.

The bar is intentionally decoupled from any content stack. It emits signals for
selection, close, rename, and context-menu requests; the owning widget
(:class:`~bidoytu.ui.repeater_tab.RepeaterTab`) maps those to a QStackedWidget
and to its grouping model.

Ordering rule for display:
    * each group, in insertion order, renders as ``[header][member][member]...``
    * ungrouped tabs render after all groups, in their own order
"""
from __future__ import annotations

from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QColor, QMouseEvent, QResizeEvent
from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QScrollArea,
    QWidget,
)

from bidoytu.ui.flow_layout import FlowLayout
from bidoytu.ui.theme import current_mode, tokens, ui_icon


class _FlowHost(QWidget):
    """Host widget whose height tracks its FlowLayout's height-for-width.

    A ``QScrollArea`` with a resizable widget sizes that widget to the viewport
    width but does not consult a layout's ``heightForWidth`` on its own. Without
    this, the flow layout collapses to a single row and chips overlap. We report
    the correct height and keep the minimum height in sync on resize.
    """

    def hasHeightForWidth(self) -> bool:
        return True

    def heightForWidth(self, width: int) -> int:
        layout = self.layout()
        if layout is not None and layout.hasHeightForWidth():
            return layout.heightForWidth(width)
        return super().heightForWidth(width)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        layout = self.layout()
        if layout is not None and layout.hasHeightForWidth():
            self.setMinimumHeight(layout.heightForWidth(self.width()))


class _Chip(QWidget):
    """A single clickable tab chip with an optional close button."""

    clicked = Signal(object)          # emits the associated key
    close_clicked = Signal(object)
    double_clicked = Signal(object)
    context_menu = Signal(object, object)  # (key, global QPoint)

    def __init__(self, key, text: str, closable: bool = True, parent=None) -> None:
        super().__init__(parent)
        self._key = key
        self._selected = False
        self._base_style = ""

        self._label = QLabel(text)
        self._label.setContentsMargins(8, 3, 6, 3)

        from PySide6.QtWidgets import QHBoxLayout, QLayout, QSizePolicy
        row = QHBoxLayout(self)
        row.setContentsMargins(2, 1, 2, 1)
        row.setSpacing(2)
        # Force the chip to always be at least as wide as its contents so the
        # flow layout never packs the next chip under this one's close button.
        row.setSizeConstraint(QLayout.SetMinimumSize)
        row.addWidget(self._label)

        # The chip takes exactly the width it needs; it never shrinks below it.
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self._close_btn = None
        if closable:
            self._close_btn = QPushButton()
            self._close_btn.setIcon(ui_icon("close"))
            self._close_btn.setIconSize(QSize(14, 14))
            self._close_btn.setObjectName("chipclose")
            self._close_btn.setFixedSize(16, 16)
            self._close_btn.setFlat(True)
            self._close_btn.setCursor(Qt.PointingHandCursor)
            self._close_btn.setToolTip("Close tab")
            self._close_btn.setFocusPolicy(Qt.NoFocus)
            # Explicit readable color so the glyph shows on any chip background,
            # with a red hover highlight. Muted color comes from the theme.
            t = tokens(current_mode())
            self._close_btn.setStyleSheet(
                "#chipclose {"
                f"  color: {t['text_faint']}; background: transparent;"
                "  border: none; border-radius: 8px; padding: 0;"
                "  font-size: 14px; font-weight: normal;"
                "}"
                "#chipclose:hover {"
                "  color: #ffffff; background: #d9534f;"
                "}"
            )
            self._close_btn.clicked.connect(lambda: self.close_clicked.emit(self._key))
            row.addWidget(self._close_btn)

        self.setObjectName("chip")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setContextMenuPolicy(Qt.DefaultContextMenu)
        self._apply_style()

    def key(self):
        return self._key

    def set_text(self, text: str) -> None:
        self._label.setText(text)

    def set_selected(self, selected: bool) -> None:
        self._selected = selected
        self._apply_style()

    def set_base_style(self, style: str) -> None:
        self._base_style = style
        self._apply_style()

    def _apply_style(self) -> None:
        t = tokens(current_mode())
        border = t["accent"] if self._selected else t["border"]
        weight = "bold" if self._selected else "normal"
        bg = t["surface_alt"] if self._selected else "transparent"
        fg = t["text"] if self._selected else t["text_muted"]
        # _base_style carries the optional group-color accent (border-left).
        self.setStyleSheet(
            "QLabel { font-weight: %s; color: %s; background: transparent; }"
            "#chip { border: 1px solid %s; border-radius: 6px; background: %s; %s }"
            "#chip:hover { border: 1px solid %s; }"
            % (weight, fg, border, bg, self._base_style, t["accent"])
        )

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self._key)
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.double_clicked.emit(self._key)
        super().mouseDoubleClickEvent(event)

    def contextMenuEvent(self, event) -> None:
        self.context_menu.emit(self._key, event.globalPos())


class _GroupHeaderChip(QWidget):
    """A group header chip: arrow + name, colored with the group color."""

    toggled = Signal(str)              # emits group name
    context_menu = Signal(str, object)  # (group name, global QPoint)

    def __init__(self, name: str, color: str, collapsed: bool, parent=None) -> None:
        super().__init__(parent)
        self._name = name
        self._collapsed = collapsed

        self._arrow = QLabel()
        self._arrow.setContentsMargins(6, 3, 2, 3)
        self._title = QLabel(name)
        self._title.setContentsMargins(2, 3, 8, 3)

        from PySide6.QtWidgets import QHBoxLayout, QLayout, QSizePolicy
        row = QHBoxLayout(self)
        row.setContentsMargins(2, 1, 2, 1)
        row.setSpacing(0)
        row.setSizeConstraint(QLayout.SetMinimumSize)
        row.addWidget(self._arrow)
        row.addWidget(self._title)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setCursor(Qt.PointingHandCursor)

        self._color = color
        self.setObjectName("ghdr")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self._refresh()

    def name(self) -> str:
        return self._name

    def set_collapsed(self, collapsed: bool) -> None:
        self._collapsed = collapsed
        self._refresh()

    def set_color(self, color: str) -> None:
        self._color = color
        self._refresh()

    def _refresh(self) -> None:
        self._arrow.setPixmap(
            ui_icon("right" if self._collapsed else "down").pixmap(QSize(14, 14))
        )
        # Readable text color against the group color.
        fg = self._contrast(self._color)
        border = tokens(current_mode())["border"]
        self.setStyleSheet(
            "QLabel { color: %s; font-weight: bold; background: transparent; }"
            "#ghdr { background: %s; border: 1px solid %s; border-radius: 6px; }"
            % (fg, self._color, border)
        )

    @staticmethod
    def _contrast(hex_color: str) -> str:
        c = QColor(hex_color)
        # Perceived luminance; dark text on light backgrounds and vice versa.
        lum = 0.299 * c.red() + 0.587 * c.green() + 0.114 * c.blue()
        return "#000000" if lum > 140 else "#ffffff"

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.toggled.emit(self._name)
        super().mousePressEvent(event)

    def contextMenuEvent(self, event) -> None:
        self.context_menu.emit(self._name, event.globalPos())


class WrappingTabBar(QScrollArea):
    """Group-aware, wrapping tab bar composed of chip widgets."""

    tab_selected = Signal(object)     # key
    tab_close_requested = Signal(object)
    tab_rename_requested = Signal(object)
    tab_context_menu = Signal(object, object)     # (key, global pos)
    group_context_menu = Signal(str, object)      # (group name, global pos)
    group_toggled = Signal(str)                   # group name

    # Vertical padding baked into a single flow row (chip height + margins +
    # spacing). Used to cap the bar at two rows before it starts scrolling.
    _ROW_HEIGHT = 29

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QScrollArea.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # Start at exactly one row; grow to a second row as chips wrap; only
        # once a third row is needed does the bar become scrollable.
        self._max_rows = 2
        self.setMinimumHeight(self._ROW_HEIGHT)
        self.setMaximumHeight(self._ROW_HEIGHT * self._max_rows + 2)

        self._host = _FlowHost()
        self._flow = FlowLayout(self._host, margin=2, h_spacing=4, v_spacing=4)
        self.setWidget(self._host)

        # key -> _Chip ; group name -> _GroupHeaderChip
        self._chips: dict[object, _Chip] = {}
        self._headers: dict[str, _GroupHeaderChip] = {}
        self._current_key = None

    # -- population -----------------------------------------------------------

    def rebuild(self, *, order, chip_titles, chip_styles,
                groups, group_members, collapsed) -> None:
        """Rebuild the whole bar from the container's model.

        Args:
            order: list of keys giving ungrouped tab order.
            chip_titles: dict key -> display text.
            chip_styles: dict key -> extra CSS for the chip (e.g. color tint).
            groups: list of (name, color) in display order.
            group_members: dict group name -> list of member keys in order.
            collapsed: set of collapsed group names.
        """
        # Strategy: REUSE existing chip/header widgets instead of destroying
        # and recreating them on every change. Wholesale destroy+recreate inside
        # a QScrollArea leaves ghost pixels (stale chips / orphan close buttons)
        # because deleted widgets keep painting until the event loop runs.
        #
        # 1) Detach every item from the layout (does NOT delete the widgets).
        # 2) Delete only the widgets whose keys/groups no longer exist.
        # 3) Create only the widgets that are newly needed.
        # 4) Re-add everything to the layout in the new display order.

        while self._flow.count():
            self._flow.takeAt(0)

        wanted_keys = set(order)
        for members in group_members.values():
            wanted_keys.update(members)
        wanted_groups = {name for name, _ in groups}

        # Drop chips/headers that are gone.
        for key in [k for k in self._chips if k not in wanted_keys]:
            self._destroy(self._chips.pop(key))
        for name in [g for g in self._headers if g not in wanted_groups]:
            self._destroy(self._headers.pop(name))

        # Groups first: header followed by its members.
        for name, color in groups:
            header = self._headers.get(name)
            if header is None:
                header = _GroupHeaderChip(name, color, name in collapsed, self._host)
                header.toggled.connect(self.group_toggled.emit)
                header.context_menu.connect(self.group_context_menu.emit)
                self._headers[name] = header
            else:
                header.set_color(color)
                header.set_collapsed(name in collapsed)
            header.show()
            self._flow.addWidget(header)

            for key in group_members.get(name, []):
                chip = self._ensure_chip(key, chip_titles.get(key, ""),
                                         chip_styles.get(key, ""))
                chip.setVisible(name not in collapsed)
                self._flow.addWidget(chip)

        # Ungrouped tabs after the groups.
        for key in order:
            chip = self._ensure_chip(key, chip_titles.get(key, ""),
                                     chip_styles.get(key, ""))
            chip.setVisible(True)
            self._flow.addWidget(chip)

        self._apply_selection()
        # Recompute layout + height now so positions are correct immediately.
        self._flow.invalidate()
        self._flow.activate()
        self._host.updateGeometry()
        self._sync_height()

    def _sync_height(self) -> None:
        """Grow the bar to fit its rows, capped at ``_max_rows`` (then scroll)."""
        width = self._host.width() or self.viewport().width()
        content = self._flow.heightForWidth(width) if width > 0 else self._ROW_HEIGHT
        # The host always spans its full content height (so the scroll area can
        # scroll when there are 3+ rows).
        self._host.setMinimumHeight(content)
        # The scroll area itself only grows up to the max-rows cap.
        cap = self._ROW_HEIGHT * self._max_rows + 2
        self.setFixedHeight(min(max(content, self._ROW_HEIGHT), cap))

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        super().resizeEvent(event)
        # Re-evaluate wrapping when the width changes (chips may wrap/unwrap).
        self._sync_height()

    @staticmethod
    def _destroy(widget) -> None:
        widget.hide()
        widget.setParent(None)
        widget.deleteLater()

    def _ensure_chip(self, key, title: str, style: str) -> _Chip:
        chip = self._chips.get(key)
        if chip is None:
            chip = _Chip(key, title, closable=True, parent=self._host)
            chip.clicked.connect(self._on_chip_clicked)
            chip.close_clicked.connect(self.tab_close_requested.emit)
            chip.double_clicked.connect(self.tab_rename_requested.emit)
            chip.context_menu.connect(self.tab_context_menu.emit)
            self._chips[key] = chip
        else:
            chip.set_text(title)
        chip.set_base_style(style)
        return chip

    # -- selection ------------------------------------------------------------

    def set_current(self, key) -> None:
        self._current_key = key
        self._apply_selection()

    def _on_chip_clicked(self, key) -> None:
        self.set_current(key)
        self.tab_selected.emit(key)

    def _apply_selection(self) -> None:
        for key, chip in self._chips.items():
            chip.set_selected(key is self._current_key or key == self._current_key)
