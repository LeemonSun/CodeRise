import json
import tempfile
import unittest
from pathlib import Path

from coderise.progress import ProgressStore


class ProgressTests(unittest.TestCase):
    def test_progress_survives_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "progress.json"
            first = ProgressStore(path)
            first.mark_solved("g01")
            first.set_draft("g02", 'print("Мир")')
            first.save()

            second = ProgressStore(path)
            self.assertEqual(second.solved, {"g01"})
            self.assertEqual(second.get_draft("g02"), 'print("Мир")')
            self.assertEqual(second.get_draft("missing", "fallback"), "fallback")
            self.assertFalse(path.with_suffix(".tmp").exists())

    def test_broken_progress_does_not_crash(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "progress.json"
            path.write_text("{oops", encoding="utf-8")
            store = ProgressStore(path)
            self.assertEqual(store.solved, set())

    def test_save_is_unicode_and_versioned(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "progress.json"
            store = ProgressStore(path)
            store.set_draft("g03", "Привет")
            store.save()
            raw = path.read_text(encoding="utf-8")
            self.assertIn("Привет", raw)
            self.assertEqual(json.loads(raw)["version"], 1)


if __name__ == "__main__":
    unittest.main()
