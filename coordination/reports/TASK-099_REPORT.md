# TASK-099 REPORT

- files changed:
  - `quant/datahub/adapters/akshare.py`
  - `quant/datahub/source_capabilities.py`
  - `tests/datahub/test_akshare_a_share_valuation_snapshot_adapter.py`
  - `tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`
  - `tests/datahub/test_source_capabilities.py`

- tests run:
  - `python3 -m unittest tests/datahub/test_datasets.py`
    - PASS (`Ran 42 tests ... OK`)
  - `python3 -m unittest tests/datahub/test_source_catalog.py`
    - PASS (`Ran 9 tests ... OK`)
  - `python3 -m unittest tests/datahub/test_source_capabilities.py`
    - PASS (`Ran 36 tests ... OK`)
  - `python3 -m unittest tests/datahub/test_akshare_a_share_valuation_snapshot_adapter.py`
    - PASS (`Ran 29 tests ... OK`)
  - `python3 -m unittest -v tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`
    - PASS with default skip behavior (`Ran 3 tests ... OK`)
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`
    - PASS (`Ran 3 tests ... OK`)

- default network behavior:
  - Default/offline suites use local fixtures only.
  - Live smoke remains explicitly gated by `QUANT_SYSTEM_LIVE_TESTS=1`.
  - Verified default run of the live file without the env gate; the live smoke stayed skipped by default.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence for real-source tasks:
  - PASS.
  - Live smoke requested `VALUATION_SNAPSHOT` for `600000.SH` and `000001.SZ` with `start_date=today-450d`, `end_date=today`.
  - Command result: `Ran 3 tests in 4.172s ... OK`.
  - Direct probe after the test returned:
    - `record_count=900`
    - `symbols=['000001.SZ', '600000.SH']`
    - `min_trade_date='2025-03-13'`
    - `max_trade_date='2026-06-05'`
  - This proves the repository now retrieves source-backed valuation records well beyond the prior bounded near-year path in the current environment.

- valuation-history route investigation result by route/source family:
  - `akshare_cn_hk_public_family` / `stock_zh_valuation_baidu`:
    - local AKShare signature/doc inspection confirmed `period` choices `近一年 / 近三年 / 近五年 / 近十年 / 全部`
    - repository hardening now selects the smallest period that covers the earliest requested date instead of always forcing `近一年`
    - dated history still comes only from this Baidu-backed route
  - `akshare_cn_hk_public_family` / `stock_individual_info_em`:
    - still latest-only enrichment for `market_cap`, `float_market_cap`, and optional snapshot fields when available
    - not used as a historical valuation series source
  - `akshare_cn_hk_public_family` / `stock_zh_valuation_comparison_em`:
    - still latest-only optional enrichment for `ps_ttm` / `dividend_yield`
    - not used as a historical valuation series source
  - no second stable no-credential dated valuation-history source was identified in the current AKShare public family

- source route coverage and known valuation-history limitations:
  - Caller-provided A-share symbols now support bounded valuation windows that can reach Baidu's multi-period selectors instead of being capped in-repo at `近一年`.
  - Latest-only requests still return one latest snapshot per symbol.
  - Historical rows still rely on Baidu dated metrics; comparison and individual-info routes do not backfill older dates.
  - Full-history continuity, second-source redundancy, and long-run route-shape stability remain unproven, so the capability cannot be promoted to `covered`.

- capability truth changed:
  - `a_share_valuation_history` remains `partial`.
  - Gap metadata was updated to reflect proven multi-period public-route breadth rather than only bounded near-year coverage.

- deviations:
  - No source catalog change was needed; source family truth did not expand beyond the existing AKShare public family.

- risks/follow-up:
  - `stock_zh_valuation_baidu` remains the only validated no-credential dated valuation-history source in this repository.
  - Very old requests may require `近十年` or `全部`; upstream payload size/shape stability for those longer selectors is still source-dependent.
  - Future hardening should target second-source redundancy or stronger continuity validation for the longest-history selectors before any capability promotion.
