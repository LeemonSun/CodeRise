"""Главное окно CodeRise."""

import sys
from html import escape

from PySide6.QtCore import QSize, Qt, QTimer, QThread, Signal
from PySide6.QtGui import QBrush, QColor, QFont, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QTextBrowser,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from .curriculum import EXERCISES, STAGES, STAGES_BY_ID
from .study_views import StudyDialog
from .engine import CheckResult, check_solution
from .editor import PythonEditor
from .models import Exercise
from .progress import ProgressStore
from .line_help import explain_line


KIND_LABELS = {
    "predict": "УГАДАЙ РЕЗУЛЬТАТ",
    "fill": "ДОПИШИ КОД",
    "fix": "ИСПРАВЬ ОШИБКУ",
    "write": "НАПИШИ САМ",
}

STYLE = """
QPushButton#guide {
    border: 1px solid #385b80;
    color: #b6d7fa;
    background: #1a2b3f;
}
QPushButton#guide:hover {
    background: #28435c;
    color: #ffffff;
}
QLineEdit {
    background: #151f2c;
    selection-background-color: #3f658b;
}

QMainWindow, QWidget {
    background: #10141d;
    color: #e9edf5;
    font-family: 'Segoe UI', Arial;
    font-size: 13px;
}
QFrame#sidebar {
    background: #171d29;
    border-right: 1px solid #2c3646;
}
QLabel#logo {
    color: #f5f7fa;
    font-size: 26px;
    font-weight: 750;
}
QLabel#subtitle {
    color: #929eb2;
    font-size: 12px;
}
QLabel#minor {
    color: #9eacc2;
    font-size: 12px;
    font-weight: 650;
}
QLabel#bigTitle {
    color: #f2f5fa;
    font-size: 28px;
    font-weight: 750;
}
QLabel#chapter {
    color: #8bb9fa;
    font-size: 12px;
    font-weight: 700;
}
QLabel#prompt {
    color: #dce5f2;
    font-size: 15px;
}
QLabel#status {
    color: #9eacc2;
    font-size: 12px;
}
QLabel#hint {
    color: #e7d6a6;
    background: #29261e;
    border: 1px solid #59503a;
    border-radius: 9px;
    padding: 12px;
}
QLabel#explanation {
    color: #badfce;
    background: #1a2a27;
    border: 1px solid #30584a;
    border-radius: 9px;
    padding: 12px;
}
QListWidget {
    background: #171d29;
    border: 0;
    outline: 0;
    padding: 0 8px 8px 8px;
}
QListWidget::item {
    border-radius: 8px;
    padding: 6px 8px;
    margin: 1px 0;
}
QListWidget::item:selected {
    background: #2b405a;
    color: #ffffff;
}
QListWidget::item:hover:!selected {
    background: #222b39;
}
QProgressBar {
    color: transparent;
    background: #293442;
    border: 0;
    border-radius: 5px;
    max-height: 9px;
    min-height: 9px;
}
QProgressBar::chunk {
    background: #79b5ed;
    border-radius: 5px;
}
QPlainTextEdit, QLineEdit {
    color: #e8eefb;
    background: #171e2b;
    border: 1px solid #344155;
    border-radius: 10px;
    selection-background-color: #40658a;
    padding: 12px;
}
QPlainTextEdit:focus, QLineEdit:focus {
    border: 1px solid #79b5ed;
}
QPushButton {
    background: #273345;
    color: #e8eefb;
    border: 1px solid #394b63;
    border-radius: 9px;
    padding: 11px 17px;
    font-weight: 650;
}
QPushButton:hover {
    background: #34475d;
}
QPushButton:pressed {
    background: #263a52;
}
QPushButton#primary {
    background: #80b7f3;
    color: #0d1a2c;
    border: 1px solid #80b7f3;
}
QPushButton#primary:hover {
    background: #a0caff;
}
QPushButton:disabled {
    color: #697487;
    background: #1c2532;
    border-color: #283343;
}
QScrollArea {
    border: 0;
    background: #10141d;
}

QScrollBar:vertical { background: #171e2b; width: 10px; border: 0; }
QScrollBar::handle:vertical { background: #40536c; border-radius: 5px; min-height: 24px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QFrame#sidebar { background: #151d2a; }
QLabel#logo { color: #c4f2ff; letter-spacing: 1px; }
QPushButton#primary { background: #8bcfff; color: #0e2438; border: 0; }
QPushButton#primary:hover { background: #b4e1ff; }
QPushButton#guide { border-color: #395a78; background: #1a2b3f; }
QPushButton#guide:hover { background: #263f56; }
"""


class CheckWorker(QThread):
    """Проверяет код вне потока интерфейса."""

    result_ready = Signal(str, object)

    def __init__(self, exercise: Exercise, source: str, parent=None):
        super().__init__(parent)
        self.exercise = exercise
        self.source = source

    def run(self) -> None:
        try:
            result = check_solution(self.exercise, self.source)
        except Exception as error:
            result = CheckResult(
                False, "Не удалось завершить проверку.",
                f"{type(error).__name__}: {error}",
            )
        self.result_ready.emit(self.exercise.id, result)


class CodeRiseWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.store = ProgressStore()
        self.current: Exercise | None = None
        self._worker: CheckWorker | None = None
        self.setWindowTitle("CodeRise — Python")
        self.setMinimumSize(800, 560)
        self.resize(1220, 800)

        container = QWidget()
        self.setCentralWidget(container)
        outer = QHBoxLayout(container)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        self.sidebar = sidebar
        sidebar.setFixedWidth(270)
        outer.addWidget(sidebar)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(18, 24, 18, 20)
        sidebar_layout.setSpacing(12)

        logo = QLabel("CodeRise")
        logo.setObjectName("logo")
        sidebar_layout.addWidget(logo)

        tagline = QLabel("Код, практика, результат")
        tagline.setObjectName("subtitle")
        sidebar_layout.addWidget(tagline)
        version = QLabel("PYTHON  /  ОТ G ДО SSS")
        version.setObjectName("chapter")
        sidebar_layout.addWidget(version)

        self.progress_label = QLabel()
        self.progress_label.setObjectName("minor")
        sidebar_layout.addSpacing(18)
        sidebar_layout.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, len(EXERCISES))
        self.progress_bar.setTextVisible(False)
        sidebar_layout.addWidget(self.progress_bar)
        sidebar_layout.addSpacing(16)

        heading = QLabel("ЗАДАНИЯ  /  ОТ G ДО SSS")
        heading.setObjectName("minor")
        sidebar_layout.addWidget(heading)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Найти задание или главу…")
        self.search_input.setClearButtonEnabled(True)
        sidebar_layout.addWidget(self.search_input)

        self.review_button = QPushButton("Вернуться к сложным заданиям")
        self.review_button.setObjectName("guide")
        self.review_button.setToolTip("Переход к заданию, где уже были ошибки")
        self.review_button.clicked.connect(self.open_review)
        sidebar_layout.addWidget(self.review_button)

        self.exercise_list = QListWidget()
        self.exercise_list.setVerticalScrollMode(
            QAbstractItemView.ScrollMode.ScrollPerPixel
        )
        self.exercise_list.currentItemChanged.connect(self.on_selection_changed)
        self.search_input.textChanged.connect(self.filter_list)
        sidebar_layout.addWidget(self.exercise_list, stretch=1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        outer.addWidget(scroll, stretch=1)

        body = QWidget()
        scroll.setWidget(body)
        main_layout = QVBoxLayout(body)
        main_layout.setContentsMargins(34, 30, 34, 34)
        main_layout.setSpacing(14)

        self.chapter_label = QLabel()
        self.chapter_label.setObjectName("chapter")
        main_layout.addWidget(self.chapter_label)

        self.title_label = QLabel()
        self.title_label.setObjectName("bigTitle")
        self.title_label.setWordWrap(True)
        main_layout.addWidget(self.title_label)

        self.kind_label = QLabel()
        self.kind_label.setObjectName("minor")
        main_layout.addSpacing(2)
        main_layout.addWidget(self.kind_label)

        self.prompt_label = QLabel()
        self.prompt_label.setObjectName("prompt")
        self.prompt_label.setWordWrap(True)
        self.prompt_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        main_layout.addWidget(self.prompt_label)
        main_layout.addSpacing(4)

        self.editor_stack = QStackedWidget()
        self.editor_stack.setMinimumHeight(250)
        main_layout.addWidget(self.editor_stack)

        self.code_editor = PythonEditor()
        self.code_editor.setPlaceholderText("Пиши код здесь…")
        self.editor_stack.addWidget(self.code_editor)

        predict_page = QWidget()
        predict_layout = QVBoxLayout(predict_page)
        predict_layout.setContentsMargins(0, 0, 0, 0)
        predict_layout.setSpacing(12)

        self.readonly_code = PythonEditor()
        self.readonly_code.setReadOnly(True)
        self.readonly_code.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        predict_layout.addWidget(self.readonly_code, stretch=1)

        self.answer_input = QLineEdit()
        self.answer_input.setPlaceholderText("Что выведет программа?")
        self.answer_input.returnPressed.connect(self.on_check)
        predict_layout.addWidget(self.answer_input)
        self.editor_stack.addWidget(predict_page)

        actions = QHBoxLayout()
        actions.setSpacing(10)
        self.check_button = QPushButton("Проверить")
        self.check_button.setObjectName("primary")
        self.check_button.clicked.connect(self.on_check)
        actions.addWidget(self.check_button)

        self.hint_button = QPushButton("Подсказка")
        self.hint_button.setToolTip("Одна мысль, которая поможет решить самому")
        self.hint_button.clicked.connect(self.toggle_hint)
        actions.addWidget(self.hint_button)

        self.reset_button = QPushButton("Сбросить")
        self.reset_button.clicked.connect(self.on_reset)
        actions.addWidget(self.reset_button)
        actions.addStretch()

        self.next_button = QPushButton("Дальше →")
        self.next_button.clicked.connect(self.on_next)
        actions.addWidget(self.next_button)
        main_layout.addLayout(actions)

        help_actions = QGridLayout()
        help_actions.setSpacing(10)
        self.line_button = QPushButton("Разобрать строку")
        self.line_button.setObjectName("guide")
        self.line_button.setToolTip("Поставь курсор на нужную строку и нажми здесь")
        self.line_button.clicked.connect(self.open_line_help)
        help_actions.addWidget(self.line_button, 0, 0)
        self.study_button = QPushButton("Справка по заданию")
        self.study_button.setObjectName("guide")
        self.study_button.clicked.connect(lambda: self.open_study(0))
        help_actions.addWidget(self.study_button, 0, 1)
        self.theory_button = QPushButton("Теория главы")
        self.theory_button.setObjectName("guide")
        self.theory_button.clicked.connect(lambda: self.open_study(1))
        help_actions.addWidget(self.theory_button, 1, 0)
        self.solutions_button = QPushButton("Два решения")
        self.solutions_button.setObjectName("guide")
        self.solutions_button.clicked.connect(lambda: self.open_study(2))
        help_actions.addWidget(self.solutions_button, 1, 1)
        main_layout.addLayout(help_actions)

        self.hint_label = QLabel()
        self.hint_label.setObjectName("hint")
        self.hint_label.setWordWrap(True)
        self.hint_label.hide()
        main_layout.addWidget(self.hint_label)

        self.result_box = QPlainTextEdit()
        self.result_box.setReadOnly(True)
        self.result_box.setMaximumHeight(145)
        self.result_box.setMinimumHeight(92)
        self.result_box.hide()
        main_layout.addWidget(self.result_box)

        self.explanation_label = QLabel()
        self.explanation_label.setObjectName("explanation")
        self.explanation_label.setWordWrap(True)
        self.explanation_label.hide()
        main_layout.addWidget(self.explanation_label)

        self.status_label = QLabel()
        self.status_label.setObjectName("status")
        main_layout.addWidget(self.status_label)
        shortcuts = QLabel("Ctrl+Enter — проверить    •    Ctrl+H — подсказка    •    Код запускается на твоём ПК")
        shortcuts.setObjectName("subtitle")
        shortcuts.setWordWrap(True)
        main_layout.addWidget(shortcuts)
        main_layout.addStretch()

        for sequence in ("Ctrl+Return", "Ctrl+Enter"):
            shortcut = QShortcut(QKeySequence(sequence), self)
            shortcut.activated.connect(self.on_check)
        shortcut_hint = QShortcut(QKeySequence("Ctrl+H"), self)
        shortcut_hint.activated.connect(self.toggle_hint)

        self.draft_timer = QTimer(self)
        self.draft_timer.setSingleShot(True)
        self.draft_timer.setInterval(650)
        self.draft_timer.timeout.connect(self.save_current_draft)
        self.code_editor.textChanged.connect(self.schedule_draft_save)
        self.answer_input.textChanged.connect(self.schedule_draft_save)

        self.rebuild_sidebar()
        self.show_exercise(EXERCISES[0])

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        # Leave enough width for the editor when working on a small screen.
        if hasattr(self, "sidebar"):
            self.sidebar.setFixedWidth(220 if self.width() < 960 else 270)

    def update_progress(self) -> None:
        completed = sum(ex.id in self.store.solved for ex in EXERCISES)
        self.progress_label.setText(
            f"Решено {completed}/{len(EXERCISES)}   •   {completed * 20} XP   •   {sum(self.store.failures.values())} ошибок"
        )
        self.progress_bar.setValue(completed)

    def rebuild_sidebar(self) -> None:
        selected_id = self.current.id if self.current else EXERCISES[0].id
        self.exercise_list.blockSignals(True)
        self.exercise_list.clear()
        selected_row = 0

        for stage in STAGES:
            stage_exercises = [e for e in EXERCISES if e.stage == stage.code]
            finished = sum(e.id in self.store.solved for e in stage_exercises)
            header = QListWidgetItem(
                f" {stage.rank}  {stage.title.upper()}   {finished}/{len(stage_exercises)}"
            )
            header.setFlags(Qt.ItemFlag.NoItemFlags)
            header.setForeground(QBrush(QColor("#8495ae")))
            header.setSizeHint(QSize(244, 36))
            self.exercise_list.addItem(header)

            for number, exercise in enumerate(stage_exercises, start=1):
                done = exercise.id in self.store.solved
                prefix = "✓" if done else ("↻" if self.store.failures.get(exercise.id) else f"{number:02}")
                item = QListWidgetItem(f" {prefix}   {exercise.title}")
                item.setToolTip(exercise.title + "\n" + exercise.prompt)
                item.setData(Qt.ItemDataRole.UserRole, exercise.id)
                item.setSizeHint(QSize(244, 38))
                if done:
                    item.setForeground(QBrush(QColor("#a2dcc1")))
                self.exercise_list.addItem(item)
                if exercise.id == selected_id:
                    selected_row = self.exercise_list.count() - 1

        self.exercise_list.setCurrentRow(selected_row)
        self.exercise_list.blockSignals(False)
        self.update_progress()
        self.filter_list(self.search_input.text())

    def filter_list(self, query: str) -> None:
        term = query.casefold().strip()
        visible_stage = False
        header_row = None
        for row in range(self.exercise_list.count()):
            item = self.exercise_list.item(row)
            exercise_id = item.data(Qt.ItemDataRole.UserRole)
            if not exercise_id:
                if header_row is not None:
                    self.exercise_list.item(header_row).setHidden(not visible_stage)
                header_row, visible_stage = row, False
                item.setHidden(bool(term))
                continue
            exercise = next(ex for ex in EXERCISES if ex.id == exercise_id)
            stage = STAGES_BY_ID[exercise.stage]
            matches = not term or term in exercise.title.casefold() or term in stage.title.casefold() or term in stage.rank.casefold() or term in exercise.prompt.casefold()
            item.setHidden(not matches)
            visible_stage = visible_stage or matches
        if header_row is not None:
            self.exercise_list.item(header_row).setHidden(not visible_stage)

    def open_study(self, tab: int = 0) -> None:
        if self.current is not None:
            StudyDialog(self.current, self, tab=tab).exec()

    def open_line_help(self) -> None:
        if self.current is None:
            return
        editor = self.readonly_code if self.current.kind == "predict" else self.code_editor
        cursor = editor.textCursor()
        number = cursor.blockNumber() + 1
        selected = cursor.selectedText()
        line, notes = explain_line(editor.toPlainText(), number, selected)

        dialog = QDialog(self)
        dialog.setWindowTitle("CodeRise — разбираем строку")
        dialog.setMinimumSize(560, 400)
        dialog.resize(750, 520)
        layout = QVBoxLayout(dialog)
        heading = QLabel(f"Строка {number}: что здесь происходит?")
        heading.setStyleSheet("font-size:19px;font-weight:700;color:#d5edff;")
        layout.addWidget(heading)
        browser = QTextBrowser(dialog)
        pieces = [
            f'<pre style="padding:16px;background:#152437;color:#a5def5">'
            f'{escape(line or "(пустая строка)")}</pre>'
        ]
        if not notes:
            pieces.append("<p>Здесь нет известных команд. Проверь, где объявлены переменные.</p>")
        for term, detail in notes:
            if detail is None:
                pieces.append("<p>После # стоит комментарий. Python его не выполняет.</p>")
                continue
            pieces.append(
                f'<h3 style="color:#b3dfff">{escape(detail.title)}</h3>'
                f'<p>{escape(detail.meaning)}</p>'
                f'<pre style="color:#aee7bd">{escape(detail.example)}</pre>'
                f'<p style="color:#e5cb92">Частая ошибка: {escape(detail.pitfall)}</p>'
            )
        browser.setHtml(
            '<div style="font-family:Segoe UI;color:#e5edf9;line-height:1.5">'
            + "".join(pieces) + "</div>"
        )
        layout.addWidget(browser)
        close_button = QPushButton("Понятно")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)
        dialog.exec()

    def open_review(self) -> None:
        pending = [
            exercise for exercise in EXERCISES
            if exercise.id not in self.store.solved and self.store.failures.get(exercise.id, 0) > 0
        ]
        if not pending:
            self.status_label.setText("Непройденных заданий с ошибками пока нет.")
            return
        pending.sort(key=lambda exercise: -self.store.failures[exercise.id])
        self.search_input.clear()
        next_id = pending[0].id
        for row in range(self.exercise_list.count()):
            item = self.exercise_list.item(row)
            if item.data(Qt.ItemDataRole.UserRole) == next_id:
                self.exercise_list.setCurrentRow(row)
                self.exercise_list.scrollToItem(item)
                break

    def on_selection_changed(
        self, current_item: QListWidgetItem | None, _previous: QListWidgetItem | None
    ) -> None:
        if current_item is None:
            return
        exercise_id = current_item.data(Qt.ItemDataRole.UserRole)
        if not exercise_id:
            return
        self.draft_timer.stop()
        self.save_current_draft()
        exercise = next(ex for ex in EXERCISES if ex.id == exercise_id)
        self.show_exercise(exercise)

    def show_exercise(self, exercise: Exercise) -> None:
        self.current = exercise
        stage = STAGES_BY_ID[exercise.stage]
        self.chapter_label.setText(
            f"РАНГ {stage.rank}   /   {stage.title}   /   {stage.subtitle}"
        )
        self.title_label.setText(exercise.title)
        self.kind_label.setText(KIND_LABELS[exercise.kind])
        self.prompt_label.setText(exercise.prompt)
        self.code_editor.setPlainText(
            self.store.get_draft(exercise.id, exercise.starter)
        )
        self.readonly_code.setPlainText(exercise.starter)
        self.answer_input.setText(self.store.get_draft(exercise.id))
        self.editor_stack.setCurrentIndex(1 if exercise.kind == "predict" else 0)

        self.hint_label.setText("Подсказка: " + exercise.hint)
        self.hint_label.hide()
        self.hint_button.setText("Подсказка")
        self.result_box.clear()
        self.result_box.hide()
        self.explanation_label.setText(exercise.explanation)
        self.explanation_label.hide()
        self.status_label.setText(
            "✓ Уже решено. Можно попробовать ещё раз."
            if exercise.id in self.store.solved
            else "Решение сохраняется при переходе к другому заданию."
        )
        self.next_button.setEnabled(exercise != EXERCISES[-1])

    def schedule_draft_save(self) -> None:
        if self.current is not None:
            self.draft_timer.start()

    def save_current_draft(self) -> None:
        if self.current is None:
            return
        if self.current.kind == "predict":
            submission = self.answer_input.text()
        else:
            submission = self.code_editor.toPlainText()
        self.store.set_draft(self.current.id, submission)
        self.store.save()

    def on_check(self) -> None:
        if self.current is None or self._worker is not None:
            return
        submission = (
            self.answer_input.text()
            if self.current.kind == "predict"
            else self.code_editor.toPlainText()
        )
        self.draft_timer.stop()
        self.save_current_draft()
        self.check_button.setEnabled(False)
        self.check_button.setText("Проверяю…")
        self.next_button.setEnabled(False)
        self.reset_button.setEnabled(False)
        self.exercise_list.setEnabled(False)
        self.review_button.setEnabled(False)
        self.status_label.setText("Проверка идёт. Окно можно прокручивать и открывать справку.")
        self.result_box.hide()

        worker = CheckWorker(self.current, submission, self)
        self._worker = worker
        worker.result_ready.connect(self.on_check_result)
        worker.finished.connect(self.on_worker_finished)
        worker.finished.connect(worker.deleteLater)
        worker.start()

    def on_check_result(self, exercise_id: str, result: CheckResult) -> None:
        self.store.record_attempt(exercise_id, result.ok)
        if result.ok:
            self.store.mark_solved(exercise_id)
        self.store.save()
        self.update_progress()
        if self.current is None or self.current.id != exercise_id:
            self.rebuild_sidebar()
            return

        self.result_box.setPlainText(
            result.message + ("\n\n" + result.details if result.details else "")
        )
        self.result_box.show()
        self.rebuild_sidebar()
        self.explanation_label.setVisible(result.ok)
        self.status_label.setText(
            "✓ Задание выполнено." if result.ok
            else "Исправь код и проверь ещё раз."
        )

    def on_worker_finished(self) -> None:
        self._worker = None
        self.check_button.setEnabled(True)
        self.check_button.setText("Проверить")
        self.reset_button.setEnabled(True)
        self.exercise_list.setEnabled(True)
        self.review_button.setEnabled(True)
        self.next_button.setEnabled(self.current is not None and self.current != EXERCISES[-1])

    def toggle_hint(self) -> None:
        visible = not self.hint_label.isVisible()
        self.hint_label.setVisible(visible)
        self.hint_button.setText("Скрыть подсказку" if visible else "Подсказка")

    def on_reset(self) -> None:
        if self.current is None:
            return
        if self.current.kind == "predict":
            self.answer_input.clear()
        else:
            self.code_editor.setPlainText(self.current.starter)
        self.save_current_draft()
        self.result_box.hide()
        self.explanation_label.hide()
        self.status_label.setText("Черновик сброшен.")

    def on_next(self) -> None:
        if self.current is None:
            return
        index = EXERCISES.index(self.current)
        if index + 1 >= len(EXERCISES):
            return
        self.save_current_draft()
        next_id = EXERCISES[index + 1].id
        for row in range(self.exercise_list.count()):
            item = self.exercise_list.item(row)
            if item.data(Qt.ItemDataRole.UserRole) == next_id:
                self.exercise_list.setCurrentRow(row)
                break

    def closeEvent(self, event) -> None:
        if self._worker is not None and self._worker.isRunning():
            self.status_label.setText("Сначала закончится текущая проверка. Она ограничена по времени.")
            event.ignore()
            return
        self.draft_timer.stop()
        self.save_current_draft()
        super().closeEvent(event)


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("CodeRise")
    app.setStyle("Fusion")
    app.setStyleSheet(STYLE)
    window = CodeRiseWindow()
    window.show()
    sys.exit(app.exec())
