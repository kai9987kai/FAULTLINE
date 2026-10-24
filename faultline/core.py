"""Deterministic core for FAULTLINE joint-failure panel selection and evaluation."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
import itertools
import math
from typing import Any

SCHEMA_ID = "faultline-dataset-v1"
MIN_COMPONENTS = 3
MAX_COMPONENTS = 12
MAX_TOTAL_ROWS = 12000

POLICIES: tuple[str, ...] = ("accuracy", "pairwise", "pooled", "joint")
POLICY_LABELS: dict[str, str] = {
    "accuracy": "Individual Accuracy (Marginal)",
    "pairwise": "Pairwise Co-Failure Bound (2nd Moment)",
    "pooled": "Pooled Majority Error (Average)",
    "joint": "Joint Worst-Condition Majority Error",
}


def _is_bit(val: Any) -> bool:
    return type(val) is int and val in (0, 1)


def _validate_rows(
    rows: Any,
    split_name: str,
    n_components: int,
    seen_ids: set[str],
) -> None:
    if not isinstance(rows, list) or len(rows) == 0:
        raise ValueError(f"'{split_name}' must be a non-empty list of rows.")
    for idx, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"Row {idx} in '{split_name}' must be an object.")
        row_id = row.get("id")
        if not isinstance(row_id, str) or not row_id.strip():
            raise ValueError(f"Row {idx} in '{split_name}' has missing or empty 'id'.")
        if row_id in seen_ids:
            raise ValueError(f"Duplicate or overlapping case id '{row_id}'.")
        seen_ids.add(row_id)

        condition = row.get("condition")
        if not isinstance(condition, str) or not condition.strip():
            raise ValueError(f"Row '{row_id}' in '{split_name}' has invalid 'condition'.")

        truth = row.get("truth")
        if not _is_bit(truth):
            raise ValueError(
                f"Row '{row_id}' in '{split_name}' has invalid 'truth' (must be int 0 or 1, not bool)."
            )

        preds = row.get("predictions")
        if not isinstance(preds, list) or len(preds) != n_components:
            raise ValueError(
                f"Row '{row_id}' in '{split_name}' has ragged or invalid 'predictions' "
                f"(expected length {n_components})."
            )
        for c_idx, p in enumerate(preds):
            if not _is_bit(p):
                raise ValueError(
                    f"Row '{row_id}' in '{split_name}' prediction[{c_idx}] must be int 0 or 1."
                )


def validate_dataset(data: dict[str, Any]) -> dict[str, Any]:
    """Validate dataset against faultline-dataset-v1 schema and return it."""
    if not isinstance(data, dict):
        raise ValueError("Dataset must be a JSON object.")
    if data.get("schema") != SCHEMA_ID:
        raise ValueError(f"Unknown or missing schema '{data.get('schema')}'; expected '{SCHEMA_ID}'.")

    name = data.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Dataset 'name' must be a non-empty string.")

    components = data.get("components")
    if not isinstance(components, list) or not (MIN_COMPONENTS <= len(components) <= MAX_COMPONENTS):
        raise ValueError(
            f"Dataset 'components' must be a list of {MIN_COMPONENTS}..{MAX_COMPONENTS} items."
        )

    comp_ids: set[str] = set()
    for idx, comp in enumerate(components):
        if not isinstance(comp, dict):
            raise ValueError(f"Component {idx} must be an object.")
        for key in ("id", "name", "family"):
            val = comp.get(key)
            if not isinstance(val, str) or not val.strip():
                raise ValueError(f"Component {idx} has missing or empty '{key}'.")
        cid = comp["id"]
        if cid in comp_ids:
            raise ValueError(f"Duplicate component id '{cid}'.")
        comp_ids.add(cid)

    calibration = data.get("calibration")
    test = data.get("test")
    if not isinstance(calibration, list) or not isinstance(test, list):
        raise ValueError("'calibration' and 'test' must be lists.")
    if len(calibration) + len(test) > MAX_TOTAL_ROWS:
        raise ValueError(f"Total rows exceed maximum of {MAX_TOTAL_ROWS}.")

    seen_ids: set[str] = set()
    _validate_rows(calibration, "calibration", len(components), seen_ids)
    _validate_rows(test, "test", len(components), seen_ids)
    return data


def _validate_panel_size(size: Any, n_components: int) -> int:
    if type(size) is not int or size < 1 or size > n_components or size % 2 == 0:
        raise ValueError(
            f"Panel size must be an odd integer between 1 and {n_components}; got {size!r}."
        )
    return size


def select_panel(
    components: list[dict[str, Any]],
    calibration: list[dict[str, Any]],
    size: int,
    policy: str,
) -> tuple[int, ...]:
    """Deterministically select a component index panel using calibration rows only."""
    if not isinstance(components, list) or not (MIN_COMPONENTS <= len(components) <= MAX_COMPONENTS):
        raise ValueError(f"Expected {MIN_COMPONENTS}..{MAX_COMPONENTS} components.")
    comp_ids: set[str] = set()
    for idx, comp in enumerate(components):
        if not isinstance(comp, dict) or not isinstance(comp.get("id"), str) or not comp["id"].strip():
            raise ValueError(f"Invalid component at index {idx}.")
        if comp["id"] in comp_ids:
            raise ValueError(f"Duplicate component id '{comp['id']}'.")
        comp_ids.add(comp["id"])

    seen_ids: set[str] = set()
    _validate_rows(calibration, "calibration", len(components), seen_ids)
    _validate_panel_size(size, len(components))
    if policy not in POLICIES:
        raise ValueError(f"Unknown policy '{policy}'; expected one of {POLICIES}.")

    n_comp = len(components)
    n_cal = len(calibration)
    threshold = (size + 1) // 2
    pair_denom = math.comb(threshold, 2) if size >= 3 else 1

    # Precompute failure indicators per row and group row indices by condition
    row_failures: list[tuple[int, ...]] = []
    condition_order: list[str] = []
    condition_rows: dict[str, list[int]] = {}
    for r_idx, row in enumerate(calibration):
        truth = row["truth"]
        preds = row["predictions"]
        fail_vec = tuple(1 if preds[i] != truth else 0 for i in range(n_comp))
        row_failures.append(fail_vec)
        cond = row["condition"]
        if cond not in condition_rows:
            condition_order.append(cond)
            condition_rows[cond] = []
        condition_rows[cond].append(r_idx)

    # Pooled individual error rates as exact Fractions
    indiv_err = [
        Fraction(sum(row_failures[r][i] for r in range(n_cal)), n_cal)
        for i in range(n_comp)
    ]

    # Condition-specific and pooled pairwise co-failure rates (and individual rates for k=1)
    cond_indiv_err: dict[str, list[Fraction]] = {}
    cond_pair_err: dict[str, dict[tuple[int, int], Fraction]] = {}
    for cond in condition_order:
        r_indices = condition_rows[cond]
        c_len = len(r_indices)
        cond_indiv_err[cond] = [
            Fraction(sum(row_failures[r][i] for r in r_indices), c_len)
            for i in range(n_comp)
        ]
        pair_map: dict[tuple[int, int], Fraction] = {}
        for u, v in itertools.combinations(range(n_comp), 2):
            cofail_count = sum(1 for r in r_indices if row_failures[r][u] and row_failures[r][v])
            pair_map[(u, v)] = Fraction(cofail_count, c_len)
        cond_pair_err[cond] = pair_map

    pooled_pair_err: dict[tuple[int, int], Fraction] = {}
    for u, v in itertools.combinations(range(n_comp), 2):
        cofail_count = sum(1 for r in range(n_cal) if row_failures[r][u] and row_failures[r][v])
        pooled_pair_err[(u, v)] = Fraction(cofail_count, n_cal)

    best_panel: tuple[int, ...] | None = None
    best_key: tuple[Any, ...] | None = None

    for panel in itertools.combinations(range(n_comp), size):
        lexical_ids = tuple(components[i]["id"] for i in panel)
        indiv_sum = sum((indiv_err[i] for i in panel), Fraction(0, 1))

        if policy == "accuracy":
            key: tuple[Any, ...] = (indiv_sum, lexical_ids)
        elif policy == "pairwise":
            if size == 1:
                idx0 = panel[0]
                worst_pair_bound = max(cond_indiv_err[c][idx0] for c in condition_order)
                pooled_pair_bound = indiv_err[idx0]
            else:
                panel_pairs = list(itertools.combinations(panel, 2))
                worst_pair_bound = max(
                    sum((cond_pair_err[c][pair] for pair in panel_pairs), Fraction(0, 1))
                    / pair_denom
                    for c in condition_order
                )
                pooled_pair_bound = (
                    sum((pooled_pair_err[pair] for pair in panel_pairs), Fraction(0, 1))
                    / pair_denom
                )
            key = (worst_pair_bound, pooled_pair_bound, indiv_sum, lexical_ids)
        else:
            # Compute exact pooled and worst-condition majority error for this panel
            pooled_maj_fails = 0
            worst_cond_maj = Fraction(0, 1)
            for cond in condition_order:
                r_indices = condition_rows[cond]
                c_fails = 0
                for r in r_indices:
                    rf = row_failures[r]
                    if sum(rf[i] for i in panel) >= threshold:
                        c_fails += 1
                pooled_maj_fails += c_fails
                c_rate = Fraction(c_fails, len(r_indices))
                if c_rate > worst_cond_maj:
                    worst_cond_maj = c_rate
            pooled_maj = Fraction(pooled_maj_fails, n_cal)
            if policy == "pooled":
                key = (pooled_maj, worst_cond_maj, indiv_sum, lexical_ids)
            else:  # policy == "joint"
                key = (worst_cond_maj, pooled_maj, indiv_sum, lexical_ids)

        if best_key is None or key < best_key:
            best_key = key
            best_panel = panel

    assert best_panel is not None
    return best_panel


def metrics(rows: list[dict[str, Any]], panel: tuple[int, ...] | list[int]) -> dict[str, Any]:
    """Compute majority-vote metrics for a panel of component indices across rows."""
    if not isinstance(rows, list) or len(rows) == 0:
        raise ValueError("'rows' must be a non-empty list.")
    panel_tuple = tuple(panel)
    if len(panel_tuple) == 0 or len(panel_tuple) % 2 == 0:
        raise ValueError("Panel must have an odd positive number of component indices.")
    if len(set(panel_tuple)) != len(panel_tuple):
        raise ValueError("Panel must not contain duplicate component indices.")

    first_preds = rows[0].get("predictions") if isinstance(rows[0], dict) else None
    n_comp = len(first_preds) if isinstance(first_preds, list) else 0
    for idx in panel_tuple:
        if type(idx) is not int or idx < 0 or idx >= n_comp:
            raise ValueError(f"Panel index {idx!r} is out of bounds for {n_comp} components.")

    k = len(panel_tuple)
    threshold = (k + 1) // 2
    n_total = len(rows)
    maj_errors = 0
    unanimous_errors = 0

    condition_order: list[str] = []
    cond_counts: dict[str, int] = {}
    cond_errors: dict[str, int] = {}

    for row in rows:
        truth = row["truth"]
        preds = row["predictions"]
        cond = row["condition"]
        if cond not in cond_counts:
            condition_order.append(cond)
            cond_counts[cond] = 0
            cond_errors[cond] = 0
        cond_counts[cond] += 1

        wrong_count = sum(1 for i in panel_tuple if preds[i] != truth)
        if wrong_count >= threshold:
            maj_errors += 1
            cond_errors[cond] += 1
        if wrong_count == k:
            unanimous_errors += 1

    groups = []
    worst_group_error = 0.0
    for cond in condition_order:
        c_n = cond_counts[cond]
        c_err = cond_errors[cond] / c_n
        if c_err > worst_group_error:
            worst_group_error = c_err
        groups.append(
            {
                "condition": cond,
                "n": c_n,
                "error": round(c_err, 6),
            }
        )

    return {
        "n": n_total,
        "error": round(maj_errors / n_total, 6),
        "worst_group_error": round(worst_group_error, 6),
        "unanimous_wrong_rate": round(unanimous_errors / n_total, 6),
        "groups": groups,
    }


def _collect_witnesses(
    rows: list[dict[str, Any]],
    components: list[dict[str, Any]],
    panel: tuple[int, ...],
    limit: int = 8,
) -> list[dict[str, Any]]:
    k = len(panel)
    threshold = (k + 1) // 2
    witnesses: list[dict[str, Any]] = []
    for row in rows:
        truth = row["truth"]
        preds = row["predictions"]
        wrong_ids = [components[i]["id"] for i in panel if preds[i] != truth]
        if len(wrong_ids) >= threshold:
            ones = sum(preds[i] for i in panel)
            vote = 1 if ones >= threshold else 0
            witnesses.append(
                {
                    "id": row["id"],
                    "condition": row["condition"],
                    "truth": truth,
                    "vote": vote,
                    "wrong_components": wrong_ids,
                }
            )
            if len(witnesses) >= limit:
                break
    return witnesses


def _compute_cofailure(
    components: list[dict[str, Any]],
    calibration: list[dict[str, Any]],
) -> dict[str, Any]:
    n_comp = len(components)
    n_cal = len(calibration)
    matrix_counts = [[0 for _ in range(n_comp)] for _ in range(n_comp)]
    sig_counter: Counter[tuple[str, ...]] = Counter()

    for row in calibration:
        truth = row["truth"]
        preds = row["predictions"]
        wrong_idx = [i for i in range(n_comp) if preds[i] != truth]
        for u in wrong_idx:
            for v in wrong_idx:
                matrix_counts[u][v] += 1
        if wrong_idx:
            sig = tuple(components[i]["id"] for i in wrong_idx)
            sig_counter[sig] += 1

    matrix = [
        [round(matrix_counts[u][v] / n_cal, 6) for v in range(n_comp)]
        for u in range(n_comp)
    ]

    signatures = [
        {
            "members": list(sig),
            "count": count,
            "rate": round(count / n_cal, 6),
        }
        for sig, count in sorted(
            sig_counter.items(),
            key=lambda item: (-item[1], -len(item[0]), item[0]),
        )
    ]

    return {
        "matrix": matrix,
        "signatures": signatures,
    }


def analyze(data: dict[str, Any], size: int = 3) -> dict[str, Any]:
    """Validate dataset, run all four selectors on calibration, and evaluate on frozen test rows."""
    validate_dataset(data)
    components = data["components"]
    calibration = data["calibration"]
    test = data["test"]
    n_comp = len(components)
    _validate_panel_size(size, n_comp)

    n_cal = len(calibration)
    n_test = len(test)
    n_candidates = math.comb(n_comp, size)

    policies_out: list[dict[str, Any]] = []
    for policy_id in POLICIES:
        panel_idx = select_panel(components, calibration, size, policy_id)
        panel_ids = [components[i]["id"] for i in panel_idx]
        policies_out.append(
            {
                "id": policy_id,
                "label": POLICY_LABELS[policy_id],
                "panel": panel_ids,
                "calibration": metrics(calibration, panel_idx),
                "test": metrics(test, panel_idx),
                "witnesses": _collect_witnesses(test, components, panel_idx, limit=8),
            }
        )

    return {
        "dataset": data["name"],
        "components": copy.deepcopy(components) if "copy" in globals() else [dict(c) for c in components],
        "n_calibration": n_cal,
        "n_test": n_test,
        "panel_size": size,
        "candidate_panels": n_candidates,
        "policies": policies_out,
        "cofailure": _compute_cofailure(components, calibration),
        "costs": {
            "calibration_component_calls": n_cal * n_comp,
            "deployment_calls_per_case": size,
            "test_deployment_calls_per_policy": n_test * size,
            "full_component_test_calls": n_test * n_comp,
            "candidate_panels": n_candidates,
            "search_panel_row_evaluations": n_candidates * n_cal,
        },
    }
