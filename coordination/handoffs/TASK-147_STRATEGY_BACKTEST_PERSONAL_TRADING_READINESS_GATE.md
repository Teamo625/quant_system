# TASK-147 StrategyLab and BacktestEngine personal trading readiness gate

## Role

5.3 Execution Window.

## Phase

Phase 5 StrategyLab and BacktestEngine Personal Trading Perfection.

## Context

TASK-070 is closed after accepted Review Agent verification of the focused BacktestEngine replay side-coercion rework. The rework fixed replay execution for `TradeIntent.side` values accepted by contract validation, including caller-provided `"buy"` and `"sell"` strings, kept default tests offline-safe, and required no live evidence because Phase 5 replay work is local/offline over caller-provided data.

Phase 5 remains incomplete under `coordination/ROADMAP.md` and `coordination/PHASE_GATE.md`. TASK-069 and TASK-070 provide useful foundation contracts and a deterministic historical replay primitive, but they do not yet prove concrete strategy rule evaluation, an owner-approved starter strategy library, parameterized experiment repeatability, cost/slippage/calendar assumption depth, decision-quality metrics/reports, multi-configuration comparison, or full reproducibility coverage.

## Objective

Create a deterministic StrategyLab and BacktestEngine personal trading readiness gate that audits current Phase 5 coverage against the roadmap standard and produces a Controller-ready follow-up queue and coherent follow-up batches.

This is an audit/gate task. It must not implement new strategy rules, starter strategies, cost/slippage models, metrics, reports, persistence, or comparison workflows.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-147_STRATEGY_BACKTEST_PERSONAL_TRADING_READINESS_GATE.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/ROADMAP.md`
- `coordination/PHASE_GATE.md`
- `coordination/reports/TASK-069_REPORT.md`
- `coordination/reviews/TASK-069_REVIEW.md`
- `coordination/reports/TASK-070_REPORT.md`
- `coordination/reviews/TASK-070_REVIEW.md`
- `quant/strategies/`
- `quant/backtest/`
- `tests/strategies/`
- `tests/backtest/`

Read Scanner/FeatureHub contracts only if needed to understand approved caller-provided input assumptions. Do not change Scanner, FeatureHub, or DataHub files.

## Allowed Writes

Only:

- `quant/strategies/**`
- `quant/backtest/**`
- `tests/strategies/**`
- `tests/backtest/**`
- `coordination/reports/TASK-147_REPORT.md`

Suggested implementation locations:

- `quant/backtest/personal_readiness.py` or a similarly named Phase 5 readiness module
- `tests/backtest/test_personal_readiness.py` and/or `tests/strategies/test_personal_readiness.py`
- `quant/backtest/__init__.py` / `quant/strategies/__init__.py` only for minimal exports if needed

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files other than `coordination/reports/TASK-147_REPORT.md`
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

## Audit Requirements

The readiness gate must classify StrategyLab and BacktestEngine against the `coordination/ROADMAP.md` Phase 5 Personal Trading Perfection Standard.

At minimum, include capability groups for:

- strategy definition contracts, concrete strategy rule evaluation, and an owner-approved starter strategy library
- parameter metadata, validation, versioning, and repeatable experiment configuration
- deterministic historical replay over caller-provided or approved local market data
- cost, slippage, cash, position, fill, and market-calendar assumptions documented and test-covered
- backtest result summaries, performance metrics, drawdown/risk metrics, and report-ready outputs
- comparing multiple strategy configurations without hidden live data or manual data patching
- offline tests for invalid configs, date boundaries, missing bars, corporate-action/source assumptions where applicable, and reproducibility

For each group, record whether current implementation is `pass`, `warn`, `blocked`, or `fail`, with evidence based on current StrategyLab/BacktestEngine files and accepted lifecycle artifacts.

## Follow-Up Queue Requirements

The gate must expose deterministic structured follow-up items suitable for Controller dispatch.

Each follow-up item should include at least:

- stable follow-up id
- capability/group id
- status
- disposition such as `strategy_backtest_hardening`, `contract_repair`, `owner_blocker`, or `blocked_upstream`
- reason
- recommended next handoff theme

Also expose coherent follow-up batches. Ordinary hardening batches should group 2-6 related items by Phase 5 domain/theme, such as strategy rule/starter-library hardening, experiment parameter/versioning, replay assumptions, performance metrics/report outputs, comparison workflows, or reproducibility regression coverage. Single-item batches are allowed only for Review rework, blocker disposition, schema/contract compatibility risk, or when no adjacent unresolved item remains.

The report must recommend the next executable Phase 5 hardening handoff after this gate. Do not dispatch it from the execution window.

## Implementation Boundaries

The task may add readiness dataclasses, enums, builders, exports, and deterministic tests.

Do not implement:

- concrete strategy signal generation or stock-picking rules
- starter strategy library behavior
- new cost, slippage, calendar, or corporate-action replay behavior
- new performance metric or report generation behavior
- multi-configuration experiment comparison
- Scanner ranking or candidate generation
- portfolio, signal, or risk logic
- DataHub source adapters, FeatureHub calculations, or local warehouse reads
- AI reports, notifications, UI, or automated trading

## Tests

Required default tests:

- `python3 -m unittest discover -s tests/strategies -p 'test_*.py'`
- `python3 -m unittest discover -s tests/backtest -p 'test_*.py'`

Run narrower focused tests during development as needed. A broader `python3 -m unittest discover -s tests -p 'test_*.py'` run is allowed if useful and must remain offline-safe.

No live tests are required or allowed. Default tests must be offline-safe.

## Completion Report

Write `coordination/reports/TASK-147_REPORT.md` with:

- files changed
- readiness model summary
- status counts and phase closure readiness
- follow-up queue and follow-up batch summary
- recommended next executable Phase 5 handoff
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled result as `SKIP` because this is local audit-only StrategyLab/BacktestEngine work
- deviations from the handoff
- risks or follow-up tasks
