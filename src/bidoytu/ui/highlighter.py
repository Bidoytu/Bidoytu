"""Lightweight syntax highlighting for raw HTTP messages.

Uses ``QSyntaxHighlighter`` over a ``QPlainTextEdit`` (the PySide6-friendly
fallback for QScintilla, which has no official PySide6 binding). This highlights
the request/response line, header names, and header values. It is intentionally
simple; a richer lexer (or a QScintilla/Monaco swap) can replace it later.
"""
from __future__ import annotations

import re

from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import (
    QColor,
    QFont,
    QSyntaxHighlighter,
    QTextCharFormat,
)


def _fmt(color: str, bold: bool = False) -> QTextCharFormat:
    f = QTextCharFormat()
    f.setForeground(QColor(color))
    if bold:
        f.setFontWeight(QFont.Bold)
    return f


class HttpHighlighter(QSyntaxHighlighter):
    """Highlights HTTP start-lines and headers."""

    def __init__(self, document) -> None:
        super().__init__(document)
        self._method_fmt = _fmt("#0a84ff", bold=True)
        self._header_name_fmt = _fmt("#7b61ff", bold=True)
        self._header_value_fmt = _fmt("#1f9d55")
        self._status_fmt = _fmt("#d9534f", bold=True)

        self._methods = QRegularExpression(
            r"^(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS|CONNECT|TRACE)\b"
        )
        self._status = QRegularExpression(r"^HTTP/\d(?:\.\d)?\s+\d{3}\b")
        self._header = QRegularExpression(r"^([A-Za-z0-9\-]+):\s*(.*)$")

    def highlightBlock(self, text: str) -> None:
        m = self._methods.match(text)
        if m.hasMatch():
            self.setFormat(m.capturedStart(), m.capturedLength(), self._method_fmt)
            return

        m = self._status.match(text)
        if m.hasMatch():
            self.setFormat(m.capturedStart(), m.capturedLength(), self._status_fmt)
            return

        m = self._header.match(text)
        if m.hasMatch():
            name_len = m.capturedEnd(1) - m.capturedStart(1)
            self.setFormat(m.capturedStart(1), name_len, self._header_name_fmt)
            val_len = m.capturedEnd(2) - m.capturedStart(2)
            if val_len > 0:
                self.setFormat(m.capturedStart(2), val_len, self._header_value_fmt)
