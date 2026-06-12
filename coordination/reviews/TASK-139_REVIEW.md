# TASK-139 Review

## Findings

1. `MACD` invalid-window coverage is still incomplete, so the rework does not fully satisfy the handoff. `calculate_macd()` validates `short_window`, `long_window`, and `signal_window` independently in [quant/features/technical.py](/Users/chenziheng/Documents/量化分析代码/quant_system/quant/features/technical.py:671), but the added regression only exercises `short_window=0` and `signal_window=0` in [tests/features/test_technical.py](/Users/chenziheng/Documents/量化分析代码/quant_system/tests/features/test_technical.py:384). The handoff required MACD coverage for invalid window values beyond ordering, and the `long_window` invalid branch remains untested. The updated report also overstates this item as fully addressed.

## Decision

Rejected pending one more focused test rework.

## Closure Status

- decision: rejected_or_blocked
- controller_closure_allowed: no
- default_tests_offline_safe: yes
- live_enabled_result: SKIP
- rework_required: yes

## Closure Readiness

- Controller may not close TASK-139 yet.
- Default tests are offline-safe.
- Live-enabled result is `SKIP`; this is pure offline FeatureHub work, so no live rework is needed.
- Blocking item remains in test completeness: add the missing `MACD long_window` invalid-value regression and update the report accordingly. No phase or scope violation was found.

## Independent Verification

- Ran `python3 -m unittest discover -s tests/features -p 'test_*.py'`
- Result: `PASS` (`Ran 70 tests in 0.007s`)
