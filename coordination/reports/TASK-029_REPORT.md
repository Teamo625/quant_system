# TASK-029 Execution Report (A-share Capital Flow Live-Network Rework)

## Task

- Task ID: `TASK-029`
- Active Handoff: `coordination/handoffs/TASK-029_DATAHUB_AKSHARE_A_SHARE_CAPITAL_FLOW_LIVE_NETWORK_REWORK.md`
- Dataset Scope: `DatasetName.CAPITAL_FLOW_SNAPSHOT` (A-share one-symbol slice only)
- Module Scope: DataHub only

## Files Changed

- `quant/datahub/adapters/akshare.py`
- `tests/datahub/test_akshare_a_share_capital_flow_snapshot_adapter.py`
- `tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py`
- `coordination/reports/TASK-029_REPORT.md`

## Live Blocker Reproduction (Before Rework)

Reproduced blocker before behavior changes:

- Command:
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py`
- Result:
  - `OK (skipped=1)`
- Skip evidence:
  - `ProxyError ... host='push2his.eastmoney.com' ... Unable to connect to proxy ... RemoteDisconnected(...)`

## Diagnosis Summary

1. Primary route remained unavailable in current environment:
   - `stock_individual_fund_flow(stock=<code>, market=<sh|sz|bj>)`
   - failure domain: `push2his.eastmoney.com`
2. Direct quote-host fallback variants on `push2.eastmoney.com` (`daykline/get`, `kline/get`, `ulist.np/get`) were tested and showed unstable/unavailable behavior in this environment.
3. A bounded one-symbol public route was identified as feasible and stable:
   - `https://datacenter.eastmoney.com/securities/api/data/get`
   - `type=RPT_FUNDFLOW_SECUCODE`
   - symbol filter: `(SECURITY_CODE="<6-digit>")`
   - includes `MAIN_NETINFLOW` and timestamp/quote extra columns through `extraCols`
4. This route preserves one-symbol bounded scope and does not require full-market ingestion.

## Rework Summary

Implemented bounded primary-route resilience while preserving scope and source-truth rules:

1. Primary-first with bounded fallback
   - Kept AKShare primary route preferred when available.
   - Added fallback route name: `datacenter_securities_fundflow_snapshot`.
   - Fallback only activates when primary failure is classified as route-unavailable (network/proxy/DNS/TLS/upstream).
   - Fallback endpoint:
     - `https://datacenter.eastmoney.com/securities/api/data/get`
     - query type: `RPT_FUNDFLOW_SECUCODE`
     - strict one-symbol filter by `SECURITY_CODE`.

2. Fallback normalization
   - Maps fallback payload to adapter’s existing source-row contract:
     - `日期`
     - `主力净流入-净额`
     - optional `换手率`
     - optional `source_ts` from `F124_TS`
   - Preserves required `main_net_inflow` and optionality for `net_inflow` / `northbound_net_buy` / `turnover_rate`.
   - Does not fabricate placeholders.

3. Hard-fail boundaries preserved
   - Primary contract/normalization issues still fail fast and do not silently fall back.
   - Fallback malformed payload/missing required `MAIN_NETINFLOW` still fail.
   - Supplemental route behavior unchanged: only network/source unavailability is tolerated for optional enrichments.

4. Network classification alignment
   - Extended capital-flow network unavailability classifier with fallback-route host/path tokens:
     - `datacenter.eastmoney.com`
     - `securities/api/data/get`
     - `RPT_FUNDFLOW_SECUCODE`

## Test Updates

Added/updated deterministic offline coverage for rework behavior:

1. `tests/datahub/test_akshare_a_share_capital_flow_snapshot_adapter.py`
   - primary route precedence (fallback not used when primary succeeds)
   - primary network unavailable -> bounded fallback path used
   - primary contract failure does not silently fall back
   - datacenter fallback parsing for timestamp-based `trade_date` and `source_ts`

2. `tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py`
   - live environment classifier token updates for fallback-route host/path

## Tests Run

1. Focused offline adapter test
   - `python3 -m unittest tests/datahub/test_akshare_a_share_capital_flow_snapshot_adapter.py`
   - Result: PASS (`Ran 26 tests`)

2. Focused live test (default gate)
   - `python3 -m unittest -v tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py`
   - Result: PASS (`Ran 3 tests`, `OK (skipped=1)`)

3. Required related regressions from rework handoff
   - `python3 -m unittest tests/datahub/test_datasets.py` -> PASS (`Ran 27 tests`)
   - `python3 -m unittest tests/datahub/test_source_catalog.py` -> PASS (`Ran 6 tests`)
   - `python3 -m unittest tests/datahub/test_akshare_adapter.py` -> PASS (`Ran 10 tests`)
   - `python3 -m unittest tests/datahub/test_source.py` -> PASS (`Ran 20 tests`)
   - `python3 -m unittest tests/datahub/test_quality.py` -> PASS (`Ran 7 tests`)

4. Full DataHub discovery
   - `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`
   - Result: PASS (`Ran 446 tests`, `OK (skipped=17)`)

5. Mandatory live-enabled smoke (after rework)
   - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py`
   - Result: PASS (`Ran 3 tests`, `OK`)

## Default Network Behavior

- Default tests remain offline-safe.
- New offline fallback tests use injected callables / patched responses.
- Live behavior remains explicitly gated by `QUANT_SYSTEM_LIVE_TESTS=1`.

## Live-Enabled Result (Mandatory)

- Final live-enabled status after rework: `PASS`
- Evidence command:
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py`
- Output tail:
  - `Ran 3 tests ... OK`

## Scope and Source-Truth Check

- Scope still limited to one-symbol A-share `CAPITAL_FLOW_SNAPSHOT`.
- No full-market capital-flow ingestion workaround introduced.
- `main_net_inflow` remains required.
- Optionality from TASK-029 is preserved:
  - `net_inflow` optional
  - `northbound_net_buy` optional
  - `turnover_rate` optional
- No placeholder capital-flow values were fabricated.

## Deviations From Handoff

- None.

## Risks / Follow-Up

1. Fallback route provides bounded one-symbol snapshot-style data; under primary-route outages it prioritizes closure-safe live availability over multi-day primary history completeness.
2. Upstream route payloads can still drift; malformed/contract regressions remain hard failures by design.
