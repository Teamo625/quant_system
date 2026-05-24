# TASK-016: DataHub AKShare Index Daily Bar Adapter

## Task ID

TASK-016

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

TASK-015 is accepted and integrated. It added the first AKShare ETF/fund NAV snapshot adapter with deterministic offline tests and mandatory gated live smoke coverage.

Phase 2 remains open. The next narrow executable source slice should expand DataHub coverage into the index data domain. The source catalog already marks index data as required Phase 2 coverage, but AKShare's public source family does not yet have an implemented `index_daily_bars` adapter in code.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-016_DATAHUB_AKSHARE_INDEX_DAILY_BAR_ADAPTER.md`

## Goal

Implement a narrow AKShare-backed China index daily bar adapter for `DatasetName.INDEX_DAILY_BARS`, with deterministic offline tests, source catalog alignment, and mandatory gated live smoke coverage.

This task should add one small index daily-bar adapter sibling to the existing AKShare adapters. It must not become broad index constituents, ETF, sector, strategy, or scanner work.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-016_REPORT.md`

Suggested implementation locations:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_index_adapter.py`
- `tests/datahub/test_akshare_index_live.py`
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

### 1. AKShare China index daily bar adapter

Add a narrow adapter for the catalog source family:

- source id: `akshare_cn_hk_public_family`
- source name/display name: `AKShare CN/HK Public Family`
- supported dataset in this task: `DatasetName.INDEX_DAILY_BARS`
- default market output for the first slice: `CN_INDEX`
- asset/domain scope in this task: one China equity index daily history at a time

The adapter should:

- implement the existing `SourceAdapter` protocol
- use lazy/optional AKShare access so importing `quant.datahub` and running default tests do not require AKShare to be installed
- allow dependency injection of fake index daily fetch functions/clients for offline tests
- reject unsupported datasets clearly
- require exactly one index code through `SourceRequest.symbols` for this first implementation
- accept canonical inputs such as `000300.CN_INDEX` and source-native inputs such as `sh000300`
- normalize output `index_code` to a stable canonical code, preferably `000300.CN_INDEX` for the first supported China index slice
- map common bare codes to AKShare source-native symbols deterministically:
  - `000300` -> `sh000300`
  - `000001` -> `sh000001`
  - `399001` -> `sz399001`
  - `399006` -> `sz399006`
- fail clearly when the index code format is unsupported or cannot be mapped
- accept optional `start_date` and `end_date` from `SourceRequest`
- pass bounded dates to the selected AKShare function when that function supports them, and locally filter records when the selected source function returns a wider history
- normalize source rows into `DatasetName.INDEX_DAILY_BARS` records compatible with `DatasetRegistry.validate_record(...)`
- include all required fields for `index_daily_bars`:
  - `index_code`
  - `index_name`
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
- set `market` to `CN_INDEX`
- set `source` to `akshare_cn_hk_public_family`
- set `schema_version` from `DatasetRegistry`
- set `ingested_at` deterministically in offline tests, for example through an injectable clock
- provide a non-empty `index_name` through a small deterministic mapping for common codes and/or an injectable name resolver
- handle DataFrame-like payloads (`to_dict(orient="records")`) and list-of-mapping source-native fixtures
- fail clearly when the source payload is malformed, required fields are missing, numeric values cannot be parsed, date values cannot be parsed, or OHLC semantics violate the existing schema rules

The default live implementation may use an AKShare public index history function such as `stock_zh_index_daily_tx`, `stock_zh_index_daily`, `stock_zh_index_daily_em`, or `index_zh_a_hist` when available in the installed AKShare version. Keep the implementation isolated and easy to update if AKShare changes function names.

Current local probing observed:

- `stock_zh_index_daily_tx(symbol="sh000300", start_date="20240102", end_date="20240105")` returned fields like `date`, `open`, `close`, `high`, `low`, and `amount`.
- Eastmoney-backed index paths may raise `ProxyError` in this environment. If the chosen primary path is Eastmoney-backed, add a feasible fallback where practical rather than only documenting the failure.

### 2. Source catalog alignment

If this task implements stable AKShare support for `DatasetName.INDEX_DAILY_BARS`, update `quant/datahub/source_catalog.py` so the `akshare_cn_hk_public_family` entry reflects that stable dataset and the `index_data` information domain where appropriate.

Add or adjust deterministic offline catalog tests to prove coverage remains complete and the AKShare index daily-bar claim is represented.

Do not add broad claims for `index_constituents`, global index data, sector data, or ETF/fund data unless implementation actually changes those stable coverages.

### 3. Offline tests

Add deterministic offline tests using fake AKShare index daily-bar payloads. They must prove:

- adapter satisfies `SourceAdapter`
- `fetch_source_result(...)` works with the adapter and `SourceRequest`
- normalized `index_daily_bars` records pass `DatasetRegistry.validate_record(...)`
- canonical/source-native index code conversion preserves stable output codes
- optional date arguments are passed to source fetch functions in expected source-native format when supported
- local date filtering works when the selected fake source returns wider history
- optional `volume`, `amount`, and `source_ts` fields are included only when valid values are available
- unsupported datasets fail clearly
- missing symbols, multiple symbols, and invalid/unmapped index code formats fail clearly
- malformed payloads fail clearly
- invalid date, numeric, optional datetime, and OHLC semantic failures remain hard failures
- DataFrame-like payload conversion works when implemented
- default test discovery performs no live network calls

Use `socket.create_connection` patching where useful to protect default tests from accidental network access.

### 4. Mandatory live smoke test

Because TASK-016 implements a real source adapter, a gated live smoke test is mandatory.

Add a live test such as `tests/datahub/test_akshare_index_live.py` that:

- is skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1`
- uses no credentials
- fetches a tiny bounded China index daily-bar sample, for example `000300.CN_INDEX` over a short historical date range
- validates at least one successfully fetched record through `DatasetRegistry.validate_record(...)`
- records environment/source unavailability as explicit `skipTest(...)`, not as an uncategorized error
- preserves adapter/data-contract bugs as failures rather than hiding them as skips

Follow the TASK-012 through TASK-015 live evidence style:

- default command result
- live-enabled command result
- skip reason if live-enabled environment cannot reach AKShare/public source
- root-cause evidence if live-enabled execution fails or skips because of network, proxy, DNS, TLS, upstream, or public-source availability

If the live-enabled smoke fails or skips because of network/proxy/DNS/TLS/upstream/source availability, the report must include root-cause evidence and any feasible repository-level fix attempted. If no repository-level fix is feasible, the report must say so and give concrete operator action.

## Do Not Implement

Do not implement:

- index constituents
- global index or global equity snapshot adapters
- sector/concept adapters
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

`python3 -m unittest tests/datahub/test_akshare_index_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_index_live.py`

If shared AKShare adapter exports or behavior are touched, also run relevant existing focused tests, for example:

`python3 -m unittest tests/datahub/test_akshare_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_calendar_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_hk_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_fund_nav_adapter.py`

If source-catalog tests are touched, run:

`python3 -m unittest tests/datahub/test_source_catalog.py`

Because TASK-016 is a real-source adapter task, run the gated live smoke command when explicitly enabled in the local environment:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_index_live.py`

If this environment cannot reach the public source or proxy, the command should complete as a clear skip instead of an uncategorized error, and the report must record that skip reason with root-cause evidence.

## Acceptance Criteria

The task is acceptable when:

- an AKShare China index `index_daily_bars` adapter exists under `quant/datahub/**`
- the adapter implements `SourceAdapter` without requiring AKShare during default imports/tests
- offline fixture-based tests prove `fetch_source_result(...) -> normalized records -> DatasetRegistry.validate_record(...)` succeeds
- index-code conversion, date argument passing, and local date filtering are covered by tests
- unsupported dataset, missing/multiple code, invalid/unmapped code, and malformed source-payload paths fail clearly
- source catalog alignment is updated and tested
- default tests do not perform live network access
- the mandatory live smoke test exists, is skipped by default, and is gated by `QUANT_SYSTEM_LIVE_TESTS=1`
- live-enabled environment failures are explicit skips with recorded root-cause evidence and feasible repository fixes where applicable
- no future-phase module contains new logic
- the report file exists at `coordination/reports/TASK-016_REPORT.md`
- the report includes files changed, tests run, default network behavior, live smoke implementation and run/skip/pass status, deviations from the handoff, and follow-up risks/tasks

## Report Path

`coordination/reports/TASK-016_REPORT.md`

## Review Path

`coordination/reviews/TASK-016_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-016_INTEGRATION.md`

## Out of Scope

Everything outside a narrow DataHub AKShare China index daily bar adapter and its tests is out of scope.
