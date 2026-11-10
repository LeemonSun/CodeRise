import unittest

from coderise.content import EXERCISES, EXERCISES_BY_ID
from coderise.engine import check_solution, normalize


REFERENCE_SOLUTIONS = {
    "g02": 'name = "Мир"\nprint(name)\n',
    "g03": 'print("Привет, мир!")\n',
    "g04": "age = 18\nprint(age)\n",
    "g06": "a = int(input())\nb = int(input())\nprint(a + b)\n",
    "f02": (
        'number = int(input())\nif number % 2 == 0:\n'
        '    print("чётное")\nelse:\n    print("нечётное")\n'
    ),
    "f03": (
        'n = int(input())\nif n > 3:\n'
        '    print("да")\nelse:\n    print("нет")\n'
    ),
    "f04": (
        'n = int(input())\nif n > 0:\n'
        '    print("плюс")\nelif n < 0:\n'
        '    print("минус")\nelse:\n    print("ноль")\n'
    ),
    "f06": "a = int(input())\nb = int(input())\nprint(min(a, b))\n",
    "e02": (
        "x = 0\nfor i in range(1, 6):\n"
        "    if i > 3:\n        x += i\nprint(x)\n"
    ),
    "e03": "for i in range(1, 4):\n    print(i)\n",
    "e04": "n = int(input())\nfor i in range(2, n + 1, 2):\n    print(i)\n",
    "e06": (
        "n = int(input())\nresult = 1\n"
        "for i in range(1, n + 1):\n    result *= i\nprint(result)\n"
    ),
    "d02": 'words = ["кот", "дом", "лес"]\nprint(len(words))\n',
    "d03": (
        "def square(x):\n    return x * x\n\n"
        "print(square(int(input())))\n"
    ),
    "d04": (
        "numbers = list(map(int, input().split()))\n"
        "print(sum(numbers))\n"
    ),
    "d06": (
        "def is_even(number):\n    return number % 2 == 0\n\n"
        "n = int(input())\nprint(is_even(n))\n"
    ),
}


class EngineTests(unittest.TestCase):
    def test_reference_solution_for_every_task(self):
        for exercise in EXERCISES:
            with self.subTest(exercise=exercise.id):
                submission = (
                    exercise.answer
                    if exercise.kind == "predict"
                    else REFERENCE_SOLUTIONS[exercise.id]
                )
                result = check_solution(exercise, submission)
                self.assertTrue(result.ok, result.message + "\n" + result.details)

    def test_wrong_output_is_rejected(self):
        result = check_solution(EXERCISES_BY_ID["g02"], 'print("не то")')
        self.assertFalse(result.ok)
        self.assertIn("Ожидалось", result.details)

    def test_syntax_error_is_shown(self):
        result = check_solution(EXERCISES_BY_ID["g04"], "if :")
        self.assertFalse(result.ok)
        self.assertIn("SyntaxError", result.details)

    def test_blank_submission_is_rejected(self):
        result = check_solution(EXERCISES_BY_ID["g03"], "   ")
        self.assertFalse(result.ok)

    def test_unix_and_windows_line_endings(self):
        self.assertEqual(normalize("1\r\n2\n"), normalize("1\n2"))

    def test_bad_prediction(self):
        result = check_solution(EXERCISES_BY_ID["g01"], "15")
        self.assertFalse(result.ok)


if __name__ == "__main__":
    unittest.main()
