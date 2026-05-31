# TASK-045: DataHub AKShare A-share Margin Financing/Lending Adapter

## Task ID

TASK-045

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2.5: DataHub Trading-Grade Source Capability

## Context

TASK-044 has been accepted, integrated, and controller-closed. It added a narrow public AKShare A-share financial-statement and financial-indicator adapter slice and moved `a_share_financial_statements` and `a_share_financial_indicators` to `partial`.

Phase 2.5 remains open because required trading-grade source capabilities still include planned A-share margin financing and securities lending coverage. TASK-042 already added the stable contract:

- `DatasetName.MARGIN_FINANCING_LENDING`

This task should implement the next no-credential public-source DataHub adapter slice without using private credentials.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-045_DATAHUB_AKSHARE_A_SHARE_MARGIN_FINANCING_LENDING_ADAPTER.md`
- `quant/datahub/datasets.py`
- `quant/datahub/source.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `quant/datahub/adapters/akshare.py`
- relevant existing AKShare adapter tests under `tests/datahub/`

## Goal

Implement a narrow AKShare-backed A-share margin financing and securities lending adapter slice that produces validated records for:

- `DatasetName.MARGIN_FINANCING_LENDING`

The task should prove that the stable margin financing/lending contract can be populated from a bounded no-credential public A-share route while preserving deterministic offline tests and gated live smoke behavior.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-045_REPORT.md`

Suggested implementation locations:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py` only if exports need adjustment
- `quant/datahub/source_capabilities.py` only to update A-share margin financing/lending capability truth after implementation
- `quant/datahub/source_catalog.py` only for minimal public-source alignment if the public AKShare route is implemented and catalog coverage is inconsistent
- `tests/datahub/test_akshare_a_share_margin_financing_lending_adapter.py`
- `tests/datahub/test_akshare_a_share_margin_financing_lending_live.py`
- focused existing tests under `tests/datahub/` if shared behavior changes

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

### 1. AKShare A-share margin financing/lending adapter slice

Add a narrow adapter for:

- source id: `akshare_cn_hk_public_family`
- source display name: `AKShare CN/HK Public Family`
- supported dataset in this task:
  - `DatasetName.MARGIN_FINANCING_LENDING`
- initial market scope: bounded A-share symbol/date or exchange-table slice sufficient to return one requested A-share stock symbol

The adapter should:

- implement the existing `SourceAdapter` protocol and `SourceResult` conventions
- use no credentials, cookies, tokens, browser session state, or private account data
- reject unsupported datasets clearly
- require exactly one A-share stock symbol unless an existing local source-query convention requires an exchange/date query and post-filtering to that symbol
- accept canonical exchange-qualified A-share symbols such as `600000.SH`, `000001.SZ`, and `430047.BJ` when supported by the selected route
- accept bare six-digit A-share codes only when existing local adapter style supports them, then normalize output `symbol` to canonical exchange-qualified form
- reject HK, ETF/fund, index, malformed, missing, and multiple symbols clearly
- set `market=A_SHARE`
- set `source=akshare_cn_hk_public_family`
- set `schema_version` from `DatasetRegistry`
- set `ingested_at` from an injectable clock for deterministic tests
- support DataFrame-like and list-of-mapping payloads in offline fixtures
- normalize available source fields into the existing `MARGIN_FINANCING_LENDING` contract without inventing values the source does not provide
- keep optional fields optional when the public route does not provide a metric
- sort output deterministically by `trade_date` and `symbol`
- deduplicate exact duplicate rows deterministically
- fail clearly on malformed payloads, missing required source fields, invalid trade dates, invalid numeric values, unsupported datasets, invalid symbols, or multiple symbols

### 2. Route and source boundary

- Prefer no-credential AKShare A-share margin financing/securities lending routes available in the local AKShare version.
- Candidate local AKShare route names observed by the controller include `stock_margin_detail_sse`, `stock_margin_detail_szse`, `stock_margin_sse`, `stock_margin_szse`, `stock_margin_account_info`, and `stock_margin_underlying_info_szse`; the execution window must still verify the selected route shape with deterministic fixtures.
- Route selection must be bounded and explicit. It may fetch an exchange/date table and filter to the requested symbol if the public source does not offer a direct one-symbol endpoint.
- Do not add Tushare, credentialed fallback, browser scraping, cookies, tokens, or private account data.
- Do not add broad A-share universe ingestion, full-history backfill, scheduler logic, storage refresh orchestration, or cross-source fallback.
- Network/proxy/DNS/TLS/upstream/source availability failures may be classified for live skip diagnostics, but adapter/schema/normalization issues must remain hard failures.

### 3. Source capability truth

If the dataset has working offline adapter coverage and gated live smoke evidence, update source capability truth conservatively:

- `a_share_margin_financing_and_lending`: use `partial` if this task validates only a narrow public-source slice
- update `gap_reason`, `recommended_handoff_theme`, and source-family alignment only as needed to reflect public AKShare coverage and remaining breadth/history limitations
- do not mark the capability `covered` unless the implementation genuinely satisfies the full trading-grade capability definition

Do not change unrelated capabilities except to preserve tests.

### 4. Offline tests

Add deterministic offline tests proving:

- adapter satisfies `SourceAdapter`
- `DatasetName.MARGIN_FINANCING_LENDING` is accepted and unsupported datasets fail clearly
- `fetch_source_result(...)` records pass `DatasetRegistry.validate_record(...)`
- canonical and accepted bare A-share symbol handling works
- invalid HK, ETF, fund, index, malformed, missing, and multiple symbols fail clearly
- DataFrame-like and list-of-mapping payload conversion works
- required trade-date parsing works and invalid dates fail clearly
- numeric parsing accepts supported source formats and rejects invalid values
- records are sorted and duplicate rows are deduplicated
- malformed payloads and missing required source fields fail clearly
- default tests remain offline-safe; patch network helpers where useful

### 5. Mandatory live smoke test

Because TASK-045 is a real-source adapter task, gated live smoke coverage is mandatory.

Add `tests/datahub/test_akshare_a_share_margin_financing_lending_live.py` or equivalent that:

- is skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1`
- uses no credentials
- fetches a minimal bounded live sample for one stable A-share symbol supported by the selected public route
- validates at least one record through `DatasetRegistry.validate_record(...)`
- asserts `source=akshare_cn_hk_public_family`, `market=A_SHARE`, and canonical A-share symbol
- classifies environment/source unavailability as explicit `skipTest(...)`
- preserves adapter/schema/normalization issues as failures

If the live-enabled run fails or skips due to network/proxy/DNS/TLS/upstream/source availability, the report must include root-cause evidence and feasible repository-level fixes attempted. Controller closure will require the rework/review/integration gate in `AGENTS.md`.

## Do Not Implement

Do not implement:

- broad A-share universe ingestion
- full margin financing/lending history backfill
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

`python3 -m unittest tests/datahub/test_akshare_a_share_margin_financing_lending_adapter.py`

`python3 -m unittest -v tests/datahub/test_akshare_a_share_margin_financing_lending_live.py`

Run related regressions if shared AKShare parsing or symbol behavior is touched:

`python3 -m unittest tests/datahub/test_akshare_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_a_share_instrument_master_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_a_share_financial_data_adapter.py`

`python3 -m unittest tests/datahub/test_source.py`

Run source-capability/catalog tests if those files change:

`python3 -m unittest tests/datahub/test_source_capabilities.py`

`python3 -m unittest tests/datahub/test_source_catalog.py`

Run gated live smoke when enabled:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_margin_financing_lending_live.py`

If any command cannot run, report the exact command and reason in `coordination/reports/TASK-045_REPORT.md`.

## Acceptance Criteria

The task is acceptable when:

- AKShare A-share margin financing/lending adapter coverage exists under `quant/datahub/**`
- records for `MARGIN_FINANCING_LENDING` validate against `DatasetRegistry`
- scope remains limited to `market=A_SHARE` and `source=akshare_cn_hk_public_family`
- offline tests pass and remain deterministic
- default tests remain offline-safe
- symbol parsing, payload parsing, trade-date parsing, numeric parsing, sorting, deduplication, malformed payload, unsupported dataset, and symbol-rejection boundaries are covered
- gated live smoke exists and result is truthfully recorded
- live-enabled PASS is provided for closure; if live-enabled skip/fail occurs because of network/proxy/DNS/TLS/upstream/source availability, the report includes root-cause evidence and feasible fixes attempted, and controller closure requires the rework/review gate in `AGENTS.md`
- no future-phase module contains new logic
- report exists at `coordination/reports/TASK-045_REPORT.md`

## Report Path

`coordination/reports/TASK-045_REPORT.md`

## Review Path

`coordination/reviews/TASK-045_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-045_INTEGRATION.md`
