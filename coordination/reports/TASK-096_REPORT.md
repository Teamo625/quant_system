# TASK-096 Report

- files changed
  - `tests/datahub/test_baostock_a_share_minute_bars_live.py`
  - `coordination/reports/TASK-096_REPORT.md`

- tests run
  - `python3 -m unittest -v tests/datahub/test_baostock_a_share_minute_bars_live.py` -> PASS (`Ran 5 tests`, ambient shell had live env enabled so the live smoke executed and passed)
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_baostock_a_share_minute_bars_live.py` -> PASS (`Ran 5 tests`, `skipped=1`)
  - `python3 -m unittest tests/datahub/test_baostock_a_share_minute_bars_adapter.py` -> PASS (`Ran 9 tests`)
  - `python3 -m unittest tests/datahub/test_source_capabilities.py` -> PASS (`Ran 34 tests`)
  - `python3 -m unittest tests/datahub/test_source_catalog.py` -> PASS (`Ran 8 tests`)
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_baostock_a_share_minute_bars_live.py` -> PASS (`Ran 5 tests`)

- default network behavior
  - Default behavior remains offline-safe when `QUANT_SYSTEM_LIVE_TESTS` is unset.
  - `env -u QUANT_SYSTEM_LIVE_TESTS ...test_baostock_a_share_minute_bars_live.py` proved the live smoke skips by default and no default test performed a real network call.
  - The plain `python3 -m unittest -v ...` invocation ran the live path only because the ambient shell already exported `QUANT_SYSTEM_LIVE_TESTS=1`; this does not change the file's default gating behavior.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence for real-source tasks
  - Result: `PASS`
  - Command: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_baostock_a_share_minute_bars_live.py`
  - Evidence: unittest completed `Ran 5 tests ... OK` and BaoStock printed `login success!` / `logout success!`.

- classifier truthfulness result
  - Removed the broad bare `"baostock"` message token from `_is_live_environment_unavailable(...)`.
  - Environment-unavailable classification now stays tied to network exception classes, transport/network message tokens, socket/timeout/connection errors, OS-level connection errnos, and narrow service-availability phrases such as `login failed` / `service unavailable`.
  - Focused regressions now prove BaoStock-specific contract/data failures do not downgrade to `SKIP`:
    - `ValueError("Invalid BaoStock date value: bad")` -> `False`
    - `ValueError("Source symbol mismatch for BaoStock A-share minute-bars adapter")` -> `False`
  - Positive regression kept for real availability classification:
    - `RuntimeError("BaoStock login failed: service unavailable")` -> `True`

- deviations
  - No scope deviation in this rework.
  - Ambient shell environment already had `QUANT_SYSTEM_LIVE_TESTS=1` for the plain unittest command; explicit `env -u ...` was used to verify true default behavior.

- risks/follow-up
  - Review Agent still needs to confirm the classifier boundary is now closure-safe.
  - If BaoStock changes its upstream availability wording materially, the live skip classifier may need another narrow token update.
