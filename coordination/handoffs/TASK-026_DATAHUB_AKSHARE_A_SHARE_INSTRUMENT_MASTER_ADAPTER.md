# TASK-026: DataHub AKShare A-share Instrument Master Adapter

## Task ID

TASK-026

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

TASK-025 has been accepted and integrated. It completed the local refresh metadata and `DATA_QUALITY_REPORT` baseline without adding live network behavior.

Phase 2 remains open. The next narrow executable source slice is A-share reference coverage. `DatasetName.INSTRUMENT_MASTER` already has a stable contract and is listed under the no-credential `akshare_cn_hk_public_family` source family.

This task must implement only the A-share stock reference slice of `DatasetName.INSTRUMENT_MASTER`.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-026_DATAHUB_AKSHARE_A_SHARE_INSTRUMENT_MASTER_ADAPTER.md`

## Goal

Implement a narrow AKShare-backed A-share instrument master adapter for `DatasetName.INSTRUMENT_MASTER`, with deterministic offline tests and mandatory gated live smoke coverage.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-026_REPORT.md`

Suggested implementation locations:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `quant/datahub/source_catalog.py` only if strict catalog assertion alignment is required
- `tests/datahub/test_akshare_a_share_instrument_master_adapter.py`
- `tests/datahub/test_akshare_a_share_instrument_master_live.py`
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

### 1. AKShare A-share instrument master adapter

Add a narrow adapter for:

- source id: `akshare_cn_hk_public_family`
- source display name: `AKShare CN/HK Public Family`
- supported dataset in this task: `DatasetName.INSTRUMENT_MASTER`
- initial scope: active A-share stock reference records for Shanghai, Shenzhen, and Beijing exchanges

Recommended bounded AKShare routes:

- `akshare.stock_info_sh_name_code(symbol="主板A股")`
- `akshare.stock_info_sh_name_code(symbol="科创板")`
- `akshare.stock_info_sz_name_code(symbol="A股列表")`
- `akshare.stock_info_bj_name_code()`

The adapter should:

- implement the existing `SourceAdapter` protocol
- use lazy/optional AKShare imports
- reject unsupported datasets clearly
- support optional `symbols` by deterministic client-side filtering after normalization
- normalize output records to `INSTRUMENT_MASTER` contract fields:
  - `symbol`
  - `raw_symbol`
  - `name`
  - `market`
  - `asset_type`
  - `currency`
  - `exchange`
  - `list_date`
  - `delist_date`
  - `is_active`
  - `source`
  - optional `source_ts`
  - `ingested_at`
  - `schema_version`
- set `market=CN`
- set `asset_type=stock`
- set `currency=CNY`
- set `source=akshare_cn_hk_public_family`
- set `schema_version` from `DatasetRegistry`
- set `ingested_at` from injectable clock for deterministic tests
- set `delist_date=9999-12-31` for active listed records when the source route only lists active instruments
- set `is_active=True` for records from active-list routes
- infer exchange from route and/or code:
  - `SSE` for Shanghai `6xxxxx` and `688xxx` records
  - `SZSE` for Shenzhen `0xxxxx` / `3xxxxx` records
  - `BSE` for Beijing records
- normalize symbols to canonical A-share form, e.g. `600000.SH`, `000001.SZ`, `920000.BJ`
- support DataFrame-like payload and list-of-mapping payload fixtures
- fail clearly on malformed payload, missing required fields, invalid list date, invalid code, invalid symbols, or invalid required string fields

### 2. Route and duplicate boundary

- Keep route order bounded and explicit.
- Network/proxy/DNS/TLS/upstream/source availability failures may be classified for route fallback or live skip diagnostics, but DataHub contract/normalization failures must remain hard failures.
- Benign exact duplicate instrument rows may be deterministically deduplicated.
- Conflicting duplicates for the same canonical `symbol` must hard-fail.

### 3. Source catalog alignment

The catalog already includes `DatasetName.INSTRUMENT_MASTER` under `akshare_cn_hk_public_family`.

Do not add broad source claims. Only perform minimal source-catalog assertion updates if required by implemented stable behavior.

### 4. Offline tests

Add deterministic offline tests proving:

- adapter satisfies `SourceAdapter`
- `fetch_source_result(...)` records pass `DatasetRegistry.validate_record(...)`
- source payload conversion from DataFrame-like and list-of-mapping works
- Shanghai, Shenzhen, and Beijing records normalize to correct canonical symbol/exchange
- optional `symbols` filtering accepts canonical and raw 6-digit forms where feasible
- invalid filters fail clearly
- required field, list-date parsing, delist-date default, active flag, and optional field behavior is covered
- duplicate boundary is preserved
- malformed payloads fail clearly
- default tests remain offline-safe

### 5. Mandatory live smoke test

Because TASK-026 is a real-source adapter task, gated live smoke is mandatory.

Add `tests/datahub/test_akshare_a_share_instrument_master_live.py` (or equivalent) that:

- is skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1`
- uses no credentials
- fetches a minimal bounded live sample
- validates at least one normalized record via `DatasetRegistry.validate_record(...)`
- classifies environment/source unavailability as explicit `skipTest(...)`
- preserves adapter/schema issues as failures

If live-enabled run fails/skips due to network/proxy/DNS/TLS/upstream/source availability, report must include root-cause evidence and feasible repository-level fixes attempted.

## Do Not Implement

Do not implement:

- HK, ETF, fund, index, policy, or corporate-action reference adapters
- valuation, capital-flow, strategy, scanner, AI report, notification, or UI logic
- broad warehouse refresh orchestration beyond preserving existing local helper behavior
- credentialed source behavior

## Testing Requirements

Default tests must remain offline.

Run:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Run focused tests, likely:

`python3 -m unittest tests/datahub/test_akshare_a_share_instrument_master_adapter.py`

`python3 -m unittest -v tests/datahub/test_akshare_a_share_instrument_master_live.py`

Run related regressions if shared AKShare adapter behavior or exports are touched:

`python3 -m unittest tests/datahub/test_akshare_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_calendar_adapter.py`

`python3 -m unittest tests/datahub/test_source.py`

`python3 -m unittest tests/datahub/test_quality.py`

If source-catalog tests are touched, run:

`python3 -m unittest tests/datahub/test_source_catalog.py`

Run gated live smoke when enabled:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_instrument_master_live.py`

## Acceptance Criteria

The task is acceptable when:

- AKShare A-share `INSTRUMENT_MASTER` adapter exists under `quant/datahub/**`
- scope remains limited to A-share stock reference records for `DatasetName.INSTRUMENT_MASTER`
- offline tests pass and remain deterministic
- default tests remain offline-safe
- malformed payload, required-field, duplicate, symbol, exchange, list-date, and delist-date boundaries are covered
- gated live smoke exists and result is truthfully recorded
- live-enabled PASS is provided for closure; if live-enabled skip/fail occurs because of network/proxy/DNS/TLS/upstream/source availability, the report must include root-cause evidence and feasible fixes attempted, and controller closure will require the rework/review gate in `AGENTS.md`
- no future-phase module contains new logic
- report exists at `coordination/reports/TASK-026_REPORT.md`

## Report Path

`coordination/reports/TASK-026_REPORT.md`

## Review Path

`coordination/reviews/TASK-026_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-026_INTEGRATION.md`

## Out of Scope

Everything outside a narrow DataHub A-share instrument master adapter and tests is out of scope.
