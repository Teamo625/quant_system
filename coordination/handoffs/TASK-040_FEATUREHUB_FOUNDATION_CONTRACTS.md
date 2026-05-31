# TASK-040: FeatureHub Foundation Contracts

## Task ID

TASK-040

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 3: FeatureHub

## Context

TASK-039 has been accepted, integrated, and closed by the controller. It completed the narrow local-only DataHub warehouse refresh runner with offline-safe tests.

The controller has applied `coordination/PHASE_GATE.md` and opened Phase 3. Phase 2 is now complete for the current approved scope because TASK-006 through TASK-039 cover the comprehensive DataHub source catalog, stable dataset contracts, real-source adapter slices, local raw/curated persistence, refresh metadata, and local data quality output.

Phase 3 must start conservatively. This first task opens FeatureHub implementation with package structure and feature contract definitions only. It must consume DataHub contracts conceptually, but it must not implement technical indicators, scoring, scanning, strategy rules, backtesting, notifications, AI reports, UI, or automated trading.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-040_FEATUREHUB_FOUNDATION_CONTRACTS.md`

## Goal

Create a minimal FeatureHub foundation that defines stable feature contract primitives and offline tests, without computing real research features yet.

## Allowed Files

The execution window may create or modify:

- `quant/features/**`
- `tests/features/**`
- `coordination/reports/TASK-040_REPORT.md`

Suggested implementation locations:

- `quant/features/__init__.py`
- `quant/features/contracts.py`
- `tests/features/test_contracts.py`

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

### 1. Feature contract primitives

Add a small FeatureHub contract module with typed primitives for future feature outputs.

The contract should include at least:

- a feature dataset/name identifier type or enum for the first planned families
- a feature value record structure with fields such as symbol, market, trade date, feature name, value, source dataset, created timestamp, and schema version
- a lightweight schema/version constant or metadata object
- deterministic validation helpers for required fields and supported value types

Keep the shape stable enough for later tasks to add actual feature calculations without changing the public contract immediately.

### 2. DataHub dependency boundary

FeatureHub may reference DataHub dataset names as input identifiers, but must not fetch live data, instantiate real adapters, or write DataHub warehouse files.

If importing `DatasetName` from `quant.datahub.datasets` is useful, keep it limited to type-safe source dataset references. Do not modify DataHub code.

### 3. Offline tests

Add deterministic tests proving:

- the contract module imports cleanly
- a valid feature value record passes validation
- missing required fields fail validation
- unsupported feature names or value types fail validation
- source dataset references are constrained to approved DataHub inputs

Tests must not perform network calls.

### 4. Scope boundaries

Do not implement:

- moving averages, RSI, MACD, returns, volatility, valuation factors, capital-flow factors, macro features, or any real feature calculation
- scanner ranking logic
- stock picking rules
- strategy rules
- backtest execution
- portfolio or signal logic
- notification delivery
- AI reports
- UI
- remote source access
- scheduling or orchestration

## Testing Requirements

Run focused tests:

`python3 -m unittest discover -s tests/features -p 'test_*.py'`

Run DataHub default regression only if the implementation imports DataHub objects:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Default tests must remain offline-safe. No live tests are required or allowed for TASK-040.

## Acceptance Criteria

The task is acceptable when:

- FeatureHub has a minimal importable package and contract module
- deterministic offline tests cover valid and invalid feature contract behavior
- no real feature calculations are introduced
- no DataHub implementation files are changed
- no future phase modules are changed
- default tests remain free of hidden network calls
- report exists at `coordination/reports/TASK-040_REPORT.md`

## Report Path

`coordination/reports/TASK-040_REPORT.md`

## Review Path

`coordination/reviews/TASK-040_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-040_INTEGRATION.md`

## Out of Scope

Everything beyond FeatureHub contract foundations is out of scope.
