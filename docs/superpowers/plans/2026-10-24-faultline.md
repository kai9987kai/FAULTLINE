# FAULTLINE Implementation Plan

> **For agentic workers:** Use test-first implementation with independent final review. The user explicitly delegated direction and execution; no further design approval is pending.

**Goal:** Build a reproducible local joint-failure ensemble selection lab.
**Architecture:** Pure deterministic core, synthetic fixtures and paired study runner, source-bound replay receipts, loopback API and browser laboratory.
**Tech Stack:** Python 3.12 standard library; HTML/CSS/native JavaScript.
**Spec:** `docs/design.md`.

## Global constraints

- No runtime network, external models, packages, or paid services required.
- Calibration-only selection; frozen held-out evaluation; equal panel size and calibration rows.
- Strict JSON, 3..12 components, at most 12000 rows; event-keyed randomness.
- Four declared selectors and explicit negative controls; no unsupported novelty or generalisation claims.

## Review focus

- Import validation must reject split overlap and ragged/non-binary values.
- Selector output must not change when only test labels change.
- Rehashed fabricated receipts must fail replay; source changes must be distinguished.
- Independent and unseen-common-cause scenarios must retain negative results.
- Browser errors/imports and repeat runs must not present stale data as a new success.

## Task 1: Core selection

- [x] Write failing unittest tests for exact parity-compatible co-failures, panel budget, deterministic ties, invalid datasets, and test-label isolation.
- [x] Implement `faultline/core.py` following design interfaces, with all four selectors.
- [x] Run `python -m unittest discover -s tests -v`; inspect core tests and review selection assumptions.

## Task 2: Experimental fixtures and study

- [x] Write failing tests for exact parity identity, deterministic event-keyed fixtures, separate cases, and paired study aggregation.
- [x] Implement `faultline/fixtures.py` and `faultline/study.py`.
- [x] Verify exact replay and run development/independent/shift studies before frozen confirmation.

## Task 3: Receipts, API, CLI and interface

- [x] Write failing tests for hash tampering, rehashed fabricated metrics, source mismatch, bounded HTTP inputs and CLI round-trip.
- [x] Implement `faultline/receipts.py`, `server.py`, `__main__.py`; native browser files under `web/`.
- [x] Verify automated tests, launch and exercise browser run, import, export and replay.

## Task 4: Review and evidence

- [x] Compile 26-source index plus current primary research, complete operational README and paper.
- [x] Independently review implementation and methodology, repair material findings with regression tests.
- [x] Run full suite and source-frozen confirmation; record accurate results and limits; package local release and launch verified application.
