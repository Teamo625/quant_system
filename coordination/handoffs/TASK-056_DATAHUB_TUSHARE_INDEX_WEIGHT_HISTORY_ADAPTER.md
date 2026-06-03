# TASK-056: DataHub Tushare Index Weight History Adapter

## Task ID

TASK-056

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2.5: DataHub Trading-Grade Source Capability

## Context

TASK-055 has been accepted by Review and integrated. It added the explicit DataHub contract:

- `DatasetName.INDEX_WEIGHT_HISTORY`

`index_weight_history` now maps to this dedicated dataset and remains conservatively `planned`. The source catalog exposes `INDEX_WEIGHT_HISTORY` only under the credentialed `tushare_pro_cn_core` source family. Public AKShare routes visible locally provide latest constituent/weight snapshots, not a reliable index x symbol x effective-date weight-history source. This task should therefore implement the next bounded credentialed source-capability slice against the TASK-055 contract.

This task must not add FeatureHub calculations, scanner ranking, strategy, backtest, portfolio, signal, risk, notification, AI, UI, automated trading, broad local collection, full-history backfill, or derived trading-signal logic.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-056_DATAHUB_TUSHARE_INDEX_WEIGHT_HISTORY_ADAPTER.md`
- `quant/datahub/datasets.py`
- `quant/datahub/source.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- relevant existing adapter patterns under `quant/datahub/adapters/`
- relevant existing source adapter and live-smoke tests under `tests/datahub/`

## Goal

Implement a narrow Tushare Pro-backed index weight-history adapter slice that produces validated source-fact records for:

- `DatasetName.INDEX_WEIGHT_HISTORY`

The first source slice should support one requested China index code and one bounded trade-date or date-range request. It should prove that the credentialed source family can populate the explicit TASK-055 contract while preserving offline default tests and truthful gated live-smoke reporting.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-056_REPORT.md`

Suggested implementation locations:

- `quant/datahub/adapters/tushare.py` or another local adapter module that matches existing repository style
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py` only if exports need adjustment
- `quant/datahub/source_capabilities.py` only to update `index_weight_history` capability truth after implementation
- `quant/datahub/source_catalog.py` only if implemented coverage makes catalog truth inconsistent
- `tests/datahub/test_tushare_index_weight_history_adapter.py`
- `tests/datahub/test_tushare_index_weight_history_live.py`
- focused existing tests under `tests/datahub/` if shared source, dataset, catalog, or capability behavior changes

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

### 1. Tushare index weight-history adapter slice

Add a narrow credentialed adapter for:

- source id: `tushare_pro_cn_core`
- source display name: `Tushare Pro CN Core`
- supported dataset in this task:
  - `DatasetName.INDEX_WEIGHT_HISTORY`
- initial market scope: China index weight history for one requested index code and a bounded trade-date/date-range request

The adapter should:

- implement the existing `SourceAdapter` protocol and `SourceResult` conventions
- load credentials only from environment variables such as `TUSHARE_TOKEN`, never from committed files or hard-coded values
- allow dependency injection for the Tushare client/API callable so offline tests need no SDK, credentials, or network
- reject unsupported datasets clearly
- require exactly one China index identifier
- accept canonical repository index identifiers such as `000300.CN_INDEX`
- accept common Tushare-style source identifiers such as `000300.SH` or `399300.SZ` only when they can be converted truthfully to canonical output `index_code`
- reject malformed, missing, multiple, stock, ETF/fund, HK, and unsupported index identifiers clearly
- require bounded request parameters; reject unbounded requests
- support either one `trade_date` request or a bounded `start_date` / `end_date` request, depending on the selected route semantics
- set `market=CN_A`
- set `source=tushare_pro_cn_core`
- set `schema_version` from `DatasetRegistry`
- set `ingested_at` from an injectable clock for deterministic tests
- support DataFrame-like and list-of-mapping payloads in offline fixtures
- normalize source fields into the `INDEX_WEIGHT_HISTORY` contract without inventing values the source does not provide
- populate `index_code`, `symbol`, `effective_date`, and `weight`
- normalize `weight` to percentage units compatible with TASK-055 validation; if upstream returns fractional weights, convert them to percentage before validation and set `weight_unit` truthfully
- populate optional `rebalance_date`, `out_date`, `source_route`, and `source_ts` only when truthfully available
- sort output deterministically by `index_code`, `effective_date`, and `symbol`
- deduplicate exact duplicate rows deterministically
- fail clearly on malformed payloads, missing required source fields, invalid dates, invalid symbols, invalid weights, unsupported datasets, missing credentials in live mode, route signature incompatibility, or schema/normalization errors

### 2. Route and credential boundary

- Prefer the official Tushare Pro index weight-history route exposed by the installed SDK/API client, commonly documented as `index_weight`.
- The execution window must verify the selected route shape with deterministic fixtures before relying on it.
- Do not add public AKShare fallback for `INDEX_WEIGHT_HISTORY` unless the route provides truthful effective-date history semantics; latest snapshot-only routes must not be treated as weight history.
- Do not commit credentials, tokens, cookies, private account data, browser session state, or private config.
- Do not add browser scraping, broad index universe ingestion, full-history backfill, scheduler logic, storage refresh orchestration, cross-source fallback, scanner ranking, stock picking, trading signals, or strategy rules.
- Credential-missing live skips must be reported as operator action required, not as source coverage evidence.
- Network/proxy/DNS/TLS/upstream/source availability failures may be classified for live skip diagnostics, but adapter/schema/normalization, credential/authentication, and SDK route argument/signature issues must remain hard failures unless the report proves they are environment-only and not repository-fixable.

### 3. Source capability truth

If the dataset has working offline adapter coverage and gated live smoke evidence with real credentials, update source capability truth conservatively:

- `index_weight_history`: use `partial` if this task validates only a narrow one-index/date-slice credentialed source adapter
- keep `source_family_ids=("tushare_pro_cn_core",)` unless additional truthful coverage is implemented
- update `gap_reason` and `recommended_handoff_theme` to reflect implemented bounded credentialed coverage and remaining breadth/history/index-universe limitations
- do not mark the capability `covered` unless the implementation genuinely satisfies the full trading-grade capability definition

If live-enabled execution cannot run because `TUSHARE_TOKEN` or the Tushare SDK is absent, keep capability truth conservative and record the exact operator action required in the report.

Do not change unrelated capabilities except to preserve tests.

### 4. Offline tests

Add deterministic offline tests proving:

- adapter satisfies `SourceAdapter`
- `DatasetName.INDEX_WEIGHT_HISTORY` is accepted and unsupported datasets fail clearly
- `fetch_source_result(...)` records pass `DatasetRegistry.validate_record(...)`
- credential loading is not required for injected offline fixtures
- missing credentials fail clearly when the non-injected live/client path is used
- bounded trade-date/date-range request behavior works and unbounded requests fail clearly
- canonical and accepted source-native index identifiers normalize correctly
- invalid stock, ETF, fund, HK, malformed, missing, and multiple symbols fail clearly
- DataFrame-like and list-of-mapping payload conversion works
- date parsing maps source date fields to `effective_date`
- numeric parsing normalizes weight units into percentage validation semantics
- optional `weight_unit`, `rebalance_date`, `out_date`, `source_route`, and `source_ts` remain source-truth based
- records are sorted and duplicate rows are deduplicated
- malformed payloads and missing required source fields fail clearly
- Tushare route argument/signature compatibility errors are not classified as live environment/source unavailable
- default tests remain offline-safe; patch network helpers where useful

### 5. Mandatory live smoke test

Because TASK-056 is a real-source adapter task, gated live smoke coverage is mandatory.

Add `tests/datahub/test_tushare_index_weight_history_live.py` or equivalent that:

- is skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1`
- requires `TUSHARE_TOKEN` or the repository-standard credential environment variable chosen by the implementation
- uses no committed credentials, cookies, browser state, or private account files
- fetches a minimal bounded live sample for one stable China index such as `000300.CN_INDEX` and one recent bounded date/date range supported by the selected Tushare route
- validates at least one record through `DatasetRegistry.validate_record(...)`
- asserts `source=tushare_pro_cn_core`, `market=CN_A`, canonical `index_code`, canonical A-share constituent `symbol`, valid `effective_date`, and valid percentage `weight`
- classifies network/proxy/DNS/TLS/upstream unavailability as explicit `skipTest(...)` with root-cause context
- treats missing credentials as explicit operator-action skip, not as source coverage evidence
- preserves adapter/schema/normalization, authentication, permission, quota, and route argument/signature issues as failures unless the report proves they are not repository-fixable

If the live-enabled run fails or skips due to network/proxy/DNS/TLS/upstream/source availability, the report must include root-cause evidence and feasible repository-level fixes attempted. Controller closure will require the rework/review/integration gate in `AGENTS.md`.

If the live-enabled run skips only because credentials or SDK installation are absent, the report must say `SKIP`, name the missing prerequisite, and state that live source coverage is not proven until an operator reruns the smoke with credentials.

## Do Not Implement

Do not implement:

- public AKShare snapshot routes as weight history unless effective-date history is truthfully available
- broad index universe ingestion
- full index-weight history backfill
- scheduler or warehouse refresh orchestration
- cross-source fallback
- feature calculations
- scanner ranking or stock picking
- strategy, backtest, portfolio, signal, risk, notification, AI, UI, or automated trading logic

## Testing Requirements

Default tests must remain offline.

Run:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Run focused tests, likely:

`python3 -m unittest tests/datahub/test_tushare_index_weight_history_adapter.py`

`python3 -m unittest -v tests/datahub/test_tushare_index_weight_history_live.py`

Run related regressions if shared source, dataset, source catalog, source capability, symbol, or adapter behavior changes:

`python3 -m unittest tests/datahub/test_source.py`

`python3 -m unittest tests/datahub/test_datasets.py`

`python3 -m unittest tests/datahub/test_source_capabilities.py`

`python3 -m unittest tests/datahub/test_source_catalog.py`

`python3 -m unittest tests/datahub/test_akshare_index_constituents_adapter.py`

Run gated live smoke when explicitly enabled and credentials are locally available:

`QUANT_SYSTEM_LIVE_TESTS=1 TUSHARE_TOKEN=<local-token> python3 -m unittest -v tests/datahub/test_tushare_index_weight_history_live.py`

If any command cannot run, report the exact command and reason in `coordination/reports/TASK-056_REPORT.md`.

## Acceptance Criteria

The task is acceptable when:

- Tushare-backed `INDEX_WEIGHT_HISTORY` adapter coverage exists under `quant/datahub/**`
- records validate against `DatasetName.INDEX_WEIGHT_HISTORY`
- scope remains limited to source facts for `source=tushare_pro_cn_core`
- offline tests pass and remain deterministic
- default tests remain offline-safe
- bounded request, route selection, credential handling, payload parsing, index/symbol handling, date parsing, weight normalization, sorting, deduplication, malformed payload, unsupported dataset, route compatibility, and source-unavailability boundaries are covered
- gated live smoke exists and result is truthfully recorded
- live-enabled PASS is provided when credentials and SDK are available; if live-enabled skip/fail occurs because of network/proxy/DNS/TLS/upstream/source availability, the report includes root-cause evidence and feasible fixes attempted, and controller closure requires the rework/review/integration gate in `AGENTS.md`
- if live-enabled skip is due only to missing credentials or missing local SDK, the report records the missing prerequisite and does not claim proven live source coverage
- no future-phase module contains new logic
- report exists at `coordination/reports/TASK-056_REPORT.md`

## Report Path

`coordination/reports/TASK-056_REPORT.md`

## Review Path

`coordination/reviews/TASK-056_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-056_INTEGRATION.md`
