"""Окна с объяснениями, примерами и справочником языка."""
from html import escape

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QHBoxLayout, QLabel, QLineEdit, QListWidget, QPlainTextEdit,
    QPushButton, QSplitter, QTabWidget, QTextBrowser, QVBoxLayout, QWidget,
)

from .reference import GUIDES, TOPICS


LEARNING_STYLE = """
QDialog { background: #101721; color: #e8edf7; }
QLabel { color: #e8edf7; font-family: 'Segoe UI'; }
QTabWidget::pane { border: 1px solid #2c3950; background: #151e2c; border-radius: 10px; }
QTabBar::tab { padding: 12px 18px; background: #202d3e; border-radius: 8px; margin: 3px; }
QTabBar::tab:selected { background: #477fb0; color: white; }
QTextBrowser, QPlainTextEdit { background: #151e2c; color: #dbe7fa; border: 0; padding: 14px; font-size: 13px; }
QListWidget { background: #151e2c; border: 1px solid #34455d; border-radius: 8px; }
QListWidget::item { padding: 9px; }
QListWidget::item:selected { background: #385678; }
QLineEdit { background: #1d2b3e; border: 1px solid #435977; border-radius: 9px; padding: 11px; color: #f2f7ff; }
QPushButton { background: #263950; padding: 10px 16px; border: 1px solid #4a6381; border-radius: 8px; color: #f6f8fc; }
QPushButton:hover { background: #344f70; }
"""


def code_block(source: str) -> str:
    return (
        '<pre style="background:#101825;border:1px solid #354662;'
        'padding:14px;border-radius:9px;white-space:pre-wrap;'
        'font-family:Consolas,monospace;color:#a6deee">'
        + escape(source)
        + '</pre>'
    )


def paragraph(text: str) -> str:
    return '<p style="color:#d3dded;line-height:1.6">' + escape(text).replace('\n', '<br>') + '</p>'


def title(text: str) -> str:
    return '<h2 style="color:#f5f8ff;margin-top:8px">' + escape(text) + '</h2>'


def hint_card(name: str, details: str) -> str:
    return '<div style="border-left:3px solid #8cbefa;padding-left:12px;margin:16px 0"><b style="color:#b9dafa">' + escape(name) + '</b>' + paragraph(details) + '</div>'


def info_html(exercise) -> str:
    guide = GUIDES.get(exercise.stage)
    chunks = [title('Что здесь нужно понять')]
    if guide:
        chunks.extend((paragraph(guide.overview),
                       hint_card('С чего начинать', guide.advice)))
    chunks.append(title('В самом задании'))
    chunks.append(paragraph(exercise.explanation))
    if exercise.walkthrough:
        chunks.extend((title('Порядок действий'), paragraph(exercise.walkthrough)))
    chunks.append(title('Обозначения и команды'))
    concepts = []
    for name in exercise.concepts:
        term = TOPICS.get(name)
        if term:
            concepts.append((name, term))
    if not concepts:
        chunks.append(paragraph('Открой полный справочник, чтобы разобрать любой оператор Python.'))
    for name, term in concepts:
        chunks.extend((title(term.title), paragraph(term.meaning), code_block(term.example),
                       hint_card('Осторожно', term.pitfall)))
    return ''.join(chunks)


def stage_html(stage_code: str) -> str:
    guide = GUIDES[stage_code]
    chunks = [title(guide.title), paragraph(guide.overview), title('После главы ты сможешь')]
    chunks.extend('<p style="color:#d3dded">• ' + escape(item) + '</p>' for item in guide.steps)
    chunks.extend((title('Пример'), code_block(guide.example), hint_card('Совет', guide.advice)))
    return ''.join(chunks)


def solutions_html(exercise) -> str:
    sections = [
        title("Разбор решения"),
        paragraph("Если ещё не пробовал сам — вернись к заданию. Здесь есть рабочие решения и примеры проверки."),
    ]
    if exercise.walkthrough:
        sections.append(hint_card("Как к этому прийти", exercise.walkthrough))
    for index, (label, source) in enumerate(exercise.methods, start=1):
        sections.append(title(f"{index}. {label}"))
        sections.append(code_block(source))
    if exercise.kind == "predict":
        sections.append(title("Ответ"))
        sections.append(code_block(exercise.answer))
        sections.append(paragraph(exercise.explanation))
    elif exercise.tests:
        sections.append(title("Проверим на примерах"))
        for index, case in enumerate(exercise.tests[:3], start=1):
            input_text = case.stdin.strip() or "(ввод не нужен)"
            output_text = case.expected.strip() or "(ничего не выводится)"
            sections.extend((
                hint_card(f"Пример {index}", "Ввод:"),
                code_block(input_text),
                paragraph("Ожидаемый результат:"),
                code_block(output_text),
            ))
    else:
        sections.append(paragraph("Для этого задания ещё нет проверочных примеров."))
    return "".join(sections)


class StudyDialog(QDialog):
    def __init__(self, exercise, parent=None, tab=0):
        super().__init__(parent)
        self.exercise = exercise
        self.setWindowTitle('CodeRise — разбираем по шагам')
        self.setMinimumSize(720, 550)
        self.resize(980, 720)
        self.setStyleSheet(LEARNING_STYLE)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(14)
        header = QLabel('СПРАВОЧНИК  /  ' + exercise.title)
        header.setStyleSheet('font-size:18px;font-weight:700;color:#c9e4ff;')
        layout.addWidget(header)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        self.tabs.addTab(self.browser(info_html(exercise)), 'Что за что отвечает')
        self.tabs.addTab(self.browser(stage_html(exercise.stage)), 'Тема целиком')
        self.tabs.addTab(self.browser(solutions_html(exercise)), 'Два способа решить')
        self.tabs.addTab(self.full_glossary(), 'Весь справочник')
        self.tabs.setCurrentIndex(tab)

        foot = QLabel('Лучше разобраться в одном решении, чем бездумно переписать два.')
        foot.setStyleSheet('color:#93a6bf;font-size:12px;')
        layout.addWidget(foot)

    @staticmethod
    def browser(html: str) -> QTextBrowser:
        browser = QTextBrowser()
        browser.setOpenExternalLinks(False)
        browser.setHtml('<html><body style="font-family:Segoe UI;background:#151e2c;">' + html + '</body></html>')
        return browser

    def full_glossary(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(12, 12, 12, 12)
        search = QLineEdit()
        search.setPlaceholderText('Поиск по командам: for, print, self, словарь…')
        layout.addWidget(search)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        names = QListWidget()
        names.setMinimumWidth(200)
        detail = QTextBrowser()
        detail.setMinimumWidth(350)
        splitter.addWidget(names)
        splitter.addWidget(detail)
        splitter.setSizes([220, 600])

        def fill(query=''):
            selected = names.currentItem().text() if names.currentItem() else ''
            names.clear()
            normalized = query.casefold().strip()
            for key, term in sorted(TOPICS.items(), key=lambda item: item[0].casefold()):
                if normalized in key.casefold() or normalized in term.meaning.casefold():
                    names.addItem(key)
            found = names.findItems(selected, Qt.MatchFlag.MatchExactly)
            if found:
                names.setCurrentItem(found[0])
            elif names.count():
                names.setCurrentRow(0)

        def show_term(item):
            if not item:
                detail.clear()
                return
            term = TOPICS[item.text()]
            detail.setHtml(title(term.title) + paragraph(term.meaning)
                           + code_block(term.example) + hint_card('Частая ошибка', term.pitfall))

        names.currentItemChanged.connect(lambda current, previous: show_term(current))
        search.textChanged.connect(fill)
        fill()
        return widget
