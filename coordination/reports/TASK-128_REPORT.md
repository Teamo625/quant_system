# TASK-128 Report

- files changed:
  - `tests/datahub/test_akshare_sector_live.py`
  - `coordination/reports/TASK-128_REPORT.md`

- implementation summary:
  - Removed the sector daily-bar live smoke branch that treated generic `ValueError` as skippable `empty_results`.
  - Kept skip behavior narrow: only network/proxy/DNS/TLS/upstream/source-availability evidence continues to map to live `SKIP`.
  - Added focused offline classifier regressions so route-signature and normalized-record validation failures are explicitly non-skippable.

- exact Review finding addressed:
  - Fixed `tests/datahub/test_akshare_sector_live.py` so broad `ValueError` catch-and-skip no longer masks repository-side schema/contract/normalization/date-window/duplicate-conflict defects as environment/source `SKIP`.

- tests run:
  - `python3 -m unittest tests.datahub.test_akshare_sector_adapter` -> PASS
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_sector_live` -> PASS (`Ran 4 tests`, `OK`, `skipped=1`)
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_sector_live` -> PASS (`Ran 4 tests in 17.917s`, `OK`)

- default network behavior:
  - Default tests remain offline-safe.
  - The live smoke is still gated by `QUANT_SYSTEM_LIVE_TESTS=1`.
  - With `QUANT_SYSTEM_LIVE_TESTS` unset, only the local classifier tests run and the real-source smoke is skipped by default.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence for real-source tasks:
  - sector daily bars: PASS
  - Evidence: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_sector_live` completed with `Ran 4 tests in 17.917s` and `OK`.
  - No environment/source-unavailability skip path triggered in this run after the classifier tightening.

- membership/history behavior changed?:
  - No. `sector_membership` / `sector_historical_changes` tests and behavior were not modified in this rework.

- deviations:
  - None.

- risks/follow-up:
  - Sector daily-bar live smoke now fails on repository-side `ValueError` defects by design; if future upstream routes expose a clearly distinguishable source-wide no-data error, that skip boundary can be refined with separate evidence.
