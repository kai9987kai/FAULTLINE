# Unified 26-Repository Portfolio Review and Primary Research Synthesis

Reviewed 24 October 2026. This document synthesises all 26 linked repositories across the three detailed source-inspection reports ([`research/review-models.md`](../research/review-models.md), [`research/review-labs.md`](../research/review-labs.md), and [`research/review-tools.md`](../research/review-tools.md)) alongside primary research on correlated failures in multi-version software and machine-learning ensembles.

## 1. Complete 26-Repository Index and Extracted Design Lessons

Every repository in the prompt was inspected live via its default branch README, metadata, and representative source files. No upstream repository code or external model weights were executed here; historical benchmark numbers belong to their source repositories.

| # | Repository | Primary Domain / Mechanism | Inspected Commit / Blob | Key Carry-Forward Lesson & Portfolio Boundary |
|---|---|---|---|---|
| 1 | [NexusSearch](https://github.com/kai9987kai/NexusSearch) | C11 immutable-snapshot hybrid search (`nx_search.c`) | HEAD `538edcba59` | Retain exact deterministic baselines, immutable inputs, and lexical tie-breaking. |
| 2 | [prometheus-alpha](https://github.com/kai9987kai/prometheus-alpha) | 1D neural cellular automaton memory & regeneration (`tissue.py`) | HEAD `417009e554` | Decodability is not causal utility; evaluate interventions on held-out stress conditions. |
| 3 | [3d-animal-simulator-Hybrid-Agent](https://github.com/kai9987kai/3d-animal-simulator-Hybrid-Agent) | Browser 3D ecosystem with separate RNG streams (`src/boot.js`) | HEAD `b7dd934770` | Isolate measurement/experiment state from UI rendering; separate RNG channels. |
| 4 | [morpheus](https://github.com/kai9987kai/morpheus) | 2D cellular tissue & audited self-improvement (`src/morpheus/rsi.py`) | HEAD `5db6f98d60` | Separate calibration/proposal selection from frozen held-out evaluation; report sample cost. |
| 5 | [Supermix-Expanse-v2](https://github.com/kai9987kai/Supermix-Expanse-v2) | Residual latent-MoE & connectome matrix (`consolidation_v2.py`) | HEAD `33e38a279c` | Added modules can contribute near-zero incremental gain when ablated; keep negative results visible. |
| 6 | [GhostInTheMachine](https://github.com/kai9987kai/GhostInTheMachine) | Coupled recurrent populations & mismatch decomposition (`engine.py`) | HEAD `239f5de645` | Retain negative results and retractions alongside positive findings in the same ledger. |
| 7 | [Supermix-expanse](https://github.com/kai9987kai/Supermix-expanse) | Language trunk + donor expert grafts + FlyCore (`connectome_full.py`) | HEAD `3fd091e9cc` | Measure downstream task output changes rather than assuming donor modules add independent skill. |
| 8 | [GenesisEngine](https://github.com/kai9987kai/GenesisEngine) | Developmental multicellular A-life (`src/genesis/experiments.py`) | HEAD `a43099ef21` | Bind source hashes to experiment receipts and bootstrap paired seed differences. |
| 9 | [supermix-archimedes](https://github.com/kai9987kai/supermix-archimedes) | 320-d trunk with lifted 256-d donor experts (`archimedes_core.py`) | HEAD `1952cf1c92` | Use explicit typed schemas and zero-effect baselines rather than cosmetic wrappers. |
| 10 | [Supermix](https://github.com/kai9987kai/Supermix) | Monorepo with heuristic stopping controller (`nexus_conformal_stopping.py`) | HEAD `6ea1c2cc41` | Avoid claiming conformal/certified bounds when the code computes empirical quantiles or bootstraps. |
| 11 | [FLY-DIAMOND-NEXUS](https://github.com/kai9987kai/FLY-DIAMOND-NEXUS) | 22-module fly-inspired controller (`worldlab-experiments.js`) | HEAD `0c8d4100b2` | One simple controller beat the 16-module bundle; more modules can degrade or duplicate decisions. |
| 12 | [QuantumBot](https://github.com/kai9987kai/QuantumBot) | Variational quantum policy circuits & causal comms (`metrics.py`) | HEAD `42e4fd637d` | Shallow unentangled policies tied or beat deeper entangled ones; test simple baselines honestly. |
| 13 | [Causeway](https://github.com/kai9987kai/Causeway) | Watershed policy workbench (`src/model.js`) | HEAD `e25ea9e6a5` | Use event-keyed randomness (`seed/split/condition/case/channel`) so changes do not shift RNG streams. |
| 14 | [MOLT](https://github.com/kai9987kai/MOLT) | Head-locked vs. distributed trace comparison (`src/engine.js`) | HEAD `8ac04b1839` | Include explicit negative controls where the proposed mechanism should not help or should fail. |
| 15 | [universal-modder](https://github.com/rehan-remade/universal-modder) | Game runtime scanner & modding CLI (`um/scan.py`) | HEAD `c1dff21663` | Validate structural preconditions before running downstream analysis. |
| 16 | [rea](https://github.com/morluto/rea) | Multi-provider reverse-engineering evidence CLI (`cliEvidenceCommands.ts`) | HEAD `2250e67bc2` | Treat evidence as a schema-validated, size-bounded artifact with explicit error projection. |
| 17 | [odysseus](https://github.com/odysseus-dev/odysseus) | Self-hosted workspace & report sanitizer (`src/visual_report.py`) | HEAD `f8e043e8ca` | Treat imported files as untrusted data; render text safely without executing or injecting HTML. |
| 18 | [MEMORY-CARRIER-OBSERVATORY](https://github.com/kai9987kai/MEMORY-CARRIER-OBSERVATORY) | 4-carrier × 6-context factorial ablation (`src/engine.js`) | HEAD `523c10b46f` | Higher-order interactions can reverse individual component gains; inspect joint combinations. |
| 19 | [nexusflow](https://github.com/kai9987kai/nexusflow) | Declarative experiment DSL (`nexusflow/lang.py`) | HEAD `3fb4be7e7f` | Separate input validation from execution; emit self-contained JSON snapshots. |
| 20 | [Flipper-Zero-Periodic-NTAG-Emulator](https://github.com/djpiper28/Flipper-Zero-Periodic-NTAG-Emulator) | C state-machine NTAG UID rotator (`ntag213_rotator.c`) | HEAD `98fd747825` | Count calibration/search evaluations separately from externally verified deployment outcomes. |
| 21 | [quibble-builds](https://github.com/7coil/quibble-builds) | Freestanding C++20 EFI Windows bootloader (`src/boot.cpp`) | HEAD `f89481a1a3` | Verify contracts at the full system boundary; hash integrity alone does not prove replay equivalence. |
| 22 | [svideo](https://github.com/7coil/svideo) | Video-to-Scratch frame deduplicator (`src/FFmpeg.ts`) | HEAD `d4b34633e9` | Compress repeated failure patterns into explicit empirical signatures with counts and rates. |
| 23 | [Mnemorph](https://github.com/kai9987kai/Mnemorph) | Active assay selection & grammar revision (`src/core/compiler.js`) | HEAD `4fc3353b4a` | Freeze choices before scoring on withheld test cases; do not duplicate assay-grammar search. |
| 24 | [TESSERA](https://github.com/kai9987kai/TESSERA) | Ratified 4-bit opcode commons (`src/engine.js`) | HEAD `85e7404528` | Evaluate frozen selections on fresh test populations under identical call budgets. |
| 25 | [Supermix-Poseidon](https://github.com/kai9987kai/Supermix-Poseidon) | Frozen policy + MNEMOSYNE episodic memory (`poseidon/mnemosyne.py`) | HEAD `72d42218ae` | Distinguish optional/complex components from simple baselines; keep replay deterministic. |
| 26 | [NEUROGRAFT](https://github.com/kai9987kai/NEUROGRAFT) | Sparse connectome routing & SR replay (`neurograft/dynamics.py`) | HEAD `2301f0af16` | Preserve component provenance; do not duplicate graph grafting or successor-representation replay. |

---

## 2. Primary Research Grounding

1. **Correlated Failures in Multi-Version Systems (Knight & Leveson, 1986; Eckhardt & Lee, 1985)**
   - Knight and Leveson (*IEEE Transactions on Software Engineering*, SE-12(1), 96–109, 1986) demonstrated experimentally that independently written software versions fail together far more often than predicted by the product of their marginal error rates because difficult or unusual inputs act as shared stress conditions.
   - Eckhardt and Lee (*IEEE Transactions on Software Engineering*, SE-11(12), 1511–1517, 1985) formalized this through a varying difficulty intensity $\theta(x)$ over the input space: even when components are conditionally independent given $x$, integrating over input difficulty induces positive co-failure correlation, and shared design assumptions induce conditional dependence even within a condition.

2. **Pairwise Diversity vs. Higher-Order Majority Vote Error (Kuncheva et al., 2003; Tang, Suganthan & Yao, 2006)**
   - Classical ensemble diversity metrics (Q-statistic, kappa, double-fault measure) summarize only *pairwise* co-failures $\Pr(E_i = 1 \land E_j = 1)$.
   - However, for an odd panel $P$ of size $k=3$ with failure count $W = \sum_{i \in P} E_i$, the sum of pairwise co-failures satisfies the exact algebraic identity:
     $$\sum_{\{i,j\} \subset P} \Pr(E_i = 1 \land E_j = 1) = \Pr(W = 2) + 3\Pr(W = 3),$$
     whereas the actual majority-vote error rate is:
     $$\Pr(W \ge 2) = \Pr(W = 2) + \Pr(W = 3).$$
   - Consequently, any pairwise co-failure bound over-weights unanimous 3-way failures by a factor of $3\times$ relative to 2-of-3 failures, even though both produce the exact same wrong majority vote. The classic 3-bit even-parity vs. odd-parity counterexample makes this failure mode extreme: both distributions have marginal failure rates $(1/2, 1/2, 1/2)$ and pairwise co-failure rates $(1/4, 1/4, 1/4)$, yet majority error is $3/4$ under even parity and $1/4$ under odd parity.

3. **Worst-Group Robustness vs. Pooled Risk (Sagawa et al., 2020) and Unobserved Common-Cause Shifts**
   - Group Distributionally Robust Optimization (Sagawa et al., *ICLR*, 2020) shows that minimizing average (pooled) error across conditions allows high error on minority or severe stress conditions when benign conditions dominate the sample count.
   - Conversely, empirical worst-group selection (`joint`) relies on all relevant common-cause failure modes being represented in the calibration conditions. When a latent common-cause channel (`scenario="shift"`) activates only at deployment time, empirical joint selection can over-concentrate on components that share that previously dormant substrate. FAULTLINE includes both `independent` and `shift` as first-class negative controls so this boundary is measured rather than hidden.
