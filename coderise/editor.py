"""Редактор для первых шагов в Python."""

import re

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QSyntaxHighlighter, QTextCharFormat
from PySide6.QtWidgets import QPlainTextEdit


class PythonHighlighter(QSyntaxHighlighter):
    KEYWORDS = re.compile(
        r"\b(?:and|as|assert|async|await|break|class|continue|def|del|"
        r"elif|else|except|False|finally|for|from|global|if|import|in|is|"
        r"lambda|nonlocal|not|or|pass|raise|return|True|try|while|with|yield)\b"
    )
    BUILTINS = re.compile(
        r"\b(?:print|input|int|str|float|len|range|list|dict|sum|min|max|"
        r"abs|enumerate|map|set|sorted|bool)\b"
    )
    NUMBERS = re.compile(r"\b\d+(?:\.\d+)?\b")
    STRINGS = re.compile(r"""(?:'(?:\\.|[^'\\])*'|"(?:\\.|[^"\\])*")""")
    COMMENTS = re.compile(r"#.*")

    def __init__(self, document):
        super().__init__(document)
        self.keyword_format = self._style("#c59aff", True)
        self.builtin_format = self._style("#8cbdff")
        self.number_format = self._style("#f5b66d")
        self.string_format = self._style("#9ed9a8")
        self.comment_format = self._style("#7f90a7")

    @staticmethod
    def _style(color: str, bold: bool = False) -> QTextCharFormat:
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        if bold:
            fmt.setFontWeight(QFont.Weight.Bold)
        return fmt

    def highlightBlock(self, text: str) -> None:
        for pattern, fmt in (
            (self.KEYWORDS, self.keyword_format),
            (self.BUILTINS, self.builtin_format),
            (self.NUMBERS, self.number_format),
            (self.STRINGS, self.string_format),
            (self.COMMENTS, self.comment_format),
        ):
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), fmt)


class PythonEditor(QPlainTextEdit):
    """Пробелы вместо табуляции и отступ после двоеточия."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(QFont("Consolas", 12))
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setTabStopDistance(32)
        self.highlighter = PythonHighlighter(self.document())

    def keyPressEvent(self, event) -> None:
        key = event.key()
        if key == Qt.Key.Key_Tab:
            self.textCursor().insertText("    ")
            return

        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            cursor = self.textCursor()
            line = cursor.block().text()
            leading = len(line) - len(line.lstrip(" "))
            indent = " " * leading
            if line.rstrip().endswith(":"):
                indent += "    "
            cursor.insertText("\n" + indent)
            return

        super().keyPressEvent(event)
