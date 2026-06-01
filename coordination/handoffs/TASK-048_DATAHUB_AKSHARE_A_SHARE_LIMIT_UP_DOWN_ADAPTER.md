# TASK-048: DataHub AKShare A-share Limit-Up/Down Adapter

## Task ID

TASK-048

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2.5: DataHub Trading-Grade Source Capability

## Context

TASK-047 has been accepted and integrated. It added a dedicated DataHub source-fact contract for A-share limit-up/down events:

- `DatasetName.LIMIT_UP_DOWN_EVENTS`

Phase 2.5 remains open because `a_share_limit_up_down` still has no implemented public-source adapter coverage. This task should implement the next bounded no-credential AKShare source slice against the new contract, without overloading `DAILY_BARS` and without introducing scanner, strategy, signal, or trading logic.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-048_DATAHUB_AKSHARE_A_SHARE_LIMIT_UP_DOWN_ADAPTER.md`
- `quant/datahub/datasets.py`
- `quant/datahub/source.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `quant/datahub/adapters/akshare.py`
- relevant existing AKShare adapter and live-smoke tests under `tests/datahub/`

## Goal

Implement a narrow AKShare-backed A-share limit-up/down adapter slice that produces validated source-fact records for:

- `DatasetName.LIMIT_UP_DOWN_EVENTS`

The task should prove that a bounded no-credential public source route can populate the TASK-047 contract while preserving deterministic offline tests and gated live smoke behavior.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-048_REPORT.md`

Suggested implementation locations:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py` only if exports need adjustment
- `quant/datahub/source_capabilities.py` only to update A-share limit-up/down capability truth after implementation
- `quant/datahub/source_catalog.py` only for minimal public-source alignment if catalog truth is inconsistent
- `tests/datahub/test_akshare_a_share_limit_up_down_adapter.py`
- `tests/datahub/test_akshare_a_share_limit_up_down_live.py`
- focused existing tests under `tests/datahub/` if shared parsing, symbol, or AKShare behavior changes

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

### 1. AKShare A-share limit-up/down adapter slice

Add a narrow adapter for:

- source id: `akshare_cn_hk_public_family`
- source display name: `AKShare CN/HK Public Family`
- supported dataset in this task:
  - `DatasetName.LIMIT_UP_DOWN_EVENTS`
- initial market scope: one bounded A-share trade-date table slice, with optional symbol filtering only when the selected public route provides enough symbol information

The adapter should:

- implement the existing `SourceAdapter` protocol and `SourceResult` conventions
- use no credentials, cookies, tokens, browser session state, or private account data
- reject unsupported datasets clearly
- require a bounded `trade_date` through existing `start_date` / `end_date` conventions; reject unbounded requests
- reject multi-day date ranges unless the implementation explicitly and safely supports bounded iteration
- accept canonical exchange-qualified A-share symbols such as `600000.SH`, `000001.SZ`, and `430047.BJ` when symbol filtering is supported by the selected route
- accept bare six-digit A-share codes only when existing local adapter style supports them, then normalize output `symbol` to canonical exchange-qualified form when the source row permits it
- reject HK, ETF/fund, index, malformed, and missing symbols clearly when symbol filtering is requested
- set `market=A_SHARE`
- set `source=akshare_cn_hk_public_family`
- set `schema_version` from `DatasetRegistry`
- set `ingested_at` from an injectable clock for deterministic tests
- support DataFrame-like and list-of-mapping payloads in offline fixtures
- normalize source fields into the `LIMIT_UP_DOWN_EVENTS` contract without inventing values the source does not provide
- emit source-fact fields such as `trade_date`, `limit_type`, `hit_limit_up`, `hit_limit_down`, limit prices, status/category fields, and source metadata only when truthfully available
- sort output deterministically by `trade_date`, `symbol`, and `limit_type`
- deduplicate exact duplicate rows deterministically
- fail clearly on malformed payloads, missing required source fields, invalid trade dates, invalid numeric values, unsupported datasets, invalid symbols, route signature incompatibility, or schema/normalization errors

### 2. Route and source boundary

- Prefer no-credential AKShare A-share limit-up/down routes available in the local AKShare version.
- Candidate local AKShare route names observed by the controller include `stock_zt_pool_em`, `stock_zt_pool_dtgc_em`, `stock_zt_pool_zbgc_em`, `stock_zt_pool_previous_em`, `stock_zt_pool_strong_em`, and `stock_zt_pool_sub_new_em`; the execution window must still verify the selected route shape with deterministic fixtures.
- Route selection must be bounded and explicit. A trade-date pool route with post-filtering is acceptable.
- Do not add Tushare, credentialed fallback, browser scraping, cookies, tokens, or private account data.
- Do not add broad A-share universe ingestion, full-history backfill, scheduler logic, storage refresh orchestration, cross-source fallback, scanner ranking, stock picking, trading signals, or strategy rules.
- Network/proxy/DNS/TLS/upstream/source availability failures may be classified for live skip diagnostics, but adapter/schema/normalization and AKShare function argument/signature issues must remain hard failures.

### 3. Source capability truth

If the dataset has working offline adapter coverage and gated live smoke evidence, update source capability truth conservatively:

- `a_share_limit_up_down`: use `partial` if this task validates only a narrow public-source slice
- update `gap_reason`, `recommended_handoff_theme`, and source-family alignment only as needed to reflect public AKShare coverage and remaining breadth/history limitations
- update `source_catalog.py` only if implemented public AKShare coverage makes catalog dataset coverage inconsistent
- do not mark the capability `covered` unless the implementation genuinely satisfies the full trading-grade capability definition

Do not change unrelated capabilities except to preserve tests.

### 4. Offline tests

Add deterministic offline tests proving:

- adapter satisfies `SourceAdapter`
- `DatasetName.LIMIT_UP_DOWN_EVENTS` is accepted and unsupported datasets fail clearly
- `fetch_source_result(...)` records pass `DatasetRegistry.validate_record(...)`
- bounded trade-date request behavior works and unbounded or invalid date requests fail clearly
- canonical and accepted bare A-share symbol handling works when symbol filtering is supported
- invalid HK, ETF, fund, index, malformed, and unsupported symbols fail clearly when symbol filtering is requested
- DataFrame-like and list-of-mapping payload conversion works
- required date parsing works and invalid dates fail clearly
- numeric parsing accepts supported source formats and rejects invalid values
- limit-up and limit-down route rows map to truthful `limit_type`, `hit_limit_up`, and `hit_limit_down` values
- optional route-specific status/category fields remain optional and source-truth based
- records are sorted and duplicate rows are deduplicated
- malformed payloads and missing required source fields fail clearly
- AKShare route argument/signature compatibility errors are not classified as live environment/source unavailable
- default tests remain offline-safe; patch network helpers where useful

### 5. Mandatory live smoke test

Because TASK-048 is a real-source adapter task, gated live smoke coverage is mandatory.

Add `tests/datahub/test_akshare_a_share_limit_up_down_live.py` or equivalent that:

- is skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1`
- uses no credentials
- fetches a minimal bounded live sample for one recent or stable A-share trade date supported by the selected public route
- validates at least one record through `DatasetRegistry.validate_record(...)`
- asserts `source=akshare_cn_hk_public_family`, `market=A_SHARE`, and A-share symbol output
- classifies environment/source unavailability as explicit `skipTest(...)`
- preserves adapter/schema/normalization and AKShare function argument/signature issues as failures

If the live-enabled run fails or skips due to network/proxy/DNS/TLS/upstream/source availability, the report must include root-cause evidence and feasible repository-level fixes attempted. Controller closure will require the rework/review/integration gate in `AGENTS.md`.

## Do Not Implement

Do not implement:

- broad A-share universe ingestion
- full limit-up/down history backfill
- Tushare or other credentialed adapters
- source routes requiring private credentials, cookies, or tokens
- storage refresh orchestration
- feature calculations
- scanner ranking or stock picking
- strategy, backtest, portfolio, signal, risk, notification, AI, UI, or automated trading logic

## Testing Requirements

Default tests must remain offline.

Run:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Run focused tests, likely:

`python3 -m unittest tests/datahub/test_akshare_a_share_limit_up_down_adapter.py`

`python3 -m unittest -v tests/datahub/test_akshare_a_share_limit_up_down_live.py`

Run related regressions if shared AKShare parsing or symbol behavior is touched:

`python3 -m unittest tests/datahub/test_akshare_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_a_share_margin_financing_lending_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_a_share_company_announcements_adapter.py`

`python3 -m unittest tests/datahub/test_source.py`

Run dataset/source-capability/catalog tests if those files change:

`python3 -m unittest tests/datahub/test_datasets.py`

`python3 -m unittest tests/datahub/test_source_capabilities.py`

`python3 -m unittest tests/datahub/test_source_catalog.py`

Run gated live smoke when enabled:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_limit_up_down_live.py`

If any command cannot run, report the exact command and reason in `coordination/reports/TASK-048_REPORT.md`.

## Acceptance Criteria

The task is acceptable when:

- AKShare A-share limit-up/down adapter coverage exists under `quant/datahub/**`
- records for `LIMIT_UP_DOWN_EVENTS` validate against `DatasetRegistry`
- scope remains limited to `market=A_SHARE` and `source=akshare_cn_hk_public_family`
- offline tests pass and remain deterministic
- default tests remain offline-safe
- date bounds, route selection, payload parsing, symbol handling if supported, numeric parsing, sorting, deduplication, malformed payload, unsupported dataset, route compatibility, and source-unavailability boundaries are covered
- gated live smoke exists and result is truthfully recorded
- live-enabled PASS is provided for closure; if live-enabled skip/fail occurs because of network/proxy/DNS/TLS/upstream/source availability, the report includes root-cause evidence and feasible fixes attempted, and controller closure requires the rework/review/integration gate in `AGENTS.md`
- no future-phase module contains new logic
- report exists at `coordination/reports/TASK-048_REPORT.md`

## Report Path

`coordination/reports/TASK-048_REPORT.md`

## Review Path

`coordination/reviews/TASK-048_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-048_INTEGRATION.md`
