# TASK-148 Strategy experiment contract truth rework

## Role

5.3 Execution Window.

## Phase

Phase 5 StrategyLab and BacktestEngine Personal Trading Perfection.

## Context

TASK-148 initial Review rejected Controller closure.

Review findings:

- `validate_repeatable_experiment_config()` validates dates, capital/cost/slippage, schema version, and `parameter_set_id`, but it does not recompute and compare `experiment_id` against normalized configuration content. A materially changed config can pass validation with a stale id.
- Starter strategy definitions declare `output_intent=SignalIntent.ENTRY`, while both starter evaluators emit both `enter_long` and `exit_long` signals. This makes starter strategy metadata contract-untruthful for downstream consumers.

This is a focused Review rework. It must not be merged with Phase 5 readiness `follow_up_batches`, ordinary hardening items, replay assumptions, metrics/report output work, multi-configuration comparison, or reproducibility expansion.

## Objective

Fix only the two Review blockers:

1. Enforce deterministic experiment identity consistency during repeatable experiment config validation.
2. Make starter strategy output-intent metadata truthful for strategies that can emit both entry and exit outputs.

The task remains local/offline over caller-provided rows and explicit metadata/configuration only.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-148_STRATEGY_EXPERIMENT_CONTRACT_TRUTH_REWORK.md`
- `coordination/reviews/TASK-148_REVIEW.md`
- `coordination/reports/TASK-148_REPORT.md`
- `quant/backtest/experiments.py`
- `quant/strategies/rules.py`
- focused related strategy/backtest contract/export files only if needed for the two Review findings
- focused existing tests under `tests/strategies/` and `tests/backtest/`

Do not read `coordination/agent_runs/**`.

## Allowed Writes

Only:

- `quant/backtest/experiments.py`
- `tests/backtest/test_experiments.py`
- `quant/strategies/rules.py`
- `quant/strategies/contracts.py` only if the minimal truthful output-intent fix requires a contract enum/schema update
- `quant/strategies/__init__.py` only if required by a minimal contract/export update
- `tests/strategies/test_rules.py`
- `coordination/reports/TASK-148_REPORT.md`

If implementation proves a listed optional file is unnecessary, leave it unchanged.

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

Do not fetch live data, call source adapters, read warehouse state, use credentials, or introduce hidden network behavior.

Do not implement production portfolio/signal/risk logic, live execution, AI reports, notifications, automated trading, UI, metrics/reporting, multi-configuration comparison, or broader replay assumption work.

## Implementation Requirements

### Experiment identity validation

`validate_repeatable_experiment_config()` must reject stale or mismatched `experiment_id` values by recomputing the expected id from normalized experiment content.

At minimum:

- compute the expected id from the same normalized content rules used by `build_repeatable_experiment_config()`
- exclude the existing `experiment_id` value from the digest input
- report a deterministic validation issue when `experiment_id` is missing, empty, stale, or mismatched
- preserve existing validation for `parameter_set_id`, strategy version, parameters, date windows, capital, transaction cost, slippage, schema version, and backtest request compatibility
- add regression coverage proving a valid config fails validation after changing material content while keeping a stale id

### Starter output metadata truth

Starter strategy metadata must truthfully describe emitted signal semantics.

At minimum:

- do not remove legitimate `exit_long` behavior merely to match the old metadata
- make definitions for `ma_crossover_long` and `rsi_mean_reversion_long` accurately indicate that they may emit both entry and exit outputs
- keep strategy ids and versions stable unless a version bump is necessary for the chosen minimal contract fix
- add focused tests asserting strategy definition metadata is compatible with observed `enter_long` and `exit_long` outputs
- preserve deterministic offline evaluation over caller-provided rows

## Tests

Required default tests:

- `python3 -m unittest discover -s tests/strategies -p 'test_*.py'`
- `python3 -m unittest discover -s tests/backtest -p 'test_*.py'`

Add or update focused tests for:

- stale/mismatched `experiment_id` rejection after material normalized-content changes
- unchanged valid config still validates cleanly
- starter definition output metadata matches entry/exit signal semantics

A broader `python3 -m unittest discover -s tests -p 'test_*.py'` run is allowed if useful and must remain offline-safe.

No live tests are required or allowed. Live-enabled result must remain `SKIP` because this is local/offline StrategyLab/BacktestEngine work.

## Completion Report

Update `coordination/reports/TASK-148_REPORT.md` with:

- files changed
- how each Review finding was addressed
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled result as `SKIP`
- deviations from this rework handoff
- remaining risks or follow-up tasks

Do not claim TASK-148 or Phase 5 closure. Controller closure requires a fresh Review Agent acceptance after this rework.
