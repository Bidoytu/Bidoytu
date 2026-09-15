"""Burp-style modal filter settings for HTTP History."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox, QDialog, QDialogButtonBox, QFormLayout, QGridLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QScrollArea, QSizePolicy, QVBoxLayout, QWidget,
)

from bidoytu.storage.advanced_history import FilterSpec


class HistoryFilterDialog(QDialog):
    """Edit a :class:`FilterSpec` without changing the table until Apply."""

    filter_applied = Signal(object)

    def __init__(self, spec: FilterSpec, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("HTTP history filter")
        self.setMinimumSize(680, 430)
        self.resize(900, 560)
        self._original = spec
        self._build()
        self._load(spec)

    def _build(self) -> None:
        root = QVBoxLayout(self); root.setContentsMargins(8, 8, 8, 8); root.setSpacing(6)
        title = QLabel("HTTP history filter")
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 4px;")
        root.addWidget(title)

        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QScrollArea.NoFrame)
        content = QWidget(); content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(4, 4, 4, 4); content_layout.setSpacing(6)
        grid = QGridLayout(); grid.setHorizontalSpacing(8); grid.setVerticalSpacing(6)
        self._request = self._group("Filter by request type", [
            ("in_scope_only", "Show only in-scope items"),
            ("hide_without_responses", "Hide items without responses"),
            ("parameterized_only", "Show only parameterized requests"),
        ])
        self._mime = self._group("Filter by MIME type", [
            ("html", "HTML"), ("script", "Script"), ("xml", "XML"), ("css", "CSS"),
            ("other text", "Other text"), ("images", "Images"), ("flash", "Flash"),
            ("other binary", "Other binary"),
        ])
        self._status = self._group("Filter by status code", [
            ("2xx", "2xx [success]"), ("3xx", "3xx [redirection]"),
            ("4xx", "4xx [request error]"), ("5xx", "5xx [server error]"),
        ])
        fields_box = QGroupBox("Filter by request fields"); fields = QFormLayout(fields_box)
        fields.setContentsMargins(7, 14, 7, 6); fields.setVerticalSpacing(2); fields.setHorizontalSpacing(6)
        self.host = QLineEdit(); self.path = QLineEdit(); self.method = QLineEdit(); self.status = QLineEdit()
        self.mime = QLineEdit(); self.size = QLineEdit(); self.time = QLineEdit(); self.tool = QLineEdit()
        for edit, placeholder in ((self.host, "example.com"), (self.path, "/api/users"), (self.method, "GET"),
                                  (self.status, "200 or 2xx"), (self.mime, "text/html"), (self.size, ">1024"),
                                  (self.time, ">0"), (self.tool, "Proxy")):
            edit.setPlaceholderText(placeholder)
        for label, edit in (("Host:", self.host), ("Path:", self.path), ("Method:", self.method), ("Status:", self.status),
                            ("MIME:", self.mime), ("Size:", self.size), ("Time:", self.time), ("Tool:", self.tool)):
            fields.addRow(label, edit)
        # Keep the three compact checkbox groups together. The request-fields
        # form is the tallest section, so placing it beside a stacked column
        # uses the row height instead of leaving large blank areas below the
        # individual checkbox groups.
        compact_column = QWidget(); compact_layout = QVBoxLayout(compact_column)
        compact_layout.setContentsMargins(0, 0, 0, 0); compact_layout.setSpacing(6)
        compact_layout.addWidget(self._request); compact_layout.addWidget(self._mime)
        compact_layout.addWidget(self._status)
        grid.addWidget(compact_column, 0, 0)
        grid.addWidget(fields_box, 0, 1)
        grid.setColumnStretch(0, 1); grid.setColumnStretch(1, 2)
        row = QGridLayout(); row.setHorizontalSpacing(8); row.setVerticalSpacing(6)
        search_box = QGroupBox("Filter by search term"); search_layout = QVBoxLayout(search_box)
        search_layout.setContentsMargins(7, 14, 7, 6); search_layout.setSpacing(2)
        self.search = QLineEdit(); self.search.setPlaceholderText("Search requests and responses")
        search_layout.addWidget(self.search)
        self.regex = QCheckBox("Regex"); self.case_sensitive = QCheckBox("Case sensitive")
        self.negative = QCheckBox("Negative search")
        search_layout.addWidget(self.regex); search_layout.addWidget(self.case_sensitive); search_layout.addWidget(self.negative)
        row.addWidget(search_box, 0, 0)

        ext_box = QGroupBox("Filter by file extension"); ext_form = QFormLayout(ext_box)
        ext_form.setContentsMargins(7, 14, 7, 6); ext_form.setVerticalSpacing(2); ext_form.setHorizontalSpacing(6)
        self.show_ext = QLineEdit(); self.hide_ext = QLineEdit()
        self.show_ext.setPlaceholderText("asp,aspx,jsp,php"); self.hide_ext.setPlaceholderText("ico,css,woff,svg")
        ext_form.addRow("Show only:", self.show_ext); ext_form.addRow("Hide:", self.hide_ext)
        row.addWidget(ext_box, 0, 1)

        ann_box = QGroupBox("Filter by annotation"); ann_layout = QVBoxLayout(ann_box)
        ann_layout.setContentsMargins(7, 14, 7, 6); ann_layout.setSpacing(2)
        self.notes_only = QCheckBox("Show only items with notes")
        self.highlighted_only = QCheckBox("Show only highlighted items")
        ann_layout.addWidget(self.notes_only); ann_layout.addWidget(self.highlighted_only)
        row.addWidget(ann_box, 0, 2)

        listener_box = QGroupBox("Filter by listener"); listener_form = QFormLayout(listener_box)
        listener_form.setContentsMargins(7, 14, 7, 6); listener_form.setVerticalSpacing(2)
        self.port = QLineEdit(); self.port.setPlaceholderText("8080")
        listener_form.addRow("Port:", self.port); row.addWidget(listener_box, 0, 3)
        row.setColumnStretch(0, 2); row.setColumnStretch(1, 2)
        row.setColumnStretch(2, 1); row.setColumnStretch(3, 1)
        # Search and annotation controls stay at the top, with HTTPQL directly
        # beneath them. The request/MIME/status sections follow below.
        query_row = QGridLayout(); query_row.setHorizontalSpacing(6)
        query_row.addWidget(QLabel("HTTPQL:"), 0, 0)
        self.query = QLineEdit(); self.query.setPlaceholderText("host:example.com and status:2xx")
        query_row.addWidget(self.query, 0, 1)
        content_layout.addLayout(row)
        content_layout.addLayout(query_row)
        content_layout.addLayout(grid)
        scroll.setWidget(content); root.addWidget(scroll, 1)

        actions = QGridLayout(); actions.setHorizontalSpacing(4)
        show_all = QPushButton("Show all"); show_all.clicked.connect(self._show_all)
        hide_all = QPushButton("Hide all"); hide_all.clicked.connect(self._hide_all)
        revert = QPushButton("Revert changes"); revert.clicked.connect(lambda: self._load(self._original))
        actions.addWidget(show_all, 0, 0); actions.addWidget(hide_all, 0, 1); actions.addWidget(revert, 0, 2)
        actions.setColumnStretch(3, 1)
        buttons = QDialogButtonBox(QDialogButtonBox.Cancel)
        apply_button = buttons.addButton("Apply", QDialogButtonBox.ApplyRole)
        close_button = buttons.addButton("Apply & close", QDialogButtonBox.AcceptRole)
        buttons.rejected.connect(self.reject); apply_button.clicked.connect(self._apply); close_button.clicked.connect(self._accept)
        actions.addWidget(buttons, 0, 4); root.addLayout(actions)

    def _group(self, title: str, items: list[tuple[str, str]]) -> QGroupBox:
        box = QGroupBox(title); layout = QVBoxLayout(box)
        layout.setContentsMargins(7, 14, 7, 6); layout.setSpacing(1); box._items = {}
        for key, label in items:
            check = QCheckBox(label)
            check.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
            layout.addWidget(check, 0, Qt.AlignTop)
            box._items[key] = check
        layout.addStretch(1)
        box.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        return box

    def _load(self, spec: FilterSpec) -> None:
        for key, check in self._request._items.items(): check.setChecked(getattr(spec, key))
        for key, check in self._mime._items.items(): check.setChecked(key in spec.mime_types)
        for key, check in self._status._items.items(): check.setChecked(key in spec.status_classes)
        self.search.setText(spec.search); self.regex.setChecked(spec.regex); self.case_sensitive.setChecked(spec.case_sensitive)
        self.negative.setChecked(spec.negative_search); self.show_ext.setText(spec.show_extensions); self.hide_ext.setText(spec.hide_extensions)
        self.notes_only.setChecked(spec.notes_only); self.highlighted_only.setChecked(spec.highlighted_only)
        self.port.setText(spec.listener_port); self.query.setText(spec.query)
        self.host.setText(spec.host); self.path.setText(spec.path); self.method.setText(spec.method)
        self.status.setText(spec.status); self.mime.setText(spec.mime); self.size.setText(spec.size)
        self.time.setText(spec.time); self.tool.setText(spec.tool)

    def _show_all(self) -> None:
        for check in self._request._items.values(): check.setChecked(False)
        for group in (self._mime, self._status):
            for check in group._items.values(): check.setChecked(False)

    def _hide_all(self) -> None:
        for group in (self._request, self._mime, self._status):
            for check in group._items.values(): check.setChecked(False)

    def spec(self) -> FilterSpec:
        return FilterSpec(
            search=self.search.text().strip(), query=self.query.text().strip(),
            host=self.host.text().strip(), path=self.path.text().strip(), method=self.method.text().strip(),
            status=self.status.text().strip(), mime=self.mime.text().strip(), size=self.size.text().strip(),
            time=self.time.text().strip(), tool=self.tool.text().strip(),
            regex=self.regex.isChecked(), case_sensitive=self.case_sensitive.isChecked(), negative_search=self.negative.isChecked(),
            in_scope_only=self._request._items["in_scope_only"].isChecked(),
            hide_without_responses=self._request._items["hide_without_responses"].isChecked(),
            parameterized_only=self._request._items["parameterized_only"].isChecked(),
            mime_types={key for key, check in self._mime._items.items() if check.isChecked()},
            status_classes={key for key, check in self._status._items.items() if check.isChecked()},
            show_extensions=self.show_ext.text().strip(), hide_extensions=self.hide_ext.text().strip(),
            notes_only=self.notes_only.isChecked(), highlighted_only=self.highlighted_only.isChecked(),
            listener_port=self.port.text().strip(),
        )

    def _apply(self) -> None:
        self._applied = self.spec()
        self.filter_applied.emit(self._applied)

    def _accept(self) -> None:
        self._apply(); self.accept()

    def applied_spec(self) -> FilterSpec:
        return getattr(self, "_applied", self._original)
    filter_applied = Signal(object)
