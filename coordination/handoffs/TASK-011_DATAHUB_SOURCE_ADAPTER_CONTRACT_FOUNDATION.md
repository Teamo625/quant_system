# TASK-011: DataHub Source Adapter Contract Foundation

## Task ID

TASK-011

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

TASK-006 completed the comprehensive DataHub source catalog and coverage matrix.

TASK-007 expanded stable DataHub dataset/schema contracts for comprehensive Phase 2 domains.

TASK-008 added lightweight semantic validation and invalid-sample coverage.

TASK-009 made semantic validation rules explicit and inspectable.

TASK-010 added initialization-time integrity checks so semantic rules cannot silently drift from schemas.

The next Phase 2 step is to rebuild the DataHub source adapter contract foundation for the new comprehensive scope. This must not reintroduce the pre-rescope narrow adapter harness. It should define small runtime primitives and offline tests that future comprehensive source adapters can reuse.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/handoffs/TASK-011_DATAHUB_SOURCE_ADAPTER_CONTRACT_FOUNDATION.md`

## Goal

Create a small, reusable DataHub source adapter contract foundation that can support future comprehensive source adapters while keeping default tests offline and deterministic.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-011_REPORT.md`

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

Implement only DataHub source adapter contract foundation behavior.

Minimum expected pieces:

- preserve the existing `SourceAdapter` protocol shape unless a very small backward-compatible extension is necessary
- add runtime source request/result primitives under `quant/datahub/**`, likely in `source.py`, such as:
  - dataset name
  - source id or source name
  - optional start/end date
  - optional symbols
  - optional source catalog entry id
  - record count
  - produced/fetched timestamp
  - normalized records
- add a payload normalization helper that converts supported adapter outputs into `list[dict]` records, for example:
  - canonical source result object
  - list of mapping records
- payload normalization must fail clearly for unsupported payload shapes and non-mapping records
- add an offline contract helper or tests that verify adapter output can be:
  - fetched through `SourceAdapter`
  - normalized to records
  - validated by `DatasetRegistry.validate_record(...)`
  - checked against the semantic validation introduced in TASK-008 through TASK-010
- use deterministic test-only fixture adapters under `tests/datahub/**`; do not implement real source adapters yet
- fixture coverage should include at least one legacy market dataset and one expanded-domain dataset, for example:
  - `daily_bars`
  - `macro_observations`, `news_events`, `fund_nav_snapshot`, or another expanded dataset
- add failing-path tests for:
  - non-protocol adapter
  - unsupported payload shape
  - non-mapping record
  - schema/semantic invalid record
- keep all tests local and deterministic

Do not implement:

- real market data downloading
- source-specific live adapters
- live data tests
- credentials, token loading, cookies, browser automation, or private account flows
- scheduled crawling
- full-market ingestion jobs
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

Live tests are forbidden for TASK-011.

Run:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

If useful, also run focused tests for changed source/contract modules.

If any command cannot run, report the exact reason in `coordination/reports/TASK-011_REPORT.md`.

## Acceptance Criteria

The task is acceptable when:

- source request/result primitives exist and are covered by tests
- payload normalization accepts canonical result objects and list-of-mapping records
- invalid payload shapes fail clearly
- at least one legacy dataset and one expanded-domain dataset pass the offline adapter contract path
- schema and semantic validation failures surface clearly through contract tests
- no default test performs live network access
- no future-phase module contains new logic
- the report file exists at `coordination/reports/TASK-011_REPORT.md`
- report includes files changed, tests run, default network behavior, deviations, and follow-ups

## Report Path

`coordination/reports/TASK-011_REPORT.md`

## Review Path

`coordination/reviews/TASK-011_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-011_INTEGRATION.md`

## Out of Scope

Everything outside DataHub source adapter contract primitives and offline contract tests is out of scope.
