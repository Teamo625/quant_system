# TASK-126 Report

- files changed
  - `quant/datahub/adapters/akshare.py`
  - `quant/datahub/source_capabilities.py`
  - `quant/datahub/source_catalog.py`
  - `tests/datahub/test_akshare_index_adapter.py`
  - `tests/datahub/test_akshare_index_live.py`
  - `tests/datahub/test_source_capabilities.py`
  - `tests/datahub/test_source_catalog.py`

- implementation summary
  - Expanded `AkshareIndexDailyBarAdapter` from the prior 4-code mainland core slice to a broader bounded mainland benchmark set: `000001`, `000300`, `000688`, `000852`, `000905`, `000906`, `399001`, `399005`, `399006`.
  - Added explicit HK benchmark support for `HSI.HK_INDEX`, `HSCEI.HK_INDEX`, `HSCCI.HK_INDEX`, and `HSTECH.HK_INDEX` through `stock_hk_index_daily_sina`.
  - Added per-record `source_route` truth and preserved route-distinct deduplication identity with `(index_code, trade_date, source, source_route)`.
  - Kept bounded date-window enforcement, invalid-symbol hard failure, whole-batch failure on empty usable rows, offline-safe default tests, and existing China index dataset compatibility.

- index daily-bar route/source-family investigation result
  - Adopted mainland routes already present in the adapter resolution order: `stock_zh_index_daily_tx`, `stock_zh_index_daily`, `stock_zh_index_daily_em`, `index_zh_a_hist`.
  - Adopted HK route: `stock_hk_index_daily_sina`. In local probing it returned stable historical OHLCV/amount rows for `HSI`, `HSTECH`, and `CES100`; `stock_hk_index_daily_em` hit `ConnectionError(RemoteDisconnected(...))` in the current environment and was not made the primary path.
  - Investigated global routes but did not promote them:
    - `index_global_hist_sina` returned history, but only via Chinese-name keyed symbols and only `1000` rows in sampled calls.
    - `index_global_spot_em` failed with `ConnectionError(RemoteDisconnected(...))` in the current environment.
    - `index_global_hist_em` raised `KeyError` for sampled major benchmark names used in local probing.
  - Capability/catalog truth was updated to reflect broader mainland plus major HK benchmark proof while keeping global coverage and independent redundancy incomplete.

- supported symbol classes, date behavior, source-route truth, and deduplication behavior
  - Supported canonical classes:
    - Mainland: bare 6-digit benchmark codes, source-native `sh/sz` codes, and canonical `.CN_INDEX`.
    - HK: explicit `.HK_INDEX` benchmark codes only.
  - Unsupported symbols still fail clearly for A-share stocks, ETF/fund codes, HK stocks, malformed values, and unmapped benchmarks.
  - Date behavior remains deterministic and bounded by caller `start_date`/`end_date`; wider source payloads are filtered locally.
  - Normalized records now carry `source_route`; mainland live reads used `stock_zh_index_daily_tx`, HK live reads used `stock_hk_index_daily_sina`.
  - Route-distinct duplicates remain distinguishable; same-route duplicates still merge only when source-backed facts agree.

- tests run
  - `python3 -m unittest tests.datahub.test_source_capabilities` -> PASS
  - `python3 -m unittest tests.datahub.test_source_catalog` -> PASS
  - `python3 -m unittest tests.datahub.test_akshare_index_adapter` -> PASS
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_index_live` -> PASS (`OK (skipped=2)`)
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_index_live` -> PASS

- default network behavior
  - Default/unit coverage remains offline-safe.
  - Live index network access remains explicitly gated behind `QUANT_SYSTEM_LIVE_TESTS=1`.
  - No unbounded full-market index fetch path was introduced; `symbols=None` or empty symbols still fail.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence for real-source tasks
  - PASS
  - Command: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_index_live`
  - Evidence from direct readback after the live suite:
    - Mainland request `000300.CN_INDEX`, `399001.CN_INDEX`, `000905.CN_INDEX` over `2024-01-02..2024-01-05` returned `12` records total; each symbol returned `4` rows; route=`stock_zh_index_daily_tx`.
    - HK request `HSI.HK_INDEX`, `HSTECH.HK_INDEX` over `2024-01-02..2024-01-10` returned `14` records total; each symbol returned `7` rows; route=`stock_hk_index_daily_sina`.
  - No repository-side schema, normalization, signature, or partial-success defect was observed in the live-enabled run.

- whether `index_daily_bars` capability truth changed
  - Status unchanged: remains `partial`.
  - Truth changed: it now reflects broader bounded mainland benchmark coverage plus major HK benchmark history with explicit route truth; global benchmark history and independent public-route redundancy remain incomplete.

- confirmation
  - Existing China index `DatasetName.INDEX_DAILY_BARS` compatibility was preserved.
  - Existing accepted symbols such as `000300.CN_INDEX` and `399001.CN_INDEX` still validate and pass live smoke.

- deviations
  - None.

- risks/follow-up
  - Global benchmark history was intentionally not promoted; sampled public routes remain too inconsistent in symbol discovery and/or continuity for truthful support claims.
  - HK support is still benchmark-slice, not full HK index-family breadth.
  - Independent public-route redundancy for index daily bars remains unproven across both mainland and HK benchmark families.
