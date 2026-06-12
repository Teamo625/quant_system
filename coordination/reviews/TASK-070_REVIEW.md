# TASK-070 Review

## Findings

1. High: valid caller-provided `TradeIntent.side` strings are accepted by contract validation but mis-executed by the replay engine. `validate_trade_intent()` explicitly accepts `"buy"` / `"sell"` via `_coerce_trade_side()` in [quant/backtest/contracts.py](/Users/chenziheng/Documents/量化分析代码/quant_system/quant/backtest/contracts.py:589), but `run_historical_replay()` dispatches with `trade_intent.side is TradeSide.BUY` in [quant/backtest/replay.py](/Users/chenziheng/Documents/量化分析代码/quant_system/quant/backtest/replay.py:102). Independent repro with `TradeIntent(side="buy")` passed validation and was rejected as `insufficient_position` instead of executing a buy. The current tests in [tests/backtest/test_replay.py](/Users/chenziheng/Documents/量化分析代码/quant_system/tests/backtest/test_replay.py:17) only cover enum instances, so this contract/behavior mismatch is unguarded.

## Closure Status

- decision: rejected_or_blocked
- controller_closure_allowed: no
- default_tests_offline_safe: yes
- live_enabled_result: SKIP
- rework_required: yes

## Closure Readiness

- Controller closure is not allowed yet; replay side handling needs execution rework and a regression test.
- Default tests are offline-safe. Independent review reran `python3 -m unittest discover -s tests/backtest -p 'test_*.py'` and `python3 -m unittest discover -s tests -p 'test_*.py'`, both PASS.
- Live-enabled result is `SKIP` as required by the handoff; no live test was added or run.
- Blocking items remain in the replay contract/execution path. No phase-scope violation was found, but the current implementation does not yet safely satisfy the replay input contract.
