# TASK-075 REPORT

- files changed:
  - `quant/datahub/adapters/akshare.py`
  - `quant/datahub/source_capabilities.py`
  - `tests/datahub/test_akshare_a_share_valuation_snapshot_adapter.py`
  - `tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`
  - `tests/datahub/test_source_capabilities.py`

- tests run:
  - `python3 -m unittest tests/datahub/test_akshare_a_share_valuation_snapshot_adapter.py`
    - PASS (`Ran 27 tests ... OK`)
  - `python3 -m unittest tests/datahub/test_source_capabilities.py`
    - PASS (`Ran 20 tests ... OK`)
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`
    - PASS with default skip behavior (`Ran 3 tests ... OK (skipped=1)`)
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`
    - PASS (`Ran 3 tests ... OK`)

- default network behavior:
  - Default/offline adapter and capability tests use local fixtures only.
  - Live smoke remains gated by `QUANT_SYSTEM_LIVE_TESTS=1`.
  - Verified skip path explicitly with `env -u QUANT_SYSTEM_LIVE_TESTS ...`; the live smoke did not run and was skipped by default.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence:
  - PASS.
  - Live smoke requested `VALUATION_SNAPSHOT` for `600000.SH` and `000001.SZ` with a bounded window of `today-10d .. today`.
  - Command result: `Ran 3 tests in 4.132s ... OK`.
  - Direct post-test sample probe returned:
    - `record_count=20`
    - `symbols=['000001.SZ', '600000.SH']`
    - `min_trade_date='2026-05-26'`
    - `max_trade_date='2026-06-04'`
  - This proves caller-provided multi-symbol bounded valuation access on the public AKShare path in the current environment.

- capability truth change:
  - `a_share_valuation_history` remains `partial`.
  - Gap text was refined to reflect proven caller-provided multi-symbol bounded near-year coverage while keeping longer-history breadth/pagination unproven.

- source route coverage and known valuation-history limitations:
  - `stock_zh_valuation_baidu` now drives deterministic per-symbol date-series normalization for required metrics (`pe_ttm`, `pb`, `market_cap`) and optional dated metrics (`ps_ttm`, `dividend_yield`) when available.
  - Multi-symbol requests are handled through `SourceRequest.symbols`; invalid or unsupported symbols fail the batch clearly before partial success is returned.
  - Unbounded requests preserve latest-snapshot behavior by returning the latest dated record per symbol.
  - Bounded requests return sorted `(symbol, trade_date)` series records inside the requested window.
  - Latest-only enrichment from optional snapshot routes is applied only to the latest trade date for a symbol; it is not projected backward across historical rows.
  - Public AKShare still exposes only bounded near-year valuation history here; broader history/pagination remains incomplete.
  - In the live sample, `float_market_cap` / `source_ts` were absent because the optional latest-only enrichment route was not needed for a PASS result and did not contribute fields in the returned sample.

- deviations:
  - None.

- risks/follow-up:
  - Longer valuation history beyond the bounded public route is still not standardized; future hardening would need deeper history breadth and pagination strategy.
  - Optional latest-only enrichment fields remain source-dependent and may be absent in live runs even when the core dated valuation series passes.
