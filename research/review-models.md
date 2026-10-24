# Live review: search, model grafts, and synthetic memory research

Reviewed 24 October 2026. Scope: nine supplied repositories, their default-branch README files, repository metadata and representative source excerpts. No upstream code or model weights were executed. Reported experimental numbers below are the repositories' own results, not independent reproductions. File presence, readable source and a README claim are different evidence levels. This is an architecture and evidence review, not a complete correctness/security audit.

## Main finding

This portfolio already contains model grafting, cellular memory, causal transplantation, online statistical audits, connectome nulls, exact search, synthetic navigation and replay receipts. The strongest inheritance is its experimental discipline. A new project should make a specific intervention change an independently measured decision under a controlled budget. Adding another memory module, graph name or self-improvement ledger would repeat existing work.

One concrete documentation drift was found: Supermix's README advertises conformal guarantees and FLOP savings while its current stopping implementation explicitly returns no certified risk bound and describes heuristic budget advice. A new system should derive claims from executable measurements and preserve the distinction between a mechanism's name and its actual contract.

## 1. NexusSearch

- **Inspected:** [README](https://github.com/kai9987kai/NexusSearch/blob/main/README.md), [active search source, lines 1–130](https://github.com/kai9987kai/NexusSearch/blob/main/src/engine/nx_search.c), metadata and source directories. Default branch `main`; HEAD `538edcba595889090946a51ce03f72ac9fb72202`.
- **Architecture:** C11 immutable JSON-document snapshots, exact integer filtering, BM25 text ranking, exhaustive cosine search and deterministic reciprocal-rank fusion. CLI, Python ctypes, local HTTP/browser and experimental stdio tool interfaces share the engine. Source confirms a bounded search arena, work accounting, typed query plans and explicit error returns.
- **Evidence boundary:** README clearly separates active snapshot paths from standalone postings, ANN/quantization, WAL and merge experiments. Having those modules does not make active search approximate or transactional. No embeddings are produced internally. Checked portions support bounded query processing; no benchmark was reproduced here.
- **Lesson to retain:** preserve an exact reference implementation, immutable inputs and stable tie-breaking; make acceleration measurable against that reference. Exact retrieval provides a useful small-scale evidence index without requiring an LLM.
- **Avoid importing as a claim:** performance, ANN recall, durability or portability beyond independently tested configurations.

## 2. Prometheus-alpha

- **Inspected:** [README](https://github.com/kai9987kai/prometheus-alpha/blob/claude/epic-tesla-l7brlx/README.md), [cell dynamics](https://github.com/kai9987kai/prometheus-alpha/blob/claude/epic-tesla-l7brlx/src/prometheus/tissue.py). Default branch `claude/epic-tesla-l7brlx`; HEAD `417009e5548453338761732152b7b8ec30ffa79a`.
- **Architecture:** one-dimensional neural cellular automaton: 40 sites, 16 channels, shared two-layer cell rule, local gradient/Laplacian perception, asynchronous firing and fixed gap-junction voltage diffusion. Cue inputs and behavioral readout are gated by synthetic head tissue. The rule is frozen during each life; within-life learning therefore changes state. The source confirms zero-initialized output weights and head-gated cue access.
- **Research contribution already covered:** paired/unpaired conditioning, decapitation and regeneration, state transplantation, sparse compiled memories, repeated injury, turnover/noise stresses, independently trained encoding systems. README reports highly decodable state that the regenerated head fails to use, and incompatible private codes across rules.
- **Lesson to retain:** decodability is not causal utility. A representation must change held-out behavior when appropriately transplanted or erased; matched timing/noise controls matter. Separate generalization from training on the actual stress condition.
- **Boundary:** synthetic finite-body experiments; no biological-memory or general-transfer conclusion. Reported preregistered prediction counts were not audited end-to-end here. A dated biology preprint linked from the README was not independently verified in this review.

## 3. Morpheus

- **Inspected:** [README](https://github.com/kai9987kai/morpheus/blob/claude/zealous-euler-y2xqul/README.md), [audited improvement loop, lines 1–130](https://github.com/kai9987kai/morpheus/blob/claude/zealous-euler-y2xqul/src/morpheus/rsi.py). Default branch `claude/zealous-euler-y2xqul`; HEAD `5db6f98d605b80245ed9ff5e2cc9d42151830a14`.
- **Architecture:** 2D neural cellular tissue with a learned cell rule, explicit voltage diffusion, cell-local forward predictions and comparator feedback. NumPy backpropagation and a browser engine support synthetic anatomy experiments. The improvement loop proposes practice, parameter mutations and physics changes.
- **What the source actually adds:** naive reused-suite acceptance, fresh paired evaluations under LORD++, and sequential betting e-process evaluation under e-LOND, with a frozen anti-forgetting anchor and separate auditor suite. It distinguishes believed improvement from auditor-measured improvement. The inspected source clips paired differences to a fixed bound for the betting process, so any statistical interpretation must respect the bounded estimand and protocol assumptions.
- **Lesson to retain:** evaluate adaptive proposals on fresh evidence; report overestimation and sample cost alongside gain. Existing online FDR/e-process machinery means an additional generic self-audit project would have weak portfolio novelty.
- **Boundary:** anatomical programs and self-models refer to this simulator. README says later compiled second heads mostly do not survive a further amputation; temporary anatomy is not durable target-memory rewriting. Author claims of global novelty need a separate literature search.

## 4. Supermix-Expanse-v2

- **Inspected:** [README](https://github.com/kai9987kai/Supermix-Expanse-v2/blob/main/README.md), [latent consolidation source, lines 1–160](https://github.com/kai9987kai/Supermix-Expanse-v2/blob/main/expanse/src/consolidation_v2.py). Default `main`; HEAD `33e38a279c86bccdb1e5680f15f193d61a3f71cb`.
- **Architecture:** Expanse trunk plus per-token residual latent-MoE blocks, zero-initialized output gates and a heterogeneous teacher-fusion bank discarded after training. Source confirms shared-space projection, configurable latent experts/memory slots and a teacher-free final phase. Later repository documentation contains a connectome experiment matrix and an input-evoked readout that subtracts a zero-input response to remove a constant-bias shortcut.
- **Results worth carrying forward:** README says the v2 consolidation blocks contributed almost none of the observed gain when zeroed; additional training explained it. Matched connectome training found no measurable superiority of real wiring over a degree-preserving shuffle under that protocol. Dynamic gates helped, largely as adapters. Later stricter receipt checks make a historical dynamic-gate result inconclusive because cohort hashes were missing asymmetrically; the document preserves both statuses.
- **Lesson to retain:** subtract nuisance responses, budget-match controls, test whether a new module actually mediates gains, and do not silently upgrade historical evidence after protocol changes. Tests of a trained model's dependency on a graph are weaker than matched-training tests of that graph's superiority.
- **Boundary:** weak code/biomedical generation remains acknowledged; small pilots are not promotion. Different split seeds can contaminate apparent comparisons. Composite model/data licensing differs from code licensing.

## 5. GhostInTheMachine

- **Inspected:** [README](https://github.com/kai9987kai/GhostInTheMachine/blob/main/README.md), [v7 engine, lines 1–160](https://github.com/kai9987kai/GhostInTheMachine/blob/main/src/ghost_v7/engine.py), v7 entry point. Default `main`; HEAD `239f5de6452f78f3960de07c393268eeac142d03`.
- **Architecture:** seeded recurrent populations coupled to a latent world, learned forward models, own/yoked actions and a comparator mismatch signal. v7 decomposes mismatch into a ridge-predictable component and a residual innovation; either can be replayed or shifted while the other stays live. Separate random streams support matched interventions.
- **Research contribution already covered:** prediction-error ownership and temporal alignment; transplanting and desynchronizing streams; independent sample replication; claims ledger retaining retractions. README reports a replicated persistence effect while explicitly downgrading causal emergence and retracting a detector-induced earlier event.
- **Lesson to retain:** signal magnitude is insufficient as a control; temporal relationship to the receiver can be the causal variable. Preserve negative results and retractions in the same display as successful claims.
- **Boundary:** no measurement or proof of consciousness. Reported 360-network meta-analysis is a repository result, not independently reproduced here. A comparator targeting a named population does not make that population intrinsically special.

## 6. Supermix-expanse

- **Inspected:** [README](https://github.com/kai9987kai/Supermix-expanse/blob/main/README.md), [connectome core, lines 1–160](https://github.com/kai9987kai/Supermix-expanse/blob/main/expanse/src/connectome_full.py). Default `main`; HEAD `3fd091e9cc3387b2c17da5ce7514831d77e2af44`.
- **Architecture:** Archimedes language trunk with donor expert grafts, frozen Omni branch, FlyCore and a fixed type-level male-CNS graph. Source implements per-token recurrent graph processing; columns do not mix. Fixed edge structure, learned gains/bias/leak and projections, zero-gated residual writes and sparse CSR kernels are distinct parts of the method.
- **Evidence:** README reports useful distillation, but negligible contribution from donor experts and FlyCore; code pass rate remains zero in its listed evaluation. Inference removal or rewiring degrades the trained graph branch, yet the README correctly states that matched training on a shuffled graph is needed before concluding biological wiring trains better. The v2 repository later carries that stronger null comparison.
- **Lesson to retain:** measure transfer in task outputs, not representation similarity or lower teacher-forced loss alone. Compare a donor transplant with additional-training and random/rewired controls.
- **Boundary:** type aggregation is not a whole individual-neuron simulation. Linear-part contraction comments do not establish global learned nonlinear stability. Composite derived-weight terms include BioMedLM/OpenRAIL restrictions; do not assume MIT code licenses cover all model artifacts.

## 7. supermix-archimedes

- **Inspected:** [README](https://github.com/kai9987kai/supermix-archimedes/blob/main/README.md), [core source, lines 1–130](https://github.com/kai9987kai/supermix-archimedes/blob/main/archimedes/src/archimedes_core.py). Default `main`; HEAD `1952cf1c92cb506fff60f9ee0c055c2365988e5e`.
- **Architecture:** a 320-dimensional Supermix trunk with 256-dimensional donor experts lifted through fitted representation maps, dormant routing slots, a PyTorch FlyCore port, 22 added connectome nodes, and separate Omni encoders for classification and native 64×64 imagery. Zero gates and gradual activation seek to preserve the base function at attachment time.
- **Lesson to retain:** incompatible models need explicit interfaces; separate encoders and fitted maps are more defensible than arbitrary weight averaging. Store the donor/run identity and test zero-gate equivalence. Display true output resolution and unknown class semantics rather than cosmetic upscaling or invented labels.
- **Boundary:** preserving the initial function does not demonstrate useful transfer after learning. Expanse's later documentation identifies a future-token averaging issue in the earlier FlyCore sensing path, illustrating why sequence causality needs a direct test. This review did not execute or independently locate that older bug in the inspected excerpt.

## 8. Supermix

- **Inspected:** [README](https://github.com/kai9987kai/Supermix/blob/main/README.md), [current stopping controller](https://github.com/kai9987kai/Supermix/blob/main/source/nexus_conformal_stopping.py). Default `main`; HEAD `6ea1c2cc41e3705b4b899b764a001cec180d155d`.
- **Architecture:** broad working monorepo: model training, local runtime, packaging, experimental math/reasoning tools and diagnostics. README includes several architectural claims alongside detailed training-measurement retrospectives. Full monorepo audit is outside this bounded review.
- **Confirmed discrepancy:** README v90 says its conformal early exit guarantees error risk and saves 30–60% FLOPs. The current inspected controller says unlabeled margins cannot identify error rates, calculates only an empirical margin quantile, returns `certified_risk_bound=None` and `risk_certified=False`, and labels savings as potential step-budget fraction rather than measured FLOPs. The code's explicit weaker contract should govern downstream claims.
- **Lesson to retain:** bind public claims to the exact active implementation. The v85 retrospective also documents token caps truncating answers, benchmark generators changing while weights stayed fixed, task exposure dilution, and an incorrect memorization corpus. Fingerprint the evaluator, freeze comparable tasks and separate software readiness from trained performance.
- **Boundary:** module labels such as diffusion, causal reasoning or conformal do not independently establish those methods' statistical or computational properties. Only the stopping path was source-reviewed here; no blanket assessment of other modules is implied.

## 9. Supermix-Poseidon

- **Inspected:** [README](https://github.com/kai9987kai/Supermix-Poseidon/blob/main/README.md), [MNEMOSYNE source, lines 1–160](https://github.com/kai9987kai/Supermix-Poseidon/blob/main/poseidon/mnemosyne.py). Default `main`; HEAD `72d42218ae92cee5c9668a090f9d31d8d9961681`.
- **Architecture:** frozen trained Tidal policy with optional trained predictor artifact, one-step planning, recurrent working memory, episodic retrieval, spatial resource estimates, residual adaptation and a synthetic partially observed world. Source confirms a GRU cell and bounded episodic buffer, similarity/reward/surprise/recency weighting, and erased, shifted and random-retrieval interventions.
- **Evidence discipline:** README separates source identity from release, optional artifacts from the default policy, candidate preparation from promotion and uncalibrated uncertainty from a survival certificate. The memory source's buffer eviction is oldest-first even though a comment mentions low-value eviction; value weighting acts in retrieval in the inspected section.
- **Lesson to retain:** observe whether memory changes decisions and compare with a matched simple recurrent baseline. Explicit support checks, fallback behavior and exact decision replay are reusable contracts. A new project should avoid merely reassembling another predictor-memory-planner stack.
- **Boundary:** learned incremental memory value remains an open research goal in the README. Synthetic resource estimates and graph telemetry do not imply real-world safety, biology or autonomous discovery. Extra mathematical and named subsystems have individual status, not a collective capability certificate.

## Synthesis for the new project

1. **Retain:** exact baselines; event-keyed pairing; typed interfaces; zero-effect attachment controls; private audits; published negative results; source/evaluator identity; finite budgets and replay.
2. **Differentiate:** a new research question should quantify when an existing component remains useful after a change in its environment, observation interface or context, and how much evidence is worth buying before acting. The useful output is a decision and its tested validity region, rather than another module catalogue.
3. **Test the mechanism:** compare against static reuse, reset/relearn, simple caching, random evidence allocation and an oracle bound where meaningful. Ablate the proposed mechanism under the same sample/action budget.
4. **Control claims:** distinguish observed evidence from a theoretical guarantee. A digital receipt authenticates a computation's identity, not the truth of its assumptions or biological meaning.

## Access and review limitations

All nine repositories were readable with the GitHub connector. Fetching slash-containing branch names through the branch endpoint failed for Morpheus and Prometheus; listing their latest default-branch commit resolved both HEADs. README and source reads used the repository default branch, avoiding an assumed `main`. A head snapshot was recorded after the file reads; no commits were written and no downloaded code was run. Scope is intentionally representative, so uninspected files or tests may contain further controls, limitations or defects.
