# TASK-003: DataHub Local Storage IO

## Task ID

TASK-003

## Owner Role

5.3 execution window

## Status

Ready

## Context

TASK-001 created the minimal DataHub package foundation.

TASK-002 added field-level dataset schema contracts and offline required-field validation:

- `FieldSpec`
- `DatasetSchema`
- `ValidationIssue`
- `DatasetRegistry.get_schema(...)`
- `DatasetRegistry.all_schemas()`
- `DatasetRegistry.validate_required_fields(...)`
- `DatasetRegistry.validate_record(...)`

TASK-002 review and integration accepted the work. The next step is to add a small local storage read/write layer on top of the existing `LocalStorage` path helpers.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/handoffs/TASK-003_DATAHUB_LOCAL_STORAGE_IO.md`

## Goal

Extend DataHub local storage from deterministic path resolution to minimal offline read/write primitives for local dataset records and metadata, without introducing real market data fetching or future-phase logic.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-003_REPORT.md`

## Forbidden Files

The execution window must not modify:

- `coordination/PROJECT_STATE.md`
- `coordination/ROADMAP.md`
- `coordination/TASK_BOARD.md`
- `coordination/DECISIONS.md`
- `coordination/RISKS.md`
- `coordination/INTERFACES.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/reviews/**`
- `coordination/integrations/**`
- `quant/features/**`
- `quant/strategies/**`
- `quant/backtest/**`
- `quant/scanner/**`
- `quant/portfolio/**`
- `quant/notification/**`
- `quant/ai/**`
- `quant/ui/**`

## Implementation Requirements

Implement only DataHub local storage IO foundation.

Minimum expected pieces:

- local write helper for in-memory records to a deterministic local file
- local read helper that returns records from that file
- dependency-free format, preferably JSON Lines, unless the existing codebase already has a better local dependency
- deterministic dataset path behavior using existing `LocalStorage`
- creation of parent directories when writing
- clear behavior for missing files
- optional schema validation before write, using the TASK-002 registry validators
- tests using temporary local directories only
- tests proving round-trip write/read behavior
- tests proving missing-file behavior
- tests proving no source fetching or network access is required

Keep the implementation small. This task is a storage foundation, not a full warehouse engine.

Optional cleanup, if it remains small:

- update the stale `SourceAdapter` docstring that still references TASK-001.

Do not implement:

- real market data downloading
- source-specific adapters
- parquet or database engines unless already available and clearly justified
- technical indicators
- stock selection rules
- strategy logic
- backtest logic
- AI explanation logic
- notification logic
- UI logic
- automated trading

## Testing Requirements

Default tests must be offline.

Live tests are forbidden for TASK-003.

Run:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

If the command cannot run, report the exact reason in `coordination/reports/TASK-003_REPORT.md`.

## Acceptance Criteria

The task is acceptable when:

- DataHub can write local in-memory records to a deterministic dataset file
- DataHub can read those records back without network access
- parent directories are created as needed
- missing-file behavior is explicit and tested
- optional schema validation, if implemented, is covered by offline tests
- all default DataHub tests run without live network access
- no future-phase module contains new logic
- the report file exists at `coordination/reports/TASK-003_REPORT.md`
- report includes files changed, tests run, network behavior, deviations, and follow-ups

## Report Path

`coordination/reports/TASK-003_REPORT.md`

## Review Path

`coordination/reviews/TASK-003_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-003_INTEGRATION.md`

## Out of Scope

Everything outside DataHub local storage IO foundation is out of scope.
