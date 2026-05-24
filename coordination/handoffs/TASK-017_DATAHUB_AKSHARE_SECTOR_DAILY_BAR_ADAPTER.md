# TASK-017: DataHub AKShare Sector Daily Bar Adapter

## Task ID

TASK-017

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

TASK-016 is accepted and integrated. It added the first AKShare China index `index_daily_bars` adapter with source catalog alignment, deterministic offline tests, and mandatory gated live smoke coverage.

Phase 2 remains open. The next narrow executable source slice should expand DataHub coverage into industry/concept sector quote data. The source catalog already identifies `akshare_cn_hk_public_family` as a prioritized public source for `sector_daily_bars`, `sector_master`, and `sector_membership` coverage. This task should implement only the narrow `sector_daily_bars` slice.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-017_DATAHUB_AKSHARE_SECTOR_DAILY_BAR_ADAPTER.md`

## Goal

Implement a narrow AKShare-backed industry/concept sector daily bar adapter for `DatasetName.SECTOR_DAILY_BARS`, with deterministic offline tests and mandatory gated live smoke coverage.

This task should add one small sector daily-bar adapter sibling to the existing AKShare adapters. It must not become broad sector master, sector membership, stock selection, scanner, or strategy work.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-017_REPORT.md`

Suggested implementation locations:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `quant/datahub/source_catalog.py` only if catalog/export alignment is needed
- `tests/datahub/test_akshare_sector_adapter.py`
- `tests/datahub/test_akshare_sector_live.py`
- `tests/datahub/test_source_catalog.py` if source-catalog coverage changes
- existing DataHub tests only as needed for import/export or catalog updates

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
- `coordination/handoffs/**`
- `quant/features/**`
- `quant/strategies/**`
- `quant/backtest/**`
- `quant/scanner/**`
- `quant/portfolio/**`
- `quant/notification/**`
- `quant/ai/**`
- `quant/ui/**`

## Implementation Requirements

### 1. AKShare sector daily bar adapter

Add a narrow adapter for the catalog source family:

- source id: `akshare_cn_hk_public_family`
- source name/display name: `AKShare CN/HK Public Family`
- supported dataset in this task: `DatasetName.SECTOR_DAILY_BARS`
- default market output for the first slice: `CN_SECTOR`
- asset/domain scope in this task: one China industry or concept sector daily history at a time

The adapter should:

- implement the existing `SourceAdapter` protocol
- use lazy/optional AKShare access so importing `quant.datahub` and running default tests do not require AKShare to be installed
- allow dependency injection of fake industry/concept sector history fetch functions for offline tests
- reject unsupported datasets clearly
- require exactly one sector identifier through `SourceRequest.symbols` for this first implementation
- accept stable sector identifiers with an explicit type prefix, for example:
  - `INDUSTRY:小金属`
  - `CONCEPT:绿色电力`
- normalize output `sector_id` to a stable canonical identifier with uppercase prefix, for example `INDUSTRY:小金属` or `CONCEPT:绿色电力`
- route `INDUSTRY:` identifiers to an industry history fetch function
- route `CONCEPT:` identifiers to a concept history fetch function
- fail clearly when the sector identifier is missing, empty, untyped, unsupported, or unmapped
- accept optional `start_date` and `end_date` from `SourceRequest`
- pass bounded dates to the selected AKShare function in source-native `YYYYMMDD` format
- apply local date filtering after normalization as a guard if the source returns wider history
- normalize source rows into `DatasetName.SECTOR_DAILY_BARS` records compatible with `DatasetRegistry.validate_record(...)`
- include all required fields for `sector_daily_bars`:
  - `sector_id`
  - `market`
  - `trade_date`
  - `open`
  - `high`
  - `low`
  - `close`
  - `source`
  - `ingested_at`
  - `schema_version`
- include optional fields only when a valid value is available:
  - `volume`
  - `amount`
  - `source_ts`
- set `market` to `CN_SECTOR`
- set `source` to `akshare_cn_hk_public_family`
- set `schema_version` from `DatasetRegistry`
- set `ingested_at` deterministically in offline tests, for example through an injectable clock
- handle DataFrame-like payloads (`to_dict(orient="records")`) and list-of-mapping source-native fixtures
- fail clearly when the source payload is malformed, required fields are missing, numeric values cannot be parsed, date values cannot be parsed, optional datetime values cannot be parsed, or OHLC semantics violate the existing schema rules

The default live implementation may use AKShare public sector history functions such as:

- `stock_board_industry_hist_em(symbol=..., start_date=..., end_date=..., period="日k", adjust="")`
- `stock_board_concept_hist_em(symbol=..., period="daily", start_date=..., end_date=..., adjust="")`

Keep function resolution isolated and easy to update if AKShare changes function names or signatures.

Current local probing observed:

- `stock_board_industry_hist_em` and `stock_board_concept_hist_em` exist in the installed AKShare version.
- These paths are Eastmoney-backed and may raise `ProxyError` in this environment. If live-enabled smoke fails or skips for this reason, diagnose and record the root cause and add a feasible repository-level fallback or guard where practical.

### 2. Source catalog alignment

The source catalog already declares AKShare coverage for `DatasetName.SECTOR_DAILY_BARS` and `InformationDomain.INDUSTRY_CONCEPT_SECTOR`.

Do not add broad new catalog claims unless implementation actually changes stable coverage. If any catalog/export change is made, add or adjust deterministic offline tests.

Do not implement or claim `sector_master` or `sector_membership` adapter behavior in this task.

### 3. Offline tests

Add deterministic offline tests using fake AKShare sector daily-bar payloads. They must prove:

- adapter satisfies `SourceAdapter`
- `fetch_source_result(...)` works with the adapter and `SourceRequest`
- normalized `sector_daily_bars` records pass `DatasetRegistry.validate_record(...)`
- industry and concept identifiers route to the correct injected fetch function
- canonical sector identifier normalization preserves stable output `sector_id`
- optional date arguments are passed to source fetch functions in expected source-native format
- local date filtering works when the selected fake source returns wider history
- optional `volume`, `amount`, and `source_ts` fields are included only when valid values are available
- unsupported datasets fail clearly
- missing symbols, multiple symbols, empty identifiers, missing type prefixes, unsupported prefixes, and malformed identifiers fail clearly
- malformed payloads fail clearly
- invalid date, numeric, optional datetime, and OHLC semantic failures remain hard failures
- DataFrame-like payload conversion works when implemented
- default test discovery performs no live network calls

Use `socket.create_connection` patching where useful to protect default tests from accidental network access.

### 4. Mandatory live smoke test

Because TASK-017 implements a real source adapter, a gated live smoke test is mandatory.

Add a live test such as `tests/datahub/test_akshare_sector_live.py` that:

- is skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1`
- uses no credentials
- fetches a tiny bounded sector daily-bar sample, for example `CONCEPT:绿色电力` or `INDUSTRY:小金属` over a short historical date range
- validates at least one successfully fetched record through `DatasetRegistry.validate_record(...)`
- records environment/source unavailability as explicit `skipTest(...)`, not as an uncategorized error
- preserves adapter/data-contract bugs as failures rather than hiding them as skips

Follow the TASK-012 through TASK-016 live evidence style:

- default command result
- live-enabled command result
- skip reason if live-enabled environment cannot reach AKShare/public source
- root-cause evidence if live-enabled execution fails or skips because of network, proxy, DNS, TLS, upstream, or public-source availability

If the live-enabled smoke fails or skips because of network/proxy/DNS/TLS/upstream/source availability, the report must include root-cause evidence and any feasible repository-level fix attempted. If no repository-level fix is feasible, the report must say so and give concrete operator action.

## Do Not Implement

Do not implement:

- sector master adapter
- sector membership adapter
- stock/constituent membership collection
- index adapters beyond existing TASK-016 behavior
- ETF/fund changes beyond existing TASK-015 behavior
- A-share stock adapter changes beyond existing TASK-012/TASK-013 behavior
- Hong Kong stock adapter changes beyond existing TASK-014 behavior
- macro/policy/news/announcement adapters
- raw/normalized warehouse refresh orchestration
- credentials, cookies, browser automation, or private account flows
- strategy, backtest, scanner, AI, notification, UI, or automated trading logic

## Testing Requirements

Default tests must be offline.

Run:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Run focused tests for changed modules, likely:

`python3 -m unittest tests/datahub/test_akshare_sector_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_sector_live.py`

If shared AKShare adapter exports or behavior are touched, also run relevant existing focused tests, for example:

`python3 -m unittest tests/datahub/test_akshare_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_calendar_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_hk_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_fund_nav_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_index_adapter.py`

If source-catalog tests are touched, run:

`python3 -m unittest tests/datahub/test_source_catalog.py`

Because TASK-017 is a real-source adapter task, run the gated live smoke command when explicitly enabled in the local environment:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_sector_live.py`

If this environment cannot reach the public source or proxy, the command should complete as a clear skip instead of an uncategorized error, and the report must record that skip reason with root-cause evidence.

## Acceptance Criteria

The task is acceptable when:

- an AKShare China sector `sector_daily_bars` adapter exists under `quant/datahub/**`
- the adapter implements `SourceAdapter` without requiring AKShare during default imports/tests
- offline fixture-based tests prove `fetch_source_result(...) -> normalized records -> DatasetRegistry.validate_record(...)` succeeds
- industry/concept routing, sector identifier validation, date argument passing, and local date filtering are covered by tests
- unsupported dataset, missing/multiple identifier, invalid identifier, and malformed source-payload paths fail clearly
- source catalog alignment is preserved and tested if touched
- default tests do not perform live network access
- the mandatory live smoke test exists, is skipped by default, and is gated by `QUANT_SYSTEM_LIVE_TESTS=1`
- live-enabled environment failures are explicit skips with recorded root-cause evidence and feasible repository fixes where applicable
- no future-phase module contains new logic
- the report file exists at `coordination/reports/TASK-017_REPORT.md`
- the report includes files changed, tests run, default network behavior, live smoke implementation and run/skip/pass status, deviations from the handoff, and follow-up risks/tasks

## Report Path

`coordination/reports/TASK-017_REPORT.md`

## Review Path

`coordination/reviews/TASK-017_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-017_INTEGRATION.md`

## Out of Scope

Everything outside a narrow DataHub AKShare China sector daily bar adapter and its tests is out of scope.
