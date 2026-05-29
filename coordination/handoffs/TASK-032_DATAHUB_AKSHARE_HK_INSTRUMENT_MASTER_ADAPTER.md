# TASK-032: DataHub AKShare Hong Kong Instrument Master Adapter

## Task ID

TASK-032

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

TASK-031 has been accepted and integrated. It completed the AKShare one-fund ETF/fund holdings slice for `DatasetName.FUND_HOLDINGS` and closed the classifier rework blocker with live-enabled PASS evidence.

Phase 2 remains open. Hong Kong stock full-data coverage currently has accepted slices for HK daily bars and HK company announcements, but HK stock reference coverage is still missing. The next narrow executable slice is therefore a Hong Kong stock `instrument_master` adapter.

This task must implement only a one-symbol Hong Kong stock reference slice for `DatasetName.INSTRUMENT_MASTER`.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-032_DATAHUB_AKSHARE_HK_INSTRUMENT_MASTER_ADAPTER.md`

## Goal

Implement a narrow AKShare-backed Hong Kong stock instrument master adapter for `DatasetName.INSTRUMENT_MASTER`, focused on one requested HK stock symbol, with deterministic offline tests and mandatory gated live smoke coverage.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-032_REPORT.md`

Suggested implementation locations:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `tests/datahub/test_akshare_hk_instrument_master_adapter.py`
- `tests/datahub/test_akshare_hk_instrument_master_live.py`
- existing DataHub tests only as needed for import/export updates

`quant/datahub/source_catalog.py` and `tests/datahub/test_source_catalog.py` may be touched only if strict catalog assertion alignment is required. The catalog already declares `DatasetName.INSTRUMENT_MASTER` under `akshare_cn_hk_public_family`.

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

### 1. AKShare HK instrument master adapter

Add a narrow adapter for:

- source id: `akshare_cn_hk_public_family`
- source display name: `AKShare CN/HK Public Family`
- supported dataset in this task: `DatasetName.INSTRUMENT_MASTER`
- market output: `HK`
- initial scope: one Hong Kong listed stock security profile

The adapter should:

- implement the existing `SourceAdapter` protocol
- use lazy/optional AKShare imports
- reject unsupported datasets clearly
- require exactly one HK stock symbol through `symbols`
- accept canonical HK symbols such as `00700.HK` and source-native numeric forms such as `00700`
- reject missing, multiple, empty, malformed, A-share, index, ETF/fund, or unsupported market symbols clearly
- normalize output `symbol` to canonical HK form such as `00700.HK`
- normalize `raw_symbol` to the source-native code where feasible
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
- set `market=HK`
- set `asset_type=stock`
- set `currency=HKD`
- set `exchange=HKEX`
- set `source=akshare_cn_hk_public_family`
- set `schema_version` from `DatasetRegistry`
- set `ingested_at` from injectable clock for deterministic tests
- set `delist_date=9999-12-31` and `is_active=True` for a current security profile when the source does not provide a delisting date
- preserve source-truth `list_date`; do not invent placeholder list dates
- support DataFrame-like payload and list-of-mapping payload fixtures
- fail clearly on malformed payload, missing required fields, invalid list date, invalid code, invalid symbol filter, invalid required string fields, or non-stock security type that cannot truthfully map to this first HK stock slice

### 2. Source route guidance

Prefer the no-credential AKShare public route:

- `akshare.stock_hk_security_profile_em(symbol="00700")`

At controller dispatch time, the local AKShare version exposes this function and a sample call for `00700` returns fields including `证券代码`, `证券简称`, `上市日期`, `证券类型`, and `交易所`.

Route rules:

- keep route order bounded and explicit
- fetch only the requested single HK stock profile
- do not perform broad HK universe ingestion
- classify network/proxy/DNS/TLS/upstream/source availability failures for live skip diagnostics
- keep contract/normalization failures as hard failures

### 3. Duplicate and identity boundary

- The stable key for duplicate checks should be the canonical `symbol`.
- Benign exact duplicate profile rows may be deterministically deduplicated.
- Conflicting duplicate rows for the same canonical `symbol` must hard-fail.
- If the source returns multiple security categories for the requested code, preserve only records that truthfully map to the current HK stock `INSTRUMENT_MASTER` slice.

### 4. Source catalog alignment

The source catalog already includes `DatasetName.INSTRUMENT_MASTER` under `akshare_cn_hk_public_family`.

Do not add broad source claims. Only perform minimal source-catalog assertion updates if required by implemented stable behavior.

### 5. Offline tests

Add deterministic offline tests proving:

- adapter satisfies `SourceAdapter`
- `fetch_source_result(...)` records pass `DatasetRegistry.validate_record(...)`
- source payload conversion from DataFrame-like and list-of-mapping works
- canonical HK symbol conversion preserves stable output codes
- source-native numeric symbol conversion works
- missing symbols, multiple symbols, invalid HK symbols, A-share symbols, ETF/fund-like symbols, and unsupported dataset are rejected clearly
- required field, list-date parsing, delist-date default, active flag, non-stock security-type rejection, and optional `source_ts` behavior are covered
- duplicate and conflicting duplicate boundaries are preserved
- malformed payloads fail clearly
- default tests remain offline-safe

### 6. Mandatory live smoke test

Because TASK-032 is a real-source adapter task, gated live smoke is mandatory.

Add `tests/datahub/test_akshare_hk_instrument_master_live.py` or equivalent that:

- is skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1`
- uses no credentials
- fetches a minimal bounded live HK stock profile sample, preferably `00700.HK`
- validates at least one `INSTRUMENT_MASTER` record via `DatasetRegistry.validate_record(...)`
- classifies environment/source unavailability as explicit `skipTest(...)`
- preserves adapter/schema/normalization issues as failures

If live-enabled run fails/skips due to network/proxy/DNS/TLS/upstream/source availability, the report must include root-cause evidence and feasible repository-level fixes attempted. Controller closure will require the rework/review gate in `AGENTS.md`.

## Do Not Implement

Do not implement:

- broad HK instrument universe ingestion
- HK corporate actions, HK valuation, HK capital flow, HK trading calendar, or HK ETF/fund profile adapters
- A-share, ETF/fund, index, global, macro, policy, news, or announcement expansion
- trading strategies, signal generation, scanner logic, AI reports, notifications, UI, or automated trading
- feature engineering or derived analytics
- storage refresh orchestration beyond what is needed for this adapter test surface

## Testing Requirements

Default tests must remain offline.

Run:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Run focused tests, likely:

`python3 -m unittest tests/datahub/test_akshare_hk_instrument_master_adapter.py`

`python3 -m unittest -v tests/datahub/test_akshare_hk_instrument_master_live.py`

Run related regressions if shared AKShare adapter behavior, exports, dataset schema, or source catalog is touched:

`python3 -m unittest tests/datahub/test_akshare_hk_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_a_share_instrument_master_adapter.py`

`python3 -m unittest tests/datahub/test_datasets.py`

`python3 -m unittest tests/datahub/test_source.py`

If source-catalog tests are touched, run:

`python3 -m unittest tests/datahub/test_source_catalog.py`

Run gated live smoke when enabled:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_instrument_master_live.py`

## Acceptance Criteria

The task is acceptable when:

- AKShare-backed HK `INSTRUMENT_MASTER` adapter exists under `quant/datahub/**`
- scope remains limited to one-symbol Hong Kong stock reference records for `DatasetName.INSTRUMENT_MASTER`
- source id remains `akshare_cn_hk_public_family`
- offline tests pass and remain deterministic
- default tests remain offline-safe
- malformed payload, required-field, duplicate, symbol, exchange, list-date, non-stock security-type, and delist-date boundaries are covered
- gated live smoke exists and result is truthfully recorded
- live-enabled PASS is provided for closure; if live-enabled skip/fail occurs because of network/proxy/DNS/TLS/upstream/source availability, the report must include root-cause evidence and feasible fixes attempted, and controller closure will require the rework/review gate in `AGENTS.md`
- no future-phase module contains new logic
- report exists at `coordination/reports/TASK-032_REPORT.md`

## Report Path

`coordination/reports/TASK-032_REPORT.md`

## Review Path

`coordination/reviews/TASK-032_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-032_INTEGRATION.md`

## Out of Scope

Everything outside a narrow DataHub AKShare HK instrument master adapter and tests is out of scope.
