# TASK-100 REPORT

- files changed:
  - `quant/datahub/adapters/akshare.py`
  - `tests/datahub/test_akshare_a_share_valuation_snapshot_adapter.py`
  - `coordination/reports/TASK-100_REPORT.md`

- tests run:
  - `python3 -m unittest tests/datahub/test_datasets.py`
    - PASS (`Ran 42 tests ... OK`)
  - `python3 -m unittest tests/datahub/test_source_catalog.py`
    - PASS (`Ran 9 tests ... OK`)
  - `python3 -m unittest tests/datahub/test_source_capabilities.py`
    - PASS (`Ran 36 tests ... OK`)
  - `python3 -m unittest tests/datahub/test_akshare_a_share_valuation_snapshot_adapter.py`
    - PASS (`Ran 32 tests ... OK`)
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`
    - PASS (`OK (skipped=1)`)
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`
    - PASS (`Ran 3 tests in 4.610s ... OK`)

- default network behavior:
  - Default/offline tests remain fixture-only and make no real network calls.
  - The live valuation smoke remains explicitly gated by `QUANT_SYSTEM_LIVE_TESTS=1`.
  - Verified true default behavior with `env -u QUANT_SYSTEM_LIVE_TESTS ...`; the live smoke skipped as designed.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence for real-source tasks:
  - PASS.
  - Command: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`
  - Result: `Ran 3 tests in 4.610s ... OK`
  - Direct post-test probe on `600000.SH` and `000001.SZ` with `start_date=today-4500d` returned:
    - `record_count=4581`
    - `route_counts={'stock_zh_valuation_baidu': 497, 'stock_value_em': 4084}`
    - `overlap_count=267`
    - first overlapping symbol/date: `('000001.SZ', '2018-01-12')`
    - first overlapping metrics stayed route-distinct:
      - `stock_value_em`: `pe_ttm=10.101119`, `pb=1.15120199`, `market_cap=232659074009.3`
      - `stock_zh_valuation_baidu`: `pe_ttm=10.1`, `pb=1.17`, `market_cap=232659000000.0`

- final Baidu/Eastmoney overlap policy:
  - Removed the first-secondary-date cutover filter from `_combine_long_history_records`.
  - Long-window valuation history now preserves both Baidu and Eastmoney records when the same `symbol + trade_date` exists in both routes.
  - Deterministic deduplication still keys on `(symbol, trade_date, source, source_route)`, so same-route duplicate conflicts still fail, while cross-route disagreements remain visible as separate source facts.

- evidence for overlapping same-date disagreement handling:
  - Offline regression `test_long_history_windows_keep_cross_route_overlaps_visible` now expects both `stock_value_em` and `stock_zh_valuation_baidu` on `2018-01-02` and `2024-06-12`.
  - That regression proves same-date cross-route differences are not silently hidden: on `2018-01-02`, Eastmoney keeps `market_cap=300100000000.0`, while Baidu keeps `market_cap=300000000000.0` and different `pe_ttm`.
  - Live probe also found `267` overlapping symbol/date pairs preserved as dual-route records.

- evidence for secondary-route gap handling after the earliest Eastmoney date:
  - Offline regression `test_long_history_windows_keep_baidu_records_when_secondary_has_gap` uses Eastmoney data for `2018-01-02` and `2024-06-12` but omits `2024-06-11`.
  - Result stays source-truthful: the `2024-06-11` Baidu record remains in normalized output instead of being dropped because Eastmoney started earlier.

- normalized record validation:
  - Successful paths still validate under `DatasetRegistry.validate_record(DatasetName.VALUATION_SNAPSHOT, ...)`.
  - The two new long-window regressions assert schema validation for every returned record.

- capability truth changed:
  - No.
  - `a_share_valuation_history` remains `partial`; no `source_catalog` or `source_capabilities` edit was needed.

- deviations:
  - None.

- risks/follow-up:
  - Latest-trade-date enrichment from `stock_individual_info_em` still overwrites `market_cap` / `float_market_cap` on records at the latest returned date, regardless of whether that date is represented by one or both history routes.
  - Public no-credential redundancy before Baidu coverage gaps and broader full-history continuity are still incomplete, so this task should not be treated as capability closure.
