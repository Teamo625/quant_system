# TASK-031: DataHub AKShare ETF/Fund Holdings Adapter

## Task ID

TASK-031

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

TASK-030 has been accepted and integrated. It completed public policy document metadata coverage for `DatasetName.POLICY_DOCUMENTS` under `macro_policy_public_sources`, including closure-ready live-enabled PASS evidence.

Phase 2 remains open. The next narrow executable source slice is ETF/fund holdings coverage. `DatasetName.FUND_HOLDINGS` already has a stable contract, and Phase 2 still requires ETF/fund holdings or composition data where available.

This task must implement only the one-fund holdings slice for `DatasetName.FUND_HOLDINGS`.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-031_DATAHUB_AKSHARE_ETF_FUND_HOLDINGS_ADAPTER.md`

## Goal

Implement a narrow AKShare-backed ETF/fund holdings adapter for `DatasetName.FUND_HOLDINGS`, focused on one requested China ETF/fund code and one bounded holdings/reporting-period slice, with deterministic offline tests and mandatory gated live smoke coverage.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-031_REPORT.md`

Suggested implementation locations:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `quant/datahub/source_catalog.py` only if strict catalog assertion alignment is required
- `tests/datahub/test_akshare_fund_holdings_adapter.py`
- `tests/datahub/test_akshare_fund_holdings_live.py`
- `tests/datahub/test_source_catalog.py` only if source-catalog expectations change

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

### 1. AKShare ETF/fund holdings adapter

Add a narrow adapter for:

- source id: `akshare_cn_hk_public_family`
- source display name: `AKShare CN/HK Public Family`
- supported dataset in this task: `DatasetName.FUND_HOLDINGS`
- initial scope: one China ETF/fund code and a bounded holdings/reporting-period sample

The adapter should:

- implement the existing `SourceAdapter` protocol
- use lazy/optional AKShare imports
- reject unsupported datasets clearly
- require exactly one ETF/fund code through `symbols`
- reject missing, multiple, empty, malformed, HK, index, stock-only, or unsupported market symbols clearly
- accept source-native bare six-digit fund codes and canonical ETF/fund codes such as `510300.ETF_CN`
- normalize output `fund_code` to a stable canonical code, preferably `510300.ETF_CN` for ETF_CN records
- support `start_date` and `end_date` by filtering normalized `report_date` where the upstream route provides report dates
- fetch only a bounded holdings slice; do not perform broad fund universe ingestion or all-fund holdings crawls
- normalize output records to `FUND_HOLDINGS` contract fields:
  - `fund_code`
  - `symbol`
  - `market`
  - `report_date`
  - `weight`
  - optional `shares`
  - optional `position_value`
  - `source`
  - optional `source_ts`
  - `ingested_at`
  - `schema_version`
- set `source=akshare_cn_hk_public_family`
- set `schema_version` from `DatasetRegistry`
- set `ingested_at` from injectable clock for deterministic tests
- normalize A-share holding symbols to a stable canonical suffix when possible, such as `600519.SH`, `000001.SZ`, or `920000.BJ`
- set `market=CN` for China-listed underlying holdings in this first slice
- preserve source-truth units for `weight`; use the DataHub contract convention that weight is a percentage value between 0 and 100
- do not invent placeholder holdings values
- support DataFrame-like payload and list-of-mapping payload fixtures
- fail clearly on malformed payload, missing required fields, invalid report date, invalid numeric values, invalid weights, unsupported dataset, unsupported symbols, or invalid required string fields

### 2. Source route guidance

Prefer a no-credential AKShare public fund holdings or portfolio route available in the installed AKShare version. Examples may include AKShare fund portfolio/holdings routes if present, but the implementation must be based on routes available locally at execution time.

Route rules:

- keep route order bounded and explicit
- do not use a full-market all-fund holdings crawl as a workaround
- do not fetch holdings for more than the requested single fund
- classify network/proxy/DNS/TLS/upstream/source availability failures for live skip diagnostics
- keep contract/normalization failures as hard failures

### 3. Duplicate and identity boundary

- The stable holdings key for duplicate checks should include at least `(fund_code, symbol, report_date)`.
- Benign exact duplicate holdings rows may be deterministically deduplicated.
- Conflicting duplicate rows for the same holdings key must hard-fail.
- If the source reports the same holding in multiple share classes or categories, preserve only records that can truthfully map to the current `FUND_HOLDINGS` contract.

### 4. Source catalog alignment

The source catalog already includes `DatasetName.FUND_HOLDINGS` under credentialed `tushare_pro_cn_core`. This task may add `DatasetName.FUND_HOLDINGS` to `akshare_cn_hk_public_family` only if the implemented AKShare route provides stable no-credential coverage for the narrow holdings slice.

Do not add broad source claims. If source-catalog expectations change, add or update deterministic offline catalog tests.

### 5. Offline tests

Add deterministic offline tests proving:

- adapter satisfies `SourceAdapter`
- `fetch_source_result(...)` records pass `DatasetRegistry.validate_record(...)`
- source payload conversion from DataFrame-like and list-of-mapping works
- canonical ETF/fund code conversion preserves stable output codes
- A-share holding symbol normalization is deterministic
- `start_date` / `end_date` filtering is deterministic when report dates are present
- missing symbols, multiple symbols, invalid fund symbols, and unsupported dataset are rejected clearly
- required field, invalid report date, optional field, invalid numeric, and invalid weight behavior is covered
- duplicate and conflicting duplicate boundaries are preserved
- malformed payloads fail clearly
- default tests remain offline-safe

### 6. Mandatory live smoke test

Because TASK-031 is a real-source adapter task, gated live smoke is mandatory.

Add `tests/datahub/test_akshare_fund_holdings_live.py` or equivalent that:

- is skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1`
- uses no credentials
- fetches a minimal bounded live holdings sample for one ETF/fund code
- validates at least one `FUND_HOLDINGS` record via `DatasetRegistry.validate_record(...)`
- classifies environment/source unavailability as explicit `skipTest(...)`
- preserves adapter/schema/normalization issues as failures

If live-enabled run fails/skips due to network/proxy/DNS/TLS/upstream/source availability, the report must include root-cause evidence and feasible repository-level fixes attempted. Controller closure will require the rework/review gate in `AGENTS.md`.

## Do Not Implement

Do not implement:

- fund profile adapter
- broad ETF/fund universe ingestion
- all-fund holdings ingestion
- HK, A-share, index, global, macro, policy, news, or announcement expansion
- trading strategies, signal generation, scanner logic, AI reports, notifications, or UI
- fund feature engineering or derived portfolio analytics
- storage refresh orchestration beyond what is needed for this adapter test surface

## Testing Requirements

Default tests must remain offline.

Run:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Run focused tests, likely:

`python3 -m unittest tests/datahub/test_akshare_fund_holdings_adapter.py`

`python3 -m unittest -v tests/datahub/test_akshare_fund_holdings_live.py`

Run related regressions if shared AKShare adapter behavior, exports, dataset schema, or source catalog is touched:

`python3 -m unittest tests/datahub/test_akshare_fund_nav_adapter.py`

`python3 -m unittest tests/datahub/test_datasets.py`

`python3 -m unittest tests/datahub/test_source.py`

If source-catalog tests are touched, run:

`python3 -m unittest tests/datahub/test_source_catalog.py`

Run gated live smoke when enabled:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_fund_holdings_live.py`

## Acceptance Criteria

The task is acceptable when:

- AKShare-backed `FUND_HOLDINGS` adapter exists under `quant/datahub/**`
- scope remains limited to one-fund ETF/fund holdings records for `DatasetName.FUND_HOLDINGS`
- source id remains `akshare_cn_hk_public_family`
- offline tests pass and remain deterministic
- default tests remain offline-safe
- duplicate, conflicting duplicate, malformed payload, required-field, date, numeric, weight, symbol normalization, and unsupported-symbol boundaries are covered
- gated live smoke exists and result is truthfully recorded
- live-enabled PASS is provided for closure; if live-enabled skip/fail occurs because of network/proxy/DNS/TLS/upstream/source availability, the report must include root-cause evidence and feasible fixes attempted, and controller closure will require the rework/review gate in `AGENTS.md`
- no future-phase module contains new logic
- report exists at `coordination/reports/TASK-031_REPORT.md`

## Report Path

`coordination/reports/TASK-031_REPORT.md`

## Review Path

`coordination/reviews/TASK-031_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-031_INTEGRATION.md`

## Out of Scope

Everything outside a narrow DataHub AKShare ETF/fund holdings adapter and tests is out of scope.
