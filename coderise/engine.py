"""Проверка решений. UI не должен знать, как запускается код."""

from dataclasses import dataclass
from pathlib import Path
import subprocess
import sys
import tempfile

from .models import Exercise


TIMEOUT_SECONDS = 3
MAX_SOURCE_LENGTH = 30_000
MAX_DISPLAY_LENGTH = 1_500


@dataclass(frozen=True, slots=True)
class CheckResult:
    ok: bool
    message: str
    details: str = ""
    passed: int = 0
    total: int = 0


def normalize(text: str) -> str:
    """Убираем разницу в переводах строк и пробелах справа."""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").strip().split("\n")
    return "\n".join(line.rstrip() for line in lines)


def _preview(value: str) -> str:
    value = value or "(пусто)"
    if len(value) > MAX_DISPLAY_LENGTH:
        return value[:MAX_DISPLAY_LENGTH] + "\n…(дальше обрезано)"
    return value


def _interpreter_command(script: Path) -> list[str]:
    # В сборке sys.executable указывает на CodeRise.exe, не на Python.
    if getattr(sys, "frozen", False):
        interpreter = Path(sys.executable).resolve().parent / "runtime" / "python.exe"
        if not interpreter.is_file():
            raise OSError("В сборке нет runtime/python.exe. Переустанови CodeRise.")
    else:
        interpreter = Path(sys.executable)
    return [str(interpreter), "-X", "utf8", "-I", "-B", str(script)]


def check_solution(exercise: Exercise, submission: str) -> CheckResult:
    if exercise.kind == "predict":
        answer = submission.strip()
        if not answer:
            return CheckResult(False, "Введи ответ, потом нажми «Проверить».")
        if normalize(answer) == normalize(exercise.answer):
            return CheckResult(True, "Верно. Так и работает.")
        return CheckResult(False, "Пока не совпало.", "Посмотри на код ещё раз или открой подсказку.")

    if not submission.strip() or submission.strip().startswith("#") and "\n" not in submission.strip():
        return CheckResult(False, "Сначала напиши код.")

    if len(submission) > MAX_SOURCE_LENGTH:
        return CheckResult(False, "Код слишком длинный для одного упражнения.")

    if not exercise.tests:
        return CheckResult(False, "У этого задания пока нет проверок.")

    with tempfile.TemporaryDirectory(prefix="coderise_") as directory:
        script = Path(directory) / "solution.py"
        script.write_text(submission, encoding="utf-8")
        for index, case in enumerate(exercise.tests, start=1):
            try:
                process = subprocess.run(
                    _interpreter_command(script),
                    input=case.stdin,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=directory,
                    timeout=TIMEOUT_SECONDS,
                    check=False,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                )
            except subprocess.TimeoutExpired:
                return CheckResult(
                    False,
                    "Программа выполняется слишком долго.",
                    "Проверь цикл: возможно, он не заканчивается.",
                    index - 1,
                    len(exercise.tests),
                )
            except OSError as error:
                return CheckResult(False, "Не удалось запустить Python.", str(error))

            if process.returncode != 0:
                return CheckResult(
                    False,
                    "Python остановился с ошибкой.",
                    _preview(process.stderr),
                    index - 1,
                    len(exercise.tests),
                )

            actual = normalize(process.stdout)
            expected = normalize(case.expected)
            if actual != expected:
                test_input = case.stdin.strip() or "(ввод не требуется)"
                return CheckResult(
                    False,
                    f"Тест {index} из {len(exercise.tests)} не пройден.",
                    "Ввод:\n"
                    + _preview(test_input)
                    + "\n\nОжидалось:\n"
                    + _preview(expected)
                    + "\n\nПолучилось:\n"
                    + _preview(actual),
                    index - 1,
                    len(exercise.tests),
                )

    count = len(exercise.tests)
    return CheckResult(
        True,
        "Готово. Все проверки пройдены.",
        f"Пройдено тестов: {count} из {count}.",
        count,
        count,
    )
