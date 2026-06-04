# TASK-060: FeatureHub Price Technical Primitives

## Task ID

TASK-060

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 3: FeatureHub

## Context

TASK-040 is accepted and closed by the controller. It established the minimal FeatureHub contract foundation in `quant/features/contracts.py`, including `FeatureValueRecord`, `FeatureName.PRICE_TECHNICAL`, schema metadata, and deterministic offline validation.

This task opens the first real FeatureHub calculation slice. Keep it narrow: implement pure, deterministic price technical feature primitives from caller-provided daily-bar-like records. Do not fetch data, persist output, rank securities, create scanner behavior, or introduce strategy/backtest/signal/risk/portfolio logic.

The execution window must read:

- `AGENTS.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-060_FEATUREHUB_PRICE_TECHNICAL_PRIMITIVES.md`
- `quant/features/contracts.py`
- `tests/features/test_contracts.py`

## Goal

Add a small offline FeatureHub technical feature module that computes validated price technical `FeatureValueRecord` outputs from local input rows.

## Allowed Files

The execution window may create or modify only:

- `quant/features/**`
- `tests/features/**`
- `coordination/reports/TASK-060_REPORT.md`

Suggested implementation locations:

- `quant/features/technical.py`
- `quant/features/__init__.py`
- `tests/features/test_technical.py`

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

### 1. Pure local technical primitives

Implement a minimal technical feature module with deterministic functions for caller-provided daily bar records.

The slice should include:

- one-day close-to-close return
- simple moving average over close prices
- realized volatility over close-to-close returns

Keep all calculations pure and local. Inputs may be dataclasses or mappings, but must be documented by code shape and tests. The functions must not read files, write files, import source adapters, call live sources, or depend on network access.

### 2. Feature contract output

At least one public function must emit `FeatureValueRecord` values for `FeatureName.PRICE_TECHNICAL`.

Each emitted record must:

- use the input symbol, market, and trade date
- set `source_dataset` to `DatasetName.DAILY_BARS`
- use the existing FeatureHub schema version
- pass `validate_feature_value_record`

If several technical measurements are emitted, encode the measurement name in a stable value or helper field only if it fits the existing TASK-040 contract. Do not change the public FeatureHub contract unless strictly necessary and covered by tests.

### 3. Input validation and edge cases

Handle edge cases deterministically:

- insufficient rows for a requested window
- non-positive or missing close prices
- unsorted input rows
- timestamp-bearing `trade_date` values
- division by zero and non-finite numeric outputs

The implementation may raise `ValueError` for invalid caller input, or skip invalid feature outputs if that behavior is explicit and tested. Prefer the smaller API surface.

### 4. Scope boundaries

Do not implement:

- scanner ranking or candidate selection
- buy/sell signals
- strategy rules
- backtest execution
- portfolio or risk logic
- persistence/versioned storage
- feature orchestration or scheduling
- DataHub source adapters or warehouse reads
- valuation, capital-flow, macro, announcement, or AI features
- notification delivery
- UI or automated trading

## Testing Requirements

Run focused tests:

`python3 -m unittest discover -s tests/features -p 'test_*.py'`

Run DataHub default regression if the implementation imports DataHub dataset identifiers directly or indirectly:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Default tests must remain offline-safe. No live tests are required or allowed for TASK-060.

## Report Requirements

Write `coordination/reports/TASK-060_REPORT.md` with:

- files changed
- tests run and results
- default network behavior
- live-enabled result as `SKIP` because TASK-060 is not a real-source task and this handoff forbids live tests
- deviations from this handoff
- risks or follow-up tasks

## Acceptance Criteria

The task is acceptable when:

- the technical module imports cleanly
- deterministic offline tests cover valid calculations and invalid/edge inputs
- emitted `FeatureValueRecord` objects pass the existing contract validator
- no DataHub implementation files are changed
- no future phase modules are changed
- default tests remain free of hidden network calls
- report exists at `coordination/reports/TASK-060_REPORT.md`

## Report Path

`coordination/reports/TASK-060_REPORT.md`

## Review Path

`coordination/reviews/TASK-060_REVIEW.md`

## Integration Path

N/A until review acceptance.
