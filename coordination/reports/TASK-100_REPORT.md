# TASK-100 REPORT

- files changed:
  - `quant/datahub/adapters/akshare.py`
  - `quant/datahub/datasets.py`
  - `quant/datahub/source_capabilities.py`
  - `tests/datahub/test_akshare_a_share_valuation_snapshot_adapter.py`
  - `tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`
  - `tests/datahub/test_source_capabilities.py`
  - `coordination/reports/TASK-100_REPORT.md`

- tests run:
  - `python3 -m unittest tests/datahub/test_datasets.py`
    - PASS (`Ran 42 tests ... OK`)
  - `python3 -m unittest tests/datahub/test_source_catalog.py`
    - PASS (`Ran 9 tests ... OK`)
  - `python3 -m unittest tests/datahub/test_source_capabilities.py`
    - PASS (`Ran 36 tests ... OK`)
  - `python3 -m unittest tests/datahub/test_akshare_a_share_valuation_snapshot_adapter.py`
    - PASS (`Ran 31 tests ... OK`)
  - `python3 -m unittest -v tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`
    - PASS in current shell (`QUANT_SYSTEM_LIVE_TESTS=1` was already exported)
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`
    - PASS with default skip behavior (`OK (skipped=1)`)
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`
    - PASS (`Ran 3 tests ... OK`)

- default network behavior:
  - Offline/default adapter and capability suites use only local fixtures.
  - The valuation live smoke remains explicitly gated by `QUANT_SYSTEM_LIVE_TESTS=1`.
  - Because the current shell already had `QUANT_SYSTEM_LIVE_TESTS=1`, I additionally ran `env -u QUANT_SYSTEM_LIVE_TESTS ...` to verify the true default behavior; the live smoke skipped as designed.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence for real-source tasks:
  - PASS.
  - Command: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`
  - Result: `Ran 3 tests in 4.175s ... OK`
  - Direct post-test probe for `600000.SH` and `000001.SZ` with `start_date=today-4500d`, `end_date=today` returned:
    - `record_count=4241`
    - `symbols=['000001.SZ', '600000.SH']`
    - `min_trade_date='2014-02-12'`
    - `max_trade_date='2026-06-05'`
    - `routes={'stock_zh_valuation_baidu': 157, 'stock_value_em': 4084}`
    - `route_ranges={'stock_zh_valuation_baidu': ('2014-02-12', '2017-12-22', 157), 'stock_value_em': ('2018-01-02', '2026-06-05', 4084)}`

- long-history selector continuity validation result by selector/source route:
  - Offline routing coverage now explicitly regression-tests `近三年`, `近五年`, `近十年`, and `全部`.
  - `近三年`: remains Baidu-only (`stock_zh_valuation_baidu`) and preserved from TASK-099.
  - `近五年`: now eligible to use dated Eastmoney continuity (`stock_value_em`) when available.
  - `近十年`: now uses Baidu for pre-Eastmoney history and switches to Eastmoney from its first available trade date.
  - `全部`: same split behavior as `近十年`; Baidu preserves older history, Eastmoney carries the denser 2018+ span.
  - All normalized records still validate against `DatasetName.VALUATION_SNAPSHOT`.

- second-source investigation result by route/source family:
  - Implemented and validated:
    - `akshare_cn_hk_public_family / stock_value_em(symbol=...)`
    - public, no-credential, dated A-share valuation history with `PE(TTM)` / `市净率` / `总市值` and optional `流通市值` / `市销率`
  - Investigated but not suitable as dated second history source:
    - `stock_zh_valuation_comparison_em(symbol=...)`: latest-only comparison snapshot, no dated history
    - `stock_individual_info_em(symbol, timeout=None)`: latest-only enrichment snapshot
    - `stock_market_pe_lg(symbol='深证')`: market-level aggregate, not symbol x date history

- source route coverage and known valuation-history limitations:
  - `VALUATION_SNAPSHOT` now carries optional `source_route` so returned records preserve whether they came from `stock_zh_valuation_baidu` or `stock_value_em`.
  - For long-history windows, the adapter avoids silently merging overlapping Baidu/Eastmoney same-date facts; it keeps Baidu only before Eastmoney's first available trade date and uses Eastmoney from that point onward.
  - Latest-only enrichment from `stock_individual_info_em` / `stock_zh_valuation_comparison_em` remains bounded to the latest returned trade date and is not backfilled across older rows.
  - Public no-credential second-source redundancy is still incomplete before Eastmoney's observed coverage start (`2018-01-02` in the live sample).

- capability truth changed:
  - `a_share_valuation_history` remains `partial`.
  - Gap text now truthfully reflects validated Baidu multi-period routing plus Eastmoney dated continuity from 2018 onward; it does not promote the capability to `covered`.

- deviations:
  - None.
  - No `source_catalog` change was needed; the work stayed inside the existing `akshare_cn_hk_public_family` truth.

- risks/follow-up:
  - Pre-2018 no-credential second-source redundancy remains unresolved; older history still depends on Baidu.
  - The Baidu long-history path remains sparser than Eastmoney in the overlap era, so future hardening should continue auditing pre-2018 continuity and payload-shape stability.
  - Cross-source overlapping dates are not numerically identical in practice, so any future dual-route merge must define an explicit reconciliation policy instead of silently coalescing metrics.
