# TASK-096 Report

- files changed
  - `coordination/reports/TASK-096_REPORT.md`

- tests run
  - `python3 -m unittest tests/datahub/test_akshare_a_share_minute_bars_adapter.py` -> PASS (`Ran 21 tests`)
  - `python3 -m unittest tests/datahub/test_source_capabilities.py` -> PASS (`Ran 34 tests`)
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_minute_bars_live.py` -> PASS with default live skip (`Ran 5 tests`, `skipped=1`)
  - `python3 -m unittest -v tests/datahub/test_akshare_a_share_minute_bars_live.py` -> suite PASS; inherited shell live env made smoke execute, result `SKIP` (`Ran 5 tests`, `skipped=1`)
  - `NO_PROXY='*' QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_minute_bars_live.py` -> suite PASS; live smoke `SKIP` (`Ran 5 tests`, `skipped=1`)

- default network behavior
  - Default offline suites remained offline-safe.
  - The live smoke file still skips by default when `QUANT_SYSTEM_LIVE_TESTS` is unset.
  - No repository code or test behavior changed.

- live environment / proxy conditions
  - Shell had `QUANT_SYSTEM_LIVE_TESTS=1` preset.
  - Environment variables `HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, `NO_PROXY` and lowercase variants were empty.
  - `urllib.request.getproxies()` still resolved system proxies to `{'http': 'http://127.0.0.1:7892', 'https': 'http://127.0.0.1:7892', 'socks': 'http://127.0.0.1:7892'}`.
  - With `NO_PROXY='*' no_proxy='*'`, `urllib.request.getproxies()` became `{'no': '*'}`, confirming the direct-access rerun bypassed the system proxy path.

- Eastmoney reachability evidence
  - `push2his.eastmoney.com` resolved to `198.18.0.12` on this host.
  - `quote.eastmoney.com` resolved to `198.18.0.15`, and `GET https://quote.eastmoney.com/concept/sh600000.html` returned `200` with a non-empty HTML body (`len=30196`).
  - `curl -kv https://push2his.eastmoney.com/api/qt/stock/kline/get?...secid=1.600000...` completed TLS, sent the HTTP request, then failed with `curl: (52) Empty reply from server`.
  - Direct Python `requests.get(...)` probes against `push2his.eastmoney.com/api/qt/stock/kline/get` and numbered `push2his` / `push2` variants all failed with `RemoteDisconnected('Remote end closed connection without response')`, including browser-like `User-Agent` and `Referer` headers.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence for real-source tasks
  - Result: `SKIP`
  - Live smoke under inherited shell proxy resolution skipped with:
    - `ProxyError: HTTPSConnectionPool(host='push2his.eastmoney.com', port=443) ... Unable to connect to proxy ... Remote end closed connection without response`
  - Live smoke under explicit direct access (`NO_PROXY='*'`) skipped with:
    - `ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))`
  - Root cause remains environment / DNS / proxy-path / upstream reachability for Eastmoney API hosts, not a repository-side adapter, contract, or offline-test defect.

- repository code/test change after rerun
  - None.

- capability truth
  - `a_share_minute_bars` remains `partial`.
  - No capability metadata or adapter semantics changed.

- deviations
  - Added direct reachability probes (`urllib.request.getproxies()`, `requests`, `curl`, DNS resolution) to distinguish shell env, system proxy resolution, and direct API behavior.

- risks/follow-up
  - Controller closure remains blocked because the required fresh live `PASS` was not obtained.
  - Next rerun needs a host or verified working proxy path where Python can successfully fetch `https://push2his.eastmoney.com/api/qt/stock/kline/get` instead of receiving empty replies / remote disconnects.
