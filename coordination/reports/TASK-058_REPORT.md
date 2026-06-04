# TASK-058 Report

## files changed

- `quant/datahub/source_capabilities.py`
- `tests/datahub/test_source_capabilities.py`
- `coordination/reports/TASK-058_REPORT.md`

## tests run

- `python3 -m unittest tests/datahub/test_source_capabilities.py`
  - PASS (`Ran 17 tests ... OK`)
- `python3 -m unittest -v tests/datahub/test_tushare_index_weight_history_live.py`
  - PASS for offline/default path (`Ran 3 tests ... OK (skipped=1)`)
  - default live smoke status: `SKIP` with message `Live source tests are disabled. Set QUANT_SYSTEM_LIVE_TESTS=1 to enable.`

## default network behavior

- Default test execution remained offline-safe.
- No real network call was attempted.
- The live smoke file stayed gated by `QUANT_SYSTEM_LIVE_TESTS`; with default environment it skipped before any credentialed request path.

## live-enabled PASS/SKIP/FAIL result and root-cause evidence

- `SKIP / not run by handoff; credentialed live evidence remains pending`
- Root-cause evidence:
  - this handoff explicitly forbade live-enabled execution
  - the default run confirmed the live smoke is still environment-gated and skipped when `QUANT_SYSTEM_LIVE_TESTS` is unset
  - prior prerequisite gap on local `tushare` SDK is resolved, but a credentialed `TUSHARE_TOKEN` live PASS validating at least one `INDEX_WEIGHT_HISTORY` record still does not exist

## deviations

- None.

## risks/follow-up

- `index_weight_history` remains `planned` by design.
- A future credentialed live PASS cycle is still required before this capability can move from `planned` to `partial`.
- Review should confirm the reconciled wording does not overstate live coverage and that default tests remain offline-safe.
