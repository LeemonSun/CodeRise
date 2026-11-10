"""Простой запуск интерфейса без монитора (для GitHub Actions)."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from coderise.app import CodeRiseWindow
from coderise.progress import ProgressStore


class GuiSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])

    def test_open_answer_and_switch_task(self):
        with tempfile.TemporaryDirectory() as directory:
            store = ProgressStore(Path(directory) / "progress.json")
            with patch("coderise.app.ProgressStore", return_value=store):
                window = CodeRiseWindow()
                window.show()
                self.assertEqual(window.current.id, "g01")
                self.assertEqual(window.exercise_list.count(), 28)

                window.answer_input.setText("14")
                window.on_check()
                self.assertIn("g01", window.store.solved)

                window.on_next()
                self.assertEqual(window.current.id, "g02")
                window.code_editor.setPlainText('name = "Мир"\nprint(name)')
                window.on_check()
                self.assertIn("g02", window.store.solved)
                self.assertEqual(window.progress_bar.value(), 2)
                window.close()

            restored = ProgressStore(store.path)
            self.assertEqual(restored.solved, {"g01", "g02"})


if __name__ == "__main__":
    unittest.main()
