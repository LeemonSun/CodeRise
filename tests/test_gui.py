"""Локальная проверка окна в невидимом режиме."""

import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest

from coderise.app import CodeRiseWindow
from coderise.curriculum import EXERCISES, STAGES
from coderise.progress import ProgressStore


class GuiSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])

    def wait_for_check(self, window, timeout=6):
        deadline = time.monotonic() + timeout
        while window._worker is not None and time.monotonic() < deadline:
            self.application.processEvents()
            QTest.qWait(20)
        self.application.processEvents()
        self.assertIsNone(window._worker, "Проверка не завершилась за отведённое время")

    def test_open_answer_and_switch_task(self):
        with tempfile.TemporaryDirectory() as directory:
            store = ProgressStore(Path(directory) / "progress.json")
            with patch("coderise.app.ProgressStore", return_value=store):
                window = CodeRiseWindow()
                window.show()
                self.assertEqual(window.current.id, "g01")
                self.assertEqual(window.exercise_list.count(), len(EXERCISES) + len(STAGES))
                self.assertEqual(len(EXERCISES), 140)
                self.assertIsNotNone(window.line_button)
                self.assertIsNotNone(window.review_button)
                self.assertIsNotNone(window.study_button)
                self.assertIsNotNone(window.solutions_button)
                self.assertIsNotNone(window.theory_button)
                window.search_input.setText("Факториал")
                self.assertLess(sum(not window.exercise_list.item(i).isHidden() for i in range(window.exercise_list.count())), window.exercise_list.count())
                window.search_input.clear()

                window.answer_input.setText("14")
                window.on_check()
                self.assertFalse(window.check_button.isEnabled())
                self.wait_for_check(window)
                self.assertIn("g01", window.store.solved)

                window.on_next()
                self.assertEqual(window.current.id, "g02")
                window.code_editor.setPlainText('name = "Мир"\nprint(name)')
                window.on_check()
                self.wait_for_check(window)
                self.assertIn("g02", window.store.solved)
                self.assertEqual(window.progress_bar.value(), 2)
                window.close()

            restored = ProgressStore(store.path)
            self.assertEqual(restored.solved, {"g01", "g02"})


    def test_wrong_answer_then_review_and_autosave(self):
        with tempfile.TemporaryDirectory() as directory:
            store = ProgressStore(Path(directory) / "progress.json")
            with patch("coderise.app.ProgressStore", return_value=store):
                window = CodeRiseWindow()
                window.show()
                window.answer_input.setText("999")
                window.on_check()
                self.wait_for_check(window)
                self.assertEqual(store.failures["g01"], 1)
                self.assertNotIn("g01", store.solved)
                window.on_next()
                window.code_editor.setPlainText("print('черновик')")
                QTest.qWait(850)
                self.application.processEvents()
                self.assertEqual(
                    ProgressStore(store.path).get_draft("g02"), "print('черновик')"
                )
                window.open_review()
                self.assertEqual(window.current.id, "g01")
                window.close()

    def test_buttons_fit_at_minimum_size(self):
        with tempfile.TemporaryDirectory() as directory:
            store = ProgressStore(Path(directory) / "progress.json")
            with patch("coderise.app.ProgressStore", return_value=store):
                window = CodeRiseWindow()
                window.resize(window.minimumSize())
                window.show()
                self.application.processEvents()
                for button in (
                    window.check_button, window.hint_button, window.reset_button,
                    window.next_button, window.line_button, window.study_button,
                    window.theory_button, window.solutions_button,
                ):
                    with self.subTest(button=button.text()):
                        required = button.fontMetrics().horizontalAdvance(
                            button.text()
                        ) + 26
                        self.assertGreaterEqual(
                            button.width(), required,
                            f"Обрезана надпись на кнопке: {button.text()}"
                        )
                window.close()


if __name__ == "__main__":
    unittest.main()
