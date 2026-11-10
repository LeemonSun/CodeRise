"""Check the new course without launching the graphical interface."""
import collections
import contextlib
import io
import unittest
from unittest.mock import patch

from coderise.extra_content import EXTRA_EXERCISES, MORE_STAGES
from coderise.reference import GUIDES, TOPICS


class ExpandedCourseTests(unittest.TestCase):
    def test_ten_rank_structure(self):
        self.assertEqual(len(MORE_STAGES), 6)
        self.assertEqual(len(EXTRA_EXERCISES), 96)
        counts = collections.Counter(ex.stage for ex in EXTRA_EXERCISES)
        self.assertEqual(counts, {
            'start': 6, 'conditions': 6, 'loops': 6, 'data': 6,
            'functions': 12, 'files': 12, 'objects': 12,
            'algorithms': 12, 'projects': 12, 'mastery': 12,
        })

    def test_every_exercise_has_two_methods_and_theory(self):
        ids = set()
        for exercise in EXTRA_EXERCISES:
            with self.subTest(exercise=exercise.id):
                self.assertNotIn(exercise.id, ids)
                ids.add(exercise.id)
                self.assertGreaterEqual(len(exercise.tests), 2)
                self.assertEqual(len(exercise.methods), 2)
                self.assertTrue(exercise.hint.strip())
                self.assertTrue(exercise.explanation.strip())
                self.assertTrue(exercise.walkthrough.strip())
                self.assertTrue(exercise.concepts)
                self.assertTrue(all(c in TOPICS for c in exercise.concepts))
                for label, code in exercise.methods:
                    self.assertTrue(label.strip())
                    compile(code, exercise.id, 'exec')

    def test_every_stage_has_study_guide(self):
        for code in ('start', 'conditions', 'loops', 'data', 'functions', 'files',
                     'objects', 'algorithms', 'projects', 'mastery'):
            with self.subTest(stage=code):
                self.assertIn(code, GUIDES)
                self.assertTrue(GUIDES[code].steps)

    def test_all_reference_solutions(self):
        for exercise in EXTRA_EXERCISES:
            for label, code in exercise.methods:
                compiled = compile(code, exercise.id, 'exec')
                for case in exercise.tests:
                    with self.subTest(exercise=exercise.id, method=label, input=case.stdin):
                        stream, output = io.StringIO(case.stdin), io.StringIO()
                        with patch('builtins.input', side_effect=lambda prompt='': stream.readline().rstrip('\n')):
                            with contextlib.redirect_stdout(output):
                                exec(compiled, {'__name__': '__main__'})
                        self.assertEqual(output.getvalue().strip(), case.expected.strip())


if __name__ == '__main__':
    unittest.main()
