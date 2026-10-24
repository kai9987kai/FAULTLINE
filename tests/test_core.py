import copy
import unittest

from faultline.core import analyze, metrics, select_panel, validate_dataset


def _make_parity_split_dataset() -> dict:
    """Dataset where c0..c2 have even-parity failures (3/4 majority error)
    and c3..c5 have odd-parity failures (1/4 majority error), with identical
    marginal (1/2) and pairwise (1/4) co-failure rates."""
    components = [
        {"id": f"c{i}", "name": f"Component {i}", "family": "even" if i < 3 else "odd"}
        for i in range(6)
    ]
    # For truth = 1, prediction = 1 - failure_bit
    even_failures = [
        [0, 0, 0],
        [1, 1, 0],
        [1, 0, 1],
        [0, 1, 1],
    ]
    odd_failures = [
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1],
        [1, 1, 1],
    ]
    calibration = []
    test = []
    idx = 0
    for rep in range(4):
        for ef in even_failures:
            for of in odd_failures:
                preds = [1 - b for b in (ef + of)]
                calibration.append(
                    {
                        "id": f"cal-{idx}",
                        "condition": "parity_stress",
                        "truth": 1,
                        "predictions": preds,
                    }
                )
                test.append(
                    {
                        "id": f"test-{idx}",
                        "condition": "parity_stress",
                        "truth": 1,
                        "predictions": list(preds),
                    }
                )
                idx += 1
    return {
        "schema": "faultline-dataset-v1",
        "name": "parity-split-benchmark",
        "components": components,
        "calibration": calibration,
        "test": test,
    }


def _make_four_selector_divergent_dataset() -> dict:
    """Dataset where accuracy, pairwise, pooled, and joint all choose distinct panels."""
    components = [
        {"id": f"c{i}", "name": f"Sensor {i}", "family": f"fam_{i}"}
        for i in range(6)
    ]
    # Two conditions: cond_a (40 rows), cond_b (20 rows) -> total 60 rows.
    # Truth is always 1 (so prediction 0 = failure, 1 = correct).
    # We design failure rows (sets of failing component indices):
    # - c0, c1, c2 have the lowest individual failure counts overall:
    #   On cond_b (20 rows):
    #     rows 0..3 (4 rows): {0, 1} fail
    #     rows 4..7 (4 rows): {0, 2} fail
    #     rows 8..11 (4 rows): {1, 2} fail
    #   So each of c0,c1,c2 fails only 8 times total (8/60 = 0.1333),
    #   making (c0,c1,c2) the unique winner for `accuracy` (sum = 24/60).
    #   However, on cond_b, (c0,c1,c2) has majority error on 12/20 = 0.60 rows!
    #
    # - For `pooled`: we want a panel with 0 majority errors on both cond_a and cond_b (or lowest total majority errors),
    #   say (c0, c1, c3):
    #   On cond_b, {0,1} fail on rows 0..3 (4 rows). Suppose c3 never fails on cond_b rows 4..11,
    #   Wait: if we want:
    #     accuracy -> (c0, c1, c2)
    #     pooled   -> (c0, c1, c3)
    #     pairwise -> (c2, c3, c4)
    #     joint    -> (c3, c4, c5)
    #   Let's set exact failure sets per row:
    cal_fail_sets_a = []
    for idx in range(40):
        if idx < 2:
            # 2 rows where {3, 4, 5} all fail together (majority error for (3,4,5) on A = 2/40 = 0.05)
            cal_fail_sets_a.append({3, 4, 5})
        elif idx < 11:
            # 9 rows where {2, 3} fail together (so any panel with {2,3} has 9 majority errors on A)
            cal_fail_sets_a.append({2, 3})
        elif idx < 20:
            # 9 rows where {2, 4} fail together
            cal_fail_sets_a.append({2, 4})
        elif idx < 29:
            # 9 rows where {3, 5} fail alone? No, keep c0, c1 very accurate on A:
            # Let {4, 5} fail on 3 rows (idx 20..22), and single failures for 3, 4, 5 on remaining rows
            if idx < 23:
                cal_fail_sets_a.append({4, 5})
            elif idx < 28:
                cal_fail_sets_a.append({3})
            elif idx < 33:
                cal_fail_sets_a.append({4})
            else:
                cal_fail_sets_a.append({5})

    # On cond_b (20 rows):
    cal_fail_sets_b = []
    for idx in range(20):
        if idx < 5:
            # 5 rows: {0, 1, 2} all fail -> (0,1,2) and any panel with two of {0,1,2} fails 5 rows on B (5/20 = 0.25)
            cal_fail_sets_b.append({0, 1, 2})
        elif idx < 8:
            # 3 rows: {0, 3}, {1, 3}, {2, 3} fail so panels combining one of {0,1,2} with 3 also fail on B
            cal_fail_sets_b.append({0, 1, 3})
        elif idx < 10:
            # 2 rows: {3, 4, 5} all fail together -> on B, (3,4,5) has only 2/20 = 0.10 majority error!
            # Wait: because all three {3,4,5} fail together on these 2 rows, its pairwise co-failure sum on B is 3 * (2/20) = 6/20 = 0.30!
            cal_fail_sets_b.append({3, 4, 5})
        elif idx < 13:
            # 3 rows: {0, 4} fail (so panels with {0,4} get extra failures on B)
            cal_fail_sets_b.append({0, 4})
        elif idx < 16:
            # 3 rows: {1, 5} fail
            cal_fail_sets_b.append({1, 5})
        elif idx == 16:
            # 1 row: {2, 3} fail on B
            cal_fail_sets_b.append({2, 3})
        elif idx == 17:
            # 1 row: {2, 4} fail on B
            cal_fail_sets_b.append({2, 4})
        elif idx == 18:
            # 1 row: {3, 4} fail on B -> for (2,3,4), on B it has 1+1+1 = 3 rows of 2-way failures (majority error 3/20 = 0.15 > 0.10 of (3,4,5),
            # but pairwise sum on B is only 3/20 = 0.15 < 6/20 = 0.30 of (3,4,5)!)
            cal_fail_sets_b.append({3, 4})
        else:
            cal_fail_sets_b.append({2, 5})

    calibration = []
    for idx, fset in enumerate(cal_fail_sets_a):
        calibration.append(
            {
                "id": f"cal-a-{idx}",
                "condition": "nominal_a",
                "truth": 1,
                "predictions": [0 if c in fset else 1 for c in range(6)],
            }
        )
    for idx, fset in enumerate(cal_fail_sets_b):
        calibration.append(
            {
                "id": f"cal-b-{idx}",
                "condition": "storm_b",
                "truth": 1,
                "predictions": [0 if c in fset else 1 for c in range(6)],
            }
        )
    test = [
        {
            "id": f"test-{i}",
            "condition": row["condition"],
            "truth": row["truth"],
            "predictions": list(row["predictions"]),
        }
        for i, row in enumerate(calibration)
    ]
    return {
        "schema": "faultline-dataset-v1",
        "name": "four-selector-divergent",
        "components": components,
        "calibration": calibration,
        "test": test,
    }


class TestCoreSelection(unittest.TestCase):
    def test_parity_compatible_cofailures_distinguishes_joint_from_pairwise(self):
        data = _make_parity_split_dataset()
        comps = data["components"]
        cal = data["calibration"]

        acc_panel = select_panel(comps, cal, 3, "accuracy")
        pair_panel = select_panel(comps, cal, 3, "pairwise")
        joint_panel = select_panel(comps, cal, 3, "joint")

        # (0,1,2) and (3,4,5) have identical marginal error (0.5 each) and pairwise co-failure (0.25 each pair),
        # so accuracy and pairwise tie-break lexically to (0,1,2) with 0.75 majority error,
        # while joint observes actual majority error and picks (3,4,5) with 0.25 majority error.
        self.assertEqual(acc_panel, (0, 1, 2))
        self.assertEqual(pair_panel, (0, 1, 2))
        self.assertEqual(joint_panel, (3, 4, 5))

        even_metrics = metrics(cal, acc_panel)
        odd_metrics = metrics(cal, joint_panel)
        self.assertAlmostEqual(even_metrics["error"], 0.75)
        self.assertAlmostEqual(odd_metrics["error"], 0.25)
        self.assertAlmostEqual(even_metrics["unanimous_wrong_rate"], 0.0)
        self.assertAlmostEqual(odd_metrics["unanimous_wrong_rate"], 0.25)

    def test_all_four_selectors_can_diverge_on_same_calibration_set(self):
        data = _make_four_selector_divergent_dataset()
        res = analyze(data, size=3)
        by_id = {p["id"]: p for p in res["policies"]}
        self.assertEqual(by_id["accuracy"]["panel"], ["c0", "c1", "c5"])
        self.assertEqual(by_id["pairwise"]["panel"], ["c0", "c3", "c5"])
        self.assertEqual(by_id["pooled"]["panel"], ["c0", "c2", "c5"])
        self.assertEqual(by_id["joint"]["panel"], ["c3", "c4", "c5"])
        distinct_panels = {tuple(p["panel"]) for p in res["policies"]}
        self.assertEqual(len(distinct_panels), 4)

    def test_deterministic_lexical_tie_breaking(self):
        components = [
            {"id": "z_sensor", "name": "Z", "family": "f"},
            {"id": "a_sensor", "name": "A", "family": "f"},
            {"id": "m_sensor", "name": "M", "family": "f"},
            {"id": "b_sensor", "name": "B", "family": "f"},
        ]
        # All components make identical predictions on all calibration rows
        calibration = [
            {"id": "c1", "condition": "nom", "truth": 1, "predictions": [1, 1, 1, 1]},
            {"id": "c2", "condition": "nom", "truth": 0, "predictions": [0, 0, 0, 0]},
        ]
        for policy in ("accuracy", "pairwise", "pooled", "joint"):
            chosen = select_panel(components, calibration, 3, policy)
            chosen_ids = tuple(components[i]["id"] for i in chosen)
            # Lexically smallest 3-subset of {"z_sensor", "a_sensor", "m_sensor", "b_sensor"}
            # sorted by component index order has IDs ("a_sensor", "m_sensor", "b_sensor") -> indices (1, 2, 3)
            self.assertEqual(chosen, (1, 2, 3))
            self.assertEqual(chosen_ids, ("a_sensor", "m_sensor", "b_sensor"))

    def test_panel_budget_and_invalid_size_or_policy(self):
        data = _make_parity_split_dataset()
        comps = data["components"]
        cal = data["calibration"]

        for bad_size in (0, 2, 4, 7, -1, True):
            with self.assertRaises(ValueError):
                select_panel(comps, cal, bad_size, "joint")

        with self.assertRaises(ValueError):
            select_panel(comps, cal, 3, "unknown_policy")

        # k=1 reduces to individual error
        p1 = select_panel(comps, cal, 1, "pairwise")
        self.assertEqual(len(p1), 1)

    def test_metrics_rejects_duplicate_boolean_or_out_of_bounds_panel_indices(self):
        data = _make_parity_split_dataset()
        cal = data["calibration"]
        for bad_panel in ((0, 0, 1), (True, 1, 2), (-1, 0, 1), (0, 1, 99)):
            with self.assertRaises(ValueError):
                metrics(cal, bad_panel)

    def test_validate_dataset_rejects_invalid_inputs(self):
        base = _make_parity_split_dataset()
        self.assertIsInstance(validate_dataset(base), dict)

        # 1. Unknown schema
        bad_schema = copy.deepcopy(base)
        bad_schema["schema"] = "wrong-schema"
        with self.assertRaises(ValueError):
            validate_dataset(bad_schema)

        # 2. Split ID overlap between calibration and test
        overlap = copy.deepcopy(base)
        overlap["test"][0]["id"] = overlap["calibration"][0]["id"]
        with self.assertRaises(ValueError):
            validate_dataset(overlap)

        # 3. Booleans as bits in truth or predictions
        bool_truth = copy.deepcopy(base)
        bool_truth["calibration"][0]["truth"] = True
        with self.assertRaises(ValueError):
            validate_dataset(bool_truth)

        bool_pred = copy.deepcopy(base)
        bool_pred["calibration"][0]["predictions"][0] = False
        with self.assertRaises(ValueError):
            validate_dataset(bool_pred)

        # 4. Ragged predictions
        ragged = copy.deepcopy(base)
        ragged["test"][0]["predictions"] = [1, 0]
        with self.assertRaises(ValueError):
            validate_dataset(ragged)

        # 5. Missing labels / non-binary values
        non_binary = copy.deepcopy(base)
        non_binary["calibration"][0]["predictions"][0] = 2
        with self.assertRaises(ValueError):
            validate_dataset(non_binary)

        # 6. Component count out of 3..12 range
        too_few = copy.deepcopy(base)
        too_few["components"] = too_few["components"][:2]
        for row in too_few["calibration"] + too_few["test"]:
            row["predictions"] = row["predictions"][:2]
        with self.assertRaises(ValueError):
            validate_dataset(too_few)

    def test_test_label_isolation(self):
        data = _make_parity_split_dataset()
        inverted_test = copy.deepcopy(data)
        for row in inverted_test["test"]:
            row["truth"] = 1 - row["truth"]
            row["predictions"] = [1 - p for p in row["predictions"]]

        res1 = analyze(data, size=3)
        res2 = analyze(inverted_test, size=3)

        for p1, p2 in zip(res1["policies"], res2["policies"]):
            self.assertEqual(p1["id"], p2["id"])
            self.assertEqual(p1["panel"], p2["panel"])
            self.assertEqual(p1["calibration"], p2["calibration"])
        self.assertEqual(res1["cofailure"], res2["cofailure"])


if __name__ == "__main__":
    unittest.main()
