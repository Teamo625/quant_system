# TASK-104 Report

## files changed
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/source_capabilities.py`
- `tests/datahub/test_akshare_a_share_limit_up_down_adapter.py`
- `tests/datahub/test_akshare_a_share_limit_up_down_live.py`
- `tests/datahub/test_source_capabilities.py`
- `coordination/reports/TASK-104_REPORT.md`

## implementation summary
- Expanded `AkshareAShareLimitUpDownAdapter` from single-day fetch to bounded multi-date iteration.
- Preserved the existing `DatasetName.LIMIT_UP_DOWN_EVENTS` contract and existing normalized fields.
- Kept current required routes:
  - `stock_zt_pool_em`
  - `stock_zt_pool_dtgc_em`
- Added optional breadth routes when the local AKShare version exposes them:
  - `stock_zt_pool_previous_em` -> `event_category=previous_day_limit_up_pool`
  - `stock_zt_pool_zbgc_em` -> `event_category=broken_board_pool`
- Changed duplicate identity from `(symbol, trade_date, limit_type)` to `(symbol, trade_date, limit_type, event_category)` so same-day multi-route facts do not overwrite each other.
- Hardened limit-price resolution to use explicit `涨停价/跌停价` when available and infer the opposite bound from current-day previous-close math, which keeps previous-day/broken-board routes truthful without abusing current `涨跌幅` as the limit ratio.
- Kept route-signature/call-compatibility defects as hard failures.
- Extended route-unavailable classifiers with the additional Eastmoney route tokens used by the new route family.
- Updated `a_share_limit_up_down` capability wording only; status remains `partial`.

## tests run
- `python3 -m unittest tests/datahub/test_akshare_a_share_limit_up_down_adapter.py`
  - PASS (`Ran 14 tests ... OK`)
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_limit_up_down_live.py`
  - PASS (`Ran 4 tests ... OK (skipped=1)`)
- `python3 -m unittest tests/datahub/test_source_capabilities.py`
  - PASS (`Ran 38 tests ... OK`)
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_limit_up_down_live.py`
  - PASS (`Ran 4 tests ... OK`)

## default network behavior
- Default tests remain offline-safe.
- Live smoke is still explicitly gated by `QUANT_SYSTEM_LIVE_TESTS=1`.
- No default test path performs real network IO.

## live-enabled PASS/SKIP/FAIL result and root-cause evidence
- Result: `PASS`
- Live-enabled command:
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_limit_up_down_live.py`
- Additional evidence captured from the live adapter after the smoke:
  - successful date: `2026-06-05`
  - normalized record count: `216`
  - observed event categories:
    - `broken_board_pool`
    - `limit_down_pool`
    - `limit_up_pool`
    - `previous_day_limit_up_pool`
  - first validated record shape:
    - `symbol=000031.SZ`
    - `trade_date=2026-06-05`
    - `limit_type=limit_up`
    - `event_category=broken_board_pool`
    - `hit_limit_up=False`
    - `hit_limit_down=False`
    - `source=akshare_cn_hk_public_family`

## capability truth changed?
- `a_share_limit_up_down` status did not change.
- Status remains `partial`.
- Gap wording was tightened to reflect validated bounded multi-date limit-up/limit-down plus previous-day/broken-board breadth, while explicitly keeping strong-pool/sub-new breadth, formal route provenance, and longer history continuity incomplete.

## deviations
- No handoff scope deviation.
- No schema change was made. The existing contract was preserved, and route-family truth is expressed through `event_category`. Formal `source_route` contract promotion remains follow-up work.

## risks/follow-up
- Capability remains `partial`; strong-pool and sub-new-stock route families are still not normalized into `LIMIT_UP_DOWN_EVENTS`.
- Formal route provenance is still not part of the dataset schema contract.
- Bounded multi-date iteration improves continuity, but long-history completeness and public-source redundancy remain unproven.
