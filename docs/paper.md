# FAULTLINE: Empirical Joint-Failure Hyperedges vs. Marginal and Pairwise Proxies in Budgeted Panel Selection

**Date:** 24 October 2026  
**Source SHA-256:** `2144abd4c154a5370ab5e353999c737d188eed3a918868dc29ed1ed14a973c79`  
**Schema Version:** `faultline-dataset-v1` / `faultline-receipt-v1`

---

## Abstract

Across 26 reviewed portfolio repositories—spanning neural cellular automata, connectome-routed language models, evolutionary opcode libraries, and multi-agent simulations—a recurring empirical finding is that combining more components frequently fails to improve, or actively degrades, downstream performance when components share failure modes. Standard ensemble selection heuristics either pick the most accurate individual components (`accuracy`), minimize pairwise co-failure bounds (`pairwise`), or minimize average pooled ensemble error (`pooled`). We present **FAULTLINE**, a deterministic CPU-local experimental laboratory that tests a focused falsifiable question: *under equal component-call and calibration budgets, when does selecting a small odd-sized voting panel using complete condition-indexed joint-failure observations (`joint`) reduce held-out worst-condition error compared with `accuracy`, `pairwise`, and `pooled`—and when does it fail?* Across a 24-seed development pilot (`4100..4123`) and a separate frozen 24-seed confirmation suite (`9100..9123`) at panel size $k=3$ and $64$ cases per condition, `joint` reduces held-out worst-condition error under shared/composed faults by $+26.50$ percentage points vs. `accuracy`, $+8.33$ pp vs. `pairwise`, and $+8.66$ pp vs. `pooled` on the confirmation set. At the same time, two mandatory negative controls establish exact boundaries: under conditionally independent errors (`independent`), `joint` confers no gain ($-0.72$ pp vs. `accuracy`), and under an unobserved test common-cause fault (`shift`), `joint` fails severely ($-12.83$ pp vs. `accuracy`, $-33.85$ pp vs. `pairwise`, $-48.18$ pp vs. `pooled`).

---

## 1. Mathematical Formulation

Let $\mathcal{C} = \{1, \dots, m\}$ be a catalog of $m \in [3, 12]$ binary prediction components, and let each labelled case $r$ carry a stress condition $g(r) \in \mathcal{G}$, ground-truth label $y(r) \in \{0, 1\}$, and component prediction vector $\hat{y}(r) \in \{0, 1\}^m$. Define the binary failure indicator of component $i$ on case $r$:
$$E_i(r) = \mathbf{1}[\hat{y}_i(r) \neq y(r)] \in \{0, 1\}.$$
The **empirical failure signature** on case $r$ is the subset $S(r) = \{i \in \mathcal{C} : E_i(r) = 1\}$, forming a hyperedge in the empirical failure hypergraph over $\mathcal{C}$.

For any odd panel $P \subset \mathcal{C}$ of size $k = |P|$ with majority threshold $t = (k+1)/2$, let $W_P(r) = \sum_{i \in P} E_i(r)$ denote the number of wrong panel members on case $r$. The panel's majority vote is wrong if and only if $W_P(r) \ge t$.

### 1.1 Why Pairwise Co-Failure Bounds Misrank Panels

For $k \ge 3$, the event $W_P(r) \ge t$ is equivalent to $\binom{W_P(r)}{2} \ge \binom{t}{2}$. Applying Markov's inequality to the second factorial moment $\binom{W_P}{2} = \sum_{\{i,j\} \subset P} E_i E_j$ within condition $c \in \mathcal{G}$ yields the second-moment upper bound optimized by `pairwise`:
$$\Pr(W_P \ge t \mid c) = \Pr\!\left(\binom{W_P}{2} \ge \binom{t}{2} \,\middle|\, c\right) \le \frac{\sum_{\{i,j\} \subset P} \Pr(E_i = 1 \land E_j = 1 \mid c)}{\binom{t}{2}}.$$

When $k = 3$ ($t = 2$, $\binom{t}{2} = 1$), this pairwise score satisfies the exact identity:
$$\text{PairwiseScore}(P, c) = \sum_{\{i,j\} \subset P} \Pr(E_i = 1 \land E_j = 1 \mid c) = \Pr(W_P = 2 \mid c) + 3\Pr(W_P = 3 \mid c),$$
whereas the true majority-vote error rate is:
$$\text{MajorityError}(P, c) = \Pr(W_P = 2 \mid c) + \Pr(W_P = 3 \mid c).$$

Two structural consequences follow immediately:
1. **The $3\times$ Unanimity Penalty Trap:** A panel $P_A$ with rare unanimous 3-way failures ($\Pr(W=3)=0.14, \Pr(W=2)=0$) has true majority error $0.14$ but pairwise score $3 \times 0.14 = 0.42$. A panel $P_B$ with frequent 2-of-3 pair failures ($\Pr(W=2)=0.27, \Pr(W=3)=0$) has pairwise score $0.27 < 0.42$ yet nearly double the true majority error ($0.27 > 0.14$).
2. **The Exact 3-Bit Even/Odd Parity Unidentifiability:** Let $E^{\text{even}}$ be uniform over $\{(0,0,0), (1,1,0), (1,0,1), (0,1,1)\}$ and $E^{\text{odd}}$ be uniform over $\{(1,0,0), (0,1,0), (0,0,1), (1,1,1)\}$. Both distributions have identical marginal failure rates $(0.5, 0.5, 0.5)$ and identical pairwise co-failure matrices ($0.25$ off-diagonal), yet $\Pr(W \ge 2) = 0.75$ under $E^{\text{even}}$ and $0.25$ under $E^{\text{odd}}$ (verified in `artifacts/parity-demo.json`).

---

## 2. Selector Definitions and Experimental Protocol

All four selectors inspect the exact same calibration split (`calibration`) and enumerate all $\binom{m}{k}$ candidate panels of odd size $k$. Ties are broken deterministically using exact rational arithmetic (`fractions.Fraction`) followed by lexical order of component IDs:

1. **`accuracy`**: minimizes sum of pooled calibration individual error rates $\sum_{i \in P} \hat{e}_i$.
2. **`pairwise`**: minimizes worst-condition calibration second-moment bound, then pooled second-moment bound, then $\sum_{i \in P} \hat{e}_i$.
3. **`pooled`**: minimizes pooled calibration majority error, then worst-condition calibration majority error, then $\sum_{i \in P} \hat{e}_i$.
4. **`joint`**: minimizes worst-condition calibration majority error $\max_{c \in \mathcal{G}} \widehat{\text{Err}}(P \mid c)$, then pooled calibration majority error, then $\sum_{i \in P} \hat{e}_i$.

Held-out `test` rows are never passed to `select_panel` (`test`-label isolation is enforced by signature and verified by unit test). Every run emits a source-bound receipt (`faultline-receipt-v1`) verified by recomputing the entire experiment from scratch (`python -m faultline verify PATH`).

---

## 3. Recorded Empirical Results

Each study evaluates $m=8$ synthetic sensor components across $4$ conditions (`nominal`, `glare_surge`, `multipath_hum`, `composed_storm`) with $64$ calibration cases and $64$ fresh test cases per condition ($256$ calibration rows and $256$ test rows per seed; panel size $k=3$).

### 3.1 Development Pilot (`seeds = 4100..4123`, $N = 24$ paired seeds)

| Scenario | Receipt Payload SHA-256 | `accuracy` Worst-Cond | `pairwise` Worst-Cond | `pooled` Worst-Cond | `joint` Worst-Cond |
|---|---|---:|---:|---:|---:|
| `shared` | `048e2c56f5391a53...` | 48.31% (`0.483073`) | 31.12% (`0.311198`) | 29.23% (`0.292318`) | **19.60%** (`0.195964`) |
| `independent` | `21c711f09a6b56ff...` | **2.93%** (`0.029297`) | 3.71% (`0.037109`) | 3.65% (`0.036458`) | 3.65% (`0.036458`) |
| `shift` | `349361e37d590e90...` | 48.31% (`0.483073`) | 28.58% (`0.285807`) | **14.06%** (`0.140625`) | 64.65% (`0.646484`) |

**Pilot Paired Differences vs. `joint` ($\text{Err}_{\text{comp}} - \text{Err}_{\text{joint}}$, Worst-Condition Test Error):**
- **`shared`:**
  - `accuracy − joint`: **$+28.71\text{ pp}$** (`+0.287109`), 95% bootstrap `[+0.250651, +0.320312]`, `joint` wins 24 / 0 ties / 0 losses.
  - `pairwise − joint`: **$+11.52\text{ pp}$** (`+0.115234`), 95% bootstrap `[+0.083984, +0.147135]`, `joint` wins 19 / 5 ties / 0 losses.
  - `pooled − joint`: **$+9.64\text{ pp}$** (`+0.096354`), 95% bootstrap `[+0.066406, +0.124349]`, `joint` wins 19 / 4 ties / 1 loss.
- **`independent` (Negative Control 1):**
  - `accuracy − joint`: **$-0.72\text{ pp}$** (`-0.007161`), 95% bootstrap `[-0.016276, +0.001302]`, `joint` wins 3 / 14 ties / 7 losses.
- **`shift` (Negative Control 2 — Unseen Test Common Cause):**
  - `accuracy − joint`: **$-16.34\text{ pp}$** (`-0.163411`), 95% bootstrap `[-0.244792, -0.070964]`, `joint` wins 3 / 0 ties / 21 losses.
  - `pairwise − joint`: **$-36.07\text{ pp}$** (`-0.360677`), 95% bootstrap `[-0.452474, -0.249349]`, `joint` wins 0 / 7 ties / 17 losses.
  - `pooled − joint`: **$-50.59\text{ pp}$** (`-0.505859`), 95% bootstrap `[-0.584635, -0.413411]`, `joint` wins 0 / 3 ties / 21 losses.

---

### 3.2 Frozen Confirmation Suite (`seeds = 9100..9123`, $N = 24$ paired seeds)

Evaluated once after source freeze (`source_sha256 = 2144abd4c154a5370ab5e353999c737d188eed3a918868dc29ed1ed14a973c79`).

| Scenario | Receipt Payload SHA-256 | `accuracy` Worst-Cond | `pairwise` Worst-Cond | `pooled` Worst-Cond | `joint` Worst-Cond |
|---|---|---:|---:|---:|---:|
| `shared` | `fe083c561e21d89a...` | 47.79% (`0.477865`) | 29.62% (`0.296224`) | 29.95% (`0.299479`) | **21.29%** (`0.212891`) |
| `independent` | `10eb3e843b3a5b31...` | **2.80%** (`0.027995`) | 3.39% (`0.033854`) | 3.52% (`0.035156`) | 3.52% (`0.035156`) |
| `shift` | `8a81909f72fdb4e6...` | 47.79% (`0.477865`) | 26.76% (`0.267578`) | **12.43%** (`0.124349`) | 60.61% (`0.606120`) |

**Confirmation Paired Differences vs. `joint` ($\text{Err}_{\text{comp}} - \text{Err}_{\text{joint}}$, Worst-Condition Test Error):**
- **`shared`:**
  - `accuracy − joint`: **$+26.50\text{ pp}$** (`+0.264974`), 95% bootstrap `[+0.235677, +0.296224]`, `joint` wins 24 / 0 ties / 0 losses.
  - `pairwise − joint`: **$+8.33\text{ pp}$** (`+0.083333`), 95% bootstrap `[+0.049479, +0.118490]`, `joint` wins 17 / 6 ties / 1 loss.
  - `pooled − joint`: **$+8.66\text{ pp}$** (`+0.086589`), 95% bootstrap `[+0.052083, +0.121094]`, `joint` wins 18 / 4 ties / 2 losses.
- **`independent` (Negative Control 1):**
  - `accuracy − joint`: **$-0.72\text{ pp}$** (`-0.007161`), 95% bootstrap `[-0.013672, -0.001953]`, `joint` wins 1 / 16 ties / 7 losses.
- **`shift` (Negative Control 2 — Unseen Test Common Cause):**
  - `accuracy − joint`: **$-12.83\text{ pp}$** (`-0.128255`), 95% bootstrap `[-0.214844, -0.029297]`, `joint` wins 6 / 0 ties / 18 losses.
  - `pairwise − joint`: **$-33.85\text{ pp}$** (`-0.338542`), 95% bootstrap `[-0.466797, -0.209635]`, `joint` wins 2 / 7 ties / 15 losses.
  - `pooled − joint`: **$-48.18\text{ pp}$** (`-0.481771`), 95% bootstrap `[-0.577474, -0.375651]`, `joint` wins 0 / 3 ties / 21 losses.

---

## 4. Limitations and Explicit Boundaries

1. **Synthetic Binary Predictions vs. Real-World Deployment:** The built-in fixtures simulate event-keyed binary sensor specialists with explicit shared-channel and higher-order fault regimes. They do not prove LLM reasoning diversity, biological cognition, or safety-critical hardware reliability.
2. **Observational Hyperedges Are Not Causal Graphs:** Empirical failure signatures identify which components failed on the same calibration cases; they do not identify physical root causes without interventional stress design.
3. **Unobserved Common Causes Cannot Be Eliminated by Calibration Selection:** As demonstrated quantitatively by the `shift` scenario, if a latent common-cause channel never activates during calibration, `joint` cannot foresee it and can concentrate risk onto that latent channel.
4. **Descriptive Bootstrap Intervals:** Reported 95% intervals are percentile bootstraps over seed pairs for descriptive uncertainty; they are not sequential anytime-valid e-processes or conformal risk certificates.
5. **Bounded Combinatorial Scope:** Exhaustive subset enumeration is intentionally capped at $m \le 12$ components and $N \le 12{,}000$ rows to keep every run fast, exact, and inspectable on a standard CPU without external dependencies.
