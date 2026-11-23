import unittest

from core.deduplicator import Deduplicator
from core.validator import validate_candidate


class ValidatorTests(unittest.TestCase):
    def test_accepts_exact_twelve_character_code_case_insensitively(self):
        self.assertEqual(
            validate_candidate(" ab12cd34ef56 ", 0.9, 0.75),
            "AB12CD34EF56",
        )

    def test_accepts_observed_hyphenated_groups_and_normalizes_them(self):
        self.assertEqual(
            validate_candidate(" f27h - 7e2l - hp9q ", 0.9, 0.75),
            "F27H7E2LHP9Q",
        )

    def test_rejects_wrong_length_non_alphanumeric_and_low_confidence(self):
        self.assertIsNone(validate_candidate("ABC123", 0.99, 0.75))
        self.assertIsNone(validate_candidate("ABCD-234-EF56", 0.99, 0.75))
        self.assertIsNone(validate_candidate("F27H-7E2LHP9Q", 0.99, 0.75))
        self.assertIsNone(validate_candidate("AB12CD34EF56", 0.74, 0.75))
        self.assertIsNone(validate_candidate("AB12CD34EF56", float("nan"), 0.75))

    def test_deduplicates_only_within_the_configured_ttl(self):
        deduplicator = Deduplicator(ttl_seconds=10)
        self.assertFalse(deduplicator.is_duplicate("AB12CD34EF56", now=100))
        self.assertTrue(deduplicator.is_duplicate("AB12CD34EF56", now=105))
        self.assertFalse(deduplicator.is_duplicate("AB12CD34EF56", now=110))


if __name__ == "__main__":
    unittest.main()
