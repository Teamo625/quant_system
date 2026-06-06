# TASK-101 Report

- files changed
  - `quant/datahub/datasets.py`
  - `quant/datahub/source_capabilities.py`
  - `quant/datahub/adapters/akshare.py`
  - `tests/datahub/test_source_capabilities.py`
  - `tests/datahub/test_akshare_a_share_capital_flow_snapshot_adapter.py`
  - `tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py`

- tests run
  - `python3 -m unittest tests/datahub/test_datasets.py` -> PASS
  - `python3 -m unittest tests/datahub/test_source_catalog.py` -> PASS
  - `python3 -m unittest tests/datahub/test_source_capabilities.py` -> PASS
  - `python3 -m unittest tests/datahub/test_akshare_a_share_capital_flow_snapshot_adapter.py` -> PASS
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py` -> PASS (`live` test skipped by default)
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py` -> PASS

- default network behavior
  - Default/offline tests remain network-safe.
  - Adapter unit tests use injected fetchers and patching; no real network calls are required.
  - Live smoke remains explicitly gated by `QUANT_SYSTEM_LIVE_TESTS=1` and skips by default.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence
  - PASS
  - `QUANT_SYSTEM_LIVE_TESTS=1 ... test_live_akshare_a_share_capital_flow_snapshot_smoke ... ok`
  - Follow-up summary fetch for `600000.SH` and `000001.SZ` over the last 45 days returned `record_count=2`, symbols `['000001.SZ', '600000.SH']`, min/max trade date `2026-06-05`, and route counter `{'datacenter_securities_fundflow_snapshot': 2}`.
  - Direct investigation also showed the primary AKShare/Eastmoney history route `stock_individual_fund_flow` and its raw `push2his.eastmoney.com` endpoint still fail in the current environment with `ConnectionError` / `RemoteDisconnected`, while the datacenter fallback responds successfully.

- capital-flow route investigation result by route/source family
  - `AKShare stock_individual_fund_flow` (`push2his.eastmoney.com/api/qt/stock/fflow/daykline/get`): still the only dated per-symbol capital-flow history route exposed by local AKShare `1.18.60`; current environment could not fetch it live because the upstream connection closed without response.
  - Datacenter fallback (`https://datacenter.eastmoney.com/securities/api/data/get`, `type=RPT_FUNDFLOW_SECUCODE`): live-reachable, but response for `600000` was `pages=1`, `count=1`, and only the latest dated snapshot row; not a broader history route.
  - Other AKShare fund-flow functions inspected locally (`stock_individual_fund_flow_rank`, `stock_main_fund_flow`, `stock_market_fund_flow`, THS-style ranking functions) are ranking/market snapshots, not stable symbol x date history routes suitable for this contract.

- source route coverage, overlap/conflict policy, and known capital-flow history limitations
  - `CAPITAL_FLOW_SNAPSHOT` now accepts optional `source_route`.
  - Adapter records now carry `source_route=stock_individual_fund_flow` for primary history records and `source_route=datacenter_securities_fundflow_snapshot` for fallback records.
  - Deduplication/sorting identity is now `(symbol, trade_date, source, source_route)`, so route-distinct source facts are preserved instead of being merged together.
  - Same-route duplicate rows still merge only when values are compatible; conflicting same-route duplicates still fail.
  - Known limitation remains: no proven second public no-credential dated symbol-history route. Current live-reachable fallback is latest-only snapshot coverage, so broader history continuity is still incomplete when the primary route is unavailable.

- whether `a_share_capital_flow` capability truth changed
  - Status remains `partial`.
  - Wording was tightened to reflect actual public-route truth: Eastmoney dated primary route plus latest-only datacenter fallback, with no proven second dated symbol-history route.

- `a_share_northbound_flow`
  - Not promoted and not changed.
  - No northbound-specific contract/profile work was added.

- deviations
  - None.

- risks/follow-up
  - Live PASS in this environment currently proves only the latest-only datacenter fallback path, not the broader Eastmoney history route.
  - If the controller wants stronger continuity proof, a future handoff should target either restoring live proof for `stock_individual_fund_flow` or finding another stable no-credential dated symbol-history route with real overlap/continuity evidence.
