import unittest

from faultline.core import analyze, validate_dataset
from faultline.fixtures import make_dataset, parity_demo
from faultline.study import run_study


class TestFixturesAndStudy(unittest.TestCase):
    def test_parity_demo_exact_identity(self):
        demo = parity_demo()
        self.assertIn("even", demo)
        self.assertIn("odd", demo)

        even = demo["even"]
        odd = demo["odd"]
        self.assertEqual(even["marginals"], [0.5, 0.5, 0.5])
        self.assertEqual(odd["marginals"], [0.5, 0.5, 0.5])
        self.assertEqual(even["pairwise"], odd["pairwise"])
        self.assertEqual(
            even["pairwise"],
            [
                [0.5, 0.25, 0.25],
                [0.25, 0.5, 0.25],
                [0.25, 0.25, 0.5],
            ],
        )
        self.assertAlmostEqual(even["majority_error"], 0.75)
        self.assertAlmostEqual(odd["majority_error"], 0.25)
        self.assertEqual(len(even["patterns"]), 4)
        self.assertEqual(len(odd["patterns"]), 4)

    def test_event_keyed_fixtures_are_deterministic_and_prefix_consistent(self):
        d32_a = make_dataset(seed=4100, cases=32, scenario="shared")
        d32_b = make_dataset(seed=4100, cases=32, scenario="shared")
        self.assertEqual(d32_a, d32_b)
        validate_dataset(d32_a)

        # Because generation is event-keyed by (seed, split, condition, case_idx),
        # the 32 cases per condition in cases=32 must exactly match the first 32 cases
        # per condition in cases=64.
        d64 = make_dataset(seed=4100, cases=64, scenario="shared")
        by_id_64_cal = {r["id"]: r for r in d64["calibration"]}
        for row in d32_a["calibration"]:
            self.assertEqual(row, by_id_64_cal[row["id"]])

        by_id_64_test = {r["id"]: r for r in d64["test"]}
        for row in d32_a["test"]:
            self.assertEqual(row, by_id_64_test[row["id"]])

        # Calibration and test rows must not share predictions identically across all cases
        cal_preds = [r["predictions"] for r in d32_a["calibration"]]
        test_preds = [r["predictions"] for r in d32_a["test"]]
        self.assertNotEqual(cal_preds, test_preds)

    def test_make_dataset_rejects_invalid_bounds(self):
        for bad_cases in (15, 257, 0, True):
            with self.assertRaises(ValueError):
                make_dataset(seed=4100, cases=bad_cases, scenario="shared")
        with self.assertRaises(ValueError):
            make_dataset(seed=4100, cases=64, scenario="unknown")

    def test_shared_independent_and_shift_scenarios_preserve_positive_and_negative_controls(self):
        # 1. Shared scenario: joint reduces held-out worst-condition error vs accuracy, pairwise, pooled
        shared_study = run_study(seeds=list(range(4100, 4108)), cases=64, size=3, scenario="shared")
        vs_joint_shared = shared_study["aggregate"]["paired_vs_joint"]
        self.assertGreater(vs_joint_shared["accuracy"]["mean_diff_worst_group_error"], 0.10)
        self.assertGreater(vs_joint_shared["pairwise"]["mean_diff_worst_group_error"], 0.08)
        self.assertGreater(vs_joint_shared["pooled"]["mean_diff_worst_group_error"], 0.08)

        # 2. Independent scenario (negative control): joint does not systematically beat accuracy
        indep_study = run_study(seeds=list(range(4100, 4108)), cases=64, size=3, scenario="independent")
        vs_joint_indep = indep_study["aggregate"]["paired_vs_joint"]
        self.assertLessEqual(vs_joint_indep["accuracy"]["mean_diff_worst_group_error"], 0.02)

        # 3. Shift scenario (negative control): unseen common-cause fault in test causes joint to fail worse
        shift_study = run_study(seeds=list(range(4100, 4108)), cases=64, size=3, scenario="shift")
        vs_joint_shift = shift_study["aggregate"]["paired_vs_joint"]
        self.assertLess(vs_joint_shift["accuracy"]["mean_diff_worst_group_error"], -0.05)
        self.assertLess(vs_joint_shift["pairwise"]["mean_diff_worst_group_error"], -0.05)

    def test_study_bounds_and_structure(self):
        with self.assertRaises(ValueError):
            run_study(seeds=[], cases=64, size=3, scenario="shared")
        with self.assertRaises(ValueError):
            run_study(seeds=list(range(65)), cases=64, size=3, scenario="shared")

        res = run_study(seeds=[4100, 4101], cases=32, size=3, scenario="shared")
        self.assertEqual(res["n_seeds"], 2)
        self.assertEqual(len(res["runs"]), 2)
        for p_id in ("accuracy", "pairwise", "pooled", "joint"):
            self.assertIn(p_id, res["aggregate"]["policies"])


if __name__ == "__main__":
    unittest.main()
