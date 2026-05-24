# TASK-002: DataHub Schema Contracts

## Task ID

TASK-002

## Owner Role

5.3 execution window

## Status

Ready

## Context

TASK-001 created the minimal DataHub foundation:

- `DataHubConfig`
- `DatasetName`
- `DatasetInfo`
- `DatasetRegistry`
- `SourceAdapter`
- `LocalStorage`
- offline unit tests

TASK-001 review and integration accepted the work. The main follow-up is to strengthen DataHub dataset contracts with field-level schema metadata and offline validation.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/handoffs/TASK-002_DATAHUB_SCHEMA_CONTRACTS.md`

## Goal

Extend the DataHub foundation with explicit, versioned, field-level dataset schema contracts that align with `docs/03_DATA_CONTRACTS.md`, plus offline tests for contract lookup and simple validation behavior.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-002_REPORT.md`

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

Implement only DataHub schema contract foundation.

Minimum expected pieces:

- a small field metadata representation, such as `FieldSpec`
- a dataset schema representation, such as `DatasetSchema`
- schema definitions for all current `DatasetName` values
- required fields aligned with `docs/03_DATA_CONTRACTS.md`
- schema version metadata compatible with the existing registry
- lookup helpers from dataset name to schema
- simple offline validation helpers for required fields
- tests that prove every registered dataset has a schema
- tests that prove missing required fields are detected

Keep the implementation lightweight and dependency-free unless a dependency is already present and clearly justified.

Optional, if it remains small and directly relevant:

- mark `SourceAdapter` as runtime-checkable and add a narrow offline test for protocol conformance.

Do not implement:

- real market data downloading
- source-specific adapters
- local warehouse read/write behavior beyond schema metadata
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

Live tests are forbidden for TASK-002.

Run:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

If the command cannot run, report the exact reason in `coordination/reports/TASK-002_REPORT.md`.

## Acceptance Criteria

The task is acceptable when:

- every `DatasetName` has a corresponding schema contract
- schema contracts include required fields from `docs/03_DATA_CONTRACTS.md`
- schema lookup is deterministic
- validation detects missing required fields using local in-memory records
- all default DataHub tests run without live network access
- no future-phase module contains new logic
- the report file exists at `coordination/reports/TASK-002_REPORT.md`
- report includes files changed, tests run, network behavior, deviations, and follow-ups

## Report Path

`coordination/reports/TASK-002_REPORT.md`

## Review Path

`coordination/reviews/TASK-002_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-002_INTEGRATION.md`

## Out of Scope

Everything outside DataHub schema contract foundation is out of scope.
