# TASK-048 Execution Report

## Task

- Task ID: `TASK-048`
- Handoff: `coordination/handoffs/TASK-048_DATAHUB_AKSHARE_A_SHARE_LIMIT_UP_DOWN_ADAPTER.md`
- Role: 5.3 Execution Window
- Phase scope respected: only `quant/datahub/**`, `tests/datahub/**`, and this report file were modified

## Files Changed

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `quant/datahub/source_capabilities.py`
- `tests/datahub/test_akshare_a_share_limit_up_down_adapter.py` (new)
- `tests/datahub/test_akshare_a_share_limit_up_down_live.py` (new)
- `tests/datahub/test_source_capabilities.py`
- `coordination/reports/TASK-048_REPORT.md` (new)

## Implementation Summary

Implemented narrow public-source AKShare A-share limit-up/down adapter coverage for `DatasetName.LIMIT_UP_DOWN_EVENTS`:

- Added `AkshareAShareLimitUpDownAdapter` under source family `akshare_cn_hk_public_family`.
- Supported routes:
  - `stock_zt_pool_em` (limit-up pool)
  - `stock_zt_pool_dtgc_em` (limit-down pool)
- Enforced bounded one-day request:
  - rejects unbounded requests
  - rejects missing one-side date bounds
  - rejects multi-day range requests
- Added symbol filter normalization/validation:
  - accepts canonical (`600000.SH`), prefixed (`SH600000`), and bare 6-digit A-share codes
  - normalizes to canonical output symbol
  - rejects HK / ETF-fund / index / malformed symbols when filtering is requested
- Added payload support for DataFrame-like and list-of-mapping inputs.
- Added route signature compatibility checks via callable inspection; unsupported argument shape is hard failure.
- Added deterministic normalization for `LIMIT_UP_DOWN_EVENTS` records:
  - `market="A_SHARE"`
  - `source="akshare_cn_hk_public_family"`
  - `schema_version` from `DatasetRegistry`
  - `ingested_at` from injected clock
  - truthful limit-up/limit-down flags and route category fields
- Added deterministic sorting by `(trade_date, symbol, limit_type)` and deduplication with conflict detection.
- Added explicit route-unavailable classifier for live skip diagnostics that keeps adapter/schema/signature issues as failures.

Exports/capability truth updates:

- Exported adapter from:
  - `quant/datahub/adapters/__init__.py`
  - `quant/datahub/__init__.py`
- Updated source capability truth for `a_share_limit_up_down` from `planned` to `partial` in `quant/datahub/source_capabilities.py`.
- Updated corresponding assertion in `tests/datahub/test_source_capabilities.py`.

## Tests Run

### Focused TASK-048 tests

1. `python3 -m unittest tests/datahub/test_akshare_a_share_limit_up_down_adapter.py`
- Result: PASS (`Ran 13 tests ... OK`)

2. `python3 -m unittest -v tests/datahub/test_akshare_a_share_limit_up_down_live.py`
- Result: PASS with default live skip (`Ran 4 tests ... OK (skipped=1)`)

3. `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_limit_up_down_live.py`
- Final Result: PASS (`Ran 4 tests ... OK`)

### Required related regressions from handoff

4. `python3 -m unittest tests/datahub/test_akshare_adapter.py`
- Result: PASS (`Ran 10 tests ... OK`)

5. `python3 -m unittest tests/datahub/test_akshare_a_share_margin_financing_lending_adapter.py`
- Result: PASS (`Ran 14 tests ... OK`)

6. `python3 -m unittest tests/datahub/test_akshare_a_share_company_announcements_adapter.py`
- Result: PASS (`Ran 14 tests ... OK`)

7. `python3 -m unittest tests/datahub/test_source.py`
- Result: PASS (`Ran 20 tests ... OK`)

8. `python3 -m unittest tests/datahub/test_source_capabilities.py`
- Result: PASS (`Ran 12 tests ... OK`)

### Full default DataHub suite

9. `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`
- Result: PASS (`Ran 736 tests ... OK (skipped=32)`)

## Default Network Behavior

- Default test path remains offline-safe.
- Live smoke test is explicitly gated by `QUANT_SYSTEM_LIVE_TESTS=1` and skipped by default.
- Focused offline adapter tests patched network helper (`socket.create_connection`) to assert no network use.

## Live-Enabled Result and Evidence

- Required live-enabled command executed:
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_limit_up_down_live.py`
- Result: PASS.
- Evidence:
  - classifier tests passed
  - live smoke passed with at least one bounded-date sample record validated via `DatasetRegistry.validate_record(...)`
  - assertions verified `source=akshare_cn_hk_public_family`, `market=A_SHARE`, and canonical A-share symbol pattern

## Deviations from Handoff

- No scope deviation.
- During live-enabled execution, one normalization issue was discovered and fixed in-task:
  - original mapping treated `封板资金/封单资金` as `seal_status` text, but live payload returned numeric values
  - fixed by only mapping `seal_status` from explicit status-like fields and improving optional label normalization robustness
- After fix, focused tests and live-enabled smoke were re-run and passed.

## Risks / Follow-up

- Capability remains `partial` by design:
  - current slice is bounded one-trade-date public pool coverage
  - breadth/history completeness remains future work
- Limit-price derivation for missing explicit threshold fields is deterministic but route-dependent; broader route-family hardening may be needed for trading-grade history/breadth expansion.

