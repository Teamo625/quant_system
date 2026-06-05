# TASK-096 Report

- files changed
  - `quant/datahub/adapters/akshare.py`
  - `quant/datahub/source_capabilities.py`
  - `tests/datahub/test_akshare_a_share_minute_bars_adapter.py`
  - `tests/datahub/test_source_capabilities.py`

- tests run
  - `python3 -m unittest tests/datahub/test_akshare_a_share_minute_bars_adapter.py` -> PASS (`Ran 21 tests`)
  - `python3 -m unittest tests/datahub/test_source_capabilities.py` -> PASS (`Ran 34 tests`)
  - `python3 -m unittest -v tests/datahub/test_akshare_a_share_minute_bars_live.py` -> PASS with default skip (`Ran 5 tests`, `skipped=1`)
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_minute_bars_live.py` -> SKIP (`Ran 5 tests`, `skipped=1`)

- default network behavior
  - Default tests remain offline-safe.
  - The live smoke still skips by default unless `QUANT_SYSTEM_LIVE_TESTS=1`.
  - The new stale `1`-minute rejection test proves neither primary nor fallback fetch is called for unsupported old windows.

- exact `1`-minute retention rule used and why it is source-backed
  - Inspected local `akshare 1.18.60` source: `stock_zh_a_hist_min_em(period='1')` uses Eastmoney `trends2/get` with hardcoded `ndays=5`.
  - Adapter rule is now:
    - first choice: resolve recent trade dates and treat the oldest of the latest 5 trade dates as the supported floor
    - fallback only if trade-date resolution itself is unavailable: use a conservative weekday-based 5-trading-day floor plus a 9-calendar-day holiday cushion so long closures are not rejected before fetch
  - This removes the incorrect fixed `10` calendar-day guard.

- offline regression evidence for holiday / long-closure retention behavior
  - Added a regression where `now=2026-10-08` and injected trade dates make `2026-09-24` to `2026-09-30` the latest 5 trade dates across the National Day closure; the adapter now accepts that >10-calendar-day span and fetches the primary route.
  - Kept the clearly stale-window rejection case (`2026-05-20` to `2026-05-21` under `now=2026-06-15`) and proved both primary and fallback calls stay at `0`.
  - Existing old-window fallback misuse protection for unsupported historical windows remains covered.

- source routes investigated or changed
  - Investigated:
    - `stock_zh_a_hist_min_em`
    - `stock_zh_a_minute`
    - `tool_trade_date_hist_sina` via the in-repo AKShare trading-calendar adapter helper
  - Changed behavior:
    - primary route is still `stock_zh_a_hist_min_em`
    - fallback route is still `stock_zh_a_minute`
    - retention gating for `1`-minute requests now prefers trade-date-backed floor resolution instead of fixed calendar subtraction
  - `stock_zh_a_minute` remains unsuitable for old bounded history because it exposes no caller `start_date/end_date` arguments and uses recent `datalen=1970` retrieval.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence for real-source task
  - Result: `SKIP`
  - Root-cause evidence:
    - enabled smoke skipped with `ProxyError: HTTPSConnectionPool(host='push2his.eastmoney.com', port=443) ... Unable to connect to proxy ... Remote end closed connection without response`
    - local requests environment proxies resolve to `http://127.0.0.1:7892` for `http` and `https`
    - a direct manual GET to Eastmoney `push2his.eastmoney.com/api/qt/stock/kline/get` reproduced the same proxy failure outside the test
  - The skip remains truthful environment/connectivity evidence, not a contract or schema failure.

- whether `a_share_minute_bars` capability truth changed
  - No status change. `a_share_minute_bars` remains `partial`.
  - Updated wording only to reflect source-backed trading-day-aware handling for recent-only `1`-minute retention.

- deviations
  - No deviations from the handoff.
  - `tests/datahub/test_akshare_a_share_minute_bars_live.py` did not need code changes; rerun evidence was captured through the required test execution and diagnosis.

- risks/follow-up
  - Controller closure is still blocked by missing live PASS evidence in the current proxy/network environment.
  - If closure-ready live proof is required, rerun TASK-096 from an environment that can reach Eastmoney without the local `127.0.0.1:7892` proxy failure.
  - Public `1`-minute history is still only recent retained data; broader intraday continuity needs a truly date-bounded public source, not fallback expansion or synthesized bars.
