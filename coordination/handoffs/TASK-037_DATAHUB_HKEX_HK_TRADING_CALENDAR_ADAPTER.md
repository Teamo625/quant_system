# TASK-037: DataHub HKEX Hong Kong Trading Calendar Adapter

## Task ID

TASK-037

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

TASK-036 has been accepted and integrated. It reconciled `quant/datahub/source_catalog.py` with accepted implementation coverage through TASK-035, including AKShare index constituents and A-share corporate-actions catalog alignment.

Phase 2 remains open. The next narrow executable source slice is Hong Kong market trading-calendar coverage. The roadmap requires Hong Kong stock full-market data including calendar coverage. The repository currently has an accepted A-share trading-calendar adapter, but no HKEX/Hong Kong trading-calendar adapter. The source catalog already lists `DatasetName.TRADING_CALENDAR` under the no-credential `hkex_disclosure_and_calendar_family` source family.

This task must implement only Hong Kong `TRADING_CALENDAR` adapter behavior.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-037_DATAHUB_HKEX_HK_TRADING_CALENDAR_ADAPTER.md`

## Goal

Implement a narrow HKEX-backed Hong Kong trading calendar adapter for `DatasetName.TRADING_CALENDAR`, with deterministic offline tests and mandatory gated live smoke coverage.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-037_REPORT.md`

Suggested implementation locations:

- `quant/datahub/adapters/hkex.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `tests/datahub/test_hkex_hk_trading_calendar_adapter.py`
- `tests/datahub/test_hkex_hk_trading_calendar_live.py`
- `tests/datahub/test_source_catalog.py` only if strict catalog assertions require alignment

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

### 1. HKEX Hong Kong trading calendar adapter

Add a narrow adapter for:

- source id: `hkex_disclosure_and_calendar_family`
- source display name: `HKEX Disclosure and Calendar Family`
- supported dataset in this task: `DatasetName.TRADING_CALENDAR`
- initial market scope: Hong Kong securities market trading calendar

The adapter should:

- implement the existing `SourceAdapter` protocol
- use no credentials, cookies, tokens, or private account data
- reject unsupported datasets clearly
- reject `symbols` input clearly because this is a market-level calendar dataset
- support optional `start_date` and `end_date` filtering
- normalize output records to `TRADING_CALENDAR` contract fields:
  - `market`
  - `trade_date`
  - `is_open`
  - `session_type`
  - `previous_trade_date`
  - `next_trade_date`
  - `source`
  - optional `source_ts`
  - `ingested_at`
  - `schema_version`
- set `market=HK`
- set `source=hkex_disclosure_and_calendar_family`
- set `schema_version` from `DatasetRegistry`
- set `ingested_at` from an injectable clock for deterministic tests
- support DataFrame-like payloads, list-of-mapping payloads, and list-of-date-like payloads in offline fixtures
- accept common HKEX calendar field names only when explicitly normalized by tests
- deduplicate exact duplicate trading dates deterministically
- sort records by `trade_date`
- fail clearly on malformed payloads, missing required date fields, invalid date values, invalid date ranges, unsupported datasets, or invalid `symbols`

It is acceptable for this first HK calendar slice to emit open trading days only with `is_open=True` and `session_type=full`, matching the current A-share calendar pattern, unless the selected HKEX public route reliably exposes holidays or half-days. Do not claim holiday or half-day coverage unless implemented and tested.

### 2. Route and source boundary

- Prefer a no-credential HKEX public trading-calendar, holiday, or market-hours route.
- Keep any route order bounded and explicit.
- The live route may fetch HTML, CSV, JSON, ICS, or another public HKEX calendar representation if normalization remains narrowly scoped and deterministic.
- Network/proxy/DNS/TLS/upstream/source availability failures may be classified for live skip diagnostics, but DataHub contract or normalization failures must remain hard failures.
- Do not add broad HKEX scraping, disclosure changes, quote routes, instrument-master changes, or storage refresh orchestration.

### 3. Source catalog alignment

The catalog already includes `DatasetName.TRADING_CALENDAR` under `hkex_disclosure_and_calendar_family` and `InformationDomain.EXCHANGE_CALENDAR`.

Do not add broad source claims. Only perform minimal source-catalog assertion updates if required by implemented stable behavior.

### 4. Offline tests

Add deterministic offline tests proving:

- adapter satisfies `SourceAdapter`
- `fetch_source_result(...)` records pass `DatasetRegistry.validate_record(...)`
- source payload conversion from DataFrame-like, list-of-mapping, and date-like payloads works
- date parsing accepts the supported source formats and rejects invalid dates
- `start_date` / `end_date` filtering is deterministic
- records are sorted and duplicate trade dates are deduplicated
- `previous_trade_date` and `next_trade_date` are stable for first, middle, and last records
- unsupported datasets and `symbols` input fail clearly
- malformed payloads fail clearly
- network/source route fallback behavior is covered if implemented
- default tests remain offline-safe; patch network connection helpers where useful

### 5. Mandatory live smoke test

Because TASK-037 is a real-source adapter task, gated live smoke is mandatory.

Add `tests/datahub/test_hkex_hk_trading_calendar_live.py` or equivalent that:

- is skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1`
- uses no credentials
- fetches a minimal bounded live sample, preferably for a narrow recent or current-year range if the route supports filtering
- validates at least one record via `DatasetRegistry.validate_record(...)`
- asserts `source=hkex_disclosure_and_calendar_family` and `market=HK`
- classifies environment/source unavailability as explicit `skipTest(...)`
- preserves adapter/schema issues as failures

If the live-enabled run fails or skips due to network/proxy/DNS/TLS/upstream/source availability, the report must include root-cause evidence and feasible repository-level fixes attempted. Controller closure will require the rework/review/integration gate in `AGENTS.md`.

## Do Not Implement

Do not implement:

- broad HK market ingestion
- quote, valuation, corporate-action, instrument-master, announcement, or news behavior changes
- new schema contracts unless strictly required and justified
- Tushare adapters or credentialed routes
- storage refresh orchestration
- trading strategies, feature calculations, scanner ranking, AI reports, notifications, automated trading, or UI

## Testing Requirements

Default tests must remain offline.

Run:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Run focused tests, likely:

`python3 -m unittest tests/datahub/test_hkex_hk_trading_calendar_adapter.py`

`python3 -m unittest -v tests/datahub/test_hkex_hk_trading_calendar_live.py`

Run related regressions if shared DataHub or adapter export behavior is touched:

`python3 -m unittest tests/datahub/test_akshare_calendar_adapter.py`

`python3 -m unittest tests/datahub/test_hkex_company_announcements_adapter.py`

`python3 -m unittest tests/datahub/test_source.py`

If source-catalog tests are touched, run:

`python3 -m unittest tests/datahub/test_source_catalog.py`

Run gated live smoke when enabled:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_hkex_hk_trading_calendar_live.py`

## Acceptance Criteria

The task is acceptable when:

- HKEX `TRADING_CALENDAR` adapter for Hong Kong market exists under `quant/datahub/**`
- scope remains limited to `DatasetName.TRADING_CALENDAR` with `market=HK`
- offline tests pass and remain deterministic
- default tests remain offline-safe
- date parsing, filtering, sorting, deduplication, previous/next trade-date, malformed payload, unsupported dataset, and symbol-rejection boundaries are covered
- gated live smoke exists and result is truthfully recorded
- live-enabled PASS is provided for closure; if live-enabled skip/fail occurs because of network/proxy/DNS/TLS/upstream/source availability, the report must include root-cause evidence and feasible fixes attempted, and controller closure will require the rework/review gate in `AGENTS.md`
- no future-phase module contains new logic
- report exists at `coordination/reports/TASK-037_REPORT.md`

## Report Path

`coordination/reports/TASK-037_REPORT.md`

## Review Path

`coordination/reviews/TASK-037_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-037_INTEGRATION.md`

## Out of Scope

Everything outside narrow HKEX Hong Kong trading-calendar adapter coverage is out of scope.
