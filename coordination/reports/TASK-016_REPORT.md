# TASK-016 Report

## Task

- Task ID: `TASK-016`
- Handoff: `coordination/handoffs/TASK-016_DATAHUB_AKSHARE_INDEX_DAILY_BAR_ADAPTER.md`
- Role: 5.3 execution window

## Files Changed

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_index_adapter.py`
- `tests/datahub/test_akshare_index_live.py`
- `tests/datahub/test_source_catalog.py`
- `coordination/reports/TASK-016_REPORT.md`

## What Was Implemented

### 1) AKShare China index daily-bar adapter

- Added `AkshareIndexDailyBarAdapter` in `quant/datahub/adapters/akshare.py`.
- Adapter behavior:
  - supports only `DatasetName.INDEX_DAILY_BARS`
  - implements `SourceAdapter` protocol shape
  - requires exactly one index code
  - accepts canonical `000300.CN_INDEX`, source-native `sh000300`/`sz399001`, and mapped bare codes
  - normalizes output `index_code` to canonical `XXXXXX.CN_INDEX`
  - sets `market="CN_INDEX"` and `source="akshare_cn_hk_public_family"`
  - sets `schema_version` from `DatasetRegistry`
  - sets `ingested_at` via injectable clock (`now_fn`)
  - provides deterministic `index_name` via code mapping (or optional injected resolver)
  - uses lazy AKShare import so default imports/tests do not require `akshare`
  - supports dependency injection via `fetch_index_daily`

- Deterministic index-code mapping implemented:
  - `000300 -> sh000300`
  - `000001 -> sh000001`
  - `399001 -> sz399001`
  - `399006 -> sz399006`

- Code validation behavior:
  - rejects unsupported market suffixes
  - rejects malformed codes
  - rejects unmapped bare/source-native codes for current narrow slice

- Source call behavior:
  - default live function resolution order:
    - `stock_zh_index_daily_tx`
    - `stock_zh_index_daily`
    - `stock_zh_index_daily_em`
    - `index_zh_a_hist`
  - signature-aware argument passing:
    - sends symbol/index/code key based on callable signature
    - passes `start_date`/`end_date` in `YYYYMMDD` only when callable supports them
  - always performs local date filtering after normalization, so wider history payloads are trimmed to request bounds

- Normalization behavior:
  - required fields populated: `index_code`, `index_name`, `market`, `trade_date`, `open`, `high`, `low`, `close`, `source`, `ingested_at`, `schema_version`
  - optional fields included only when valid values exist: `volume`, `amount`, `source_ts`
  - supports DataFrame-like payload (`to_dict(orient="records")`) and list-of-mapping payload
  - clear failures for malformed payload shape, missing fields, invalid numeric/date/datetime values
  - explicit hard failure for OHLC semantic violation (`high < low`)

### 2) Source catalog alignment

- Updated `quant/datahub/source_catalog.py` AKShare entry (`akshare_cn_hk_public_family`):
  - added `DatasetName.INDEX_DAILY_BARS` in `dataset_coverage`
  - added `InformationDomain.INDEX_DATA` stable dataset linkage with `DatasetName.INDEX_DAILY_BARS`

- Updated offline catalog assertions in `tests/datahub/test_source_catalog.py`:
  - AKShare appears in sources for `INDEX_DAILY_BARS`
  - AKShare appears in sources for `InformationDomain.INDEX_DATA`

### 3) Export alignment

- Exported new adapter from:
  - `quant/datahub/adapters/__init__.py`
  - `quant/datahub/__init__.py`

### 4) Offline deterministic tests

- Added `tests/datahub/test_akshare_index_adapter.py` covering:
  - protocol compatibility (`SourceAdapter`)
  - `fetch_source_result(...)` integration and `DatasetRegistry.validate_record(...)` validation
  - canonical/bare/source-native code normalization and mapping
  - date argument passing when source function supports date kwargs
  - local date filtering when source ignores date bounds
  - optional field inclusion behavior
  - unsupported dataset and symbol cardinality errors
  - invalid suffix/format/unmapped code errors
  - malformed payload and missing required field errors
  - invalid trade-date/numeric/optional `source_ts` errors
  - invalid OHLC semantics as hard failure
  - DataFrame-like payload compatibility
  - default offline path guarded with `socket.create_connection` patch in integration test

### 5) Mandatory gated live smoke

- Added `tests/datahub/test_akshare_index_live.py`:
  - skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1`
  - no credentials
  - bounded sample request (`000300.CN_INDEX`, short date range)
  - validates first live record via `DatasetRegistry.validate_record(...)`
  - classifies environment/source network unavailability as explicit `skipTest(...)`
  - preserves adapter/data-contract bugs as failures

## Tests Run

### Focused tests

1. `python3 -m unittest tests/datahub/test_akshare_index_adapter.py`
   - Result: `Ran 21 tests`, `OK`
2. `python3 -m unittest -v tests/datahub/test_akshare_index_live.py`
   - Result: `Ran 1 test`, `OK (skipped=1)`
   - Skip reason: `Live source tests are disabled. Set QUANT_SYSTEM_LIVE_TESTS=1 to enable.`
3. `python3 -m unittest tests/datahub/test_source_catalog.py`
   - Result: `Ran 6 tests`, `OK`

### Required related regression tests

1. `python3 -m unittest tests/datahub/test_akshare_adapter.py`
   - Result: `Ran 10 tests`, `OK`
2. `python3 -m unittest tests/datahub/test_akshare_calendar_adapter.py`
   - Result: `Ran 11 tests`, `OK`
3. `python3 -m unittest tests/datahub/test_akshare_hk_adapter.py`
   - Result: `Ran 16 tests`, `OK`
4. `python3 -m unittest tests/datahub/test_akshare_fund_nav_adapter.py`
   - Result: `Ran 17 tests`, `OK`

### Full DataHub default suite

1. `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`
   - Result: `Ran 151 tests`, `OK (skipped=5)`

### Mandatory live-enabled command

1. `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_index_live.py`
   - Result: `Ran 1 test`, `OK`
   - Verbose case: `test_live_akshare_index_daily_bars_smoke ... ok`

## Default Network Behavior

- Default tests remain offline-safe.
- Live tests are explicitly gated by `QUANT_SYSTEM_LIVE_TESTS=1`.
- Default run path keeps live tests skipped and does not force network access.

## Live Smoke Status (TASK-016)

- Implementation status: present and gated correctly.
- Default status: `SKIP` (as designed).
- Live-enabled status in this environment: `PASS`.

## Deviations From Handoff

- No deviations.

## Risks / Follow-up

- Index code coverage in this first slice is intentionally narrow (current deterministic mapping set only).
- AKShare upstream function signatures/fields can change over time; update scope should remain localized to the adapter’s function-resolution and field-mapping logic.
