# TASK-051: DataHub AKShare ETF/Fund Flow Adapter

## Task ID

TASK-051

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2.5: DataHub Trading-Grade Source Capability

## Context

TASK-050 has been accepted, integrated, and controller-closed. It added a narrow public AKShare A-share `MINUTE_BARS` adapter slice, moved `a_share_minute_bars` to `partial`, kept default tests offline-safe, and provided live-enabled PASS evidence.

Phase 2.5 remains open because required trading-grade source capabilities still include planned or partial DataHub source-capability work. The next executable gap is `fund_flow`: TASK-042 added the stable `DatasetName.FUND_FLOW` contract, but no ETF/fund flow adapter slice is implemented yet.

Current source-capability truth marks `fund_flow` as `planned` with credentialed Tushare listed as a known source family. This task should first attempt a narrow no-credential public AKShare ETF/fund flow or share-change source slice. Local AKShare route names observed by the controller include `fund_etf_scale_sse`, `fund_etf_scale_szse`, and related ETF/fund routes such as `fund_etf_fund_info_em`; the execution window must verify selected route shape with deterministic fixtures and gated live smoke before updating capability truth.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-051_DATAHUB_AKSHARE_FUND_FLOW_ADAPTER.md`
- `quant/datahub/datasets.py`
- `quant/datahub/source.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `quant/datahub/adapters/akshare.py`
- relevant existing AKShare fund/ETF adapter and live-smoke tests under `tests/datahub/`

## Goal

Implement a narrow no-credential AKShare-backed ETF/fund flow adapter slice that produces validated records for:

- `DatasetName.FUND_FLOW`

The first source slice should support one requested ETF/fund code and one bounded date or recent-source request, preserving source-fact flow/share-change semantics only.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-051_REPORT.md`

Suggested implementation locations:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py` only if exports need adjustment
- `quant/datahub/datasets.py` only if verified public-source evidence requires minimal source-truth hardening of `FUND_FLOW` requiredness
- `quant/datahub/source_capabilities.py` only to update `fund_flow` capability truth after implementation
- `quant/datahub/source_catalog.py` only if verified public AKShare coverage makes catalog truth inconsistent
- `tests/datahub/test_akshare_fund_flow_adapter.py`
- `tests/datahub/test_akshare_fund_flow_live.py`
- focused existing tests under `tests/datahub/` if shared fund/ETF parsing, source catalog, source capability, or AKShare behavior changes

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

### 1. AKShare ETF/fund flow adapter slice

Add a narrow adapter for:

- source id: `akshare_cn_hk_public_family`
- source display name: `AKShare CN/HK Public Family`
- supported dataset in this task:
  - `DatasetName.FUND_FLOW`
- initial market scope: one requested ETF/fund code and one bounded source request

The adapter should:

- implement the existing `SourceAdapter` protocol and `SourceResult` conventions
- use no credentials, cookies, tokens, browser session state, or private account data
- reject unsupported datasets clearly
- require exactly one ETF/fund code unless a selected public route only exposes an exchange/date table and the adapter post-filters to exactly one requested fund code
- accept stable local ETF/fund code style used by existing DataHub fund adapters
- reject A-share stock, HK stock, index, malformed, missing, and multiple symbols clearly
- require bounded request parameters where the selected route supports dates; reject unbounded full-history or broad all-fund ingestion
- set `market=ETF_FUND`
- set `source=akshare_cn_hk_public_family`
- set `schema_version` from `DatasetRegistry`
- set `ingested_at` from an injectable clock for deterministic tests
- support DataFrame-like and list-of-mapping payloads in offline fixtures
- normalize source fields into the `FUND_FLOW` contract without inventing values the source does not provide
- populate `fund_code`, `market`, `trade_date`, and at least one truthful flow/share-change metric supported by the selected route
- populate `net_inflow`, `subscription_amount`, `redemption_amount`, `shares_change`, and `source_ts` only when truthfully available from the source or from an explicitly documented source formula
- sort output deterministically by `fund_code`, `trade_date`
- deduplicate exact duplicate rows deterministically
- fail clearly on malformed payloads, missing required source fields, invalid dates, invalid numeric values, unsupported datasets, invalid fund codes, route signature incompatibility, or schema/normalization errors

If verified public AKShare routes cannot truthfully provide currently required `net_inflow` but can provide a useful source-fact `shares_change` / scale-change slice, the execution window may make a minimal `DatasetName.FUND_FLOW` schema hardening change in `quant/datahub/datasets.py`:

- keep `fund_code`, `market`, `trade_date`, `source`, `ingested_at`, and `schema_version` required
- make `net_inflow` optional only with source evidence recorded in the report and covered by tests
- do not add derived feature fields or compute economic flow values from prices/NAV unless the source payload or documentation explicitly defines that computation

### 2. Route and source boundary

- Prefer no-credential AKShare ETF/fund routes available in the local AKShare version.
- Candidate local AKShare route names observed by the controller include `fund_etf_scale_sse`, `fund_etf_scale_szse`, and `fund_etf_fund_info_em`; the execution window must still verify selected route behavior with deterministic fixtures.
- Route selection must be bounded and explicit. It may fetch an exchange/date table and filter to the requested fund code if the public source does not offer a direct one-fund endpoint.
- Do not add Tushare, credentialed fallback, browser scraping, cookies, tokens, or private account data.
- Do not add broad ETF/fund universe ingestion, full-history backfill, scheduler logic, storage refresh orchestration, cross-source fallback, feature calculation, scanner ranking, stock/fund picking, trading signals, or strategy rules.
- Network/proxy/DNS/TLS/upstream/source availability failures may be classified for live skip diagnostics, but adapter/schema/normalization and AKShare function argument/signature issues must remain hard failures.

### 3. Source capability truth

If the dataset has working offline adapter coverage and gated live smoke evidence, update source capability truth conservatively:

- `fund_flow`: use `partial` if this task validates only a narrow public-source one-fund or exchange/date-table slice
- add `akshare_cn_hk_public_family` to `source_family_ids` only if the selected public AKShare route is actually implemented and validated
- update `gap_reason` and `recommended_handoff_theme` only as needed to reflect public AKShare coverage and remaining breadth/history limitations
- update `source_catalog.py` only if implemented public AKShare coverage makes catalog dataset coverage inconsistent
- do not mark the capability `covered` unless the implementation genuinely satisfies the full trading-grade capability definition

Do not change unrelated capabilities except to preserve tests.

### 4. Offline tests

Add deterministic offline tests proving:

- adapter satisfies `SourceAdapter`
- `DatasetName.FUND_FLOW` is accepted and unsupported datasets fail clearly
- `fetch_source_result(...)` records pass `DatasetRegistry.validate_record(...)`
- bounded request behavior works and unbounded or invalid request parameters fail clearly when applicable
- accepted ETF/fund code handling works
- invalid A-share stock, HK stock, index, malformed, missing, and multiple symbols fail clearly
- DataFrame-like and list-of-mapping payload conversion works
- required date parsing works and invalid dates fail clearly
- numeric parsing accepts supported source formats and rejects invalid flow/share-change values
- optional `net_inflow`, `subscription_amount`, `redemption_amount`, `shares_change`, and `source_ts` remain source-truth based
- records are sorted and duplicate rows are deduplicated
- malformed payloads and missing required source fields fail clearly
- AKShare route argument/signature compatibility errors are not classified as live environment/source unavailable
- default tests remain offline-safe; patch network helpers where useful

### 5. Mandatory live smoke test

Because TASK-051 is a real-source adapter task, gated live smoke coverage is mandatory.

Add `tests/datahub/test_akshare_fund_flow_live.py` or equivalent that:

- is skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1`
- uses no credentials
- fetches a minimal bounded live sample for one stable ETF/fund code supported by the selected public route
- validates at least one record through `DatasetRegistry.validate_record(...)`
- asserts `source=akshare_cn_hk_public_family`, `market=ETF_FUND`, stable `fund_code`, and valid `trade_date`
- classifies environment/source unavailability as explicit `skipTest(...)`
- preserves adapter/schema/normalization and AKShare function argument/signature issues as failures

If the live-enabled run fails or skips due to network/proxy/DNS/TLS/upstream/source availability, the report must include root-cause evidence and feasible repository-level fixes attempted. Controller closure will require the rework/review/integration gate in `AGENTS.md`.

## Do Not Implement

Do not implement:

- Tushare or other credentialed adapters
- source routes requiring private credentials, cookies, or tokens
- broad ETF/fund universe ingestion
- full fund-flow history backfill
- storage refresh orchestration
- feature calculations
- scanner ranking or stock/fund picking
- strategy, backtest, portfolio, signal, risk, notification, AI, UI, or automated trading logic

## Testing Requirements

Default tests must remain offline.

Run:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Run focused tests, likely:

`python3 -m unittest tests/datahub/test_akshare_fund_flow_adapter.py`

`python3 -m unittest -v tests/datahub/test_akshare_fund_flow_live.py`

Run related regressions if shared AKShare parsing, source catalog, source capability, fund code, or dataset behavior changes:

`python3 -m unittest tests/datahub/test_akshare_fund_profile_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_etf_daily_bar_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_etf_daily_bar_live.py`

`python3 -m unittest tests/datahub/test_source.py`

`python3 -m unittest tests/datahub/test_datasets.py`

`python3 -m unittest tests/datahub/test_source_capabilities.py`

`python3 -m unittest tests/datahub/test_source_catalog.py`

Run gated live smoke when enabled:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_fund_flow_live.py`

If any command cannot run, report the exact command and reason in `coordination/reports/TASK-051_REPORT.md`.

## Acceptance Criteria

The task is acceptable when:

- AKShare ETF/fund `FUND_FLOW` adapter coverage exists under `quant/datahub/**`
- records for `FUND_FLOW` validate against `DatasetRegistry`
- scope remains limited to `market=ETF_FUND` and `source=akshare_cn_hk_public_family`
- offline tests pass and remain deterministic
- default tests remain offline-safe
- bounded request, route selection, payload parsing, fund-code handling, date parsing, numeric parsing, sorting, deduplication, malformed payload, unsupported dataset, route compatibility, and source-unavailability boundaries are covered
- gated live smoke exists and result is truthfully recorded
- live-enabled PASS is provided for closure; if live-enabled skip/fail occurs because of network/proxy/DNS/TLS/upstream/source availability, the report includes root-cause evidence and feasible fixes attempted, and controller closure requires the rework/review/integration gate in `AGENTS.md`
- no future-phase module contains new logic
- report exists at `coordination/reports/TASK-051_REPORT.md`

## Report Path

`coordination/reports/TASK-051_REPORT.md`

## Review Path

`coordination/reviews/TASK-051_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-051_INTEGRATION.md`
