# TASK-067 Scanner Filter Matching Primitives

## Role

5.3 execution window.

## Context

TASK-064 established Scanner foundation contracts. TASK-065 added universe validation helpers. TASK-066 added pure local persistence for already-built candidate-list artifacts.

This task is the next Phase 4 step and is not part of the current three-task pipeline run. Keep it narrow: implement pure offline filter matching over caller-provided feature values only. Do not implement ranking, scoring, stock-picking decisions, strategy, backtest, signal, risk, portfolio, notification, AI reports, UI, automated trading, scheduling, live data access, DataHub warehouse reads, FeatureHub persisted-file reads, persistence, or broad orchestration.

## Objective

Add deterministic filter matching primitives that can evaluate declarative `FilterSpec` values against caller-provided feature values and report matched filter ids without ranking or candidate selection policy.

## Allowed Files

You may modify only:

- `quant/scanner/README.md`
- `quant/scanner/__init__.py`
- `quant/scanner/matching.py`
- `tests/scanner/__init__.py`
- `tests/scanner/test_matching.py`
- `coordination/reports/TASK-067_REPORT.md`

If a listed file does not exist, create it.

## Required Scope

Implement pure offline matching helpers for:

- caller-provided feature value maps keyed by existing declarative `FeatureReference`
- operator evaluation for existing `FilterOperator` values
- deterministic matched filter id output
- clear validation errors for missing feature values, malformed values, unsupported thresholds, or invalid filter specs

The helpers must not read FeatureHub storage or DataHub storage. They may consume only in-memory caller-provided values and existing Scanner contract objects.

## Explicit Non-Goals

Do not:

- implement ranking, scoring, sorting candidates, stock-picking decisions, or strategy rules
- implement backtest, signal, risk, portfolio, notification, AI, UI, automated trading, or scheduling logic
- read DataHub warehouse files or FeatureHub persisted files
- add or modify DataHub or FeatureHub implementation
- add live-network tests or real source calls
- implement persistence or artifact IO
- modify controller-owned coordination state files

## Testing

Allowed tests:

- `python3 -m unittest discover -s tests/scanner -p 'test_*.py'`
- `python3 -m unittest discover -s tests/features -p 'test_*.py'`

Default tests must remain offline-safe. Live tests are forbidden for this task.

## Completion Report

Write `coordination/reports/TASK-067_REPORT.md` with:

- files changed
- tests run
- default network behavior
- live-enabled result, which should be `SKIP / not run; live tests forbidden by handoff`
- deviations from this handoff
- risks or follow-up tasks
