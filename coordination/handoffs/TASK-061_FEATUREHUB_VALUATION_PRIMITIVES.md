# TASK-061: FeatureHub Valuation Primitives

## Task ID

TASK-061

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 3: FeatureHub

## Context

TASK-060 is accepted by Review and closed by the controller. It added pure offline price technical primitives and `FeatureValueRecord` builders under `FeatureName.PRICE_TECHNICAL`.

This task opens the next narrow FeatureHub calculation slice: deterministic valuation primitives built only from caller-provided valuation-snapshot-like rows. Do not fetch data, persist output, rank securities, create scanner behavior, or introduce strategy/backtest/signal/risk/portfolio logic.

The execution window must read:

- `AGENTS.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-061_FEATUREHUB_VALUATION_PRIMITIVES.md`
- `quant/features/contracts.py`
- `quant/features/technical.py`
- `tests/features/test_contracts.py`
- `tests/features/test_technical.py`

## Goal

Add a small offline FeatureHub valuation module that computes validated valuation `FeatureValueRecord` outputs from local valuation snapshot inputs.

## Allowed Files

The execution window may create or modify only:

- `quant/features/**`
- `tests/features/**`
- `coordination/reports/TASK-061_REPORT.md`

Suggested implementation locations:

- `quant/features/valuation.py`
- `quant/features/__init__.py`
- `tests/features/test_valuation.py`

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

### 1. Pure local valuation primitives

Implement deterministic functions for caller-provided valuation snapshot records.

The slice should include at least:

- earnings yield from `pe_ttm`
- book-to-price from `pb`
- optional float-market-cap ratio from `float_market_cap / market_cap` when both inputs are present

Keep all calculations pure and local. Inputs may be dataclasses or mappings, but must be documented by code shape and tests. The functions must not read files, write files, import source adapters, call live sources, or depend on network access.

### 2. Feature contract output

At least one public function must emit `FeatureValueRecord` values for `FeatureName.VALUATION`.

Each emitted record must:

- use the input symbol, market, and trade date
- set `source_dataset` to `DatasetName.VALUATION_SNAPSHOT`
- use the existing FeatureHub schema version
- pass `validate_feature_value_record`

Do not change the `FeatureValueRecord` contract in this task unless unavoidable. If metric identity needs a record-level contract field, report it as a follow-up instead of widening this slice.

### 3. Input validation and edge cases

Handle edge cases deterministically:

- missing required valuation fields for a requested calculation
- zero, non-finite, boolean, or non-numeric ratio inputs
- optional `float_market_cap` absent when building the float-market-cap-ratio feature
- non-positive market-cap denominators
- unsorted input rows
- duplicate `trade_date` rows for the same symbol/market
- timestamp-bearing `trade_date` values

The implementation may raise `ValueError` for invalid caller input. Prefer the smaller API surface.

### 4. Scope boundaries

Do not implement:

- scanner ranking, cheap/expensive classification, or candidate selection
- buy/sell signals
- strategy rules
- backtest execution
- portfolio or risk logic
- persistence/versioned storage
- feature orchestration or scheduling
- DataHub source adapters or warehouse reads
- capital-flow, macro, announcement, AI, or notification features
- UI or automated trading

## Testing Requirements

Run focused tests:

`python3 -m unittest discover -s tests/features -p 'test_*.py'`

Run DataHub default regression if the implementation imports DataHub dataset identifiers directly or indirectly:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Default tests must remain offline-safe. No live tests are required or allowed for TASK-061.

## Report Requirements

Write `coordination/reports/TASK-061_REPORT.md` with:

- files changed
- tests run and results
- default network behavior
- live-enabled result as `SKIP` because TASK-061 is not a real-source task and this handoff forbids live tests
- deviations from this handoff
- risks or follow-up tasks

## Acceptance Criteria

The task is acceptable when:

- the valuation module imports cleanly
- deterministic offline tests cover valid calculations and invalid/edge inputs
- emitted `FeatureValueRecord` objects pass the existing contract validator
- no DataHub implementation files are changed
- no future phase modules are changed
- default tests remain free of hidden network calls
- report exists at `coordination/reports/TASK-061_REPORT.md`

## Report Path

`coordination/reports/TASK-061_REPORT.md`

## Review Path

`coordination/reviews/TASK-061_REVIEW.md`

## Integration Path

N/A until review acceptance.
