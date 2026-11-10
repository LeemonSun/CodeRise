"""Local course audit, no GitHub Actions.

Run: python scripts/check_course.py
Full reference checks: python scripts/check_course.py --solutions
"""

import argparse
from collections import Counter
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from coderise.curriculum import EXERCISES, STAGES
from coderise.engine import check_solution, normalize
from coderise.limited_run import execute_python
from coderise.reference import GUIDES, TOPICS


def validate() -> list[str]:
    faults = []
    ids = [e.id for e in EXERCISES]
    if len(ids) != len(set(ids)):
        faults.append("В курсе есть повторяющиеся ID заданий")
    if len(STAGES) != 10:
        faults.append(f"Ожидалось 10 глав, получено {len(STAGES)}")
    counts = Counter(e.stage for e in EXERCISES)
    for stage in STAGES:
        if counts[stage.code] != 14:
            faults.append(f"В главе {stage.rank} {counts[stage.code]} заданий вместо 14")
        if stage.code not in GUIDES:
            faults.append(f"Для главы {stage.rank} нет вводного урока")
    for e in EXERCISES:
        if not e.prompt.strip() or not e.hint.strip() or not e.walkthrough.strip():
            faults.append(f"{e.id}: нет условия, подсказки или разбора")
        if e.walkthrough.startswith("1. Разбери входные данные."):
            faults.append(f"{e.id}: осталось шаблонное объяснение")
        if len(e.methods) != 2:
            faults.append(f"{e.id}: должно быть два решения")
        if e.kind not in {"predict", "fill", "fix", "write"}:
            faults.append(f"{e.id}: неизвестный тип упражнения")
        if e.kind == "predict" and not e.answer:
            faults.append(f"{e.id}: отсутствует правильный ответ")
        elif e.kind != "predict" and not e.tests:
            faults.append(f"{e.id}: отсутствуют проверочные примеры")
        for concept in e.concepts:
            if concept not in TOPICS:
                faults.append(f"{e.id}: нет статьи для {concept}")
        for name, source in e.methods:
            if not name.strip():
                faults.append(f"{e.id}: пустое название способа")
            try:
                compile(source, e.id, "exec")
            except SyntaxError as error:
                faults.append(f"{e.id}: синтаксическая ошибка в примере: {error}")
    return faults


def check_all_solutions() -> tuple[int, list[str]]:
    checks, faults = 0, []
    with tempfile.TemporaryDirectory(prefix="coderise_audit_") as directory:
        script = Path(directory) / "answer.py"
        for exercise in EXERCISES:
            for label, source in exercise.methods:
                if exercise.kind == "predict":
                    script.write_text(source, encoding="utf-8")
                    result = execute_python(
                        [sys.executable, "-X", "utf8", "-I", str(script)],
                        timeout=3, cwd=directory,
                    )
                    checks += 1
                    if (result.returncode != 0 or
                            normalize(result.stdout) != normalize(exercise.answer)):
                        faults.append(f"{exercise.id} ({label}): неправильный вывод")
                else:
                    result = check_solution(exercise, source)
                    checks += len(exercise.tests)
                    if not result.ok:
                        faults.append(
                            f"{exercise.id} ({label}): {result.message}; {result.details[:250]}"
                        )
    return checks, faults


def main():
    parser = argparse.ArgumentParser(description="Проверка материалов CodeRise")
    parser.add_argument("--solutions", action="store_true",
                        help="проверить оба решения каждой задачи")
    args = parser.parse_args()
    faults = validate()
    print(f"Глав: {len(STAGES)} | заданий: {len(EXERCISES)} | понятий: {len(TOPICS)}")
    if args.solutions:
        checks, solution_faults = check_all_solutions()
        print(f"Проверочных запусков: {checks}")
        faults.extend(solution_faults)
    if faults:
        for fault in faults:
            print("ОШИБКА:", fault)
        raise SystemExit(1)
    print("Проверка прошла без ошибок.")


if __name__ == "__main__":
    main()
