# TASK-062: FeatureHub Capital-Flow Primitives

## Task ID

TASK-062

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 3: FeatureHub

## Context

TASK-061 is accepted by Review and closed by the controller. It confirmed the pure offline valuation primitive slice and strengthened edge-case coverage without changing DataHub or future-phase modules.

This task opens the next narrow FeatureHub calculation slice: deterministic capital-flow primitives built only from caller-provided capital-flow-snapshot-like rows. Do not fetch data, persist output, rank securities, create scanner behavior, or introduce strategy/backtest/signal/risk/portfolio logic.

The execution window must read:

- `AGENTS.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-062_FEATUREHUB_CAPITAL_FLOW_PRIMITIVES.md`
- `quant/features/contracts.py`
- `quant/features/technical.py`
- `quant/features/valuation.py`
- `tests/features/test_contracts.py`
- `tests/features/test_technical.py`
- `tests/features/test_valuation.py`

## Goal

Add a small offline FeatureHub capital-flow module that computes validated `FeatureValueRecord` outputs from local capital-flow snapshot inputs.

## Allowed Files

The execution window may create or modify only:

- `quant/features/**`
- `tests/features/**`
- `coordination/reports/TASK-062_REPORT.md`

Suggested implementation locations:

- `quant/features/capital_flow.py`
- `quant/features/__init__.py`
- `tests/features/test_capital_flow.py`

## Forbidden Files

The execution window must not modify:

- `coordination/PROJECT_STATE.md`
- `coordination/ROADMAP.md`
- `coordination/TASK_BOARD.md`
- `coordination/DECISIONS.md`
- `coordination/RISKS.md`
- `coordination/INTERFACES.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/reviews/**`
- `coordination/integrations/**`
- `coordination/handoffs/**`
- `quant/datahub/**`
- `quant/strategies/**`
- `quant/backtest/**`
- `quant/scanner/**`
- `quant/portfolio/**`
- `quant/notification/**`
- `quant/ai/**`
- `quant/ui/**`

## Implementation Requirements

### 1. Pure local capital-flow primitives

Implement deterministic functions for caller-provided capital-flow snapshot records.

The slice should include at least:

- latest main net inflow from `main_net_inflow`
- trailing main net inflow sum over a positive integer window
- optional northbound net buy value from `northbound_net_buy` when present
- optional turnover-adjusted main net inflow from `main_net_inflow / turnover_rate` when `turnover_rate` is present and positive

Keep all calculations pure and local. Inputs may be dataclasses or mappings, but must be documented by code shape and tests. The functions must not read files, write files, import source adapters, call live sources, or depend on network access.

### 2. Feature contract output

At least one public function must emit `FeatureValueRecord` values for `FeatureName.CAPITAL_FLOW`.

Each emitted record must:

- use the input symbol, market, and trade date
- set `source_dataset` to `DatasetName.CAPITAL_FLOW_SNAPSHOT`
- use the existing FeatureHub schema version
- pass `validate_feature_value_record`

Do not change the `FeatureValueRecord` contract in this task unless unavoidable. If metric identity needs a record-level contract field, report it as a follow-up instead of widening this slice.

### 3. Input validation and edge cases

Handle edge cases deterministically:

- missing required `main_net_inflow` for required calculations
- missing optional `northbound_net_buy` or `turnover_rate` for optional calculations
- zero, non-finite, boolean, or non-numeric numeric inputs
- non-positive `turnover_rate` when turnover-adjusted flow is requested
- insufficient rows for a requested trailing window
- non-positive or non-integer window arguments
- unsorted input rows
- duplicate `trade_date` rows for the same symbol/market
- mixed symbol or market rows in one series
- timestamp-bearing `trade_date` values

The implementation may raise `ValueError` for invalid caller input. Prefer the smaller API surface.

### 4. Scope boundaries

Do not implement:

- scanner ranking, capital-flow strength classification, or candidate selection
- buy/sell signals
- strategy rules
- backtest execution
- portfolio or risk logic
- persistence/versioned storage
- feature orchestration or scheduling
- DataHub source adapters or warehouse reads
- technical, valuation, macro, announcement, AI, or notification features beyond exports needed for this module
- UI or automated trading

## Testing Requirements

Run focused tests:

`python3 -m unittest discover -s tests/features -p 'test_*.py'`

Run DataHub default regression if the implementation imports DataHub dataset identifiers directly or indirectly:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Default tests must remain offline-safe. No live tests are required or allowed for TASK-062.

## Report Requirements

Write `coordination/reports/TASK-062_REPORT.md` with:

- files changed
- tests run and results
- default network behavior
- live-enabled result as `SKIP` because TASK-062 is not a real-source task and this handoff forbids live tests
- deviations from this handoff
- risks or follow-up tasks

## Acceptance Criteria

The task is acceptable when:

- the capital-flow module imports cleanly
- deterministic offline tests cover valid calculations and invalid/edge inputs
- emitted `FeatureValueRecord` objects pass the existing contract validator
- no DataHub implementation files are changed
- no future phase modules are changed
- default tests remain free of hidden network calls
- report exists at `coordination/reports/TASK-062_REPORT.md`

## Report Path

`coordination/reports/TASK-062_REPORT.md`

## Review Path

`coordination/reviews/TASK-062_REVIEW.md`

## Integration Path

N/A until review acceptance.
