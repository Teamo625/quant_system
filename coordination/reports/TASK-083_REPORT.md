# TASK-083 Report

- files changed:
  - `quant/datahub/adapters/akshare.py`
  - `quant/datahub/source_capabilities.py`
  - `tests/datahub/test_akshare_fund_nav_adapter.py`
  - `tests/datahub/test_akshare_fund_nav_live.py`
  - `tests/datahub/test_source_capabilities.py`

- implementation summary:
  - Hardened `AkshareETFFundNavSnapshotAdapter` from single-symbol fetches to caller-provided multi-symbol ETF/fund NAV batches.
  - Added batch symbol normalization/validation, multi-symbol bounded date-window enforcement, deterministic local date filtering, duplicate merge/sort behavior, and clear failure when any requested batch symbol yields no usable rows.
  - Improved normalization resilience for live AKShare NAV rows with missing required values by skipping unusable rows when the same symbol still has usable rows, while preserving hard failure when an entire payload is unusable.
  - Kept `fund_nav` capability truth `partial` and updated wording to reflect proven multi-symbol bounded date-window access plus remaining breadth/history gaps.

- tests run:
  - `python3 -m unittest tests/datahub/test_akshare_fund_nav_adapter.py` -> PASS
  - `python3 -m unittest tests/datahub/test_source_capabilities.py` -> PASS
  - `python3 -m unittest -v tests/datahub/test_akshare_fund_nav_live.py` -> PASS
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_fund_nav_live.py` -> PASS
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_fund_nav_live.py` -> PASS (`skipped=1`)

- default network behavior:
  - Default adapter and capability tests are offline-safe and use injected fixtures only.
  - `tests/datahub/test_akshare_fund_nav_live.py` remains env-gated and skips when `QUANT_SYSTEM_LIVE_TESTS` is unset.
  - In this shell, `QUANT_SYSTEM_LIVE_TESTS=1` was already preset, so the handoff’s default `python3 -m unittest -v tests/datahub/test_akshare_fund_nav_live.py` command executed live instead of skipping; the explicit `env -u ...` run confirmed the intended offline-safe default gate.

- live-enabled result and evidence:
  - PASS
  - Evidence:
    - Isolated live-enabled smoke passed for `510300.ETF_CN` and `159915.ETF_CN` over `2024-01-02` to `2024-01-10`.
    - Normalized records validated against `DatasetName.FUND_NAV_SNAPSHOT`.
    - During one concurrent diagnostic run, AKShare returned rows with missing required NAV/trade-date values; the adapter now skips those unusable source rows when usable rows for the same symbol remain, and isolated acceptance-style live runs passed afterward.

- capability truth:
  - `fund_nav` remains `partial`.
  - Reason: bounded multi-symbol exchange ETF/fund NAV access is now proven, but broader fund breadth, longer history continuity, and non-exchange public-route coverage remain incomplete.

- source route coverage and known ETF/fund NAV limitations:
  - Covered by this task: caller-provided multi-symbol AKShare public NAV access for supported China exchange ETF/fund codes in bounded date windows.
  - Still limited: unsupported stock/index/HK-like symbols are rejected; multi-symbol requests require both `start_date` and `end_date`; full-market breadth, long-history continuity, and non-exchange/public-route expansion are not solved here.

- deviations:
  - No scope deviations.
  - Added one extra verification command with `env -u QUANT_SYSTEM_LIVE_TESTS` to prove the live test file still skips by default when the environment flag is absent.

- risks/follow-up:
  - AKShare NAV responses can intermittently include incomplete rows; current hardening tolerates missing-value rows only when other usable rows exist for the same symbol.
  - Future Phase 2.5 follow-up should extend ETF/fund NAV breadth/history beyond bounded public exchange ETF coverage before any promotion from `partial`.
