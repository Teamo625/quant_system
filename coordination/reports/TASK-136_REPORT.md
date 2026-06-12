# TASK-136 Report

- files changed
  - `quant/datahub/adapters/akshare.py`
  - `quant/datahub/source_capabilities.py`
  - `quant/datahub/source_catalog.py`
  - `tests/datahub/test_akshare_etf_daily_bar_adapter.py`
  - `tests/datahub/test_akshare_etf_daily_bar_live.py`
  - `tests/datahub/test_akshare_fund_premium_discount_adapter.py`
  - `tests/datahub/test_akshare_fund_premium_discount_live.py`
  - `tests/datahub/test_source_capabilities.py`
  - `tests/datahub/test_source_catalog.py`

- selected readiness batch id and included follow-up ids
  - batch id: `etf_fund__datahub_hardening__etf_fund__batch_01`
  - follow-up ids:
    - `etf_fund__etf_fund_capability_readiness__fund_daily_bars`
    - `etf_fund__etf_fund_capability_readiness__fund_nav`
    - `etf_fund__etf_fund_capability_readiness__fund_holdings_composition`
    - `etf_fund__etf_fund_capability_readiness__fund_scale_and_share`
    - `etf_fund__etf_fund_capability_readiness__fund_flow`
    - `etf_fund__etf_fund_capability_readiness__fund_premium_discount`

- implementation summary by included capability
  - `fund_daily_bars`: broadened listed-fund/LOF acceptance from a single hard-coded `161725.FUND_CN` gate to listed-fund market-price codes that the live routes can actually prove, while preserving off-exchange rejection and per-request hard failure on empty/no-row results. Tightened the route-unavailable classifier so route-name-bearing repository defects no longer downgrade to environment `SKIP`.
  - `fund_nav`: no adapter truth change; rechecked accepted `fund_etf_fund_info_em` + `fund_open_fund_info_em` behavior and left capability/catalog wording unchanged.
  - `fund_holdings_composition`: no adapter truth change; rechecked accepted `fund_portfolio_hold_em` boundary and left capability/catalog wording unchanged.
  - `fund_scale_and_share`: no adapter truth change; rechecked accepted bounded ETF history plus request-scoped Sina snapshot fallback boundary and left capability/catalog wording unchanged.
  - `fund_flow`: no adapter truth change; rechecked accepted exchange share-slice route boundary and left capability/catalog wording unchanged.
  - `fund_premium_discount`: broadened listed-fund/LOF support from single-code wording to multi-code historical listed-price + open-fund NAV composite coverage, aligned symbol normalization with actual listed ETF vs listed-fund code families, and kept off-exchange funds unsupported.

- ETF/fund route/source-family investigation result
  - direct route probes in this environment showed `fund_lof_hist_em`, `fund_etf_hist_sina`, and `fund_open_fund_info_em` all returned usable data for listed-fund/LOF codes `160706`, `161725`, `501018`; adapter probes also passed for `160706.FUND_CN` and `501018.FUND_CN`.
  - `180012` remained unproven here: `fund_lof_hist_em` raised `KeyError('180012')`, `fund_etf_hist_sina` returned `rows=0`, and the adapter now fails clearly instead of over-claiming support.
  - unchanged investigations remained conservative:
    - `fund_nav`: broader open-fund/listed-fund history path already accepted; no new stronger independent route was found.
    - `fund_holdings_composition`: `fund_portfolio_hold_em` still returns empty for some funds (`501018`) and non-A-share constituents for others (`162411`), so no promotion.
    - `fund_scale_and_share` / `fund_flow`: no stronger bounded per-fund dated public route beyond accepted exchange share slices plus request-scoped snapshot fallback.

- supported behavior after rework
  - `fund_daily_bars` symbol families:
    - exchange ETFs: existing accepted listed ETF families via `.ETF_CN` or bare ETF codes.
    - listed funds/LOFs: non-ETF listed market-price codes starting with `1` or `5` now normalize to `.FUND_CN`; explicit `.FUND_CN` works; off-exchange `0*` funds remain rejected.
  - `fund_premium_discount` symbol families:
    - exchange ETFs: existing accepted listed ETF families preserved.
    - listed funds/LOFs: non-ETF listed market-price codes starting with `1` or `5` now normalize to `.FUND_CN`; explicit `.ETF_CN` mismatch fails clearly; off-exchange `0*` funds remain unsupported.
  - date/report-period behavior:
    - `fund_daily_bars`: still caller-bounded `start_date` / `end_date`; fallback rows remain locally filtered to the requested window.
    - `fund_premium_discount`: still bounded `start_date` / `end_date`; ETF snapshot latest rows fill same-day windows, listed-fund history uses `fund_lof_hist_em` or `fund_etf_hist_sina` plus `fund_open_fund_info_em`.
  - source-route truth and dedup:
    - `fund_daily_bars`: dataset still has no first-class `source_route`; record-level truth unchanged.
    - `fund_premium_discount`: route-composite truth preserved in `source_route`; dedup remains by `(fund_code, trade_date, source, source_route)`.

- whether any of the six ETF/fund capability truths changed
  - `fund_daily_bars`: status stays `partial`; wording changed from single-code truth to broader multi-code listed-fund/LOF proof with explicit remaining failures/empties.
  - `fund_premium_discount`: status stays `partial`; wording changed from single-code truth to broader multi-code listed-fund/LOF composite proof with explicit remaining failures/empties.
  - `fund_nav`, `fund_holdings_composition`, `fund_scale_and_share`, `fund_flow`: no capability-status or wording change.

- known public-source limitations and why capability truth remains conservative
  - some listed-fund codes still fail or return empty at source (`180012` reproduced here).
  - off-exchange `0*` funds still lack listed market-price / premium-discount proof.
  - holdings still mix empty payloads and non-A-share constituents on some fund classes.
  - scale/share and flow still lack stronger bounded per-fund dated public-route redundancy.
  - no capability in this batch reached practical public-source/no-paid completeness; all remain conservative.

- tests run
  - `python3 -m unittest tests.datahub.test_source_capabilities` -> PASS
  - `python3 -m unittest tests.datahub.test_source_catalog` -> PASS
  - `python3 -m unittest tests.datahub.test_akshare_etf_daily_bar_adapter` -> PASS
  - `python3 -m unittest tests.datahub.test_akshare_fund_nav_adapter` -> PASS
  - `python3 -m unittest tests.datahub.test_akshare_fund_holdings_adapter` -> PASS
  - `python3 -m unittest tests.datahub.test_akshare_fund_scale_share_adapter` -> PASS
  - `python3 -m unittest tests.datahub.test_akshare_fund_flow_adapter` -> PASS
  - `python3 -m unittest tests.datahub.test_akshare_fund_premium_discount_adapter` -> PASS
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_etf_daily_bar_live` -> PASS (`skipped=1`)
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_fund_nav_live` -> PASS (`skipped=1`)
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_fund_holdings_live` -> PASS (`skipped=1`)
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_fund_scale_share_live` -> PASS (`skipped=2`)
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_fund_flow_live` -> PASS (`skipped=1`)
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_fund_premium_discount_live` -> PASS (`skipped=1`)

- default network behavior
  - default/unit tests remain offline-safe.
  - all live tests remain explicitly gated behind `QUANT_SYSTEM_LIVE_TESTS=1`.
  - no hidden default network path or unbounded full-table default behavior was added.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence for materially changed real-source paths
  - `fund_daily_bars` -> PASS
    - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_etf_daily_bar_live` passed with `510300.ETF_CN` + newly supported `160706.FUND_CN`.
    - direct adapter probes also passed for `160706.FUND_CN` and `501018.FUND_CN` over `2024-01-02..2024-01-10` (`count=7` each); `180012.FUND_CN` failed with `KeyError('180012')`.
  - `fund_premium_discount` -> PASS
    - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_fund_premium_discount_live` passed with `510300.ETF_CN` + newly supported `160706.FUND_CN`.
    - direct adapter probes also passed for `160706.FUND_CN` and `501018.FUND_CN` over `2024-01-04..2024-01-10` with `source_route=fund_lof_hist_em+fund_open_fund_info_em`; `180012.FUND_CN` failed with `KeyError('180012')`.

- deviations
  - none.

- risks/follow-up
  - `fund_daily_bars` and `fund_premium_discount` still rely on source truth at fetch time for some listed-fund codes; wider controller follow-up should decide whether to keep runtime-probed breadth or introduce a stronger curated allow/deny layer once broader public evidence is collected.
  - if future daily-bar live reworks happen, keep the narrowed classifier behavior: route-name tokens alone must not turn repository defects into environment `SKIP`.
  - broader off-exchange fund coverage, stronger direct premium-discount redundancy, and richer fund holdings/flow/scale completeness remain open follow-up work.
