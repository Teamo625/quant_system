# TASK-127 Report

- files changed
  - `quant/datahub/adapters/akshare.py`
  - `quant/datahub/source_capabilities.py`
  - `quant/datahub/source_catalog.py`
  - `tests/datahub/test_akshare_index_adapter.py`
  - `tests/datahub/test_akshare_index_live.py`
  - `tests/datahub/test_akshare_index_constituents_adapter.py`
  - `tests/datahub/test_akshare_index_constituents_live.py`
  - `tests/datahub/test_source_capabilities.py`
  - `tests/datahub/test_source_catalog.py`

- implementation summary
  - Hardened `AkshareIndexDailyBarAdapter` with explicit key global benchmark support under `.GLOBAL_INDEX` using bounded local filtering over `index_global_hist_sina`; kept mainland and HK benchmark behavior from TASK-126 intact.
  - Broadened `AkshareIndexConstituentsAdapter` to accept validated China benchmark codes `000688` and `399005`, preserving whole-batch failure, dated membership truth, and duplicate-conflict hard failures.
  - Tightened `source_capabilities` and `source_catalog` wording so China/HK/global benchmark proof, global-route limits, and rebalance-calendar gaps are explicit without promoting any index capability.

- selected readiness batch id and included follow-up ids
  - batch id: `index__datahub_hardening__index__batch_01`
  - follow-up ids:
    - `index__index_capability_readiness__index_daily_bars`
    - `index__index_capability_readiness__index_constituent_history`
    - `index__index_capability_readiness__index_rebalance_effective_dates`
    - `index__index_capability_readiness__index_china_hk_global_benchmarks`

- index route/source-family investigation result
  - Promoted no new source family; stayed inside `akshare_cn_hk_public_family`.
  - Daily bars:
    - Mainland kept `stock_zh_index_daily_tx`, `stock_zh_index_daily`, `stock_zh_index_daily_em`, `index_zh_a_hist`.
    - HK kept `stock_hk_index_daily_sina` as the proven route.
    - Added curated key global slice through `index_global_hist_sina`.
  - Investigated but did not promote:
    - `index_global_spot_em` and `index_global_hist_em` reproduced `ConnectionError(RemoteDisconnected(...))` locally.
    - `index_global_hist_sina` proved stable for the accepted slice but only returns a recent `1000`-row window and does not cover stable major US benchmark history in the accepted route family.
  - Constituents/rebalance:
    - `000688` proved stable on `index_stock_cons_weight_csindex`/`index_stock_cons_csindex`.
    - `399005` public fallback proved usable through `index_stock_cons`; local route probing saw `index_stock_cons_weight_csindex` / `index_stock_cons_csindex` raise `ValueError: Excel file format cannot be determined`.

- supported index symbol classes, benchmark families, market suffixes, date behavior, source-route truth, and deduplication behavior
  - Daily-bar symbol classes:
    - Mainland `.CN_INDEX`: `000001`, `000300`, `000688`, `000852`, `000905`, `000906`, `399001`, `399005`, `399006` plus validated `sh`/`sz` native forms.
    - HK `.HK_INDEX`: `HSI`, `HSCEI`, `HSCCI`, `HSTECH`.
    - Global `.GLOBAL_INDEX`: `UKX`, `DAX`, `SX5E`, `GSPTSE`, `TWJQ`, `NKY`, `KOSPI`, `AS51`.
  - Constituents slice now supports caller-provided China benchmarks: `000001`, `000300`, `000688`, `000852`, `000905`, `000906`, `399001`, `399005`, `399006`.
  - Date behavior remains deterministic and bounded by caller `start_date` / `end_date`; routes without native window params are locally filtered and hard-fail if no usable bounded rows remain.
  - Daily-bar records keep explicit `source_route`; constituent records preserve source-backed `in_date`, optional `out_date`, and optional `weight` where exposed.
  - Dedupe remains conservative:
    - daily bars by `(index_code, trade_date, source, source_route)`
    - constituents by `(index_code, symbol, in_date, source)`
    - conflicting duplicates still fail hard.

- constituent/effective-date/rebalance source truth and known limitations
  - `INDEX_CONSTITUENTS` continues to carry only source-backed dated membership facts; fallback snapshot rows still use the existing sentinel when a route exposes no dated field.
  - The broadened China slice now preserves effective-date-like fields, optional `out_date`, and optional `weight` when available, but there is still no explicit index-level rebalance calendar contract or stable HK/global constituent history path.
  - No `source_route` field was added to `INDEX_CONSTITUENTS`; this task stayed schema-compatible and conservative.

- tests run
  - `python3 -m unittest tests.datahub.test_source_capabilities` -> PASS
  - `python3 -m unittest tests.datahub.test_source_catalog` -> PASS
  - `python3 -m unittest tests.datahub.test_akshare_index_adapter` -> PASS
  - `python3 -m unittest tests.datahub.test_akshare_index_constituents_adapter` -> PASS
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_index_live` -> PASS (`skipped=3`)
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_index_constituents_live` -> PASS (`skipped=2`)
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_index_live` -> PASS
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_index_constituents_live` -> PASS

- default network behavior
  - Default/unit tests remain offline-safe.
  - Live source tests remain explicitly gated behind `QUANT_SYSTEM_LIVE_TESTS=1`.
  - No `symbols=None` or unbounded full-market index fetch path was added.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence for real-source tasks
  - Daily-bar live result: PASS
  - Evidence:
    - bounded readback for `000300.CN_INDEX`, `HSI.HK_INDEX`, `UKX.GLOBAL_INDEX`, `NKY.GLOBAL_INDEX` over `2024-01-02..2024-01-10` returned `25` records
    - `000300.CN_INDEX`: `7` rows via `stock_zh_index_daily_tx`
    - `HSI.HK_INDEX`: `7` rows via `stock_hk_index_daily_sina`
    - `UKX.GLOBAL_INDEX`: `7` rows via `index_global_hist_sina`
    - `NKY.GLOBAL_INDEX`: `4` rows via `index_global_hist_sina`
  - Constituent/rebalance live result: PASS
  - Evidence:
    - bounded readback for `000300.CN_INDEX`, `000688.CN_INDEX`, `399005.CN_INDEX` returned `450` records
    - `000300.CN_INDEX`: `300` rows, all weighted, dated `2026-05-29`
    - `000688.CN_INDEX`: `50` rows, all weighted, dated `2026-05-29`
    - `399005.CN_INDEX`: `100` rows, `in_date` range `2006-01-24 .. 2025-12-15`, no fallback `1900-01-01` rows observed

- whether any of the four index capability truths changed
  - No status promotion.
  - `index_daily_bars`, `index_constituent_history`, `index_rebalance_effective_dates`, and `index_china_hk_global_benchmarks` all remain `partial`.
  - Truth changed:
    - `index_daily_bars` now explicitly includes a curated no-credential global slice and its `1000`-row / no-stable-US limitations.
    - `index_constituent_history` now explicitly reflects the broader China benchmark slice including `000688` and `399005`.
    - `index_rebalance_effective_dates` now explicitly documents preserved effective/in/out/weight truth and the missing index-level rebalance calendar.
    - `index_china_hk_global_benchmarks` now explicitly documents the accepted China/HK/global slice and its remaining global gaps.

- confirmation
  - `index_weight_history` remained out of scope and blocked/planned; no credential, token, or Tushare-path behavior was changed.

- deviations
  - None.

- risks/follow-up
  - The accepted global route is still a curated slice, not exhaustive global coverage; stable major US benchmark history remains unproven.
  - `index_global_hist_sina` is limited to a recent `1000`-row window, so long-history global benchmark continuity is still incomplete.
  - HK/global constituent history and an explicit rebalance-calendar dataset remain unresolved follow-up work.
