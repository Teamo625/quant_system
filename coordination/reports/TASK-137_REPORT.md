# TASK-137 Report

- files changed
  - `quant/datahub/adapters/akshare.py`
  - `quant/datahub/source_capabilities.py`
  - `quant/datahub/source_catalog.py`
  - `tests/datahub/test_akshare_index_adapter.py`
  - `tests/datahub/test_akshare_index_live.py`
  - `tests/datahub/test_source_capabilities.py`
  - `tests/datahub/test_source_catalog.py`

- selected readiness batch id and included follow-up ids
  - batch id: `index__datahub_hardening__index__batch_01`
  - follow-up ids:
    - `index__index_capability_readiness__index_daily_bars`
    - `index__index_capability_readiness__index_constituent_history`
    - `index__index_capability_readiness__index_rebalance_effective_dates`
    - `index__index_capability_readiness__index_china_hk_global_benchmarks`

- implementation summary by included capability
  - `index_daily_bars`: expanded `.GLOBAL_INDEX` support from the prior 8-code curated slice to the full 20-code no-credential `ak.index_global_name_table()` / `index_global_hist_sina` table; preserved bounded CN/HK behavior, `source_route` truth, and whole-request hard failure semantics.
  - `index_constituent_history`: no adapter-path change; strengthened capability truth to reflect currently reproduced China-slice dated membership ranges instead of leaving continuity evidence implicit.
  - `index_rebalance_effective_dates`: no adapter-path change; tightened capability truth around what is actually proven today: effective-date-like fields, optional end dates, weights, and latest CSIndex snapshot dates, but no dedicated rebalance-calendar contract.
  - `index_china_hk_global_benchmarks`: updated capability/catalog truth from “curated global slice” to the stronger verified statement that AKShare currently publishes a 20-code non-US global table while still excluding the major US benchmarks.

- index route/source-family investigation result
  - `index_global_name_table()` returned `20` public global benchmark codes in this environment; direct probes of all 20 names through `index_global_hist_sina` returned usable history, each with `1000` rows.
  - reproduced examples from the table:
    - `UKX`: `2022-06-27 .. 2026-06-11`
    - `CASE`: `2022-04-17 .. 2026-06-11`
  - the published AKShare public global table did not include S&P 500, Nasdaq Composite, or Dow Jones Industrial Average names/codes; sampled US aliases on `index_global_hist_sina` remained `KeyError`.
  - constituent probes preserved stronger China-slice history evidence:
    - `index_stock_cons("000001")`: `2229` rows, `1990-12-19 .. 2026-06-12`
    - `index_stock_cons("399001")`: `500` rows, `2003-05-26 .. 2026-05-11`

- supported behavior after rework
  - `INDEX_DAILY_BARS` symbol classes:
    - mainland: accepted `.CN_INDEX`, bare validated benchmark codes, and validated `sh` / `sz` native forms.
    - HK: accepted `.HK_INDEX` for the proven major Hang Seng slice.
    - global: accepted `.GLOBAL_INDEX` for the 20 AKShare-advertised non-US codes; bare global codes remain rejected.
  - market suffixes remain explicit: unsupported A-share stock, HK stock, ETF/fund, malformed, and unmapped index identifiers still fail clearly.
  - date behavior remains caller-bounded by `start_date` / `end_date`; wider upstream payloads are locally filtered.
  - source-route truth remains first-class on daily-bar records; dedupe remains by `(index_code, trade_date, source, source_route)`.
  - constituent/rebalance adapter behavior is unchanged: China benchmark slice only, no partial-success on invalid/empty requested symbols, and existing `INDEX_CONSTITUENTS` contract compatibility preserved.

- constituent/effective-date/rebalance source truth and known limitations
  - current public proof is still China-slice only for constituents.
  - effective-date-like `in_date`, optional `out_date`, and optional `weight` remain source-backed when exposed.
  - latest CSIndex routes expose recent constituent snapshot dates, but there is still no explicit index-level rebalance calendar dataset and no guaranteed full remove-date history.
  - HK/global constituent history remains unproven in the current public no-credential slice.

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
  - default/unit coverage remains offline-safe.
  - live index tests remain explicitly gated behind `QUANT_SYSTEM_LIVE_TESTS=1`.
  - no hidden default network path, `symbols=None` behavior, or unbounded full-market fetch path was introduced.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence for real-source tasks
  - `index_daily_bars` -> PASS
    - live suite passed for mainland, HK, and the expanded global slice.
    - direct adapter readback for newly supported `DAX.GLOBAL_INDEX` + `SENSEX.GLOBAL_INDEX` over `2024-01-02 .. 2024-01-10` returned `14` records total, `7` rows per symbol, route=`index_global_hist_sina`.
  - `index_constituent_history` / `index_rebalance_effective_dates` -> PASS
    - live suite passed for `000300.CN_INDEX`, `399001.CN_INDEX`, and `000688.CN_INDEX`.
    - no repository-side schema, normalization, signature, or partial-success defects were observed in this review window.

- whether any of the four index capability truths changed
  - no status promotion: `index_daily_bars`, `index_constituent_history`, `index_rebalance_effective_dates`, and `index_china_hk_global_benchmarks` all remain `partial`.
  - truth changed:
    - `index_daily_bars`: now states the verified 20-code AKShare-advertised non-US global table instead of the older narrower curated-slice wording.
    - `index_constituent_history`: now records reproduced dated-history evidence for the current China slice.
    - `index_rebalance_effective_dates`: now records recent CSIndex snapshot-date truth and keeps the missing rebalance-calendar boundary explicit.
    - `index_china_hk_global_benchmarks`: now explicitly records that AKShare public global coverage is non-US and excludes the major US benchmarks.

- confirmation
  - `index_weight_history` remained out of scope and blocked; no Tushare credential path, token handling, or promotion logic changed.

- deviations
  - none.

- risks/follow-up
  - the strengthened global slice is still bounded by `index_global_hist_sina`'s recent `1000`-row window; long-history global continuity remains incomplete.
  - major US benchmark history is still absent from AKShare's published public global table; a future task would need a different stable public route or an owner-approved credentialed path.
  - HK/global constituent history and a dedicated rebalance-calendar dataset remain unresolved follow-up work.
