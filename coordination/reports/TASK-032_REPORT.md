# TASK-032 Report

## Task
- `TASK-032_DATAHUB_AKSHARE_HK_INSTRUMENT_MASTER_ADAPTER`

## Files Changed
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `tests/datahub/test_akshare_hk_instrument_master_adapter.py`
- `tests/datahub/test_akshare_hk_instrument_master_live.py`

## Implementation Summary
- Added `AkshareHKInstrumentMasterAdapter` for `DatasetName.INSTRUMENT_MASTER` under source id `akshare_cn_hk_public_family`.
- Enforced one-symbol-only input and HK-only symbol normalization:
  - accepts `00700.HK` and `00700`
  - normalizes to canonical `symbol=00700.HK`, `raw_symbol=00700`
  - rejects missing/multiple/malformed/non-HK symbol requests.
- Implemented bounded AKShare route usage:
  - route: `stock_hk_security_profile_em(symbol=<single_code>)`
  - no broad-universe HK ingestion.
- Implemented normalization to instrument master contract fields:
  - `market=HK`, `asset_type=stock`, `currency=HKD`, `exchange=HKEX`
  - `delist_date=9999-12-31`, `is_active=True`
  - `source=akshare_cn_hk_public_family`
  - schema version from `DatasetRegistry`
  - deterministic `ingested_at` via injectable clock
  - optional `source_ts` normalization.
- Implemented payload compatibility and validation:
  - supports DataFrame-like payloads and list-of-mapping payloads
  - supports item/value style payload collapse (`项目`/`值`) when returned that way
  - strict missing-field, invalid-date, invalid-required-text, malformed payload checks.
- Implemented duplicate boundary handling:
  - dedupe key is canonical `symbol`
  - benign duplicates deduped deterministically (prefer latest `source_ts`)
  - conflicting duplicates hard-fail.
- Implemented non-stock screening:
  - rejects ETF/fund/index/warrant/bond/reit/option-like security types
  - accepts HK stock-like values observed in source (including `非H股`).
- Added live-network unavailability classifier for this adapter and wrapped network-related route failures for live-skip diagnostics.
- Exported adapter in package `__init__` files.

## Live Diagnostic Note During Execution
- First live-enabled attempt failed with:
  - `ValueError: No stock-like HK instrument profile row found for requested symbol: '00700.HK'`
- Root-cause evidence from direct bounded source inspection:
  - `stock_hk_security_profile_em("00700")` returned `证券类型='非H股'`
  - `上市日期='2004-06-16 00:00:00'`
- Repository-level fixes applied:
  - treat `非H股` as stock-like in this HK stock slice
  - accept datetime-like list-date strings and normalize to `YYYY-MM-DD`.
- Re-run live-enabled smoke after fix: PASS.

## Tests Run

### Focused TASK-032 tests
1. `python3 -m unittest tests/datahub/test_akshare_hk_instrument_master_adapter.py`
   - PASS (20 tests)
2. `python3 -m unittest -v tests/datahub/test_akshare_hk_instrument_master_live.py`
   - PASS (3 tests, live smoke skipped by default)
3. `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_instrument_master_live.py`
   - PASS (3 tests, live smoke PASS)

### Required related regressions from handoff
4. `python3 -m unittest tests/datahub/test_akshare_hk_adapter.py`
   - PASS (16 tests)
5. `python3 -m unittest tests/datahub/test_akshare_adapter.py`
   - PASS (10 tests)
6. `python3 -m unittest tests/datahub/test_akshare_a_share_instrument_master_adapter.py`
   - PASS (21 tests)
7. `python3 -m unittest tests/datahub/test_datasets.py`
   - PASS (27 tests)
8. `python3 -m unittest tests/datahub/test_source.py`
   - PASS (20 tests)
9. `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`
   - PASS (513 tests, 20 skipped)

## Default Network Behavior
- Default tests remain offline-safe.
- Live network access remains explicitly gated by `QUANT_SYSTEM_LIVE_TESTS=1`.
- Live smoke test is skipped by default and only runs when explicitly enabled.

## Live-Enabled Result
- Result: **PASS**
- Command:
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_instrument_master_live.py`
- Evidence:
  - classifier tests PASS
  - live smoke PASS
  - at least one normalized HK `INSTRUMENT_MASTER` record validated by `DatasetRegistry.validate_record(...)`.

## Deviations From Handoff
- None.

## Risks / Follow-up
- Upstream AKShare field semantics may change (e.g., `证券类型` vocabulary, date formatting). Current adapter now explicitly handles observed `非H股` + datetime-like `上市日期` values, but future upstream drift should be monitored in live smoke.
- Scope remains intentionally narrow to one requested HK stock symbol for this task; broad HK universe ingestion remains out of scope.
