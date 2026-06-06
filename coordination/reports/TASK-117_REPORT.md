# TASK-117 Report

- files changed:
  - `quant/datahub/adapters/akshare.py`
  - `tests/datahub/test_akshare_hk_financial_data_adapter.py`
  - `tests/datahub/test_akshare_hk_financial_data_live.py`

- implementation summary:
  - Narrowed the HK financial route-unavailable classifier in `AkshareHKFinancialDataAdapter`.
  - Narrowed `_is_live_environment_unavailable()` in the HK financial live test helper.
  - Removed route/provider names as standalone skip triggers. `stock_financial_hk_report_em`, `stock_financial_hk_analysis_indicator_em`, `Eastmoney`, and `AKShare` now only contribute to `SKIP` when paired with genuine availability symptoms.
  - Preserved positive classification for real transport/upstream failures: proxy, timeout, DNS/name-resolution, connection refused/reset, SSL/TLS, `RemoteDisconnected`, and explicit HTTP/service-unavailable signals.
  - Added regression coverage proving route-name-bearing signature, schema/payload, and normalization defects remain hard failures rather than environment `SKIP`.

- tests run:
  - `python3 -m unittest tests.datahub.test_akshare_hk_financial_data_adapter.AkshareHKFinancialDataAdapterTests.test_hk_financial_route_unavailable_classifier_marks_network_errors tests.datahub.test_akshare_hk_financial_data_adapter.AkshareHKFinancialDataAdapterTests.test_hk_financial_route_unavailable_classifier_keeps_signature_errors_hard_failures tests.datahub.test_akshare_hk_financial_data_adapter.AkshareHKFinancialDataAdapterTests.test_hk_financial_route_unavailable_classifier_keeps_schema_errors_hard_failures tests.datahub.test_akshare_hk_financial_data_adapter.AkshareHKFinancialDataAdapterTests.test_hk_financial_route_unavailable_classifier_keeps_normalization_errors_hard_failures` -> PASS
  - `python3 -m unittest tests.datahub.test_akshare_hk_financial_data_live.AkshareHKFinancialDataLiveClassifierTests` -> PASS
  - `python3 -m unittest tests/datahub/test_akshare_hk_financial_data_adapter.py` -> PASS (`Ran 23 tests`)
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_hk_financial_data_live.py` -> PASS (`Ran 8 tests`, `skipped=2`)
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_financial_data_live.py` -> PASS (`Ran 8 tests`)

- default network behavior:
  - `tests/datahub/test_akshare_hk_financial_data_adapter.py` remains offline-safe.
  - `tests/datahub/test_akshare_hk_financial_data_live.py` still skips live smokes by default unless `QUANT_SYSTEM_LIVE_TESTS=1` is set.
  - No hidden default live network behavior was introduced.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence for real-source tasks:
  - PASS.
  - `QUANT_SYSTEM_LIVE_TESTS=1` rerun completed successfully for both HK financial statements and indicators.
  - No network/proxy/DNS/TLS/upstream skip occurred in this rerun, so the new classifier logic was exercised without masking repository-side defects.

- deviations:
  - None.

- risks/follow-up:
  - This rework is classifier-only. It does not change `hk_financial_data` capability status or broader HK financial coverage claims.
  - If future HK financial routes are added, they should reuse the same rule: route/provider tokens alone must never classify repository-side defects as environment unavailable.
