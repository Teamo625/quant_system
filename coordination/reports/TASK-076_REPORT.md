# TASK-076 Report

- files changed
  - `quant/datahub/adapters/akshare.py`
  - `quant/datahub/source_capabilities.py`
  - `tests/datahub/test_akshare_a_share_capital_flow_snapshot_adapter.py`
  - `tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py`
  - `tests/datahub/test_source_capabilities.py`
  - `coordination/reports/TASK-076_REPORT.md`

- tests run
  - `python3 -m unittest tests/datahub/test_akshare_a_share_capital_flow_snapshot_adapter.py` -> PASS (`Ran 28 tests`)
  - `python3 -m unittest tests/datahub/test_source_capabilities.py` -> PASS (`Ran 21 tests`)
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py` -> PASS with default skip (`Ran 3 tests`, `OK (skipped=1)`)
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py` -> PASS (`Ran 3 tests`, `OK`)

- default network behavior
  - Default/offline adapter tests use injected fetchers; the normalization test also patches `socket.create_connection` to fail if real network is attempted.
  - `tests/datahub/test_source_capabilities.py` is fully offline.
  - Live smoke stays skipped by default when `QUANT_SYSTEM_LIVE_TESTS` is unset.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence
  - PASS
  - Evidence: `QUANT_SYSTEM_LIVE_TESTS=1 ... test_akshare_a_share_capital_flow_snapshot_live.py` finished `OK`.
  - The live smoke asserts bounded date-window output for at least two A-share symbols (`600000.SH`, `000001.SZ`), schema-valid normalized records, sorted symbol order, and trade dates within the requested window.

- capability truth change
  - `a_share_capital_flow`: status remains `partial`; gap text was refined to reflect proven multi-symbol bounded date-window support plus remaining history/fallback limits.
  - `a_share_northbound_flow`: unchanged; remains `partial`.

- source route coverage and known capital-flow/northbound limitations
  - Primary capital-flow route: `stock_individual_fund_flow`.
  - Bounded fallback route: `datacenter_securities_fundflow_snapshot`.
  - Optional turnover enrichment: `stock_zh_a_hist`.
  - Optional northbound enrichment: `stock_hsgt_individual_em`.
  - Multi-symbol requests now flow through `SourceRequest.symbols`, deduplicate repeated requested symbols, fail fast on invalid symbols, and deterministically filter by normalized `trade_date`.
  - Remaining limitation: broader historical continuity is not proven; fallback coverage is still route-limited and northbound remains an optional field rather than a dedicated guaranteed slice.

- deviations
  - None.

- risks/follow-up
  - Capital-flow coverage should stay `partial` until a broader, non-latest-dependent history path is proven across longer windows.
  - Northbound should stay conservative until a dedicated contract/profile is added and live-proven independently of optional capital-flow enrichment.
