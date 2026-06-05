# TASK-096 Report

- files changed
  - `coordination/reports/TASK-096_REPORT.md`

- tests run
  - `python3 -m unittest tests/datahub/test_akshare_a_share_minute_bars_adapter.py` -> PASS (`Ran 21 tests`)
  - `python3 -m unittest tests/datahub/test_source_capabilities.py` -> PASS (`Ran 34 tests`)
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_minute_bars_live.py` -> PASS with default live skip (`Ran 5 tests`, `skipped=1`)
  - `python3 -m unittest -v tests/datahub/test_akshare_a_share_minute_bars_live.py` -> suite exit PASS with live path active from preset shell env; live smoke SKIP (`Ran 5 tests`, `skipped=1`)
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_minute_bars_live.py` -> suite exit PASS; live smoke SKIP (`Ran 5 tests`, `skipped=1`)

- default network behavior
  - Default offline suites remained offline-safe.
  - The live smoke file still skips by default when `QUANT_SYSTEM_LIVE_TESTS` is unset.
  - No repository code or test changes were needed for this rerun.

- live environment / proxy conditions
  - Shell environment had `QUANT_SYSTEM_LIVE_TESTS='1'` preset.
  - Standard proxy env vars in `os.environ` were unset: `http_proxy`, `https_proxy`, `HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, `all_proxy`, `NO_PROXY`, `no_proxy`.
  - Python `urllib.request.getproxies()` still resolved system proxies to `http://127.0.0.1:7892` for `http` and `https`, plus `socks` on the same endpoint.
  - `NO_PROXY='*' no_proxy='*'` reduced `urllib.request.getproxies()` to `{'no': '*'}`, confirming the direct probe bypassed the system proxy path.

- Eastmoney reachability evidence
  - Default Python networking probe to `https://push2his.eastmoney.com/api/qt/stock/kline/get?...secid=1.600000...` failed with `requests.exceptions.ProxyError` caused by `RemoteDisconnected('Remote end closed connection without response')`.
  - Direct Python probe with `NO_PROXY='*' no_proxy='*'` failed with `requests.exceptions.ConnectionError` caused by the same remote disconnect.
  - Direct `curl -I --max-time 20 https://push2his.eastmoney.com/api/qt/stock/kline/get?...secid=1.600000...` failed with `curl: (52) Empty reply from server`.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence for real-source tasks
  - Result: `SKIP`
  - Live smoke output:
    - `skipped "live AKShare A-share minute-bars source unavailable in current environment for bounded historical 5-minute trade-date windows: ProxyError: HTTPSConnectionPool(host='push2his.eastmoney.com', port=443) ... Unable to connect to proxy ... Remote end closed connection without response"`
  - Root-cause evidence:
    - The host remained unreachable through the macOS system proxy path resolved by Python.
    - Bypassing that proxy path did not produce a working direct API response; the remote endpoint still closed the connection / returned an empty reply.
  - Assessment: the blocker remains environment / proxy / upstream connectivity, not a repository-side adapter, contract, or default-test defect.

- repository code/test change after rerun
  - None.

- capability truth
  - `a_share_minute_bars` remains `partial`.
  - No adapter behavior or capability metadata changed.

- deviations
  - Added direct Python and `curl` API probes, plus an explicit `NO_PROXY='*'` verification, to distinguish system-proxy failure from direct-connect failure.

- risks/follow-up
  - Controller closure remains blocked because the required fresh live `PASS` evidence was not obtained.
  - A future rerun needs an environment or verified working proxy path where Python can complete HTTPS requests to `push2his.eastmoney.com/api/qt/stock/kline/get` without remote disconnects.
