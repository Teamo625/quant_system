# TASK-070: BacktestEngine historical replay primitives

## Role

5.3 Execution Window.

Read `AGENTS.md` first, then this handoff. Implement exactly this task and write the completion report to `coordination/reports/TASK-070_REPORT.md`.

## Context

TASK-069 established pure offline StrategyLab and BacktestEngine foundation contracts. Phase 5 remains open because historical replay, cost/slippage assumptions, and backtest reports are not complete.

Controller re-dispatch note: this handoff was previously deferred while DataHub, FeatureHub, and Scanner were re-reviewed under the Personal Trading Perfection Standard. It is now the Active Phase 5 handoff again after accepted public-source/no-paid closure of Phase 2.5-P DataHub, Phase 3-P FeatureHub, and Phase 4-P Scanner.

This handoff explicitly opens the first BacktestEngine historical replay sub-scope. The implementation must remain local and deterministic. It may replay caller-provided market bars and caller-provided dated trade intents, but it must not generate strategy decisions, rank candidates, read persisted FeatureHub/Scanner/DataHub artifacts, fetch live data, or implement production portfolio/signal/risk modules.

## Allowed Files

You may create or modify only:

- `quant/backtest/README.md`
- `quant/backtest/__init__.py`
- `quant/backtest/contracts.py`
- `quant/backtest/replay.py`
- `tests/backtest/__init__.py`
- `tests/backtest/test_contracts.py`
- `tests/backtest/test_replay.py`
- `coordination/reports/TASK-070_REPORT.md`

Do not edit controller-owned coordination state files.

## Requirements

### Replay input primitives

- Add importable BacktestEngine primitives for caller-provided replay inputs.
- Include stable dataclasses or equivalent structured contracts for at least:
  - market bar records keyed by symbol and trade date
  - dated trade intents or orders supplied by the caller
  - replay configuration derived from or compatible with `BacktestRequest`
  - per-date portfolio/equity snapshots produced by replay
  - final replay summary metrics needed by later reporting work
- Validation must reject empty symbols, invalid ISO trade dates, invalid date ordering, non-positive prices, negative volumes where volume is provided, non-finite quantities, and trade intents outside the configured replay date range.

### Historical replay behavior

- Implement a deterministic offline replay function over caller-provided bars and caller-provided trade intents.
- The replay must:
  - process dates in ascending trade-date order
  - maintain cash, positions, realized/unrealized value, and total equity for the simulated account
  - apply configured transaction cost and slippage values from the backtest request/configuration
  - reject or report intents whose symbol/date has no usable market bar
  - return structured snapshots and a summary without writing files
- Keep the behavior intentionally simple and documented. This is a foundation primitive, not a production execution simulator.

### Scope boundaries

- Do not implement concrete trading strategies or strategy signal generation.
- Do not implement scanner ranking, stock-picking, or candidate-list generation.
- Do not read from or write to DataHub, FeatureHub, Scanner, warehouse, or artifact directories.
- Do not implement production PortfolioMonitor, SignalEngine, RiskEngine, AI, notification, UI, automated trading, scheduling, persistence, or report generation.
- Do not add live data access, live tests, credentials, or network calls.

## Tests

Add focused offline unit tests for the replay primitives.

Required test commands:

- `python3 -m unittest discover -s tests/backtest -p 'test_*.py'`
- `python3 -m unittest discover -s tests -p 'test_*.py'`

Do not run live-enabled tests. Do not add live tests.

## Completion Report

Write `coordination/reports/TASK-070_REPORT.md` with:

- files changed
- tests run and results
- default network behavior
- live-enabled result: `SKIP` because live tests are forbidden for this task
- deviations from this handoff, if any
- risks or follow-up tasks
