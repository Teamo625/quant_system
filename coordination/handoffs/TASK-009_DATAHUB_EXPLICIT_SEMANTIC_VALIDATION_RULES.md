# TASK-009: DataHub Explicit Semantic Validation Rules

## Task ID

TASK-009

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

TASK-006 completed the comprehensive DataHub source catalog and coverage matrix.

TASK-007 expanded stable DataHub dataset/schema contracts for comprehensive Phase 2 domains.

TASK-008 added lightweight semantic validation for expanded contracts and invalid-sample coverage. TASK-008 review and integration accepted the work, but noted one maintainability risk: identifier/title field validation currently depends on field-name keyword matching. That is acceptable for TASK-008, but source adapter implementation will be safer if semantic validation rules are explicit and less coupled to incidental field names.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/handoffs/TASK-009_DATAHUB_EXPLICIT_SEMANTIC_VALIDATION_RULES.md`

## Goal

Refactor DataHub semantic validation so core rules are explicit, maintainable, and covered by offline tests before source adapter implementation begins.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-009_REPORT.md`

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

Implement only DataHub semantic validation rule maintainability improvements.

Minimum expected pieces:

- preserve existing required-field, dtype, and TASK-008 semantic validation behavior
- remove or reduce dependence on broad field-name keyword heuristics for identifier/title non-empty validation
- introduce an explicit semantic-rule structure under `quant/datahub/**`, for example:
  - per-dataset field rules
  - per-rule named checks
  - schema-level metadata or a small rule registry
- explicit rules should cover the TASK-008 semantic checks where applicable:
  - `schema_version` must match registered schema version
  - selected identifier/title/name fields must be non-empty when required
  - OHLC high/low consistency
  - nonnegative numeric fields
  - percentage/weight range checks
  - `in_date` / `out_date` ordering
- rule definitions should be local, deterministic, and easy for later adapter tasks to inspect
- `DatasetRegistry.validate_record(...)` should continue to return `ValidationIssue` objects with clear field and code values
- add tests that prove:
  - existing valid records still pass
  - existing invalid semantic samples still fail
  - non-empty string validation is driven by explicit rules, not accidental keyword matching
  - fields with names containing `id`, `code`, `symbol`, `title`, or `name` are not automatically rejected unless they are explicitly covered by a rule and required/present
  - semantic issue codes are stable enough for future adapter tests to assert
- keep all tests local and deterministic

Do not implement:

- real market data downloading
- source-specific live adapters
- live data tests
- credentials, token loading, cookies, browser automation, or private account flows
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

Live tests are forbidden for TASK-009.

Run:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

If useful, also run focused tests for changed validation modules.

If any command cannot run, report the exact reason in `coordination/reports/TASK-009_REPORT.md`.

## Acceptance Criteria

The task is acceptable when:

- semantic validation no longer relies on broad identifier/title keyword matching
- TASK-008 semantic validation behavior is preserved or made stricter only where explicitly justified
- explicit rule definitions are readable and maintainable for future source adapter work
- tests cover valid records, invalid semantic records, and keyword-coupling regression cases
- no default test performs live network access
- no future-phase module contains new logic
- the report file exists at `coordination/reports/TASK-009_REPORT.md`
- report includes files changed, tests run, default network behavior, deviations, and follow-ups

## Report Path

`coordination/reports/TASK-009_REPORT.md`

## Review Path

`coordination/reviews/TASK-009_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-009_INTEGRATION.md`

## Out of Scope

Everything outside DataHub semantic validation rule explicitness and offline tests is out of scope.
