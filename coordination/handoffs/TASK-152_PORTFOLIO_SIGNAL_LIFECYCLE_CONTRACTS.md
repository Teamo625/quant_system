# TASK-152 Phase 6 Portfolio/Watchlist and Signal Lifecycle Contract Foundation

## Role

5.3 Execution

## Phase

Phase 6: PortfolioMonitor, SignalEngine, and RiskEngine Personal Trading Perfection.

## Objective

Implement the first ordinary Phase 6 hardening batch from TASK-151 readiness gate:

- `portfolio_signal_risk__personal_trading_hardening__batch_01`
- `phase6__portfolio_watchlist_and_holding_state_contracts`
- `phase6__signal_lifecycle_and_audit_contracts`
- `phase6__signal_source_link_and_decision_audit_contracts`

The goal is to create deterministic local/offline contracts and validation/update helpers for portfolio watchlists, holding/cash/exposure snapshots, signal lifecycle state, source links, and decision audit records. This task should establish stable Phase 6 contract truth before later composition and risk-rule evaluation work.

## Required Reading

- `AGENTS.md`
- `coordination/ROADMAP.md`
- `coordination/PHASE_GATE.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/reports/TASK-151_REPORT.md`
- `coordination/reviews/TASK-151_REVIEW.md`
- `quant/portfolio/personal_readiness.py`
- this handoff

Do not read `coordination/agent_runs/**`.

## Allowed Writes

- `quant/portfolio/`
- `tests/portfolio/`
- `coordination/reports/TASK-152_REPORT.md`

## Forbidden Writes

- `AGENTS.md`
- `coordination/PROJECT_STATE.md`
- `coordination/ROADMAP.md`
- `coordination/TASK_BOARD.md`
- `coordination/DECISIONS.md`
- `coordination/RISKS.md`
- `coordination/INTERFACES.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/agent_runs/**`
- `quant/datahub/`
- `quant/features/`
- `quant/scanner/`
- `quant/strategies/`
- `quant/backtest/`
- `quant/notification/`
- `quant/ai/`
- `quant/ui/`

## Scope Requirements

Implement local/offline Phase 6 contract primitives under `quant/portfolio/`.

Required portfolio/watchlist/holding contract surface:

- importable watchlist item / watchlist snapshot contracts with stable identity and deterministic ordering
- holding-state contracts with symbol, market, quantity, average cost or cost-basis fields where appropriate, and update metadata
- cash or exposure snapshot contracts sufficient for later risk-rule evaluation
- deterministic update or merge helpers for caller-provided local records
- validation for duplicate symbols, invalid quantities, invalid weights/exposure values, and inconsistent dates or ids

Required signal lifecycle and audit contract surface:

- importable signal record contracts with explicit lifecycle states including `created`, `updated`, `expired`, and `closed`
- deterministic transition helpers or validators that reject unsupported state transitions
- explicit source-link contracts that can reference upstream Scanner, StrategyLab, BacktestEngine, and portfolio context without importing or executing those modules at runtime
- decision audit records capturing why a signal exists and why later risk checks passed, warned, blocked, expired, or closed
- closure/expiry reason fields where lifecycle state requires them
- deterministic serialization-friendly output structures using only local/caller-provided inputs

Readiness gate maintenance:

- Update `quant/portfolio/personal_readiness.py` so TASK-152-completed capabilities are represented truthfully.
- Phase 6 must remain not closure-ready after TASK-152 unless all roadmap groups truly pass.
- Preserve coherent remaining follow-up batches for composition/risk foundation and regression coverage.

## Out of Scope

Do not implement:

- Scanner/StrategyLab/BacktestEngine composition behavior
- executable risk-rule evaluation, exposure limits, sizing advice, blacklist/suspension checks, or market-constraint blocking
- notification, AI report, UI, live brokerage, order execution, automated trading, credentials, private account data, warehouse reads, browser/session state, or live network behavior
- DataHub, FeatureHub, Scanner, StrategyLab, or BacktestEngine implementation changes

## Tests

Run focused offline tests:

- `python3 -m unittest discover -s tests/portfolio -p 'test_*.py'`

You may run broader local tests only if needed to validate imports, but do not run live-enabled tests.

Required test coverage should include:

- valid watchlist/holding/cash or exposure contract construction
- deterministic portfolio/watchlist update or merge behavior
- invalid duplicate or malformed portfolio state inputs
- valid signal creation and lifecycle transition behavior
- rejection of invalid signal state transitions
- source-link and decision-audit contract validation
- readiness gate truth after TASK-152 changes

## Network and Data Rules

- Default tests must be offline-safe.
- No live network calls.
- No warehouse reads.
- No DataHub/FeatureHub/Scanner runtime data fetching.
- No credentials, private account data, brokerage sessions, browser/session state, or hidden clock dependency.
- Use caller-provided/local code evidence only.

## Completion Report

Write `coordination/reports/TASK-152_REPORT.md` with:

- files changed
- implemented TASK-151 batch/follow-up ids
- readiness gate summary after the change, including `phase_closure_ready`, status counts, remaining follow-up queue count, and remaining follow-up batch count
- tests run
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence
- deviations from this handoff
- risks or follow-up tasks
