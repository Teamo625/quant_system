# TASK-096 Review

## Findings

- Blocking: [tests/datahub/test_baostock_a_share_minute_bars_live.py](/Users/chenziheng/Documents/量化分析代码/quant_system/tests/datahub/test_baostock_a_share_minute_bars_live.py:43) includes `"baostock"` in the generic network token list and then treats any matching exception message as environment-unavailable at [tests/datahub/test_baostock_a_share_minute_bars_live.py](/Users/chenziheng/Documents/量化分析代码/quant_system/tests/datahub/test_baostock_a_share_minute_bars_live.py:76). That causes BaoStock-labeled contract/data failures to be skipped instead of failed in the live smoke path at [tests/datahub/test_baostock_a_share_minute_bars_live.py](/Users/chenziheng/Documents/量化分析代码/quant_system/tests/datahub/test_baostock_a_share_minute_bars_live.py:124). I independently verified `_is_live_environment_unavailable(ValueError("Invalid BaoStock date value: bad")) == True` and `_is_live_environment_unavailable(ValueError("Source symbol mismatch for BaoStock A-share minute-bars adapter")) == True`. This makes the reported BaoStock live PASS in [coordination/reports/TASK-096_REPORT.md](/Users/chenziheng/Documents/量化分析代码/quant_system/coordination/reports/TASK-096_REPORT.md:29) non-closure-safe because future contract regressions can be silently downgraded to `SKIP`.

## Decision

Rejected. Controller closure is not allowed until the live smoke classifier distinguishes actual network/environment failures from BaoStock-specific contract/data errors.

## Closure Readiness

- Controller closure allowed: No
- Default tests offline-safe: Yes. I independently verified `python3 -m unittest tests/datahub/test_baostock_a_share_minute_bars_adapter.py`, `python3 -m unittest tests/datahub/test_source_capabilities.py`, and `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_baostock_a_share_minute_bars_live.py`; the live file remained default-skipped.
- Live-enabled result: PASS reported for BaoStock in the execution report, but not closure-sufficient. Rework required: Yes, because the current skip classifier can misclassify BaoStock contract/data failures as environment-unavailable `SKIP`.
- Phase/scope/contract/test blockers: Yes. Scope is acceptable and capability truth remains `partial`, but there is a test-truthfulness blocker in the BaoStock live smoke classifier.

## Required Follow-up

- Narrow the BaoStock live-environment classifier so only real network/proxy/DNS/TLS/upstream availability failures skip; BaoStock-specific normalization, schema, symbol, or other contract/data errors must fail the live test.
