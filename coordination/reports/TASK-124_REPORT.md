# TASK-124 Report

- files changed
  - `quant/datahub/adapters/akshare.py`
  - `quant/datahub/datasets.py`
  - `quant/datahub/source_capabilities.py`
  - `quant/datahub/source_catalog.py`
  - `tests/datahub/test_akshare_fund_flow_adapter.py`
  - `tests/datahub/test_akshare_fund_flow_live.py`
  - `tests/datahub/test_source_capabilities.py`
  - `tests/datahub/test_source_catalog.py`

- implementation summary
  - Added optional `source_route` to `DatasetName.FUND_FLOW` and emitted it from `AkshareETFFundFlowAdapter` so route truth is preserved instead of collapsing under source-family-only identity.
  - Tightened fund-flow deduplication to keep route-distinct records separate by `(fund_code, trade_date, source_route, source)`.
  - Kept bounded request behavior unchanged: `FUND_FLOW` still requires explicit bounded `start_date` + `end_date` and explicit requested symbols, and still fails on partial batch success.
  - Tightened `source_capabilities` and `source_catalog` wording so `fund_flow` no longer overclaims richer per-fund public flow breadth/history beyond the proven exchange share-slice routes.

- ETF/fund flow route investigation result
  - Kept implemented/proven routes: `fund_etf_scale_sse` and `fund_scale_daily_szse`.
  - Investigated but did not wire as `FUND_FLOW` proof:
    - `fund_scale_change_em`: live call succeeded, but only returns market-wide aggregate rows such as `截止日期` / `期间申购` / `期间赎回` / `期末总份额`; no per-fund symbols.
    - `fund_purchase_em`: live call succeeded, but only returns fund subscription/redemption status metadata; no dated per-fund flow history.
    - `fund_etf_scale_szse`: latest-only snapshot route and in this accepted local environment raised `TypeError: Expected file path name or file-like object, got <class 'bytes'> type`.
  - Result: no stronger stable no-credential bounded per-fund dated public flow route was proven, so capability status stayed conservative and wording was tightened instead of promotion.

- supported behavior
  - symbol classes: existing accepted exchange ETF/fund codes only; explicit `.ETF_CN` or bare `5*` / `1*` codes normalize as before. Unsupported stock/HK/index/malformed inputs still fail clearly.
  - date behavior: unchanged bounded `trade_date` window only; no silent full-table fetch.
  - metric identity: still source-backed only; `shares_change` remains the guaranteed proven field, with optional `net_inflow`, `subscription_amount`, and `redemption_amount` only when the source actually emits them.
  - source-route truth: `FUND_FLOW` records now carry `source_route` (`fund_etf_scale_sse` or `fund_scale_daily_szse` in current proof).
  - deduplication: exact same-route duplicates still merge; route-distinct rows no longer collapse together.

- tests run
  - `python3 -m unittest tests.datahub.test_datasets` -> PASS (`Ran 48 tests`)
  - `python3 -m unittest tests.datahub.test_source_capabilities` -> PASS (`Ran 43 tests`)
  - `python3 -m unittest tests.datahub.test_source_catalog` -> PASS (`Ran 9 tests`)
  - `python3 -m unittest tests.datahub.test_akshare_fund_flow_adapter` -> PASS (`Ran 18 tests`)
  - `python3 -m unittest tests.datahub.test_akshare_fund_scale_share_adapter` -> PASS (`Ran 8 tests`)
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_fund_flow_live` -> PASS default skip (`OK (skipped=1)`)
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_fund_flow_live` -> PASS (`Ran 1 test in 1.463s`)

- default network behavior
  - Default tests remain offline-safe.
  - Live network access is still gated behind `QUANT_SYSTEM_LIVE_TESTS=1`.
  - No new default live path or unbounded snapshot fetch was introduced.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence
  - PASS
  - Evidence: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_fund_flow_live`
  - Verified live expectations:
    - bounded request for `510300.ETF_CN` and `159915.ETF_CN`
    - returned records stayed within `2024-01-04` to `2024-01-05`
    - records validated under `DatasetName.FUND_FLOW`
    - first record carried explicit `source_route`

- capability truth changed?
  - `fund_flow` status: unchanged at `partial`
  - truth wording: tightened to explicitly state that current proof is bounded exchange share-slice data only, and that investigated broader public routes are aggregate-only, status-only, or currently call-incompatible/latest-only

- TASK-123 compatibility
  - Confirmed `FUND_SCALE_SHARE_SNAPSHOT` bounded-request behavior was preserved by rerunning `tests.datahub.test_akshare_fund_scale_share_adapter`.
  - No change reintroduced Sina full-table snapshot use for already-satisfied bounded ETF-only scale/share requests.
  - Existing ETF/fund dataset validation compatibility was preserved; `test_datasets` passed after the optional `FUND_FLOW.source_route` addition.

- deviations
  - None.

- risks/follow-up
  - `fund_flow` still lacks independent bounded per-fund dated public-route redundancy and broader non-exchange fund breadth.
  - If a future handoff reopens stronger flow expansion, the next practical candidate is a repository-side wrapper around a genuinely per-fund dated public route; aggregate/statustable/latest-only routes should not be promoted as `FUND_FLOW` breadth proof without contract changes.
