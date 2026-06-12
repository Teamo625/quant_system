# TASK-138 FeatureHub personal trading readiness gate

## Role

5.3 Execution Window.

## Phase

Phase 3-P FeatureHub Personal Trading Perfection Re-Review.

## Context

TASK-137 is closed after accepted Review Agent verification. It completed the residual DataHub index capability-cluster batch with default offline safety and live-enabled PASS evidence, while keeping `index_weight_history` as a separate owner accepted paid-credential blocker.

Controller closes Phase 2.5-P DataHub under the public-source/no-paid Personal Trading Perfection scope because all ordinary DataHub hardening batches have accepted reports/reviews, residual public-source limitations are explicitly recorded as conservative `warn` truth, and the only paid/private path remains blocked pending owner-provided Tushare scope. DataHub is now an upstream baseline for FeatureHub re-review, not an implementation target for this task.

FeatureHub historical tasks TASK-040 and TASK-060 through TASK-063 are foundation progress only. Under `coordination/ROADMAP.md`, FeatureHub cannot be treated as personally trading-perfect from those representative primitives alone.

## Objective

Create a deterministic FeatureHub personal trading readiness gate that audits current FeatureHub coverage against the roadmap standard and produces a Controller-ready follow-up queue and coherent follow-up batches.

This is an audit/gate task. It must not implement new indicator families or downstream workflows.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-138_FEATUREHUB_PERSONAL_TRADING_READINESS_GATE.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/ROADMAP.md`
- `coordination/PHASE_GATE.md`
- `coordination/reports/TASK-040_REPORT.md`
- `coordination/reviews/TASK-040_REVIEW.md`
- `coordination/reports/TASK-060_REPORT.md`
- `coordination/reviews/TASK-060_REVIEW.md`
- `coordination/reports/TASK-061_REPORT.md`
- `coordination/reviews/TASK-061_REVIEW.md`
- `coordination/reports/TASK-062_REPORT.md`
- `coordination/reviews/TASK-062_REVIEW.md`
- `coordination/reports/TASK-063_REPORT.md`
- `coordination/reviews/TASK-063_REVIEW.md`
- `quant/features/`
- `tests/features/`

Read DataHub contracts only if needed to understand FeatureHub input assumptions. Do not change DataHub files.

## Allowed Writes

Only:

- `quant/features/**`
- `tests/features/**`
- `coordination/reports/TASK-138_REPORT.md`

Suggested implementation locations:

- `quant/features/personal_readiness.py`
- `tests/features/test_personal_readiness.py`
- `quant/features/__init__.py` only for minimal exports if needed

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files other than `coordination/reports/TASK-138_REPORT.md`
- `coordination/reviews/**`
- `coordination/integrations/**`
- `coordination/handoffs/**`
- `quant/datahub/**`
- `tests/datahub/**`
- `quant/scanner/**`
- `quant/strategies/**`
- `quant/backtest/**`
- `quant/portfolio/**`
- `quant/notification/**`
- `quant/ai/**`
- `quant/ui/**`

Do not fetch live data, call source adapters, read browser/session state, use credentials, or introduce hidden network behavior.

## Audit Requirements

The readiness gate must classify FeatureHub against the `coordination/ROADMAP.md` FeatureHub Personal Trading Perfection Standard.

At minimum, include capability groups for:

- price/volume technical indicator core set: returns, moving averages, EMA, MACD, RSI, KDJ/stochastic, Bollinger Bands, ATR, volatility, volume/turnover/liquidity, gap/breakout primitives, and rolling helpers
- valuation features: PE/PB/PS-style values, earnings yield/book-to-price, valuation percentile or relative valuation where source history exists
- capital-flow and money-flow features: main/northbound/fund-flow levels, rolling changes, intensity/normalization, and missing-source behavior
- sector-relative and market-relative features: stock-vs-sector returns, sector strength, index-relative performance, breadth/rotation primitives where source data exists
- batch calculation APIs over caller-provided or locally refreshed data
- feature output persistence/versioning and downstream Scanner/StrategyLab consumability
- offline tests for success, missing data, window boundaries, invalid input, duplicate dates, and schema compatibility

For each group, record whether current implementation is `pass`, `warn`, `blocked`, or `fail`, with evidence based on current FeatureHub files and accepted lifecycle artifacts.

## Follow-Up Queue Requirements

The gate must expose deterministic structured follow-up items suitable for Controller dispatch.

Each follow-up item should include at least:

- stable follow-up id
- capability/group id
- status
- disposition such as `featurehub_hardening`, `contract_repair`, `owner_blocker`, or `blocked_upstream`
- reason
- recommended next handoff theme

Also expose coherent follow-up batches. Ordinary hardening batches should group 2-6 related items by FeatureHub domain/theme, for example technical indicators, valuation/capital-flow, relative/market features, batch APIs, or persistence/downstream consumability. Single-item batches are allowed only for blocker/rework/schema-risk cases and must explain why they cannot be merged.

The report must recommend the next executable FeatureHub hardening handoff after this gate. Do not dispatch it from the execution window.

## Implementation Boundaries

The task may add readiness dataclasses, enums, builders, and deterministic tests.

Do not implement:

- new technical indicators beyond existing accepted primitives
- scanner ranking or candidate selection
- strategy rules
- backtest execution
- portfolio, signal, or risk logic
- DataHub source adapters or DataHub warehouse reads
- AI reports, notifications, UI, or automated trading

## Tests

Required default tests:

- `python3 -m unittest discover -s tests/features -p 'test_*.py'`

Run narrower focused tests during development as needed.

No live tests are required or allowed. Default tests must be offline-safe.

## Completion Report

Write `coordination/reports/TASK-138_REPORT.md` with:

- files changed
- readiness model summary
- status counts and phase closure readiness
- follow-up queue and follow-up batch summary
- recommended next executable FeatureHub handoff
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled result as `SKIP` because this is local audit-only FeatureHub work
- deviations from the handoff
- risks or follow-up tasks

