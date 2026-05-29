# TASK-038: DataHub AKShare ETF Daily Bar Adapter

## Task ID

TASK-038

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

TASK-037 has been accepted and integrated. It added HKEX-backed Hong Kong `DatasetName.TRADING_CALENDAR` coverage with deterministic offline tests and live-enabled PASS evidence.

Phase 2 remains open. The roadmap requires ETF and fund data including reference, price/volume, holdings or composition where available, flow/scale where available, and quality metadata. The accepted implementation set currently includes ETF/fund NAV snapshots, fund profiles, and holdings, but it does not yet include ETF exchange-traded price/volume bars under the stable `DatasetName.DAILY_BARS` contract.

This task must implement only a narrow AKShare-backed ETF daily bar adapter slice.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-038_DATAHUB_AKSHARE_ETF_DAILY_BAR_ADAPTER.md`

## Goal

Implement a narrow AKShare-backed ETF daily bar adapter for one requested China ETF code, with deterministic offline tests and mandatory gated live smoke coverage.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-038_REPORT.md`

Suggested implementation locations:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `quant/datahub/source_catalog.py` only for minimal ETF/fund daily-bar source-catalog alignment
- `tests/datahub/test_akshare_etf_daily_bar_adapter.py`
- `tests/datahub/test_akshare_etf_daily_bar_live.py`
- `tests/datahub/test_source_catalog.py` only if source-catalog assertions are aligned

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

### 1. AKShare ETF daily bar adapter

Add a narrow adapter for:

- source id: `akshare_cn_hk_public_family`
- source display name: `AKShare CN/HK Public Family`
- supported dataset in this task: `DatasetName.DAILY_BARS`
- initial market scope: one requested China ETF symbol

The adapter should:

- implement the existing `SourceAdapter` protocol
- use no credentials, cookies, tokens, or private account data
- reject unsupported datasets clearly
- require exactly one ETF symbol
- accept canonical `510300.ETF_CN` and bare `510300` style ETF codes
- normalize output `symbol` to canonical `XXXXXX.ETF_CN`
- reject A-share stock suffixes, HK suffixes, fund-only suffixes, malformed codes, missing symbols, and multiple symbols clearly
- support optional `start_date` and `end_date` filtering
- normalize output records to the existing `DAILY_BARS` contract fields:
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
  - optional `source_ts`
  - `ingested_at`
  - `schema_version`
- set `market=ETF_CN`
- set `source=akshare_cn_hk_public_family`
- set `schema_version` from `DatasetRegistry`
- set `ingested_at` from an injectable clock for deterministic tests
- support DataFrame-like and list-of-mapping payloads in offline fixtures
- accept common AKShare ETF daily bar field names only when explicitly normalized by tests
- sort output by `trade_date`
- deduplicate exact duplicate ETF daily-bar rows deterministically
- fail clearly on malformed payloads, missing required OHLCV fields, invalid numeric values, invalid dates, invalid date ranges, unsupported datasets, or invalid symbols

It is acceptable to set `adj_factor=1.0` for source routes that do not provide an adjustment factor, as long as `price_adjustment` truthfully records the selected adjustment mode.

### 2. Route and source boundary

- Prefer the no-credential AKShare ETF historical daily route available in the local AKShare version, such as `fund_etf_hist_em`.
- Keep any route order bounded and explicit.
- Do not add broad ETF universe ingestion.
- Do not implement LOF, money-market fund, open-end fund NAV behavior, fund profile changes, holdings changes, capital-flow behavior, storage refresh orchestration, or cross-source fallback unless strictly needed for this ETF daily-bar slice.
- Network/proxy/DNS/TLS/upstream/source availability failures may be classified for live skip diagnostics, but DataHub contract or normalization failures must remain hard failures.

### 3. Source catalog alignment

`akshare_cn_hk_public_family` already has `DatasetName.DAILY_BARS` in broad dataset coverage. If tests reveal that `InformationDomain.ETF_FUND_FULL_DATA` stable datasets omit ETF price/volume coverage, add only the minimal catalog alignment needed to include `DatasetName.DAILY_BARS` for ETF/fund stable coverage.

Do not add broad source claims beyond accepted ETF daily-bar behavior.

### 4. Offline tests

Add deterministic offline tests proving:

- adapter satisfies `SourceAdapter`
- `fetch_source_result(...)` records pass `DatasetRegistry.validate_record(...)`
- canonical and bare ETF code handling works
- unsupported symbols and unsupported datasets fail clearly
- DataFrame-like and list-of-mapping payload conversion works
- date parsing accepts supported source formats and rejects invalid dates
- numeric parsing accepts supported source formats and rejects invalid values
- `start_date` / `end_date` filtering is deterministic
- records are sorted and duplicate trade dates are deduplicated
- malformed payloads and missing required source fields fail clearly
- default tests remain offline-safe; patch network connection helpers where useful

### 5. Mandatory live smoke test

Because TASK-038 is a real-source adapter task, gated live smoke is mandatory.

Add `tests/datahub/test_akshare_etf_daily_bar_live.py` or equivalent that:

- is skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1`
- uses no credentials
- fetches a minimal bounded live sample for one liquid ETF symbol, preferably `510300.ETF_CN`
- uses a short date window when supported by the route
- validates at least one record via `DatasetRegistry.validate_record(...)`
- asserts `source=akshare_cn_hk_public_family`, `market=ETF_CN`, and canonical ETF symbol
- classifies environment/source unavailability as explicit `skipTest(...)`
- preserves adapter/schema issues as failures

If the live-enabled run fails or skips due to network/proxy/DNS/TLS/upstream/source availability, the report must include root-cause evidence and feasible repository-level fixes attempted. Controller closure will require the rework/review/integration gate in `AGENTS.md`.

## Do Not Implement

Do not implement:

- broad ETF or fund universe ingestion
- non-ETF fund daily bars
- LOF or money-market fund adapters
- ETF/fund capital flow
- fund profile, NAV, or holdings changes unless strictly required to preserve existing tests
- new schema contracts unless strictly required and justified
- Tushare adapters or credentialed routes
- storage refresh orchestration
- trading strategies, feature calculations, scanner ranking, AI reports, notifications, automated trading, or UI

## Testing Requirements

Default tests must remain offline.

Run:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Run focused tests, likely:

`python3 -m unittest tests/datahub/test_akshare_etf_daily_bar_adapter.py`

`python3 -m unittest -v tests/datahub/test_akshare_etf_daily_bar_live.py`

Run related regressions if shared AKShare daily-bar or adapter export behavior is touched:

`python3 -m unittest tests/datahub/test_akshare_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_hk_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_fund_nav_adapter.py`

`python3 -m unittest tests/datahub/test_source.py`

If source-catalog tests are touched, run:

`python3 -m unittest tests/datahub/test_source_catalog.py`

Run gated live smoke when enabled:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_etf_daily_bar_live.py`

## Acceptance Criteria

The task is acceptable when:

- AKShare ETF `DAILY_BARS` adapter for one China ETF symbol exists under `quant/datahub/**`
- scope remains limited to `DatasetName.DAILY_BARS` with `market=ETF_CN`
- offline tests pass and remain deterministic
- default tests remain offline-safe
- symbol parsing, date filtering, sorting, deduplication, malformed payload, unsupported dataset, and symbol-rejection boundaries are covered
- gated live smoke exists and result is truthfully recorded
- live-enabled PASS is provided for closure; if live-enabled skip/fail occurs because of network/proxy/DNS/TLS/upstream/source availability, the report must include root-cause evidence and feasible fixes attempted, and controller closure will require the rework/review gate in `AGENTS.md`
- no future-phase module contains new logic
- report exists at `coordination/reports/TASK-038_REPORT.md`

## Report Path

`coordination/reports/TASK-038_REPORT.md`

## Review Path

`coordination/reviews/TASK-038_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-038_INTEGRATION.md`

## Out of Scope

Everything outside narrow AKShare ETF daily-bar adapter coverage is out of scope.
