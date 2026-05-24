# TASK-006: DataHub All Source Catalog

## Task ID

TASK-006

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

The project owner changed the Phase 2 goal from selected source-adapter work to collecting comprehensive data coverage across all major data domains required by the system.

The previous TASK-006 through TASK-009 handoff chain has been deleted and should not be used as context for this new Phase 2 direction.

Phase 1 remains complete and provides the DataHub foundation:

- DataHub package skeleton
- dataset registry and schema contracts
- local JSONL/JSON storage IO
- deterministic offline fixtures
- lightweight schema type validation
- base `SourceAdapter` protocol

The execution window must read:

- `AGENTS.md`
- `docs/01_SYSTEM_ARCHITECTURE.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/handoffs/TASK-006_DATAHUB_ALL_SOURCE_CATALOG.md`

## Goal

Create a code-level DataHub source catalog and coverage matrix for all target data-source requirements across the expanded Phase 2 scope.

This task should make the expanded Phase 2 goal explicit and testable before implementing broad live adapters. The catalog should distinguish existing stable `DatasetName` contracts from planned data domains that still need future schema work.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-006_REPORT.md`

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

Implement only a DataHub source catalog foundation.

Minimum expected pieces:

- add a small runtime catalog module under `quant/datahub/**`, for example `source_catalog.py`
- define structured source/catalog primitives, such as:
  - source identifier
  - source name
  - covered stable dataset contracts, when available
  - planned data domain coverage, including domains not yet represented by `DatasetName`
  - market coverage
  - asset type coverage
  - geography or region coverage
  - whether credentials are required
  - whether live network access is required
  - priority or implementation stage
  - notes about limitations, licensing, freshness, or validation needs
- include coverage entries for all current `DatasetName` contracts:
  - `instrument_master`
  - `trading_calendar`
  - `daily_bars`
  - `corporate_actions`
  - `valuation_snapshot`
  - `capital_flow_snapshot`
  - `data_quality_report`
- include coverage across the expanded required data domains:
  - A-share full data
  - Hong Kong stock full data
  - ETF and fund full data
  - index data
  - concise global equity market data
  - industry and concept sector data
  - global macroeconomic data
  - China macroeconomic data
  - policy data
  - news data
  - listed-company announcement data
  - exchange calendars and trading schedules where relevant
  - source health and data quality metadata
- provide helper functions that can answer:
  - which sources cover a dataset
  - which datasets are missing source coverage
  - whether all required dataset contracts have at least one planned source
  - whether all required market, asset, geography, and information domains have at least one planned source
  - which expanded data domains do not yet have stable DataHub dataset contracts
- add offline tests proving the catalog covers every required stable dataset contract and every expanded Phase 2 data domain
- keep the catalog deterministic and local; no default test may perform live network access

Acceptable source entries may include planned providers, public source families, commercial-provider placeholders, or manually curated source families, but they must be explicit enough for follow-up adapter/schema handoffs.

Do not implement broad live downloading in this task.

Do not add credentials, tokens, cookies, private account flows, browser automation, scheduled crawlers, or full-market ingestion jobs.

Do not implement:

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

Live tests are forbidden for TASK-006.

Run:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

If the command cannot run, report the exact reason in `coordination/reports/TASK-006_REPORT.md`.

## Acceptance Criteria

The task is acceptable when:

- a DataHub comprehensive source catalog exists under `quant/datahub/**`
- all current `DatasetName` contracts have at least one planned source entry
- A-share full data, Hong Kong stock full data, ETF/fund full data, index data, concise global equity data, industry/concept sector data, global macro data, China macro data, policy data, news data, and announcement data have coverage entries
- catalog helper functions expose missing source coverage and missing stable dataset-contract coverage clearly
- tests validate full required coverage without live network access
- no future-phase module contains new logic
- the report file exists at `coordination/reports/TASK-006_REPORT.md`
- report includes files changed, tests run, default network behavior, deviations, and follow-ups

## Report Path

`coordination/reports/TASK-006_REPORT.md`

## Review Path

`coordination/reviews/TASK-006_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-006_INTEGRATION.md`

## Out of Scope

Everything outside a code-level DataHub comprehensive source catalog and offline coverage tests is out of scope.
