# TASK-015: DataHub AKShare ETF/Fund NAV Snapshot Adapter

## Task ID

TASK-015

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

TASK-014 is accepted and integrated. It completed the AKShare Hong Kong `daily_bars` adapter and the required live-network diagnosis/fallback rework.

Phase 2 remains open. The next narrow executable source slice should expand DataHub coverage from stock price/calendar data into the ETF/fund domain. The source catalog already identifies `akshare_cn_hk_public_family` as a prioritized public source for ETF/fund data with stable `fund_nav_snapshot` coverage.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-015_DATAHUB_AKSHARE_ETF_FUND_NAV_ADAPTER.md`

## Goal

Implement a narrow AKShare-backed ETF/fund NAV snapshot adapter for `DatasetName.FUND_NAV_SNAPSHOT`, with deterministic offline tests and mandatory gated live smoke coverage.

This task should add a small sibling adapter to the existing AKShare DataHub adapters. It must not become broad ETF/fund ingestion, holdings, profile, or trading strategy work.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-015_REPORT.md`

Suggested implementation locations:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `quant/datahub/source_catalog.py` only if catalog/export alignment is needed
- `tests/datahub/test_akshare_fund_nav_adapter.py`
- `tests/datahub/test_akshare_fund_nav_live.py`
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

### 1. AKShare ETF/fund NAV snapshot adapter

Add a narrow adapter for the catalog source family:

- source id: `akshare_cn_hk_public_family`
- source name/display name: `AKShare CN/HK Public Family`
- supported dataset in this task: `DatasetName.FUND_NAV_SNAPSHOT`
- default market output for the first slice: `ETF_CN`
- asset/domain scope in this task: one China exchange-traded ETF/fund NAV history at a time

The adapter should:

- implement the existing `SourceAdapter` protocol
- use lazy/optional AKShare access so importing `quant.datahub` and running default tests do not require AKShare to be installed
- allow dependency injection of a fake NAV fetch function/client for offline tests
- reject unsupported datasets clearly
- require exactly one ETF/fund code for this first implementation
- accept canonical inputs such as `510300.ETF_CN` and source-native bare codes such as `510300`
- normalize output `fund_code` to a stable canonical code, preferably `510300.ETF_CN` for ETF_CN records
- accept optional `start_date` and `end_date` from `SourceRequest`
- pass bounded dates to the selected AKShare function when that function supports them
- normalize source rows into `DatasetName.FUND_NAV_SNAPSHOT` records compatible with `DatasetRegistry.validate_record(...)`
- include all required fields for `fund_nav_snapshot`:
  - `fund_code`
  - `market`
  - `trade_date`
  - `nav`
  - `source`
  - `ingested_at`
  - `schema_version`
- include optional fields only when a valid value is available:
  - `accumulated_nav`
  - `shares_outstanding`
  - `fund_scale`
  - `source_ts`
- set `market` to `ETF_CN` for this first adapter slice
- set `source` to `akshare_cn_hk_public_family`
- set `schema_version` from `DatasetRegistry`
- set `ingested_at` deterministically in offline tests, for example through an injectable clock
- handle DataFrame-like payloads (`to_dict(orient="records")`) and list-of-mapping source-native fixtures
- fail clearly when the source payload is malformed, required fields are missing, numeric values cannot be parsed, date values cannot be parsed, or the fund code format is unsupported

The default live implementation may use AKShare's public ETF/fund NAV history function, for example `fund_etf_fund_info_em(fund=..., start_date=..., end_date=...)` when available in the installed AKShare version. Keep the implementation isolated and easy to update if AKShare changes function names.

Known observed AKShare field names for `fund_etf_fund_info_em` include:

- `净值日期`
- `单位净值`
- `累计净值`

The implementation may support English aliases too, such as `trade_date`, `nav`, and `accumulated_nav`, to keep offline fixtures readable.

### 2. Source catalog alignment

The source catalog already declares AKShare coverage for `DatasetName.FUND_NAV_SNAPSHOT`.

Do not add broad new catalog claims unless implementation actually changes stable coverage. If any catalog/export change is made, add or adjust deterministic offline tests.

### 3. Offline tests

Add deterministic offline tests using fake AKShare ETF/fund NAV payloads. They must prove:

- adapter satisfies `SourceAdapter`
- `fetch_source_result(...)` works with the adapter and `SourceRequest`
- normalized `fund_nav_snapshot` records pass `DatasetRegistry.validate_record(...)`
- canonical ETF/fund code conversion preserves stable output codes
- optional date arguments are passed to the source fetch function in the expected source-native format
- optional fields are included only when valid values are available
- unsupported datasets fail clearly
- missing symbols, multiple symbols, and invalid ETF/fund code formats fail clearly
- malformed payloads fail clearly
- DataFrame-like payload conversion works when implemented
- default test discovery performs no live network calls

Use `socket.create_connection` patching where useful to protect default tests from accidental network access.

### 4. Mandatory live smoke test

Because TASK-015 implements a real source adapter, a gated live smoke test is mandatory.

Add a live test such as `tests/datahub/test_akshare_fund_nav_live.py` that:

- is skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1`
- uses no credentials
- fetches a tiny bounded ETF/fund NAV sample, for example `510300` over a short historical date range
- validates at least one successfully fetched record through `DatasetRegistry.validate_record(...)`
- records environment/source unavailability as explicit `skipTest(...)`, not as an uncategorized error
- preserves adapter/data-contract bugs as failures rather than hiding them as skips

Follow the TASK-012 through TASK-014 live evidence style:

- default command result
- live-enabled command result
- skip reason if live-enabled environment cannot reach AKShare/public source
- root-cause evidence if live-enabled execution fails or skips because of network, proxy, DNS, TLS, upstream, or public-source availability

## Do Not Implement

Do not implement:

- ETF/fund holdings
- ETF/fund profile/master data
- ETF or fund trading/price daily bars beyond NAV snapshot
- A-share stock adapter changes beyond existing TASK-012/TASK-013 behavior
- Hong Kong stock adapter changes beyond existing TASK-014 behavior
- index adapters
- sector/concept adapters
- macro/policy/news/announcement adapters
- raw/normalized warehouse refresh orchestration
- credentials, cookies, browser automation, or private account flows
- strategy, backtest, scanner, AI, notification, UI, or automated trading logic

## Testing Requirements

Default tests must be offline.

Run:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Run focused tests for changed modules, likely:

`python3 -m unittest tests/datahub/test_akshare_fund_nav_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_fund_nav_live.py`

If shared AKShare adapter exports or behavior are touched, also run relevant existing focused tests, for example:

`python3 -m unittest tests/datahub/test_akshare_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_calendar_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_hk_adapter.py`

If source-catalog tests are touched, run:

`python3 -m unittest tests/datahub/test_source_catalog.py`

Because TASK-015 is a real-source adapter task, run the gated live smoke command when explicitly enabled in the local environment:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_fund_nav_live.py`

If this environment cannot reach the public source or proxy, the command should complete as a clear skip instead of an uncategorized error, and the report must record that skip reason with root-cause evidence.

## Acceptance Criteria

The task is acceptable when:

- an AKShare ETF/fund `fund_nav_snapshot` adapter exists under `quant/datahub/**`
- the adapter implements `SourceAdapter` without requiring AKShare during default imports/tests
- offline fixture-based tests prove `fetch_source_result(...) -> normalized records -> DatasetRegistry.validate_record(...)` succeeds
- fund-code conversion and date argument passing are covered by tests
- unsupported dataset, missing/multiple code, invalid code, and malformed source-payload paths fail clearly
- source catalog alignment is preserved and tested if touched
- default tests do not perform live network access
- the mandatory live smoke test exists, is skipped by default, and is gated by `QUANT_SYSTEM_LIVE_TESTS=1`
- live-enabled environment failures are explicit skips with recorded root-cause evidence and feasible repository fixes where applicable
- no future-phase module contains new logic
- the report file exists at `coordination/reports/TASK-015_REPORT.md`
- the report includes files changed, tests run, default network behavior, live smoke implementation and run/skip/pass status, deviations from the handoff, and follow-up risks/tasks

## Report Path

`coordination/reports/TASK-015_REPORT.md`

## Review Path

`coordination/reviews/TASK-015_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-015_INTEGRATION.md`

## Out of Scope

Everything outside a narrow DataHub AKShare ETF/fund NAV snapshot adapter and its tests is out of scope.
