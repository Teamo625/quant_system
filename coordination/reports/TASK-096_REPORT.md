# TASK-096 Report

- files changed
  - `quant/datahub/adapters/akshare.py`
  - `quant/datahub/source_capabilities.py`
  - `tests/datahub/test_akshare_a_share_minute_bars_adapter.py`
  - `tests/datahub/test_akshare_a_share_minute_bars_live.py`
  - `tests/datahub/test_source_capabilities.py`

- tests run
  - `python3 -m unittest tests/datahub/test_akshare_a_share_minute_bars_adapter.py` -> PASS (`Ran 20 tests`)
  - `python3 -m unittest tests/datahub/test_source_capabilities.py` -> PASS (`Ran 34 tests`)
  - `python3 -m unittest -v tests/datahub/test_akshare_a_share_minute_bars_live.py` -> PASS with default skip (`Ran 5 tests`, smoke skipped by env gate)
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_minute_bars_live.py` -> SKIP (`Ran 5 tests`, smoke skipped truthfully)

- default network behavior
  - Default/offline tests remain offline-safe.
  - `tests/datahub/test_akshare_a_share_minute_bars_live.py` still skips the live smoke unless `QUANT_SYSTEM_LIVE_TESTS=1`.
  - Added offline assertions that old 1-minute windows fail before any fetch call and that unsupported fallback history windows do not hit the fallback route.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence
  - Result: `SKIP`
  - Evidence: enabled smoke attempted bounded historical `5`-minute fetches and skipped on upstream connectivity failure:
    - `ProxyError: HTTPSConnectionPool(host='push2his.eastmoney.com', port=443) ... Unable to connect to proxy ... Remote end closed connection without response`
  - The skip is environment/upstream related, not a contract-validation failure.

- source routes investigated and which route is used
  - Investigated local `akshare 1.18.60` route behavior:
    - `stock_zh_a_hist_min_em`
    - `stock_zh_a_minute`
  - Primary route remains `stock_zh_a_hist_min_em`.
  - Fallback route remains `stock_zh_a_minute`, but it is now limited to recent bounded windows only because it has no caller `start_date/end_date` arguments.
  - Local `akshare` source inspection showed:
    - `stock_zh_a_hist_min_em(period='1')` hardcodes `ndays=5`
    - `stock_zh_a_minute` uses recent snapshot-style `datalen=1970` fetches without caller date bounds

- historical continuity, bounded-window, interval, and fallback limitations
  - Added an explicit recent-window guard for public `1`-minute requests so old history is rejected clearly instead of silently returning empty/incomplete results.
  - Kept broader bounded history available for non-`1`-minute periods (`5/15/30/60`) via the primary Eastmoney route.
  - Prevented fallback use for older historical windows when the primary route is unavailable; this avoids pretending the Sina route can satisfy bounded historical continuity it cannot parameterize.
  - Added offline coverage for:
    - rejecting stale `1`-minute history
    - allowing older bounded `5`-minute history
    - blocking fallback misuse on older historical windows
  - Live smoke now probes bounded historical `5`-minute windows with at least two distinct trade dates instead of a latest-only sample path.

- whether `a_share_minute_bars` capability truth changed
  - Status remains `partial`.
  - Updated wording only: public AKShare has stronger bounded non-`1`-minute history than recent-only `1`-minute retention, but broader intraday continuity and trading-grade source breadth are still unproven.

- deviations
  - No file-scope deviations from the handoff.
  - No controller-owned files, downstream modules, credentials, or extra adapters were touched.

- risks/follow-up
  - Live historical proof remains blocked in this environment by proxy/upstream connectivity to Eastmoney.
  - If the controller wants closure-ready live evidence later, a rework should be run from an environment that can reach Eastmoney without the current proxy failure.
  - Public `1`-minute continuity is still recent-only; full longer-horizon minute continuity would need a genuinely date-bounded public route, not synthesis or over-broad fallback use.
