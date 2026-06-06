# TASK-111 Report

- files changed
  - `quant/datahub/adapters/akshare.py`
  - `quant/datahub/source_capabilities.py`
  - `tests/datahub/test_akshare_hk_instrument_master_adapter.py`
  - `tests/datahub/test_akshare_hk_instrument_master_live.py`
  - `tests/datahub/test_source_capabilities.py`

- implementation summary
  - Added a bounded HK current-listed list path to `AkshareHKInstrumentMasterAdapter` for `symbols=None`.
  - The new path fetches only one bounded Eastmoney list page (`stock_hk_spot_em` route family), sorts deterministically by canonical HK symbol, then reconciles each candidate through per-symbol `stock_hk_security_profile_em` normalization.
  - List-derived records emit `source_route="stock_hk_spot_em+stock_hk_security_profile_em"`.
  - Non-stock candidates discovered during bounded list reconciliation are skipped only when profile truth explicitly classifies them as non-stock; malformed payloads, empty stock yield, unexpected symbols, schema/normalization defects, and route token `TypeError` remain hard failures.
  - `hk_universe_reference` stays `partial`; capability wording now reflects bounded spot-list plus profile reconciliation while keeping breadth/taxonomy/lifecycle limits explicit.

- tests run
  - `python3 -m unittest tests/datahub/test_akshare_hk_instrument_master_adapter.py` -> PASS
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_hk_instrument_master_live.py` -> PASS (`skipped=2`; live tests disabled by default)
  - `python3 -m unittest tests/datahub/test_source_capabilities.py` -> PASS
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_instrument_master_live.py` -> PASS overall (`skipped=1`)

- default network behavior
  - Default tests remain offline-safe.
  - Adapter/unit tests use injected fixtures only.
  - The live test file still skips live cases by default unless `QUANT_SYSTEM_LIVE_TESTS=1` is explicitly set.
  - The new bounded list-route behavior is exercised offline through injected list/profile fixtures; no default test performs real network IO.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence
  - Result: PASS overall
  - Evidence:
    - `test_live_akshare_hk_instrument_master_smoke` -> PASS against live `stock_hk_security_profile_em` for `00005.HK` and `00700.HK`
    - `test_live_akshare_hk_instrument_master_bounded_current_list_smoke` -> SKIP due genuine upstream/environment unavailability:
      - `RuntimeError: AKShare HK instrument-master route unavailable: stock_hk_spot_em -> ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))`
  - Repository-side classifier/result truth after rework:
    - profile-route live contract/normalization remains proven PASS
    - bounded list-route branch now truthfully skips only on real upstream/network failure and no longer relies on unbounded AKShare pagination

- whether `hk_universe_reference` capability truth changed
  - Status unchanged: `partial`
  - Gap wording changed to include bounded current-listed spot-list plus per-symbol profile reconciliation
  - No promotion to `covered`

- source route coverage and known HK universe/lifecycle limitations
  - Proven per-symbol source route: `stock_hk_security_profile_em`
  - Implemented bounded current-listed reconciliation route: `stock_hk_spot_em+stock_hk_security_profile_em`
  - Current bounded list path is limited to one live list page and at most 20 normalized stock records
  - No full-market HK universe collection, dated delisting reconstruction, inactive-status timeline, or trustworthy lifecycle history was added
  - Public non-stock taxonomy remains incomplete; bulk list handling only keeps rows whose profile route proves stock compatibility

- non-stock handling and batch/list behavior
  - Caller-provided symbol batches still require full validation before source calls; explicit empty symbol sequences remain invalid
  - `symbols=None` now means bounded current-listed sampling, not unbounded market crawl
  - Deterministic ordering is by canonical HK symbol after list-route deduplication
  - Non-stock list candidates are skipped only after explicit profile-route classification; non-stock caller-requested symbols still hard fail
  - If bounded list reconciliation yields zero stock records, the adapter hard fails instead of silently returning an empty partial success

- deviations
  - None

- risks/follow-up
  - The Eastmoney HK spot/list route was not live-pass-proven in this environment because the upstream connection aborted; future controller follow-up may need a dedicated rework if that route must become closure-grade.
  - Even with the new bounded list path, HK reference capability still lacks full practical breadth, stable non-stock taxonomy, and source-backed delisting/lifecycle dates.
  - If a future task needs configurable bounded list size or richer HK reference fields, it should reopen `INSTRUMENT_MASTER` explicitly rather than infer them from this accepted stock-only slice.
