"""A single Intruder session: one request template + its attack + results.

This is the per-tab unit. The :class:`~bidoytu.ui.intruder_tab.IntruderTab`
container holds one of these per open tab, mirroring how ``RepeaterTab`` holds
``RepeaterSession`` instances.

Workflow, mirroring mature intruder tools:

1. A request template is loaded (via "Send to Intruder") or typed. Payload
   positions are marked with ``§`` markers - use the "Add §" button to wrap the
   current selection, or type them by hand. Marked positions are colour-
   highlighted in the template.
2. An **attack type** decides how positions and payload sets combine: Sniper,
   Battering ram, Pitchfork, or Cluster bomb.
3. One or more **payload sets** supply the values (list / numbers / brute force
   / null), each with an optional chain of processing rules.
4. **Start attack** iterates the resulting requests through the shared
   :class:`~bidoytu.net.async_sender.AsyncHttpSender` with bounded concurrency,
   filling a sortable, filterable results table.
5. Selecting a result shows its full request/response; results can be diffed
   against a baseline, copied as cURL, and exported to CSV. Attacks (template +
   config) save to and restore from JSON.
"""
from __future__ import annotations

import base64
import csv
import io
import json
from dataclasses import asdict
from pathlib import Path
from shlex import quote

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QGuiApplication, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QSplitter,
    QTabWidget,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from bidoytu.http_utils import (
    build_request_text,
    host_from_headers_or_url,
    parse_request_text,
)
from bidoytu.net.async_sender import AsyncHttpSender
from bidoytu.net.attack import (
    ATTACK_LABELS,
    ATTACK_TYPES,
    CLUSTER_BOMB,
    PITCHFORK,
    SNIPER,
    PayloadSet,
    count_jobs,
    find_markers,
    iter_jobs,
    strip_markers,
    wrap_selection,
)
from bidoytu.net.payloads import GeneratorSpec, ProcessingRule
from bidoytu.storage.models import FlowRecord
from bidoytu.ui.attack_runner import AttackRunner, GrepConfig, ResultRow
from bidoytu.ui.body_format import content_type_from_headers
from bidoytu.ui.find_bar import FindBar
from bidoytu.ui.intruder_results_model import (
    IntruderResultsModel,
    ResultFilterProxy,
)
from bidoytu.ui.marker_highlighter import MarkerHighlighter
from bidoytu.ui.message_view import RENDER_MODES, MessageView
from bidoytu.ui.payload_editor import PayloadSetEditor


class IntruderSession(QWidget):
    """One Intruder attack: template + positions + payload sets + results."""

    title_changed = Signal(str)  # emitted when the derived tab title changes
    send_to_repeater = Signal(object)  # FlowRecord (right-click)
    send_to_intruder = Signal(object)  # FlowRecord (right-click)

    def __init__(self, sender: AsyncHttpSender, name: str = "Intruder",
                 parent=None) -> None:
        super().__init__(parent)
        self._sender = sender
        self._name = name
        self._scheme = "http"
        self._host = ""
        self._port = 80

        self._runner: AttackRunner | None = None
        self._baseline: ResultRow | None = None
        # Optional provider returning a fresh Collaborator (OAST) payload host,
        # set by the container so the template context menu can insert one.
        self.payload_provider = None  # Callable[[], Optional[str]] | None

        self._model = IntruderResultsModel()
        self._proxy = ResultFilterProxy()
        self._proxy.setSourceModel(self._model)

        self._build_ui()
        self._wire_shortcuts()

    def name(self) -> str:
        return self._name

    def _wire_shortcuts(self) -> None:
        # Ctrl+R -> Send to Repeater, Ctrl+I -> Send to Intruder, matching the
        # send-to shortcuts used elsewhere in the app.
        rep_sc = QShortcut(QKeySequence("Ctrl+R"), self)
        rep_sc.activated.connect(self._send_to_repeater_shortcut)
        intr_sc = QShortcut(QKeySequence("Ctrl+I"), self)
        intr_sc.activated.connect(self._send_to_intruder_shortcut)

    def _send_to_repeater_shortcut(self) -> None:
        record = self._current_as_record()
        if record is not None:
            self.send_to_repeater.emit(record)

    def _send_to_intruder_shortcut(self) -> None:
        record = self._current_as_record()
        if record is not None:
            self.send_to_intruder.emit(record)

    # -- UI construction ------------------------------------------------------

    def _build_ui(self) -> None:
        self._tabs = QTabWidget()
        self._tabs.addTab(self._build_config_tab(), "Positions & Payloads")
        self._tabs.addTab(self._build_results_tab(), "Results")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(self._build_top_controls())
        layout.addWidget(self._tabs, 1)

    def _build_top_controls(self) -> QHBoxLayout:
        self._start_btn = QPushButton("Start attack")
        self._start_btn.setEnabled(False)
        self._start_btn.clicked.connect(self._start_attack)

        self._pause_btn = QPushButton("Pause")
        self._pause_btn.setEnabled(False)
        self._pause_btn.clicked.connect(self._toggle_pause)

        self._stop_btn = QPushButton("Stop")
        self._stop_btn.setEnabled(False)
        self._stop_btn.clicked.connect(self._stop_attack)

        self._attack_combo = QComboBox()
        for atype in ATTACK_TYPES:
            self._attack_combo.addItem(ATTACK_LABELS[atype], atype)

        self._concurrency = QSpinBox()
        self._concurrency.setRange(1, 100)
        self._concurrency.setValue(10)
        self._concurrency.setToolTip("Number of concurrent requests")

        self._follow_redirects = QCheckBox("Follow redirects")
        self._verify_tls = QCheckBox("Verify TLS")

        self._progress = QProgressBar()
        self._progress.setTextVisible(True)
        self._progress.setFormat("%v / %m")

        self._target_label = QLabel("No request loaded")

        row = QHBoxLayout()
        row.addWidget(self._start_btn)
        row.addWidget(self._pause_btn)
        row.addWidget(self._stop_btn)
        row.addSpacing(12)
        row.addWidget(QLabel("Attack:"))
        row.addWidget(self._attack_combo)
        row.addWidget(QLabel("Threads:"))
        row.addWidget(self._concurrency)
        row.addWidget(self._follow_redirects)
        row.addWidget(self._verify_tls)
        row.addSpacing(12)
        row.addWidget(self._progress, 1)
        row.addWidget(self._target_label)

        # Save / restore attack config.
        save_btn = QPushButton("Save")
        save_btn.setToolTip("Save this attack configuration to a file")
        save_btn.clicked.connect(self._save_attack_dialog)
        load_btn = QPushButton("Load")
        load_btn.setToolTip("Load an attack configuration from a file")
        load_btn.clicked.connect(self._load_attack_dialog)
        row.addWidget(save_btn)
        row.addWidget(load_btn)
        return row

    def _build_config_tab(self) -> QWidget:
        # -- template with marker buttons -----------------------------------
        # The template uses a highlighter that also colours §payload§ spans.
        self._template = MessageView(
            read_only=False, highlighter_factory=MarkerHighlighter
        )
        self._template.setContextMenuPolicy(Qt.CustomContextMenu)
        self._template.customContextMenuRequested.connect(self._on_context_menu)
        add_marker = QPushButton("Add \u00a7")
        add_marker.setToolTip("Wrap the selected text in payload markers")
        add_marker.clicked.connect(self._add_marker)
        clear_markers = QPushButton("Clear \u00a7")
        clear_markers.setToolTip("Remove all payload markers")
        clear_markers.clicked.connect(self._clear_markers)
        auto_markers = QPushButton("Auto (params)")
        auto_markers.setToolTip("Mark query/body parameter values automatically")
        auto_markers.clicked.connect(self._auto_mark_params)

        marker_row = QHBoxLayout()
        tlbl = QLabel("Request template")
        tlbl.setStyleSheet("font-weight: bold; padding: 4px;")
        marker_row.addWidget(tlbl)
        marker_row.addStretch(1)
        marker_row.addWidget(add_marker)
        marker_row.addWidget(clear_markers)
        marker_row.addWidget(auto_markers)

        template_pane = QWidget()
        tv = QVBoxLayout(template_pane)
        tv.setContentsMargins(0, 0, 0, 0)
        tv.addLayout(marker_row)
        tv.addWidget(self._template)

        # -- payload sets ----------------------------------------------------
        self._payload_tabs = QTabWidget()
        self._payload_editors: list[PayloadSetEditor] = []
        self._ensure_payload_sets(1)

        payload_pane = QWidget()
        pv = QVBoxLayout(payload_pane)
        pv.setContentsMargins(0, 0, 0, 0)
        plbl = QLabel("Payload sets")
        plbl.setStyleSheet("font-weight: bold; padding: 4px;")
        pv.addWidget(plbl)
        pv.addWidget(self._payload_tabs, 1)

        # -- grep match / extract -------------------------------------------
        self._grep_match = QLineEdit()
        self._grep_match.setPlaceholderText("Grep-match regex (flag matching responses)")
        self._grep_extract = QLineEdit()
        self._grep_extract.setPlaceholderText("Grep-extract regex (first group -> column)")
        grep_row = QHBoxLayout()
        grep_row.addWidget(QLabel("Match:"))
        grep_row.addWidget(self._grep_match, 1)
        grep_row.addWidget(QLabel("Extract:"))
        grep_row.addWidget(self._grep_extract, 1)
        pv.addLayout(grep_row)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(template_pane)
        splitter.addWidget(payload_pane)
        splitter.setSizes([700, 400])
        return splitter

    def _build_results_tab(self) -> QWidget:
        # -- filter bar ------------------------------------------------------
        self._filter_status = QComboBox()
        self._filter_status.addItem("All statuses", "")
        self._filter_status.addItem("2xx", "2")
        self._filter_status.addItem("3xx", "3")
        self._filter_status.addItem("4xx", "4")
        self._filter_status.addItem("5xx", "5")
        self._filter_status.currentIndexChanged.connect(
            lambda: self._proxy.set_status_prefix(self._filter_status.currentData())
        )
        self._filter_minlen = QSpinBox()
        self._filter_minlen.setRange(0, 1_000_000_000)
        self._filter_minlen.setToolTip("Minimum response length")
        self._filter_minlen.valueChanged.connect(self._proxy.set_min_length)
        self._filter_matched = QCheckBox("Only matched")
        self._filter_matched.stateChanged.connect(
            lambda s: self._proxy.set_matched_only(bool(s))
        )
        self._filter_needle = QLineEdit()
        self._filter_needle.setPlaceholderText("Filter by payload / extracted...")
        self._filter_needle.textChanged.connect(self._proxy.set_needle)

        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("Filter:"))
        filter_row.addWidget(self._filter_status)
        filter_row.addWidget(QLabel("Min len:"))
        filter_row.addWidget(self._filter_minlen)
        filter_row.addWidget(self._filter_matched)
        filter_row.addWidget(self._filter_needle, 1)

        baseline_btn = QPushButton("Set baseline")
        baseline_btn.setToolTip("Use the selected result as the diff baseline")
        baseline_btn.clicked.connect(self._set_baseline)
        diff_btn = QPushButton("Diff vs baseline")
        diff_btn.clicked.connect(self._diff_selected)
        curl_btn = QPushButton("Copy as cURL")
        curl_btn.clicked.connect(self._copy_selected_curl)
        csv_btn = QPushButton("Export CSV")
        csv_btn.clicked.connect(self._export_csv)
        clear_btn = QPushButton("Clear results")
        clear_btn.clicked.connect(self._clear_results)
        filter_row.addWidget(baseline_btn)
        filter_row.addWidget(diff_btn)
        filter_row.addWidget(curl_btn)
        filter_row.addWidget(csv_btn)
        filter_row.addWidget(clear_btn)

        # -- results table ---------------------------------------------------
        self._table = QTableView()
        self._table.setModel(self._proxy)
        self._table.setSortingEnabled(True)
        self._table.setSelectionBehavior(QTableView.SelectRows)
        self._table.setSelectionMode(QTableView.SingleSelection)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.selectionModel().currentRowChanged.connect(
            self._on_row_selected
        )

        # Compact rows matching the Proxy HTTP-history table: as tall as the
        # text plus a small pad, fixed height (Qt's default row height leaves a
        # large gap between rows).
        vheader = self._table.verticalHeader()
        vheader.setVisible(False)
        row_h = self._table.fontMetrics().height() + 2
        vheader.setSectionResizeMode(QHeaderView.Fixed)
        vheader.setDefaultSectionSize(row_h)
        vheader.setMinimumSectionSize(row_h)

        # -- detail view (request + response) --------------------------------
        self._req_view = MessageView(read_only=True)
        self._req_find = FindBar(self._req_view)
        self._resp_view = MessageView(read_only=True)
        self._resp_find = FindBar(self._resp_view)

        self._resp_mode = QComboBox()
        self._resp_mode.addItems(list(RENDER_MODES))
        self._resp_mode.currentTextChanged.connect(self._resp_view.set_render_mode)

        req_pane = QWidget()
        rv = QVBoxLayout(req_pane)
        rv.setContentsMargins(0, 0, 0, 0)
        rlbl = QLabel("Request")
        rlbl.setStyleSheet("font-weight: bold; padding: 4px;")
        rv.addWidget(rlbl)
        rv.addWidget(self._req_find)
        rv.addWidget(self._req_view, 1)

        resp_pane = QWidget()
        pv = QVBoxLayout(resp_pane)
        pv.setContentsMargins(0, 0, 0, 0)
        resp_header = QHBoxLayout()
        plbl = QLabel("Response")
        plbl.setStyleSheet("font-weight: bold; padding: 4px;")
        resp_header.addWidget(plbl)
        resp_header.addStretch(1)
        resp_header.addWidget(QLabel("View:"))
        resp_header.addWidget(self._resp_mode)
        pv.addLayout(resp_header)
        pv.addWidget(self._resp_find)
        pv.addWidget(self._resp_view, 1)

        detail = QSplitter(Qt.Horizontal)
        detail.addWidget(req_pane)
        detail.addWidget(resp_pane)
        detail.setSizes([600, 600])

        vertical = QSplitter(Qt.Vertical)
        top = QWidget()
        tv = QVBoxLayout(top)
        tv.setContentsMargins(0, 0, 0, 0)
        tv.addLayout(filter_row)
        tv.addWidget(self._table, 1)
        vertical.addWidget(top)
        vertical.addWidget(detail)
        vertical.setSizes([300, 400])

        container = QWidget()
        cv = QVBoxLayout(container)
        cv.setContentsMargins(0, 0, 0, 0)
        cv.addWidget(vertical)
        return container

    # -- payload sets ---------------------------------------------------------

    def _ensure_payload_sets(self, n: int) -> None:
        """Grow/shrink the payload-set tabs to exactly ``n`` (min 1)."""
        n = max(1, n)
        while len(self._payload_editors) < n:
            editor = PayloadSetEditor()
            self._payload_editors.append(editor)
            self._payload_tabs.addTab(editor, f"Set {len(self._payload_editors)}")
        while len(self._payload_editors) > n:
            idx = len(self._payload_editors) - 1
            self._payload_tabs.removeTab(idx)
            self._payload_editors.pop()

    def _sync_payload_sets_to_positions(self) -> None:
        """Pitchfork/cluster bomb use one set per position; others use one."""
        atype = self._attack_combo.currentData()
        _, markers = find_markers(self._template.toPlainText())
        if atype in (PITCHFORK, CLUSTER_BOMB):
            self._ensure_payload_sets(max(1, len(markers)))
        else:
            self._ensure_payload_sets(1)

    # -- marker editing -------------------------------------------------------

    def _add_marker(self) -> None:
        cursor = self._template.textCursor()
        text = self._template.toPlainText()
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        self._template.setPlainText(wrap_selection(text, start, end))

    def _clear_markers(self) -> None:
        self._template.setPlainText(strip_markers(self._template.toPlainText()))

    def _auto_mark_params(self) -> None:
        """Wrap each ``name=value`` value (query + body) in markers."""
        import re

        text = strip_markers(self._template.toPlainText())

        def mark_pairs(segment: str) -> str:
            # Replace value in name=value pairs with §value§.
            return re.sub(
                r"([?&;]?[\w.\-\[\]]+=)([^&;\r\n#]*)",
                lambda m: m.group(1) + "\u00a7" + m.group(2) + "\u00a7",
                segment,
            )

        lines = text.split("\n")
        if lines:
            # Request line: mark query-string values only.
            parts = lines[0].split(" ")
            if len(parts) >= 2 and "?" in parts[1]:
                path, _, query = parts[1].partition("?")
                parts[1] = path + "?" + mark_pairs(query)
                lines[0] = " ".join(parts)
        # Body (after blank line): mark form values.
        joined = "\n".join(lines)
        head, sep, body = joined.partition("\n\n")
        if sep and body.strip():
            body = mark_pairs(body)
        self._template.setPlainText(head + sep + body)

    # -- attack lifecycle -----------------------------------------------------

    def _start_attack(self) -> None:
        self._sync_payload_sets_to_positions()
        clean_text, markers = find_markers(self._template.toPlainText())
        if not markers:
            QMessageBox.warning(
                self, "No payload positions",
                "Mark at least one payload position with \u00a7 markers "
                "(select text and click 'Add \u00a7').",
            )
            return

        atype = self._attack_combo.currentData()
        if atype in (PITCHFORK, CLUSTER_BOMB):
            sets = [ed.to_payload_set() for ed in self._payload_editors]
        else:
            sets = [self._payload_editors[0].to_payload_set()]

        if not any(s.count() != 0 for s in sets):
            QMessageBox.warning(
                self, "No payloads",
                "Add at least one payload to the payload set.",
            )
            return

        total = count_jobs(atype, markers, sets)
        jobs = iter_jobs(clean_text, markers, atype, sets)

        grep = GrepConfig(
            match_pattern=self._grep_match.text(),
            extract_pattern=self._grep_extract.text(),
        )
        self._runner = AttackRunner(
            self._sender,
            concurrency=self._concurrency.value(),
            verify_tls=self._verify_tls.isChecked(),
            follow_redirects=self._follow_redirects.isChecked(),
            fallback_scheme=self._scheme,
            fallback_host=self._host,
            fallback_port=self._port,
            grep=grep,
            parent=self,
        )
        self._runner.row_ready.connect(self._model.add_row)
        self._runner.progress.connect(self._on_progress)
        self._runner.finished.connect(self._on_finished)

        self._model.clear()
        self._baseline = None
        self._progress.setMaximum(total if total and total > 0 else 0)
        self._progress.setValue(0)
        self._set_running_ui(True)
        self._tabs.setCurrentIndex(1)  # jump to Results
        self._target_label.setText("Attacking...")
        self._runner.start(jobs, total if total is not None else -1)

    def _toggle_pause(self) -> None:
        if self._runner is None:
            return
        if self._runner.is_paused():
            self._runner.resume()
            self._pause_btn.setText("Pause")
        else:
            self._runner.pause()
            self._pause_btn.setText("Resume")

    def _stop_attack(self) -> None:
        if self._runner is not None:
            self._runner.stop()
        self._target_label.setText("Stopping...")

    @Slot(int, int)
    def _on_progress(self, completed: int, total: int) -> None:
        if total and total > 0:
            self._progress.setMaximum(total)
        self._progress.setValue(completed)

    @Slot()
    def _on_finished(self) -> None:
        self._set_running_ui(False)
        self._target_label.setText(
            f"Done - {self._model.rowCount()} requests"
        )
        self._runner = None

    def _set_running_ui(self, running: bool) -> None:
        self._start_btn.setEnabled(not running)
        self._pause_btn.setEnabled(running)
        self._stop_btn.setEnabled(running)
        self._attack_combo.setEnabled(not running)
        self._concurrency.setEnabled(not running)
        if not running:
            self._pause_btn.setText("Pause")

    # -- results interaction --------------------------------------------------

    def _selected_row(self) -> ResultRow | None:
        index = self._table.currentIndex()
        if not index.isValid():
            return None
        source = self._proxy.mapToSource(index)
        return self._model.row_at(source.row())

    @Slot()
    def _on_row_selected(self, current, _previous=None) -> None:
        row = self._selected_row()
        if row is None:
            return
        self._req_view.setPlainText(row.request_text)
        if row.error:
            self._resp_view.setPlainText(f"Error: {row.error}")
            return
        ct = row.response_content_type or content_type_from_headers(
            row.response_headers
        )
        self._resp_view.show_message(
            row.response_start_line, row.response_headers,
            row.response_body, ct,
        )

    def _set_baseline(self) -> None:
        row = self._selected_row()
        if row is None:
            return
        self._baseline = row
        self._target_label.setText(f"Baseline: request #{row.index + 1}")

    def _diff_selected(self) -> None:
        row = self._selected_row()
        if row is None or self._baseline is None:
            QMessageBox.information(
                self, "Diff",
                "Select a result and set a baseline first.",
            )
            return
        import difflib

        base_text = self._baseline.response_body.decode("utf-8", errors="replace")
        cur_text = row.response_body.decode("utf-8", errors="replace")
        diff = difflib.unified_diff(
            base_text.splitlines(), cur_text.splitlines(),
            fromfile=f"baseline #{self._baseline.index + 1}",
            tofile=f"result #{row.index + 1}",
            lineterm="",
        )
        self._resp_view.setPlainText("\n".join(diff) or "(no differences)")

    def _copy_selected_curl(self) -> None:
        row = self._selected_row()
        if row is None:
            return
        parsed = parse_request_text(row.request_text)
        scheme, host, port, path = host_from_headers_or_url(
            parsed, self._host, self._scheme, self._port
        )
        default_ports = {"http": 80, "https": 443}
        netloc = host if port == default_ports.get(scheme) else f"{host}:{port}"
        url = f"{scheme}://{netloc}{path}"
        parts = ["curl", "-X", parsed.method, quote(url)]
        for k, v in parsed.headers:
            if k.lower() == "content-length":
                continue
            parts += ["-H", quote(f"{k}: {v}")]
        if parsed.body:
            parts += ["--data-binary", quote(parsed.body.decode("utf-8", "replace"))]
        if self._follow_redirects.isChecked():
            parts.append("-L")
        if not self._verify_tls.isChecked():
            parts.append("-k")
        QGuiApplication.clipboard().setText(" ".join(parts))
        self._target_label.setText("Copied cURL to clipboard")

    def _export_csv(self) -> None:
        if self._model.rowCount() == 0:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export results", "intruder_results.csv",
            "CSV files (*.csv);;All files (*)",
        )
        if not path:
            return
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["#", "Payloads", "Status", "Reason", "Length",
                         "Time (ms)", "Matched", "Extracted", "Error"])
        for row in self._model.all_rows():
            writer.writerow([
                row.index + 1, " | ".join(row.payloads),
                row.status_code if row.status_code is not None else "",
                row.reason, row.length, f"{row.duration_ms:.0f}",
                "yes" if row.matched else "", row.extracted, row.error,
            ])
        try:
            Path(path).write_text(buf.getvalue(), encoding="utf-8")
            self._target_label.setText(f"Exported {self._model.rowCount()} rows")
        except OSError as exc:
            QMessageBox.warning(self, "Export failed", str(exc))

    def _clear_results(self) -> None:
        self._model.clear()
        self._baseline = None
        self._req_view.clear_message()
        self._resp_view.clear_message()
        self._progress.setValue(0)

    # -- loading --------------------------------------------------------------

    def load_from_record(self, record: FlowRecord) -> None:
        self._scheme = record.scheme or "http"
        self._host = record.host
        self._port = record.port or (443 if self._scheme == "https" else 80)
        text = build_request_text(
            record.method, record.path, record.http_version,
            record.request_headers, record.request_body_inline,
        )
        self._template.setPlainText(text)
        self._target_label.setText(f"{self._scheme}://{self._host}:{self._port}")
        self._start_btn.setEnabled(True)
        self._tabs.setCurrentIndex(0)
        self._set_name_from_record(record)

    def _set_name_from_record(self, record: FlowRecord) -> None:
        path = (record.path or "/").split("?", 1)[0]
        short = path if len(path) <= 20 else path[:17] + "..."
        self._name = f"{record.method} {short}".strip() or "Intruder"
        self.title_changed.emit(self._name)

    # -- save / restore attack config ----------------------------------------

    def _serialize_attack(self) -> dict:
        sets = [ed.to_payload_set() for ed in self._payload_editors]
        return {
            "name": self._name,
            "scheme": self._scheme,
            "host": self._host,
            "port": self._port,
            "template_b64": base64.b64encode(
                self._template.toPlainText().encode("utf-8")
            ).decode("ascii"),
            "attack_type": self._attack_combo.currentData(),
            "concurrency": self._concurrency.value(),
            "follow_redirects": self._follow_redirects.isChecked(),
            "verify_tls": self._verify_tls.isChecked(),
            "grep_match": self._grep_match.text(),
            "grep_extract": self._grep_extract.text(),
            "payload_sets": [
                {
                    "generator": asdict(s.generator),
                    "rules": [asdict(r) for r in s.rules],
                }
                for s in sets
            ],
        }

    def _restore_attack(self, payload: dict) -> None:
        self._name = payload.get("name", self._name)
        self._scheme = payload.get("scheme", "http")
        self._host = payload.get("host", "")
        self._port = int(payload.get("port", 80))
        try:
            template = base64.b64decode(
                payload.get("template_b64", "")
            ).decode("utf-8", errors="replace")
        except Exception:
            template = ""
        self._template.setPlainText(template)

        atype = payload.get("attack_type", SNIPER)
        idx = self._attack_combo.findData(atype)
        if idx >= 0:
            self._attack_combo.setCurrentIndex(idx)
        self._concurrency.setValue(int(payload.get("concurrency", 10)))
        self._follow_redirects.setChecked(bool(payload.get("follow_redirects", False)))
        self._verify_tls.setChecked(bool(payload.get("verify_tls", False)))
        self._grep_match.setText(payload.get("grep_match", ""))
        self._grep_extract.setText(payload.get("grep_extract", ""))

        raw_sets = payload.get("payload_sets", [])
        self._ensure_payload_sets(len(raw_sets) or 1)
        for editor, raw in zip(self._payload_editors, raw_sets):
            gen = GeneratorSpec(**raw.get("generator", {}))
            rules = [ProcessingRule(**r) for r in raw.get("rules", [])]
            editor.load_payload_set(PayloadSet(generator=gen, rules=rules))

        self._target_label.setText(f"{self._scheme}://{self._host}:{self._port}")
        self._start_btn.setEnabled(bool(template.strip()))
        self.title_changed.emit(self._name)

    # -- public state accessors (used by the container) ----------------------

    def to_state(self) -> dict:
        """Return a JSON-serializable snapshot of this session."""
        return self._serialize_attack()

    def load_state(self, payload: dict) -> None:
        """Restore this session from a snapshot produced by :meth:`to_state`."""
        self._restore_attack(payload)

    def _save_attack_dialog(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Save attack", "intruder_attack.json",
            "JSON files (*.json);;All files (*)",
        )
        if not path:
            return
        try:
            Path(path).write_text(
                json.dumps(self._serialize_attack(), indent=2), encoding="utf-8"
            )
            self._target_label.setText("Attack saved")
        except OSError as exc:
            QMessageBox.warning(self, "Save failed", str(exc))

    def _load_attack_dialog(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Load attack", "", "JSON files (*.json);;All files (*)"
        )
        if not path:
            return
        try:
            payload = json.loads(Path(path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            QMessageBox.warning(self, "Load failed", str(exc))
            return
        self._restore_attack(payload)

    # -- context menu / send-to ----------------------------------------------

    def _on_context_menu(self, pos) -> None:
        record = self._current_as_record()
        menu = QMenu(self)
        act_rep = menu.addAction("Send to Repeater\tCtrl+R")
        act_int = menu.addAction("Send to Intruder\tCtrl+I")
        act_rep.setEnabled(record is not None)
        act_int.setEnabled(record is not None)
        act_oast = None
        if self.payload_provider is not None:
            menu.addSeparator()
            act_oast = menu.addAction("Insert Collaborator payload")
        chosen = menu.exec(self._template.viewport().mapToGlobal(pos))
        if chosen is not None and chosen == act_oast:
            self._insert_collaborator_payload()
            return
        if record is None:
            return
        if chosen == act_rep:
            self.send_to_repeater.emit(record)
        elif chosen == act_int:
            self.send_to_intruder.emit(record)

    def _insert_collaborator_payload(self) -> None:
        if self.payload_provider is None:
            return
        host = self.payload_provider()
        if host:
            self._template.insertPlainText(host)

    def _current_as_record(self) -> FlowRecord | None:
        """Build a FlowRecord from the template (payload markers removed)."""
        text = strip_markers(self._template.toPlainText())
        if not text.strip():
            return None
        parsed = parse_request_text(text)
        return FlowRecord(
            flow_id="",
            method=parsed.method,
            scheme=self._scheme,
            host=self._host,
            port=self._port,
            path=parsed.path,
            http_version=parsed.http_version,
            request_headers="\r\n".join(f"{k}: {v}" for k, v in parsed.headers),
            request_body_inline=parsed.body or None,
            request_body_size=len(parsed.body),
        )
