# TASK-013 Report

## Task

- Task ID: `TASK-013`
- Handoff: `coordination/handoffs/TASK-013_DATAHUB_AKSHARE_A_SHARE_TRADING_CALENDAR_ADAPTER.md`
- Role: 5.3 execution window

## Files Changed

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_calendar_adapter.py`
- `tests/datahub/test_akshare_calendar_live.py`
- `tests/datahub/test_source_catalog.py`
- `coordination/reports/TASK-013_REPORT.md`

## What Was Implemented

### 1) AKShare A-share trading calendar adapter

- Added `AkshareAShareTradingCalendarAdapter` in `quant/datahub/adapters/akshare.py`.
- Adapter contract behavior:
  - implements existing `SourceAdapter` protocol shape
  - supports only `DatasetName.TRADING_CALENDAR`
  - rejects symbol inputs (`symbols` must be `None`)
  - accepts optional `start_date` / `end_date`
  - uses lazy/optional AKShare import (`tool_trade_date_hist_sina`), so default imports/tests do not require AKShare
  - supports dependency injection (`fetch_trade_dates`, `now_fn`) for deterministic offline tests
- Normalization behavior:
  - accepts DataFrame-like payloads (`to_dict(orient="records")`)
  - accepts list-of-mapping and list-of-date-like fixtures
  - parses supported trade-date forms (`date`, `datetime`, ISO date string, `YYYYMMDD` string)
  - deduplicates and sorts trade dates
  - filters deterministically by `start_date`/`end_date`
  - computes `previous_trade_date` and `next_trade_date` from the filtered sorted sequence
  - outputs schema-compatible `trading_calendar` records with:
    - `market="CN"`
    - `is_open=True`
    - `session_type="full"`
    - `source="akshare_cn_hk_public_family"`
    - `schema_version` from `DatasetRegistry`
    - `ingested_at` from injected/default clock
- Clear failure paths:
  - unsupported dataset
  - symbols supplied
  - malformed payload shape
  - missing trade-date field in mapping rows
  - invalid trade-date value
  - empty usable date set after filtering

### 2) Source catalog alignment

- Updated AKShare source catalog entry in `quant/datahub/source_catalog.py`:
  - added `DatasetName.TRADING_CALENDAR` to `akshare_cn_hk_public_family.dataset_coverage`
  - added `InformationDomain.EXCHANGE_CALENDAR` stable dataset linkage (`TRADING_CALENDAR`) for AKShare entry
- Updated `tests/datahub/test_source_catalog.py` assertions to verify AKShare now appears in:
  - trading-calendar dataset sources
  - exchange-calendar information-domain sources

### 3) Exports

- Exported new adapter through:
  - `quant/datahub/adapters/__init__.py`
  - `quant/datahub/__init__.py`

### 4) Offline and live tests added

- Added `tests/datahub/test_akshare_calendar_adapter.py` (deterministic offline adapter tests):
  - protocol compatibility
  - `fetch_source_result(...)` integration
  - schema validation via `DatasetRegistry.validate_record(...)`
  - deterministic date filtering
  - previous/next trade-date computation
  - DataFrame-like and list-of-date payload compatibility
  - all required failure paths
- Added `tests/datahub/test_akshare_calendar_live.py` (mandatory gated live smoke):
  - skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1`
  - no credentials
  - bounded date range sample
  - validates at least one normalized live record through `DatasetRegistry.validate_record(...)`
  - converts environment/source unavailability to explicit `skipTest(...)`
  - preserves adapter/data-contract bugs as failures

## Tests Run

Required offline suite:

- `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`
  - Result: `Ran 94 tests`, `OK (skipped=2)`

Focused tests:

- `python3 -m unittest tests/datahub/test_akshare_calendar_adapter.py`
  - Result: `Ran 11 tests`, `OK`
- `python3 -m unittest tests/datahub/test_akshare_calendar_live.py`
  - Result: `Ran 1 test`, `OK (skipped=1)`
- `python3 -m unittest tests/datahub/test_source_catalog.py`
  - Result: `Ran 6 tests`, `OK`

Live-enabled mandatory smoke command:

- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_calendar_live.py`
  - Result: `Ran 1 test`, `OK`
  - Verbose case result: `test_live_akshare_trading_calendar_smoke ... ok`

## Default Network Behavior

- Default discovery remains offline; live tests are skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1` is set.
- Offline adapter tests use injected fake payloads and do not require live network access.

## Live Smoke Implementation and Status

- Live smoke file: `tests/datahub/test_akshare_calendar_live.py`
- Gate: `QUANT_SYSTEM_LIVE_TESTS=1`
- Default run behavior: skipped
- Live-enabled behavior in this environment: pass (live sample fetched and validated)

## Deviations From Handoff

- No deviation.

## Risks / Follow-up

- Live-source behavior remains environment-dependent; in restricted/proxy-limited environments, live-enabled runs may produce explicit skip rather than pass.
- Current calendar adapter intentionally scopes to A-share market-level open-day calendar with `session_type="full"`; finer session granularity (half-day/special session) should be deferred to a future explicitly scoped task.
