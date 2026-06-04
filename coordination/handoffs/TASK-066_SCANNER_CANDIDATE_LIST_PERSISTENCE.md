# TASK-066 Scanner Candidate-List Persistence

## Role

5.3 execution window.

## Context

TASK-064 established Scanner foundation contracts. TASK-065 added pure offline universe definition and membership snapshot validation helpers.

This task adds local persistence for already-built `ScanCandidateList` artifacts only. It must not implement screening execution, ranking, scoring, sorting candidates beyond validating the existing deterministic contract, stock-picking decisions, strategies, backtests, signals, risk, portfolio logic, notification, AI reports, UI, automated trading, scheduling, live data access, DataHub warehouse reads, or FeatureHub persisted-file reads.

## Objective

Add a minimal, deterministic, pure local persistence helper for Scanner candidate-list artifacts so later tasks can write scan outputs safely.

## Allowed Files

You may modify only:

- `quant/scanner/README.md`
- `quant/scanner/__init__.py`
- `quant/scanner/storage.py`
- `tests/scanner/__init__.py`
- `tests/scanner/test_storage.py`
- `coordination/reports/TASK-066_REPORT.md`

If a listed file does not exist, create it.

## Required Scope

Implement pure local Scanner artifact persistence for caller-provided `ScanCandidateList` values:

- write candidate rows as JSONL
- write a compact manifest JSON with run metadata, schema version, feature references, filters, candidate count, and deterministic content checksum
- preflight path conflicts before writing so an invalid manifest/records path does not partially overwrite the other artifact
- support `overwrite=False` by default and reject existing output paths
- validate the candidate list with existing Scanner contract validation before writing
- serialize datetimes as ISO strings and enum values as their string values

## Explicit Non-Goals

Do not:

- implement screening execution, ranking, scoring, sorting candidates, or stock-picking decisions
- implement strategy, backtest, signal, risk, portfolio, notification, AI, UI, automated trading, or scheduling logic
- read DataHub warehouse files or FeatureHub persisted files
- add or modify DataHub or FeatureHub implementation
- add live-network tests or real source calls
- implement broad orchestration, refresh runners, or scan scheduling
- modify controller-owned coordination state files

## Testing

Allowed tests:

- `python3 -m unittest discover -s tests/scanner -p 'test_*.py'`
- `python3 -m unittest discover -s tests/features -p 'test_*.py'`

Default tests must remain offline-safe. Live tests are forbidden for this task.

## Completion Report

Write `coordination/reports/TASK-066_REPORT.md` with:

- files changed
- tests run
- default network behavior
- live-enabled result, which should be `SKIP / not run; live tests forbidden by handoff`
- deviations from this handoff
- risks or follow-up tasks
