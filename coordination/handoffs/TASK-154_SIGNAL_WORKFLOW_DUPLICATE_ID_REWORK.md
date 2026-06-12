# TASK-154 Signal Workflow Duplicate ID Rework

## Role

5.3 Execution rework.

## Phase

Phase 6: PortfolioMonitor, SignalEngine, and RiskEngine Personal Trading Perfection.

## Objective

Fix the focused TASK-154 Review blocking finding:

- `reconcile_conflicting_signals()` currently keys its working/result state by `signal_id` without first validating uniqueness.
- Duplicate caller-provided `signal_id` inputs can be silently collapsed, causing one input to be lost and the conflict/supersession audit trail to become wrong.

This is a minimal Review rework only. Do not merge it with readiness `follow_up_batches` or any ordinary Phase 6 hardening item.

## Required Reading

- `AGENTS.md`
- `coordination/ROADMAP.md`
- `coordination/PHASE_GATE.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-154_SIGNAL_RISK_WORKFLOW_REGRESSIONS.md`
- `coordination/reports/TASK-154_REPORT.md`
- `coordination/reviews/TASK-154_REVIEW.md`
- `quant/portfolio/signal_workflow.py`
- `tests/portfolio/test_signal_workflow.py`
- this handoff

Do not read `coordination/agent_runs/**`.

## Allowed Writes

- `quant/portfolio/signal_workflow.py`
- `tests/portfolio/test_signal_workflow.py`
- `coordination/reports/TASK-154_REPORT.md`

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

Implement the smallest local/offline fix that makes duplicate `signal_id` handling deterministic and audit-safe.

Required behavior:

- Reject duplicate `signal_id` inputs before any dict/materialized state can collapse caller-provided signals, or otherwise define deterministic supported behavior that preserves every input and produces correct audit evidence.
- Add a focused regression proving duplicate `signal_id` inputs no longer produce silent overwrite/collapse behavior.
- Preserve existing accepted conflict, supersession, stale-input, risk-blocked, and lifecycle workflow behavior unless the duplicate-ID fix exposes a directly related bug.
- Keep all behavior local/offline over caller-provided objects only.

Preferred contract:

- Reject duplicate `signal_id` inputs with a clear exception before conflict reconciliation proceeds.
- Keep exception behavior simple and deterministic; do not introduce broad new workflow abstractions unless required by the existing code shape.

## Out of Scope

Do not implement:

- new readiness follow-up batches or broad Phase 6 capability expansion
- DataHub, FeatureHub, Scanner, StrategyLab, or BacktestEngine implementation changes
- runtime upstream module execution, warehouse reads, live data fetching, credentials, private account data, brokerage sessions, browser/session state, or hidden clock dependency
- notification, AI report, UI, live brokerage, order execution, or automated trading
- unrelated refactors in portfolio/signal/risk modules

## Tests

Run focused offline tests:

- `python3 -m unittest tests.portfolio.test_signal_workflow`
- `python3 -m unittest discover -s tests/portfolio -p 'test_*.py'`

You may run narrower tests while iterating. Do not run live-enabled tests.

Required test coverage:

- duplicate `signal_id` caller inputs are rejected or deterministically handled without silent collapse
- existing conflict/supersession workflow regressions still pass

## Network and Data Rules

- Default tests must be offline-safe.
- No live network calls.
- No warehouse reads.
- No DataHub/FeatureHub/Scanner/StrategyLab/BacktestEngine runtime fetching or execution.
- No credentials, private account data, brokerage sessions, browser/session state, or hidden clock dependency.

## Completion Report

Update `coordination/reports/TASK-154_REPORT.md` with:

- files changed in the rework
- the Review finding addressed
- readiness gate summary after the rework, including `phase_closure_ready`, status counts, remaining follow-up queue count, and remaining follow-up batch count
- tests run
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence
- deviations from this handoff
- risks or follow-up tasks
