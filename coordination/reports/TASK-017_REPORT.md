# TASK-017 Report (Live PASS Rework)

## Task

- Task ID: `TASK-017`
- Handoff: `coordination/handoffs/TASK-017_DATAHUB_SECTOR_LIVE_PASS_REWORK.md`
- Role: 5.3 execution window

## Files Changed

- `quant/datahub/adapters/akshare.py`
- `tests/datahub/test_akshare_sector_adapter.py`
- `tests/datahub/test_akshare_sector_live.py`
- `coordination/reports/TASK-017_REPORT.md`

## Repository-Level Fix Implemented

1. Added sector adapter fallback route for live network failures:
   - primary: Eastmoney history APIs (`stock_board_industry_hist_em` / `stock_board_concept_hist_em`)
   - fallback: THS index history APIs (`stock_board_industry_index_ths` / `stock_board_concept_index_ths`)
2. Fallback is only triggered for transport/network-unavailable exception classes/signals (proxy/timeout/DNS/connection reset/eastmoney-host failures), and keeps non-network exceptions as hard failures.
3. Extended sector row normalization to support THS OHLC field names:
   - `开盘价`, `最高价`, `最低价`, `收盘价`
4. Updated live smoke candidate order to prefer source-compatible name routes that can succeed under current environment:
   - `INDUSTRY:小金属`
   - `CONCEPT:绿色电力`
   - `CONCEPT:阿里巴巴概念`
5. Added offline regression tests for:
   - fallback success path under simulated proxy failure
   - non-network error path remains hard-fail (no fallback masking)

## Root-Cause and Fix Feasibility

- Previously confirmed blocker: Eastmoney route family in this environment can fail with proxy-style remote disconnect behavior (and related TLS/proxy symptoms in prior evidence rework), causing live-enabled sector smoke to skip.
- Feasible repository-level fix: add an in-adapter fallback to THS sector index history route while preserving typed `INDUSTRY:` / `CONCEPT:` semantics and `SECTOR_DAILY_BARS` contract.
- Outcome: live-enabled smoke reaches `PASS` in current environment.

## Tests Run

### Required task tests

1. `python3 -m unittest tests/datahub/test_akshare_sector_adapter.py`
   - Result: `Ran 25 tests`, `OK`

2. `python3 -m unittest -v tests/datahub/test_akshare_sector_live.py`
   - Result: `Ran 1 test`, `OK (skipped=1)`
   - Default gated behavior confirmed.

3. `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`
   - Result: `Ran 177 tests`, `OK (skipped=6)`

### Focused regression tests

1. `python3 -m unittest tests/datahub/test_akshare_index_adapter.py`
   - Result: `Ran 21 tests`, `OK`

2. `python3 -m unittest tests/datahub/test_akshare_fund_nav_adapter.py`
   - Result: `Ran 17 tests`, `OK`

3. `python3 -m unittest tests/datahub/test_akshare_adapter.py`
   - Result: `Ran 10 tests`, `OK`

4. `python3 -m unittest tests/datahub/test_akshare_calendar_adapter.py`
   - Result: `Ran 11 tests`, `OK`

5. `python3 -m unittest tests/datahub/test_akshare_hk_adapter.py`
   - Result: `Ran 16 tests`, `OK`

### Mandatory live-enabled command

1. `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_sector_live.py`
   - Result:
     - `test_live_akshare_sector_daily_bars_smoke ... ok`
     - `Ran 1 test in 8.292s`
     - `OK`

## Default Network Behavior

- Default test runs remain offline-safe.
- Live network behavior remains explicitly gated by `QUANT_SYSTEM_LIVE_TESTS=1`.
- No hidden live call was introduced into default test paths.

## Live Smoke Status

- Default run status: `SKIP` (expected by gate design)
- Live-enabled run status: `PASS`
- Under current handoff gate, TASK-017 is now closure-ready from execution evidence perspective.

## Deviations From Handoff

- No deviations.

## Risks / Follow-up

- Eastmoney route family may still remain unstable in this environment; success currently relies on validated THS fallback path.
- Live availability still depends on public-source stability of THS endpoints.
