# FAULTLINE: Empirical Joint-Failure Hyperedges vs. Marginal and Pairwise Proxies in Budgeted Ensemble Selection

**Authors:** FAULTLINE Research Laboratory  
**Date:** 24 October 2026  
**Repository:** [https://github.com/kai9987kai/FAULTLINE](https://github.com/kai9987kai/FAULTLINE)  
**Verified Computation Source SHA-256:** `2144abd4c154a5370ab5e353999c737d188eed3a918868dc29ed1ed14a973c79`  
**Artifact Schemas:** `faultline-dataset-v1` / `faultline-receipt-v1`

---

## Abstract

A recurring empirical observation across multi-version software systems, sensor fusion networks, and machine-learning ensembles is that combining more components frequently fails to improveâ€”or actively degradesâ€”worst-case reliability when components fail together under shared stress conditions. Across a live architectural review of 26 software and research repositories spanning cellular automata, connectome-grafted language models, evolutionary program synthesis, and multi-agent controllers, we observe the same structural bottleneck: added modules or specialists repeatedly underperform simpler subsets when their errors are correlated on difficult inputs. Standard ensemble selection criteria rely on marginal individual accuracy (`accuracy`), second-moment pairwise co-failure bounds (`pairwise`), or average pooled majority error (`pooled`).

In this paper, we introduce **FAULTLINE**, a zero-dependency, deterministic experimental instrument that isolates and tests a single falsifiable question: *under equal component-call and calibration budgets, when does selecting an odd-sized voting panel using complete condition-indexed joint-failure observations (`joint`) reduce held-out worst-condition error compared with `accuracy`, `pairwise`, and `pooled`â€”and when does it fail?* We prove algebraically that for a 3-component majority vote, the second factorial-moment pairwise bound weights unanimous 3-way failures $3\times$ as heavily as 2-of-3 failures ($\Pr(W=2) + 3\Pr(W=3)$ vs. $\Pr(W=2) + \Pr(W=3)$), creating a persistent approximation bias that does not vanish with infinite calibration data. Across a 24-seed development pilot (`seeds = 4100..4123`) and a preregistered source-frozen 24-seed confirmation suite (`seeds = 9100..9123`) at panel size $k=3$ and $64$ cases per condition, `joint` reduces held-out worst-condition error under shared and higher-order faults (`shared`) to **21.29%**, outperforming `accuracy` (**47.79%**, $\Delta = +26.50\text{ pp}$), `pairwise` (**29.62%**, $\Delta = +8.33\text{ pp}$), and `pooled` (**29.95%**, $\Delta = +8.66\text{ pp}$). Simultaneously, two negative-control regimes establish exact validity boundaries: when component errors are conditionally independent (`independent`), `joint` provides no benefit ($\Delta = -0.72\text{ pp}$ vs. `accuracy`), and when an unobserved common-cause fault activates only at test time (`shift`), `joint` degrades sharply (**60.61%** worst-condition error; $\Delta = -12.83\text{ pp}$ vs. `accuracy` and $-33.85\text{ pp}$ vs. `pairwise`). Finally, a panel-size ablation ($k \in \{1, 3, 5, 7\}$) demonstrates that expanding the panel to $k=7$ degrades worst-condition error from **21.29%** ($k=3$) to **38.54%** ($k=7$) by forcing the inclusion of shared-channel components.

---

## 1. Introduction & Portfolio Motivation

The classical justification for voting ensembles rests on Condorcet's jury theorem: if $k$ binary predictors make independent errors with probability $p < 1/2$, majority-vote error decreases monotonically with $k$. In engineered systems, however, errors are rarely independent. Knight and Leveson (1986) famously refuted the independence assumption in $N$-version programming by showing that independently implemented programs fail on the same difficult corner cases. Eckhardt and Lee (1985) provided the theoretical mechanism: even if components fail independently conditional on a specific input $x$, variation in difficulty $\theta(x)$ across conditions induces positive error correlation when integrated over a condition distribution, and shared architectural channels induce correlation even conditional on $x$.

### 1.1 Synthesis of 26 Portfolio Repositories

Before designing FAULTLINE, we conducted a live source-and-documentation review of 26 linked repositories (documented in full in [`docs/portfolio-and-research-review.md`](portfolio-and-research-review.md), [`research/review-models.md`](../research/review-models.md), [`research/review-labs.md`](../research/review-labs.md), and [`research/review-tools.md`](../research/review-tools.md)). Five empirical findings across those systems directly motivated our experimental design:

1. **More Components Can Lose to One Simple Controller:** In [`FLY-DIAMOND-NEXUS`](https://github.com/kai9987kai/FLY-DIAMOND-NEXUS), a single Antennal Lobe controller outperformed a 16-module coupled neural bundle. In [`QuantumBot`](https://github.com/kai9987kai/QuantumBot), shallow unentangled circuits tied or outperformed deeper entangled policies.
2. **Inactive or Redundant Grafts Under Ablation:** In [`Supermix-Expanse-v2`](https://github.com/kai9987kai/Supermix-Expanse-v2) and [`Supermix-expanse`](https://github.com/kai9987kai/Supermix-expanse), zero-gating donor experts or latent consolidation modules revealed that apparent gains came from additional training steps rather than the added modules.
3. **Destructive Higher-Order Subset Interactions:** In [`MEMORY-CARRIER-OBSERVATORY`](https://github.com/kai9987kai/MEMORY-CARRIER-OBSERVATORY), full-factorial $2^4$ carrier ablations showed that mechanisms useful in isolation can interact destructively when combined.
4. **Honest Contracts Over Aspirational Labels:** Review of [`Supermix`](https://github.com/kai9987kai/Supermix) (`nexus_conformal_stopping.py`) identified documentation drift where a README described conformal risk guarantees while the active controller explicitly returned `certified_risk_bound=None`. FAULTLINE therefore binds every reported claim to replayable receipts (`faultline-receipt-v1`) and labels bootstrap intervals as descriptive rather than certified.
5. **Non-Duplication of Existing Labs:** Because [`Mnemorph`](https://github.com/kai9987kai/Mnemorph) already tests active assay-grammar revision, [`TESSERA`](https://github.com/kai9987kai/TESSERA) tests ratified 4-bit opcode reuse, and [`NEUROGRAFT`](https://github.com/kai9987kai/NEUROGRAFT) tests sparse connectome routing and successor-representation replay, FAULTLINE targets the unaddressed upstream question: *how should a fixed-budget ensemble selector choose which components to combine when failures are condition-dependent and higher-order?*

---

## 2. Mathematical Framework and Theoretical Analysis

### 2.1 Empirical Failure Hypergraphs

Let $\mathcal{C} = \{0, 1, \dots, m-1\}$ be a set of $m \in [3, 12]$ binary predictors. A labelled dataset consists of a calibration split $\mathcal{D}_{\text{cal}}$ and a disjoint held-out test split $\mathcal{D}_{\text{test}}$. Each case $r \in \mathcal{D}$ has a unique identifier $\text{id}(r)$, a discrete stress condition $g(r) \in \mathcal{G}$, a binary ground-truth label $y(r) \in \{0, 1\}$, and a vector of component predictions $\hat{y}(r) = (\hat{y}_0(r), \dots, \hat{y}_{m-1}(r)) \in \{0, 1\}^m$.

Define the binary failure indicator of component $i \in \mathcal{C}$ on case $r$ as:
$$E_i(r) = \mathbf{1}[\hat{y}_i(r) \neq y(r)] \in \{0, 1\}.$$
The **failure signature** of case $r$ is the set of simultaneously wrong components:
$$S(r) = \{i \in \mathcal{C} : E_i(r) = 1\} \subseteq \mathcal{C}.$$
The multiset of nonempty failure signatures $\{S(r) : r \in \mathcal{D}_{\text{cal}}, S(r) \neq \emptyset\}$ defines an **empirical failure hypergraph** on vertex set $\mathcal{C}$, where a hyperedge of cardinality $|S(r)| = d$ represents an observed $d$-way simultaneous failure.

For any odd-sized panel $P \subset \mathcal{C}$ with $|P| = k \in \{1, 3, 5, \dots\}$ and majority threshold $t = (k+1)/2$, let $W_P(r) = |S(r) \cap P| = \sum_{i \in P} E_i(r)$ denote the number of failing panel members on case $r$. Because $y(r) \in \{0, 1\}$ and $k$ is odd, the majority vote $\hat{y}_P(r) = \mathbf{1}\!\left[\sum_{i \in P} \hat{y}_i(r) \ge t\right]$ errs if and only if at least $t$ members of $P$ err:
$$\text{Err}_P(r) = \mathbf{1}[W_P(r) \ge t].$$

Given a subset of rows $\mathcal{D}' \subseteq \mathcal{D}$ and condition partition $\mathcal{D}'_c = \{r \in \mathcal{D}' : g(r) = c\}$, the **pooled majority error** and **worst-condition majority error** of panel $P$ are:
$$\widehat{\text{Err}}_{\text{pool}}(P; \mathcal{D}') = \frac{1}{|\mathcal{D}'|} \sum_{r \in \mathcal{D}'} \mathbf{1}[W_P(r) \ge t], \qquad \widehat{\text{Err}}_{\text{worst}}(P; \mathcal{D}') = \max_{c \in \mathcal{G}} \frac{1}{|\mathcal{D}'_c|} \sum_{r \in \mathcal{D}'_c} \mathbf{1}[W_P(r) \ge t].$$

### 2.2 The Second Factorial-Moment Pairwise Bound and Its $3\times$ Unanimity Bias

Pairwise ensemble selection methods seek to avoid simultaneous failures using only the $m \times m$ co-failure matrix $M_{ij}(c) = \Pr(E_i = 1 \land E_j = 1 \mid c)$. For $k \ge 3$ and $t = (k+1)/2$, since $W_P \in \{0, 1, \dots, k\}$ is a non-negative integer, the event $W_P \ge t$ is equivalent to $\binom{W_P}{2} \ge \binom{t}{2}$. Because $\binom{W_P}{2} = \sum_{\{i,j\} \subset P} E_i E_j$, Markov's inequality yields the second factorial-moment upper bound:
$$\Pr(W_P \ge t \mid c) = \Pr\!\left(\binom{W_P}{2} \ge \binom{t}{2} \,\middle|\, c\right) \le \frac{\mathbb{E}\!\left[\binom{W_P}{2} \,\middle|\, c\right]}{\binom{t}{2}} = \frac{\sum_{\{i,j\} \subset P} \Pr(E_i = 1 \land E_j = 1 \mid c)}{\binom{t}{2}} \equiv B_{\text{pair}}(P, c).$$

**Proposition 1 (Exact Decomposition for $k=3$).** *For any panel $P = \{i, j, \ell\}$ of size $k=3$ ($t=2, \binom{t}{2}=1$), the pairwise bound $B_{\text{pair}}(P, c)$ and the true majority-vote error $\text{Err}(P, c) = \Pr(W_P \ge 2 \mid c)$ satisfy:*
$$B_{\text{pair}}(P, c) = \Pr(W_P = 2 \mid c) + 3\Pr(W_P = 3 \mid c),$$
$$\text{Err}(P, c) = \Pr(W_P = 2 \mid c) + \Pr(W_P = 3 \mid c),$$
$$B_{\text{pair}}(P, c) - \text{Err}(P, c) = 2\Pr(W_P = 3 \mid c).$$

*Proof.* For $W_P = E_i + E_j + E_\ell \in \{0, 1, 2, 3\}$, the sum of pair products $E_i E_j + E_i E_\ell + E_j E_\ell$ equals $0$ when $W_P \in \{0, 1\}$, equals $\binom{2}{2} = 1$ when $W_P = 2$, and equals $\binom{3}{2} = 3$ when $W_P = 3$. Taking expectations conditional on $c$ yields the identity. $\square$

Proposition 1 exposes a fundamental flaw in pairwise co-failure selection: **every unanimous 3-way failure ($W_P = 3$) is counted three times in $B_{\text{pair}}(P, c)$, whereas a 2-of-3 failure ($W_P = 2$) is counted only once, even though both produce the exact same majority-vote failure ($\hat{y}_P \neq y$).** Consequently, whenever a candidate panel $P_{\text{joint}}$ experiences rare 3-way faults with probability $p_3$ ($\text{Err} = p_3, B_{\text{pair}} = 3p_3$) and an alternative panel $P_{\text{pair}}$ experiences 2-way faults with probability $p_2 \in (p_3, 3p_3)$ ($\text{Err} = p_2, B_{\text{pair}} = p_2$), `pairwise` strictly prefers $P_{\text{pair}}$ despite its higher true error rate $p_2 > p_3$.

### 2.3 Exact 3-Bit Even/Odd Parity Unidentifiability Theorem

**Proposition 2 (Parity Counterexample).** *Let $E^{\text{even}}$ be uniformly distributed over the four even-weight failure vectors in $\{0, 1\}^3$, and let $E^{\text{odd}}$ be uniformly distributed over the four odd-weight failure vectors in $\{0, 1\}^3$:*
$$\mathcal{S}_{\text{even}} = \{(0,0,0), (1,1,0), (1,0,1), (0,1,1)\}, \qquad \mathcal{S}_{\text{odd}} = \{(1,0,0), (0,1,0), (0,0,1), (1,1,1)\}.$$
*Then $E^{\text{even}}$ and $E^{\text{odd}}$ have identical marginal failure rates and identical pairwise co-failure matrices:*
$$\mathbb{E}[E^{\text{even}}_i] = \mathbb{E}[E^{\text{odd}}_i] = \frac{1}{2} \quad \forall i \in \{1,2,3\}, \qquad \mathbb{E}[E^{\text{even}}_i E^{\text{even}}_j] = \mathbb{E}[E^{\text{odd}}_i E^{\text{odd}}_j] = \frac{1}{4} \quad \forall i \neq j,$$
*yet their 3-component majority-vote error rates differ by a factor of three:*
$$\Pr(W^{\text{even}} \ge 2) = \frac{3}{4} = 0.75, \qquad \Pr(W^{\text{odd}} \ge 2) = \frac{1}{4} = 0.25.$$

This counterexample (verified programmatically via `python -m faultline parity`, receipt [`artifacts/parity-demo.json`](../artifacts/parity-demo.json), `payload_sha256 = d8a695a0f616304f...`) proves that no function of first- and second-order failure moments can identify majority-vote reliability.

---

## 3. Experimental Design and Selector Architecture

### 3.1 The Four Deterministic Selectors

Given calibration split $\mathcal{D}_{\text{cal}}$ and odd panel size $k$, `faultline.core.select_panel` enumerates all $\binom{m}{k}$ candidate panels $P$ and evaluates a lexicographic key using exact rational arithmetic (`fractions.Fraction`) so mathematically equal rates never diverge due to IEEE-754 rounding. Let $\text{id}(P) = (\text{id}(i_1), \dots, \text{id}(i_k))$ be the tuple of component IDs in $P$, and let $\hat{e}_i = \frac{1}{|\mathcal{D}_{\text{cal}}|} \sum_{r \in \mathcal{D}_{\text{cal}}} E_i(r)$ be component $i$'s pooled calibration error rate:

| Selector ID | Primary Objective | Secondary Tie-Break | Tertiary Tie-Break | Final Tie-Break |
|---|---|---|---|---|
| **`accuracy`** | $\sum_{i \in P} \hat{e}_i$ | â€” | â€” | Lexical $\text{id}(P)$ |
| **`pairwise`** | $\max_{c \in \mathcal{G}} \widehat{B}_{\text{pair}}(P, c)$ | $\widehat{B}_{\text{pair}}(P, \mathcal{D}_{\text{cal}})$ | $\sum_{i \in P} \hat{e}_i$ | Lexical $\text{id}(P)$ |
| **`pooled`** | $\widehat{\text{Err}}_{\text{pool}}(P; \mathcal{D}_{\text{cal}})$ | $\widehat{\text{Err}}_{\text{worst}}(P; \mathcal{D}_{\text{cal}})$ | $\sum_{i \in P} \hat{e}_i$ | Lexical $\text{id}(P)$ |
| **`joint`** | $\widehat{\text{Err}}_{\text{worst}}(P; \mathcal{D}_{\text{cal}})$ | $\widehat{\text{Err}}_{\text{pool}}(P; \mathcal{D}_{\text{cal}})$ | $\sum_{i \in P} \hat{e}_i$ | Lexical $\text{id}(P)$ |

### 3.2 Synthetic Sensor Catalog and Stress Conditions

`faultline.fixtures.make_dataset` simulates $m = 8$ binary sensor components across 6 physical families and $|\mathcal{G}| = 4$ environmental stress conditions (`nominal`, `glare_surge`, `multipath_hum`, `composed_storm`):
- **Optical Triad (`c0` Optic-Alpha, `c1` Optic-Beta, `c2` Optic-Gamma):** Near-zero error in `nominal`, `multipath_hum`, and `composed_storm` ($\approx 0.5\%$ background noise), achieving the lowest pooled individual error across the dataset ($\hat{e}_i \approx 12.5\%$). However, all three share an optical front-end channel that saturates during `glare_surge` ($\approx 47.5\%$ simultaneous failure).
- **Mid-Tier Cross-Modal Specialists (`c3` Thermal-IR, `c4` Acoustic-Array):** Immune to optical glare majority failure when paired with `c5`, achieving low pooled average error, but subject to 2-of-3 pairwise sub-band faults (`{c3,c4}`, `{c3,c5}`, `{c4,c5}`) during `composed_storm` ($\approx 27\%$ majority error, with zero 3-way faults so $B_{\text{pair}} \approx 0.27$).
- **Hardened Triad (`c5` Radar-MMW, `c6` Mag-Flux, `c7` Inertial-Gyro):** Experiences mild 2-of-3 jitter in benign conditions ($\approx 11\%$ majority error in `nominal`, `glare_surge`, and `multipath_hum`) and a single 3-way EMI burst regime in `composed_storm` ($\approx 14\%$ true majority error, but $B_{\text{pair}} \approx 3 \times 0.14 = 0.42$).

Every random draw is keyed by a stateless SHA-256 event hash:
$$u(\text{seed}, \text{split}, \text{condition}, \text{case\_idx}, \text{channel}) = \frac{\text{uint64}(\text{SHA256}(\texttt{faultline-v1}|\text{seed}|\text{split}|\text{condition}|\text{case\_idx}|\text{channel})_{0..7})}{2^{64}}.$$
This event-keyed architecture (adapted from `Causeway`) guarantees that `calibration` and `test` splits draw independent events, and that increasing `cases` from 32 to 64 preserves the first 32 cases per condition bit-for-bit.

### 3.3 The Three Experimental Scenarios

1. **`shared` (Primary Hypothesis Test â€” Observed Shared & Higher-Order Faults):** Both `calibration` and `test` follow the shared-channel and composed-storm fault model above.
2. **`independent` (Negative Control 1 â€” Conditionally Independent Errors):** All shared channels are disabled; components `c0..c7` fail independently with monotone base rates $(0.05, 0.06, 0.07, 0.14, 0.16, 0.19, 0.21, 0.23)$ scaled by $1.35\times$ in `composed_storm`. Here `('c0', 'c1', 'c2')` is Bayes-optimal.
3. **`shift` (Negative Control 2 â€” Unobserved Test Common-Cause Fault):** Calibration is identical to `shared`, but during `test` in `composed_storm`, a previously dormant common-cause clock fault (`latent_clock_fault`) triggers with probability $0.68$, simultaneously failing `{c5, c6, c7}`.

---

## 4. Empirical Results

### 4.1 Single-Seed Failure Hypergraph Inspection (`seed = 4100`, `shared`, $c = 64$)

On seed `4100` ($256$ calibration rows, $256$ test rows), the calibration pairwise co-failure matrix $M_{ij}$ (diagonal = marginal failure rate $\hat{e}_i$) is:

| Component | `c0` | `c1` | `c2` | `c3` | `c4` | `c5` | `c6` | `c7` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **`c0` (Optic-Alpha)** | **0.1250** | 0.1250 | 0.1250 | 0.0508 | 0.0586 | 0.0195 | 0.0625 | 0.0469 |
| **`c1` (Optic-Beta)** | 0.1250 | **0.1328** | 0.1250 | 0.0547 | 0.0586 | 0.0234 | 0.0625 | 0.0469 |
| **`c2` (Optic-Gamma)** | 0.1250 | 0.1250 | **0.1250** | 0.0508 | 0.0586 | 0.0195 | 0.0625 | 0.0469 |
| **`c3` (Thermal-IR)** | 0.0508 | 0.0547 | 0.0508 | **0.3047** | 0.0391 | 0.0117 | 0.0664 | 0.0469 |
| **`c4` (Acoustic-Array)** | 0.0586 | 0.0586 | 0.0586 | 0.0391 | **0.3438** | 0.0391 | 0.0586 | 0.0664 |
| **`c5` (Radar-MMW)** | 0.0195 | 0.0234 | 0.0195 | 0.0117 | 0.0391 | **0.2852** | 0.1172 | 0.0547 |
| **`c6` (Mag-Flux)** | 0.0625 | 0.0625 | 0.0625 | 0.0664 | 0.0586 | 0.1172 | **0.3203** | 0.0469 |
| **`c7` (Inertial-Gyro)** | 0.0469 | 0.0469 | 0.0469 | 0.0469 | 0.0664 | 0.0547 | 0.0469 | **0.2266** |

Notice that `c0, c1, c2` have the lowest marginal error rates ($12.50\%â€“13.28\%$), but their off-diagonal co-failure rate equals their marginal rate ($0.1250$), indicating total lockstep failure during `glare_surge` (where hyperedges `{c0, c1, c2, c3, c6}` and `{c0, c1, c2, c4, c7}` occur). On this seed:
- `accuracy` selects `['c0', 'c1', 'c2']` $\rightarrow$ held-out worst-condition test error **56.25%** (`0.562500`).
- `pairwise` and `pooled` select `['c0', 'c3', 'c5']` $\rightarrow$ held-out worst-condition test error **32.81%** (`0.328125`).
- `joint` selects `['c5', 'c6', 'c7']` $\rightarrow$ held-out worst-condition test error **14.06%** (`0.140625`).

---

### 4.2 Development Pilot (`seeds = 4100..4123`, $N = 24$ Paired Seeds, $k = 3$, $c = 64$)

#### Table 1: Development Pilot Calibration and Held-Out Test Performance

| Scenario | Selector | Most Frequent Panel ($n/24$) | Mean Cal Pooled | Mean Cal Worst-Cond | Mean Test Pooled | Mean Test Worst-Cond | Mean Test Unanimous Wrong |
|---|---|---|---:|---:|---:|---:|---:|
| **`shared`** | `accuracy` | `('c0','c1','c2')` (24/24) | 12.34% | 49.35% | 12.08% | 48.31% | 12.08% |
| **`shared`** | `pairwise` | `('c3','c4','c5')` (11/24) | 7.91% | 22.85% | 10.04% | 31.12% | 0.41% |
| **`shared`** | `pooled` | `('c3','c4','c5')` (20/24) | **7.24%** | 26.11% | **8.11%** | 29.23% | **0.05%** |
| **`shared`** | `joint` | `('c5','c6','c7')` (21/24) | 12.52% | **17.19%** | 12.48% | **19.60%** | 3.17% |
| **`independent`** | `accuracy` | `('c0','c1','c2')` (24/24) | 1.42% | 2.93% | **1.27%** | **2.93%** | **0.07%** |
| **`independent`** | `pairwise` | `('c0','c1','c2')` (12/24) | 1.06% | 2.08% | 1.73% | 3.71% | 0.08% |
| **`independent`** | `pooled` | `('c0','c1','c2')` (12/24) | **1.01%** | 2.08% | 1.73% | 3.65% | 0.08% |
| **`independent`** | `joint` | `('c0','c1','c2')` (12/24) | 1.03% | **2.02%** | 1.71% | 3.65% | 0.08% |
| **`shift`** | `accuracy` | `('c0','c1','c2')` (24/24) | 12.34% | 49.35% | 12.08% | 48.31% | 12.08% |
| **`shift`** | `pairwise` | `('c3','c4','c5')` (11/24) | 7.91% | 22.85% | 9.23% | 28.58% | 1.48% |
| **`shift`** | `pooled` | `('c3','c4','c5')` (20/24) | **7.24%** | 26.11% | **3.99%** | **14.06%** | **0.02%** |
| **`shift`** | `joint` | `('c5','c6','c7')` (21/24) | 12.52% | **17.19%** | 24.45% | 64.65% | 15.87% |

#### Table 2: Development Pilot Paired Differences Against `joint` ($\text{Err}_{\text{comp}} - \text{Err}_{\text{joint}}$)

| Scenario | Comparator | Mean $\Delta$ Worst-Cond | 95% Bootstrap CI (Worst-Cond) | Median $\Delta$ (`[Min, Max]`) | Mean $\Delta$ Pooled | Win / Tie / Loss (`joint` vs. Comp) |
|---|---|---:|---|---:|---:|---:|
| **`shared`** | `accuracy` | **+28.71 pp** (`+0.287109`) | `[+25.07, +32.03]` pp | +28.13 pp (`[+12.50, +43.75]`) | âˆ’0.41 pp | **24 W / 0 T / 0 L** |
| **`shared`** | `pairwise` | **+11.52 pp** (`+0.115234`) | `[+8.40, +14.71]` pp | +11.72 pp (`[0.00, +25.00]`) | âˆ’2.44 pp | **19 W / 5 T / 0 L** |
| **`shared`** | `pooled` | **+9.64 pp** (`+0.096354`) | `[+6.64, +12.43]` pp | +10.94 pp (`[âˆ’6.25, +21.88]`) | âˆ’4.38 pp | **19 W / 4 T / 1 L** |
| **`independent`** | `accuracy` | **âˆ’0.72 pp** (`âˆ’0.007161`) | `[âˆ’1.63, +0.13]` pp | 0.00 pp (`[âˆ’7.81, +3.13]`) | âˆ’0.44 pp | **3 W / 14 T / 7 L** |
| **`independent`** | `pairwise` | **+0.07 pp** (`+0.000651`) | `[0.00, +0.26]` pp | 0.00 pp (`[0.00, +1.56]`) | +0.02 pp | **1 W / 23 T / 0 L** |
| **`independent`** | `pooled` | **0.00 pp** (`0.000000`) | `[0.00, 0.00]` pp | 0.00 pp (`[0.00, 0.00]`) | +0.02 pp | **0 W / 24 T / 0 L** |
| **`shift`** | `accuracy` | **âˆ’16.34 pp** (`âˆ’0.163411`) | `[âˆ’24.48, âˆ’7.10]` pp | âˆ’21.09 pp (`[âˆ’45.31, +48.44]`) | âˆ’12.37 pp | **3 W / 0 T / 21 L** |
| **`shift`** | `pairwise` | **âˆ’36.07 pp** (`âˆ’0.360677`) | `[âˆ’45.25, âˆ’24.93]` pp | âˆ’42.97 pp (`[âˆ’71.88, 0.00]`) | âˆ’15.22 pp | **0 W / 7 T / 17 L** |
| **`shift`** | `pooled` | **âˆ’50.59 pp** (`âˆ’0.505859`) | `[âˆ’58.46, âˆ’41.34]` pp | âˆ’57.03 pp (`[âˆ’71.88, 0.00]`) | âˆ’20.46 pp | **0 W / 3 T / 21 L** |

*(Pilot receipt digests: [`pilot-shared-4100.json`](../artifacts/pilot-shared-4100.json) `048e2c56f5391a53...`, [`pilot-independent-4100.json`](../artifacts/pilot-independent-4100.json) `21c711f09a6b56ff...`, [`pilot-shift-4100.json`](../artifacts/pilot-shift-4100.json) `349361e37d590e90...`.)*

---

### 4.3 Frozen Confirmation Suite (`seeds = 9100..9123`, $N = 24$ Paired Seeds, $k = 3$, $c = 64$)

After freezing the implementation (`source_sha256 = 2144abd4c154a5370ab5e353999c737d188eed3a918868dc29ed1ed14a973c79`), the confirmation seed block `9100..9123` was evaluated once without post-hoc parameter tuning.

#### Table 3: Frozen Confirmation Calibration and Held-Out Test Performance

| Scenario | Selector | Most Frequent Panel ($n/24$) | Mean Cal Pooled | Mean Cal Worst-Cond | Mean Test Pooled | Mean Test Worst-Cond | Mean Test Unanimous Wrong |
|---|---|---|---:|---:|---:|---:|---:|
| **`shared`** | `accuracy` | `('c0','c1','c2')` (24/24) | 11.57% | 46.29% | 11.95% | 47.79% | 11.95% |
| **`shared`** | `pairwise` | `('c3','c4','c5')` (11/24) | 8.01% | 21.94% | 10.03% | 29.62% | 0.31% |
| **`shared`** | `pooled` | `('c3','c4','c5')` (20/24) | **6.85%** | 24.41% | **8.53%** | 29.95% | **0.29%** |
| **`shared`** | `joint` | `('c5','c6','c7')` (18/24) | 11.20% | **17.51%** | 12.66% | **21.29%** | 2.83% |
| **`independent`** | `accuracy` | `('c0','c1','c2')` (24/24) | 1.32% | 3.06% | **1.09%** | **2.80%** | **0.02%** |
| **`independent`** | `pairwise` | `('c0','c1','c2')` (13/24) | 1.24% | 2.34% | 1.63% | 3.39% | 0.03% |
| **`independent`** | `pooled` | `('c0','c1','c2')` (13/24) | **1.07%** | 2.41% | 1.89% | 3.52% | 0.03% |
| **`independent`** | `joint` | `('c0','c1','c2')` (14/24) | 1.09% | **2.34%** | 1.86% | 3.52% | 0.03% |
| **`shift`** | `accuracy` | `('c0','c1','c2')` (24/24) | 11.57% | 46.29% | 11.95% | 47.79% | 11.95% |
| **`shift`** | `pairwise` | `('c3','c4','c5')` (11/24) | 8.01% | 21.94% | 8.85% | 26.76% | 1.38% |
| **`shift`** | `pooled` | `('c3','c4','c5')` (20/24) | **6.85%** | 24.41% | **3.86%** | **12.43%** | **0.29%** |
| **`shift`** | `joint` | `('c5','c6','c7')` (18/24) | 11.20% | **17.51%** | 22.72% | 60.61% | 13.88% |

#### Table 4: Frozen Confirmation Paired Differences Against `joint` ($\text{Err}_{\text{comp}} - \text{Err}_{\text{joint}}$)

| Scenario | Comparator | Mean $\Delta$ Worst-Cond | 95% Bootstrap CI (Worst-Cond) | Median $\Delta$ (`[Min, Max]`) | Mean $\Delta$ Pooled | Win / Tie / Loss (`joint` vs. Comp) |
|---|---|---:|---|---:|---:|---:|
| **`shared`** | `accuracy` | **+26.50 pp** (`+0.264974`) | `[+23.57, +29.62]` pp | +25.00 pp (`[+10.94, +42.19]`) | âˆ’0.72 pp | **24 W / 0 T / 0 L** |
| **`shared`** | `pairwise` | **+8.33 pp** (`+0.083333`) | `[+4.95, +11.85]` pp | +7.81 pp (`[âˆ’9.38, +23.44]`) | âˆ’2.64 pp | **17 W / 6 T / 1 L** |
| **`shared`** | `pooled` | **+8.66 pp** (`+0.086589`) | `[+5.21, +12.11]` pp | +8.59 pp (`[âˆ’7.81, +23.44]`) | âˆ’4.13 pp | **18 W / 4 T / 2 L** |
| **`independent`** | `accuracy` | **âˆ’0.72 pp** (`âˆ’0.007161`) | `[âˆ’1.37, âˆ’0.20]` pp | 0.00 pp (`[âˆ’4.69, +1.56]`) | âˆ’0.77 pp | **1 W / 16 T / 7 L** |
| **`independent`** | `pairwise` | **âˆ’0.13 pp** (`âˆ’0.001302`) | `[âˆ’0.33, 0.00]` pp | 0.00 pp (`[âˆ’1.56, 0.00]`) | âˆ’0.23 pp | **0 W / 22 T / 2 L** |
| **`independent`** | `pooled` | **0.00 pp** (`0.000000`) | `[0.00, 0.00]` pp | 0.00 pp (`[0.00, 0.00]`) | +0.03 pp | **0 W / 24 T / 0 L** |
| **`shift`** | `accuracy` | **âˆ’12.83 pp** (`âˆ’0.128255`) | `[âˆ’21.48, âˆ’2.93]` pp | âˆ’21.88 pp (`[âˆ’42.19, +39.06]`) | âˆ’10.77 pp | **6 W / 0 T / 18 L** |
| **`shift`** | `pairwise` | **âˆ’33.85 pp** (`âˆ’0.338542`) | `[âˆ’46.68, âˆ’20.96]` pp | âˆ’47.66 pp (`[âˆ’73.44, +37.50]`) | âˆ’13.87 pp | **2 W / 7 T / 15 L** |
| **`shift`** | `pooled` | **âˆ’48.18 pp** (`âˆ’0.481771`) | `[âˆ’57.75, âˆ’37.57]` pp | âˆ’57.03 pp (`[âˆ’75.00, 0.00]`) | âˆ’18.86 pp | **0 W / 3 T / 21 L** |

*(Confirmation receipt digests: [`confirm-shared-9100.json`](../artifacts/confirm-shared-9100.json) `fe083c561e21d89a...`, [`confirm-independent-9100.json`](../artifacts/confirm-independent-9100.json) `10eb3e843b3a5b31...`, [`confirm-shift-9100.json`](../artifacts/confirm-shift-9100.json) `8a81909f72fdb4e6...`.)*

---

### 4.4 Per-Condition Error Profile and the Robustnessâ€“Average Trade-Off

Decomposing held-out test error by stress condition across the 24 confirmation seeds (`confirm-shared-9100.json`) explains *why* the four selectors diverge:

| Selector | `nominal` | `glare_surge` | `multipath_hum` | `composed_storm` | Pooled Mean | Worst-Group Mean |
|---|---:|---:|---:|---:|---:|---:|
| **`accuracy`** | **0.00%** | 47.79% | **0.00%** | **0.00%** | 11.95% | 47.79% |
| **`pooled`** | 0.72% | 5.60% | 0.52% | 27.28% | **8.53%** | 29.95% |
| **`pairwise`** | 2.54% | 13.28% | 1.82% | 22.46% | 10.03% | 29.62% |
| **`joint`** | 10.74% | 13.87% | 10.03% | **16.02%** | 12.66% | **21.29%** |

- **`accuracy`** achieves $0.00\%$ error in three of four conditions by selecting the optical triad `('c0', 'c1', 'c2')`, but suffers catastrophic shared-channel failure (**47.79%**) in `glare_surge`.
- **`pooled`** minimizes average error across all four conditions (**8.53%**) by selecting `('c3', 'c4', 'c5')`, which is nearly error-free in benign conditions but suffers **27.28%** 2-of-3 failure in `composed_storm`.
- **`pairwise`** also rejects `('c5', 'c6', 'c7')` on most seeds because the 3-way EMI burst in `composed_storm` is multiplied by $3\times$ in the second-moment bound (Proposition 1).
- **`joint`** flattens the risk profile across all four conditions ($10.03\%â€“16.02\%$), trading $+4.13\text{ pp}$ higher average error against `pooled` to gain $+8.66\text{ pp}$ lower worst-condition error.

---

### 4.5 Ablation 1: Calibration Sample Budget Scaling ($c \in \{16, 32, 64, 128, 256\}$)

To separate finite-sample estimation variance from structural approximation bias, we evaluated the confirmation seed block (`9100..9123`, `shared`, $k=3$) across five calibration budgets $c \in \{16, 32, 64, 128, 256\}$ cases per condition ($64$ to $1024$ total calibration rows):

| Cases / Condition ($c$) | Total Cal Rows ($4c$) | `accuracy` Worst-Cond | `pairwise` Worst-Cond | `pooled` Worst-Cond | `joint` Worst-Cond | Gain of `joint` over `pairwise` |
|---:|---:|---:|---:|---:|---:|---:|
| **16** | 64 | 47.14% | 32.03% | 31.77% | **30.47%** | +1.56 pp |
| **32** | 128 | 48.31% | 30.60% | 29.69% | **27.47%** | +3.13 pp |
| **64** | 256 | 47.79% | 29.62% | 29.95% | **21.29%** | +8.33 pp |
| **128** | 512 | 47.30% | 30.11% | 27.90% | **17.38%** | +12.73 pp |
| **256** | 1024 | 46.92% | 29.13% | 28.08% | **15.77%** | **+13.36 pp** |

As $c$ increases from $16$ to $256$, `pairwise` plateaus around **29.13%** because its second-moment objective is biased away from `('c5', 'c6', 'c7')` by Proposition 1 regardless of sample size. By contrast, `joint` is statistically consistent for worst-condition majority error, dropping monotonically from **30.47%** ($c=16$) to **15.77%** ($c=256$).

---

### 4.6 Ablation 2: Panel Size Scaling ($k \in \{1, 3, 5, 7\}$) and Non-Monotone Ensemble Degradation

Evaluating all odd panel sizes $k \in \{1, 3, 5, 7\}$ on the confirmation seed block (`9100..9123`, `shared`, $c=64$) reveals non-monotone scaling with ensemble size:

| Odd Panel Size ($k$) | Candidate Panels $\binom{8}{k}$ | Majority Threshold $t$ | `accuracy` Worst-Cond | `pairwise` Worst-Cond | `pooled` Worst-Cond | `joint` Worst-Cond |
|---:|---:|---:|---:|---:|---:|---:|
| **$k = 1$** | 8 | 1 | 48.05% | 36.39% | 48.05% | **36.39%** |
| **$k = 3$** | 56 | 2 | 47.79% | 29.62% | 29.95% | **21.29%** |
| **$k = 5$** | 56 | 3 | 47.79% | 19.21% | **18.62%** | 18.68% |
| **$k = 7$** | 8 | 4 | 47.79% | 38.54% | 38.54% | **38.54%** |

Two structural insights emerge:
1. **At $k=1$, `pairwise` and `joint` coincide (`36.39%`)** because a 1-member panel has no higher-order interactions, reducing both rules to worst-condition individual error.
2. **Expanding the ensemble from $k=3$ (`21.29%`) or $k=5$ (`18.68%`) to $k=7$ (`38.54%`) severely degrades worst-condition reliability.** Because there are only $m=8$ components and three of them (`c0, c1, c2`) fail together during `glare_surge` along with two cross-family sensors (`X1..X4` fail 5 sensors simultaneously: `{0,1,2,3,6}`, `{0,1,2,3,7}`, `{0,1,2,4,6}`, `{0,1,2,4,7}`), **every** 7-component subset is forced to include at least 4 of those 5 simultaneously failing sensors ($W \ge 4 = t$), causing majority failure across `glare_surge`! This provides a sharp mathematical demonstration of the portfolio-wide lesson from *FLY-DIAMOND-NEXUS* and *Supermix-Expanse-v2*: larger ensembles are inferior to smaller curated panels when the candidate pool contains correlated failure clusters.

---

## 5. Threat Model, Verification Protocol, and Scope Boundaries

### 5.1 Source-Bound Cryptographic Receipts (`faultline-receipt-v1`)

To prevent silent drift between code, configuration, and reported metrics, every CLI and HTTP execution emits a canonical JSON receipt signed with three SHA-256 digests (`faultline/receipts.py`):
- `source_sha256`: digest over normalized UTF-8 source bytes of `core.py`, `fixtures.py`, `study.py`, and `receipts.py`.
- `input_sha256`: digest over canonical imported dataset JSON (for `analyze` receipts).
- `payload_sha256`: digest over `(schema, kind, config, source_sha256, input_sha256, result)`.

Crucially, `verify_receipt` does **not** trust `payload_sha256` alone: it recomputes the full experiment from `config` / `input_data` and compares the recomputed result digest against `result`. An attacker who edits a metric and recomputes `payload_sha256` is caught and rejected as a replay mismatch (`test_receipt_replay_catches_hash_tampering_and_rehashed_fabrication`).

### 5.2 Scientific and Operational Boundaries

1. **Synthetic Sensor Regime vs. Foundation Model Reasoning:** Our fixtures model discrete binary predictors under explicit shared-channel and higher-order fault distributions. They do not prove that LLM multi-agent debate, biological neural circuits, or clinical decision systems follow the same numerical gains without domain-specific calibration data.
2. **Observational Hyperedges vs. Causal Mechanisms:** Empirical failure hyperedges record *which* components failed simultaneously on calibration cases; they do not identify physical root causes without interventional fault injection.
3. **Vulnerability to Unobserved Common Causes (`shift`):** As proven in Negative Control 2 (Tables 2 and 4), empirical joint-failure selection can only guard against stress regimes observed during calibration. If a selected panel shares a latent hardware, data, or clock dependency that triggers only in deployment, `joint` can perform substantially worse than `pooled` or `pairwise`.
4. **Descriptive Bootstrap Intervals:** Reported 95% intervals are percentile bootstraps over seed pairs ($1{,}000$ resamples) and do not constitute sequential anytime-valid e-processes or finite-sample conformal risk bounds.

---

## 6. Reproducibility Commands

All tables and receipts in this paper can be reproduced and verified offline in under 15 seconds on Python 3.12+:

```powershell
# 1. Run all 16 unit, isolation, control, and tamper-detection tests
python -m unittest discover -s tests -v

# 2. Verify all 7 recorded receipts in artifacts/
python -m faultline verify artifacts/pilot-shared-4100.json
python -m faultline verify artifacts/pilot-independent-4100.json
python -m faultline verify artifacts/pilot-shift-4100.json
python -m faultline verify artifacts/confirm-shared-9100.json
python -m faultline verify artifacts/confirm-independent-9100.json
python -m faultline verify artifacts/confirm-shift-9100.json
python -m faultline verify artifacts/parity-demo.json
```

---

## References

1. Knight, J. C., & Leveson, N. G. (1986). An experimental evaluation of the assumption of independence in multiversion programming. *IEEE Transactions on Software Engineering*, SE-12(1), 96â€“109.
2. Eckhardt, D. E., & Lee, L. D. (1985). A theoretical basis for the analysis of multiversion software subject to coincident errors. *IEEE Transactions on Software Engineering*, SE-11(12), 1511â€“1517.
3. Kuncheva, L. I., Whitaker, C. J., Shipp, C. A., & Duin, R. P. W. (2003). Limits on the majority vote accuracy in classifier fusion. *Pattern Analysis & Applications*, 6(1), 22â€“31.
4. Sagawa, S., Koh, P. W., Hashimoto, T. B., & Liang, P. (2020). Distributionally robust neural networks for group shifts: On the importance of regularization for worst-case generalization. *International Conference on Learning Representations (ICLR)*.
5. Portfolio Source Reviews (24 October 2026): [`docs/portfolio-and-research-review.md`](portfolio-and-research-review.md), [`research/review-models.md`](../research/review-models.md), [`research/review-labs.md`](../research/review-labs.md), and [`research/review-tools.md`](../research/review-tools.md).
