"""Редактор для первых шагов в Python."""

import re

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QFont, QPainter, QSyntaxHighlighter, QTextCharFormat, QTextFormat, QTextCursor
from PySide6.QtWidgets import QPlainTextEdit, QTextEdit, QWidget


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


class LineNumberArea(QWidget):
    """Полоса с номерами строк у редактора."""

    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.line_number_width(), 0)

    def paintEvent(self, event):
        self.editor.paint_line_numbers(event)


class PythonEditor(QPlainTextEdit):
    """Пробелы вместо табуляции и отступ после двоеточия."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(QFont("Consolas", 12))
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setTabStopDistance(self.fontMetrics().horizontalAdvance("    "))
        self.highlighter = PythonHighlighter(self.document())
        self.gutter = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.update_line_number_width()
        self.highlight_current_line()

    def line_number_width(self) -> int:
        digits = len(str(max(1, self.blockCount())))
        return 15 + self.fontMetrics().horizontalAdvance("9") * digits + 10

    def update_line_number_width(self, _count=None) -> None:
        self.setViewportMargins(self.line_number_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy) -> None:
        if dy:
            self.gutter.scroll(0, dy)
        else:
            self.gutter.update(0, rect.y(), self.gutter.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_width()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        rect = self.contentsRect()
        self.gutter.setGeometry(rect.left(), rect.top(), self.line_number_width(), rect.height())

    def paint_line_numbers(self, event) -> None:
        painter = QPainter(self.gutter)
        painter.fillRect(event.rect(), QColor("#121c2a"))
        block = self.firstVisibleBlock()
        number = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())
        current = self.textCursor().blockNumber()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                color = "#b8dfff" if number == current else "#718299"
                painter.setPen(QColor(color))
                painter.drawText(
                    0, top, self.gutter.width() - 9, self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight, str(number + 1)
                )
            block = block.next()
            number += 1
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())

    def highlight_current_line(self) -> None:
        selection = QTextEdit.ExtraSelection()
        selection.format.setBackground(QColor("#1a2b40"))
        selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()
        self.setExtraSelections([selection])

    def keyPressEvent(self, event) -> None:
        if self.isReadOnly():
            super().keyPressEvent(event)
            return
        key = event.key()
        if key == Qt.Key.Key_Backtab:
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
            line = cursor.block().text()
            count = min(4, len(line) - len(line.lstrip(" ")))
            if count:
                cursor.movePosition(QTextCursor.MoveOperation.Right,
                                    QTextCursor.MoveMode.KeepAnchor, count)
                cursor.removeSelectedText()
            return
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
