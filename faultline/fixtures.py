"""Deterministic event-keyed synthetic datasets and exact parity benchmark for FAULTLINE."""

from __future__ import annotations

import hashlib
from typing import Any

from faultline.core import SCHEMA_ID

SCENARIOS: tuple[str, ...] = ("shared", "independent", "shift")

COMPONENTS_SPEC: list[dict[str, str]] = [
    {"id": "c0", "name": "Optic-Alpha", "family": "optical"},
    {"id": "c1", "name": "Optic-Beta", "family": "optical"},
    {"id": "c2", "name": "Optic-Gamma", "family": "optical"},
    {"id": "c3", "name": "Thermal-IR", "family": "thermal"},
    {"id": "c4", "name": "Acoustic-Array", "family": "acoustic"},
    {"id": "c5", "name": "Radar-MMW", "family": "radar"},
    {"id": "c6", "name": "Mag-Flux", "family": "magnetic"},
    {"id": "c7", "name": "Inertial-Gyro", "family": "inertial"},
]

CONDITIONS: tuple[str, ...] = (
    "nominal",
    "glare_surge",
    "multipath_hum",
    "composed_storm",
)


def _event_u01(
    seed: int,
    split: str,
    condition: str,
    case_idx: int,
    channel: str,
) -> float:
    """Deterministic event-keyed uniform draw in [0, 1)."""
    key = f"faultline-v1|{seed}|{split}|{condition}|{case_idx}|{channel}".encode("utf-8")
    digest = hashlib.sha256(key).digest()
    val = int.from_bytes(digest[:8], "big")
    return val / float(1 << 64)


def parity_demo() -> dict[str, Any]:
    """Return the exact 3-bit even/odd parity failure distribution demonstration.

    Both distributions have identical marginal failure rates (1/2) and identical
    pairwise co-failure matrices (1/4 off-diagonal, 1/2 diagonal), yet even-parity
    failures produce 3/4 majority error whereas odd-parity failures produce 1/4
    majority error.
    """
    even_patterns = [
        [0, 0, 0],
        [1, 1, 0],
        [1, 0, 1],
        [0, 1, 1],
    ]
    odd_patterns = [
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1],
        [1, 1, 1],
    ]

    def _summarize(patterns: list[list[int]]) -> dict[str, Any]:
        n = len(patterns)
        marginals = [round(sum(p[i] for p in patterns) / n, 6) for i in range(3)]
        pairwise = [
            [round(sum(1 for p in patterns if p[i] and p[j]) / n, 6) for j in range(3)]
            for i in range(3)
        ]
        maj_err = round(sum(1 for p in patterns if sum(p) >= 2) / n, 6)
        return {
            "marginals": marginals,
            "pairwise": pairwise,
            "majority_error": maj_err,
            "patterns": patterns,
        }

    return {
        "even": _summarize(even_patterns),
        "odd": _summarize(odd_patterns),
    }


def _simulate_row_failures(
    seed: int,
    split: str,
    condition: str,
    case_idx: int,
    scenario: str,
) -> list[int]:
    """Return length-8 binary failure indicator vector (1 = component wrong, 0 = component right)."""
    if scenario == "independent":
        # Negative control 1: strictly independent component errors across all conditions.
        # c0, c1, c2 have the lowest individual error rates in every condition.
        base_rates = [0.05, 0.06, 0.07, 0.14, 0.16, 0.19, 0.21, 0.23]
        cond_mult = 1.35 if condition == "composed_storm" else 1.0
        return [
            1 if _event_u01(seed, split, condition, case_idx, f"indep_{i}") < (base_rates[i] * cond_mult) else 0
            for i in range(8)
        ]

    # Shared-channel model (used for both 'shared' and 'shift', with unseen test common-cause in 'shift')
    fails = [0] * 8
    u_regime = _event_u01(seed, split, condition, case_idx, "regime")

    if condition == "nominal":
        # c0..c2 are error-free in nominal; c3..c7 have single-sensor and mild pair events
        # so c0,c1,c2 have the lowest pooled individual error across the 4 conditions.
        if u_regime < 0.04:
            fails[5] = 1
            fails[6] = 1
        elif u_regime < 0.08:
            fails[5] = 1
            fails[7] = 1
        elif u_regime < 0.12:
            fails[6] = 1
            fails[7] = 1
        elif u_regime < 0.30:
            fails[3] = 1
        elif u_regime < 0.48:
            fails[4] = 1
        elif u_regime < 0.65:
            fails[5] = 1
        elif u_regime < 0.82:
            fails[6] = 1
        elif u_regime < 0.98:
            fails[7] = 1

    elif condition == "glare_surge":
        # Subsets X1..X5 each fail {0, 1, 2} plus at most ONE of {3, 4, 5} and at most ONE of {5, 6, 7}:
        # X1 (0.095): {0, 1, 2, 3, 6}
        # X2 (0.095): {0, 1, 2, 3, 7}
        # X3 (0.095): {0, 1, 2, 4, 6}
        # X4 (0.095): {0, 1, 2, 4, 7}
        # X5 (0.095): {0, 1, 2, 5}
        # Thus (c3,c4,c5) and (c5,c6,c7) have 0 majority errors during glare regimes,
        # while (c0,c1,c2) has ~0.475 majority error.
        if u_regime < 0.095:
            for i in (0, 1, 2, 3, 6):
                fails[i] = 1
        elif u_regime < 0.190:
            for i in (0, 1, 2, 3, 7):
                fails[i] = 1
        elif u_regime < 0.285:
            for i in (0, 1, 2, 4, 6):
                fails[i] = 1
        elif u_regime < 0.380:
            for i in (0, 1, 2, 4, 7):
                fails[i] = 1
        elif u_regime < 0.475:
            for i in (0, 1, 2, 5):
                fails[i] = 1
        elif u_regime < 0.595:
            fails[5] = 1
            fails[6] = 1
        elif u_regime < 0.780:
            fails[3] = 1
        elif u_regime < 0.960:
            fails[4] = 1

    elif condition == "multipath_hum":
        # c0..c2 are error-free in multipath_hum (keeping their 4-condition individual error lowest);
        # (c5,c6,c7) has ~0.12 majority error; c3..c7 have single-sensor noise.
        if u_regime < 0.04:
            fails[5] = 1
            fails[6] = 1
        elif u_regime < 0.08:
            fails[5] = 1
            fails[7] = 1
        elif u_regime < 0.12:
            fails[6] = 1
            fails[7] = 1
        elif u_regime < 0.30:
            fails[3] = 1
        elif u_regime < 0.48:
            fails[4] = 1
        elif u_regime < 0.65:
            fails[5] = 1
        elif u_regime < 0.82:
            fails[6] = 1
        elif u_regime < 0.98:
            fails[7] = 1

    elif condition == "composed_storm":
        # Negative control 2 ('shift'): latent common-cause clock fault on the hardened {c5, c6, c7} triad
        # that never activates in calibration but triggers with probability 0.68 in test on composed_storm.
        if scenario == "shift" and split == "test":
            u_latent = _event_u01(seed, split, condition, case_idx, "latent_clock_fault")
            if u_latent < 0.68:
                fails[5] = 1
                fails[6] = 1
                fails[7] = 1
                return fails

        # Composed storm over {c3, c4, c5, c6, c7} (c0..c2 stay error-free here so their pooled indiv error is ~0.12):
        # - R1 (0.09): {3, 4} fail -> hits pair (3,4)
        # - R2 (0.09): {3, 5} fail -> hits pair (3,5)
        # - R3 (0.09): {4, 5} fail -> hits pair (4,5)
        # - R4 (0.14): {3, 6} fail -> hits pair (3,6)
        # - R5 (0.14): {4, 6} fail -> hits pair (4,6)
        # - R6 (0.14): {3, 7} fail -> hits pair (3,7)
        # - R7 (0.14): {4, 7} fail -> hits pair (4,7)
        # - R8 (0.14): {5, 6, 7} all 3 fail together!
        # Notice:
        # * (c5, c6, c7) fails ONLY on R8 -> true majority error = 0.14 (unique worst-condition minimum!),
        #   but because R8 is a 3-way failure, its pairwise bound is 3 * 0.14 = 0.42!
        # * (c3, c4, c5) fails on R1, R2, R3 -> all 2-way failures!
        #   Its pairwise bound is 0.09 + 0.09 + 0.09 = 0.27 (< 0.42, unique minimum pairwise bound!),
        #   while its true majority error is 0.27 (> 0.14)!
        if u_regime < 0.09:
            for i in (3, 4):
                fails[i] = 1
        elif u_regime < 0.18:
            for i in (3, 5):
                fails[i] = 1
        elif u_regime < 0.27:
            for i in (4, 5):
                fails[i] = 1
        elif u_regime < 0.41:
            for i in (3, 6):
                fails[i] = 1
        elif u_regime < 0.55:
            for i in (4, 6):
                fails[i] = 1
        elif u_regime < 0.69:
            for i in (3, 7):
                fails[i] = 1
        elif u_regime < 0.83:
            for i in (4, 7):
                fails[i] = 1
        elif u_regime < 0.97:
            for i in (5, 6, 7):
                fails[i] = 1

    # Small independent sensor noise (0.5%) keyed per component
    for i in range(8):
        if _event_u01(seed, split, condition, case_idx, f"noise_{i}") < 0.005:
            fails[i] = 1

    return fails


def make_dataset(
    seed: int = 4100,
    cases: int = 64,
    scenario: str = "shared",
) -> dict[str, Any]:
    """Generate a deterministic, event-keyed synthetic dataset in faultline-dataset-v1 format."""
    if type(seed) is not int:
        raise ValueError("Seed must be an integer.")
    if type(cases) is not int or not (16 <= cases <= 256):
        raise ValueError("Cases per condition must be an integer in 16..256.")
    if scenario not in SCENARIOS:
        raise ValueError(f"Unknown scenario '{scenario}'; expected one of {SCENARIOS}.")

    def _build_split(split: str) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for cond in CONDITIONS:
            for idx in range(cases):
                truth = 1 if _event_u01(seed, split, cond, idx, "truth") >= 0.5 else 0
                fails = _simulate_row_failures(seed, split, cond, idx, scenario)
                preds = [1 - truth if f else truth for f in fails]
                rows.append(
                    {
                        "id": f"{split}-{cond}-{idx:03d}",
                        "condition": cond,
                        "truth": truth,
                        "predictions": preds,
                    }
                )
        return rows

    return {
        "schema": SCHEMA_ID,
        "name": f"faultline-{scenario}-seed{seed}-c{cases}",
        "metadata": {
            "seed": seed,
            "cases_per_condition": cases,
            "scenario": scenario,
            "conditions": list(CONDITIONS),
        },
        "components": [dict(c) for c in COMPONENTS_SPEC],
        "calibration": _build_split("calibration"),
        "test": _build_split("test"),
    }
