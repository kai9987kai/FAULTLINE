# FAULTLINE: joint-failure laboratory

Design decision, 24 October 2026. The user authorised choosing the direction and building through testing. Platform choice: CPU-local Python 3.12 standard library, a browser interface, no model downloads or paid APIs.

## Research question

Under equal component-call and calibration budgets, when does selecting an ensemble using complete joint-failure observations reduce held-out worst-condition error compared with individual accuracy, pairwise co-failure, or pooled ensemble error? When does it fail under unobserved common causes?

The proposed contribution is a small, inspectable experimental instrument and a portfolio integration boundary. Ensemble selection, robust optimisation, fault injection, and dependent failures are established ideas; global novelty or a breakthrough is not claimed.

## Alternatives considered

1. Another adaptive memory or program-sharing engine: substantial overlap with Mnemorph, TESSERA, Poseidon, and NEUROGRAFT.
2. A general orchestration layer: overlap with NexusFlow and Odysseus, with weak evidence of incremental capability.
3. Joint-failure panel synthesis: chosen because it measures a missing prerequisite for combining the portfolio's components and can be falsified at a fixed budget.

## Executable mechanism

Each labelled case records all binary component predictions and a stress-condition identifier. A failure signature is the complete set of wrong components on that case, forming an empirical hyperedge. Enumerate all odd panels of a specified size and compare four deterministic selectors:

- `accuracy`: minimum sum of pooled individual error rates.
- `pairwise`: minimum worst-condition second factorial-moment upper bound on majority error, then pooled bound, then pooled individual error. For threshold t=(k+1)/2, the unclipped score is sum of pair co-failure rates / choose(t,2). k=1 reduces to individual error.
- `pooled`: minimum pooled observed majority error, then worst-condition error.
- `joint`: minimum worst-condition observed majority error, then pooled error.

Every selector sees exactly the same calibration rows and candidates. Ties use component IDs in lexical order. Test rows are evaluated only after a panel is frozen; selection takes calibration data only. Panel size and component calls are reported. Calibration collection queries every component; this cost is separate from deployment calls. Search cost is panel-row evaluations, not FLOPs.

## Controls and falsification

Use deterministic event-keyed synthetic binary sensor specialists, overlapping channel dependencies, and explicit independent-error, shared-channel, composed-fault, and unseen-common-cause conditions. Retain poor outcomes. Use fresh test events and paired seeds across policies. Include the exact three-bit even/odd parity example: both distributions have identical marginal and pairwise co-failure rates but majority error 3/4 versus 1/4. This proves the limits of pairwise summaries, not learned generalisation.

Primary development pilot: 24 consecutive seeds beginning 4100, panel size 3, 64 cases per condition. Report mean paired differences and descriptive seed-bootstrap intervals; these are not sequential/conformal guarantees. A separate 24-seed confirmation beginning 9100 is evaluated once after implementation is frozen; report separately. No tuning after viewing confirmation.

## Data and module interfaces

JSON schema `faultline-dataset-v1`: `name` string; `components` list of `{id,name,family}`; `calibration` and `test` nonempty lists of `{id,condition,truth,predictions}`. Predictions are lists of integers 0/1 aligned with components. Case IDs globally unique, component IDs unique, 3..12 components; at most 12000 total rows. Metadata is optional. No executable imports. All supplied rows must be finite and structurally valid. Reject overlapping IDs, unknown schema, missing labels, booleans as bits, and ragged predictions.

`faultline.core.validate_dataset(data) -> dict` validates and returns input.
`faultline.core.select_panel(components, calibration, size, policy) -> tuple[int,...]` has no test argument.
`faultline.core.metrics(rows, panel) -> dict` returns `n,error,worst_group_error,unanimous_wrong_rate,groups` where groups are `{condition,n,error}`.
`faultline.core.analyze(data, size=3) -> dict` returns `dataset,components,n_calibration,n_test,panel_size,candidate_panels,policies,cofailure,costs`. Each policy is `{id,label,panel,calibration,test,witnesses}`; `panel` contains IDs, witnesses up to 8 test failures `{id,condition,truth,vote,wrong_components}`. `cofailure` has `matrix` of pair co-failure rates, `signatures` list `{members,count,rate}` from calibration only. All outputs JSON serialisable and deterministic.
`faultline.fixtures.make_dataset(seed=4100,cases=64,scenario='shared') -> dict`; scenarios `shared,independent,shift`.
`faultline.fixtures.parity_demo() -> dict` returns `even,odd`, each containing `marginals,pairwise,majority_error,patterns`.
`faultline.study.run_study(seeds,cases=64,size=3,scenario='shared') -> dict` uses analyze, outputs per-seed results and aggregate per-policy errors and paired differences vs joint. Seeds bounded to 1..64, cases 16..256.
`faultline.receipts.make_receipt(kind,config,result,input_data=None) -> dict`, `verify_receipt(receipt) -> dict`: SHA-256 canonical payload plus source identity; verifier recomputes results, checks source and data identity, and rejects edited/rehashed false results. Hash integrity alone is not verification.

HTTP interface: GET `/api/demo?seed=4100&cases=64&scenario=shared&size=3` -> receipt with result; GET `/api/parity` -> parity demo; GET `/api/study?seed=4100&replicates=8&cases=64&scenario=shared&size=3` -> study receipt; POST `/api/analyze` `{dataset,size}` -> data-bound analysis receipt; POST `/api/verify` receipt -> `{valid,reason}`. Health `/api/health`. Strict local server, bounded body size, explicit errors. Browser controls with loading/errors, dataset import, receipt export and replay, comparison chart, co-failure view and exact parity control. An experiment result must never be silently replaced with fixture data after import failure.

CLI: `python -m faultline demo`, `study`, `analyze PATH`, `verify PATH`, `serve --port 8786`; output JSON through `--out`. Windows launcher opens browser and runs loopback server. Tests use unittest. Docs include all 26 repository reviews, research rationale, protocol, limits, and recorded local results.

## Boundaries

Synthetic binary sensor errors do not establish LLM reasoning, biological cognition, or deployment reliability. Empirical hyperedges reveal joint failures, not causal identification. Imported data rely on its producer's label quality and split hygiene; ID disjointness cannot detect semantic duplicates. Exhaustive selection is deliberately capped at 12 components. No unattended network actions, hardware interference, or code execution from imported files. Reviewed projects are sources of design lessons; no claim that their runtimes are integrated or their licences grant unrestricted reuse.
