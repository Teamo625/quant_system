# TASK-050: DataHub AKShare A-share Minute Bars Adapter

## Task ID

TASK-050

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2.5: DataHub Trading-Grade Source Capability

## Context

TASK-049 has been accepted, integrated, and controller-closed after the live-route rework. It added bounded public AKShare A-share `MAJOR_ACTIVITY_EVENTS` coverage and the reworked live smoke now passes.

Phase 2.5 remains open because required trading-grade source capabilities still include planned or partial DataHub source-capability work. The next executable gap is `a_share_minute_bars`, which has a stable `DatasetName.MINUTE_BARS` contract from TASK-042 but still lacks implemented adapter coverage.

Current source-capability truth marks `a_share_minute_bars` as `planned`. The catalog already has credentialed Tushare minute-bar coverage, but this task should first attempt a narrow no-credential public AKShare A-share minute-bar source slice. Local AKShare route names observed by the controller include `stock_zh_a_hist_min_em` and `stock_zh_a_minute`; the execution window must verify route shape with deterministic fixtures and live smoke before updating capability truth.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-050_DATAHUB_AKSHARE_A_SHARE_MINUTE_BARS_ADAPTER.md`
- `quant/datahub/datasets.py`
- `quant/datahub/source.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `quant/datahub/adapters/akshare.py`
- relevant existing AKShare adapter and live-smoke tests under `tests/datahub/`

## Goal

Implement a narrow no-credential AKShare-backed A-share minute-bar adapter slice that produces validated records for:

- `DatasetName.MINUTE_BARS`

The first source slice should support one requested A-share stock symbol and one bounded intraday period/date request, preserving source-fact OHLCV semantics only.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-050_REPORT.md`

Suggested implementation locations:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py` only if exports need adjustment
- `quant/datahub/source_capabilities.py` only to update A-share minute-bars capability truth after implementation
- `quant/datahub/source_catalog.py` only if verified public AKShare coverage makes catalog truth inconsistent
- `tests/datahub/test_akshare_a_share_minute_bars_adapter.py`
- `tests/datahub/test_akshare_a_share_minute_bars_live.py`
- focused existing tests under `tests/datahub/` if shared parsing, symbol, source catalog, or AKShare behavior changes

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

### 1. AKShare A-share minute-bars adapter slice

Add a narrow adapter for:

- source id: `akshare_cn_hk_public_family`
- source display name: `AKShare CN/HK Public Family`
- supported dataset in this task:
  - `DatasetName.MINUTE_BARS`
- initial market scope: one requested A-share stock symbol and a bounded minute-bar request

The adapter should:

- implement the existing `SourceAdapter` protocol and `SourceResult` conventions
- use no credentials, cookies, tokens, browser session state, or private account data
- reject unsupported datasets clearly
- require exactly one A-share stock symbol
- accept canonical exchange-qualified A-share symbols such as `600000.SH`, `000001.SZ`, and `430047.BJ`
- accept bare six-digit A-share codes only when existing local adapter style supports them, then normalize output `symbol` to canonical exchange-qualified form when the source row permits it
- reject HK, ETF/fund, index, malformed, missing, and multiple symbols clearly
- require bounded request parameters; reject unbounded requests
- reject full-market minute-bar ingestion and broad multi-symbol requests
- set `market=A_SHARE`
- set `source=akshare_cn_hk_public_family`
- set `schema_version` from `DatasetRegistry`
- set `ingested_at` from an injectable clock for deterministic tests
- support DataFrame-like and list-of-mapping payloads in offline fixtures
- normalize source fields into the `MINUTE_BARS` contract without inventing values the source does not provide
- populate `trade_date` from each minute bar timestamp
- populate `bar_time`, `open`, `high`, `low`, `close`, and `volume` from verified source fields
- populate optional `amount`, `vwap`, and `source_ts` only when truthfully available
- sort output deterministically by `symbol`, `bar_time`
- deduplicate exact duplicate bars deterministically
- fail clearly on malformed payloads, missing required source fields, invalid timestamps, invalid OHLCV values, unsupported datasets, invalid symbols, route signature incompatibility, or schema/normalization errors

### 2. Route and source boundary

- Prefer no-credential AKShare A-share minute-bar routes available in the local AKShare version.
- Candidate route names observed by the controller include `stock_zh_a_hist_min_em` and `stock_zh_a_minute`; the execution window must still verify selected route behavior with deterministic fixtures.
- Route selection must be bounded and explicit. If the route only supports recent intraday windows, preserve that limitation in source-capability truth and the execution report.
- Do not add Tushare, credentialed fallback, browser scraping, cookies, tokens, or private account data.
- Do not add broad A-share universe ingestion, full-history minute-bar backfill, scheduler logic, storage refresh orchestration, cross-source fallback, scanner ranking, stock picking, trading signals, or strategy rules.
- Network/proxy/DNS/TLS/upstream/source availability failures may be classified for live skip diagnostics, but adapter/schema/normalization and AKShare function argument/signature issues must remain hard failures.

### 3. Source capability truth

If the dataset has working offline adapter coverage and gated live smoke evidence, update source capability truth conservatively:

- `a_share_minute_bars`: use `partial` if this task validates only a narrow public-source one-symbol/recent-window slice
- add `akshare_cn_hk_public_family` to `source_family_ids` only if the selected public AKShare route is actually implemented and validated
- update `gap_reason` and `recommended_handoff_theme` only as needed to reflect public AKShare coverage and remaining breadth/history limitations
- update `source_catalog.py` only if implemented public AKShare coverage makes catalog dataset coverage inconsistent
- do not mark the capability `covered` unless the implementation genuinely satisfies the full trading-grade capability definition

Do not change unrelated capabilities except to preserve tests.

### 4. Offline tests

Add deterministic offline tests proving:

- adapter satisfies `SourceAdapter`
- `DatasetName.MINUTE_BARS` is accepted and unsupported datasets fail clearly
- `fetch_source_result(...)` records pass `DatasetRegistry.validate_record(...)`
- bounded request behavior works and unbounded or invalid request parameters fail clearly
- canonical and accepted bare A-share symbol handling works
- invalid HK, ETF, fund, index, malformed, missing, and multiple symbols fail clearly
- DataFrame-like and list-of-mapping payload conversion works
- timestamp parsing works, sets `trade_date`, and invalid timestamps fail clearly
- numeric parsing accepts supported source formats and rejects invalid OHLCV/volume values
- optional `amount`, `vwap`, and `source_ts` remain source-truth based
- records are sorted and duplicate bars are deduplicated
- malformed payloads and missing required source fields fail clearly
- AKShare route argument/signature compatibility errors are not classified as live environment/source unavailable
- default tests remain offline-safe; patch network helpers where useful

### 5. Mandatory live smoke test

Because TASK-050 is a real-source adapter task, gated live smoke coverage is mandatory.

Add `tests/datahub/test_akshare_a_share_minute_bars_live.py` or equivalent that:

- is skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1`
- uses no credentials
- fetches a minimal bounded live sample for one liquid A-share symbol, preferably `600000.SH` or another stable main-board symbol supported by the selected public route
- validates at least one record through `DatasetRegistry.validate_record(...)`
- asserts `source=akshare_cn_hk_public_family`, `market=A_SHARE`, canonical A-share symbol output, and valid `bar_time`
- classifies environment/source unavailability as explicit `skipTest(...)`
- preserves adapter/schema/normalization and AKShare function argument/signature issues as failures

If the live-enabled run fails or skips due to network/proxy/DNS/TLS/upstream/source availability, the report must include root-cause evidence and feasible repository-level fixes attempted. Controller closure will require the rework/review/integration gate in `AGENTS.md`.

## Do Not Implement

Do not implement:

- Tushare or other credentialed adapters
- source routes requiring private credentials, cookies, or tokens
- broad A-share universe ingestion
- full minute-bar history backfill
- storage refresh orchestration
- feature calculations
- scanner ranking or stock picking
- strategy, backtest, portfolio, signal, risk, notification, AI, UI, or automated trading logic

## Testing Requirements

Default tests must remain offline.

Run:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Run focused tests, likely:

`python3 -m unittest tests/datahub/test_akshare_a_share_minute_bars_adapter.py`

`python3 -m unittest -v tests/datahub/test_akshare_a_share_minute_bars_live.py`

Run related regressions if shared AKShare parsing, source catalog, source capability, or symbol behavior is touched:

`python3 -m unittest tests/datahub/test_akshare_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_a_share_daily_bar_adapter.py`

`python3 -m unittest tests/datahub/test_source.py`

`python3 -m unittest tests/datahub/test_datasets.py`

`python3 -m unittest tests/datahub/test_source_capabilities.py`

`python3 -m unittest tests/datahub/test_source_catalog.py`

Run gated live smoke when enabled:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_minute_bars_live.py`

If any command cannot run, report the exact command and reason in `coordination/reports/TASK-050_REPORT.md`.

## Acceptance Criteria

The task is acceptable when:

- AKShare A-share minute-bar adapter coverage exists under `quant/datahub/**`
- records for `MINUTE_BARS` validate against `DatasetRegistry`
- scope remains limited to `market=A_SHARE` and `source=akshare_cn_hk_public_family`
- offline tests pass and remain deterministic
- default tests remain offline-safe
- bounded request, route selection, payload parsing, symbol handling, timestamp parsing, numeric parsing, sorting, deduplication, malformed payload, unsupported dataset, route compatibility, and source-unavailability boundaries are covered
- gated live smoke exists and result is truthfully recorded
- live-enabled PASS is provided for closure; if live-enabled skip/fail occurs because of network/proxy/DNS/TLS/upstream/source availability, the report includes root-cause evidence and feasible fixes attempted, and controller closure requires the rework/review/integration gate in `AGENTS.md`
- no future-phase module contains new logic
- report exists at `coordination/reports/TASK-050_REPORT.md`

## Report Path

`coordination/reports/TASK-050_REPORT.md`

## Review Path

`coordination/reviews/TASK-050_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-050_INTEGRATION.md`
