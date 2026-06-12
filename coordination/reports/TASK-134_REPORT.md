# TASK-134 Report

## files changed
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_hk_instrument_master_adapter.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`

## implementation summary by capability
- `hk_universe_reference`: hardened `AkshareHKInstrumentMasterAdapter` bounded current-listed flow. When `stock_hk_spot_em` succeeds but its first bounded sample has zero symbol overlap with the Sina stock page, the adapter now switches to `sina_hk_stock_spot_page1` before per-symbol profile fetch. This fixes the live defect where the primary list sample was a non-stock structured-product slice (`85081.HK`, `85082.HK`, ...), which then triggered `stock_hk_security_profile_em` `NoneType` payload failures. The bounded list path also skips obvious ETF/fund/index rows when list metadata exposes those families. Remaining blocker: no proven no-credential HK non-stock taxonomy or dated delist/inactive lifecycle route.
- `hk_daily_bars`: no adapter logic change. Capability/catalog wording and tests now state the proven boundary explicitly: `stock_hk_hist` plus `stock_hk_daily` preserves bounded-window filtering and practical continuity, but both are the same AKShare family, so independent public-source redundancy is still unproven.
- `hk_valuation_history`: no adapter logic change. Capability/catalog wording and tests now record the concrete blocker explicitly: accepted dated history still goes stale at `2022-07-13`, and the undated comparison snapshot route cannot safely satisfy the dated-history contract. Remaining blocker: current-dated continuity and independent public-source redundancy.
- `hk_financial_data`: no adapter logic change. Capability/catalog wording and tests now record that accepted live proof is still sampled-liquid-issuer proof only, even though bounded multi-symbol report-period history, source-route truth, statement-family truth, and metric-family truth are established. Remaining blocker: broader issuer breadth, non-stock support, longer continuity, and independent redundancy.
- `hk_turnover_liquidity`: no adapter logic change. Capability/catalog wording and tests now record that the proven source-backed facts remain dated `volume` and `amount` only, sourced from the same daily-bar family (`stock_hk_hist` / `stock_hk_daily`), with no independent liquidity-specific route. Remaining blocker: turnover-rate, float-share, spread, and deeper microstructure facts.
- `hk_corporate_actions`: accepted TASK-134 behavior preserved. No code-path change in this rework; regression coverage and live smoke still pass.

## tests run
- `python3 -m unittest tests.datahub.test_source_capabilities`
- `python3 -m unittest tests.datahub.test_source_catalog`
- `python3 -m unittest tests.datahub.test_akshare_hk_instrument_master_adapter`
- `python3 -m unittest tests.datahub.test_akshare_hk_instrument_master_live`
- `python3 -m unittest tests.datahub.test_akshare_hk_adapter`
- `python3 -m unittest tests.datahub.test_akshare_hk_valuation_snapshot_adapter`
- `python3 -m unittest tests.datahub.test_akshare_hk_valuation_snapshot_live`
- `python3 -m unittest tests.datahub.test_akshare_hk_financial_data_adapter`
- `python3 -m unittest tests.datahub.test_akshare_hk_financial_data_live`
- `python3 -m unittest tests.datahub.test_akshare_hk_live`
- `python3 -m unittest tests.datahub.test_akshare_hk_corporate_actions_live`
- `QUANT_SYSTEM_LIVE_TESTS=0 python3 -m unittest tests.datahub.test_source_capabilities tests.datahub.test_source_catalog tests.datahub.test_akshare_hk_instrument_master_adapter tests.datahub.test_akshare_hk_instrument_master_live tests.datahub.test_akshare_hk_adapter tests.datahub.test_akshare_hk_valuation_snapshot_adapter tests.datahub.test_akshare_hk_financial_data_adapter tests.datahub.test_akshare_hk_corporate_actions_adapter tests.datahub.test_akshare_hk_corporate_actions_live`

## default network behavior
- Default behavior remains offline-safe when `QUANT_SYSTEM_LIVE_TESTS` is unset or `0`.
- The explicit offline regression command above passed: `Ran 201 tests in 0.740s, OK (skipped=3)`.
- Live smokes remain environment-gated by `QUANT_SYSTEM_LIVE_TESTS=1`; no hidden default live network calls were added.

## live-enabled PASS/SKIP/FAIL result and root-cause evidence
- `hk_universe_reference`: PASS
  - Command: `python3 -m unittest tests.datahub.test_akshare_hk_instrument_master_live`
  - Result: `Ran 7 tests in 4.050s, OK`
  - Root-cause evidence for the fixed defect: live diagnosis showed `stock_hk_spot_em` currently returned a bounded sample beginning with `85081.HK`, `85082.HK`, ... and zero overlap with the Sina stock page sample; the new overlap check switched bounded current-listed sampling to `sina_hk_stock_spot_page1`, after which the live module passed.
- `hk_daily_bars` and `hk_turnover_liquidity`: PASS
  - Command: `python3 -m unittest tests.datahub.test_akshare_hk_live`
  - Result: `Ran 4 tests in 3.109s, OK`
  - Evidence: bounded primary-route and fallback-route smokes both passed for HK daily bars and turnover/liquidity.
- `hk_valuation_history`: PASS
  - Command: `python3 -m unittest tests.datahub.test_akshare_hk_valuation_snapshot_live`
  - Result: `Ran 3 tests in 70.738s, OK`
  - Evidence: dated multi-symbol valuation smoke passed; blocker remains current-dated continuity, not route unavailability.
- `hk_financial_data`: PASS
  - Command: `python3 -m unittest tests.datahub.test_akshare_hk_financial_data_live`
  - Result: `Ran 8 tests in 6.652s, OK`
  - Evidence: both statements and indicators smokes passed with bounded report-period assertions.
- `hk_corporate_actions`: PASS
  - Command: `python3 -m unittest tests.datahub.test_akshare_hk_corporate_actions_live`
  - Result: `Ran 4 tests in 1.260s, OK`
  - Evidence: previously accepted corporate-actions live smoke still passes unchanged.

## deviations
- None.

## risks/follow-up
- `hk_universe_reference` is still stock-only proof; no public no-credential route in this repo proves reusable HK non-stock taxonomy or dated delist/inactive lifecycle metadata.
- `hk_daily_bars` and `hk_turnover_liquidity` still rely on one AKShare family; no independent second public route was proven here.
- `hk_valuation_history` still lacks current-dated dated-history proof; `stock_hk_indicator_eniu` live history remains stale through `2022-07-13`.
- `hk_financial_data` still lacks broader issuer sampling proof beyond liquid-stock examples and still has no independent public-route redundancy.
