# TASK-008: DataHub Expanded Contract Semantic Validation

## Task ID

TASK-008

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

TASK-006 completed the comprehensive DataHub source catalog and coverage matrix.

TASK-007 expanded stable DataHub dataset/schema contracts for Phase 2 domains:

- index data
- ETF/fund data
- industry and concept sector data
- macroeconomic data
- policy documents
- news events
- company announcements
- concise global equity snapshots

TASK-007 review and integration accepted the work. The new schemas are intentionally lightweight foundations. Before implementing source adapters, DataHub should reject obvious semantic defects in records, not just missing fields and dtype mismatches.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/handoffs/TASK-008_DATAHUB_EXPANDED_CONTRACT_SEMANTIC_VALIDATION.md`

## Goal

Add lightweight semantic validation and stronger invalid-sample tests for expanded Phase 2 DataHub contracts while keeping default tests offline and deterministic.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-008_REPORT.md`

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

Implement only DataHub contract validation hardening.

Minimum expected pieces:

- preserve existing required-field and dtype validation behavior
- add lightweight semantic validation in `quant/datahub/**`, preferably through `DatasetRegistry.validate_record(...)` or a small helper it calls
- semantic validation should cover obvious, local-only record issues such as:
  - `schema_version` value must match the registered schema version when present
  - required identifier/title fields must not be empty strings
  - OHLC-style records must not have `high < low`
  - nonnegative fields such as `volume`, `amount`, `nav`, `fund_scale`, `shares_outstanding`, `shares`, `position_value`, and similar size/price fields should not be negative when present
  - weights such as `weight` should be within a sane percentage range when present
  - date ranges such as `out_date` before `in_date` should be rejected when both are present
  - datetime/date strings that pass dtype parsing should remain accepted
- keep validation generic enough to avoid hard-coding strategy, signal, ranking, or downstream research logic
- add invalid-sample tests for the expanded domains added in TASK-007, prioritizing:
  - macro observations
  - policy documents
  - news events
  - company announcements
  - sector membership or sector daily bars
  - fund holdings or fund NAV snapshots
  - index daily bars or index constituents
  - global equity snapshots
- update tests to ensure existing valid fixtures still pass
- fix the known TASK-007 review P3 fragility: `tests/datahub/test_source_catalog.py` should not assert that `InformationDomain.NEWS` has exactly one source; use a contains-style assertion instead
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

Live tests are forbidden for TASK-008.

Run:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

If useful, also run focused tests for changed validation/catalog modules.

If any command cannot run, report the exact reason in `coordination/reports/TASK-008_REPORT.md`.

## Acceptance Criteria

The task is acceptable when:

- semantic validation catches obvious invalid values for expanded Phase 2 contracts
- required-field and dtype validation behavior remains intact
- representative valid records for existing and expanded schemas still pass validation
- invalid samples exist for the prioritized expanded domains
- the source catalog news-source assertion is no longer brittle against normal source expansion
- no default test performs live network access
- no future-phase module contains new logic
- the report file exists at `coordination/reports/TASK-008_REPORT.md`
- report includes files changed, tests run, default network behavior, deviations, and follow-ups

## Report Path

`coordination/reports/TASK-008_REPORT.md`

## Review Path

`coordination/reviews/TASK-008_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-008_INTEGRATION.md`

## Out of Scope

Everything outside DataHub contract semantic validation and offline tests is out of scope.
