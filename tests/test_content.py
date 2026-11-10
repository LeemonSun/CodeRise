import unittest
from collections import Counter

from coderise.content import EXERCISES, EXERCISES_BY_ID, STAGES, STAGES_BY_ID


class ContentTests(unittest.TestCase):
    def test_unique_ids(self):
        ids = [exercise.id for exercise in EXERCISES]
        self.assertEqual(len(ids), len(set(ids)))

    def test_course_has_four_stages_with_six_tasks_each(self):
        self.assertEqual(len(STAGES), 4)
        self.assertEqual(len(EXERCISES), 24)
        counts = Counter(ex.stage for ex in EXERCISES)
        self.assertEqual(set(counts), set(STAGES_BY_ID))
        self.assertTrue(all(count == 6 for count in counts.values()))

    def test_each_exercise_is_checkable(self):
        for exercise in EXERCISES:
            with self.subTest(exercise=exercise.id):
                self.assertTrue(exercise.title.strip())
                self.assertTrue(exercise.prompt.strip())
                self.assertTrue(exercise.hint.strip())
                self.assertTrue(exercise.explanation.strip())
                self.assertIn(exercise.kind, {"predict", "fill", "fix", "write"})
                if exercise.kind == "predict":
                    self.assertTrue(exercise.answer)
                else:
                    self.assertGreater(len(exercise.tests), 0)
                self.assertIs(EXERCISES_BY_ID[exercise.id], exercise)


if __name__ == "__main__":
    unittest.main()
