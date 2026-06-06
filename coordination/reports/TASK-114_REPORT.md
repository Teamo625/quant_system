# TASK-114 Report

- files changed
  - `quant/datahub/adapters/akshare.py`
  - `quant/datahub/source_capabilities.py`
  - `quant/datahub/source_catalog.py`
  - `tests/datahub/test_akshare_hk_adapter.py`
  - `tests/datahub/test_akshare_hk_live.py`
  - `tests/datahub/test_source_capabilities.py`
  - `tests/datahub/test_source_catalog.py`
  - `coordination/reports/TASK-114_REPORT.md`

- tests run
  - `python3 -m unittest tests/datahub/test_akshare_hk_adapter.py` -> PASS (`Ran 20 tests`)
  - `python3 -m unittest tests/datahub/test_source_capabilities.py` -> PASS (`Ran 39 tests`)
  - `python3 -m unittest tests/datahub/test_source_catalog.py` -> PASS (`Ran 9 tests`)
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_hk_live.py` -> PASS default-skip (`Ran 2 tests`, `skipped=2`)
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_live.py` -> PASS (`Ran 2 tests`)

- default network behavior
  - Default/offline tests remain network-safe.
  - `tests/datahub/test_akshare_hk_live.py` is still gated by `QUANT_SYSTEM_LIVE_TESTS=1` and skips by default.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence
  - Result: PASS.
  - Real-source smoke now checks two liquid HK stocks (`00700.HK`, `00005.HK`) over bounded historical window `2019-01-02` to `2019-01-15`.
  - Default adapter smoke PASSed.
  - Real fallback-route smoke PASSed by forcing `stock_hk_hist` unavailability and using live `stock_hk_daily`.
  - Direct route evidence in this environment:
    - `stock_hk_hist("00700")` -> `ConnectionError('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))`
    - `stock_hk_hist("00005")` -> same `ConnectionError/RemoteDisconnected`
    - `stock_hk_daily("00700")` returned `5403` rows (`2004-06-16` .. `2026-06-05`) and `10` bounded rows in the requested 2019 window
    - `stock_hk_daily("00005")` returned `6904` rows (`1998-06-01` .. `2026-06-05`) and `10` bounded rows in the requested 2019 window

- capability truth changed
  - `hk_daily_bars` status stays `partial`.
  - Wording was tightened/updated to state that proven no-credential history continuity currently comes from `stock_hk_hist` plus `stock_hk_daily` same-family fallback, not from an independent second public source.

- source route coverage, date-window behavior, fallback behavior, history-continuity evidence, known limitations
  - Adapter still preserves caller-provided HK stock symbol contract and full batch validation before source calls.
  - Primary route remains `stock_hk_hist(symbol, period, start_date, end_date, adjust)`.
  - Fallback route remains `stock_hk_daily(symbol, adjust)`.
  - New hardening: if `stock_hk_hist` returns no rows, adapter now tries `stock_hk_daily` and then applies the requested date-window filter locally.
  - Non-network `stock_hk_hist` failures still hard-fail; fallback is not used for route-signature/schema/payload/normalization defects.
  - Non-network `stock_hk_daily` failures after fallback selection still hard-fail.
  - Returned records remain deterministically deduped/sorted and date-filtered after normalization.
  - Proven limitation: both proven routes are inside one AKShare public family; independent public-source redundancy is still unproven.
  - Proven limitation: scope remains HK stocks only; no full-market backfill or closure-grade completeness claim was added.

- whether stronger public-source redundancy was implemented, constrained, or unsupported
  - Implemented: stronger same-family practical redundancy/history continuity via `stock_hk_daily` fallback when `stock_hk_hist` is unavailable or empty.
  - Constrained: capability/catalog truth now explicitly says this is not independent second-source redundancy.

- deviations
  - None.

- risks/follow-up
  - Future hardening would need an independent no-credential HK daily-bar source, or stronger proof that a second non-identical public route is stable enough for trading-grade redundancy.
  - `hk_daily_bars` must remain conservative until independent-source redundancy and broader closure-grade completeness are proven.
