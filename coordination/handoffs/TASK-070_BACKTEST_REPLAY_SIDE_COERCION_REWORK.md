# TASK-070 Rework: Backtest replay side coercion

## Role

5.3 Execution Window.

Read `AGENTS.md` first, then this handoff. Implement exactly this rework and write the completion report to `coordination/reports/TASK-070_REPORT.md`.

## Context

The Review Agent rejected the current TASK-070 result because the replay contract accepts caller-provided `TradeIntent.side` strings such as `"buy"` / `"sell"`, but the replay engine dispatches using enum identity. As a result, a validated `TradeIntent(side="buy")` can be routed through the non-buy path and rejected as `insufficient_position` instead of executing a buy.

This is a focused Review rework. Do not combine it with ordinary Phase 5 hardening, report expansion, metrics work, strategy logic, or readiness follow-up batches.

## Allowed Files

You may create or modify only:

- `quant/backtest/contracts.py`
- `quant/backtest/replay.py`
- `tests/backtest/test_contracts.py`
- `tests/backtest/test_replay.py`
- `coordination/reports/TASK-070_REPORT.md`

Do not edit controller-owned coordination state files.

## Required Fix

- Ensure `run_historical_replay()` uses the same side semantics accepted by the `TradeIntent` contract validation.
- A caller-provided side string accepted by validation, including at least `"buy"` and `"sell"`, must execute identically to the corresponding `TradeSide` enum value.
- Preserve existing invalid-side rejection behavior. Do not silently accept side values outside the current contract.
- Keep the replay primitive deterministic and offline-only.

## Required Regression Coverage

Add focused offline unit coverage proving:

- `TradeIntent(side="buy")` validates and executes as a buy in replay.
- `TradeIntent(side="sell")` validates and executes as a sell in replay when sufficient position exists.
- The regression would fail if replay branches on enum identity without coercing or otherwise normalizing accepted string sides.

## Scope Boundaries

- Do not implement concrete strategy generation, scanner ranking, stock-picking, candidate-list generation, report generation, persistence, scheduling, live data, credentials, or network calls.
- Do not read from or write to DataHub, FeatureHub, Scanner, warehouse, artifact directories, portfolio/signal/risk modules, AI, notification, UI, or automated trading code.
- Do not expand this rework into broader cost/slippage, calendar, corporate-action, metric, or report hardening.

## Tests

Run only offline tests:

- `python3 -m unittest discover -s tests/backtest -p 'test_*.py'`
- `python3 -m unittest discover -s tests -p 'test_*.py'`

Do not run live-enabled tests. Do not add live tests.

## Completion Report

Update `coordination/reports/TASK-070_REPORT.md` with:

- files changed
- tests run and results
- default network behavior
- live-enabled result: `SKIP` because live tests are forbidden for this task
- deviations from this rework handoff, if any
- risks or follow-up tasks
