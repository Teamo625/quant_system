# TASK-038 REPORT (LIVE NETWORK REWORK)

## Task
- Task ID: TASK-038
- Role: 5.3 Execution
- Handoff: `coordination/handoffs/TASK-038_DATAHUB_AKSHARE_ETF_DAILY_BAR_LIVE_NETWORK_REWORK.md`

## Files Changed (this rework)
- `quant/datahub/adapters/akshare.py`
- `tests/datahub/test_akshare_etf_daily_bar_adapter.py`
- `coordination/reports/TASK-038_REPORT.md`

## Rework Goal
- Diagnose reviewer-side live-enabled SKIP (`push2his.eastmoney.com` proxy/network unavailability).
- Keep primary AKShare ETF daily route (`fund_etf_hist_em`) preferred.
- Add bounded repository-level resilience only for live source unavailability, without expanding dataset scope.

## Diagnosis Evidence (before code change)
1. Reproduced live-enabled command:
- Command: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_etf_daily_bar_live.py`
- Result: `OK (skipped=1)`
- Key evidence:
  - `ProxyError: HTTPSConnectionPool(host='push2his.eastmoney.com', port=443) ... Unable to connect to proxy ... Remote end closed connection without response`

2. Route capability check in local akshare:
- Available ETF history routes detected:
  - `fund_etf_hist_em`
  - `fund_etf_hist_min_em`
  - `fund_etf_hist_sina`

3. Direct route probe:
- `fund_etf_hist_em(symbol='510300', ...)` -> `ProxyError` to `push2his.eastmoney.com`
- `fund_etf_hist_sina(symbol='sh510300')` -> returned valid DataFrame with OHLCV+amount fields

## Implementation Changes
1. Bounded fallback in `AkshareETFDailyBarAdapter`:
- Keep `fund_etf_hist_em` as primary route.
- On classified network/proxy/DNS/TLS/source unavailability only, fallback to `fund_etf_hist_sina`.
- Fallback remains narrow:
  - one requested ETF symbol
  - `DatasetName.DAILY_BARS`
  - `market=ETF_CN`
  - same normalization/validation/dedup/date-filter pipeline
- Added deterministic market-prefix conversion for Sina symbol format:
  - `5xxxxx -> shxxxxxx`
  - otherwise `szxxxxxx`

2. Failure boundaries preserved:
- Primary contract/normalization/payload errors still hard-fail and do not trigger fallback.
- Only route-unavailability class errors trigger fallback.

3. Offline tests added for rework behavior:
- primary-unavailable -> fallback route selected
- fallback symbol prefix mapping (`sh` / `sz`)
- non-network contract errors do not fallback
- both routes unavailable -> explicit RuntimeError with attempted route evidence

## Tests Run
1. `python3 -m unittest tests/datahub/test_akshare_etf_daily_bar_adapter.py`
- PASS (`Ran 27 tests ... OK`)

2. `QUANT_SYSTEM_LIVE_TESTS=0 python3 -m unittest -v tests/datahub/test_akshare_etf_daily_bar_live.py`
- PASS with default skip (`Ran 1 test ... OK (skipped=1)`)

3. `python3 -m unittest tests/datahub/test_source_catalog.py`
- PASS (`Ran 6 tests ... OK`)

4. `python3 -m unittest tests/datahub/test_akshare_adapter.py`
- PASS (`Ran 10 tests ... OK`)

5. `python3 -m unittest tests/datahub/test_akshare_hk_adapter.py`
- PASS (`Ran 16 tests ... OK`)

6. `python3 -m unittest tests/datahub/test_akshare_fund_nav_adapter.py`
- PASS (`Ran 17 tests ... OK`)

7. `python3 -m unittest tests/datahub/test_source.py`
- PASS (`Ran 20 tests ... OK`)

8. `QUANT_SYSTEM_LIVE_TESTS=0 python3 -m unittest discover -s tests/datahub -p 'test_*.py'`
- PASS (`Ran 626 tests ... OK (skipped=25)`)

9. Mandatory live smoke rerun:
- Command: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_etf_daily_bar_live.py`
- Result: PASS (`Ran 1 test ... OK`)

## Default Network Behavior
- Default flow remains offline-safe:
  - live tests are gated and skipped unless `QUANT_SYSTEM_LIVE_TESTS=1`
  - offline tests use fixtures/injected callables
- No hidden live network dependency introduced in default test execution.

## Live-Enabled Result (Mandatory)
- Status: **PASS**
- Command: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_etf_daily_bar_live.py`
- Evidence:
  - `test_live_akshare_etf_daily_bars_smoke ... ok`
  - `Ran 1 test ... OK`

## Routes Attempted / Feasible Fix Evidence
- Primary preferred route retained: `fund_etf_hist_em`
- Added bounded fallback route: `fund_etf_hist_sina`
- Feasible repository-level fix implemented: source-unavailability fallback with unchanged contract normalization boundaries.

## Deviations From Handoff
- None.

## Risks / Follow-up
- Residual environmental risk remains possible if both Eastmoney and Sina routes are unavailable in a reviewer environment.
- Current fallback market-prefix rule is intentionally narrow and deterministic for this one-symbol ETF daily-bar scope.
