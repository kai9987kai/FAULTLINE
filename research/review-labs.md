# Portfolio review: synthetic laboratories and graph agents

Reviewed live on 24 October 2026 through the GitHub connector. This is a README/design review with bounded representative-source inspection, not a full code audit or rerun of the projects' tests. No downloaded repository code was executed. Every reported historical result below is attributed to the repository, not independently reproduced here. The SHA column records Git blob IDs returned for the fetched README, not repository commit IDs.

| Repository | README blob SHA | Additional source inspected |
|---|---|---|
| [3d-animal-simulator-Hybrid-Agent](https://github.com/kai9987kai/3d-animal-simulator-Hybrid-Agent) | `e2007f9bd5f92cc5fe00c642f7ffe23d786e6061` | `src/boot.js` |
| [GenesisEngine](https://github.com/kai9987kai/GenesisEngine) | `6f4c8624bd1ab0930ee12c82ca5ab3aa8ed04f4d` | `src/genesis/experiments.py`, `docs/model.md`, `pyproject.toml` |
| [FLY-DIAMOND-NEXUS](https://github.com/kai9987kai/FLY-DIAMOND-NEXUS) | root `0a92b00e9c7462fbcea3ef786336280dac5a3746`; nested `41cfdd29a5ab7d686cd0949055da49ce62840638` | `DIAMOND-SIM-FLY/README.md`, `DIAMOND-SIM-FLY/src/worldlab-experiments.js` |
| [QuantumBot](https://github.com/kai9987kai/QuantumBot) | `5b123109885715a354fcfdd6e1077f3eee524c9b` | `quantumbot/metrics.py` |
| [Causeway](https://github.com/kai9987kai/Causeway) | `12a5dc50881d70531f231cfe3717ce66584b030f` | `src/model.js` |
| [MOLT](https://github.com/kai9987kai/MOLT) | `4e6f97f271d61ac1522674ca8a80bf9b08ed42c8` | `src/engine.js` |
| [MEMORY-CARRIER-OBSERVATORY](https://github.com/kai9987kai/MEMORY-CARRIER-OBSERVATORY) | `5bd88adefa55478e6f2244592bbc2041af58a679` | `src/engine.js` |
| [Mnemorph](https://github.com/kai9987kai/Mnemorph) | `de71f25e756d436da9ee6a7e5df7c092d7aab9fb` | `src/core/compiler.js`, roadmap search excerpt |
| [NEUROGRAFT](https://github.com/kai9987kai/NEUROGRAFT) | `be29ccd1181cee4fe30c263efa2441b3ec3bb5bc` | `neurograft/dynamics.py`, `docs/v12-build-report.md` |

## EvoSim / 3d-animal-simulator-Hybrid-Agent

**What exists.** A browser Three.js ecosystem with inherited traits, local learning, disease/weather rules, resource renewal, energy-aware predation, seeded runs, snapshots and paired interventions. Version 6.1 adds an explicit population census and inspectable resource/energy flows. The README states 1/60-second stepping, schema-7 snapshots and separate observation noise.

**Source check.** [`src/boot.js`](https://github.com/kai9987kai/3d-animal-simulator-Hybrid-Agent/blob/main/src/boot.js) creates distinct ecology, sensor and visual RNG streams; resets counters/census; exposes deterministic stepping and state inspection hooks; and prevents ordinary stepping during experiments. This supports the isolation and inspectability design, without proving every snapshot field or ecological equation correct.

**Carry forward.** Separate rendering and measurement from the experiment state; instrument conservation/accounting identities; expose deterministic hooks for UI validation.

**Boundary.** Short rollouts and 2–6 replicates do not establish long-run ecological viability. Sequential randomness can diverge between intervention arms. Eco-types and simulated eDNA signatures are model categories, not biological species or validated assays. Source indexed at commit `b7dd934770380a28717ddc82e3dfa7f127732a75`.

## GenesisEngine

**What exists.** A Python developmental artificial-life model: regulatory genomes create multicellular bodies and recurrent controllers, followed by lifetime learning, energy accounting, reproduction and evolutionary selection. The browser is a viewer/controller over the deterministic core. Development, lifetime learning and intergenerational inheritance are distinct processes.

**Source check.** [`src/genesis/experiments.py`](https://github.com/kai9987kai/GenesisEngine/blob/main/src/genesis/experiments.py) validates explicit intervention manifests and workload limits, creates independent control/treatment worlds, records per-run snapshot hashes and source hashes, and bootstraps seed-pair differences. It explicitly rejects pretending that direct encoding exists as a comparator. [`docs/model.md`](https://github.com/kai9987kai/GenesisEngine/blob/main/docs/model.md) says learned neural weights are not inherited and explains the simplified organ model.

**Carry forward.** Record when an intervention acts; retain source identity alongside state; make unsupported comparators fail clearly.

**Boundary.** Initial-seed pairing is not event synchronization after trajectories diverge. Direct-versus-developmental matched-budget evidence, open-ended evolution, predation and biological realism are not implemented findings. Source indexed at commit `a43099ef21e91b75b812e3eb883cb4f3813ab7c7`.

## FLY-DIAMOND-NEXUS

**What exists.** Three related browser labs: reward-map planning; a larger TensorFlow.js neural/evolution sandbox; and a fly-inspired network. The nested [`DIAMOND-SIM-FLY/README.md`](https://github.com/kai9987kai/FLY-DIAMOND-NEXUS/blob/main/DIAMOND-SIM-FLY/README.md) is newer than the root README: 22 modules, changing weather/resources, per-agent memory and a bounded local Supermix advice interface. Root documentation still describes 16 modules. The expanded network's added modules are finite engineered heuristics, not imported connectome synapses.

**Source check.** [`worldlab-experiments.js`](https://github.com/kai9987kai/FLY-DIAMOND-NEXUS/blob/main/DIAMOND-SIM-FLY/src/worldlab-experiments.js) validates distinct seed blocks, explicitly assigns comparison planners, reports raw metrics and resamples at seed level using a separate RNG. It distinguishes inconclusive results from gains.

**Carry forward.** Separate legacy and current mechanisms, retain simpler baselines, and audit whether a sophisticated component is actually on the decision path.

**Boundary.** The README reports that a single Antennal Lobe controller can outperform the 16-module bundle; extra modules are not evidence of extra capability. The standalone spiking circuit is not used by the interactive app. Network advice cannot be reproduced from a seed alone. Source indexed at commit `0c8d4100b21d8889bacdef1a9c6dfc20b3424242`. Initial root `src/worldlab-experiments.js` fetch returned 404; the nested path succeeded.

## QuantumBot

**What exists.** NumPy-based classical simulation of small variational quantum policy circuits, population evolution, multiple classical baselines, batched evaluation, noise models and causal communication diagnostics. The project reports that a shallow unentangled circuit is strongest in its measured default configuration and ties a linear policy rather than demonstrating quantum advantage.

**Source check.** [`quantumbot/metrics.py`](https://github.com/kai9987kai/QuantumBot/blob/main/quantumbot/metrics.py) distinguishes messages correlated with the sender's state from a receiver causally using messages. It implements histogram mutual information with shuffled-label correction and describes matched mute/shuffle listening interventions.

**Carry forward.** A component must change downstream behaviour beneficially to earn its cost. Test no-component, shuffled-component and simple-controller alternatives. Neutral initialization matters: implementation shortcuts can grant an accidental baseline advantage.

**Boundary.** The README's performance ratios, Qiskit verification and 500-plus tests are project reports, not rerun here. No hardware quantum advantage follows from efficiently simulated 2–6-qubit circuits. Source indexed at commit `42e4fd637da2df1da5241da484ebc2c625050e72`.

## Causeway

**What exists.** A local evidence-to-experiment workbench with a synthetic 12-grower watershed, four policy packages, four assumption lenses, source notes and reproducible receipts. It already covers evidence mapping and paired policy comparison.

**Source check.** [`src/model.js`](https://github.com/kai9987kai/Causeway/blob/main/src/model.js) exposes parameters, fixed grower types, policy and stress configurations, and an event-keyed draw function using seed/week/actor/channel. Rain, heat and practice choices use independent event identities so branching need not shift the entire random stream.

**Carry forward.** Match comparable exogenous events by identity; make assumptions editable and preserve them with each receipt.

**Boundary.** The source-note library does not calibrate model equations. The watershed is illustrative; no field observations or validated policy forecasts are bundled. The latest commit returned by the connector was `e25ea9e6a5a70f60f5a6ee36756aceb3c6c9baac` (security policy); this is discovery metadata, not a claim that every source fetch was pinned to it.

## MOLT

**What exists.** A compact memory-location comparison: head-locked versus distributed cue traces, tissue loss/regrowth, training controls, cue reversal and a shared food pool. It makes one mechanism easy to inspect.

**Source check.** [`src/engine.js`](https://github.com/kai9987kai/MOLT/blob/main/src/engine.js) precomputes schedules, cohort orders and noise; balances unpaired training within each cue; assigns traces to head or body carriers; and implements head replacement as blank cells. The surviving distributed trace advantage under head removal follows partly from the chosen carrier placement.

**Carry forward.** Include null/unpaired training and reversal controls. Preserve all condition-defining random schedules.

**Boundary.** Its published 42.5-point choice difference is a toy-model reference result, not biological evidence. Exports are aggregate seed/arm data rather than full event histories. The short FNV protocol ID is not a cryptographic integrity proof. Latest returned commit: `8ac04b1839b82d4e4d83166f1938bc6e1150197a`.

## Memory Carrier Observatory

**What exists.** Four synthetic carriers crossed with six transfer contexts, then all 16 carrier-removal subsets. The Interaction Atlas decomposes outcomes through fourth-order inclusion–exclusion terms and shows leave-one-pair-out sensitivity.

**Source check.** [`src/engine.js`](https://github.com/kai9987kai/MEMORY-CARRIER-OBSERVATORY/blob/main/src/engine.js) uses fixed channel weights and saturating hand-set trace accuracy, a shared group trace, and a weighted decision vote. Transfer removes/reverses channels. The source explicitly computes normal-approximation intervals and deterministic leave-one-out means.

**Carry forward.** Measure combinations of mechanisms; useful individual parts may interact destructively. Report sensitivity to individual seed blocks.

**Boundary.** The next-probe hypotheses are fixed and not updated by observations. Ninety nonempty subset/context terms reuse outcomes with no multiplicity adjustment; they are exploratory. This already occupies the full-factorial memory-ablation space. Latest returned commit: `523c10b46fa26acd53cd8468f95d3cbf55011437`.

## Mnemorph

**What exists.** Adaptive memory-mechanism investigation with a typed assay grammar, frozen pre-outcome predictions, withheld intervention scoring, an auditor split and six methods including equal-budget random and frozen-grammar information gain. Its specific research question is whether grammar revision improves on active selection with a fixed grammar.

**Source check.** [`src/core/compiler.js`](https://github.com/kai9987kai/Mnemorph/blob/main/src/core/compiler.js) bounds candidate/template counts, validates public JSON, rejects known hidden-label keys, validates typed programs and computes expected information gain from posterior predictions. These are real selection mechanisms; forbidden-key checks alone do not prove secrecy.

**Carry forward.** Freeze predictions before outcomes and score on withheld interventions. Account for search budget as well as experiment budget.

**Boundary.** The repository calls itself a V0 workbench with a V1/V2 scaffold; its smoke run is not confirmation. Public snapshots expose wiring that may allow source-informed label inference. An experiment-selector project alone would substantially duplicate this work. Source indexed at commit `4fc3353b4aa4ea3e2c7b24798121ee65deda6939`.

## NEUROGRAFT

**What exists.** Provenance-preserving sparse graph modules, recurrent graph encoders, learned cross-source routing, graph controls, a frozen-language interface and a live navigation workspace. Current v0.12 also contains successor-representation planning, Laplacian features and reverse Bellman replay over experienced transitions.

**Source check.** [`neurograft/dynamics.py`](https://github.com/kai9987kai/NEUROGRAFT/blob/main/neurograft/dynamics.py) stores observed source graphs separately from learned routing. Sparse relation messages are normalized by absolute incoming weight and aggregated without dense adjacency. Config validation explicitly selects human-only or residual readout. [`docs/v12-build-report.md`](https://github.com/kai9987kai/NEUROGRAFT/blob/main/docs/v12-build-report.md) explains the SR equation and reports local mathematical/regression checks; these were not rerun here.

**Carry forward.** Preserve source identity; keep measured data separate from artificial coupling; distinguish a tested interface from trained capability; evaluate controls that remove effective information rather than merely equalizing parameter count.

**Boundary.** Included fly/human graphs are fixtures; pretrained Qwen capability was not demonstrated by tiny random-model tests. The reported five-seed synthetic delayed-cue experiment has wide uncertainty and no reliable topology advantage. Several named live mechanisms are telemetry or engineering analogies rather than optimized policy inputs. Planning/replay would duplicate existing v0.12 work. Latest returned commit: `2301f0af16a92a9722608c868e4719f1898ca0fe`.

## Cross-project opportunity

The strongest recurring problem is deciding which mechanism deserves to remain active. Memory retention can be harmful after reversal; communication may be present but ignored; deeper quantum circuits can underperform shallow ones; more coupled neural modules can lose to one simple controller. Meanwhile experiment selection, graph grafting, memory interventions, synthetic ecology and provenance ledgers already have dedicated projects.

A distinct candidate is a bounded mechanism-selection laboratory: learn when a costly predictor, memory, specialist or verification step changes the decision enough to justify its cost; detect when its value disappears after a shift; and compare selective use against always-on, always-off, random and equal-budget alternatives. Central outcomes should be decision loss and compute cost, with paired held-out shifts, stale/shuffled signals, false activation and missed-benefit rates. This is an engineering/research direction inferred from the review, not a claim of global scientific novelty or a completed system.

No access failure prevented reviewing these nine repositories. Two guessed source paths returned 404 and were resolved through source search. All sources above are conceptual references; no code or weights were incorporated into the new project during this review.
