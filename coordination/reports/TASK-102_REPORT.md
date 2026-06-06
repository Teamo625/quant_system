# TASK-102 Report

- files changed
  - `quant/datahub/datasets.py`
  - `quant/datahub/source_catalog.py`
  - `quant/datahub/source_capabilities.py`
  - `quant/datahub/adapters/akshare.py`
  - `tests/datahub/test_datasets.py`
  - `tests/datahub/test_source_catalog.py`
  - `tests/datahub/test_source_capabilities.py`
  - `tests/datahub/test_akshare_a_share_northbound_flow_adapter.py`
  - `tests/datahub/test_akshare_a_share_northbound_flow_live.py`
  - `coordination/reports/TASK-102_REPORT.md`

- tests run
  - `python3 -m unittest tests/datahub/test_datasets.py` -> PASS (`Ran 42 tests`)
  - `python3 -m unittest tests/datahub/test_source_catalog.py` -> PASS (`Ran 9 tests`)
  - `python3 -m unittest tests/datahub/test_source_capabilities.py` -> PASS (`Ran 37 tests`)
  - `python3 -m unittest tests/datahub/test_akshare_a_share_capital_flow_snapshot_adapter.py` -> PASS (`Ran 29 tests`)
  - `python3 -m unittest tests/datahub/test_akshare_a_share_northbound_flow_adapter.py` -> PASS (`Ran 7 tests`)
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py` -> PASS (`OK`, `skipped=1`)
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_northbound_flow_live.py` -> PASS (`OK`, `skipped=1`)
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py` -> PASS
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_northbound_flow_live.py` -> PASS

- default network behavior
  - Default/offline tests stay network-safe.
  - Adapter unit tests use injected fetchers; no real network is required.
  - Both live smokes remain explicitly gated by `QUANT_SYSTEM_LIVE_TESTS=1` and skip by default when unset.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence
  - PASS
  - `CAPITAL_FLOW_SNAPSHOT` live smoke passed and returned `record_count=2`, symbols `['000001.SZ', '600000.SH']`, route counter `{'datacenter_securities_fundflow_snapshot': 2}`, min/max trade date `2026-06-05`.
  - `NORTHBOUND_FLOW_SNAPSHOT` live smoke initially skipped under a last-45-days window. Diagnosis showed the upstream `stock_hsgt_individual_em` history currently ends at `2024-08-16` for both `600000` and `000001`, so the relative 2026 window was invalid for this source.
  - After narrowing the live assertion to “historical tail availability” instead of “recent 45 days”, the dedicated northbound live smoke passed. Direct fetch summary: `record_count=3417`, symbols `['000001.SZ', '600000.SH']`, earliest dates `2017-03-16`, latest dates `2024-08-16`, `records_with_northbound_net_buy=3415`, source route `stock_hsgt_individual_em`.

- northbound route investigation result by route/source family
  - Proven dedicated public route: `AKShare stock_hsgt_individual_em`.
  - Proven source facts from that route: symbol/date holdings, holding market value, holding ratio vs A-shares, daily share delta, daily增持资金, daily holding market-value change.
  - Existing capital-flow family remained unchanged: `stock_individual_fund_flow` primary dated route, `datacenter_securities_fundflow_snapshot` bounded latest-only fallback, `stock_zh_a_hist` optional turnover enrichment, `stock_hsgt_individual_em` optional northbound enrichment.
  - Local AKShare surface inspection shows other `stock_hsgt_*` functions exist, but no broader second symbol/date no-credential northbound route was proven or wired in this task.

- dedicated contract/profile fields, granularity, identity, and known limitations
  - Added `DatasetName.NORTHBOUND_FLOW_SNAPSHOT` as a dedicated first-class contract surface.
  - Required fields: `symbol`, `market`, `trade_date`, `northbound_shares_held`, `northbound_holding_market_value`, `northbound_holding_ratio_a_share_pct`, `source`, `source_route`, `ingested_at`, `schema_version`.
  - Optional source-backed fields: `northbound_share_change`, `northbound_net_buy`, `northbound_holding_market_value_change`, `source_ts`.
  - Granularity is explicit `symbol x date`; records are normalized only from source-backed facts and do not fabricate market-level quota, buy/sell decomposition, or other unsupported northbound metrics.
  - Deterministic identity remains `(symbol, trade_date, source, source_route)`.
  - Known limitations: only one public no-credential route is proven; upstream historical freshness currently stops at `2024-08-16`; market-level quota/buy-sell decomposition is still unproven.

- whether capability truth changed
  - `a_share_northbound_flow` remains `partial`.
  - Its dataset mapping now points to `NORTHBOUND_FLOW_SNAPSHOT` instead of piggybacking on `CAPITAL_FLOW_SNAPSHOT`.
  - Its source-family truth is now the proven no-credential public AKShare family for this dedicated contract.
  - `a_share_capital_flow` truth did not change and remains `partial`.

- confirmation on capital-flow compatibility and conservative truth
  - Existing `DatasetName.CAPITAL_FLOW_SNAPSHOT` behavior was preserved.
  - Optional `northbound_net_buy` enrichment for capital-flow records was kept, but northbound semantics are now also available through the dedicated contract.
  - Capital-flow route/distinct-source behavior and conservative capability wording from TASK-101 were not promoted or broadened.

- deviations
  - None.

- risks/follow-up
  - The only proven dedicated northbound public route is still `stock_hsgt_individual_em`; second-route redundancy remains open.
  - Upstream freshness for this route is stale relative to `2026-06-06`; future live smokes should continue validating historical-tail availability unless the source resumes timely updates.
  - If the controller wants broader northbound completeness, a future handoff should investigate whether any other public `stock_hsgt_*` families can support stable market-level or alternate symbol/date contract coverage without overclaiming.
