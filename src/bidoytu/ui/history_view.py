"""HTTP history: the traffic table plus a request/response detail view.

Emits a signal when a row is selected (so the owner can populate detail) and
exposes a context menu with "Send to Repeater/Intruder" actions.
"""
from __future__ import annotations

from dataclasses import replace

from PySide6.QtCore import QEvent, QModelIndex, QTimer, Qt, Signal, Slot
from PySide6.QtGui import QAction, QKeySequence, QColor, QPainter
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QMenu,
    QComboBox,
    QFileDialog,
    QColorDialog,
    QInputDialog,
    QListView,
    QPushButton,
    QHBoxLayout,
    QSplitter,
    QStyle,
    QStyleOptionViewItem,
    QTableView,
    QVBoxLayout,
    QStyledItemDelegate,
    QWidget,
)

from bidoytu.storage.models import FlowRecord
from bidoytu.ui.detail_view import DetailView
from bidoytu.ui.flow_table_model import FlowTableModel
from bidoytu.ui.history_delegate import HistoryItemDelegate
from bidoytu.storage.advanced_history import (
    FilterSpec, deserialize_filter_spec, export_records, serialize_filter_spec,
)
from bidoytu.ui.history_filter_dialog import HistoryFilterDialog


class _SavedFilterDelegate(QStyledItemDelegate):
    """Paint saved-filter names with a compact delete affordance."""

    def paint(self, painter: QPainter, option, index) -> None:
        active = bool(option.state & (QStyle.State_Selected | QStyle.State_MouseOver))
        if active:
            painter.save()
            painter.fillRect(option.rect, option.palette.highlight())
            painter.restore()
        item_option = QStyleOptionViewItem(option)
        if index.row() > 0:
            item_option.rect = option.rect.adjusted(6, 0, -28, 0)
        super().paint(painter, item_option, index)
        if index.row() > 0:
            painter.save()
            color = (option.palette.highlightedText().color()
                     if active else option.palette.mid().color())
            painter.setPen(color)
            painter.drawText(
                option.rect.adjusted(option.rect.width() - 28, 0, -6, 0),
                int(Qt.AlignCenter), "×",
            )
            painter.restore()


class _SavedFilterCombo(QComboBox):
    delete_requested = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        view = QListView()
        view.setItemDelegate(_SavedFilterDelegate(view))
        view.setMouseTracking(True)
        view.viewport().installEventFilter(self)
        self.setView(view)

    def eventFilter(self, watched, event) -> bool:  # noqa: N802 (Qt override)
        if watched is self.view().viewport() and event.type() == QEvent.MouseButtonPress:
            position = event.position().toPoint()
            index = self.view().indexAt(position)
            rect = self.view().visualRect(index)
            if index.isValid() and index.row() > 0 and position.x() >= rect.right() - 30:
                self.hidePopup()
                name = str(index.data(Qt.DisplayRole))
                # Let the combo finish closing its popup before opening the
                # modal confirmation. Otherwise the popup can consume the
                # first click and the dialog appears only after another click.
                QTimer.singleShot(0, lambda: self.delete_requested.emit(name))
                return True
        return super().eventFilter(watched, event)


class HistoryView(QWidget):
    """Traffic table + detail, with send-to context actions."""

    send_to_repeater = Signal(object)  # FlowRecord
    send_to_intruder = Signal(object)  # FlowRecord
    send_to_scanner = Signal(object)
    send_to_compare = Signal(object)
    send_to_findings = Signal(object)
    metadata_changed = Signal(object)
    save_filter_requested = Signal(str, str)
    delete_filter_requested = Signal(str)
    load_filters_requested = Signal()
    body_provider = None  # set by owner: callable(record, response: bool) -> bytes|None

    def __init__(self, model: FlowTableModel, parent=None) -> None:
        super().__init__(parent)
        self._model = model
        self._spec = FilterSpec()
        # Re-entrancy guard: our own resizeSection() calls emit sectionResized
        # again, which would recurse into the handler. Set while we adjust Path.
        self._resizing_guard = False

        controls = QHBoxLayout()
        self._filter_btn = QPushButton("Filter settings…")
        self._filter_btn.setToolTip("Open HTTP history filter settings")
        self._filter_btn.setFixedWidth(125)
        self._filter_btn.clicked.connect(self._open_filter_settings)
        controls.addWidget(self._filter_btn)
        self._filter_summary = QPushButton("All traffic")
        self._filter_summary.setEnabled(False)
        self._filter_summary.setMinimumWidth(110)
        controls.addWidget(self._filter_summary, 1)
        self._method_combo = QComboBox()
        self._method_combo.setToolTip("Filter by HTTP method")
        self._method_combo.addItems(["All methods", "GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"])
        self._method_combo.setFixedWidth(165)
        self._method_combo.currentTextChanged.connect(self._quick_method_filter)
        self._status_combo = QComboBox()
        self._status_combo.setToolTip("Filter by response status")
        self._status_combo.addItems(["All statuses", "2xx", "3xx", "4xx", "5xx"])
        self._status_combo.setFixedWidth(145)
        self._status_combo.currentTextChanged.connect(self._quick_status_filter)
        self._save_btn = QPushButton("Save filter")
        self._save_btn.setFixedWidth(105)
        self._save_btn.clicked.connect(self._save_filter)
        self._export_btn = QPushButton("Export")
        self._export_btn.setFixedWidth(80)
        self._export_btn.clicked.connect(self._export)
        controls.addWidget(self._method_combo)
        controls.addWidget(self._status_combo)
        controls.addWidget(self._save_btn)
        controls.addWidget(self._export_btn)

        self._table = QTableView()
        self._table.setModel(model)
        self._table.setSortingEnabled(True)
        self._table.horizontalHeader().setSortIndicatorShown(True)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SingleSelection)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # The delegate fully self-paints every cell (soft wash + accent bar +
        # text) and never calls the base style, so no style-drawn selection
        # background or coloured focus/selection frame can appear.
        self._table.setItemDelegate(HistoryItemDelegate(self._table))
        # No gridlines: cleaner look, and removes any per-column boundary ticks.
        self._table.setShowGrid(False)
        # No focus rectangle regardless of platform style.
        self._table.setFocusPolicy(Qt.NoFocus)
        self._table.verticalHeader().setVisible(False)
        self._table.setContextMenuPolicy(Qt.CustomContextMenu)
        self._table.customContextMenuRequested.connect(self._on_context_menu)
        self._configure_columns()

        self._detail = DetailView(editable_request=False)
        # Right-clicking inside the request pane offers the same send-to actions
        # as the table row menu.
        self._detail.send_to_repeater.connect(self.send_to_repeater)
        self._detail.send_to_intruder.connect(self.send_to_intruder)

        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self._table)
        splitter.addWidget(self._detail)
        splitter.setSizes([350, 450])

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(controls)
        layout.addWidget(splitter)

        self._table.selectionModel().selectionChanged.connect(self._on_selection)

        # Shortcuts active when the history table has focus.
        self._add_shortcut("Ctrl+R", self._emit_repeater)
        self._add_shortcut("Ctrl+I", self._emit_intruder)

    def _configure_columns(self) -> None:
        """Size columns so Path fills the leftover width initially, while every
        column divider stays freely draggable.

        Column order (from FlowTableModel.COLUMNS):
        0 #, 1 Method, 2 Host, 3 Path, 4 Ext, 5 Status, 6 Type, 7 Length,
        8 Cookies, 9 Time (ms).

        Every column uses Interactive resize mode. We deliberately avoid
        QHeaderView.Stretch on a middle column: a stretch section has no
        draggable right edge (so Path's right side can't be dragged), and it
        greedily reabsorbs space, which makes dragging any divider *after* it
        feel inverted. With all sections Interactive, Path is simply given the
        remaining viewport width once at layout time via :meth:`_fit_path_column`.
        """
        header = self._table.horizontalHeader()
        header.setMinimumSectionSize(36)

        # Compact defaults for everything except Path (index 3), which is sized
        # to fill the leftover space in _fit_path_column().
        self._default_widths = {
            0: 44,    # #
            1: 66,    # Method
            2: 220,   # Host
            3: 320,   # Path (initial; recomputed to fill leftover width)
            4: 54,    # Ext
            5: 58,    # Status
            6: 130,   # Type (MIME)
            7: 72,    # Length
            8: 160,   # Cookies
            9: 76,    # Time (ms)
        }

        for col in range(self._model.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.Interactive)
            header.resizeSection(col, self._default_widths.get(col, 80))

        # Path (index 3) is the single flexible column: it absorbs or releases
        # the delta whenever any other column is dragged, keeping the total row
        # width invariant. We deliberately do NOT use setStretchLastSection here
        # - a stretch-pinned last column would compete with Path for the same
        # slack and make dragging feel inverted.
        header.sectionResized.connect(self._on_section_resized)

        # No horizontal scrollbar: Path reflows so the row always fits the
        # viewport, so the table never scrolls a column out of bounds.
        self._table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Rows as tall as the text, no extra padding.
        vheader = self._table.verticalHeader()
        row_h = self._table.fontMetrics().height() + 2
        vheader.setSectionResizeMode(QHeaderView.Fixed)
        vheader.setDefaultSectionSize(row_h)
        vheader.setMinimumSectionSize(row_h)

    _PATH_COL = 3
    _PATH_MIN_WIDTH = 120  # Path's floor when it's the one absorbing/being dragged.

    def _on_section_resized(self, logical_index: int, old_size: int, new_size: int) -> None:
        """Whenever a column is resized, compensate its immediate right neighbor
        (or left neighbor, if this is the last column) by the opposite delta, so
        the total row width stays invariant and the visual change stays local to
        the two columns touching the dragged divider - not some distant column.

        Path gets no special treatment as a "sink" anymore; it's just floored
        like any neighbor would be, whether it's the column being dragged or the
        column absorbing the delta.
        """
        if self._resizing_guard:
            return

        header = self._table.horizontalHeader()
        last_col = self._model.columnCount() - 1

        # Direct drag on Path's own edge: floor it before doing anything else.
        if logical_index == self._PATH_COL and new_size < self._PATH_MIN_WIDTH:
            self._resizing_guard = True
            try:
                header.resizeSection(self._PATH_COL, old_size)
            finally:
                self._resizing_guard = False
            return

        delta = new_size - old_size
        if delta == 0:
            return

        # The divider being dragged sits between logical_index and its right
        # neighbor (standard Qt convention) - except for the last column, which
        # has no right neighbor, so it borrows from the left instead.
        neighbor = logical_index + 1 if logical_index < last_col else logical_index - 1
        neighbor_min = (
            self._PATH_MIN_WIDTH if neighbor == self._PATH_COL
            else header.minimumSectionSize()
        )
        new_neighbor_w = header.sectionSize(neighbor) - delta

        self._resizing_guard = True
        try:
            if new_neighbor_w < neighbor_min:
                # Neighbor has no slack left - reject the drag, snap back.
                header.resizeSection(logical_index, old_size)
            else:
                header.resizeSection(neighbor, new_neighbor_w)
        finally:
            self._resizing_guard = False

    def _fit_path_column(self) -> None:
        """Reflow the Path column to absorb the viewport's leftover width.

        Path is the flexible column: it fills whatever space the other columns
        don't use, so the total always matches the viewport. That keeps the
        stretch-pinned last column flush against the right edge and prevents any
        column from spilling out of bounds when the window shrinks. Path keeps a
        draggable right edge (it's Interactive, not Stretch), so the user can
        still resize it; it just re-fills on the next view resize.
        """
        header = self._table.horizontalHeader()
        viewport_w = self._table.viewport().width()
        if viewport_w <= 0:
            return
        min_w = max(header.minimumSectionSize(), self._PATH_MIN_WIDTH)
        others = sum(
            header.sectionSize(c)
            for c in range(self._model.columnCount())
            if c != self._PATH_COL
        )
        self._resizing_guard = True
        try:
            header.resizeSection(self._PATH_COL, max(min_w, viewport_w - others))
        finally:
            self._resizing_guard = False

    def showEvent(self, event) -> None:  # noqa: N802 (Qt override)
        super().showEvent(event)
        self._fit_path_column()

    def resizeEvent(self, event) -> None:  # noqa: N802 (Qt override)
        super().resizeEvent(event)
        # Path reflows to keep the row width == viewport, so the last column
        # stays pinned to the right and nothing overflows.
        self._fit_path_column()

    def _add_shortcut(self, seq: str, handler) -> None:
        action = QAction(self)
        action.setShortcut(QKeySequence(seq))
        action.triggered.connect(handler)
        self.addAction(action)

    def _selected_record(self) -> FlowRecord | None:
        indexes = self._table.selectionModel().selectedRows()
        if not indexes:
            return None
        return self._model.record_at(indexes[0].row())

    @Slot()
    def _on_selection(self) -> None:
        record = self._selected_record()
        if record is None:
            return
        req_body = self._get_body(record, response=False)
        self._detail.show_request(record, req_body)
        resp_body = self._get_body(record, response=True)
        self._detail.show_response(record, resp_body)

    def _get_body(self, record: FlowRecord, response: bool):
        if callable(self.body_provider):
            return self.body_provider(record, response)
        return (record.response_body_inline if response
                else record.request_body_inline)

    def _on_context_menu(self, pos) -> None:
        record = self._selected_record()
        if record is None:
            index: QModelIndex = self._table.indexAt(pos)
            if index.isValid():
                record = self._model.record_at(index.row())
        if record is None:
            return
        menu = QMenu(self)
        act_bookmark = menu.addAction("★ Toggle bookmark")
        act_interesting = menu.addAction("Flag as interesting")
        act_tag = menu.addAction("Add tag…")
        act_note = menu.addAction("Edit note…")
        act_color = menu.addAction("Set color…")
        menu.addSeparator()
        act_rep = menu.addAction("Send to Repeater\tCtrl+R")
        act_int = menu.addAction("Send to Intruder\tCtrl+I")
        act_scan = menu.addAction("Send to Scanner")
        act_compare = menu.addAction("Send to Compare")
        act_findings = menu.addAction("Send to Findings")
        menu.addSeparator()
        export_menu = menu.addMenu("Export selected as")
        export_actions = {export_menu.addAction(label): fmt for label, fmt in
                          (("Raw HTTP", "raw"), ("cURL", "curl"), ("HAR", "har"),
                           ("JSON", "json"), ("CSV", "csv"))}
        chosen = menu.exec(self._table.viewport().mapToGlobal(pos))
        if chosen == act_bookmark:
            record.bookmarked = not record.bookmarked; self.metadata_changed.emit(record)
        elif chosen == act_interesting:
            record.interesting = not record.interesting; self.metadata_changed.emit(record)
        elif chosen == act_tag:
            tag, ok = QInputDialog.getText(self, "Add tag", "Tag:")
            if ok and tag.strip():
                tags = [t.strip() for t in record.tags.split(",") if t.strip()]
                if tag.strip() not in tags: tags.append(tag.strip())
                record.tags = ", ".join(tags); self.metadata_changed.emit(record)
        elif chosen == act_note:
            note, ok = QInputDialog.getMultiLineText(self, "Edit note", "Note:", record.notes)
            if ok:
                record.notes = note; self.metadata_changed.emit(record)
        elif chosen == act_color:
            color = QColorDialog.getColor(QColor(record.color or "#000000"), self, "History row color")
            if color.isValid():
                record.color = color.name(); self.metadata_changed.emit(record)
        elif chosen == act_rep:
            self.send_to_repeater.emit(record)
        elif chosen == act_int:
            self.send_to_intruder.emit(record)
        elif chosen == act_scan: self.send_to_scanner.emit(record)
        elif chosen == act_compare: self.send_to_compare.emit(record)
        elif chosen == act_findings: self.send_to_findings.emit(record)
        elif chosen in export_actions:
            self._export(fmt=export_actions[chosen], records=[record])

    def _apply_filters(self) -> None:
        self._model.apply_filter(self._spec)

    def _open_filter_settings(self) -> None:
        dialog = HistoryFilterDialog(self._spec, self)
        dialog.filter_applied.connect(self._set_filter)
        if dialog.exec() == dialog.Accepted:
            self._set_filter(dialog.applied_spec())

    def _set_filter(self, spec: FilterSpec) -> None:
        self._spec = spec
        self._model.apply_filter(spec)
        self._method_combo.blockSignals(True)
        method_index = self._method_combo.findText(spec.method or "All methods")
        self._method_combo.setCurrentIndex(max(0, method_index))
        self._method_combo.blockSignals(False)
        self._status_combo.blockSignals(True)
        status_value = next(iter(spec.status_classes), "") if len(spec.status_classes) == 1 else ""
        status_index = self._status_combo.findText(status_value or "All statuses")
        self._status_combo.setCurrentIndex(max(0, status_index))
        self._status_combo.blockSignals(False)
        active = []
        if spec.search: active.append("search")
        if spec.query: active.append("HTTPQL")
        if spec.in_scope_only: active.append("scope")
        if spec.mime_types: active.append("MIME")
        if spec.status_classes: active.append("status")
        self._filter_summary.setText("All traffic" if not active else "Filters: " + ", ".join(active))

    def _quick_method_filter(self, value: str) -> None:
        method = "" if value == "All methods" else value
        self._set_filter(replace(self._spec, method=method))

    def _quick_status_filter(self, value: str) -> None:
        classes = set() if value == "All statuses" else {value}
        self._set_filter(replace(self._spec, status="", status_classes=classes))

    def _save_filter(self) -> None:
        name, ok = QInputDialog.getText(self, "Save filter", "Name:")
        if ok and name.strip():
            self.save_filter_requested.emit(name.strip(), serialize_filter_spec(self._spec))

    def set_saved_filters(self, filters: list[tuple[str, str]]) -> None:
        """Populate the saved-filter picker without coupling the widget to SQLite."""
        toolbar = self.layout().itemAt(0).layout()
        if hasattr(self, "_saved_filter_container"):
            toolbar.removeWidget(self._saved_filter_container)
            self._saved_filter_container.deleteLater()
        combo = _SavedFilterCombo(self)
        combo.addItem("Saved filters…", "")
        for name, query in filters:
            combo.addItem(name, query)
        combo.currentIndexChanged.connect(
            lambda index: self._load_saved_query(combo.itemData(index))
        )
        combo.delete_requested.connect(self._confirm_delete_saved_filter)
        self._saved_filters = combo
        self._saved_filter_container = combo
        toolbar.insertWidget(0, combo)

    def _confirm_delete_saved_filter(self, name: str) -> None:
        from PySide6.QtWidgets import QMessageBox
        answer = QMessageBox.question(
            self, "Delete saved filter", f"Delete '{name}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if answer == QMessageBox.Yes:
            self.delete_filter_requested.emit(name)

    def _load_saved_query(self, query: str) -> None:
        self._set_filter(deserialize_filter_spec(str(query)))

    def _export(self, fmt: str | None = None, records=None) -> None:
        if fmt is None:
            fmt, ok = QInputDialog.getItem(self, "Export history", "Format:",
                ["raw", "curl", "har", "json", "csv"], 0, False)
            if not ok: return
        path, _ = QFileDialog.getSaveFileName(self, "Export HTTP history", f"history.{fmt}")
        if not path: return
        try:
            text = export_records(records or self._model.visible_records(), fmt, self.body_provider)
            with open(path, "w", encoding="utf-8", newline="") as handle: handle.write(text)
        except (OSError, ValueError) as exc:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Export failed", str(exc))

    def _emit_repeater(self) -> None:
        record = self._selected_record()
        if record is not None:
            self.send_to_repeater.emit(record)

    def _emit_intruder(self) -> None:
        record = self._selected_record()
        if record is not None:
            self.send_to_intruder.emit(record)

    def clear_detail(self) -> None:
        self._detail.clear()
