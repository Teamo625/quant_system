# TASK-010: DataHub Semantic Rule Integrity Checks

## Task ID

TASK-010

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

TASK-006 completed the comprehensive DataHub source catalog and coverage matrix.

TASK-007 expanded stable DataHub dataset/schema contracts for comprehensive Phase 2 domains.

TASK-008 added lightweight semantic validation and invalid-sample coverage for expanded contracts.

TASK-009 refactored semantic validation into explicit per-dataset rules and removed broad keyword-coupled validation. TASK-009 review and integration accepted the work, but identified a non-blocking maintainability gap: semantic rule fields should be checked against dataset schemas at initialization time so field-name typos or dtype mismatches cannot silently disable validation.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/handoffs/TASK-010_DATAHUB_SEMANTIC_RULE_INTEGRITY_CHECKS.md`

## Goal

Add DataHub semantic rule integrity checks so explicit semantic validation rules are verified against registered dataset schemas before source adapter implementation begins.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-010_REPORT.md`

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

Implement only DataHub semantic-rule integrity validation.

Minimum expected pieces:

- preserve existing required-field, dtype, and semantic validation behavior
- add an initialization-time rule integrity check in `DatasetRegistry` or a small helper it calls
- rule integrity checks should fail clearly if a semantic rule references a field that is not present in the dataset schema
- rule integrity checks should fail clearly if a semantic rule references fields with incompatible dtype, for example:
  - `nonempty_required_strings` should reference required `str` fields
  - `nonnegative_numeric_fields` should reference `float` fields or otherwise explicitly numeric-compatible fields
  - `weight_percentage_fields` should reference `float` fields
  - `ohlc_pairs` should reference numeric-compatible fields present in the same schema
  - `ordered_date_pairs` should reference date-compatible fields present in the same schema
- rule integrity errors should include enough detail to identify dataset, rule category, and field name
- keep `DatasetRegistry.get_semantic_rules(...)` available for tests and future adapter work
- add failure-path tests using synthetic or monkeypatched rule definitions so the default registry remains valid while broken rules are proven to fail
- add passing tests proving all default semantic rules align with all registered schemas
- keep tests local, deterministic, and network-free

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

Live tests are forbidden for TASK-010.

Run:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

If useful, also run focused tests for changed validation modules.

If any command cannot run, report the exact reason in `coordination/reports/TASK-010_REPORT.md`.

## Acceptance Criteria

The task is acceptable when:

- default semantic rules are checked against registered dataset schemas at initialization time or equivalent construction time
- broken semantic rules fail loudly with clear dataset/rule/field context
- existing validation behavior and issue codes remain stable
- tests cover valid default rules and representative broken-rule cases
- no default test performs live network access
- no future-phase module contains new logic
- the report file exists at `coordination/reports/TASK-010_REPORT.md`
- report includes files changed, tests run, default network behavior, deviations, and follow-ups

## Report Path

`coordination/reports/TASK-010_REPORT.md`

## Review Path

`coordination/reviews/TASK-010_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-010_INTEGRATION.md`

## Out of Scope

Everything outside DataHub semantic-rule integrity checking and offline tests is out of scope.
