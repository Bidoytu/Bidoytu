"""Highlighter for the Intruder request template.

A :class:`~PySide6.QtGui.QTextDocument` can host only one
``QSyntaxHighlighter``, and the Intruder template wants both the normal HTTP
colouring *and* a visual callout for the ``§payload§`` positions. So this
subclass extends :class:`~bidoytu.ui.highlighter.HttpHighlighter` and, after the
base HTTP rules run, paints every ``§...§`` span (markers included) with a
distinct background so payload positions pop out.

The span match is done per text block (line). Because payload markers in a
request template are effectively always on a single line (method line, a header
value, or a body field), per-block matching is sufficient and keeps the
highlighter simple and fast.
"""
from __future__ import annotations

from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QColor, QFont, QTextCharFormat

from bidoytu.ui.highlighter import HttpHighlighter

MARKER = "\u00a7"  # §


class MarkerHighlighter(HttpHighlighter):
    """HTTP highlighting plus a highlighted background for ``§payload§`` spans."""

    def __init__(self, document) -> None:
        super().__init__(document)
        # Warm amber background with bold dark text so positions are obvious in
        # both light and dark themes.
        self._marker_fmt = QTextCharFormat()
        self._marker_fmt.setBackground(QColor("#f39c12"))
        self._marker_fmt.setForeground(QColor("#1a1a1a"))
        self._marker_fmt.setFontWeight(QFont.Bold)
        # A paired-marker span: §, anything but § (lazy), §.
        self._span = QRegularExpression(MARKER + r"[^" + MARKER + r"]*" + MARKER)

    def highlightBlock(self, text: str) -> None:
        # Run the base HTTP colouring first (method, status, header name/value).
        super().highlightBlock(text)
        # Then overlay the payload-position spans on top.
        it = self._span.globalMatch(text)
        while it.hasNext():
            match = it.next()
            self.setFormat(match.capturedStart(), match.capturedLength(),
                           self._marker_fmt)
