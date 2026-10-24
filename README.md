# FAULTLINE: Joint-Failure Ensemble Selection Laboratory

**FAULTLINE** is a zero-dependency, CPU-local Python 3.12 research laboratory and browser instrument for studying **correlated and higher-order failures in small voting ensembles**.

Across 26 reviewed portfolio repositories (see [Portfolio & Research Review](docs/portfolio-and-research-review.md), [`research/review-models.md`](research/review-models.md), [`research/review-labs.md`](research/review-labs.md), and [`research/review-tools.md`](research/review-tools.md)), a recurring empirical finding is that adding more models, memories, or specialist modules often fails to add independent capability because components fail together on shared stress conditions.

FAULTLINE isolates and tests this prerequisite directly:

> **Research Question:** *Under equal component-call and calibration budgets, when does selecting an odd-sized voting panel using complete condition-indexed joint-failure observations (`joint`) reduce held-out worst-condition error compared with individual accuracy (`accuracy`), pairwise co-failure bounds (`pairwise`), or pooled ensemble error (`pooled`)—and when does it fail under unobserved common causes?*

---

## Quickstart

Requires only **Python 3.12+** (standard library only; no runtime network calls, external packages, or model downloads).

### 1. Run the Automated Test Suite
```powershell
python -m unittest discover -s tests -v
```

### 2. Launch the Interactive Browser Laboratory
```powershell
python -m faultline serve --port 8786
# Or on Windows PowerShell (launches server and opens http://127.0.0.1:8786/):
.\Run-FAULTLINE.ps1
```

### 3. CLI Commands & Deterministic Receipt Replay
```powershell
# Single-seed analysis receipt
python -m faultline demo --seed 4100 --cases 64 --scenario shared --size 3 --out artifacts/demo-4100.json

# Paired multi-seed study receipt
python -m faultline study --seed 4100 --replicates 24 --cases 64 --scenario shared --size 3 --out artifacts/pilot-shared-4100.json

# Exact 3-bit even/odd parity algebraic proof receipt
python -m faultline parity --out artifacts/parity-demo.json

# Analyze an external faultline-dataset-v1 JSON file
python -m faultline analyze path/to/dataset.json --size 3 --out artifacts/custom-analysis.json

# Verify and deterministically replay any receipt (rejects hash tampering, source drift, and rehashed fabrications)
python -m faultline verify artifacts/confirm-shared-9100.json
```

---

## The Four Deterministic Selectors

Every selector inspects the **exact same calibration rows** (`calibration`) and enumerates all $\binom{m}{k}$ odd-sized candidate panels of size $k$. Ties are broken deterministically via exact rational arithmetic (`fractions.Fraction`) followed by lexical component ID order:

1. **`accuracy` (Individual Accuracy / Marginal):** Minimizes the sum of pooled individual error rates $\sum_{i \in P} \hat{e}_i$.
2. **`pairwise` (Pairwise Co-Failure Bound):** Minimizes the worst-condition second factorial-moment upper bound on majority error:
   $$\text{PairwiseBound}(P, c) = \frac{\sum_{\{i,j\} \subset P} \widehat{\text{cofail}}(i, j \mid c)}{\binom{t}{2}}, \quad t = \frac{k+1}{2},$$
   then the pooled pairwise bound, then $\sum_{i \in P} \hat{e}_i$.
3. **`pooled` (Pooled Majority Error):** Minimizes average majority-vote error across all calibration rows combined, then worst-condition majority error.
4. **`joint` (Joint Worst-Condition Majority Error):** Minimizes worst-condition observed majority-vote error $\max_{c} \widehat{\text{Err}}(P \mid c)$ directly from empirical failure hyperedges, then pooled majority error.

### Why Pairwise Co-Failure Fails on Higher-Order Faults ($k=3$)

For a 3-component panel $P$, let $W \in \{0,1,2,3\}$ be the number of wrong panel members on a case. The sum of pair co-failure rates satisfies:
$$\sum_{\{i,j\} \subset P} \Pr(E_i = 1 \land E_j = 1 \mid c) = \Pr(W = 2 \mid c) + 3\Pr(W = 3 \mid c),$$
whereas actual majority-vote error is $\Pr(W \ge 2 \mid c) = \Pr(W = 2 \mid c) + \Pr(W = 3 \mid c)$. Because unanimous 3-way failures count **$3\times$** in the pairwise sum, `pairwise` rejects panels with rare 3-way faults in favor of panels with frequent 2-of-3 faults.

In the extreme **3-bit even/odd parity control** (`/api/parity`, `artifacts/parity-demo.json`), both distributions have identical marginal failure rates `[0.5, 0.5, 0.5]` and identical pairwise co-failure rates `0.25`, yet majority error is **75.00%** (`3/4`) under even parity and **25.00%** (`1/4`) under odd parity.

---

## Recorded Experimental Evidence

Full analysis and mathematical derivations are in [`docs/paper.md`](docs/paper.md). All recorded receipts are stored in [`artifacts/`](artifacts/) and verified against `source_sha256 = 2144abd4c154a5370ab5e353999c737d188eed3a918868dc29ed1ed14a973c79`.

### Frozen Confirmation Suite (`seeds = 9100..9123`, $N=24$ seeds, $k=3$, $64$ cases/condition)

| Scenario | Purpose | `accuracy` Worst-Cond | `pairwise` Worst-Cond | `pooled` Worst-Cond | `joint` Worst-Cond | Mean $\Delta$ (`accuracy − joint`) | Mean $\Delta$ (`pairwise − joint`) | Mean $\Delta$ (`pooled − joint`) | Receipt |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| **`shared`** | Shared-channel & composed higher-order faults | 47.79% | 29.62% | 29.95% | **21.29%** | **+26.50 pp** `[+23.57, +29.62]` | **+8.33 pp** `[+4.95, +11.85]` | **+8.66 pp** `[+5.21, +12.11]` | [`confirm-shared-9100.json`](artifacts/confirm-shared-9100.json) |
| **`independent`** | Negative control 1: independent errors | **2.80%** | 3.39% | 3.52% | 3.52% | **−0.72 pp** `[−1.37, −0.20]` | **−0.13 pp** `[−0.33, +0.00]` | **0.00 pp** `[0.00, 0.00]` | [`confirm-independent-9100.json`](artifacts/confirm-independent-9100.json) |
| **`shift`** | Negative control 2: unseen test common cause | 47.79% | 26.76% | **12.43%** | 60.61% | **−12.83 pp** `[−21.48, −2.93]` | **−33.85 pp** `[−46.68, −20.96]` | **−48.18 pp** `[−57.75, −37.57]` | [`confirm-shift-9100.json`](artifacts/confirm-shift-9100.json) |

*(Positive $\Delta = \text{Err}_{\text{comparator}} - \text{Err}_{\text{joint}}$ means `joint` achieved lower held-out worst-condition error; negative $\Delta$ means `joint` had higher error.)*

---

## Dataset Schema (`faultline-dataset-v1`)

Imported datasets via CLI (`python -m faultline analyze PATH`) or HTTP (`POST /api/analyze`) are strictly validated:
- `schema`: must be `"faultline-dataset-v1"`
- `name`: non-empty string
- `components`: list of `3..12` objects `{id, name, family}` with unique IDs
- `calibration` and `test`: non-empty lists of `{id, condition, truth, predictions}` with globally disjoint case IDs across both splits, integer bits `0` or `1` (`bool` is rejected), and at most `12,000` total rows.

---

## Repository Structure

- [`faultline/core.py`](faultline/core.py) — Schema validation, exact rational selector keys, failure-signature hyperedges, and evaluation metrics.
- [`faultline/fixtures.py`](faultline/fixtures.py) — Event-keyed (`SHA-256`) synthetic sensor specialists (`shared`, `independent`, `shift`) and exact 3-bit parity benchmark.
- [`faultline/study.py`](faultline/study.py) — Paired multi-seed study runner and descriptive percentile bootstrap intervals.
- [`faultline/receipts.py`](faultline/receipts.py) — Source-bound SHA-256 receipts (`faultline-receipt-v1`) and deterministic replay verifier.
- [`faultline/server.py`](faultline/server.py) & [`web/`](web/) — Loopback HTTP API and responsive browser laboratory.
- [`docs/design.md`](docs/design.md) & [`docs/paper.md`](docs/paper.md) — Architecture specification and full empirical report.
- [`docs/portfolio-and-research-review.md`](docs/portfolio-and-research-review.md) & [`research/`](research/) — Live reviews of all 26 linked repositories.

---

## Boundaries and Limitations

- **Synthetic vs. Real-World Scope:** Synthetic binary sensor fixtures demonstrate the mathematical and statistical properties of ensemble selection rules under controlled dependence; they do not establish LLM reasoning quality, biological cognition, or safety-critical certification.
- **Unobserved Common Causes:** Empirical joint-failure selection only protects against fault modes represented in calibration (`shared`); when a dormant common-cause fault activates only in test (`shift`), `joint` fails as shown in Negative Control 2.
- **Descriptive Uncertainty:** Bootstrap intervals summarize seed-pair variability and are not sequential anytime-valid e-processes or conformal guarantees.
