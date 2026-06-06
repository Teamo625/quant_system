# TASK-106 Report

- files changed
  - `quant/datahub/adapters/akshare.py`
  - `quant/datahub/datasets.py`
  - `quant/datahub/source_capabilities.py`
  - `tests/datahub/test_akshare_a_share_financial_data_adapter.py`
  - `tests/datahub/test_akshare_a_share_financial_data_live.py`
  - `tests/datahub/test_datasets.py`
  - `tests/datahub/test_source_capabilities.py`
  - `coordination/reports/TASK-106_REPORT.md`

- implementation summary
  - Added optional `source_route` contract support to `DatasetName.FINANCIAL_STATEMENTS`.
  - A-share financial-statement normalization now emits `source_route="stock_financial_report_sina"` on every normalized statement record.
  - Tightened A-share financial live-unavailable classification so route/provider names alone no longer downgrade signature, payload-shape, schema, or normalization defects into environment `SKIP`.
  - Added offline regression coverage for statement provenance, route-signature hard failures, classifier truthfulness, and updated capability wording.
  - Updated `a_share_financial_statements` gap wording to reflect the currently proven Sina three-statement-family bounded coverage and the remaining continuity/redundancy gaps.

- tests run
  - `python3 -m unittest tests/datahub/test_akshare_a_share_financial_data_adapter.py`
    - `Ran 17 tests ... OK`
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_financial_data_live.py`
    - `Ran 5 tests ... OK (skipped=2)`
  - `python3 -m unittest tests/datahub/test_source_capabilities.py`
    - `Ran 38 tests ... OK`
  - `python3 -m unittest tests/datahub/test_datasets.py`
    - `Ran 42 tests ... OK`
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_financial_data_live.py`
    - `Ran 5 tests in 5.885s ... OK`

- default network behavior
  - Default adapter/capability/schema tests remain offline-safe and use only fixtures/injected callables.
  - The live suite still skips by default unless `QUANT_SYSTEM_LIVE_TESTS=1` is set.
  - New classifier regressions are offline-only and specifically verify that route-named payload/signature defects remain hard failures.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence
  - `PASS`
  - Evidence: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_financial_data_live.py` finished `OK`.
  - The live financial-statements smoke validated real records through `DatasetRegistry` and asserted:
    - `source == "akshare_cn_hk_public_family"`
    - `source_route == "stock_financial_report_sina"`
    - `market == "A_SHARE"`
    - canonical A-share symbols
    - bounded `report_period_end` filtering inside the requested window
  - No environment/upstream skip root cause applied in the final run.

- capability truth changed
  - `a_share_financial_statements` remains `partial`.
  - Status was not promoted. Only the gap wording became more explicit about currently proven Sina statement-family coverage and remaining public-source limitations.

- source route coverage and known financial-statement history limitations
  - Proven route in this task: `stock_financial_report_sina`
  - Proven statement families in this task: `资产负债表`, `利润表`, `现金流量表`
  - Proven behavior: caller-provided multi-symbol bounded report-period history, explicit canonical `statement_type`, explicit `source_route`, deterministic sorting, and hard-failure handling for signature/payload defects.
  - Remaining limitations: no validated second no-credential public statement route, no proof of full long-history continuity, and no basis yet to promote the capability to `covered`.

- deviations
  - None.

- risks/follow-up
  - The bounded public route remains Sina-only for A-share statements; public-source redundancy is still missing.
  - The stricter classifier now surfaces route-shape/signature regressions as hard failures, which is correct for closure truth but may expose upstream/API drift sooner in future live runs.
