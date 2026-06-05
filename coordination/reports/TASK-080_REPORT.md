# TASK-080 Report

- files changed
  - `quant/datahub/adapters/akshare.py`
  - `quant/datahub/source_capabilities.py`
  - `tests/datahub/test_akshare_hk_instrument_master_adapter.py`
  - `tests/datahub/test_akshare_hk_instrument_master_live.py`
  - `tests/datahub/test_source_capabilities.py`

- tests run
  - `python3 -m unittest tests/datahub/test_akshare_hk_instrument_master_adapter.py` -> PASS
  - `python3 -m unittest tests/datahub/test_source_capabilities.py` -> PASS
  - `python3 -m unittest -v tests/datahub/test_akshare_hk_instrument_master_live.py` -> PASS in current shell environment
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_hk_instrument_master_live.py` -> PASS, live smoke SKIP by default (`skipped=1`)
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_instrument_master_live.py` -> PASS

- default network behavior
  - Adapter/unit tests are offline-safe via injected fetch stubs.
  - Live smoke file remains gated by `QUANT_SYSTEM_LIVE_TESTS=1`; explicit unset run skipped the live case and made no real network call.
  - The plain default command passed in this shell because the environment already exposed `QUANT_SYSTEM_LIVE_TESTS=1`; explicit unset confirmed the repository default behavior is still offline-safe.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence
  - PASS
  - Evidence: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_instrument_master_live.py`
  - Result: classifier tests passed and the live smoke passed for bounded two-symbol HK stock batch `("00005.HK", "00700.HK")`.
  - Route exercised: AKShare public `stock_hk_security_profile_em` per requested symbol.

- capability truth
  - `hk_universe_reference` remains `partial`.
  - Truth text changed from narrow one-symbol slice wording to bounded caller-provided multi-symbol HK stock reference batch wording.
  - Status was not promoted to `covered`.

- source route coverage / behavior
  - Batch access now uses the existing `SourceRequest.symbols` path and validates the full requested symbol set before any source call.
  - Supported request inputs remain canonical `00700.HK` and existing raw 5-digit codes such as `00700`.
  - Duplicate requested symbols are normalized/deduplicated before source calls.
  - Each validated symbol is fetched through the AKShare public security-profile route individually.
  - Output is normalized to `DatasetName.INSTRUMENT_MASTER`, deduplicated by `(symbol, source)`, and sorted by symbol.
  - Any invalid symbol, unexpected returned symbol, malformed payload, normalization error, or fetch failure aborts the full batch instead of returning partial success.
  - Non-stock instruments now fail clearly with `Requested HK instrument is not a stock security`.

- known HK reference limitations
  - No full-market HK universe collection was added.
  - No dated delisting reconstruction or broader lifecycle taxonomy was added.
  - No non-stock HK taxonomy coverage was added; those requests are rejected for this stock-reference slice.
  - `start_date` and `end_date` remain accepted but still do not imply historical reconstruction.

- deviations
  - None.

- risks/follow-up
  - Public AKShare coverage is still bounded to caller-provided stock symbols and current profile snapshots; wider HK breadth and dated lifecycle metadata remain open.
  - If downstream work needs ETF/fund/index HK reference handling, it should use a separate capability/handoff rather than relaxing this stock-only adapter path.
