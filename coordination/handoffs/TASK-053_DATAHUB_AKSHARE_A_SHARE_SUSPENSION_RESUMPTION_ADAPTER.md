# TASK-053: DataHub AKShare A-share Suspension/Resumption Adapter

## Task ID

TASK-053

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2.5: DataHub Trading-Grade Source Capability

## Context

TASK-052 has been accepted by Review and integrated. It added the dedicated DataHub source-fact contract:

- `DatasetName.SUSPENSION_RESUMPTION_EVENTS`

`a_share_suspension_resumption` now maps to this dedicated dataset and remains conservatively `planned`. Phase 2.5 remains open because adapter-backed public-source coverage and source-taxonomy normalization for suspension/resumption events are still pending.

This task should implement the next bounded no-credential AKShare source slice against the TASK-052 contract. It must not add FeatureHub, scanner, strategy, backtest, portfolio, signal, risk, notification, AI, UI, automated trading, broad collection, or derived trading-signal logic.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-053_DATAHUB_AKSHARE_A_SHARE_SUSPENSION_RESUMPTION_ADAPTER.md`
- `quant/datahub/datasets.py`
- `quant/datahub/source.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `quant/datahub/adapters/akshare.py`
- relevant existing AKShare adapter and live-smoke tests under `tests/datahub/`

## Goal

Implement a narrow no-credential AKShare-backed A-share suspension/resumption adapter slice that produces validated source-fact records for:

- `DatasetName.SUSPENSION_RESUMPTION_EVENTS`

The task should prove that a bounded public source route can populate the TASK-052 contract while preserving deterministic offline tests and gated live smoke behavior.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-053_REPORT.md`

Suggested implementation locations:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py` only if exports need adjustment
- `quant/datahub/source_capabilities.py` only to update A-share suspension/resumption capability truth after implementation
- `quant/datahub/source_catalog.py` only if implemented public AKShare coverage makes catalog truth inconsistent
- `tests/datahub/test_akshare_a_share_suspension_resumption_adapter.py`
- `tests/datahub/test_akshare_a_share_suspension_resumption_live.py`
- focused existing tests under `tests/datahub/` if shared parsing, symbol, source catalog, source capability, or AKShare behavior changes

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

### 1. AKShare A-share suspension/resumption adapter slice

Add a narrow adapter for:

- source id: `akshare_cn_hk_public_family`
- source display name: `AKShare CN/HK Public Family`
- supported dataset in this task:
  - `DatasetName.SUSPENSION_RESUMPTION_EVENTS`
- initial market scope: one bounded A-share trade-date table slice, with optional symbol filtering only when the selected public route provides enough symbol information

The adapter should:

- implement the existing `SourceAdapter` protocol and `SourceResult` conventions
- use no credentials, cookies, tokens, browser session state, or private account data
- reject unsupported datasets clearly
- require bounded request parameters through existing `start_date` / `end_date` conventions when the selected route supports dates
- reject unbounded requests and reject multi-day date ranges unless the implementation explicitly and safely supports bounded iteration
- accept canonical exchange-qualified A-share symbols such as `600000.SH`, `000001.SZ`, and `430047.BJ` when symbol filtering is supported by the selected route
- accept bare six-digit A-share codes only when existing local adapter style supports them, then normalize output `symbol` to canonical exchange-qualified form when the source row permits it
- reject HK, ETF/fund, index, malformed, and missing symbols clearly when symbol filtering is requested
- set `market=A_SHARE`
- set `source=akshare_cn_hk_public_family`
- set `schema_version` from `DatasetRegistry`
- set `ingested_at` from an injectable clock for deterministic tests
- support DataFrame-like and list-of-mapping payloads in offline fixtures
- normalize source fields into the `SUSPENSION_RESUMPTION_EVENTS` contract without inventing values the source does not provide
- emit source-fact fields such as `event_date`, `event_type`, `start_date`, `end_date`, `reason`, `raw_status`, exchange or board metadata, and source timestamp only when truthfully available
- normalize event taxonomy to conservative contract values such as `suspension`, `resumption`, `temporary_suspension`, or `continued_suspension` only when source text supports that mapping
- preserve source text in `raw_status` or similar optional fields when taxonomy is ambiguous
- sort output deterministically by `event_date`, `symbol`, and event classification
- deduplicate exact duplicate rows deterministically
- fail clearly on malformed payloads, missing required source fields, invalid dates, invalid symbols, unsupported datasets, route signature incompatibility, or schema/normalization errors

### 2. Route and source boundary

- Prefer no-credential AKShare A-share suspension/resumption routes available in the local AKShare version.
- Candidate local AKShare route names observed by the controller include `stock_tfp_em` and `stock_zh_a_stop_em`. `news_trade_notify_suspend_baidu` exists locally but has a `cookie` parameter; do not use a cookie or any private session data.
- The execution window must verify the selected route shape with deterministic fixtures before relying on it.
- Route selection must be bounded and explicit. A trade-date table route with post-filtering is acceptable if it stays narrow and deterministic.
- Do not add Tushare, credentialed fallback, browser scraping, cookies, tokens, or private account data.
- Do not add broad A-share universe ingestion, full-history backfill, scheduler logic, storage refresh orchestration, cross-source fallback, scanner ranking, stock picking, trading signals, or strategy rules.
- Network/proxy/DNS/TLS/upstream/source availability failures may be classified for live skip diagnostics, but adapter/schema/normalization and AKShare function argument/signature issues must remain hard failures.

### 3. Source capability truth

If the dataset has working offline adapter coverage and gated live smoke evidence, update source capability truth conservatively:

- `a_share_suspension_resumption`: use `partial` if this task validates only a narrow public-source slice
- update `gap_reason`, `recommended_handoff_theme`, and source-family alignment only as needed to reflect public AKShare coverage and remaining breadth/history/taxonomy limitations
- update `source_catalog.py` only if implemented public AKShare coverage makes catalog dataset coverage inconsistent
- do not mark the capability `covered` unless the implementation genuinely satisfies the full trading-grade capability definition

Do not change unrelated capabilities except to preserve tests.

### 4. Offline tests

Add deterministic offline tests proving:

- adapter satisfies `SourceAdapter`
- `DatasetName.SUSPENSION_RESUMPTION_EVENTS` is accepted and unsupported datasets fail clearly
- `fetch_source_result(...)` records pass `DatasetRegistry.validate_record(...)`
- bounded trade-date request behavior works and unbounded or invalid date requests fail clearly
- canonical and accepted bare A-share symbol handling works when symbol filtering is supported
- invalid HK, ETF, fund, index, malformed, and unsupported symbols fail clearly when symbol filtering is requested
- DataFrame-like and list-of-mapping payload conversion works
- required date parsing works and invalid dates fail clearly
- source status text maps only to truthful event taxonomy
- ambiguous source status text is preserved without inventing a false event type
- optional `start_date`, `end_date`, `reason`, `raw_status`, exchange/board metadata, and `source_ts` remain source-truth based
- records are sorted and duplicate rows are deduplicated
- malformed payloads and missing required source fields fail clearly
- AKShare route argument/signature compatibility errors are not classified as live environment/source unavailable
- default tests remain offline-safe; patch network helpers where useful

### 5. Mandatory live smoke test

Because TASK-053 is a real-source adapter task, gated live smoke coverage is mandatory.

Add `tests/datahub/test_akshare_a_share_suspension_resumption_live.py` or equivalent that:

- is skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1`
- uses no credentials, cookies, tokens, or private browser/session state
- fetches a minimal bounded live sample for one recent or stable A-share trade date supported by the selected public route
- validates at least one record through `DatasetRegistry.validate_record(...)`
- asserts `source=akshare_cn_hk_public_family`, `market=A_SHARE`, valid A-share `symbol`, and valid event date fields
- classifies environment/source unavailability as explicit `skipTest(...)`
- preserves adapter/schema/normalization and AKShare function argument/signature issues as failures

If the live-enabled run fails or skips due to network/proxy/DNS/TLS/upstream/source availability, the report must include root-cause evidence and feasible repository-level fixes attempted. Controller closure will require the rework/review/integration gate in `AGENTS.md`.

## Do Not Implement

Do not implement:

- broad A-share universe ingestion
- full suspension/resumption history backfill
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

`python3 -m unittest tests/datahub/test_akshare_a_share_suspension_resumption_adapter.py`

`python3 -m unittest -v tests/datahub/test_akshare_a_share_suspension_resumption_live.py`

Run related regressions if shared AKShare parsing, source catalog, source capability, symbol, or dataset behavior changes:

`python3 -m unittest tests/datahub/test_akshare_a_share_corporate_actions_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_a_share_limit_up_down_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_a_share_major_activity_events_adapter.py`

`python3 -m unittest tests/datahub/test_source.py`

`python3 -m unittest tests/datahub/test_datasets.py`

`python3 -m unittest tests/datahub/test_source_capabilities.py`

`python3 -m unittest tests/datahub/test_source_catalog.py`

Run gated live smoke when enabled:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_suspension_resumption_live.py`

If any command cannot run, report the exact command and reason in `coordination/reports/TASK-053_REPORT.md`.

## Acceptance Criteria

The task is acceptable when:

- AKShare A-share suspension/resumption adapter coverage exists under `quant/datahub/**`
- records for `SUSPENSION_RESUMPTION_EVENTS` validate against `DatasetRegistry`
- scope remains limited to `market=A_SHARE` and `source=akshare_cn_hk_public_family`
- offline tests pass and remain deterministic
- default tests remain offline-safe
- bounded request, route selection, payload parsing, symbol handling if supported, date parsing, taxonomy normalization, sorting, deduplication, malformed payload, unsupported dataset, route compatibility, and source-unavailability boundaries are covered
- gated live smoke exists and result is truthfully recorded
- live-enabled PASS is provided for closure; if live-enabled skip/fail occurs because of network/proxy/DNS/TLS/upstream/source availability, the report includes root-cause evidence and feasible fixes attempted, and controller closure requires the rework/review/integration gate in `AGENTS.md`
- no future-phase module contains new logic
- report exists at `coordination/reports/TASK-053_REPORT.md`

## Report Path

`coordination/reports/TASK-053_REPORT.md`

## Review Path

`coordination/reviews/TASK-053_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-053_INTEGRATION.md`
