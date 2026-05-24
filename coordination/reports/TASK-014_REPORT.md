# TASK-014 Report (Live Network Evidence Rework)

## Task

- Task ID: `TASK-014`
- Handoff: `coordination/handoffs/TASK-014_DATAHUB_HK_LIVE_NETWORK_EVIDENCE_REWORK.md`
- Role: 5.3 execution window

## Files Changed In This Rework

- `quant/datahub/adapters/akshare.py`
- `tests/datahub/test_akshare_hk_adapter.py`
- `coordination/reports/TASK-014_REPORT.md`

## Diagnosis Evidence (HK Live Connectivity)

### 1) Proxy environment variables (redacted)

Command:

- `python3 - <<'PY' ... os.getenv(...) ... PY`

Result:

- `HTTP_PROXY=<unset>`
- `HTTPS_PROXY=<unset>`
- `ALL_PROXY=<unset>`
- `NO_PROXY=<unset>`
- `http_proxy=<unset>`
- `https_proxy=<unset>`
- `all_proxy=<unset>`
- `no_proxy=<unset>`

Conclusion:

- No explicit proxy environment variables are set in this runtime.

### 2) DNS resolution for `33.push2his.eastmoney.com`

Command:

- `python3 - <<'PY' ... socket.getaddrinfo(...) ... PY`

Result:

- `resolved_ip=198.18.0.114`

Conclusion:

- DNS resolution works.

### 3) TCP connectivity to `33.push2his.eastmoney.com:443`

Command:

- `python3 - <<'PY' ... socket.create_connection(...) ... PY`

Result:

- `tcp_connect=OK`
- `peer=('198.18.0.114', 443)`

Conclusion:

- TCP layer connectivity is available.

### 4) TLS/HTTPS behavior

TLS probe command:

- `python3 - <<'PY' ... ssl.create_default_context().wrap_socket(...) ... PY`

TLS probe result:

- `tls_handshake=FAIL`
- `SSLCertVerificationError: certificate verify failed: unable to get local issuer certificate`

HTTPS probe command:

- `python3 - <<'PY' ... requests.get(...) ... PY`

HTTPS probe results (same endpoint, different attempts):

- Attempt A: `status=200` with JSON body prefix
- Attempt B: `requests.exceptions.ProxyError` + `RemoteDisconnected('Remote end closed connection without response')`

Conclusion:

- L3/L4 is reachable, but higher-layer behavior is unstable: certificate path/proxy-like disconnect appears intermittently.

### 5) AKShare routing and function behavior

Routing evidence command:

- `python3 - <<'PY' ... inspect.getsource(ak.stock_hk_hist) ... PY`

Result:

- `ak.stock_hk_hist` source code explicitly calls:
  - `https://33.push2his.eastmoney.com/api/qt/stock/kline/get`

Behavior evidence command:

- `python3 - <<'PY' ... run stock_hk_hist 5x and stock_hk_daily 5x ... PY`

Result:

- `stock_hk_hist`: `OK, OK, OK, FAIL(ProxyError), FAIL(ProxyError)`
- `stock_hk_daily`: `OK` for all 5 attempts

Conclusion:

- HK primary source (`stock_hk_hist` -> Eastmoney push2his) is intermittently unavailable in this environment.
- Alternate public HK source (`stock_hk_daily`, Sina path) is stable in the same environment.

## Root-Cause Attribution

Attribution judgment:

- Not an adapter data-contract bug.
- Not a symbol/parameter mismatch (same parameters can succeed and fail intermittently).
- Primary issue is external network/source path instability to Eastmoney endpoint (proxy-like remote disconnect / TLS trust path inconsistency), which can occur even when DNS and TCP are healthy.

## Repository-Level Fix Implemented

In `AkshareHKDailyBarAdapter` (`quant/datahub/adapters/akshare.py`):

- Added fallback path:
  - primary: `stock_hk_hist(...)`
  - on network-unavailable exception chain: fallback to `stock_hk_daily(...)`
- Added explicit local date filtering after normalization for fallback payloads.
- Kept non-network exceptions as hard failures (no masking of adapter/contract bugs).

Offline test coverage added in `tests/datahub/test_akshare_hk_adapter.py`:

- `test_adapter_falls_back_to_hk_daily_when_hist_network_unavailable`
- `test_adapter_does_not_mask_non_network_hist_errors`

## Tests Run

### Mandatory live commands

1. Default gate command:

- Command: `python3 -m unittest -v tests/datahub/test_akshare_hk_live.py`
- Result: `Ran 1 test`, `OK (skipped=1)`
- Skip reason: `Live source tests are disabled. Set QUANT_SYSTEM_LIVE_TESTS=1 to enable.`

2. Live-enabled mandatory command:

- Command: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_live.py`
- Result: `Ran 1 test`, `OK`
- Successful case: `test_live_akshare_hk_daily_bars_smoke ... ok`
- Validation path: fetched records were normalized and validated via `DatasetRegistry.validate_record(DatasetName.DAILY_BARS, first_record)`.

### Focused offline tests

- `python3 -m unittest tests/datahub/test_akshare_hk_adapter.py`
  - `Ran 16 tests`, `OK`
- `python3 -m unittest tests/datahub/test_akshare_adapter.py`
  - `Ran 10 tests`, `OK`
- `python3 -m unittest tests/datahub/test_akshare_calendar_adapter.py`
  - `Ran 11 tests`, `OK`

### DataHub suite

- `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`
  - `Ran 111 tests`, `OK (skipped=3)`

## Default Network Behavior

- Default test path remains offline-safe.
- Live smoke remains explicitly gated by `QUANT_SYSTEM_LIVE_TESTS=1`.
- Default run of live file is skipped and does not force real network calls.

## Deviations From Handoff

- No deviations.

## Risks / Follow-up

- Eastmoney HK endpoint behavior is intermittent in this environment; live-enabled outcomes may still vary by network policy/time window.
- Operator follow-up recommendation:
  - check outbound network policy/proxy appliance behavior for `33.push2his.eastmoney.com:443`
  - check TLS trust chain consistency in the runtime environment
- Even with fallback, if both Eastmoney and Sina public endpoints are unavailable, live smoke will still skip with explicit external-unavailable reason (as designed by testing policy).
