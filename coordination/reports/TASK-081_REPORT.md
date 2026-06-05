# TASK-081 Report

- files changed:
  - `quant/datahub/adapters/akshare.py`
  - `quant/datahub/source_capabilities.py`
  - `tests/datahub/test_akshare_hk_financial_data_adapter.py`
  - `tests/datahub/test_akshare_hk_financial_data_live.py`
  - `tests/datahub/test_source_capabilities.py`
  - `coordination/reports/TASK-081_REPORT.md`

- tests run:
  - `python3 -m unittest tests/datahub/test_akshare_hk_financial_data_adapter.py` -> PASS (`Ran 17 tests`)
  - `python3 -m unittest tests/datahub/test_source_capabilities.py` -> PASS (`Ran 26 tests`)
  - `python3 -m unittest -v tests/datahub/test_akshare_hk_financial_data_live.py` -> PASS in this shell because ambient `QUANT_SYSTEM_LIVE_TESTS=1` (`Ran 4 tests`)
  - `QUANT_SYSTEM_LIVE_TESTS=0 python3 -m unittest -v tests/datahub/test_akshare_hk_financial_data_live.py` -> PASS with default live smokes skipped (`OK (skipped=2)`)
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_financial_data_live.py` -> PASS (`Ran 4 tests`)

- default network behavior:
  - Offline adapter/capability tests do not use network.
  - The live smoke file remains gated by `QUANT_SYSTEM_LIVE_TESTS`; with `QUANT_SYSTEM_LIVE_TESTS=0` both live tests skip and only classifier tests run.
  - Note: this shell had ambient `QUANT_SYSTEM_LIVE_TESTS=1`, so the ungated `-v tests/datahub/test_akshare_hk_financial_data_live.py` command exercised live routes until explicitly overridden.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence:
  - PASS
  - Evidence: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_financial_data_live.py` completed `OK`.
  - Live smoke now validates both `00700.HK` and `00005.HK` for `FINANCIAL_STATEMENTS` and `FINANCIAL_INDICATORS`.
  - No network/proxy/DNS/TLS/upstream skip or failure occurred in this run.

- `hk_financial_data` capability truth changed:
  - Status stayed `PARTIAL`.
  - Gap text was tightened from one-symbol wording to proven multi-symbol + bounded report-period filtering, while keeping broader market breadth and long-history coverage as open gaps.

- source route coverage and known HK financial-history limitations:
  - Statements route: `stock_financial_hk_report_em` across the existing three statement types (`资产负债表`, `利润表`, `现金流量表`) for each requested symbol.
  - Indicators route: `stock_financial_hk_analysis_indicator_em` for each requested symbol.
  - Adapter now accepts caller-provided multi-symbol batches, deduplicates canonical duplicates, preserves single-symbol behavior, filters by `report_period_end`, and deterministically sorts/deduplicates output.
  - If a requested symbol normalizes but yields no usable rows, the adapter now fails clearly instead of returning a partial-success batch.
  - Limitations remain: no full-market HK stock discovery here, no non-stock taxonomy support, no guarantee of full long-history continuity from the public routes, and no promotion to trading-usable `covered`.

- deviations:
  - None from the allowed write scope.
  - Extra verification added to separate true default skip behavior from the shell's ambient live-enabled environment.

- risks/follow-up:
  - Public AKShare HK financial routes may still have symbol-specific gaps or history discontinuities outside the validated symbols/date ranges.
  - Non-stock HK instruments are rejected only when format is invalid or when normalized symbols return no usable financial rows; broader instrument-type classification would require a dedicated stock/universe validation source.
  - A future hardening slice would need broader HK stock breadth sampling and longer history continuity evidence before considering capability promotion.
