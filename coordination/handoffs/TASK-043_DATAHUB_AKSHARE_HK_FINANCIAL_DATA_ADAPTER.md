# TASK-043: DataHub AKShare Hong Kong Financial Data Adapter

## Task ID

TASK-043

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2.5: DataHub Trading-Grade Source Capability

## Context

TASK-042 has been accepted and integrated. It added stable DataHub dataset contracts for the required TASK-041 no-mapping gaps, including `DatasetName.FINANCIAL_STATEMENTS` and `DatasetName.FINANCIAL_INDICATORS`.

Phase 2.5 remains open because those contracts do not by themselves implement source capability. The `hk_financial_data` capability is still `planned` and maps to the public `akshare_cn_hk_public_family`, so it is the next executable adapter slice without requiring private credentials.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-043_DATAHUB_AKSHARE_HK_FINANCIAL_DATA_ADAPTER.md`
- `quant/datahub/datasets.py`
- `quant/datahub/source.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `quant/datahub/adapters/akshare.py`
- relevant existing AKShare adapter tests under `tests/datahub/`

## Goal

Implement a narrow AKShare-backed Hong Kong financial data adapter slice for one requested Hong Kong stock symbol, producing validated records for:

- `DatasetName.FINANCIAL_STATEMENTS`
- `DatasetName.FINANCIAL_INDICATORS`

This task should prove the newly contracted cross-market financial datasets can be populated from a public HK source route while preserving deterministic offline tests and gated live smoke behavior.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-043_REPORT.md`

Suggested implementation locations:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py` only if exports need adjustment
- `quant/datahub/source_capabilities.py` only to update `hk_financial_data` status/gap truth after implementation
- `quant/datahub/source_catalog.py` only for minimal alignment if tests show catalog coverage is inconsistent
- `tests/datahub/test_akshare_hk_financial_data_adapter.py`
- `tests/datahub/test_akshare_hk_financial_data_live.py`
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

### 1. AKShare HK financial adapter slice

Add a narrow adapter for:

- source id: `akshare_cn_hk_public_family`
- source display name: `AKShare CN/HK Public Family`
- supported datasets in this task:
  - `DatasetName.FINANCIAL_STATEMENTS`
  - `DatasetName.FINANCIAL_INDICATORS`
- initial market scope: one requested Hong Kong stock symbol

The adapter should:

- implement the existing `SourceAdapter` protocol and `SourceResult` conventions
- use no credentials, cookies, tokens, or private account data
- reject unsupported datasets clearly
- require exactly one HK symbol
- accept canonical `00700.HK` and bare `00700` / `700` style inputs when the local adapter style supports bare HK symbols
- normalize output `symbol` to canonical `NNNNN.HK`
- set `market=HK`
- set `source=akshare_cn_hk_public_family`
- set `schema_version` from `DatasetRegistry`
- set `ingested_at` from an injectable clock for deterministic tests
- support DataFrame-like and list-of-mapping payloads in offline fixtures
- normalize available source fields into the existing financial-statement and financial-indicator contracts without inventing values the source does not provide
- keep optional fields optional when public HK routes do not provide a metric
- sort output deterministically by report period and statement/metric dimensions
- deduplicate exact duplicate rows deterministically
- fail clearly on malformed payloads, missing required source fields, invalid dates/report periods, invalid numeric values, unsupported datasets, invalid symbols, or multiple symbols

### 2. Route and source boundary

- Prefer no-credential AKShare HK financial routes available in the local AKShare version.
- Keep route selection bounded and explicit.
- It is acceptable to support one or more report/indicator routes only when each route has deterministic offline fixtures and contract validation.
- Do not add Tushare, credentialed fallback, browser scraping, cookies, tokens, or private account data.
- Do not add broad HK universe ingestion, full-history backfill, scheduler logic, storage refresh orchestration, or cross-source fallback.
- Network/proxy/DNS/TLS/upstream/source availability failures may be classified for live skip diagnostics, but adapter/schema/normalization failures must remain hard failures.

### 3. Source capability truth

If both datasets have working offline adapter coverage and gated live smoke evidence, update `hk_financial_data` status truthfully:

- use `partial` if the task validates a narrow one-symbol slice but does not prove broad trading-grade universe coverage
- do not mark it `covered` unless the implementation genuinely satisfies the existing capability definition
- keep `gap_reason` and `recommended_handoff_theme` aligned with remaining breadth/history limitations

Do not change unrelated capabilities except to preserve tests.

### 4. Offline tests

Add deterministic offline tests proving:

- adapter satisfies `SourceAdapter`
- both supported datasets are accepted and unsupported datasets fail clearly
- `fetch_source_result(...)` records pass `DatasetRegistry.validate_record(...)`
- canonical and accepted bare HK symbol handling works
- invalid A-share, ETF, fund, malformed, missing, and multiple symbols fail clearly
- DataFrame-like and list-of-mapping payload conversion works
- required date/report-period parsing works and invalid dates fail clearly
- numeric parsing accepts supported source formats and rejects invalid values
- records are sorted and duplicate rows are deduplicated
- malformed payloads and missing required source fields fail clearly
- default tests remain offline-safe; patch network helpers where useful

### 5. Mandatory live smoke test

Because TASK-043 is a real-source adapter task, gated live smoke coverage is mandatory.

Add `tests/datahub/test_akshare_hk_financial_data_live.py` or equivalent that:

- is skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1`
- uses no credentials
- fetches a minimal bounded live sample for one liquid HK symbol, preferably `00700.HK`
- validates at least one record through `DatasetRegistry.validate_record(...)`
- asserts `source=akshare_cn_hk_public_family`, `market=HK`, and canonical HK symbol
- classifies environment/source unavailability as explicit `skipTest(...)`
- preserves adapter/schema/normalization issues as failures

If the live-enabled run fails or skips due to network/proxy/DNS/TLS/upstream/source availability, the report must include root-cause evidence and feasible repository-level fixes attempted. Controller closure will require the rework/review/integration gate in `AGENTS.md`.

## Do Not Implement

Do not implement:

- broad HK universe ingestion
- full financial history backfill
- A-share financial statement or indicator adapters
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

`python3 -m unittest tests/datahub/test_akshare_hk_financial_data_adapter.py`

`python3 -m unittest -v tests/datahub/test_akshare_hk_financial_data_live.py`

Run related regressions if shared AKShare HK adapter behavior is touched:

`python3 -m unittest tests/datahub/test_akshare_hk_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_hk_instrument_master_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_hk_valuation_snapshot_adapter.py`

`python3 -m unittest tests/datahub/test_source.py`

Run source-capability/catalog tests if those files change:

`python3 -m unittest tests/datahub/test_source_capabilities.py`

`python3 -m unittest tests/datahub/test_source_catalog.py`

Run gated live smoke when enabled:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_financial_data_live.py`

If any command cannot run, report the exact command and reason in `coordination/reports/TASK-043_REPORT.md`.

## Acceptance Criteria

The task is acceptable when:

- AKShare HK financial data adapter coverage exists for one HK symbol under `quant/datahub/**`
- records for `FINANCIAL_STATEMENTS` and `FINANCIAL_INDICATORS` validate against `DatasetRegistry`
- scope remains limited to `market=HK` and `source=akshare_cn_hk_public_family`
- offline tests pass and remain deterministic
- default tests remain offline-safe
- symbol parsing, payload parsing, date/report-period parsing, numeric parsing, sorting, deduplication, malformed payload, unsupported dataset, and symbol-rejection boundaries are covered
- gated live smoke exists and result is truthfully recorded
- live-enabled PASS is provided for closure; if live-enabled skip/fail occurs because of network/proxy/DNS/TLS/upstream/source availability, the report includes root-cause evidence and feasible fixes attempted, and controller closure requires the rework/review gate in `AGENTS.md`
- no future-phase module contains new logic
- report exists at `coordination/reports/TASK-043_REPORT.md`

## Report Path

`coordination/reports/TASK-043_REPORT.md`

## Review Path

`coordination/reviews/TASK-043_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-043_INTEGRATION.md`

## Out of Scope

Everything outside narrow AKShare Hong Kong financial-statement and financial-indicator adapter coverage is out of scope.
