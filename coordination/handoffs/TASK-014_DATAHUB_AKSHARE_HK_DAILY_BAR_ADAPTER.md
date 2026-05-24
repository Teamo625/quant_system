# TASK-014: DataHub AKShare Hong Kong Daily Bar Adapter

## Task ID

TASK-014

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

TASK-013 is accepted and integrated. It added the AKShare A-share `trading_calendar` adapter and kept the real-source task pattern stable:

- deterministic offline adapter tests
- source catalog alignment when coverage changes
- mandatory gated live smoke coverage
- truthful live-enabled PASS/SKIP evidence in the execution report

Phase 2 remains open. The next narrow source adapter slice should expand the existing AKShare public-source family from A-share coverage into Hong Kong stock coverage. The source catalog already identifies `akshare_cn_hk_public_family` as a prioritized public source for Hong Kong stock full data and stable `daily_bars` coverage.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-014_DATAHUB_AKSHARE_HK_DAILY_BAR_ADAPTER.md`

## Goal

Implement a narrow AKShare-backed Hong Kong stock daily bar adapter for `DatasetName.DAILY_BARS`, with deterministic offline tests and mandatory gated live smoke coverage.

This task should add HK daily bars as a small sibling to the existing A-share daily-bar and A-share calendar adapters, not as a broad HK ingestion job.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-014_REPORT.md`

Suggested implementation locations:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `tests/datahub/test_akshare_hk_adapter.py`
- `tests/datahub/test_akshare_hk_live.py`
- existing DataHub tests only as needed for import/export updates

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

### 1. AKShare Hong Kong daily bar adapter

Add a narrow adapter for the catalog source family:

- source id: `akshare_cn_hk_public_family`
- source name/display name: `AKShare CN/HK Public Family`
- supported dataset in this task: `DatasetName.DAILY_BARS`
- market output: `HK`
- asset/domain scope in this task: Hong Kong listed stock daily bars only

The adapter should:

- implement the existing `SourceAdapter` protocol
- use lazy/optional AKShare access so importing `quant.datahub` and running default tests do not require AKShare to be installed
- allow dependency injection of a fake HK daily-history fetch function/client for offline tests
- reject unsupported datasets clearly
- require exactly one symbol for this first HK implementation
- accept optional `start_date` and `end_date` from `SourceRequest`
- convert canonical HK symbols such as `00700.HK` or `00005.HK` to the source-native AKShare symbol format when needed
- normalize source rows into `DatasetName.DAILY_BARS` records compatible with `DatasetRegistry.validate_record(...)`
- include all required fields for `daily_bars`:
  - `symbol`
  - `market`
  - `trade_date`
  - `open`
  - `high`
  - `low`
  - `close`
  - `volume`
  - `amount`
  - `adj_factor`
  - `price_adjustment`
  - `source`
  - `ingested_at`
  - `schema_version`
- set `market` to `HK`
- set `source` to `akshare_cn_hk_public_family`
- set `schema_version` from `DatasetRegistry`
- set `ingested_at` deterministically in offline tests, for example through an injectable clock
- set `adj_factor` to `1.0` when the selected source payload does not provide an adjustment factor
- set `price_adjustment` consistently with the adapter request/default, for example `raw`, `qfq`, or `hfq` only if AKShare HK support is reliable for that adjustment
- handle DataFrame-like payloads (`to_dict(orient="records")`) and list-of-mapping source-native fixtures
- fail clearly when the source payload is malformed, required fields are missing, numeric values cannot be parsed, or the symbol format is unsupported

The default live implementation may use an AKShare public HK stock historical function such as `stock_hk_hist` if available in the installed AKShare version. Keep the implementation isolated and easy to update if AKShare changes function names.

### 2. Source catalog alignment

The source catalog already declares AKShare coverage for Hong Kong stock `daily_bars`. Do not add broad new catalog claims unless implementation actually changes stable coverage.

If any catalog/export change is made, add or adjust deterministic offline tests.

### 3. Offline tests

Add deterministic offline tests using fake AKShare HK daily-bar payloads. They must prove:

- adapter satisfies `SourceAdapter`
- `fetch_source_result(...)` works with the adapter and `SourceRequest`
- normalized HK `daily_bars` records pass `DatasetRegistry.validate_record(...)`
- canonical HK symbol conversion preserves canonical output symbols
- optional date arguments are passed to the source fetch function in the expected source-native format
- unsupported datasets fail clearly
- missing symbols, multiple symbols, and invalid HK symbol formats fail clearly
- malformed payloads fail clearly
- DataFrame-like payload conversion works when implemented
- default test discovery performs no live network calls

Use `socket.create_connection` patching where useful to protect default tests from accidental network access.

### 4. Mandatory live smoke test

Because TASK-014 implements a real source adapter, a gated live smoke test is mandatory.

Add a live test such as `tests/datahub/test_akshare_hk_live.py` that:

- is skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1`
- uses no credentials
- fetches a tiny bounded HK stock daily-bar sample, for example one liquid HK symbol over a short historical date range
- validates at least one successfully fetched record through `DatasetRegistry.validate_record(...)`
- records environment/source unavailability as explicit `skipTest(...)`, not as an uncategorized error
- preserves adapter/data-contract bugs as failures rather than hiding them as skips

Follow the TASK-012/TASK-013 live evidence style:

- default command result
- live-enabled command result
- skip reason if live-enabled environment cannot reach AKShare/public source

## Do Not Implement

Do not implement:

- A-share daily-bar changes beyond existing TASK-012 behavior
- A-share trading-calendar changes beyond existing TASK-013 behavior
- HK instrument master, corporate actions, valuation, capital flow, announcements, or full-market ingestion jobs
- ETF/fund adapters
- index adapters
- sector/concept adapters
- macro/policy/news adapters
- raw/normalized warehouse refresh orchestration
- credentials, cookies, browser automation, or private account flows
- strategy, backtest, scanner, AI, notification, UI, or automated trading logic

## Testing Requirements

Default tests must be offline.

Run:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Run focused tests for changed modules, likely:

`python3 -m unittest tests/datahub/test_akshare_hk_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_hk_live.py`

If shared source or A-share adapter behavior is touched, also run relevant existing focused tests, for example:

`python3 -m unittest tests/datahub/test_akshare_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_calendar_adapter.py`

Because TASK-014 is a real-source adapter task, run the gated live smoke command when explicitly enabled in the local environment:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_live.py`

If this environment cannot reach the public source or proxy, the command should complete as a clear skip instead of an uncategorized error, and the report must record that skip reason.

## Acceptance Criteria

The task is acceptable when:

- an AKShare HK `daily_bars` adapter exists under `quant/datahub/**`
- the adapter implements `SourceAdapter` without requiring AKShare during default imports/tests
- offline fixture-based tests prove `fetch_source_result(...) -> normalized records -> DatasetRegistry.validate_record(...)` succeeds
- symbol conversion and date argument passing are covered by tests
- unsupported dataset, missing/multiple symbol, invalid HK symbol, and malformed source-payload paths fail clearly
- default tests do not perform live network access
- the mandatory live smoke test exists, is skipped by default, and is gated by `QUANT_SYSTEM_LIVE_TESTS=1`
- live-enabled environment failures are explicit skips with recorded reasons
- no future-phase module contains new logic
- the report file exists at `coordination/reports/TASK-014_REPORT.md`
- the report includes files changed, tests run, default network behavior, live smoke implementation and run/skip status, deviations from the handoff, and follow-up risks/tasks

## Report Path

`coordination/reports/TASK-014_REPORT.md`

## Review Path

`coordination/reviews/TASK-014_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-014_INTEGRATION.md`

## Out of Scope

Everything outside a narrow DataHub AKShare Hong Kong daily bar adapter and its tests is out of scope.
