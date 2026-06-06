# TASK-107 Report

- files changed
  - `quant/datahub/adapters/akshare.py`
  - `quant/datahub/datasets.py`
  - `quant/datahub/source_capabilities.py`
  - `tests/datahub/test_akshare_a_share_financial_data_adapter.py`
  - `tests/datahub/test_akshare_a_share_financial_data_live.py`
  - `tests/datahub/test_datasets.py`
  - `tests/datahub/test_source_capabilities.py`
  - `coordination/reports/TASK-107_REPORT.md`

- implementation summary
  - Added compatible optional `source_route` and `metric_family` fields to `DatasetName.FINANCIAL_INDICATORS`.
  - A-share financial-indicator normalization now emits `source_route="stock_financial_analysis_indicator_em"` on every normalized record.
  - Added deterministic `metric_family` truth for common per-share, growth, profitability, cash-flow, leverage/solvency, operating-efficiency, return, liquidity, asset-quality, capital-adequacy, scale, and fallback `other` indicator groups.
  - Hardened indicator deduplication to keep same symbol/report-period/metric records from distinct `source_route` values separate instead of silently coalescing them.
  - Expanded offline and live assertions for indicator provenance and capability wording without changing `FINANCIAL_STATEMENTS` behavior.

- tests run
  - `python3 -m unittest tests/datahub/test_akshare_a_share_financial_data_adapter.py`
    - `Ran 19 tests in 0.012s`
    - `OK`
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_financial_data_live.py`
    - `Ran 5 tests in 0.001s`
    - `OK (skipped=2)`
  - `python3 -m unittest tests/datahub/test_source_capabilities.py`
    - `Ran 38 tests in 0.001s`
    - `OK`
  - `python3 -m unittest tests/datahub/test_datasets.py`
    - `Ran 42 tests in 0.016s`
    - `OK`
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_financial_data_live.py`
    - `Ran 5 tests in 7.692s`
    - `OK`

- default network behavior
  - Default adapter/capability/contract tests remain offline-safe and use fixtures or injected callables only.
  - The live test module still skips both live smokes unless `QUANT_SYSTEM_LIVE_TESTS=1` is explicitly set.
  - New provenance and classifier regressions are offline-only.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence
  - `PASS`
  - Evidence: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_financial_data_live.py` finished `OK`.
  - The live financial-indicators smoke validated real `FINANCIAL_INDICATORS` records through `DatasetRegistry` and asserted:
    - `source == "akshare_cn_hk_public_family"`
    - `source_route == "stock_financial_analysis_indicator_em"`
    - canonical A-share symbols
    - bounded `report_period_end` filtering inside the requested window
    - emitted `metric_family` values from the allowed normalized family set
  - No environment/upstream skip classification was used in the final run.

- capability truth changed
  - `a_share_financial_indicators` remains `partial`.
  - Status was not promoted. Gap wording is now more explicit about the currently proven Eastmoney route plus source-route/indicator-family provenance and the remaining public-source limitations.

- source route coverage and known financial-indicator history limitations
  - Proven route in this task: `stock_financial_analysis_indicator_em`
  - Proven source truth in this task: explicit `source_route` and normalized `metric_family` on A-share financial-indicator records
  - Proven behavior: caller-provided multi-symbol bounded report-period history, deterministic sorting, route-aware duplicate handling, route-signature hard failures, and live schema validation
  - Remaining limitations: no validated second no-credential public indicator route, no proof of full long-history continuity, and no proof that all cross-industry indicator families are complete enough to mark the capability `covered`

- deviations
  - None.

- risks/follow-up
  - `metric_family` is deterministic and conservative, but some long-tail upstream metric codes still fall back to `other`; future hardening can expand explicit family coverage if another public route or broader cross-industry evidence is added.
  - Public A-share financial-indicator coverage is still only proven through the bounded Eastmoney route; redundancy and full continuity remain unresolved.
