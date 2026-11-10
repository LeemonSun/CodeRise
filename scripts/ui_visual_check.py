"""Render UI snapshots and check if action buttons fit their text.

Local only: python scripts/ui_visual_check.py
For high DPI on Windows:
  $env:QT_SCALE_FACTOR="1.5"; python scripts/ui_visual_check.py

Snapshots are saved to build/screenshots (ignored by Git).
"""

import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from coderise.app import CodeRiseWindow, STYLE
from coderise.progress import ProgressStore
from coderise.study_views import StudyDialog


def main() -> None:
    app = QApplication.instance() or QApplication([])
    app.setStyle("Fusion")
    app.setStyleSheet(STYLE)
    output = ROOT / "build" / "screenshots"
    output.mkdir(parents=True, exist_ok=True)
    failures = []

    with tempfile.TemporaryDirectory() as temp:
        progress = ProgressStore(Path(temp) / "progress.json")
        with patch("coderise.app.ProgressStore", return_value=progress):
            window = CodeRiseWindow()
            window.show()
            for width, height in ((800, 560), (960, 670), (1280, 800)):
                window.resize(width, height)
                app.processEvents()
                buttons = (
                    window.check_button, window.hint_button, window.reset_button,
                    window.next_button, window.line_button, window.study_button,
                    window.theory_button, window.solutions_button,
                )
                for button in buttons:
                    required = button.fontMetrics().horizontalAdvance(button.text()) + 26
                    if button.width() < required:
                        failures.append(
                            f"{width}x{height}: обрезана кнопка {button.text()!r} "
                            f"({button.width()} < {required})"
                        )
                path = output / f"main-{width}x{height}.png"
                if not window.grab().save(str(path)):
                    failures.append(f"Не удалось сохранить {path}")

            # Test the longest advanced task as well, not only the first lesson.
            for row in range(window.exercise_list.count()):
                item = window.exercise_list.item(row)
                if item.data(Qt.ItemDataRole.UserRole) == "mastery14":
                    window.exercise_list.setCurrentRow(row)
                    break
            app.processEvents()
            window.grab().save(str(output / "advanced.png"))

            for tab in range(4):
                dialog = StudyDialog(window.current, window, tab)
                dialog.show()
                app.processEvents()
                dialog.grab().save(str(output / f"reference-{tab}.png"))
                dialog.close()
            window.close()

    for item in failures:
        print("ОШИБКА:", item)
    if failures:
        raise SystemExit(1)
    print(f"Готово. Снимки окон: {output}")


if __name__ == "__main__":
    main()
