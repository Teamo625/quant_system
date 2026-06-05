# TASK-074 Report

- files changed:
  - `quant/datahub/adapters/akshare.py`
  - `quant/datahub/adapters/__init__.py`
  - `quant/datahub/source_capabilities.py`
  - `tests/datahub/test_akshare_a_share_instrument_status_history_adapter.py`
  - `tests/datahub/test_akshare_a_share_instrument_status_history_live.py`
  - `tests/datahub/test_source_capabilities.py`

- tests run:
  - `python3 -m unittest tests/datahub/test_akshare_a_share_instrument_status_history_adapter.py` -> PASS
  - `python3 -m unittest tests/datahub/test_source_capabilities.py` -> PASS
  - `python3 -m unittest -v tests/datahub/test_akshare_a_share_instrument_status_history_live.py` -> PASS
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_instrument_status_history_live.py` -> PASS

- default network behavior:
  - Offline/default adapter tests use injected fixtures only and patch `socket.create_connection` to fail on unexpected network.
  - The live smoke file remains skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1` is set.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence:
  - PASS
  - Live smoke resolved `000001.SZ` as the active normal sample and `600001.SH` from `stock_info_sh_delist(全部)` as the lifecycle sample.
  - Live fetch returned 4 validated `INSTRUMENT_STATUS_HISTORY` records:
    - `000001.SZ`: `listing_status=listed` at `1991-04-03`, `risk_warning=normal` at current fetch date
    - `600001.SH`: `listing_status=listed` at `1998-01-22`, `listing_status=delisted` at `2009-12-29`

- capability truth changes:
  - `a_share_listing_delisting_st_status` remains `partial`
  - Gap text was tightened to reflect proven bounded AKShare coverage: listing dates, terminal delisting dates, current normal/ST snapshots, and SZ short-name status deltas for caller-provided symbols

- source route coverage and known limitations:
  - Implemented bounded AKShare coverage through:
    - `stock_info_sh_name_code(主板A股)`
    - `stock_info_sh_name_code(科创板)`
    - `stock_info_sz_name_code(A股列表)`
    - `stock_info_bj_name_code()`
    - `stock_info_sh_delist(全部)`
    - `stock_info_sz_delist(终止上市公司)`
    - `stock_info_sz_change_name(简称变更)`
  - Active normal/ST status is normalized conservatively from current short-name snapshots; no historical continuity is invented from snapshot-only routes.
  - Dated risk-warning deltas are only source-proven for SZ symbols via the SZSE short-name change route.
  - No public bounded SH/BJ dated ST/*ST history route was added here, so full exchange-wide dated continuity is still incomplete.

- deviations:
  - None

- risks/follow-up:
  - SH/SZ/BJ active-list routes are public-web dependent; environment or upstream network failures should remain classified as live-environment unavailability, not default-test failures.
  - Future hardening can expand dated ST/*ST continuity beyond SZ and add broader lifecycle taxonomy if a stable public route is identified.
