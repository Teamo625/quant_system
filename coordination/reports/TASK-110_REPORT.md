# TASK-110 Report

- files changed
  - `quant/datahub/adapters/akshare.py`
  - `quant/datahub/datasets.py`
  - `quant/datahub/source_capabilities.py`
  - `tests/datahub/test_akshare_hk_instrument_master_adapter.py`
  - `tests/datahub/test_akshare_hk_instrument_master_live.py`
  - `tests/datahub/test_datasets.py`
  - `tests/datahub/test_source_capabilities.py`

- implementation summary
  - Added optional `source_route` contract support to `DatasetName.INSTRUMENT_MASTER`.
  - `AkshareHKInstrumentMasterAdapter` now emits `source_route="stock_hk_security_profile_em"` on normalized HK stock reference records.
  - Tightened the HK instrument-master live unavailability classifier so provider/route tokens alone no longer downgrade repository-side `TypeError` / payload-shape defects to environment `SKIP`.
  - Kept `hk_universe_reference` conservative at `partial`; wording now explicitly states profile-route provenance while preserving the open breadth/lifecycle gaps.

- tests run
  - `python3 -m unittest tests/datahub/test_akshare_hk_instrument_master_adapter.py` -> PASS
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_hk_instrument_master_live.py` -> PASS (`live` skipped by default, `skipped=1`)
  - `python3 -m unittest tests/datahub/test_source_capabilities.py` -> PASS
  - `python3 -m unittest tests/datahub/test_datasets.py` -> PASS
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_instrument_master_live.py` -> PASS

- default network behavior
  - Default tests remain offline-safe.
  - Adapter tests use injected fetch callables only.
  - The live test file still skips by default unless `QUANT_SYSTEM_LIVE_TESTS=1` is explicitly set.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence
  - Result: PASS
  - Evidence:
    - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_instrument_master_live.py` finished `OK` on 2026-06-06.
    - Direct post-test probe with `AkshareHKInstrumentMasterAdapter` over `("00005.HK", "00700.HK")` returned `record_count=2`.
    - Sample normalized facts:
      - `00005.HK`: `list_date=1980-01-02`, `source_route=stock_hk_security_profile_em`, `exchange=HKEX`, `asset_type=stock`, `currency=HKD`
      - `00700.HK`: `list_date=2004-06-16`, `source_route=stock_hk_security_profile_em`, `exchange=HKEX`, `asset_type=stock`, `currency=HKD`

- capability truth changed
  - `hk_universe_reference` remains `partial`.
  - Status was not promoted to `covered`.
  - Gap wording now explicitly reflects bounded multi-symbol HK stock reference batches with profile-route provenance.

- source route coverage and known HK universe/lifecycle limitations
  - Implemented route truth: `stock_hk_security_profile_em` is now explicit on normalized `INSTRUMENT_MASTER` records.
  - Covered slice remains bounded to caller-provided HK stock symbols and current profile snapshots.
  - No full-market HK universe collection was added.
  - No dated delisting reconstruction or broader lifecycle timeline was added.
  - No non-stock taxonomy coverage was added beyond explicit rejection/hard-failure behavior.
  - `delist_date` remains the active sentinel `9999-12-31` for the proven current-stock slice only.

- non-stock handling and batch behavior
  - Full-batch validation remains intact: invalid requested symbols fail before any source call.
  - Duplicate requested symbols are normalized/deduplicated before fetch.
  - Unexpected returned symbols, malformed payload rows, missing required fields, invalid dates, conflicting duplicates, and non-stock profile rows remain hard failures.
  - Route-name-bearing `TypeError` failures such as `stock_hk_security_profile_em ... NoneType ...` now remain non-environment hard failures instead of becoming live `SKIP`.

- deviations
  - None.

- risks/follow-up
  - Public no-credential HK stock reference coverage is still limited to per-symbol current profile snapshots; wider current-listed breadth still lacks a proven bounded list route.
  - Stable public dated delisting / inactive-status metadata for HK instruments remains unproven and should stay a separate hardening target.
  - If a future handoff wants board, lot-size, or industry as stable contract fields, it should reopen `INSTRUMENT_MASTER` explicitly instead of inferring them from this accepted minimal source-route hardening.
