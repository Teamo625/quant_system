# TASK-123 Report

- files changed
  - `quant/datahub/adapters/akshare.py`
  - `quant/datahub/source_capabilities.py`
  - `quant/datahub/source_catalog.py`
  - `tests/datahub/test_source_capabilities.py`
  - `tests/datahub/test_source_catalog.py`
  - `tests/datahub/test_akshare_fund_scale_share_adapter.py`
  - `tests/datahub/test_akshare_fund_scale_share_live.py`

- implementation summary
  - Extended `AkshareETFFundFlowAdapter` to emit `DatasetName.FUND_SCALE_SHARE_SNAPSHOT` while preserving accepted `FUND_FLOW` behavior.
  - Added dedicated normalized scale/share facts from:
    - bounded ETF exchange share history: `fund_etf_scale_sse`, `fund_scale_daily_szse`
    - latest dated per-fund snapshot routes: `fund_scale_open_sina`, `fund_scale_close_sina`
  - Preserved route/source truth with `source_route`, `metric_code`, `observation_type`, deterministic sort/dedupe, and clear invalid-symbol / partial-batch failure behavior.
  - Kept `fund_scale_and_share` conservative at `partial`; updated capability/catalog wording from “overlapping proof only” to “dedicated adapter-backed proof exists, but still incomplete”.

- scale/share source-route investigation result
  - Wired:
    - `fund_etf_scale_sse` -> dated ETF `shares_outstanding`
    - `fund_scale_daily_szse` -> dated ETF `shares_outstanding`
    - `fund_scale_open_sina` -> latest dated `shares_outstanding` and `total_raised_scale`
    - `fund_scale_close_sina` -> latest dated `shares_outstanding` and `total_raised_scale`
  - Investigated but not wired:
    - `fund_scale_structured_sina` sample rows had `更新日期=NaT` and `最近总份额=nan`, so it cannot truthfully satisfy required dated share facts yet.
  - Live rework root cause fixed:
    - Sina full-table snapshots include malformed non-target codes such as `37001B`; initial normalization failed before request-symbol filtering.
    - Adapter now skips malformed unrequested snapshot rows and still fails clearly on requested-symbol defects.

- supported symbol classes, date behavior, metrics, deduplication
  - Supported:
    - exchange ETF families as bare `5*` / `159*` or explicit `.ETF_CN`
    - public fund families as explicit `.FUND_CN`
    - non-ETF `1*` / `5*` bare codes normalize to `.FUND_CN`
  - Rejected clearly:
    - bare ambiguous `0*` codes
    - explicit market mismatches like `510300.FUND_CN` or `161725.ETF_CN`
    - stock-like, HK-like, index-like, malformed codes
  - Observation semantics:
    - `trade_date` for exchange history
    - `snapshot_update_date` for Sina latest snapshot routes
  - Metric semantics:
    - `shares_outstanding` with `metric_unit="share"`
    - `total_raised_scale` left source-shaped; no extra unit inference added
  - Deduplication key:
    - `(fund_code, observation_date, source, source_route, metric_code, observation_type)`
  - Redundancy behavior:
    - if an ETF exchange route is unavailable but snapshot routes still cover all requested symbols inside the bounded window, the scale/share request can still succeed

- tests run
  - `python3 -m unittest tests.datahub.test_datasets` -> PASS (`Ran 48 tests`)
  - `python3 -m unittest tests.datahub.test_source_capabilities` -> PASS (`Ran 43 tests`)
  - `python3 -m unittest tests.datahub.test_source_catalog` -> PASS (`Ran 9 tests`)
  - `python3 -m unittest tests.datahub.test_akshare_fund_flow_adapter tests.datahub.test_akshare_fund_nav_adapter tests.datahub.test_akshare_fund_scale_share_adapter` -> PASS (`Ran 53 tests`)
  - `python3 -m unittest tests.datahub.test_datasets tests.datahub.test_source_capabilities tests.datahub.test_source_catalog tests.datahub.test_akshare_fund_flow_adapter tests.datahub.test_akshare_fund_nav_adapter tests.datahub.test_akshare_fund_scale_share_adapter` -> PASS (`Ran 153 tests`)
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_fund_flow_live tests.datahub.test_akshare_fund_scale_share_live` -> PASS default skip (`Ran 3 tests`, `skipped=3`)
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_fund_flow_live` -> PASS (`Ran 1 test in 2.513s`)
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_fund_scale_share_live` -> PASS (`Ran 2 tests in 48.803s`)

- default network behavior
  - Default tests remain offline-safe.
  - New live smokes are explicitly gated by `QUANT_SYSTEM_LIVE_TESTS=1`.
  - No hidden default live-network path was added.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence
  - Result: PASS
  - Live ETF history proof:
    - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_fund_scale_share_live`
    - `test_live_akshare_fund_scale_share_historical_etf_smoke` passed for `510300.ETF_CN` + `159915.ETF_CN`, bounded `2024-01-04..2024-01-05`
  - Live public-fund snapshot proof:
    - same command
    - `test_live_akshare_fund_scale_share_fund_snapshot_smoke` passed for `000001.FUND_CN` + `161725.FUND_CN`, bounded recent 30-day window
  - Additional evidence:
    - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_fund_flow_live` still PASS after the adapter extension
  - Diagnosed/fixed live defect before final PASS:
    - initial scale/share live run failed with `ValueError: Invalid fund_code value: '37001B'`
    - cause: malformed non-target Sina snapshot row reached normalization before symbol filtering
    - fix: skip malformed unrequested snapshot codes; rerun passed

- capability truth changed
  - `fund_scale_and_share` remains `partial`
  - changed truth: capability/catalog wording now reflects dedicated adapter-backed AKShare exchange-history plus latest-snapshot scale/share proof instead of only overlapping NAV/profile/exchange evidence

- compatibility confirmation
  - Existing `FUND_FLOW` behavior was preserved; live regression PASS confirmed.
  - No `quant/datahub/datasets.py` schema change was required.

- deviations
  - No scope deviations.
  - Added direct local route probes for `fund_scale_structured_sina` / `fund_scale_close_sina` only to document public-route limitations in this report.

- risks/follow-up
  - `fund_scale_and_share` must not be promoted beyond `partial`.
  - `fund_scale_structured_sina` remains unsuitable for dated share facts because sampled rows had missing update dates and missing latest shares.
  - Sina snapshot routes are full-table latest snapshots, not source-side caller-filtered symbol/date endpoints; malformed extra codes can appear.
  - `total_raised_scale` unit semantics remain source-shaped and should not be overinterpreted without stronger public documentation or second-route confirmation.
  - Independent public-route redundancy for scale/share remains incomplete.
