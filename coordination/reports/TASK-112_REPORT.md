# TASK-112 Report

- files changed
  - `quant/datahub/adapters/akshare.py`
  - `quant/datahub/source_capabilities.py`
  - `tests/datahub/test_akshare_hk_instrument_master_adapter.py`
  - `tests/datahub/test_akshare_hk_instrument_master_live.py`
  - `tests/datahub/test_source_capabilities.py`

- implementation summary
  - Added a bounded HK listed-universe fallback path in `AkshareHKInstrumentMasterAdapter`: primary `stock_hk_spot_em`, fallback `sina_hk_stock_spot_page1`, both still reconciled through per-symbol `stock_hk_security_profile_em`.
  - Fallback triggers only when the primary list route is classified as genuine environment/upstream unavailability; schema, payload, normalization, signature, and route-token `TypeError` defects remain hard failures.
  - Fallback-normalized records emit `source_route="sina_hk_stock_spot_page1+stock_hk_security_profile_em"`.
  - Capability wording for `hk_universe_reference` remains conservative at `partial`, now explicitly describing Eastmoney list plus bounded Sina page-1 fallback.

- tests run
  - `python3 -m unittest tests/datahub/test_akshare_hk_instrument_master_adapter.py` -> PASS
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_hk_instrument_master_live.py` -> PASS (`skipped=2`)
  - `python3 -m unittest tests/datahub/test_source_capabilities.py` -> PASS
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_instrument_master_live.py` -> PASS

- default network behavior
  - Default tests remain offline-safe.
  - Adapter/unit coverage uses injected fixtures only.
  - Live cases remain explicitly gated by `QUANT_SYSTEM_LIVE_TESTS=1`.
  - No new default-path real network IO was added.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence
  - Result: PASS
  - Required live smoke passed for both `test_live_akshare_hk_instrument_master_smoke` and `test_live_akshare_hk_instrument_master_bounded_current_list_smoke`.
  - Root-cause evidence for the TASK-111 skip path remains reproducible locally:
    - direct `ak.stock_hk_spot_em()` -> `ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))`
    - adapter diagnostic `adapter._fetch_current_list_rows()` selected `sina_hk_stock_spot_page1` and returned 60 bounded list rows after the primary route failed

- whether the bounded HK listed-universe route is now live-pass-proven
  - Yes, but only via the bounded Sina page-1 fallback plus `stock_hk_security_profile_em` reconciliation.
  - The original Eastmoney primary list route is still not live-pass-proven in this environment.

- whether `hk_universe_reference` capability truth changed
  - Status unchanged: `partial`
  - Wording updated to reflect Eastmoney primary plus bounded Sina fallback
  - No promotion to `covered`

- source route coverage and known HK universe/list/lifecycle limitations
  - Proven per-symbol route: `stock_hk_security_profile_em`
  - Proven bounded list routes:
    - `stock_hk_spot_em+stock_hk_security_profile_em` when primary is reachable
    - `sina_hk_stock_spot_page1+stock_hk_security_profile_em` when primary is environment/upstream unavailable
  - Still limited to bounded current-listed sampling, stock-only truth after profile reconciliation, and no dated delisting/lifecycle reconstruction
  - Full-market breadth, stable non-stock taxonomy, and source-backed inactive history remain incomplete

- fallback-route feasibility decision
  - Implemented
  - Reason: no-credential Sina page-1 route was reachable locally, returns deterministic HK symbol rows, and can be truthfully constrained by downstream profile-route stock validation

- non-stock handling and batch/list behavior
  - Caller-provided symbol batches still require full upfront validation and remain all-or-nothing.
  - `symbols=None` remains bounded; no unbounded crawl or historical backfill was added.
  - Non-stock list candidates are still dropped only after profile truth explicitly classifies them as non-stock.
  - Empty stock yield, malformed payloads, duplicate conflicts, unexpected symbols, and route-signature/call-compatibility defects still hard fail.

- deviations
  - None

- risks/follow-up
  - Eastmoney HK list endpoints still reproduce `RemoteDisconnected` in this environment; if controller needs the primary route itself to become closure-grade, another upstream-focused rework would still be required.
  - The new fallback proves only a bounded current-listed sample path, not closure-grade HK universe completeness.
  - `hk_universe_reference` still lacks full practical breadth, non-stock taxonomy truth, and dated lifecycle metadata.
