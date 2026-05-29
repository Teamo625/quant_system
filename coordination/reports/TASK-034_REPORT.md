# TASK-034 Report

## Task
- `TASK-034_DATAHUB_AKSHARE_HK_VALUATION_SNAPSHOT_ADAPTER`

## Files Changed
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_hk_valuation_snapshot_adapter.py`
- `tests/datahub/test_akshare_hk_valuation_snapshot_live.py`
- `tests/datahub/test_source_catalog.py`

## Implementation Summary
- Added `AkshareHKValuationSnapshotAdapter` for `DatasetName.VALUATION_SNAPSHOT` under source id `akshare_cn_hk_public_family`.
- Scope is strictly one requested HK stock symbol:
  - accepts `00700.HK` and `00700`
  - normalizes to canonical `symbol=00700.HK`
  - rejects missing/multiple/malformed/non-HK symbol forms clearly.
- Implemented bounded route usage with deterministic merge logic:
  - `stock_hk_indicator_eniu(symbol="hk<5-digit>", indicator=...)`
  - `stock_hk_valuation_comparison_em(symbol="<5-digit>")`
  - optional `stock_hk_valuation_baidu(symbol="<5-digit>", indicator=..., period="近一年")`
- Implemented route precedence:
  - when Eniu provides required fields (`pe_ttm`, `pb`, `market_cap`), required fields are taken from Eniu
  - `ps_ttm` can be supplemented by comparison route
  - `float_market_cap` can be supplemented by optional baidu route
  - if required fields are still missing after bounded merge, task fails clearly (no placeholder fabrication).
- Implemented deterministic trade-date policy:
  - prefer Eniu metric date
  - fallback to baidu metric date
  - fallback to injectable local clock date.
- Implemented deterministic `start_date` / `end_date` filtering by normalized `trade_date`.
- Implemented numeric and unit normalization:
  - market-cap related values support deterministic unit conversion (including `亿`-scale normalization to HKD amount when unit is clear).
- Implemented duplicate boundaries:
  - benign exact duplicate metric rows are deduped
  - conflicting duplicate metric rows for same metric/date hard-fail
  - conflicting duplicate comparison rows hard-fail.
- Implemented explicit malformed-payload / required-field / date / numeric error boundaries.
- Implemented HK valuation network/source unavailability classifier for live skip diagnostics, while preserving contract/normalization failures as hard failures.
- Exported adapter in package exports:
  - `quant.datahub.adapters`
  - `quant.datahub`.
- Source catalog alignment:
  - `InformationDomain.HK_STOCK_FULL_DATA` stable datasets now include `DatasetName.VALUATION_SNAPSHOT`.

## Tests Run

### Focused TASK-034 tests
1. `python3 -m unittest tests/datahub/test_akshare_hk_valuation_snapshot_adapter.py`
   - PASS (23 tests)
2. `python3 -m unittest -v tests/datahub/test_akshare_hk_valuation_snapshot_live.py`
   - PASS (3 tests, live smoke skipped by default)
3. `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_valuation_snapshot_live.py`
   - PASS (3 tests, live smoke PASS)

### Related regressions from handoff
4. `python3 -m unittest tests/datahub/test_akshare_hk_corporate_actions_adapter.py`
   - PASS (19 tests)
5. `python3 -m unittest tests/datahub/test_akshare_a_share_valuation_snapshot_adapter.py`
   - PASS (24 tests)
6. `python3 -m unittest tests/datahub/test_datasets.py`
   - PASS (27 tests)
7. `python3 -m unittest tests/datahub/test_source.py`
   - PASS (20 tests)
8. `python3 -m unittest tests/datahub/test_source_catalog.py`
   - PASS (6 tests)
9. `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`
   - PASS (561 tests, 22 skipped)

## Default Network Behavior
- Default tests remain offline-safe.
- Live tests remain environment-gated and skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1`.

## Live-Enabled Result
- Result: **PASS**
- Command:
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_valuation_snapshot_live.py`
- Evidence:
  - classifier tests PASS
  - live smoke PASS
  - normalized HK valuation snapshot record validated by `DatasetRegistry.validate_record(...)`.

## Deviations From Handoff
- None.

## Risks / Follow-up
- Upstream HK valuation source freshness differs by route (observed route date behavior can vary). Current implementation keeps deterministic precedence and fails clearly for required-field truth gaps instead of synthesizing values.
- Optional baidu route may be unavailable in some environments (e.g., SSL/certificate/proxy constraints); implementation treats this as bounded optional fallback behavior and does not mask contract bugs.
