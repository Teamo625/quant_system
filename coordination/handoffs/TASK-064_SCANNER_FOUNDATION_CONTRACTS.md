# TASK-064 Scanner Foundation Contracts

## Role

5.3 execution window.

## Context

The 5.5 Controller closed TASK-063 after accepted Review Agent verification. Phase 3 FeatureHub is complete under `coordination/PHASE_GATE.md`, and Phase 4 Scanner is now open.

This is the first Phase 4 task. Keep it narrow: establish Scanner contract primitives and offline validation only. Do not implement stock-picking logic, ranking algorithms, strategies, backtests, signals, risk, portfolio logic, notification, AI reports, UI, automated trading, scheduling, or live data access.

## Objective

Create a minimal Scanner foundation contract layer that can later support universe definition, feature-based screening, candidate-list outputs, and scan artifact persistence without crossing into ranking or trading logic.

## Allowed Files

You may modify only:

- `quant/scanner/README.md`
- `quant/scanner/__init__.py`
- `quant/scanner/contracts.py`
- `tests/scanner/__init__.py`
- `tests/scanner/test_contracts.py`
- `coordination/reports/TASK-064_REPORT.md`

If a listed file does not exist, create it.

## Required Scope

Implement pure offline Scanner contracts and validation helpers for:

- universe identity and membership inputs
- scanner feature inputs that reference existing FeatureHub output identifiers without reading FeatureHub storage
- filter/condition specifications as declarative data only
- scan candidate output records
- scan run metadata and candidate-list containers

The contracts should be deterministic, typed, and easy for later tasks to consume.

Validation should cover basic contract integrity such as:

- required string fields are non-empty
- trade dates use the existing project date-string conventions
- candidate records have stable symbol/date/run identifiers
- feature references are declarative and do not fetch data
- filter specs reject unsupported operators or malformed thresholds

## Explicit Non-Goals

Do not:

- implement scanner ranking, scoring, sorting beyond deterministic container validation, or stock-picking decisions
- implement strategy, backtest, signal, risk, portfolio, notification, AI, UI, or automated trading logic
- read DataHub warehouse files or FeatureHub persisted files
- add or modify DataHub or FeatureHub implementation
- add live-network tests or real source calls
- modify controller-owned coordination state files

## Testing

Allowed tests:

- `python3 -m unittest discover -s tests/scanner -p 'test_*.py'`
- `python3 -m unittest discover -s tests/features -p 'test_*.py'`

Default tests must remain offline-safe. Live tests are forbidden for this task.

## Completion Report

Write `coordination/reports/TASK-064_REPORT.md` with:

- files changed
- tests run
- default network behavior
- live-enabled result, which should be `SKIP / not run; live tests forbidden by handoff`
- deviations from this handoff
- risks or follow-up tasks

