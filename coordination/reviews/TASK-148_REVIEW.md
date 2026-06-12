# TASK-148 Review

## Findings

- High: `validate_repeatable_experiment_config()` does not verify that `experiment_id` still matches normalized content. In [quant/backtest/experiments.py](/Users/chenziheng/Documents/量化分析代码/quant_system/quant/backtest/experiments.py:231) validation checks date window, capital/cost/slippage, schema version, and `parameter_set_id`, but it never recomputes or compares `experiment_id`. I built a valid config, changed `transaction_cost_bps`, replaced `experiment_id` with `stale-id`, and `validate_repeatable_experiment_config()` returned no issues. That breaks the handoff requirement for deterministic experiment/run identity from normalized content and allows materially different runs to pass under the same id. Coverage in [tests/backtest/test_experiments.py](/Users/chenziheng/Documents/量化分析代码/quant_system/tests/backtest/test_experiments.py:22) proves build-time determinism only; it does not guard stale-id rejection.

- Medium: starter strategy metadata is not contract-truthful about output intent. Both definitions declare `output_intent=SignalIntent.ENTRY` in [quant/strategies/rules.py](/Users/chenziheng/Documents/量化分析代码/quant_system/quant/strategies/rules.py:93), but the evaluators emit `exit_long` signals in the same module at [quant/strategies/rules.py](/Users/chenziheng/Documents/量化分析代码/quant_system/quant/strategies/rules.py:352) and [quant/strategies/rules.py](/Users/chenziheng/Documents/量化分析代码/quant_system/quant/strategies/rules.py:389). The tests in [tests/strategies/test_rules.py](/Users/chenziheng/Documents/量化分析代码/quant_system/tests/strategies/test_rules.py:67) assert exit outputs, but there is no assertion that definition metadata matches emitted signal semantics. Downstream consumers relying on declared `output_intent` will get misleading contract metadata.

## Closure Status

- decision: rejected_or_blocked
- controller_closure_allowed: no
- default_tests_offline_safe: yes
- live_enabled_result: SKIP
- rework_required: yes

## Closure Readiness

- Controller closure is not allowed yet; a rework is required to enforce experiment-id/content consistency and to make starter strategy output metadata truthful.
- Default tests are offline-safe. I reran `python3 -m unittest discover -s tests/strategies -p 'test_*.py'` and `python3 -m unittest discover -s tests/backtest -p 'test_*.py'`, both PASS.
- Live-enabled result is `SKIP` because this handoff is local/offline only; no live tests were required or allowed.
- There are current contract/test blockers, but no phase-scope violation and no hidden network behavior found in the reviewed changes.
