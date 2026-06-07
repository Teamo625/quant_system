# TASK-125 Report

- files changed
  - `quant/datahub/adapters/akshare.py`
  - `quant/datahub/source_capabilities.py`
  - `quant/datahub/source_catalog.py`
  - `tests/datahub/test_akshare_fund_premium_discount_adapter.py`
  - `tests/datahub/test_akshare_fund_premium_discount_live.py`
  - `tests/datahub/test_source_capabilities.py`
  - `tests/datahub/test_source_catalog.py`

- implementation summary
  - Preserved accepted latest-snapshot premium-discount behavior for bounded ETF requests through `fund_etf_fund_daily_em` with `fund_etf_spot_em` fallback.
  - Added request-scoped historical premium-discount backfill by combining listed historical market-price routes with NAV history:
    - ETF: `fund_etf_hist_em` primary, `fund_etf_hist_sina` fallback, NAV from `fund_etf_fund_info_em`
    - listed fund: `fund_lof_hist_em` primary, `fund_etf_hist_sina` fallback, NAV from `fund_open_fund_info_em`
  - Added explicit supported `161725.FUND_CN` history path; bare `161725` now stays rejected as ambiguous.
  - Historical rows emit composite `source_route` and `source_category="historical_market_price_nav_composite"`.

- ETF/fund premium-discount route/source-family investigation result
  - Proven direct snapshot routes: `fund_etf_fund_daily_em`, `fund_etf_spot_em`
  - Proven historical composite inputs in current environment:
    - `fund_etf_hist_sina` for `510300` / `161725`
    - `fund_etf_fund_info_em` for ETF NAV history
    - `fund_open_fund_info_em` for explicit `161725.FUND_CN` NAV history
  - Investigated limits kept conservative:
    - broader listed-fund breadth beyond explicit `161725.FUND_CN` remains unproven
    - off-exchange fund premium-discount remains unsupported
    - independent direct public premium-discount history route redundancy remains unproven

- supported behavior
  - symbol classes: existing exchange ETF codes plus explicit proven `161725.FUND_CN`; malformed / stock / HK / index / ambiguous bare listed-fund inputs fail clearly
  - date behavior: bounded `start_date` + `end_date` required; single-day latest ETF requests still use direct snapshots; wider/older bounded windows backfill historical rows per requested symbol only
  - metric identity: snapshot rows keep source-emitted `premium_discount_rate`; historical rows derive `premium_discount_rate` and `premium_discount_amount` from source-backed market price plus NAV
  - source-route truth: direct routes remain distinct; historical rows carry composite routes such as `fund_etf_hist_sina+fund_etf_fund_info_em` and `fund_etf_hist_sina+fund_open_fund_info_em`
  - deduplication: same-route duplicates still merge; route-distinct rows remain distinguishable

- tests run
  - `python3 -m unittest tests.datahub.test_source_capabilities` -> PASS
  - `python3 -m unittest tests.datahub.test_source_catalog` -> PASS
  - `python3 -m unittest tests.datahub.test_akshare_fund_premium_discount_adapter` -> PASS
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_fund_premium_discount_live` -> PASS (`OK (skipped=1)`)
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_fund_premium_discount_live` -> PASS

- default network behavior
  - Default adapter/unit tests are offline-safe and use injected fixtures only.
  - Live network access remains gated behind `QUANT_SYSTEM_LIVE_TESTS=1`.
  - No default unbounded market-wide fetch path was introduced.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence
  - PASS
  - Command: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_fund_premium_discount_live`
  - Evidence from bounded request `2024-01-04..2024-01-10` for `510300.ETF_CN` + `161725.FUND_CN`:
    - `record_count=10`
    - symbols returned: `161725.FUND_CN`, `510300.ETF_CN`
    - sample historical rows:
      - `161725.FUND_CN 2024-01-04 fund_etf_hist_sina+fund_open_fund_info_em premium_discount_rate=0.122782`
      - `510300.ETF_CN 2024-01-04 fund_etf_hist_sina+fund_etf_fund_info_em premium_discount_rate=-0.058565`

- capability truth changed?
  - `fund_premium_discount` status remains `partial`
  - wording now reflects proven latest snapshots plus request-scoped historical listed ETF / explicit `161725.FUND_CN` composite continuity, without promotion

- dataset compatibility
  - `DatasetName.FUND_PREMIUM_DISCOUNT` schema compatibility preserved
  - existing direct snapshot route fields remain intact; new historical rows also validate under the same contract

- deviations
  - None

- risks/follow-up
  - Broader listed-fund premium-discount breadth beyond explicit `161725.FUND_CN` still needs proof before expansion.
  - Off-exchange fund premium-discount and independent direct public history-route redundancy remain unresolved.
  - Historical price fallback currently depends on `fund_etf_hist_sina` when Eastmoney history routes are unavailable; future hardening can seek a stronger second dated direct route.
