# TASK-148 Report

## files changed

- `quant/backtest/experiments.py`
- `quant/strategies/contracts.py`
- `quant/strategies/rules.py`
- `tests/backtest/test_experiments.py`
- `tests/strategies/test_rules.py`

## review blockers addressed

- `experiment_id` truth:
  - extracted one shared normalized identity payload path for experiment-id hashing
  - `build_repeatable_experiment_config()` and validation now use the same normalized content rules
  - `validate_repeatable_experiment_config()` now rejects stale or mismatched `experiment_id` with `experiment_id_mismatch` when the rest of the config is otherwise valid
- starter output metadata truth:
  - added `SignalIntent.ENTRY_EXIT`
  - updated `ma_crossover_long` and `rsi_mean_reversion_long` definitions to declare entry+exit output semantics without removing `exit_long` behavior
  - added tests that assert declared metadata matches observed `enter_long` / `exit_long` emissions

## tests run

- `python3 -m unittest discover -s tests/strategies -p 'test_*.py'` -> PASS (`Ran 14 tests`)
- `python3 -m unittest discover -s tests/backtest -p 'test_*.py'` -> PASS (`Ran 26 tests`)

## default network behavior

- Offline-safe only.
- No network calls, source-adapter calls, credentials, warehouse reads, or hidden IO were added.
- Experiment validation and starter strategy evaluation remain local over caller-provided config/rows only.

## live-enabled PASS/SKIP/FAIL result and root-cause evidence

- `SKIP`
- Root cause / evidence: this handoff is local/offline StrategyLab and BacktestEngine rework only; no live test was required or allowed.

## deviations

- None.

## risks/follow-up

- `SignalIntent.ENTRY_EXIT` is a minimal contract extension for starter metadata truth only; downstream consumers should treat it as a dual entry/exit declarative intent, not a broader execution-model change.
- Phase 5 remains open. This rework does not address replay assumptions, market rules, metrics/report outputs, multi-configuration comparison, or broader reproducibility coverage.
