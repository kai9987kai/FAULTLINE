"""Paired multi-seed study runner and descriptive bootstrap aggregation for FAULTLINE."""

from __future__ import annotations

import hashlib
import random
from typing import Any, Iterable

from faultline.core import POLICIES, POLICY_LABELS, analyze
from faultline.fixtures import SCENARIOS, make_dataset


def _bootstrap_ci95(
    diffs: list[float],
    rng_key: str,
    n_resamples: int = 1000,
) -> list[float]:
    """Deterministic percentile bootstrap 95% interval over seed-level paired differences."""
    n = len(diffs)
    if n == 0:
        return [0.0, 0.0]
    if n == 1:
        val = round(diffs[0], 6)
        return [val, val]

    seed_int = int.from_bytes(hashlib.sha256(rng_key.encode("utf-8")).digest()[:8], "big")
    rng = random.Random(seed_int)
    means: list[float] = []
    for _ in range(n_resamples):
        sample_sum = sum(diffs[rng.randrange(n)] for _ in range(n))
        means.append(sample_sum / n)
    means.sort()
    lo_idx = max(0, min(n_resamples - 1, int(0.025 * n_resamples)))
    hi_idx = max(0, min(n_resamples - 1, int(0.975 * n_resamples)))
    return [round(means[lo_idx], 6), round(means[hi_idx], 6)]


def run_study(
    seeds: Iterable[int],
    cases: int = 64,
    size: int = 3,
    scenario: str = "shared",
) -> dict[str, Any]:
    """Run paired panel-selection experiments across seeds and summarize vs joint selector."""
    if isinstance(seeds, (str, bytes, dict)):
        raise ValueError("'seeds' must be a sequence of 1..64 integers.")
    seed_list = list(seeds)
    if not (1 <= len(seed_list) <= 64):
        raise ValueError(f"Expected 1..64 seeds; got {len(seed_list)}.")
    seen_seeds: set[int] = set()
    for s in seed_list:
        if type(s) is not int:
            raise ValueError(f"Seed must be an integer; got {s!r}.")
        if s in seen_seeds:
            raise ValueError(f"Duplicate seed {s} in study.")
        seen_seeds.add(s)

    if type(cases) is not int or not (16 <= cases <= 256):
        raise ValueError("Cases per condition must be an integer in 16..256.")
    if scenario not in SCENARIOS:
        raise ValueError(f"Unknown scenario '{scenario}'; expected one of {SCENARIOS}.")

    runs: list[dict[str, Any]] = []
    per_policy_runs: dict[str, list[dict[str, Any]]] = {p: [] for p in POLICIES}

    for seed in seed_list:
        dataset = make_dataset(seed=seed, cases=cases, scenario=scenario)
        analysis = analyze(dataset, size=size)
        policy_map: dict[str, dict[str, Any]] = {}
        for pol in analysis["policies"]:
            pid = pol["id"]
            entry = {
                "id": pid,
                "label": pol["label"],
                "panel": pol["panel"],
                "calibration": pol["calibration"],
                "test": pol["test"],
            }
            policy_map[pid] = entry
            per_policy_runs[pid].append(entry)

        runs.append(
            {
                "seed": seed,
                "dataset": analysis["dataset"],
                "policies": policy_map,
            }
        )

    n_seeds = len(seed_list)
    agg_policies: dict[str, dict[str, Any]] = {}
    for pid in POLICIES:
        entries = per_policy_runs[pid]
        agg_policies[pid] = {
            "id": pid,
            "label": POLICY_LABELS[pid],
            "mean_calibration_error": round(
                sum(e["calibration"]["error"] for e in entries) / n_seeds, 6
            ),
            "mean_calibration_worst_group_error": round(
                sum(e["calibration"]["worst_group_error"] for e in entries) / n_seeds, 6
            ),
            "mean_test_error": round(
                sum(e["test"]["error"] for e in entries) / n_seeds, 6
            ),
            "mean_test_worst_group_error": round(
                sum(e["test"]["worst_group_error"] for e in entries) / n_seeds, 6
            ),
            "mean_test_unanimous_wrong_rate": round(
                sum(e["test"]["unanimous_wrong_rate"] for e in entries) / n_seeds, 6
            ),
        }

    paired_vs_joint: dict[str, dict[str, Any]] = {}
    joint_entries = per_policy_runs["joint"]
    for comp_id in ("accuracy", "pairwise", "pooled"):
        comp_entries = per_policy_runs[comp_id]
        # Positive difference = comparator has higher error than joint (i.e. joint reduces error)
        worst_diffs = [
            comp_entries[i]["test"]["worst_group_error"]
            - joint_entries[i]["test"]["worst_group_error"]
            for i in range(n_seeds)
        ]
        pooled_diffs = [
            comp_entries[i]["test"]["error"] - joint_entries[i]["test"]["error"]
            for i in range(n_seeds)
        ]
        joint_wins = sum(1 for d in worst_diffs if d > 1e-9)
        ties = sum(1 for d in worst_diffs if abs(d) <= 1e-9)
        comp_wins = sum(1 for d in worst_diffs if d < -1e-9)

        rng_base = f"faultline-boot|{scenario}|{cases}|{size}|{comp_id}|{seed_list}"
        paired_vs_joint[comp_id] = {
            "comparator": comp_id,
            "label": POLICY_LABELS[comp_id],
            "mean_diff_worst_group_error": round(sum(worst_diffs) / n_seeds, 6),
            "ci95_worst_group_error": _bootstrap_ci95(worst_diffs, rng_base + "|worst"),
            "mean_diff_pooled_error": round(sum(pooled_diffs) / n_seeds, 6),
            "ci95_pooled_error": _bootstrap_ci95(pooled_diffs, rng_base + "|pooled"),
            "joint_wins": joint_wins,
            "ties": ties,
            "comparator_wins": comp_wins,
            "per_seed_diff_worst_group_error": [round(d, 6) for d in worst_diffs],
            "note": "Descriptive percentile bootstrap over seed pairs; not a sequential or conformal guarantee.",
        }

    return {
        "scenario": scenario,
        "cases_per_condition": cases,
        "panel_size": size,
        "seeds": seed_list,
        "n_seeds": n_seeds,
        "runs": runs,
        "aggregate": {
            "policies": agg_policies,
            "paired_vs_joint": paired_vs_joint,
        },
    }
