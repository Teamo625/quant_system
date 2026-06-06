# TASK-123 Report

- files changed
  - `quant/datahub/adapters/akshare.py`
  - `quant/datahub/source_capabilities.py`
  - `quant/datahub/source_catalog.py`
  - `tests/datahub/test_akshare_fund_scale_share_adapter.py`
  - `tests/datahub/test_source_capabilities.py`
  - `tests/datahub/test_source_catalog.py`
  - `coordination/reports/TASK-123_REPORT.md`

- Review findings addressed
  - Fixed the blocking behavior: bounded ETF-only `FUND_SCALE_SHARE_SNAPSHOT` requests no longer call Sina full-table snapshot routes when exchange history already covers all requested symbols.
  - Removed the unrelated duplicate scale/share dedupe helpers that had been inserted into `AkshareETFFundNavSnapshotAdapter`.

- implementation summary
  - `AkshareETFFundFlowAdapter` now fetches exchange ETF history first, then computes the still-uncovered requested symbols before considering any Sina snapshot fallback.
  - Snapshot normalization now only targets the uncovered requested symbols, so mixed ETF + `FUND_CN` requests can use fund snapshots without adding redundant ETF snapshot rows.
  - Deterministic scale/share dedupe and accepted `FUND_FLOW` / `FUND_NAV_SNAPSHOT` behavior were preserved.

- final Sina snapshot route disposition
  - `fund_scale_open_sina` / `fund_scale_close_sina` remain enabled only as request-scoped fallback for bounded requests that still have uncovered target symbols.
  - They are disabled by default for already-satisfied bounded ETF-only requests.

- bounded request confirmation
  - Added offline regression proving a bounded ETF-only request returns exchange-history scale/share data without invoking snapshot routes at all.
  - Mixed requests still allow snapshot use for uncovered `FUND_CN` symbols, while non-target snapshot rows continue to be ignored.

- duplicate NAV adapter helpers
  - Removed from `AkshareETFFundNavSnapshotAdapter`.

- supported behavior after rework
  - Supported symbols: exchange ETFs as bare `5*` / `159*` or explicit `.ETF_CN`; public funds as explicit `.FUND_CN`; proven non-ETF bare `1*` / `5*` codes normalize to `.FUND_CN`.
  - Rejected clearly: bare ambiguous `0*`, market-suffix mismatches, stock-like, HK-like, index-like, malformed codes.
  - Date behavior: exchange history uses bounded `trade_date`; snapshot fallback emits `snapshot_update_date` only when the source update date falls inside the requested window.
  - Metric identity: `shares_outstanding` and source-shaped `total_raised_scale` remain distinct by `metric_code`, `source_route`, and `observation_type`.
  - Deduplication key remains `(fund_code, observation_date, source, source_route, metric_code, observation_type)`.

- tests run
  - `python3 -m unittest tests.datahub.test_datasets` -> PASS (`Ran 48 tests`)
  - `python3 -m unittest tests.datahub.test_source_capabilities` -> PASS (`Ran 43 tests`)
  - `python3 -m unittest tests.datahub.test_source_catalog` -> PASS (`Ran 9 tests`)
  - `python3 -m unittest tests.datahub.test_akshare_fund_flow_adapter tests.datahub.test_akshare_fund_nav_adapter tests.datahub.test_akshare_fund_scale_share_adapter` -> PASS (`Ran 55 tests`)
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_fund_flow_live tests.datahub.test_akshare_fund_scale_share_live` -> PASS default skip (`Ran 3 tests`, `skipped=3`)
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_fund_scale_share_live` -> PASS (`Ran 2 tests in 26.802s`)
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_fund_flow_live` -> PASS (`Ran 1 test in 1.667s`)

- default network behavior
  - Default tests remain offline-safe.
  - Snapshot fallback is not used unless the bounded request still has uncovered requested symbols.
  - Live tests remain explicitly gated by `QUANT_SYSTEM_LIVE_TESTS=1`.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence
  - Result: PASS
  - `test_live_akshare_fund_scale_share_historical_etf_smoke` passed for bounded ETF history with `510300.ETF_CN` and `159915.ETF_CN`.
  - `test_live_akshare_fund_scale_share_fund_snapshot_smoke` passed for bounded `FUND_CN` snapshot fallback with `000001.FUND_CN` and `161725.FUND_CN`.
  - `test_live_akshare_fund_flow_smoke` also passed, confirming accepted `FUND_FLOW` behavior remained intact after the rework.

- capability truth and compatibility
  - `fund_scale_and_share` remains `partial`; no promotion.
  - `source_capabilities` / `source_catalog` wording now states that Sina snapshot routes are request-scoped fallback rather than default bounded ETF coverage.
  - No schema change was made; `FUND_FLOW`, `FUND_NAV_SNAPSHOT`, and `FUND_SCALE_SHARE_SNAPSHOT` compatibility were preserved.

- deviations
  - None.

- risks/follow-up
  - Sina snapshot routes are still source-side full-table latest snapshots; repository behavior now bounds their use, but the upstream API itself remains non-parameterized.
  - Structured/other fund families, stronger history continuity beyond ETF exchange share history, clearer raised-scale unit semantics, and independent public-route redundancy remain incomplete.
