# TASK-096 Report

- files changed
  - `coordination/reports/TASK-096_REPORT.md`

- tests run
  - `python3 -m unittest tests/datahub/test_akshare_a_share_minute_bars_adapter.py` -> PASS (`Ran 21 tests`)
  - `python3 -m unittest tests/datahub/test_source_capabilities.py` -> PASS (`Ran 34 tests`)
  - `python3 -m unittest -v tests/datahub/test_akshare_a_share_minute_bars_live.py` -> PASS in current shell with live env already enabled (`Ran 5 tests`, `skipped=1`)
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_minute_bars_live.py` -> PASS with default skip (`Ran 5 tests`, `skipped=1`)
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_minute_bars_live.py` -> SKIP (`Ran 5 tests`, `skipped=1`)

- default network behavior
  - Default offline suites remain offline-safe.
  - The live smoke still skips by default when `QUANT_SYSTEM_LIVE_TESTS` is unset.
  - No repository code or test changes were needed for the rerun.

- live environment / proxy conditions
  - Shell environment had `QUANT_SYSTEM_LIVE_TESTS=1` preset, so the plain live-test command exercised the enabled path until explicitly unset.
  - Standard proxy environment variables were unset in `os.environ`.
  - Python `requests` still resolved system proxies as `http://127.0.0.1:7892` for `http` and `https`.
  - `socket.getaddrinfo("push2his.eastmoney.com", 443)` resolved successfully to `198.18.0.12`.
  - `curl -I https://push2his.eastmoney.com` returned `HTTP/1.1 404 Not Found`, so basic host reachability exists.
  - Direct API probes to `https://push2his.eastmoney.com/api/qt/stock/kline/get...` failed:
    - with default Python networking: `ProxyError ... Unable to connect to proxy ... RemoteDisconnected`
    - with `NO_PROXY='*'`: `ConnectionError ... RemoteDisconnected`
    - with `curl`: `curl: (52) Empty reply from server`

- live-enabled PASS/SKIP/FAIL result and root-cause evidence for real-source task
  - Result: `SKIP`
  - Evidence:
    - required live rerun skipped with `ProxyError: HTTPSConnectionPool(host='push2his.eastmoney.com', port=443) ... Unable to connect to proxy ... Remote end closed connection without response`
    - bypassing proxy did not convert the run to PASS; Python direct requests and `curl` against the API endpoint still received remote disconnect / empty reply
  - Assessment: this remains an environment / proxy / upstream connectivity issue, not a repository-side contract or normalization defect.

- capability truth
  - `a_share_minute_bars` remains `partial`.
  - No source-capability wording or adapter behavior changed in this rerun.

- deviations
  - Added one extra verification command with `env -u QUANT_SYSTEM_LIVE_TESTS` because the shell had live tests pre-enabled and the handoff required confirming default skip behavior truthfully.

- risks/follow-up
  - Controller closure is still blocked because fresh live PASS evidence was not obtained.
  - A future rerun needs an environment where Python can reach the Eastmoney minute-bars API without the `127.0.0.1:7892` system proxy path and without remote disconnects on direct API requests.
