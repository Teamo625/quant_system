# TASK-029 Execution Report (A-share Capital Flow Snapshot Adapter)

## Task

- Task ID: `TASK-029`
- Active Handoff: `coordination/handoffs/TASK-029_DATAHUB_AKSHARE_A_SHARE_CAPITAL_FLOW_SNAPSHOT_ADAPTER.md`
- Dataset Scope: `DatasetName.CAPITAL_FLOW_SNAPSHOT` (A-share one-symbol slice only)
- Module Scope: DataHub only

## Files Changed

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `quant/datahub/datasets.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_a_share_capital_flow_snapshot_adapter.py`
- `tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py`
- `tests/datahub/test_datasets.py`
- `tests/datahub/test_source_catalog.py`
- `coordination/reports/TASK-029_REPORT.md`

## Implementation Summary

Implemented `AkshareAShareCapitalFlowSnapshotAdapter` with bounded one-symbol A-share scope:

1. Contract and scope boundaries
   - Supports only `DatasetName.CAPITAL_FLOW_SNAPSHOT`.
   - Requires exactly one symbol.
   - Accepts canonical and raw forms (e.g. `600000.SH`, `000001.SZ`, `920000.BJ`, `600000`, `sh600000`).
   - Rejects HK, ETF/fund, index-like, invalid/ambiguous market-code combinations.

2. Bounded AKShare route design
   - Primary required route:
     - `stock_individual_fund_flow(stock=<code>, market=<sh|sz|bj>)`
     - provides required `main_net_inflow`.
   - Supplemental bounded route:
     - `stock_zh_a_hist(symbol=<code>, period='daily', adjust='', start_date, end_date)`
     - provides optional `turnover_rate`.
   - Optional bounded route:
     - `stock_hsgt_individual_em(symbol=<code>)`
     - provides optional `northbound_net_buy` from `今日增持资金`.
   - No unbounded full-market ingestion path introduced.

3. Normalization and validation behavior
   - Normalizes to stable contract fields:
     - `symbol`, `market=CN`, `trade_date`, `main_net_inflow`, `source`, `ingested_at`, `schema_version`
     - optional: `net_inflow`, `northbound_net_buy`, `turnover_rate`, `source_ts`
   - Supports DataFrame-like payloads and list-of-mapping payloads.
   - Enforces hard failures on malformed payloads, missing required source fields, invalid date/numeric values, and conflicting duplicates.
   - Applies deterministic client-side `start_date` / `end_date` filtering after normalized `trade_date`.
   - Passes bounded dates to turnover history route; when request range is not provided, uses primary-route min/max trade dates to keep bounded calls.

4. Duplicate/conflict boundaries
   - Deduplicates identical rows by `(symbol, trade_date, source)`.
   - Merges complementary duplicates when values are consistent.
   - Raises hard failure on conflicting duplicates (primary or supplemental date collisions).

5. Supplemental-route availability handling
   - Supplemental turnover/northbound network/proxy/DNS/TLS/upstream unavailability is classified and skipped without breaking valid core records.
   - Contract/normalization issues are not masked.

## Source-Truth Optionality Changes

Minimal schema hardening was applied in `quant/datahub/datasets.py`:

- `net_inflow`: changed to `required=False`
- `northbound_net_buy`: changed to `required=False`
- `turnover_rate`: changed to `required=False`
- `main_net_inflow`: remains required

Rationale:

- The bounded primary route (`stock_individual_fund_flow`) reliably exposes `主力净流入-净额` but does not reliably expose a dedicated total-net field in all cases.
- `turnover_rate` and `northbound_net_buy` come from supplemental routes and should remain truthful optional enrichments, not closure-blocking required fields.
- No placeholder synthesis was introduced.

Related test and catalog alignment:

- Updated `tests/datahub/test_datasets.py` required-field expectations.
- Updated `quant/datahub/source_catalog.py` + `tests/datahub/test_source_catalog.py` so AKShare `A_SHARE_FULL_DATA` stable datasets include `CAPITAL_FLOW_SNAPSHOT`.

## Tests Run

1. Focused offline adapter test
   - `python3 -m unittest tests/datahub/test_akshare_a_share_capital_flow_snapshot_adapter.py`
   - Result: PASS (`Ran 22 tests`)

2. Focused live test (default gate)
   - `python3 -m unittest -v tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py`
   - Result: PASS (`Ran 3 tests`, `OK (skipped=1)`)

3. Related regressions requested by handoff
   - `python3 -m unittest tests/datahub/test_akshare_adapter.py` -> PASS (`Ran 10 tests`)
   - `python3 -m unittest tests/datahub/test_akshare_a_share_valuation_snapshot_adapter.py` -> PASS (`Ran 24 tests`)
   - `python3 -m unittest tests/datahub/test_akshare_a_share_corporate_actions_adapter.py` -> PASS (`Ran 19 tests`)
   - `python3 -m unittest tests/datahub/test_datasets.py` -> PASS (`Ran 27 tests`)
   - `python3 -m unittest tests/datahub/test_source.py` -> PASS (`Ran 20 tests`)
   - `python3 -m unittest tests/datahub/test_quality.py` -> PASS (`Ran 7 tests`)
   - `python3 -m unittest tests/datahub/test_source_catalog.py` -> PASS (`Ran 6 tests`)

4. Full DataHub discovery
   - `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`
   - Result: PASS (`Ran 442 tests`, `OK (skipped=17)`)

5. Mandatory live-enabled smoke
   - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py`
   - Result: `OK (skipped=1)`
   - Skip evidence:
     - `ProxyError: HTTPSConnectionPool(host='push2his.eastmoney.com', port=443) ... Unable to connect to proxy ... Remote end closed connection without response`

## Default Network Behavior

- Default test runs remain offline-safe.
- Newly added offline tests use injected fixtures/callables and do not require live network.
- Live behavior remains explicitly gated by `QUANT_SYSTEM_LIVE_TESTS=1`.

## Live-Enabled Result (Mandatory)

- Final live-enabled status: `SKIP` (environmental network/proxy unavailability)
- Root cause evidence:
  - primary capital-flow endpoint `push2his.eastmoney.com` unreachable via current proxy path.
- Feasible repository-level fixes attempted in this round:
  1. Added robust network-unavailability classification for live smoke diagnostics.
  2. Ensured supplemental-route outages do not block valid core records.
  3. Preserved hard-fail behavior for contract/normalization defects.
- Remaining blocker:
  - Primary required route is externally unreachable in current environment; no scope-compliant repository fallback exists without violating bounded-route constraints.

## Deviations From Handoff

- None.

## Risks / Follow-Up

1. Controller-side closure still depends on live-enabled `PASS`; this environment currently produces network `SKIP` on the primary source endpoint.
2. When connectivity to `push2his.eastmoney.com` is available, rerun:
   - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py`
3. Upstream AKShare payload drift remains a general risk; adapter currently keeps malformed/contract issues as hard failures.
