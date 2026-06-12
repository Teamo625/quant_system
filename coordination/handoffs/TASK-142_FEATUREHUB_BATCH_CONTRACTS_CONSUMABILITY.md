# TASK-142 FeatureHub batch contracts and downstream consumability

## Role

5.3 Execution Window.

## Phase

Phase 3-P FeatureHub Personal Trading Perfection Re-Review.

## Context

TASK-141 is closed after accepted Review Agent verification of the FeatureHub relative-feature expansion. Default tests remained offline-safe, and no live evidence was required because the work was pure local FeatureHub calculation over caller-provided rows.

Phase 3-P remains incomplete under `coordination/PHASE_GATE.md` and the FeatureHub Personal Trading Perfection Standard in `coordination/ROADMAP.md`. TASK-138 created deterministic FeatureHub `follow_up_batches`; TASK-139 closed `featurehub_technical_indicators_batch_01`; TASK-140 closed `featurehub_valuation_flow_batch_01`; TASK-141 closed `featurehub_relative_features_batch_01`.

The next coherent readiness batch is `featurehub_batch_contracts_batch_01`, covering:

- `FH-BATCH-001`: introduce a stable batch calculation API that accepts caller-provided multi-symbol inputs and returns deterministic multi-feature outputs
- `FH-CONTRACT-001`: add metric-level identity or equivalent downstream-safe semantics so multiple records within one feature family remain distinguishable
- `FH-TEST-001`: expand offline regression coverage alongside the new batch path and downstream contract changes

This is an ordinary current-phase capability cluster. It intentionally groups three related items because batch orchestration, metric identity, persistence compatibility, exports, and regression coverage share the same FeatureHub contract surface.

## Objective

Add deterministic, offline-only FeatureHub batch and downstream-consumability contracts so caller-provided FeatureHub inputs and outputs can be consumed consistently by future Scanner and StrategyLab phases without implementing Scanner or StrategyLab behavior.

The task must provide:

- a stable batch API surface for caller-provided multi-symbol feature jobs
- deterministic multi-feature output ordering and validation
- metric-level identity or an equivalent explicit contract that distinguishes records within shared feature families such as `price_technical`, `valuation`, `capital_flow`, and relative/market-context outputs
- storage/manifest compatibility for the chosen metric-identity contract
- focused offline regression coverage for success paths, invalid specs, duplicate identities, missing data, deterministic ordering, schema compatibility, and readiness-gate closure truth

Keep all behavior local and deterministic. Do not fetch data, read local warehouse state, call DataHub adapters, use credentials, or implement scanner ranking, candidate selection, strategy rules, backtest execution, portfolio/signal/risk behavior, AI, notification, UI, or automated trading.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-142_FEATUREHUB_BATCH_CONTRACTS_CONSUMABILITY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/ROADMAP.md`
- `coordination/PHASE_GATE.md`
- `coordination/reports/TASK-138_REPORT.md`
- `coordination/reviews/TASK-138_REVIEW.md`
- `coordination/reports/TASK-141_REPORT.md`
- `coordination/reviews/TASK-141_REVIEW.md`
- `quant/features/contracts.py`
- `quant/features/storage.py`
- `quant/features/personal_readiness.py`
- `quant/features/__init__.py`
- `tests/features/test_contracts.py`
- `tests/features/test_storage.py`
- `tests/features/test_personal_readiness.py`

Read existing feature-family modules and tests only as needed to preserve local conventions and to wire the batch API to already implemented offline primitives:

- `quant/features/technical.py`
- `quant/features/valuation.py`
- `quant/features/capital_flow.py`
- `quant/features/relative.py`
- `tests/features/test_technical.py`
- `tests/features/test_valuation.py`
- `tests/features/test_capital_flow.py`
- `tests/features/test_relative.py`

Do not change DataHub files.

## Allowed Writes

Only:

- `quant/features/batch.py`
- `quant/features/contracts.py`
- `quant/features/storage.py`
- `quant/features/personal_readiness.py`
- `quant/features/__init__.py`
- `quant/features/technical.py` only if minimal compatibility changes are required for the chosen metric-identity contract
- `quant/features/valuation.py` only if minimal compatibility changes are required for the chosen metric-identity contract
- `quant/features/capital_flow.py` only if minimal compatibility changes are required for the chosen metric-identity contract
- `quant/features/relative.py` only if minimal compatibility changes are required for the chosen metric-identity contract or batch API
- `tests/features/test_batch.py`
- `tests/features/test_contracts.py`
- `tests/features/test_storage.py`
- `tests/features/test_personal_readiness.py`
- focused existing feature-family tests only when the contract compatibility change requires updates
- `coordination/reports/TASK-142_REPORT.md`

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files other than `coordination/reports/TASK-142_REPORT.md`
- `coordination/reviews/**`
- `coordination/integrations/**`
- `coordination/handoffs/**`
- `quant/datahub/**`
- `tests/datahub/**`
- `quant/scanner/**`
- `tests/scanner/**`
- `quant/strategies/**`
- `quant/backtest/**`
- `quant/portfolio/**`
- `quant/notification/**`
- `quant/ai/**`
- `quant/ui/**`

Do not implement scanner ranking, scoring, stock-picking, strategy rules, backtest replay, portfolio/signal/risk logic, AI reports, notification behavior, UI, automated trading, paid credentials, private data access, source adapters, local warehouse refreshes, or hidden network behavior.

## Implementation Requirements

Batch API hardening must:

- accept caller-provided in-memory inputs only
- support multi-symbol or multi-entity batch jobs with explicit symbol/entity, market, trade-date, source-dataset, feature-family, metric identity, and calculation parameters
- return deterministic `FeatureValueRecord`-compatible outputs or a clearly documented batch result that can be serialized through FeatureHub storage
- preserve deterministic ordering by market, symbol/entity, trade date, feature family, metric identity, and any explicit job order required by the chosen contract
- validate non-empty identifiers, supported feature families, supported source datasets, finite numeric outputs, duplicate output identities, invalid calculation specs, and missing required inputs
- keep missing optional context explicit; do not silently substitute one feature family, source route, sector, index, or metric for another
- avoid changing calculation semantics for accepted technical, valuation, capital-flow, and relative primitives except where minimal compatibility wiring is needed

Downstream contract hardening must:

- add metric-level identity or an equivalent explicit field/contract so records in the same `FeatureName` family are distinguishable after persistence
- keep schema/version behavior deliberate and test-covered; if schema version changes, storage deserialization and tests must handle the change explicitly
- update serialization, deserialization, manifest metadata, and validation so downstream consumers can inspect available metrics deterministically
- preserve backward compatibility where practical, or document and test any intentional incompatibility
- avoid adding Scanner, StrategyLab, or BacktestEngine imports or behavior

Readiness update must:

- update `quant/features/personal_readiness.py` so `featurehub_batch_contracts_batch_01` truthfully reflects the implementation state if the batch is fully completed
- remove or adjust only completed `FH-BATCH-001`, `FH-CONTRACT-001`, and `FH-TEST-001` follow-up truth
- mark the remaining FeatureHub capability groups `PASS` only if the implementation and tests fully satisfy the roadmap standard for this batch
- keep `phase_closure_ready` conservative if any current FeatureHub capability group remains incomplete

## Tests

Required default tests:

- `python3 -m unittest tests.features.test_batch`
- `python3 -m unittest tests.features.test_contracts`
- `python3 -m unittest tests.features.test_storage`
- `python3 -m unittest tests.features.test_personal_readiness`
- `python3 -m unittest discover -s tests/features -p 'test_*.py'`

If existing feature-family modules are modified, also run the directly affected focused tests, such as:

- `python3 -m unittest tests.features.test_technical`
- `python3 -m unittest tests.features.test_valuation`
- `python3 -m unittest tests.features.test_capital_flow`
- `python3 -m unittest tests.features.test_relative`

No live tests are required or allowed. Default tests must remain offline-safe.

## Completion Report

Write `coordination/reports/TASK-142_REPORT.md` with:

- files changed
- selected readiness batch id and included follow-up ids
- implemented batch API surface
- implemented downstream metric-identity or equivalent contract
- storage/manifest/schema compatibility behavior
- readiness-gate updates
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled result as `SKIP` because this is local FeatureHub contract/batch work
- deviations from the handoff
- risks or follow-up tasks
