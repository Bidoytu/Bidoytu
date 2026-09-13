"""Dialogs for configuring an Intruder payload set.

A payload set is a *generator* (how raw payloads are produced) plus an ordered
list of *processing rules* (how each payload is transformed before use). This
module provides:

* :class:`ProcessingRuleDialog` - configure a single rule.
* :class:`PayloadSetEditor` - a self-contained widget with a generator selector
  (list / numbers / brute force / null) and a processing-rule list with
  add / edit / remove / reorder. It reads and writes
  :class:`~bidoytu.net.attack.PayloadSet`.

The tab embeds one :class:`PayloadSetEditor` per position set.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from bidoytu.net.attack import PayloadSet
from bidoytu.net.payloads import (
    GEN_BRUTE,
    GEN_LIST,
    GEN_NULL,
    GEN_NUMBERS,
    RULE_HASH,
    RULE_KINDS,
    RULE_LABELS,
    RULE_PREFIX,
    RULE_REGEX_REPLACE,
    RULE_SUFFIX,
    GeneratorSpec,
    ProcessingRule,
    describe_rule,
)


class ProcessingRuleDialog(QDialog):
    """Configure a single :class:`ProcessingRule`."""

    def __init__(self, rule: ProcessingRule | None = None, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Payload processing rule")
        self._kind = QComboBox()
        for kind in RULE_KINDS:
            self._kind.addItem(RULE_LABELS[kind], kind)
        self._kind.currentIndexChanged.connect(self._sync_fields)

        self._text = QLineEdit()
        self._algo = QComboBox()
        self._algo.addItems(["md5", "sha1", "sha256", "sha512"])
        self._pattern = QLineEdit()
        self._replacement = QLineEdit()

        form = QFormLayout()
        form.addRow("Rule:", self._kind)
        self._text_row = QLabel("Text:")
        form.addRow(self._text_row, self._text)
        self._algo_row = QLabel("Algorithm:")
        form.addRow(self._algo_row, self._algo)
        self._pattern_row = QLabel("Pattern:")
        form.addRow(self._pattern_row, self._pattern)
        self._replacement_row = QLabel("Replacement:")
        form.addRow(self._replacement_row, self._replacement)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

        if rule is not None:
            idx = self._kind.findData(rule.kind)
            if idx >= 0:
                self._kind.setCurrentIndex(idx)
            self._text.setText(rule.text)
            algo_idx = self._algo.findText(rule.algo)
            if algo_idx >= 0:
                self._algo.setCurrentIndex(algo_idx)
            self._pattern.setText(rule.pattern)
            self._replacement.setText(rule.replacement)
        self._sync_fields()

    def _sync_fields(self) -> None:
        kind = self._kind.currentData()
        show_text = kind in (RULE_PREFIX, RULE_SUFFIX)
        show_algo = kind == RULE_HASH
        show_regex = kind == RULE_REGEX_REPLACE
        self._text.setVisible(show_text)
        self._text_row.setVisible(show_text)
        self._algo.setVisible(show_algo)
        self._algo_row.setVisible(show_algo)
        self._pattern.setVisible(show_regex)
        self._pattern_row.setVisible(show_regex)
        self._replacement.setVisible(show_regex)
        self._replacement_row.setVisible(show_regex)

    def rule(self) -> ProcessingRule:
        return ProcessingRule(
            kind=self._kind.currentData(),
            text=self._text.text(),
            algo=self._algo.currentText(),
            pattern=self._pattern.text(),
            replacement=self._replacement.text(),
        )


class PayloadSetEditor(QWidget):
    """Edit one payload set: a generator plus a processing-rule pipeline."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._rules: list[ProcessingRule] = []

        # -- generator selector ---------------------------------------------
        self._gen_kind = QComboBox()
        self._gen_kind.addItem("Simple list", GEN_LIST)
        self._gen_kind.addItem("Numbers", GEN_NUMBERS)
        self._gen_kind.addItem("Brute forcer", GEN_BRUTE)
        self._gen_kind.addItem("Null payloads", GEN_NULL)
        self._gen_kind.currentIndexChanged.connect(self._on_gen_changed)

        self._gen_stack = QStackedWidget()
        self._gen_stack.addWidget(self._build_list_page())
        self._gen_stack.addWidget(self._build_numbers_page())
        self._gen_stack.addWidget(self._build_brute_page())
        self._gen_stack.addWidget(self._build_null_page())

        # -- processing rules -----------------------------------------------
        self._rule_list = QListWidget()
        add_rule = QPushButton("Add")
        add_rule.clicked.connect(self._add_rule)
        edit_rule = QPushButton("Edit")
        edit_rule.clicked.connect(self._edit_rule)
        del_rule = QPushButton("Remove")
        del_rule.clicked.connect(self._remove_rule)
        up_rule = QPushButton("\u25b2")
        up_rule.setMaximumWidth(30)
        up_rule.clicked.connect(lambda: self._move_rule(-1))
        down_rule = QPushButton("\u25bc")
        down_rule.setMaximumWidth(30)
        down_rule.clicked.connect(lambda: self._move_rule(1))

        rule_btns = QHBoxLayout()
        rule_btns.addWidget(add_rule)
        rule_btns.addWidget(edit_rule)
        rule_btns.addWidget(del_rule)
        rule_btns.addStretch(1)
        rule_btns.addWidget(up_rule)
        rule_btns.addWidget(down_rule)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        gen_row = QHBoxLayout()
        gen_row.addWidget(QLabel("Type:"))
        gen_row.addWidget(self._gen_kind)
        gen_row.addStretch(1)
        layout.addLayout(gen_row)
        layout.addWidget(self._gen_stack)
        rules_lbl = QLabel("Payload processing (applied in order)")
        rules_lbl.setStyleSheet("font-weight: bold; padding-top: 6px;")
        layout.addWidget(rules_lbl)
        layout.addWidget(self._rule_list, 1)
        layout.addLayout(rule_btns)

    # -- generator pages ------------------------------------------------------

    def _build_list_page(self) -> QWidget:
        page = QWidget()
        v = QVBoxLayout(page)
        v.setContentsMargins(0, 0, 0, 0)
        self._list_edit = QPlainTextEdit()
        self._list_edit.setPlaceholderText("One payload per line...")
        load_btn = QPushButton("Load from file...")
        load_btn.clicked.connect(self._load_list_file)
        v.addWidget(self._list_edit, 1)
        v.addWidget(load_btn)
        return page

    def _build_numbers_page(self) -> QWidget:
        page = QWidget()
        form = QFormLayout(page)
        self._num_from = QDoubleSpinBox()
        self._num_from.setRange(-1e12, 1e12)
        self._num_to = QDoubleSpinBox()
        self._num_to.setRange(-1e12, 1e12)
        self._num_to.setValue(100)
        self._num_step = QDoubleSpinBox()
        self._num_step.setRange(-1e9, 1e9)
        self._num_step.setValue(1)
        self._num_pad = QSpinBox()
        self._num_pad.setRange(0, 64)
        self._num_hex = QComboBox()
        self._num_hex.addItems(["Decimal", "Hex"])
        form.addRow("From:", self._num_from)
        form.addRow("To:", self._num_to)
        form.addRow("Step:", self._num_step)
        form.addRow("Zero-pad width:", self._num_pad)
        form.addRow("Base:", self._num_hex)
        return page

    def _build_brute_page(self) -> QWidget:
        page = QWidget()
        form = QFormLayout(page)
        self._brute_charset = QLineEdit("abcdefghijklmnopqrstuvwxyz0123456789")
        self._brute_min = QSpinBox()
        self._brute_min.setRange(1, 12)
        self._brute_min.setValue(1)
        self._brute_max = QSpinBox()
        self._brute_max.setRange(1, 12)
        self._brute_max.setValue(3)
        form.addRow("Character set:", self._brute_charset)
        form.addRow("Min length:", self._brute_min)
        form.addRow("Max length:", self._brute_max)
        return page

    def _build_null_page(self) -> QWidget:
        page = QWidget()
        form = QFormLayout(page)
        self._null_count = QSpinBox()
        self._null_count.setRange(1, 1_000_000)
        self._null_count.setValue(10)
        form.addRow("Repeat count:", self._null_count)
        note = QLabel("Sends the base request N times (empty payload).")
        note.setStyleSheet("color: gray;")
        form.addRow(note)
        return page

    def _on_gen_changed(self, index: int) -> None:
        self._gen_stack.setCurrentIndex(index)

    def _load_list_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Load payload list", "", "Text files (*.txt);;All files (*)"
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                content = fh.read()
        except OSError:
            return
        existing = self._list_edit.toPlainText()
        if existing.strip():
            content = existing.rstrip("\n") + "\n" + content
        self._list_edit.setPlainText(content)

    # -- processing rules -----------------------------------------------------

    def _refresh_rules(self) -> None:
        self._rule_list.clear()
        for rule in self._rules:
            item = QListWidgetItem(describe_rule(rule))
            item.setCheckState(Qt.Checked if rule.enabled else Qt.Unchecked)
            self._rule_list.addItem(item)

    def _add_rule(self) -> None:
        dialog = ProcessingRuleDialog(parent=self)
        if dialog.exec():
            self._rules.append(dialog.rule())
            self._refresh_rules()

    def _edit_rule(self) -> None:
        row = self._rule_list.currentRow()
        if not (0 <= row < len(self._rules)):
            return
        dialog = ProcessingRuleDialog(self._rules[row], parent=self)
        if dialog.exec():
            enabled = self._rules[row].enabled
            self._rules[row] = dialog.rule()
            self._rules[row].enabled = enabled
            self._refresh_rules()

    def _remove_rule(self) -> None:
        row = self._rule_list.currentRow()
        if 0 <= row < len(self._rules):
            self._rules.pop(row)
            self._refresh_rules()

    def _move_rule(self, delta: int) -> None:
        row = self._rule_list.currentRow()
        new = row + delta
        if 0 <= row < len(self._rules) and 0 <= new < len(self._rules):
            self._rules[row], self._rules[new] = self._rules[new], self._rules[row]
            self._refresh_rules()
            self._rule_list.setCurrentRow(new)

    def _sync_rule_enabled(self) -> None:
        for i, rule in enumerate(self._rules):
            item = self._rule_list.item(i)
            if item is not None:
                rule.enabled = item.checkState() == Qt.Checked

    # -- read / write PayloadSet ---------------------------------------------

    def to_payload_set(self) -> PayloadSet:
        self._sync_rule_enabled()
        kind = self._gen_kind.currentData()
        spec = GeneratorSpec(kind=kind)
        if kind == GEN_LIST:
            spec.items = [
                ln for ln in self._list_edit.toPlainText().split("\n")
            ]
            # Drop a single trailing empty line (common when editing).
            if spec.items and spec.items[-1] == "":
                spec.items.pop()
        elif kind == GEN_NUMBERS:
            spec.num_from = self._num_from.value()
            spec.num_to = self._num_to.value()
            spec.num_step = self._num_step.value()
            spec.num_pad = self._num_pad.value()
            spec.num_hex = self._num_hex.currentText() == "Hex"
        elif kind == GEN_BRUTE:
            spec.brute_charset = self._brute_charset.text()
            spec.brute_min = self._brute_min.value()
            spec.brute_max = self._brute_max.value()
        elif kind == GEN_NULL:
            spec.null_count = self._null_count.value()
        return PayloadSet(generator=spec, rules=list(self._rules))

    def load_payload_set(self, payload_set: PayloadSet) -> None:
        spec = payload_set.generator
        idx = self._gen_kind.findData(spec.kind)
        if idx >= 0:
            self._gen_kind.setCurrentIndex(idx)
        if spec.kind == GEN_LIST:
            self._list_edit.setPlainText("\n".join(spec.items))
        elif spec.kind == GEN_NUMBERS:
            self._num_from.setValue(spec.num_from)
            self._num_to.setValue(spec.num_to)
            self._num_step.setValue(spec.num_step)
            self._num_pad.setValue(spec.num_pad)
            self._num_hex.setCurrentText("Hex" if spec.num_hex else "Decimal")
        elif spec.kind == GEN_BRUTE:
            self._brute_charset.setText(spec.brute_charset)
            self._brute_min.setValue(spec.brute_min)
            self._brute_max.setValue(spec.brute_max)
        elif spec.kind == GEN_NULL:
            self._null_count.setValue(spec.null_count)
        self._rules = list(payload_set.rules)
        self._refresh_rules()
