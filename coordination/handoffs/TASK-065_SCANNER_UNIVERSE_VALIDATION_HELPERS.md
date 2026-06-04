# TASK-065 Scanner Universe Validation Helpers

## Role

5.3 execution window.

## Context

TASK-064 established pure offline Scanner foundation contracts. Phase 4 Scanner remains open, but implementation must stay narrow and must not introduce ranking, screening execution, strategies, backtests, signals, risk, portfolio logic, notification, AI reports, UI, automated trading, scheduling, live data access, DataHub warehouse reads, FeatureHub persisted-file reads, or persistence.

This task extends the Scanner foundation with deterministic universe definition and universe snapshot validation helpers only.

## Objective

Add pure offline helpers that validate and normalize caller-provided universe definitions and membership snapshots so later Scanner work can safely consume them.

## Allowed Files

You may modify only:

- `quant/scanner/README.md`
- `quant/scanner/__init__.py`
- `quant/scanner/contracts.py`
- `quant/scanner/universe.py`
- `tests/scanner/__init__.py`
- `tests/scanner/test_contracts.py`
- `tests/scanner/test_universe.py`
- `coordination/reports/TASK-065_REPORT.md`

If a listed file does not exist, create it.

## Required Scope

Implement pure offline universe helpers for:

- universe definition records, including universe id, display name, market, source, and optional description
- normalized universe membership snapshots built from caller-provided symbols
- validation that required text fields are non-empty
- validation that dates follow existing ISO date-string conventions
- validation that symbol lists are non-empty, unique, and deterministically ordered after normalization
- validation that membership snapshots align with their universe definition

The helpers may reuse TASK-064 contract types and validation functions.

## Explicit Non-Goals

Do not:

- implement screening execution, ranking, scoring, sorting candidates, or stock-picking decisions
- implement strategy, backtest, signal, risk, portfolio, notification, AI, UI, automated trading, or scheduling logic
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

Write `coordination/reports/TASK-065_REPORT.md` with:

- files changed
- tests run
- default network behavior
- live-enabled result, which should be `SKIP / not run; live tests forbidden by handoff`
- deviations from this handoff
- risks or follow-up tasks
