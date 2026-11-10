"""Local tests for accidental infinite loops and noisy output."""

import sys
import unittest

from coderise.limited_run import execute_python


class LimitedRunTests(unittest.TestCase):
    def test_simple_output(self):
        result = execute_python([sys.executable, "-c", "print(2 + 3)"])
        self.assertEqual(result.stdout.strip(), "5")
        self.assertEqual(result.returncode, 0)
        self.assertFalse(result.timed_out)

    def test_unicode_input(self):
        result = execute_python(
            [sys.executable, "-X", "utf8", "-c", "print(input())"],
            stdin="Привет\n",
        )
        self.assertEqual(result.stdout.strip(), "Привет")

    def test_infinite_loop_stops(self):
        result = execute_python(
            [sys.executable, "-c", "while True: pass"], timeout=0.3,
        )
        self.assertTrue(result.timed_out)

    def test_infinite_print_stops_before_timeout(self):
        result = execute_python(
            [sys.executable, "-c", "while True: print('a' * 2048)"],
            timeout=2.0, max_output_bytes=8192,
        )
        self.assertTrue(result.too_much_output)
        self.assertLessEqual(len(result.stdout.encode("utf-8")), 8192)

    def test_nonzero_exit_and_stderr(self):
        result = execute_python(
            [sys.executable, "-c", "raise ValueError('wrong')"],
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ValueError", result.stderr)


if __name__ == "__main__":
    unittest.main()
