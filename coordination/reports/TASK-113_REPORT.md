# TASK-113 Report

- files changed
  - `quant/datahub/source_capabilities.py`
  - `quant/datahub/source_catalog.py`
  - `tests/datahub/test_source_capabilities.py`
  - `tests/datahub/test_source_catalog.py`

- implementation summary
  - Kept `AkshareHKInstrumentMasterAdapter` behavior unchanged and tightened project truth instead of over-claiming new HK coverage.
  - Updated `hk_universe_reference` capability wording to state that the proven no-credential HK routes are still stock-only, do not provide reusable non-stock taxonomy truth, and do not expose trustworthy dated delist/inactive lifecycle metadata.
  - Updated AKShare source-catalog notes so HK instrument-master coverage is explicitly constrained to `stock_hk_security_profile_em` plus bounded `stock_hk_spot_em` / `sina_hk_stock_spot_page1` current-listed stock sampling.
  - Added regression assertions so future wording drift cannot silently imply closure-grade HK universe breadth.

- tests run
  - `python3 -m unittest tests/datahub/test_akshare_hk_instrument_master_adapter.py` -> PASS
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_hk_instrument_master_live.py` -> PASS (`skipped=2`)
  - `python3 -m unittest tests/datahub/test_source_capabilities.py` -> PASS
  - `python3 -m unittest tests/datahub/test_source_catalog.py` -> PASS
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_instrument_master_live.py` -> PASS

- default network behavior
  - Default tests remain offline-safe.
  - No default-path live IO was added.
  - Live HK tests still run only when `QUANT_SYSTEM_LIVE_TESTS=1` is explicitly set.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence
  - Result: PASS
  - Evidence:
    - Gated live suite finished `OK` on 2026-06-06.
    - Direct post-test stock probe returned 2 normalized records for `('00005.HK', '00700.HK')` with `source_route=stock_hk_security_profile_em`.
    - Direct bounded list probe returned 20 normalized current-listed records with `source_route=sina_hk_stock_spot_page1+stock_hk_security_profile_em`.
    - Sample normalized facts:
      - `00005.HK` -> `list_date=1980-01-02`, `delist_date=9999-12-31`, `is_active=True`
      - `00001.HK` -> `source_route=sina_hk_stock_spot_page1+stock_hk_security_profile_em`

- whether HK non-stock taxonomy truth is source-backed, constrained, or unsupported by proven no-credential routes
  - Constrained / unsupported for closure-grade use.
  - Route exploration evidence:
    - `stock_hk_security_profile_em('02800')`, `('00823')`, and `('02828')` each raised `TypeError: 'NoneType' object is not subscriptable` instead of returning reusable taxonomy rows.
    - Direct Sina page-1 spot probe returned 60 rows with `tradetype=''` throughout the sampled payload, so it does not provide reusable non-stock classification truth.
  - Resulting project truth: proven HK `INSTRUMENT_MASTER` coverage remains stock-only.

- whether HK listed/delisted/inactive lifecycle truth is source-backed, constrained, or unsupported by proven no-credential routes
  - Constrained / unsupported for dated lifecycle truth.
  - Proven routes provide current stock `list_date` and active-slice normalization only.
  - No explored local AKShare HK callable exposed trustworthy dated delist or inactive-status metadata suitable for `INSTRUMENT_MASTER`.
  - `delist_date=9999-12-31` remains a current-stock sentinel for the proven slice only and is not treated as dated lifecycle coverage.

- whether `hk_universe_reference` capability truth changed
  - Status unchanged: `partial`
  - No promotion to `covered`
  - Wording tightened to make stock-only taxonomy/lifecycle limitations explicit

- source route coverage and known HK universe/taxonomy/lifecycle limitations
  - Proven stock-profile route: `stock_hk_security_profile_em`
  - Proven bounded current-listed route in this environment: `sina_hk_stock_spot_page1+stock_hk_security_profile_em`
  - Bounded Eastmoney list route remains implemented but was not needed for this live PASS
  - Still missing:
    - closure-grade HK full-market breadth
    - source-backed non-stock taxonomy under `INSTRUMENT_MASTER`
    - trustworthy dated delist/inactive lifecycle metadata

- deviations
  - None

- risks/follow-up
  - If controller wants progress beyond stock-only HK reference truth, a future handoff must first prove a stable no-credential HK route for non-stock classification or dated lifecycle facts; current local AKShare exploration did not.
  - `stock_hk_spot()` remains unsuitable for this phase as-is because AKShare implements it as an unbounded 99-page crawl path rather than a bounded reference route.
