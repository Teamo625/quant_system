# TASK-068 Scanner Scan Runner Primitives

## Role

5.3 execution window.

## Context

TASK-064 established Scanner foundation contracts. TASK-065 added universe validation helpers. TASK-066 added pure local persistence for already-built candidate-list artifacts. TASK-067 added pure offline filter matching over caller-provided feature values.

This task is the next Phase 4 step. Keep it narrow: implement a deterministic in-memory scan runner that combines caller-provided universe membership, caller-provided feature values, and existing filter matching primitives to produce a `ScanCandidateList`.

Do not implement ranking, scoring, stock-picking decisions, strategy, backtest, signal, risk, portfolio, notification, AI reports, UI, automated trading, scheduling, live data access, DataHub warehouse reads, FeatureHub persisted-file reads, persistence, or broad orchestration.

## Objective

Add pure offline scan execution primitives that can build candidate-list contract objects from already-supplied in-memory scanner inputs.

## Allowed Files

You may modify only:

- `quant/scanner/README.md`
- `quant/scanner/__init__.py`
- `quant/scanner/runner.py`
- `tests/scanner/__init__.py`
- `tests/scanner/test_runner.py`
- `coordination/reports/TASK-068_REPORT.md`

If a listed file does not exist, create it.

## Required Scope

Implement pure offline helpers for:

- accepting an existing universe/membership snapshot or equivalent already-validated scanner universe input
- accepting caller-provided per-symbol feature value maps
- applying existing `FilterSpec` matching primitives from TASK-067
- producing a valid `ScanCandidateList` with deterministic candidate ordering based on the input universe order or an explicitly documented stable order
- recording matched filter ids per candidate
- clear validation errors for missing symbol feature values, malformed runner inputs, duplicate candidate symbols, invalid filters, or invalid output contract objects

The helper must not fetch, read, or refresh any external data. It may consume only in-memory caller-provided values and existing Scanner contract objects/helpers.

## Explicit Non-Goals

Do not:

- implement ranking, scoring, score normalization, priority sorting, stock-picking decisions, or strategy rules
- implement backtest, signal, risk, portfolio, notification, AI, UI, automated trading, or scheduling logic
- read DataHub warehouse files or FeatureHub persisted files
- call DataHub, FeatureHub, source adapters, or live network routes
- add or modify DataHub or FeatureHub implementation
- add live-network tests or real source calls
- implement persistence or artifact IO
- implement broad orchestration, refresh runners, or scan scheduling
- modify controller-owned coordination state files

## Testing

Allowed tests:

- `python3 -m unittest discover -s tests/scanner -p 'test_*.py'`
- `python3 -m unittest discover -s tests/features -p 'test_*.py'`

Default tests must remain offline-safe. Live tests are forbidden for this task.

## Completion Report

Write `coordination/reports/TASK-068_REPORT.md` with:

- files changed
- tests run
- default network behavior
- live-enabled result, which should be `SKIP / not run; live tests forbidden by handoff`
- deviations from this handoff
- risks or follow-up tasks
