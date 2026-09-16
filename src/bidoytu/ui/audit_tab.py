"""Burp-inspired UI for the passive live audit."""
from __future__ import annotations

from collections import Counter

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView, QCheckBox, QHeaderView, QLabel, QListWidget, QLineEdit,
    QPlainTextEdit, QSplitter, QTabWidget, QTableView, QTextBrowser, QVBoxLayout,
    QWidget,
)

from bidoytu.audit.catalog import VULNERABILITY_CATALOG, VulnerabilityAdvisory
from bidoytu.audit.service import AuditIssue, AuditItem, LiveAuditService, Severity
from bidoytu.http_utils import ensure_host_header
from bidoytu.ui.audit_model import AuditIssueModel, AuditItemModel, SEVERITY_COLORS
from bidoytu.ui.body_format import content_type_from_headers
from bidoytu.ui.message_view import MessageView


class LiveAuditTab(QWidget):
    """Displays scope-limited, passive findings from proxied traffic."""

    enabled_changed = Signal(bool)
    active_changed = Signal(bool)
    active_result = Signal(object)
    body_provider = None

    def __init__(self, service: LiveAuditService, parent=None) -> None:
        super().__init__(parent)
        self._service = service
        self._items = AuditItemModel(self)
        self._issues = AuditIssueModel(self)

        self._toggle = QCheckBox("Enable passive live audit")
        self._toggle.setToolTip("Analyzes in-scope traffic already passing through the proxy. It never sends probes.")
        self._toggle.toggled.connect(self._on_toggle)
        self._active_toggle = QCheckBox("Enable active verification (safe methods only)")
        self._active_toggle.setToolTip(
            "Sends bounded diagnostic requests only for in-scope GET, HEAD, and OPTIONS traffic. "
            "POST/PUT/PATCH/DELETE requests are skipped."
        )
        self._active_toggle.toggled.connect(self._on_active_toggle)
        self._status = QLabel("Off — no traffic is being audited")
        self._status.setStyleSheet("color: #6b7280;")

        summary = QWidget(); summary_layout = QVBoxLayout(summary)
        self._summary = QLabel(); self._summary.setWordWrap(True)
        self._summary.setTextInteractionFlags(Qt.TextSelectableByMouse)
        summary_layout.addWidget(self._summary); summary_layout.addStretch(1)
        self._refresh_summary()

        items_view = self._table(self._items)
        issues_view = self._table(self._issues)
        issues_view.selectionModel().selectionChanged.connect(self._on_issue_selected)
        self._issues_view = issues_view

        self._advisory = QPlainTextEdit(); self._advisory.setReadOnly(True)
        self._request = MessageView(read_only=True)
        self._response = MessageView(read_only=True)
        self._path = QPlainTextEdit(); self._path.setReadOnly(True)
        detail_tabs = QTabWidget()
        detail_tabs.addTab(self._advisory, "Advisory")
        detail_tabs.addTab(self._request, "Request")
        detail_tabs.addTab(self._response, "Response")
        detail_tabs.addTab(self._path, "Path to issue")

        issue_panel = QWidget(); issue_layout = QVBoxLayout(issue_panel)
        issue_layout.setContentsMargins(0, 0, 0, 0)
        splitter = QSplitter(Qt.Vertical); splitter.addWidget(issues_view); splitter.addWidget(detail_tabs); splitter.setSizes([300, 420])
        issue_layout.addWidget(splitter)

        tabs = QTabWidget()
        tabs.addTab(summary, "Summary")
        tabs.addTab(items_view, "Audit items")
        tabs.addTab(issue_panel, "Issues")
        tabs.addTab(self._catalog_widget(), "Vulnerability catalog")
        self._tabs = tabs

        layout = QVBoxLayout(self); layout.setContentsMargins(8, 8, 8, 0)
        layout.addWidget(self._toggle); layout.addWidget(self._active_toggle)
        layout.addWidget(self._status); layout.addWidget(tabs, 1)

    def _catalog_widget(self) -> QWidget:
        """Build the local Burp-style advisory catalog and detail reader."""
        widget = QWidget(); layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        search = QLineEdit(); search.setPlaceholderText("Search vulnerability catalog...")
        layout.addWidget(search)
        split = QSplitter(Qt.Horizontal)
        listing = QListWidget(); listing.setMinimumWidth(250)
        reader = QTextBrowser(); reader.setOpenExternalLinks(True)
        reader.setHtml("<h2>Vulnerability catalog</h2><p>Select an entry to read its advisory.</p>")
        split.addWidget(listing); split.addWidget(reader); split.setSizes([300, 850])
        layout.addWidget(split, 1)

        def visible_entries(needle: str = "") -> list[VulnerabilityAdvisory]:
            query = needle.casefold().strip()
            return [entry for entry in VULNERABILITY_CATALOG if not query or query in f"{entry.name} {entry.aliases}".casefold()]

        def render(entry: VulnerabilityAdvisory) -> None:
            reader.setHtml(
                f"<h2>{entry.name}</h2><p><b>Burp severity:</b> {entry.severity} &nbsp; "
                f"<b>Scanner ID:</b> {entry.scanner_id}</p><p><b>Also known as:</b> {entry.aliases}</p>"
                f"<h3>Advisory</h3><p>{entry.summary}</p>"
                f"<h3>Potential impact</h3><p>{entry.impact}</p>"
                f"<h3>How it is detected</h3><p>{entry.detection}</p>"
                f"<h3>Prevention</h3><p>{entry.prevention}</p>"
                f"<h3>Bidoytu coverage</h3><p>{entry.bidoytu_coverage}</p>"
                f"<p><a href='{entry.url}'>Read the full PortSwigger advisory</a></p>"
            )

        def refill(needle: str = "") -> None:
            entries = visible_entries(needle); listing.clear()
            for entry in entries:
                listing.addItem(f"[{entry.severity}] {entry.name}")
            if entries:
                listing.setCurrentRow(0); render(entries[0])
            else:
                reader.setHtml("<h2>No matching vulnerability</h2><p>Try a different search term.</p>")

        def selected(row: int) -> None:
            entries = visible_entries(search.text())
            if 0 <= row < len(entries):
                render(entries[row])

        search.textChanged.connect(refill)
        listing.currentRowChanged.connect(selected)
        refill()
        return widget

    @staticmethod
    def _table(model):
        table = QTableView(); table.setModel(model); table.setSortingEnabled(True)
        table.setSelectionBehavior(QAbstractItemView.SelectRows); table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers); table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        table.horizontalHeader().setStretchLastSection(True)
        return table

    def _on_toggle(self, enabled: bool) -> None:
        if not enabled and self._active_toggle.isChecked():
            self._active_toggle.setChecked(False)
        self._service.set_enabled(enabled)
        self._status.setText("On — passively auditing in-scope proxy traffic" if enabled else "Off — no traffic is being audited")
        self._status.setStyleSheet("color: #15803d;" if enabled else "color: #6b7280;")
        self.enabled_changed.emit(enabled)
        self._refresh_summary()

    def _on_active_toggle(self, enabled: bool) -> None:
        if enabled and not self._service.enabled:
            self._toggle.setChecked(True)
        self.active_changed.emit(enabled)
        self._refresh_summary()

    def add(self, item: AuditItem, issues: list[AuditIssue]) -> None:
        self._items.add(item); self._issues.add_many(issues); self._refresh_summary()

    def add_active_issue(self, issue: AuditIssue) -> None:
        self._issues.add_many([issue]); self._refresh_summary()

    def clear(self) -> None:
        self._items.clear(); self._issues.clear(); self._advisory.clear(); self._request.clear_message(); self._response.clear_message(); self._path.clear(); self._refresh_summary()

    def _refresh_summary(self) -> None:
        counts = Counter(issue.severity for issue in self._issues.rows)
        colors = " ".join(f"<span style='color:{SEVERITY_COLORS[level]}'>{level}: {counts[level]}</span>" for level in Severity)
        coverage = ", ".join(LiveAuditService.COVERAGE)
        self._summary.setText(
            f"<h3>Passive live audit</h3><p>{'Enabled' if self._service.enabled else 'Disabled'}. "
            "Only in-scope traffic already captured by the proxy is analyzed; no requests are sent.</p>"
            f"<p><b>Audit items:</b> {len(self._items.rows)} &nbsp; <b>Issues:</b> {len(self._issues.rows)}<br>{colors}</p>"
            f"<p><b>Active verification:</b> {'enabled for safe methods' if self._active_toggle.isChecked() else 'off'}</p>"
            f"<p><b>Current coverage:</b> {coverage}.</p>"
            f"<p><b>Catalog:</b> {len(VULNERABILITY_CATALOG)} Burp issue definitions. "
            "Catalog inclusion and a scanner finding are intentionally distinct.</p>"
            "<p>Findings are evidence-based review items. Passive analysis cannot confirm exploitability or detect every vulnerability.</p>"
        )

    def _on_issue_selected(self) -> None:
        rows = self._issues_view.selectionModel().selectedRows()
        issue = self._issues.issue_at(rows[0].row()) if rows else None
        if issue is None:
            return
        evidence = ", ".join(f"{e.location}: {e.text}" for e in issue.evidence) or "Header or response condition was absent."
        self._advisory.setPlainText(
            f"{issue.title}\n\nSeverity: {issue.severity}\nConfidence: {issue.confidence}\nURL: {issue.url}\n\n"
            f"Issue detail\n{issue.detail}\n\nRemediation\n{issue.remediation}\n\nEvidence\n{evidence}"
        )
        record = issue.record
        request_body = self.body_provider(record, False) if self.body_provider else record.request_body_inline
        response_body = self.body_provider(record, True) if self.body_provider else record.response_body_inline
        request_headers = ensure_host_header(record.request_headers, record.host, record.port, record.scheme)
        self._request.show_message(f"{record.method} {record.path} {record.http_version}".strip(), request_headers, request_body, content_type_from_headers(request_headers))
        self._response.show_message(f"{record.http_version} {record.status_code or ''} {record.reason}".strip(), record.response_headers, response_body, record.content_type or content_type_from_headers(record.response_headers))
        self._request.set_evidence([e.text for e in issue.evidence if e.location == "request"])
        self._response.set_evidence([e.text for e in issue.evidence if e.location == "response"])
        self._path.setPlainText(
            "Observed proxy flow\n"
            f"  {record.method} {issue.url}\n"
            f"  status: {record.status_code if record.status_code is not None else 'pending'}\n"
            "  passive rule matched captured request/response evidence\n"
            f"  finding: {issue.title}"
        )
