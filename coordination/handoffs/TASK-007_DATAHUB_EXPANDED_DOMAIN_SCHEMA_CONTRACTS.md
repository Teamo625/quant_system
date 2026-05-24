# TASK-007: DataHub Expanded Domain Schema Contracts

## Task ID

TASK-007

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

TASK-006 completed the DataHub comprehensive source catalog and coverage matrix.

TASK-006 established coverage planning for the expanded Phase 2 domains:

- A-share full data
- Hong Kong stock full data
- ETF/fund full data
- index data
- concise global equity data
- industry and concept sector data
- global macroeconomic data
- China macroeconomic data
- policy data
- news data
- listed-company announcement data
- exchange calendars and trading schedules
- source health and data quality metadata

TASK-006 review and integration accepted the work. The main remaining gap is that several planned information domains have source coverage but do not yet have stable `DatasetName` contracts and schemas. Adapter implementation should not proceed for those domains until contracts exist.

The execution window must read:

- `AGENTS.md`
- `docs/01_SYSTEM_ARCHITECTURE.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/handoffs/TASK-007_DATAHUB_EXPANDED_DOMAIN_SCHEMA_CONTRACTS.md`

## Goal

Add stable DataHub dataset names and schema contracts for expanded Phase 2 information domains that are currently planned in the source catalog but not fully represented by `DatasetName`.

This task is contract-only. It prepares DataHub for comprehensive source ingestion without implementing live adapters or downloading data.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-007_REPORT.md`

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

Implement only DataHub dataset/schema contract expansion.

Minimum expected pieces:

- extend `DatasetName` and `DatasetRegistry` with stable contracts for expanded Phase 2 domains, including at least:
  - index bars or index snapshot data
  - index constituents or membership data
  - fund/ETF profile or master data beyond generic instrument master when needed
  - fund/ETF NAV or share/scale snapshots
  - fund/ETF holdings or composition data
  - industry/concept sector master data
  - industry/concept membership data
  - industry/concept quote or daily bars data
  - macro indicator metadata
  - macro observations covering both China and global macro series
  - policy document metadata
  - news event metadata
  - listed-company announcement metadata
  - concise global equity snapshot data
- keep schemas lightweight but explicit, using existing `FieldSpec` dtype conventions only (`str`, `bool`, `float`, `date`, `datetime`, `any`)
- each new schema must include provenance and version fields consistent with existing contracts where practical:
  - `source`
  - optional `source_ts` when useful
  - `ingested_at`
  - `schema_version`
- update `source_catalog` stable dataset linkage so information domains no longer incorrectly appear contractless once new schemas exist
- preserve the helper that identifies information domains missing stable dataset contracts; after this task it should return only intentional future gaps, if any
- add or update offline tests proving:
  - every `DatasetName` has a schema
  - every schema version matches its dataset info version
  - new dataset schemas validate representative valid records
  - missing required fields and dtype mismatches are still reported
  - source catalog stable dataset linkage reflects the new contracts
- keep default tests fully offline and deterministic

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

Live tests are forbidden for TASK-007.

Run:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

If the command cannot run, report the exact reason in `coordination/reports/TASK-007_REPORT.md`.

## Acceptance Criteria

The task is acceptable when:

- expanded Phase 2 domains have stable `DatasetName` entries and schema contracts
- `DatasetRegistry` schema coverage remains complete for all dataset names
- representative valid records for new schemas pass validation
- invalid records for new schemas fail with clear validation issues
- source catalog stable dataset linkage is updated to reflect the new contracts
- no default test performs live network access
- no future-phase module contains new logic
- the report file exists at `coordination/reports/TASK-007_REPORT.md`
- report includes files changed, tests run, default network behavior, deviations, and follow-ups

## Report Path

`coordination/reports/TASK-007_REPORT.md`

## Review Path

`coordination/reviews/TASK-007_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-007_INTEGRATION.md`

## Out of Scope

Everything outside DataHub expanded dataset/schema contracts and offline tests is out of scope.
