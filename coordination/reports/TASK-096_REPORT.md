# TASK-096 Report

- files changed
  - `quant/datahub/adapters/baostock.py`
  - `quant/datahub/adapters/__init__.py`
  - `quant/datahub/__init__.py`
  - `quant/datahub/source_catalog.py`
  - `quant/datahub/source_capabilities.py`
  - `tests/datahub/test_baostock_a_share_minute_bars_adapter.py`
  - `tests/datahub/test_baostock_a_share_minute_bars_live.py`
  - `tests/datahub/test_source_catalog.py`
  - `tests/datahub/test_source_capabilities.py`
  - `coordination/reports/TASK-096_REPORT.md`

- tests run
  - `python3 -m unittest tests/datahub/test_baostock_a_share_minute_bars_adapter.py` -> PASS (`Ran 9 tests`)
  - `python3 -m unittest tests/datahub/test_source_capabilities.py` -> PASS (`Ran 34 tests`)
  - `python3 -m unittest tests/datahub/test_source_catalog.py` -> PASS (`Ran 8 tests`)
  - `python3 -m unittest -v tests/datahub/test_baostock_a_share_minute_bars_live.py` -> PASS with default live skip (`Ran 3 tests`, `skipped=1`)
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_baostock_a_share_minute_bars_live.py` -> PASS (`Ran 3 tests`)
  - `python3 -m unittest tests/datahub/test_akshare_a_share_minute_bars_adapter.py` -> PASS (`Ran 24 tests`)
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_minute_bars_live.py` -> PASS with default live skip (`Ran 5 tests`, `skipped=1`)

- default network behavior
  - Default offline suites remained offline-safe.
  - The new BaoStock live smoke file skips by default when `QUANT_SYSTEM_LIVE_TESTS` is unset.
  - Existing AKShare minute-bars live smoke still skips by default when `QUANT_SYSTEM_LIVE_TESTS` is unset.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence for real-source tasks
  - Result: `PASS` for BaoStock A-share minute-bars public historical source coverage.
  - Command: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_baostock_a_share_minute_bars_live.py`.
  - Evidence: BaoStock `login success!`, live smoke completed `Ran 3 tests ... OK`, and `logout success!`.
  - Live smoke validated `DatasetName.MINUTE_BARS` for `600000.SH` and `000001.SZ`, `minute_period=5`, bounded window `2024-01-02` through `2024-01-05`, at least two distinct trade dates, source `baostock_public_cn`, market `A_SHARE`, and schema-valid normalized records.
  - Prior Eastmoney evidence remains true: `push2his.eastmoney.com` / numbered `push2his` / `push2.eastmoney.com` minute-bars API paths were unavailable in this environment with remote disconnect / empty reply. This implementation avoids treating that Eastmoney environment failure as the only closure route by adding a separate no-credential public BaoStock source.

- source routes investigated and which route is used
  - Implemented route: BaoStock `query_history_k_data_plus(...)` after credential-free `login()`.
  - Adapter query shape:
    - `fields="date,time,code,open,high,low,close,volume,amount,adjustflag"`
    - `frequency in {"5", "15", "30", "60"}`
    - `adjustflag="3"` for raw source bars
    - explicit caller-provided `start_date` / `end_date`
  - Existing AKShare/Eastmoney routes remain available in the existing adapter, but are not promoted as the successful live source for this rerun.

- historical continuity, bounded-window, interval, and fallback limitations
  - BaoStock provides stronger no-credential historical continuity for explicit-date-window `5/15/30/60` minute bars than the currently unreachable Eastmoney `push2his` route in this environment.
  - BaoStock `1`-minute history is intentionally unsupported by this adapter because this task did not verify a stable BaoStock 1-minute historical route.
  - The adapter still requires caller-provided symbols and a bounded date window. It does not implement full-market minute-bar collection or unbounded history backfill.
  - The capability remains conservative because full long-history continuity, full-market breadth, 1-minute historical continuity, and deeper public-source redundancy remain incomplete.

- capability truth changed
  - `a_share_minute_bars` remains `partial`.
  - Added `baostock_public_cn` to `a_share_minute_bars.source_family_ids`.
  - Updated `a_share_minute_bars` gap text to record BaoStock no-credential multi-symbol explicit-date-window `5/15/30/60` historical minute-bar evidence while preserving remaining limitations.
  - Added `baostock_public_cn` to the source catalog as a no-credential live public source for `DatasetName.MINUTE_BARS` under A-share stock coverage.

- deviations
  - The active project state still described TASK-096 as an Eastmoney live PASS rerun. The owner explicitly authorized implementing the BaoStock主源 plan in this window, so this execution widened the route from an Eastmoney-only rerun to a no-credential public-source replacement path for TASK-096 closure evidence.
  - No controller-owned coordination state files were edited.

- risks/follow-up
  - A fresh Review Agent pass is required before Controller closure.
  - If future Controller truth must remain Eastmoney-specific, TASK-096 should still stay open for a separate Eastmoney network rerun; otherwise, the BaoStock live PASS provides the public no-credential minute-bars history continuity evidence needed to unblock the current single-source Eastmoney failure.
  - Future hardening should evaluate `1`-minute historical public-source continuity, pytdx/Sina/Tencent redundancy, and broader universe sampling before any promotion beyond `partial`.
