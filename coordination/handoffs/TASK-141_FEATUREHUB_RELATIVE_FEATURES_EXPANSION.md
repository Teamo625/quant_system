# TASK-141 FeatureHub relative features expansion

## Role

5.3 Execution Window.

## Phase

Phase 3-P FeatureHub Personal Trading Perfection Re-Review.

## Context

TASK-140 is closed after accepted Review Agent verification of the FeatureHub valuation and flow feature expansion. Default tests remained offline-safe, and no live evidence was required because the work was pure local FeatureHub calculation over caller-provided rows.

Phase 3-P remains incomplete under `coordination/PHASE_GATE.md` and the FeatureHub Personal Trading Perfection Standard in `coordination/ROADMAP.md`. TASK-138 created deterministic FeatureHub `follow_up_batches`; TASK-139 closed `featurehub_technical_indicators_batch_01`; TASK-140 closed `featurehub_valuation_flow_batch_01`. The next coherent readiness batch is `featurehub_relative_features_batch_01`, covering:

- `FH-REL-001`: add stock-vs-sector return spread and sector-strength features over caller-provided sector inputs
- `FH-REL-002`: add index-relative performance plus breadth/rotation primitives for market-context features

This is an ordinary current-phase hardening capability cluster. It intentionally groups two related relative-feature items because both combine validated caller-provided stock, sector, and index/market-context inputs, share date/window alignment semantics, and should remain pure local FeatureHub calculations.

## Objective

Add deterministic, offline-only FeatureHub relative-feature primitives that make caller-provided stock, sector, index, and constituent-like inputs usable for scanner and strategy research without introducing Scanner behavior or source fetching.

Implement practical local calculations for:

- stock-vs-sector return spread over aligned bounded windows
- sector strength over caller-provided sector price/return rows
- index-relative stock or ETF/fund performance over aligned bounded windows
- breadth primitives such as positive-return ratio or above-threshold ratio over caller-provided member return rows
- rotation primitives such as sector return ranking, relative sector momentum, or top/bottom sector spread over caller-provided sector rows

Keep all behavior local and deterministic. Do not fetch data, read local warehouse state, call DataHub adapters, use credentials, or implement scanner ranking, candidate selection, strategy rules, backtest execution, portfolio/signal/risk behavior, AI, notification, UI, or automated trading.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-141_FEATUREHUB_RELATIVE_FEATURES_EXPANSION.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/ROADMAP.md`
- `coordination/PHASE_GATE.md`
- `coordination/reports/TASK-138_REPORT.md`
- `coordination/reviews/TASK-138_REVIEW.md`
- `coordination/reports/TASK-140_REPORT.md`
- `coordination/reviews/TASK-140_REVIEW.md`
- `quant/features/contracts.py`
- `quant/features/personal_readiness.py`
- `quant/features/technical.py`
- `quant/features/__init__.py`
- `tests/features/test_personal_readiness.py`

Read existing `quant/features/valuation.py`, `quant/features/capital_flow.py`, or DataHub dataset definitions only if needed to preserve local FeatureHub conventions or confirm existing enum names. Do not change DataHub files.

## Allowed Writes

Only:

- `quant/features/relative.py`
- `quant/features/contracts.py` only if a minimal FeatureHub contract export/source-dataset update is required for relative feature records
- `quant/features/personal_readiness.py`
- `quant/features/__init__.py` only for minimal exports
- `tests/features/test_relative.py`
- `tests/features/test_contracts.py` only if `contracts.py` changes
- `tests/features/test_personal_readiness.py`
- `coordination/reports/TASK-141_REPORT.md`

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files other than `coordination/reports/TASK-141_REPORT.md`
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

Relative-feature hardening must:

- normalize caller-provided rows deterministically by symbol or entity id, market, and trade date
- validate finite numeric inputs, non-empty identifiers, bounded windows, duplicate dates, mixed symbol/market/entity errors, and insufficient history
- align stock/sector/index series by common trade dates and fail clearly when the bounded aligned window is insufficient
- preserve deterministic sorting and output ordering for any multi-entity primitive such as breadth or rotation ranking
- keep missing optional context explicit; do not silently substitute a sector or index series with another route or source
- avoid changing existing technical, valuation, capital-flow, storage, Scanner, strategy, or DataHub behavior except for minimal exports required by the new FeatureHub module

Readiness update must:

- update `quant/features/personal_readiness.py` so `featurehub_relative_features_batch_01` truthfully reflects the new implementation state if the batch is fully completed
- remove or adjust only completed `FH-REL-001` / `FH-REL-002` follow-up truth
- keep later batch API, downstream contract, and broad test-coverage gaps conservative
- set the next recommended handoff batch to `featurehub_batch_contracts_batch_01` only if this task fully closes the relative-feature batch

## Tests

Required default tests:

- `python3 -m unittest tests.features.test_relative`
- `python3 -m unittest tests.features.test_personal_readiness`
- `python3 -m unittest discover -s tests/features -p 'test_*.py'`

If `contracts.py` changes, also run:

- `python3 -m unittest tests.features.test_contracts`

No live tests are required or allowed. Default tests must remain offline-safe.

## Completion Report

Write `coordination/reports/TASK-141_REPORT.md` with:

- files changed
- selected readiness batch id and included follow-up ids
- implemented sector-relative capabilities
- implemented market/index-relative capabilities
- implemented breadth/rotation primitives
- readiness-gate updates
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled result as `SKIP` because this is local FeatureHub calculation work
- deviations from the handoff
- risks or follow-up tasks
