# TASK-139 Review

## Findings

1. `tests/features/test_technical.py:342`-`tests/features/test_technical.py:416` does not meet the handoff's required negative-path coverage for the new EMA and oscillator families. The handoff explicitly requires EMA tests for seed, smoothing, insufficient-row behavior, and invalid-window behavior, plus oscillator tests for insufficient history and invalid windows/ordering (`coordination/handoffs/TASK-139_FEATUREHUB_TECHNICAL_INDICATORS_CORE_EXPANSION.md:112`-`:126`). Current coverage verifies EMA seed behavior, MACD normal path plus equal-window rejection, RSI normal/edge cases, and stochastic normal/flat-range behavior, but it does not exercise EMA insufficient/invalid windows, MACD insufficient history, RSI invalid window, or stochastic insufficient/invalid windows. This leaves key validation branches in [quant/features/technical.py](/Users/chenziheng/Documents/量化分析代码/quant_system/quant/features/technical.py:90) and [quant/features/technical.py](/Users/chenziheng/Documents/量化分析代码/quant_system/quant/features/technical.py:135) unverified against the task's acceptance bar.

## Decision

Rejected pending test-completeness rework. Scope stayed inside `quant/features/**` and `tests/features/**`, the readiness update remains conservative, and the default suite is offline-safe, but the handoff-required regression coverage is still incomplete.

## Closure Status

- decision: rejected_or_blocked
- controller_closure_allowed: no
- default_tests_offline_safe: yes
- live_enabled_result: SKIP
- rework_required: yes

## Closure Readiness

- Controller may not close TASK-139 yet.
- Default tests are offline-safe.
- Live-enabled result is `SKIP` because TASK-139 is pure offline FeatureHub work; no live rework is needed.
- Rework is required to add the missing handoff-mandated negative-path tests for EMA and momentum oscillators. No phase/scope violation was found, but the current test gap is a closure blocker.

## Independent Verification

- Ran `python3 -m unittest discover -s tests/features -p 'test_*.py'`
- Result: `PASS` (`Ran 65 tests in 0.007s`)
