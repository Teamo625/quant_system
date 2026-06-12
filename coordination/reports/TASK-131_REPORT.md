# TASK-131 Report

## files changed
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_a_share_instrument_status_history_adapter.py`
- `tests/datahub/test_akshare_a_share_instrument_status_history_live.py`
- `tests/datahub/test_akshare_a_share_corporate_actions_adapter.py`
- `tests/datahub/test_akshare_a_share_corporate_actions_live.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`
- `coordination/reports/TASK-131_REPORT.md`

## implementation summary
- Selected readiness batch: `a_share__datahub_hardening__a_share__batch_01`
- Included follow-up ids:
  - `a_share__a_share_capability_readiness__a_share_listing_delisting_st_status`
  - `a_share__a_share_capability_readiness__a_share_suspension_resumption`
  - `a_share__a_share_capability_readiness__a_share_minute_bars`
  - `a_share__a_share_capability_readiness__a_share_adjustment_factors`
  - `a_share__a_share_capability_readiness__a_share_corporate_actions`
  - `a_share__a_share_capability_readiness__a_share_valuation_history`
- Hardened `AkshareAShareInstrumentStatusHistoryAdapter` so caller `start_date` / `end_date` now filter normalized rows deterministically by `effective_start_date` instead of being ignored.
- Hardened A-share corporate-actions taxonomy so explicit zero-distribution source rows with no-distribution plan text emit `action_family=dividend_no_distribution` instead of being mislabeled as `dividend_distribution`.
- Tightened `source_capabilities` and `source_catalog` wording to record the cluster’s current public-route truth and limits without promoting any capability to `covered`.

## route investigation result by included capability
- `a_share_listing_delisting_st_status`:
  - `stock_info_sh_delist(symbol="全部")`: live probe returned `152` rows with `公司代码/上市日期/暂停上市日期`; still no explicit SH terminal delist date.
  - `stock_info_sz_delist(symbol="暂停上市公司")`: live probe returned `0` rows; no broader SZ pause continuity proof.
  - `stock_info_sz_delist(symbol="终止上市公司")`: live probe returned `204` rows with dated terminal delists.
  - `stock_info_sz_change_name(symbol="简称变更")`: live probe returned `7402` rows; remains the only validated dated SZ ST/*ST delta route.
  - `stock_zh_a_st_em` / `stock_zh_a_stop_em`: still current-only snapshots, not dated continuity evidence; no new integration.
- `a_share_suspension_resumption`:
  - `stock_tfp_em`: still a one-trade-date bounded Eastmoney route.
  - `news_trade_notify_suspend_baidu`: live probe on `2026-06-02` returned `5` rows with `复牌时间`; still useful only as same-day supplemental exact-resumption evidence.
  - No stable multi-day public route was proven; capability truth kept conservative.
- `a_share_minute_bars`:
  - `stock_zh_a_hist_min_em`: direct live probe hit `ProxyError` against Eastmoney in this environment.
  - Existing adapter truth remains correct: bounded AKShare Eastmoney primary, direct Eastmoney fallback, recent-only `stock_zh_a_minute` fallback, plus BaoStock `5/15/30/60` minute history.
  - No new broader public `1` minute continuity route was proven.
- `a_share_adjustment_factors`:
  - `stock_zh_a_daily(symbol='sz000001', adjust='qfq-factor')`: live probe returned `31` factor rows.
  - No second validated no-credential A-share factor-history route was identified; current `stock_zh_a_daily` / Sina-backed change-point truth remains conservative.
- `a_share_corporate_actions`:
  - Existing route family remains `stock_dividend_cninfo`, `stock_allotment_cninfo`, and Sina detail fallback `stock_history_dividend_detail(indicator=分红|配股)`.
  - New behavior is source-truth only: when explicit source text says no distribution and all distribution ratios are zero, records now emit `action_family=dividend_no_distribution`.
  - Quick live probes on `600000/000001/600584/600030` found no no-distribution rows in those samples; capability remains partial.
- `a_share_valuation_history`:
  - `stock_zh_valuation_baidu(period='近三年')`: live probe returned `1097` rows.
  - `stock_value_em(symbol='000001')`: live probe returned `2046` dated rows.
  - Current Baidu + Eastmoney overlap truth remains valid; no stronger pre-2018 public redundancy was proven.

## supported classes / window / provenance / dedup truth
- Instrument-status history still supports caller-provided A-share `SH/SZ/BJ` stock symbols only. Date-window behavior is now deterministic: normalized records are filtered by `effective_start_date`; no hidden route-side window assumption remains.
- Suspension/resumption remains bounded to one trade date per request, with Eastmoney primary facts and Baidu supplemental exact resumption dates; existing overlap dedup behavior is unchanged.
- Minute-bars truth remains unchanged: A-share stock symbols only, bounded caller windows, route-distinct AKShare/Eastmoney/BaoStock behavior preserved, default tests offline-safe.
- Adjustment-factors truth remains unchanged: caller-provided bounded A-share symbols and dates, `qfq/hfq` basis kept route-distinct, no per-trade-date overclaim added.
- Corporate-actions remain single-symbol bounded requests. Top-level `action_family` / `source_route` and nested value provenance remain source-backed; duplicate identity behavior is unchanged.
- Valuation-history truth remains unchanged: caller-provided bounded A-share symbols, Baidu dated history plus Eastmoney overlap/current enrichments, route-distinct rows still visible.

## capability truth change
- No capability status was promoted.
- `a_share_corporate_actions` remains `partial`, but its public-source truth now explicitly includes source-backed `dividend_no_distribution`.
- `a_share_listing_delisting_st_status`, `a_share_suspension_resumption`, `a_share_minute_bars`, `a_share_adjustment_factors`, and `a_share_valuation_history` remain conservative and unpromoted.

## tests run
- `python3 -m unittest tests.datahub.test_source_capabilities` -> PASS (`Ran 46 tests`)
- `python3 -m unittest tests.datahub.test_source_catalog` -> PASS (`Ran 10 tests`)
- `python3 -m unittest tests.datahub.test_akshare_a_share_instrument_status_history_adapter` -> PASS (`Ran 10 tests`)
- `python3 -m unittest tests.datahub.test_akshare_a_share_suspension_resumption_adapter` -> PASS (`Ran 16 tests`)
- `python3 -m unittest tests.datahub.test_akshare_a_share_minute_bars_adapter` -> PASS (`Ran 24 tests`)
- `python3 -m unittest tests.datahub.test_baostock_a_share_minute_bars_adapter` -> PASS (`Ran 9 tests`)
- `python3 -m unittest tests.datahub.test_akshare_a_share_adjustment_factors_adapter` -> PASS (`Ran 5 tests`)
- `python3 -m unittest tests.datahub.test_akshare_a_share_corporate_actions_adapter` -> PASS (`Ran 24 tests`)
- `python3 -m unittest tests.datahub.test_akshare_a_share_valuation_snapshot_adapter` -> PASS (`Ran 33 tests`)
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_a_share_instrument_status_history_live` -> PASS (`OK`, `skipped=1`)
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_a_share_suspension_resumption_live` -> PASS (`OK`, `skipped=1`)
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_a_share_minute_bars_live` -> PASS (`OK`, `skipped=1`)
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_baostock_a_share_minute_bars_live` -> PASS (`OK`, `skipped=1`)
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_a_share_adjustment_factors_live` -> PASS (`OK`, `skipped=1`)
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_a_share_corporate_actions_live` -> PASS (`OK`, `skipped=1`)
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_a_share_valuation_snapshot_live` -> PASS (`OK`, `skipped=1`)
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_a_share_instrument_status_history_live` -> PASS (`Ran 4 tests in 10.339s`)
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_a_share_corporate_actions_live` -> PASS (`Ran 3 tests in 1.055s`)

## default network behavior
- Default adapter/unit tests remained offline-only.
- All live test files still require explicit `QUANT_SYSTEM_LIVE_TESTS=1`; verified with `env -u QUANT_SYSTEM_LIVE_TESTS ...` where each live smoke skipped by default.

## live-enabled PASS/SKIP/FAIL result and root-cause evidence
- Instrument-status live result: PASS.
  - Evidence: gated live smoke passed and the new bounded request path returned only records whose `effective_start_date == today`.
- Corporate-actions live result: PASS.
  - Evidence: gated live smoke passed, returned schema-valid records, and still included CNInfo rights-issue route evidence.
- Other included real-source capabilities in this handoff were investigation-only; no adapter-path behavior changed, so their accepted prior live truth remains unchanged.

## deviations
- No forbidden files were modified.
- No paid/private source, credential, or downstream module work was added.

## risks / follow-up
- Instrument-status filtering now honors requested windows by `effective_start_date`, but this remains event/history filtering rather than full interval reconstruction; explicit SH terminal delist dates and full dated ST/*ST continuity still need a stronger public route.
- A-share no-distribution taxonomy depends on explicit source text plus zero ratios; current live samples did not surface such rows, so broader live proof for that family remains future work.
- Eastmoney minute-bar availability is still environment-sensitive in this shell (`ProxyError` on direct probe); the existing conservative minute-bar truth should remain unpromoted.
