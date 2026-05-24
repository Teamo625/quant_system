# TASK-005: DataHub Schema Type Validation

## Task ID

TASK-005

## Owner Role

5.3 execution window

## Status

Ready

## Context

TASK-001 created the minimal DataHub package foundation.

TASK-002 added field-level dataset schema contracts and required-field validation.

TASK-003 added local JSONL/JSON storage IO.

TASK-004 added deterministic synthetic offline fixtures and fixture validation tests.

TASK-004 review and integration accepted the work. The main remaining gap repeatedly identified by review/integration is that validation currently focuses on required-field presence, while `FieldSpec.dtype` metadata is not yet enforced.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/handoffs/TASK-005_DATAHUB_SCHEMA_TYPE_VALIDATION.md`

## Goal

Extend DataHub schema validation with lightweight offline type checks based on existing `FieldSpec.dtype` metadata, while keeping validation small, dependency-free, deterministic, and limited to DataHub contracts.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-005_REPORT.md`

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

Implement only DataHub schema type validation.

Minimum expected pieces:

- extend existing validation to detect type mismatches for supported `FieldSpec.dtype` values
- keep supported dtypes aligned with current schemas:
  - `str`
  - `bool`
  - `date`
  - `datetime`
  - `float`
  - `any`
- allow `any` to pass without type checks
- keep optional fields optional when missing
- preserve existing missing-required-field validation behavior
- return structured `ValidationIssue` values for type mismatch failures
- add offline tests for valid fixture records
- add offline tests for invalid type examples
- add offline tests proving storage validation can reject bad typed records when enabled

Keep the implementation lightweight. ISO date/datetime strings are acceptable for `date` and `datetime` if documented in tests or code. Native Python `date`/`datetime` values may also be accepted if this stays simple.

Optional, if it remains small:

- add a batch validation helper for records
- update `tests/datahub/test_fixtures.py` to avoid ambiguous top-level `from fixtures import ...` imports

Do not implement:

- real market data downloading
- source-specific adapters
- live data tests
- a full data quality engine
- cross-record checks
- trading calendar logic beyond field-level type validation
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

Live tests are forbidden for TASK-005.

Run:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

If the command cannot run, report the exact reason in `coordination/reports/TASK-005_REPORT.md`.

## Acceptance Criteria

The task is acceptable when:

- validation still detects missing required fields
- validation detects basic type mismatches using `FieldSpec.dtype`
- optional missing fields do not fail validation
- valid offline fixtures pass validation
- invalid typed records fail validation with structured issues
- `LocalStorage.write_records(..., validate_schema=True)` rejects invalid typed records
- all default DataHub tests run without live network access
- no future-phase module contains new logic
- the report file exists at `coordination/reports/TASK-005_REPORT.md`
- report includes files changed, tests run, network behavior, deviations, and follow-ups

## Report Path

`coordination/reports/TASK-005_REPORT.md`

## Review Path

`coordination/reviews/TASK-005_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-005_INTEGRATION.md`

## Out of Scope

Everything outside DataHub schema type validation is out of scope.
