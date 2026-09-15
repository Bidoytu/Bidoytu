"""Target workspace: sitemap review and target-scope configuration."""
from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse
from datetime import datetime

from PySide6.QtCore import QAbstractTableModel, QSignalBlocker, QTimer, Qt, Signal
from PySide6.QtGui import QColor, QGuiApplication, QIcon, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView, QCheckBox, QComboBox, QFileDialog, QInputDialog, QMenu, QMessageBox,
    QHBoxLayout, QLabel, QLineEdit, QPushButton, QSizePolicy, QTableWidget, QTableWidgetItem,
    QHeaderView, QSplitter, QStyle, QTabWidget, QTableView, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget, QGroupBox,
)
from bidoytu.storage.advanced_history import FilterSpec, matches
from bidoytu.ui.history_filter_dialog import HistoryFilterDialog
from bidoytu.ui.detail_view import DetailView


def _protocol_icon(secure: bool) -> QIcon:
    """Small lock/unlock glyph used by the sitemap host tree."""
    pixmap = QPixmap(16, 16); pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap); painter.setRenderHint(QPainter.Antialiasing)
    color = QColor("#3d4856") if secure else QColor("#d9534f")
    pen = QPen(color); pen.setWidth(2); painter.setPen(pen); painter.setBrush(Qt.NoBrush)
    painter.drawRoundedRect(4, 7, 8, 6, 1.5, 1.5)
    if secure:
        painter.drawArc(5, 2, 6, 9, 0, 180 * 16)
    else:
        painter.drawArc(3, 2, 6, 9, 25 * 16, 140 * 16)
    painter.end()
    return QIcon(pixmap)


class _SitemapTableModel(QAbstractTableModel):
    COLUMNS = ["Host", "Method", "URL", "Params", "Status code", "Length", "MIME type", "Title", "Notes", "Time requested"]

    def __init__(self, parent=None):
        super().__init__(parent); self._rows = []
    def rowCount(self, parent=None): return 0 if parent and parent.isValid() else len(self._rows)
    def columnCount(self, parent=None): return 0 if parent and parent.isValid() else len(self.COLUMNS)
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole: return None
        return self.COLUMNS[section] if orientation == Qt.Horizontal else section + 1
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid(): return None
        record = self._rows[index.row()]
        if role == Qt.UserRole: return record
        if role == Qt.DisplayRole:
            timestamp = datetime.fromtimestamp(record.started_at).strftime("%H:%M:%S %d %b") if record.started_at else ""
            return [record.host, record.method, record.url, "?" if "?" in record.path else "", str(record.status_code or ""), str(record.response_body_size), record.mime_type, "", record.notes, timestamp][index.column()]
        return None
    def set_rows(self, rows):
        self.beginResetModel(); self._rows = list(rows); self.endResetModel()
    def record_at(self, row): return self._rows[row] if 0 <= row < len(self._rows) else None


class _ScopeTable(QWidget):
    changed = Signal()

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Enabled", "Prefix", "Include subdomains"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setMinimumHeight(175)
        self.table.itemChanged.connect(lambda _item: self.changed.emit())
        label = QLabel(title); label.setStyleSheet("font-weight: 600;")
        self.add_btn = QPushButton("Add"); self.edit_btn = QPushButton("Edit")
        self.remove_btn = QPushButton("Remove"); self.paste_btn = QPushButton("Paste URL")
        self.load_btn = QPushButton("Load ...")
        self.add_btn.clicked.connect(self._add); self.edit_btn.clicked.connect(self._edit)
        self.remove_btn.clicked.connect(self._remove); self.paste_btn.clicked.connect(self._paste)
        self.load_btn.clicked.connect(self._load)
        buttons = QVBoxLayout()
        for button in (self.add_btn, self.edit_btn, self.remove_btn, self.paste_btn, self.load_btn): buttons.addWidget(button)
        buttons.addStretch(1)
        row = QHBoxLayout(); row.addLayout(buttons); row.addWidget(self.table, 1)
        layout = QVBoxLayout(self); layout.addWidget(label); layout.addLayout(row)

    def values(self):
        return [self.table.item(row, 1).text() for row in range(self.table.rowCount()) if self.table.item(row, 1) is not None]
    def set_values(self, values):
        self.table.setRowCount(0)
        for value in values: self._insert(str(value), False)
    def _insert(self, value, emit=True):
        value = value.strip()
        if not value or value in self.values(): return
        row = self.table.rowCount(); self.table.insertRow(row)
        enabled = QTableWidgetItem(); enabled.setCheckState(Qt.Checked)
        prefix = QTableWidgetItem(value)
        subdomains = QTableWidgetItem(); subdomains.setCheckState(Qt.Checked)
        self.table.setItem(row, 0, enabled); self.table.setItem(row, 1, prefix); self.table.setItem(row, 2, subdomains)
        if emit: self.changed.emit()
    def _selected_row(self):
        rows = self.table.selectionModel().selectedRows(); return rows[0].row() if rows else -1
    def _add(self):
        value, ok = QInputDialog.getText(self, "Add scope entry", "Prefix:")
        if ok: self._insert(value)
    def _edit(self):
        row = self._selected_row()
        if row < 0: return
        value, ok = QInputDialog.getText(self, "Edit scope entry", "Prefix:", text=self.values()[row])
        if ok and value.strip(): self.table.item(row, 1).setText(value.strip()); self.changed.emit()
    def _remove(self):
        row = self._selected_row()
        if row >= 0: self.table.removeRow(row); self.changed.emit()
    def _paste(self):
        clipboard = QGuiApplication.clipboard()
        text = clipboard.text() if clipboard else ""
        for raw in text.replace("\r", "\n").split("\n"):
            value = raw.strip(); parsed = urlparse(value); self._insert(parsed.netloc or value.split("/", 1)[0])
    def _load(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load scope entries", "", "Text files (*.txt);;All files (*)")
        if path:
            for line in Path(path).read_text(encoding="utf-8").splitlines(): self._insert(line)


class _ScopePage(QWidget):
    changed = Signal()
    def __init__(self, hosts=None, excluded=None, paths=None, excluded_paths=None, regex=None, excluded_regex=None, parent=None):
        super().__init__(parent)
        title = QLabel("Target scope"); title.setStyleSheet("font-size: 18px; font-weight: 700;")
        description = QLabel("Use these settings to define exactly what hosts and URLs constitute the target for your current work. This configuration affects the behavior of tools throughout the suite."); description.setWordWrap(True)
        self.advanced = QCheckBox("Use advanced scope control"); self.advanced.toggled.connect(self._toggle_advanced)
        self.include = _ScopeTable("Include in scope"); self.exclude = _ScopeTable("Exclude from scope")
        self.include.changed.connect(self.changed.emit); self.exclude.changed.connect(self.changed.emit)
        self._include_paths = list(paths or []); self._exclude_paths = list(excluded_paths or [])
        self._include_regex = list(regex or []); self._exclude_regex = list(excluded_regex or [])
        self._advanced_group = QGroupBox("Advanced scope"); advanced_layout = QVBoxLayout(self._advanced_group)
        self._preset = QComboBox(); self._preset.addItems(["Preset: none", "Web app", "API surface", "Static assets"]); self._preset.currentTextChanged.connect(self._apply_preset)
        self._advanced_summary = QLabel(self._summary()); self._advanced_summary.setWordWrap(True)
        advanced_layout.addWidget(self._preset); advanced_layout.addWidget(self._advanced_summary); self._advanced_group.hide()
        layout = QVBoxLayout(self); layout.addWidget(title); layout.addWidget(description); layout.addWidget(self.advanced); layout.addWidget(self.include); layout.addWidget(self.exclude); layout.addWidget(self._advanced_group); layout.addStretch(1)
        self.include.set_values(hosts or []); self.exclude.set_values(excluded or [])
    def _toggle_advanced(self, enabled): self._advanced_group.setVisible(enabled); self.changed.emit()
    def _apply_preset(self, name):
        presets = {"Web app": (["/api/"], ["/static/", "/assets/"], []), "API surface": (["/api/", "/graphql"], [], [r"/v[0-9]+/"]), "Static assets": (["/static/", "/assets/"], [], [r"\.(?:css|js|png|jpg|svg)$"])}
        if name in presets:
            self._include_paths, self._exclude_paths, self._include_regex = presets[name]; self._exclude_regex = []; self._advanced_summary.setText(self._summary()); self.changed.emit()
    def _summary(self): return f"Include paths: {len(self._include_paths)}  |  Exclude paths: {len(self._exclude_paths)}  |  Include regex: {len(self._include_regex)}  |  Exclude regex: {len(self._exclude_regex)}"
    def include_scope(self): return self.include.values()
    def exclude_scope(self): return self.exclude.values()
    def include_paths(self): return self._include_paths if self.advanced.isChecked() else []
    def exclude_paths(self): return self._exclude_paths if self.advanced.isChecked() else []
    def include_regex(self): return self._include_regex if self.advanced.isChecked() else []
    def exclude_regex(self): return self._exclude_regex if self.advanced.isChecked() else []


class _SitemapPage(QWidget):
    changed = Signal()
    def __init__(self, urls=None, parent=None):
        super().__init__(parent); self._urls = list(urls or []); self._records_by_flow = {}; self.body_provider = None; self._refresh_pending = False; self._active = False
        self.add_edit = QLineEdit(); self.add_edit.setPlaceholderText("https://example.com/sitemap.xml")
        add = QPushButton("Add"); add.clicked.connect(self._add); clear = QPushButton("Clear all"); clear.clicked.connect(self._clear_all); add_row = QHBoxLayout(); add_row.addWidget(self.add_edit, 1); add_row.addWidget(add); add_row.addWidget(clear)
        self.filter_edit = QLineEdit(); self.filter_edit.setPlaceholderText("Site map filter"); self.filter_edit.textChanged.connect(self._refresh)
        self.filter_btn = QPushButton("Advanced filters..."); self.filter_btn.clicked.connect(self._show_filters)
        filter_row = QHBoxLayout(); filter_row.addWidget(self.filter_edit, 1); filter_row.addWidget(self.filter_btn)
        self.domains = QTreeWidget(); self.domains.setHeaderLabel("Domains and paths"); self.domains.setMinimumWidth(260); self.domains.setUniformRowHeights(True); self.domains.setAnimated(False); self.domains.setMouseTracking(True); self.domains.viewport().setCursor(Qt.PointingHandCursor); self.domains.setContextMenuPolicy(Qt.CustomContextMenu); self.domains.customContextMenuRequested.connect(self._show_tree_menu); self.domains.setStyleSheet("QTreeWidget::item:hover { background: palette(highlight); color: palette(highlighted-text); }"); self.domains.itemSelectionChanged.connect(self._domain_changed)
        self.table = QTableView(); self.table_model = _SitemapTableModel(self.table); self.table.setModel(self.table_model); self.table.setAlternatingRowColors(True); self.table.setSelectionBehavior(QAbstractItemView.SelectRows); self.table.setSelectionMode(QAbstractItemView.SingleSelection); self.table.setSortingEnabled(True); self.table.setWordWrap(False); self.table.verticalHeader().setDefaultSectionSize(24); self.table.setMouseTracking(True); self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding); self.table.setStyleSheet("QTableView::item:hover { background: palette(highlight); color: palette(highlighted-text); }"); self.table.selectionModel().selectionChanged.connect(lambda *_: self._show_selected_record())
        header = self.table.horizontalHeader()
        for column in (0, 1, 3, 4, 5, 6, 9): header.setSectionResizeMode(column, QHeaderView.ResizeToContents)
        for column in (2, 7, 8): header.setSectionResizeMode(column, QHeaderView.Stretch)
        top_split = QSplitter(); top_split.addWidget(self.domains); top_split.addWidget(self.table); top_split.setStretchFactor(1, 1)
        self.detail = DetailView(self); self.detail.setMinimumHeight(220)
        split = QSplitter(Qt.Vertical); split.addWidget(top_split); split.addWidget(self.detail); split.setSizes([520, 300])
        self._spec = FilterSpec(); self._selected_host = ""; self._selected_path = ""; self._row_records = []; self._host_items = {}; self._path_items = {}
        layout = QVBoxLayout(self); layout.addLayout(add_row); layout.addLayout(filter_row); layout.addWidget(split); self._refresh()
    def values(self): return list(self._urls)
    def add_record(self, record, defer=False):
        self._records_by_flow[record.flow_id] = record
        if defer: self._schedule_refresh()
        else: self._refresh()
    def set_records(self, records):
        self._records_by_flow = {record.flow_id: record for record in records}
        self._reset_tree()
        self._refresh()
    def _schedule_refresh(self):
        if not self._active: return
        if self._refresh_pending: return
        self._refresh_pending = True
        QTimer.singleShot(250, self._flush_refresh)
    def _flush_refresh(self):
        self._refresh_pending = False
        self._refresh()
    def _add(self):
        value = self.add_edit.text().strip()
        if value and value not in self._urls: self._urls.append(value); self.add_edit.clear(); self._refresh(); self.changed.emit()
    def _clear_all(self):
        if not self._records_by_flow and not self._urls: return
        answer = QMessageBox.question(self, "Clear sitemap", "Remove all sitemap hosts, paths, and entries?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if answer != QMessageBox.Yes: return
        self._records_by_flow.clear(); self._urls.clear(); self._selected_host = ""; self._selected_path = ""; self._reset_tree(); self._refresh(); self.detail.clear(); self.changed.emit()
    def _show_tree_menu(self, position):
        item = self.domains.itemAt(position)
        if item is None: return
        self.domains.setCurrentItem(item)
        data = item.data(0, Qt.UserRole)
        host = data[0] if isinstance(data, tuple) else str(data or "")
        if not host: return
        menu = QMenu(self)
        delete_action = menu.addAction("Delete host")
        chosen = menu.exec(self.domains.viewport().mapToGlobal(position))
        if chosen is delete_action: self._delete_host(host)
    def _delete_host(self, host):
        answer = QMessageBox.question(self, "Delete host", f"Remove {host} from the sitemap?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if answer != QMessageBox.Yes: return
        self._records_by_flow = {flow_id: record for flow_id, record in self._records_by_flow.items() if record.host != host}
        self._urls = [url for url in self._urls if urlparse(url).netloc != host]
        if self._selected_host == host: self._selected_host = ""; self._selected_path = ""
        self._reset_tree(); self._refresh(); self.detail.clear(); self.changed.emit()
    def _refresh(self):
        needle = self.filter_edit.text().casefold(); host = self._selected_host; path = self._selected_path
        records = list(self._records_by_flow.values())
        self._sync_tree(records)
        visible = [record for record in records if (not host or record.host == host) and (not path or record.path.split("?", 1)[0].startswith(path)) and matches(record, self._spec) and (not needle or needle in record.url.casefold())]
        self._row_records = visible
        self.table_model.set_rows(visible)

    def _reset_tree(self):
        blocker = QSignalBlocker(self.domains); self.domains.clear(); del blocker
        self._host_items.clear(); self._path_items.clear()

    def _sync_tree(self, records):
        """Add only newly discovered hosts/paths to the tree."""
        records_by_host = {}
        for record in records: records_by_host.setdefault(record.host, []).append(record)
        for url in self._urls:
            parsed = urlparse(url)
            if parsed.netloc and parsed.netloc not in self._host_items:
                self._ensure_host(parsed.netloc, parsed.scheme == "https")
        for host, host_records in records_by_host.items():
            secure = any(record.scheme == "https" for record in host_records)
            root = self._ensure_host(host, secure)
            if secure: root.setIcon(0, _protocol_icon(True)); root.setToolTip(0, f"{host} (HTTPS)")
            for record in host_records: self._ensure_path(record)

    def _ensure_host(self, host, secure=False):
        item = self._host_items.get(host)
        if item is not None: return item
        item = QTreeWidgetItem([host]); item.setData(0, Qt.UserRole, (host, "")); item.setIcon(0, _protocol_icon(secure)); item.setToolTip(0, f"{host} ({'HTTPS' if secure else 'HTTP'})")
        self.domains.addTopLevelItem(item); self._host_items[host] = item
        return item

    def _ensure_path(self, record):
        clean = record.path.split("?", 1)[0] or "/"; segments = [part for part in clean.split("/") if part]
        parent = self._host_items[record.host]; prefix = ""
        if not segments:
            key = (record.host, "/", True)
            if key not in self._path_items:
                leaf = QTreeWidgetItem(["/"]); leaf.setData(0, Qt.UserRole, (record.host, "/")); leaf.setIcon(0, self.style().standardIcon(QStyle.SP_FileIcon)); parent.addChild(leaf); self._path_items[key] = leaf
            return
        for index, segment in enumerate(segments):
            prefix += "/" + segment; final = index == len(segments) - 1; key = (record.host, prefix, final)
            item = self._path_items.get(key)
            if item is None:
                item = QTreeWidgetItem([segment]); item.setData(0, Qt.UserRole, (record.host, prefix)); item.setIcon(0, self.style().standardIcon(QStyle.SP_FileIcon if final and "." in segment else QStyle.SP_DirIcon)); parent.addChild(item); self._path_items[key] = item
            parent = item

    def _domain_changed(self):
        items = self.domains.selectedItems()
        self._selected_host, self._selected_path = items[0].data(0, Qt.UserRole) if items else ("", "")
        self._refresh()
    def _show_selected_record(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows: return
        record = self.table_model.record_at(rows[0].row())
        if record is None: return
        request_body = self.body_provider(record, False) if self.body_provider else record.request_body_inline
        response_body = self.body_provider(record, True) if self.body_provider else record.response_body_inline
        self.detail.show_request(record, request_body); self.detail.show_response(record, response_body)
    def _show_filters(self):
        dialog = HistoryFilterDialog(self._spec, self); dialog.filter_applied.connect(self._apply_filters); dialog.exec()
    def _apply_filters(self, spec):
        self._spec = spec; self._refresh(); self.filter_btn.setText("Advanced filters... (active)" if (spec.search or spec.query or spec.host or spec.path or spec.method or spec.status or spec.mime or spec.size or spec.time or spec.tool or spec.mime_types or spec.status_classes or spec.show_extensions or spec.hide_extensions) else "Advanced filters...")

    def set_active(self, active):
        self._active = bool(active)
        if self._active:
            self._refresh()


class TargetTab(QWidget):
    scope_changed = Signal(list, list, list, list, list, list, list)
    def __init__(self, include_scope=None, exclude_scope=None, include_paths=None, exclude_paths=None, include_regex=None, exclude_regex=None, sitemaps=None, parent=None):
        super().__init__(parent)
        self.scope_page = _ScopePage(include_scope, exclude_scope, include_paths, exclude_paths, include_regex, exclude_regex); self.sitemap_page = _SitemapPage(sitemaps)
        self.scope_page.changed.connect(self._emit); self.sitemap_page.changed.connect(self._emit)
        self.tabs = QTabWidget(); self.tabs.addTab(self.sitemap_page, "Site map"); self.tabs.addTab(self.scope_page, "Scope"); self.tabs.setCurrentWidget(self.scope_page)
        layout = QVBoxLayout(self); layout.addWidget(self.tabs)
    def _emit(self): self.scope_changed.emit(self.include_scope(), self.exclude_scope(), self.include_paths(), self.exclude_paths(), self.include_regex(), self.exclude_regex(), self.sitemaps())
    def include_scope(self): return self.scope_page.include_scope()
    def exclude_scope(self): return self.scope_page.exclude_scope()
    def include_paths(self): return self.scope_page.include_paths()
    def exclude_paths(self): return self.scope_page.exclude_paths()
    def include_regex(self): return self.scope_page.include_regex()
    def exclude_regex(self): return self.scope_page.exclude_regex()
    def sitemaps(self): return self.sitemap_page.values()
    def add_record(self, record, defer=False): self.sitemap_page.add_record(record, defer=defer)
    def set_records(self, records): self.sitemap_page.set_records(records)
    def set_body_provider(self, provider): self.sitemap_page.body_provider = provider
    def set_active(self, active): self.sitemap_page.set_active(active)
