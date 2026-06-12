# TASK-148 Strategy starter library and repeatable experiment configuration hardening

## Role

5.3 Execution Window.

## Phase

Phase 5 StrategyLab and BacktestEngine Personal Trading Perfection.

## Context

TASK-147 is closed after accepted Review Agent verification of the local/offline StrategyLab and BacktestEngine readiness gate. The gate reports `phase_closure_ready=false`, status counts `pass=1`, `warn=6`, `blocked=0`, `fail=0`, and three coherent follow-up batches.

Controller read the TASK-147 readiness `follow_up_batches`. The first executable current-phase capability cluster is:

- batch id: `strategy_backtest__personal_trading_hardening__batch_01`
- theme: starter strategy rules and repeatable experiment configuration hardening
- follow-up items:
  - `phase5__strategy_definition_and_starter_library`
  - `phase5__parameter_versioning_and_experiment_config`

This is a two-item coherent Phase 5 cluster. It is dispatched together because executable starter strategy rules and repeatable experiment configuration identity must agree on strategy ids, parameter metadata, parameter-set versioning, and deterministic run inputs.

## Objective

Move StrategyLab beyond contract-only definitions by adding deterministic offline starter strategy rule evaluation and repeatable experiment configuration contracts.

The implementation must remain local/offline over caller-provided market/feature rows and explicit configuration objects. It must not fetch data, read the warehouse, create live trading signals, or implement portfolio/signal/risk modules.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-148_STRATEGY_STARTER_EXPERIMENT_CONFIG_HARDENING.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/ROADMAP.md`
- `coordination/PHASE_GATE.md`
- `coordination/reports/TASK-147_REPORT.md`
- `coordination/reviews/TASK-147_REVIEW.md`
- `quant/strategies/`
- `quant/backtest/`
- `tests/strategies/`
- `tests/backtest/`

Read Scanner/FeatureHub contracts only if needed to preserve caller-provided input assumptions. Do not change Scanner, FeatureHub, or DataHub files.

## Allowed Writes

Only:

- `quant/strategies/**`
- `quant/backtest/**`
- `tests/strategies/**`
- `tests/backtest/**`
- `coordination/reports/TASK-148_REPORT.md`

Suggested implementation locations:

- `quant/strategies/rules.py` or similarly scoped module for deterministic starter strategy evaluation
- `quant/backtest/experiments.py` or similarly scoped module for repeatable experiment configuration identity
- focused exports in `quant/strategies/__init__.py` and `quant/backtest/__init__.py` if needed
- focused tests under `tests/strategies/` and `tests/backtest/`

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files other than `coordination/reports/TASK-148_REPORT.md`
- `coordination/reviews/**`
- `coordination/integrations/**`
- `coordination/handoffs/**`
- `quant/datahub/**`
- `tests/datahub/**`
- `quant/features/**`
- `tests/features/**`
- `quant/scanner/**`
- `tests/scanner/**`
- `quant/portfolio/**`
- `quant/notification/**`
- `quant/ai/**`
- `quant/ui/**`

Do not fetch live data, call source adapters, read local warehouse state, use credentials, operate browser/session state, or introduce hidden network behavior.

Do not implement production portfolio/signal/risk logic, live execution, AI reports, notifications, automated trading, or UI.

## Implementation Requirements

### Starter Strategy Library

Add a small deterministic offline starter strategy library suitable for personal research baselines.

At minimum:

- define stable starter strategy identifiers, names, versions, required input fields, output intent, and parameter metadata
- provide at least two concrete starter rule evaluators with distinct practical behavior, such as trend/moving-average crossover and mean-reversion/RSI-style entry/exit logic
- accept only caller-provided ordered market/feature rows or mappings; do not import FeatureHub calculations or fetch source data
- emit deterministic strategy outputs suitable for downstream replay preparation, such as dated entry/exit intents, scores, or signal rows with explicit strategy id/version and parameter-set identity
- validate missing required inputs, duplicate dates where relevant, invalid parameter overrides, unsupported strategy ids, and empty inputs through controlled exceptions or structured issues
- keep behavior stable and simple enough for offline unit tests; avoid optimizing strategy profitability or making stock-picking claims

### Repeatable Experiment Configuration

Add first-class repeatable experiment configuration contracts.

At minimum:

- bind a strategy reference, validated parameter set, selection/input reference, replay date window, starting capital, transaction cost/slippage assumptions, and schema version
- create a deterministic experiment/run identity or digest from normalized content
- preserve parameter-set versioning and strategy versioning
- support serialization-friendly normalized output for repeated runs
- reject invalid date windows, non-finite capital/cost/slippage values, unknown strategy parameters, type mismatches, out-of-range values, and choices violations
- avoid reading Scanner artifacts, DataHub warehouse files, FeatureHub outputs, or any external state; references must remain metadata only

## Readiness Update

If this task completes the selected TASK-147 batch, update the local Phase 5 readiness gate metadata where appropriate so the two covered groups no longer overstate unresolved starter strategy or repeatable experiment gaps.

Do not mark Phase 5 closure-ready unless every remaining TASK-147 follow-up batch is also complete and the readiness gate truthfully reports no unresolved `warn`, `blocked`, or `fail` items.

## Tests

Required default tests:

- `python3 -m unittest discover -s tests/strategies -p 'test_*.py'`
- `python3 -m unittest discover -s tests/backtest -p 'test_*.py'`

Add focused tests for:

- starter library exports and definitions
- deterministic rule evaluation on caller-provided rows
- invalid/missing input behavior
- parameter override validation and parameter-set identity
- experiment configuration normalization and reproducibility
- no hidden network or warehouse dependency

A broader `python3 -m unittest discover -s tests -p 'test_*.py'` run is allowed if useful and must remain offline-safe.

No live tests are required or allowed. Default tests must be offline-safe.

## Completion Report

Write `coordination/reports/TASK-148_REPORT.md` with:

- files changed
- starter strategies and experiment configuration capabilities added
- readiness gate updates, if any
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled result as `SKIP` because this is local/offline StrategyLab/BacktestEngine work
- deviations from the handoff
- risks or follow-up tasks
