# TASK-004: DataHub Offline Fixture Validation

## Task ID

TASK-004

## Owner Role

5.3 execution window

## Status

Ready

## Context

TASK-001 created the minimal DataHub package foundation.

TASK-002 added field-level dataset schema contracts and offline required-field validation.

TASK-003 added local storage IO:

- `LocalStorage.write_records(...)`
- `LocalStorage.read_records(...)`
- `LocalStorage.write_metadata(...)`
- `LocalStorage.read_metadata(...)`
- optional required-field schema validation during record writes

TASK-003 review and integration accepted the work. The next step is to add explicit offline fixture validation so future changes have deterministic local examples for core DataHub datasets.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/handoffs/TASK-004_DATAHUB_OFFLINE_FIXTURE_VALIDATION.md`

## Goal

Create a small offline fixture validation foundation for DataHub that proves local fixture records conform to schema contracts and can round-trip through local storage without network access.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-004_REPORT.md`

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

Implement only DataHub offline fixture validation.

Minimum expected pieces:

- small deterministic fixture records under `tests/datahub/**`
- fixture coverage for at least these datasets:
  - `instrument_master`
  - `trading_calendar`
  - `daily_bars`
  - `data_quality_report`
- tests proving fixture records satisfy required-field schema validation
- tests proving invalid fixture records fail required-field validation
- tests proving fixture records can be written and read through `LocalStorage`
- no real market data download, API call, browser access, credential use, or live source adapter

Keep fixtures tiny and synthetic. They should be suitable for source control and must not contain private account data.

Optional, if it remains small:

- add a lightweight helper in `quant/datahub/` for validating a batch of records against a dataset schema
- replace direct socket monkeypatching in storage tests with `unittest.mock.patch` if this can be done without broad refactoring

Do not implement:

- real market data downloading
- source-specific adapters
- live data tests
- full data quality engine
- type/range/semantic validation beyond small required-field fixture checks unless it is tiny and directly tied to existing code
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

Live tests are forbidden for TASK-004.

Run:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

If the command cannot run, report the exact reason in `coordination/reports/TASK-004_REPORT.md`.

## Acceptance Criteria

The task is acceptable when:

- offline fixture records exist and are small, deterministic, and synthetic
- fixture validation covers at least `instrument_master`, `trading_calendar`, `daily_bars`, and `data_quality_report`
- valid fixture records pass required-field validation
- invalid fixture records fail required-field validation
- fixture records round-trip through local storage without network access
- all default DataHub tests run without live network access
- no future-phase module contains new logic
- the report file exists at `coordination/reports/TASK-004_REPORT.md`
- report includes files changed, tests run, network behavior, deviations, and follow-ups

## Report Path

`coordination/reports/TASK-004_REPORT.md`

## Review Path

`coordination/reviews/TASK-004_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-004_INTEGRATION.md`

## Out of Scope

Everything outside DataHub offline fixture validation is out of scope.
