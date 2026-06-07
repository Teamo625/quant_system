# TASK-125 Report

- files changed
  - `quant/datahub/adapters/akshare.py`
  - `tests/datahub/test_akshare_fund_premium_discount_live.py`

- classifier fix summary
  - Narrowed `AkshareETFFundPremiumDiscountAdapter._is_fund_premium_discount_route_unavailable()`.
  - Removed bare historical route/function-name tokens from environment-unavailable matching:
    - `fund_etf_hist_em`
    - `fund_lof_hist_em`
    - `fund_etf_hist_sina`
  - Genuine network/proxy/DNS/TLS/upstream/source-host evidence remains classified as environment unavailability through exception types, errno checks, and concrete host/network tokens.

- regression coverage added
  - Added live-classifier regression proving `TypeError("fund_etf_hist_em() got an unexpected keyword argument 'adjust'")` is not treated as environment unavailability.
  - Added regression proving a bare historical route-name token inside a repository-side payload/schema-style error is not treated as environment unavailability.
  - Existing network-oriented classifier tests remain and still pass.

- tests run
  - `python3 -m unittest tests.datahub.test_akshare_fund_premium_discount_adapter` -> PASS
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_fund_premium_discount_live` -> PASS (`OK (skipped=1)`)
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_fund_premium_discount_live` -> PASS (`Ran 6 tests in 14.481s`)

- default network behavior
  - Default/unit coverage remains offline-safe.
  - Live network access remains gated behind `QUANT_SYSTEM_LIVE_TESTS=1`.
  - No new default live calls or unbounded fetch paths were introduced by this rework.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence
  - PASS
  - The gated live smoke completed successfully after the classifier change.
  - The live test still exercises the bounded real-source request for `510300.ETF_CN` and `161725.FUND_CN` over `2024-01-04..2024-01-10`, and its assertions still require both supported symbols plus the explicit `fund_etf_hist_sina+fund_open_fund_info_em` historical route path when upstream data is available.

- confirmation
  - Historical route/function-name tokens alone no longer trigger environment/source-unavailability classification.
  - Route-signature and call-compatibility defects now fail rather than skip for the reviewed reproduction shape.

- deviations
  - None.

- risks/follow-up
  - This rework is intentionally classifier-only; it does not expand ETF/fund premium-discount breadth/history beyond the already accepted TASK-125 implementation.
  - If future AKShare historical routes introduce new genuine source-unavailability signatures, they should be added only with concrete host/network/upstream evidence rather than route-name-only matching.
