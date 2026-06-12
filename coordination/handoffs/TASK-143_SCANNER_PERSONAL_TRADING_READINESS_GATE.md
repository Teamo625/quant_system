# TASK-143 Scanner personal trading readiness gate

## Role

5.3 Execution Window.

## Phase

Phase 4-P Scanner Personal Trading Perfection Re-Review.

## Context

TASK-142 is closed after accepted Review Agent verification. It completed Phase 3-P FeatureHub batch contracts and downstream consumability, kept all behavior offline over caller-provided rows, and left the FeatureHub readiness gate at `phase_closure_ready=true` with status counts `pass=7`, `warn=0`, `blocked=0`, `fail=0`.

Controller applied `coordination/PHASE_GATE.md` and closed Phase 3-P. Scanner historical tasks TASK-064 through TASK-068 are foundation progress only under the current Personal Trading Perfection Standard. They provide contracts, universe helpers, candidate-list persistence, filter matching, and in-memory scan runner primitives, but Scanner is not yet proven personally trading-perfect under `coordination/ROADMAP.md`.

## Objective

Create a deterministic Scanner personal trading readiness gate that audits current Scanner coverage against the roadmap standard and produces a Controller-ready follow-up queue and coherent follow-up batches.

This is an audit/gate task. It must not implement ranking, scoring, candidate selection beyond existing foundation behavior, market-constraint handling, downstream strategy/backtest behavior, or broader workflow hardening.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-143_SCANNER_PERSONAL_TRADING_READINESS_GATE.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/ROADMAP.md`
- `coordination/PHASE_GATE.md`
- `coordination/reports/TASK-064_REPORT.md`
- `coordination/reviews/TASK-064_REVIEW.md`
- `coordination/reports/TASK-065_REPORT.md`
- `coordination/reviews/TASK-065_REVIEW.md`
- `coordination/reports/TASK-066_REPORT.md`
- `coordination/reviews/TASK-066_REVIEW.md`
- `coordination/reports/TASK-067_REPORT.md`
- `coordination/reviews/TASK-067_REVIEW.md`
- `coordination/reports/TASK-068_REPORT.md`
- `coordination/reviews/TASK-068_REVIEW.md`
- `coordination/reports/TASK-142_REPORT.md`
- `coordination/reviews/TASK-142_REVIEW.md`
- `quant/scanner/`
- `tests/scanner/`

Read FeatureHub contracts only if needed to understand Scanner input assumptions. Do not change FeatureHub or DataHub files.

## Allowed Writes

Only:

- `quant/scanner/**`
- `tests/scanner/**`
- `coordination/reports/TASK-143_REPORT.md`

Suggested implementation locations:

- `quant/scanner/personal_readiness.py`
- `tests/scanner/test_personal_readiness.py`
- `quant/scanner/__init__.py` only for minimal exports if needed

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files other than `coordination/reports/TASK-143_REPORT.md`
- `coordination/reviews/**`
- `coordination/integrations/**`
- `coordination/handoffs/**`
- `quant/datahub/**`
- `tests/datahub/**`
- `quant/features/**`
- `tests/features/**`
- `quant/strategies/**`
- `quant/backtest/**`
- `quant/portfolio/**`
- `quant/notification/**`
- `quant/ai/**`
- `quant/ui/**`

Do not fetch live data, call source adapters, read local warehouse state, use credentials, or introduce hidden network behavior.

## Audit Requirements

The readiness gate must classify Scanner against the `coordination/ROADMAP.md` Scanner Personal Trading Perfection Standard.

At minimum, include capability groups for:

- universe definition and validation for A-share, Hong Kong stock, ETF/fund, sector, index, custom watchlist, and exclusion lists
- deterministic feature-filter evaluation over batches, not only one symbol
- ranking/scoring and explicitly configured ordering suitable for research candidate prioritization
- candidate-list persistence with manifests, reproducibility metadata, and downstream handoff readiness
- support for missing features, stale features, suspended/limit-up/down securities, and market-specific constraints
- realistic multi-symbol scan workflows and offline tests for invalid filters, missing values, deterministic ordering, and artifact safety

For each group, record whether current implementation is `pass`, `warn`, `blocked`, or `fail`, with evidence based on current Scanner files and accepted lifecycle artifacts.

## Follow-Up Queue Requirements

The gate must expose deterministic structured follow-up items suitable for Controller dispatch.

Each follow-up item should include at least:

- stable follow-up id
- capability/group id
- status
- disposition such as `scanner_hardening`, `contract_repair`, `owner_blocker`, or `blocked_upstream`
- reason
- recommended next handoff theme

Also expose coherent follow-up batches. Ordinary hardening batches should group 2-6 related items by Scanner domain/theme, such as universe/exclusion/market constraints, ranking/scoring, batch scan workflow depth, persistence/downstream handoff, or offline regression coverage. Single-item batches are allowed only for blocker/rework/schema-risk cases and must explain why they cannot be merged.

The report must recommend the next executable Scanner hardening handoff after this gate. Do not dispatch it from the execution window.

## Implementation Boundaries

The task may add readiness dataclasses, enums, builders, exports, and deterministic tests.

Do not implement:

- new ranking or scoring behavior
- new universe loaders or DataHub/FeatureHub fetches
- strategy rules
- backtest execution
- portfolio, signal, or risk logic
- DataHub source adapters or local warehouse reads
- FeatureHub calculation changes
- AI reports, notifications, UI, or automated trading

## Tests

Required default tests:

- `python3 -m unittest discover -s tests/scanner -p 'test_*.py'`

Run narrower focused tests during development as needed.

No live tests are required or allowed. Default tests must be offline-safe.

## Completion Report

Write `coordination/reports/TASK-143_REPORT.md` with:

- files changed
- readiness model summary
- status counts and phase closure readiness
- follow-up queue and follow-up batch summary
- recommended next executable Scanner handoff
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled result as `SKIP` because this is local audit-only Scanner work
- deviations from the handoff
- risks or follow-up tasks
