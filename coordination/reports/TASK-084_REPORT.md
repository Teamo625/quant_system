# TASK-084 REPORT

- files changed
  - `quant/datahub/adapters/akshare.py`
  - `quant/datahub/source_capabilities.py`
  - `tests/datahub/test_akshare_fund_holdings_adapter.py`
  - `tests/datahub/test_akshare_fund_holdings_live.py`
  - `tests/datahub/test_source_capabilities.py`

- tests run
  - `python3 -m unittest tests/datahub/test_akshare_fund_holdings_adapter.py` -> PASS (`Ran 30 tests`)
  - `python3 -m unittest tests/datahub/test_source_capabilities.py` -> PASS (`Ran 29 tests`)
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_fund_holdings_live.py` -> PASS (`OK (skipped=1)`)
  - `python3 -m unittest -v tests/datahub/test_akshare_fund_holdings_live.py` -> PASS (`Ran 3 tests`)
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_fund_holdings_live.py` -> PASS (`Ran 3 tests`)

- default network behavior
  - Default/offline adapter and capability tests use injected fixtures only and do not perform real network calls.
  - Live smoke remains gated by `QUANT_SYSTEM_LIVE_TESTS=1`; explicit `env -u QUANT_SYSTEM_LIVE_TESTS` verification confirmed skip-by-default behavior.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence
  - PASS
  - Live request used `symbols=("510300.ETF_CN", "159915.ETF_CN")`, `start_date=2025-01-01`, `end_date=2025-03-31`.
  - Direct post-test verification returned `record_count=330`, fund counts `{'159915.ETF_CN': 98, '510300.ETF_CN': 232}`, and only `report_date='2025-03-31'`.
  - During implementation, live data exposed an upstream dirty row outside the requested window (`510300`, `2025年2季度`, missing `占净值比例`/NaN). Adapter hardening now prefilters by bounded `report_date` before required-field validation so out-of-window dirty rows no longer break bounded requests.

- capability truth changed
  - `fund_holdings_composition` status remains `PARTIAL`.
  - Gap text/recommended handoff theme were refined to reflect proven caller-provided multi-symbol bounded report-period access while keeping breadth/history limits conservative.

- source route coverage and known ETF/fund holdings limitations
  - Coverage now proves caller-provided multi-symbol ETF/fund holdings access through AKShare `fund_portfolio_hold_em` with bounded report-period filtering and deterministic failure on partial batch success.
  - Canonical/bare six-digit ETF/fund codes are accepted when they match supported exchange-style public-route patterns.
  - A-share stock-like, index-like, HK stock-like, malformed, missing, and unsupported symbols fail clearly.
  - Multi-symbol requests require both `start_date` and `end_date`; single-symbol requests keep the existing latest-reporting-slice behavior.
  - Capability is still not closure-ready for broader fund breadth, longer history continuity, and non-exchange/public-route coverage.

- deviations
  - Shell environment already had `QUANT_SYSTEM_LIVE_TESTS=1`; to verify true default behavior I additionally ran the live test file with `env -u QUANT_SYSTEM_LIVE_TESTS`.

- risks/follow-up
  - AKShare yearly holdings payloads can include dirty rows or mixed-quarter rows outside the caller window; current hardening handles out-of-window noise but in-window schema drift would still correctly fail.
  - Multi-symbol batch scope is intentionally bounded by caller-supplied report-period windows; no full-market holdings collection or non-exchange route expansion was added.
