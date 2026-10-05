import unittest

from ml.src.evaluate import compute_baseline_vs_predictive


class BaselineComparisonTests(unittest.TestCase):
    def test_counts_tier_downgrades_false_alerts_and_interval_misses(self):
        result = compute_baseline_vs_predictive(
            y_true=[10, 14, 8, 50, 51, 120],
            y_pred=[16, 15, 10, 49, 49, 110],
        )

        self.assertEqual(
            result,
            {
                "fixed_interval_missed_failures": 5,
                "predictive_missed_failures": 1,
                "fixed_interval_unnecessary_services": 1,
                "predictive_unnecessary_services": 1,
                "total_test_engines": 6,
            },
        )


if __name__ == "__main__":
    unittest.main()