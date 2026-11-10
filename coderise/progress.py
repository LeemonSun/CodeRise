"""Локальный прогресс: решённые задания и черновики."""

import json
import os
from pathlib import Path


def default_progress_path() -> Path:
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA") or Path.home())
        return base / "CodeRise" / "progress.json"
    return Path.home() / ".coderise" / "progress.json"


class ProgressStore:
    def __init__(self, path: Path | None = None):
        self.path = path if path is not None else default_progress_path()
        self.solved: set[str] = set()
        self.drafts: dict[str, str] = {}
        self.load()

    def load(self) -> None:
        if not self.path.exists():
            return
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            solved = data.get("solved", [])
            drafts = data.get("drafts", {})
            if not isinstance(solved, list) or not isinstance(drafts, dict):
                return
            self.solved = {key for key in solved if isinstance(key, str)}
            self.drafts = {
                key: value
                for key, value in drafts.items()
                if isinstance(key, str) and isinstance(value, str)
            }
        except (OSError, ValueError, TypeError, AttributeError):
            # Битый файл не должен мешать запуску программы.
            self.solved = set()
            self.drafts = {}

    def get_draft(self, exercise_id: str, fallback: str = "") -> str:
        return self.drafts.get(exercise_id, fallback)

    def set_draft(self, exercise_id: str, source: str) -> None:
        self.drafts[exercise_id] = source

    def mark_solved(self, exercise_id: str) -> None:
        self.solved.add(exercise_id)

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "version": 1,
            "solved": sorted(self.solved),
            "drafts": self.drafts,
        }
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        temporary.replace(self.path)
