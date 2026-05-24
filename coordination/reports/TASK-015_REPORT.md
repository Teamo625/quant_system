# TASK-015 Report

## Task

- Task ID: `TASK-015`
- Handoff: `coordination/handoffs/TASK-015_DATAHUB_AKSHARE_ETF_FUND_NAV_ADAPTER.md`
- Role: 5.3 execution window

## Files Changed

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `tests/datahub/test_akshare_fund_nav_adapter.py`
- `tests/datahub/test_akshare_fund_nav_live.py`
- `coordination/reports/TASK-015_REPORT.md`

## What Was Implemented

### 1) AKShare ETF/Fund NAV snapshot adapter

- Added `AkshareETFFundNavSnapshotAdapter` in `quant/datahub/adapters/akshare.py`.
- Adapter behavior:
  - supports only `DatasetName.FUND_NAV_SNAPSHOT`
  - implements `SourceAdapter` protocol shape
  - requires exactly one fund code
  - accepts both canonical `510300.ETF_CN` and bare `510300`
  - normalizes output `fund_code` to canonical `XXXXXX.ETF_CN`
  - sets `market="ETF_CN"`, `source="akshare_cn_hk_public_family"`
  - sets `schema_version` from `DatasetRegistry`
  - sets `ingested_at` via injectable clock (`now_fn`)
  - uses lazy AKShare import so default imports/tests do not require `akshare`
  - supports dependency injection via `fetch_fund_nav`
- AKShare function resolution:
  - prefers `fund_etf_fund_info_em`
  - fallback to `fund_em_etf_fund_info` for compatibility
- Date argument behavior:
  - accepts `start_date`/`end_date` from `SourceRequest`
  - inspects fetch callable signature and passes bounded dates only when supported
  - uses source-native `YYYYMMDD` format when passing dates
- Payload/normalization behavior:
  - supports DataFrame-like payload (`to_dict(orient="records")`)
  - supports list-of-mapping payload
  - required source fields: trade date + NAV (`净值日期`/`trade_date`/`date`, `单位净值`/`nav`/`unit_nav`)
  - optional fields parsed when valid:
    - `accumulated_nav` (`累计净值`)
    - `shares_outstanding` (`shares_outstanding`/`基金份额`/`份额`)
    - `fund_scale` (`fund_scale`/`基金规模`/`规模`)
    - `source_ts` (`source_ts`/`更新时间`/`update_time`)
  - optional fields are omitted when absent/empty, and fail clearly when present but invalid
  - clear failures for malformed payloads, missing required fields, invalid numeric/date/datetime values, and unsupported fund code format

### 2) Export alignment

- Exported the new adapter from:
  - `quant/datahub/adapters/__init__.py`
  - `quant/datahub/__init__.py`

### 3) Offline deterministic tests

- Added `tests/datahub/test_akshare_fund_nav_adapter.py` covering:
  - protocol compatibility (`SourceAdapter`)
  - `fetch_source_result(...)` integration path
  - `DatasetRegistry.validate_record(...)` contract validation
  - canonical fund code conversion
  - date argument passing with source-native format
  - callable-signature compatibility when date kwargs are unsupported
  - optional field inclusion behavior
  - unsupported dataset failures
  - missing symbol / multiple symbol / invalid fund code failures
  - malformed payload failures
  - missing required source field failures
  - invalid trade-date, numeric, and optional `source_ts` failures
  - DataFrame-like payload conversion
  - default offline path guarded with `socket.create_connection` patch in integration test

### 4) Mandatory gated live smoke

- Added `tests/datahub/test_akshare_fund_nav_live.py`:
  - skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1`
  - no credentials
  - bounded sample request (`510300`, short historical range)
  - validates first live record with `DatasetRegistry.validate_record(...)`
  - converts environment/source network unavailability into explicit `skipTest(...)`
  - preserves adapter/data-contract bugs as test failures

## Tests Run

### Focused adapter and related tests

1. `python3 -m unittest tests/datahub/test_akshare_fund_nav_adapter.py`
   - Result: `Ran 17 tests`, `OK`
2. `python3 -m unittest tests/datahub/test_akshare_adapter.py`
   - Result: `Ran 10 tests`, `OK`
3. `python3 -m unittest tests/datahub/test_akshare_calendar_adapter.py`
   - Result: `Ran 11 tests`, `OK`
4. `python3 -m unittest tests/datahub/test_akshare_hk_adapter.py`
   - Result: `Ran 16 tests`, `OK`

### Mandatory live smoke file (default gate behavior)

1. `python3 -m unittest -v tests/datahub/test_akshare_fund_nav_live.py`
   - Result: `Ran 1 test`, `OK (skipped=1)`
   - Skip reason: `Live source tests are disabled. Set QUANT_SYSTEM_LIVE_TESTS=1 to enable.`

### Mandatory live smoke command (enabled)

1. `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_fund_nav_live.py`
   - Result: `Ran 1 test`, `OK`
   - Verbose case: `test_live_akshare_fund_nav_snapshot_smoke ... ok`

### Full DataHub default suite

1. `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`
   - Result: `Ran 129 tests`, `OK (skipped=4)`

## Default Network Behavior

- Default tests remain offline-safe.
- Live source tests are still skipped by default and only run when `QUANT_SYSTEM_LIVE_TESTS=1`.
- Offline tests use injected fake payloads; no new default live-network path was introduced.

## Live Smoke Status (TASK-015)

- Implementation status: present and gated correctly.
- Default status: `SKIP` (as designed).
- Live-enabled status in this environment: `PASS`.

## Deviations From Handoff

- No deviations.

## Risks / Follow-up

- AKShare public-source behavior can still vary by upstream/network environment across time.
- If future AKShare releases change ETF NAV function signatures/field names again, only this adapter class should need targeted updates due to isolated function-resolution/call logic.
