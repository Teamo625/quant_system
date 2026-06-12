# TASK-154 Phase 6 Signal/Risk Workflow Regression Coverage

## Role

5.3 Execution

## Phase

Phase 6: PortfolioMonitor, SignalEngine, and RiskEngine Personal Trading Perfection.

## Objective

Implement the remaining ordinary Phase 6 hardening batch from the TASK-151/TASK-153 readiness gate:

- `portfolio_signal_risk__personal_trading_hardening__batch_03`
- `phase6__conflicting_and_risk_blocked_signal_regressions`
- `phase6__stale_input_and_lifecycle_transition_regressions`

The goal is to deepen deterministic local/offline workflow regression coverage now that Phase 6 has portfolio contracts, signal lifecycle contracts, structured signal composition, and risk-rule evaluation foundations.

## Required Reading

- `AGENTS.md`
- `coordination/ROADMAP.md`
- `coordination/PHASE_GATE.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/reports/TASK-151_REPORT.md`
- `coordination/reports/TASK-152_REPORT.md`
- `coordination/reports/TASK-153_REPORT.md`
- `coordination/reviews/TASK-153_REVIEW.md`
- `quant/portfolio/personal_readiness.py`
- `quant/portfolio/contracts.py`
- `quant/portfolio/signal_composition.py`
- `quant/portfolio/risk_rules.py`
- this handoff

Do not read `coordination/agent_runs/**`.

## Allowed Writes

- `quant/portfolio/`
- `tests/portfolio/`
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

Add local/offline Phase 6 workflow regression depth under `quant/portfolio/` and `tests/portfolio/`.

Required conflicting-signal and risk-blocked coverage:

- Prove deterministic handling for conflicting caller-provided signals for the same symbol/market, including supersession or conflict markers and audit records.
- Prove that risk-blocked composed signals retain clear block reason codes and decision-audit records.
- Cover conflicts across at least opposite actionable intents, duplicate or competing signal identities where applicable, and risk-blocked outcomes caused by explicit local risk context.
- If existing contracts or helpers cannot express a required conflict/supersession workflow deterministically, add the smallest local/offline helper or contract extension needed under `quant/portfolio/`.

Required stale-input and lifecycle-transition coverage:

- Extend stale-input tests from focused composition warnings into broader composed-signal workflow regressions.
- Prove deterministic lifecycle transitions for composed signals through created, updated, expired, and closed states where the existing contract permits them.
- Prove invalid lifecycle transitions remain rejected in multi-step workflow context.
- Preserve source links and decision-audit evidence across lifecycle updates, expiry, closure, and risk-blocked decisions.

Readiness gate maintenance:

- Update `quant/portfolio/personal_readiness.py` so TASK-154-completed capabilities are represented truthfully.
- If all Phase 6 roadmap groups are genuinely complete after this batch, the readiness gate may report `phase_closure_ready=true` with no remaining follow-up queue or batches.
- Do not mark Phase 6 closure-ready unless the implemented tests and local code truth satisfy the roadmap standard for watchlist/holding contracts, signal lifecycle, structured composition, risk rules, auditability, and the required workflow regression coverage.

## Out of Scope

Do not implement:

- DataHub, FeatureHub, Scanner, StrategyLab, or BacktestEngine implementation changes
- runtime upstream module execution, warehouse reads, live data fetching, credentials, private account data, brokerage sessions, browser/session state, or hidden clock dependency
- notification, AI report, UI, live brokerage, order execution, or automated trading
- broad product features beyond the conflict/staleness/risk-block/lifecycle workflow regressions needed to close the remaining Phase 6 readiness batch

## Tests

Run focused offline tests:

- `python3 -m unittest discover -s tests/portfolio -p 'test_*.py'`

You may run narrower portfolio tests while iterating. Do not run live-enabled tests.

Required test coverage should include:

- conflicting signal workflow behavior for same symbol/market inputs
- supersession or conflict audit trace behavior
- stale composed-signal workflow behavior
- risk-blocked signal workflow behavior with stable reason codes
- valid lifecycle transitions over composed signals
- invalid lifecycle transition rejection in workflow context
- readiness gate truth after TASK-154 changes

## Network and Data Rules

- Default tests must be offline-safe.
- No live network calls.
- No warehouse reads.
- No DataHub/FeatureHub/Scanner/StrategyLab/BacktestEngine runtime fetching or execution.
- No credentials, private account data, brokerage sessions, browser/session state, or hidden clock dependency.
- Use caller-provided/local code evidence only.

## Completion Report

Write `coordination/reports/TASK-154_REPORT.md` with:

- files changed
- implemented TASK-151/TASK-153 batch/follow-up ids
- readiness gate summary after the change, including `phase_closure_ready`, status counts, remaining follow-up queue count, and remaining follow-up batch count
- tests run
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence
- deviations from this handoff
- risks or follow-up tasks
