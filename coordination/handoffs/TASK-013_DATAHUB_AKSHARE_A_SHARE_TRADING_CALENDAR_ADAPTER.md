# TASK-013: DataHub AKShare A-share Trading Calendar Adapter

## Task ID

TASK-013

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

TASK-012 is accepted and integrated. It added the first narrow real-source adapter seed for AKShare A-share `daily_bars`, including:

- `AkshareAShareDailyBarAdapter`
- offline fixture-based adapter tests
- mandatory gated live smoke test behavior
- explicit live-enabled skip evidence in `coordination/reports/TASK-012_REPORT.md`

Phase 2 remains open. The next useful DataHub slice is a second small AKShare adapter for A-share trading calendars. This expands Phase 2 coverage from price bars into exchange-calendar foundation data without touching downstream modules.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-013_DATAHUB_AKSHARE_A_SHARE_TRADING_CALENDAR_ADAPTER.md`

## Goal

Implement a narrow AKShare-backed A-share trading calendar adapter for `DatasetName.TRADING_CALENDAR`, with deterministic offline tests and mandatory gated live smoke coverage.

This task should add the calendar adapter as a small sibling to the TASK-012 daily-bar adapter, not as a broad ingestion job.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-013_REPORT.md`

Suggested implementation locations:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `quant/datahub/source_catalog.py` if catalog coverage needs to reflect AKShare trading-calendar support
- `tests/datahub/test_akshare_calendar_adapter.py`
- `tests/datahub/test_akshare_calendar_live.py`
- existing DataHub tests only as needed for import/catalog updates

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

### 1. AKShare A-share trading calendar adapter

Add a narrow adapter for the catalog source family:

- source id: `akshare_cn_hk_public_family`
- source name/display name: `AKShare CN/HK Public Family`
- supported dataset in this task: `DatasetName.TRADING_CALENDAR`
- market output: `CN`
- asset/domain scope in this task: A-share exchange trading calendar only

The adapter should:

- implement the existing `SourceAdapter` protocol
- use lazy/optional AKShare access so importing `quant.datahub` and running default tests do not require AKShare to be installed
- allow dependency injection of a fake calendar fetch function/client for offline tests
- reject unsupported datasets clearly
- reject symbol inputs if supplied, since trading calendar is market-level rather than symbol-level
- accept optional `start_date` and `end_date` from `SourceRequest`
- normalize source rows into `DatasetName.TRADING_CALENDAR` records compatible with `DatasetRegistry.validate_record(...)`
- include all required fields for `trading_calendar`:
  - `market`
  - `trade_date`
  - `is_open`
  - `session_type`
  - `previous_trade_date`
  - `next_trade_date`
  - `source`
  - `ingested_at`
  - `schema_version`
- set `market` to `CN`
- set `is_open` to `True` for returned AKShare trading dates
- set `session_type` to `full` unless the selected source payload reliably distinguishes half-days/special sessions
- set `source` to `akshare_cn_hk_public_family`
- set `schema_version` from `DatasetRegistry`
- set `ingested_at` deterministically in offline tests, for example through an injectable clock
- compute `previous_trade_date` and `next_trade_date` from the returned sorted trading-date sequence
- handle source payloads that are DataFrame-like (`to_dict(orient="records")`) or list-of-mapping/list-of-date-like fixtures
- fail clearly when the source payload is malformed or does not contain usable dates

The default live implementation may use an AKShare public calendar function such as a Sina trading-date helper if available in the installed AKShare version. Keep the implementation isolated and easy to update if AKShare changes function names.

### 2. Source catalog alignment

If the adapter introduces AKShare support for `DatasetName.TRADING_CALENDAR`, update the DataHub source catalog under `quant/datahub/source_catalog.py` so the `akshare_cn_hk_public_family` entry reflects this stable dataset and the exchange-calendar information domain when appropriate.

If updated, add or adjust offline catalog tests to prove coverage remains deterministic and complete.

### 3. Offline tests

Add deterministic offline tests using fake AKShare calendar payloads. They must prove:

- adapter satisfies `SourceAdapter`
- `fetch_source_result(...)` works with the adapter and `SourceRequest`
- normalized `trading_calendar` records pass `DatasetRegistry.validate_record(...)`
- start/end date filtering behaves deterministically
- previous/next trading dates are computed correctly
- unsupported datasets fail clearly
- symbol inputs fail clearly
- malformed payloads fail clearly
- DataFrame-like payload conversion works when implemented
- default test discovery performs no live network calls

Use `socket.create_connection` patching where useful to protect default tests from accidental network access.

### 4. Mandatory live smoke test

Because TASK-013 implements a real source adapter, a gated live smoke test is mandatory.

Add a live test such as `tests/datahub/test_akshare_calendar_live.py` that:

- is skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1`
- uses no credentials
- fetches a tiny bounded calendar sample
- validates at least one successfully fetched record through `DatasetRegistry.validate_record(...)`
- records environment/source unavailability as explicit `skipTest(...)`, not as an uncategorized error
- preserves adapter/data-contract bugs as failures rather than hiding them as skips

Follow the TASK-012 live evidence style:

- default command result
- live-enabled command result
- skip reason if live-enabled environment cannot reach AKShare/public source

## Do Not Implement

Do not implement:

- new daily-bar functionality beyond what TASK-012 already added
- A-share instrument master, valuation, capital flow, corporate action, or full-market ingestion jobs
- Hong Kong stock adapters
- ETF/fund adapters
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

`python3 -m unittest tests/datahub/test_akshare_calendar_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_calendar_live.py`

If source-catalog tests are touched, run:

`python3 -m unittest tests/datahub/test_source_catalog.py`

Because TASK-013 is a real-source adapter task, run the gated live smoke command when explicitly enabled in the local environment:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_calendar_live.py`

If this environment cannot reach the public source or proxy, the command should complete as a clear skip instead of an uncategorized error, and the report must record that skip reason.

## Acceptance Criteria

The task is acceptable when:

- an AKShare A-share `trading_calendar` adapter exists under `quant/datahub/**`
- the adapter implements `SourceAdapter` without requiring AKShare during default imports/tests
- offline fixture-based tests prove `fetch_source_result(...) -> normalized records -> DatasetRegistry.validate_record(...)` succeeds
- date filtering and previous/next trading-date computation are covered by tests
- unsupported dataset, symbol input, and malformed source-payload paths fail clearly
- source catalog alignment is updated and tested if needed
- default tests do not perform live network access
- the mandatory live smoke test exists, is skipped by default, and is gated by `QUANT_SYSTEM_LIVE_TESTS=1`
- live-enabled environment failures are explicit skips with recorded reasons
- no future-phase module contains new logic
- the report file exists at `coordination/reports/TASK-013_REPORT.md`
- the report includes files changed, tests run, default network behavior, live smoke implementation and run/skip status, deviations from the handoff, and follow-up risks/tasks

## Report Path

`coordination/reports/TASK-013_REPORT.md`

## Review Path

`coordination/reviews/TASK-013_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-013_INTEGRATION.md`

## Out of Scope

Everything outside a narrow DataHub AKShare A-share trading calendar adapter and its tests is out of scope.
