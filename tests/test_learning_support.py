"""Локальные проверки подсказок, ошибок и упаковки без GUI."""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from coderise.engine import _interpreter_command
from coderise.error_guide import explain_python_error
from coderise.line_help import explain_line
from coderise.reference import TOPICS
from coderise.data_bundle import load_bundle


class StudySupportTests(unittest.TestCase):
    def test_explain_code_not_string_literal(self):
        line, notes = explain_line('text = "print(if)"', 1)
        self.assertEqual(line, 'text = "print(if)"')
        self.assertNotIn("print", [name for name, _ in notes])
        self.assertNotIn("if", [name for name, _ in notes])

    def test_for_loop_terms(self):
        _, notes = explain_line("for i in range(1, 6):", 1)
        names = [name for name, _ in notes]
        self.assertIn("for", names)
        self.assertIn("range", names)

    def test_variable_named_items_not_dict_method(self):
        _, notes = explain_line("print(items[-1])", 1)
        self.assertNotIn("items", [name for name, _ in notes])

    def test_comment(self):
        _, notes = explain_line("    # комментарий", 1)
        self.assertEqual(notes[0][0], "Комментарий")

    def test_name_error_hint(self):
        message = 'File "solution.py", line 2\nNameError: name \\'scoree\\' is not defined'
        hint = explain_python_error(message)
        self.assertIn("scoree", hint)
        self.assertIn("2", hint)

    def test_division_by_zero_hint(self):
        self.assertIn("ноль", explain_python_error("ZeroDivisionError: division by zero"))

    def test_course_has_no_repeated_generic_walkthrough(self):
        bundle = load_bundle()
        self.assertGreaterEqual(len(bundle["exercises"]), 116)
        self.assertGreaterEqual(len(TOPICS), 100)
        self.assertFalse(any(
            item["walkthrough"].startswith("1. Разбери входные данные.")
            for item in bundle["exercises"]
        ))

    def test_frozen_version_uses_real_python(self):
        with tempfile.TemporaryDirectory() as folder:
            exe = Path(folder) / "CodeRise.exe"
            runtime = Path(folder) / "runtime"
            runtime.mkdir()
            (runtime / "python.exe").write_bytes(b"placeholder")
            with patch.object(sys, "frozen", True, create=True), patch.object(sys, "executable", str(exe)):
                command = _interpreter_command(Path("solution.py"))
            self.assertEqual(Path(command[0]), runtime / "python.exe")
            self.assertIn("-I", command)


if __name__ == "__main__":
    unittest.main()
