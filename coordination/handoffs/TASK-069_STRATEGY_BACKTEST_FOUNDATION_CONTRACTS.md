# TASK-069: StrategyLab and BacktestEngine foundation contracts

## Role

5.3 Execution Window.

Read `AGENTS.md` first, then this handoff. Implement exactly this task and write the completion report to `coordination/reports/TASK-069_REPORT.md`.

## Context

Phase 5 is newly opened after accepted TASK-068 closure completed the Phase 4 Scanner foundation/local artifact scope.

This first Phase 5 task must establish small, importable, offline-only foundation contracts for StrategyLab and BacktestEngine. It must not implement concrete strategy logic, stock-picking decisions, scanner ranking, historical replay execution, portfolio/signal/risk logic, AI reports, notification, UI, automated trading, live data access, warehouse reads, or DataHub/FeatureHub source adapters.

## Allowed Files

You may create or modify only:

- `quant/strategies/README.md`
- `quant/strategies/__init__.py`
- `quant/strategies/contracts.py`
- `quant/backtest/README.md`
- `quant/backtest/__init__.py`
- `quant/backtest/contracts.py`
- `tests/strategies/__init__.py`
- `tests/strategies/test_contracts.py`
- `tests/backtest/__init__.py`
- `tests/backtest/test_contracts.py`
- `coordination/reports/TASK-069_REPORT.md`

Do not edit controller-owned coordination state files.

## Requirements

### StrategyLab contracts

- Add importable contract primitives under `quant/strategies/` for describing strategy research definitions without executing them.
- Include stable identifiers and validation for at least:
  - strategy id/name
  - strategy version
  - declared input feature names
  - declared parameter definitions with type metadata and optional default/min/max/choices where appropriate
  - declared output intent or signal-kind metadata
- Validation must reject empty identifiers, duplicate feature names, duplicate parameter names, unsupported parameter type declarations, and inconsistent parameter constraints.
- Keep the contracts deterministic and pure Python. No network, no filesystem reads, no DataHub/FeatureHub reads, and no scanner execution.

### BacktestEngine contracts

- Add importable contract primitives under `quant/backtest/` for describing backtest requests/configuration and result summaries without running historical replay.
- Include stable identifiers and validation for at least:
  - backtest request id
  - strategy id/version reference
  - universe or candidate-list reference metadata
  - start/end trade-date boundaries
  - starting capital
  - basic cost/slippage assumptions as declared configuration values only
  - result summary metadata placeholders
- Validation must reject empty identifiers, invalid date ordering, non-positive starting capital, negative cost/slippage values, and missing strategy references.
- Keep this task contract-only. Do not simulate trades, load market data, compute returns, produce reports, or persist artifacts.

### Package exports and docs

- Add package exports in `__init__.py` files for the new contracts.
- Update README files so they no longer say the modules are unopened placeholders. The wording must still state the current scope is foundation contracts only.

## Tests

Add focused offline unit tests for the new contracts.

Allowed test commands:

- `python3 -m unittest discover -s tests/strategies -p 'test_*.py'`
- `python3 -m unittest discover -s tests/backtest -p 'test_*.py'`
- Optional broader offline regression if useful: `python3 -m unittest discover -s tests -p 'test_*.py'`

Do not run live-enabled tests. Do not add live tests.

## Completion Report

Write `coordination/reports/TASK-069_REPORT.md` with:

- files changed
- tests run and results
- default network behavior
- live-enabled result: `SKIP` because live tests are forbidden for this task
- deviations from this handoff, if any
- risks or follow-up tasks
