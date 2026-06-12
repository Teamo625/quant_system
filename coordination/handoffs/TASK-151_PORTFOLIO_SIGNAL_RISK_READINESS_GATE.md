# TASK-151 Portfolio, Signal, and Risk Personal Trading Readiness Gate

## Role

5.3 Execution

## Phase

Phase 6: PortfolioMonitor, SignalEngine, and RiskEngine Personal Trading Perfection.

## Objective

Create the initial local/offline Phase 6 readiness gate for PortfolioMonitor, SignalEngine, and RiskEngine. The gate must classify the current Phase 6 capability state against `coordination/ROADMAP.md`, emit deterministic follow-up queue items and coherent follow-up batches, and recommend the next executable Phase 6 hardening handoff.

This task is audit/gate work. It must not implement production signal generation, portfolio monitoring, risk sizing, notification, AI, UI, automated trading, live brokerage integration, or real data fetching.

## Required Reading

- `AGENTS.md`
- `coordination/ROADMAP.md`
- `coordination/PHASE_GATE.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- this handoff
- Existing local upstream contracts as needed for interface awareness only:
  - `quant/scanner/`
  - `quant/strategies/`
  - `quant/backtest/`

Do not read `coordination/agent_runs/**`.

## Allowed Writes

- `quant/portfolio/`
- `tests/portfolio/`
- `coordination/reports/TASK-151_REPORT.md`

If `tests/portfolio/` does not exist, create it.

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

Implement deterministic local readiness/audit primitives under `quant/portfolio/` that can be imported and tested offline.

The readiness gate must evaluate these Phase 6 roadmap capability groups:

- watchlist and holding-state contracts with deterministic updates
- signal lifecycle management, including created, updated, expired, and closed states
- combination of Scanner, StrategyLab, BacktestEngine, and portfolio context into structured signal records
- risk rules for exposure, concentration, liquidity, drawdown, position sizing guidance, blacklists, suspensions, and market-specific constraints
- auditability of why a signal exists and why it passed or failed risk checks
- tests for conflicting signals, stale data, risk-blocked signals, and lifecycle transitions

The readiness output must include:

- `phase_closure_ready`
- status counts for `pass`, `warn`, `blocked`, and `fail`
- capability items with stable ids, names, statuses, evidence, limitations, and recommended follow-up disposition
- a `follow_up_queue`
- coherent `follow_up_batches` suitable for later Controller dispatch, normally grouping 2-6 related items by workflow or contract surface
- a recommended next handoff title and rationale

Because Phase 6 starts from a placeholder module, the gate should be conservative. Foundation absence should be represented as `warn` or `fail` only when appropriate and must not be treated as completion.

## Expected Initial Follow-up Themes

Use the roadmap and observed local code state to decide the exact final queue, but the gate should at least consider these coherent Phase 6 themes:

- portfolio/watchlist/holding-state contract foundation
- signal lifecycle and source-link/audit contract foundation
- risk rule evaluation foundation for exposure, concentration, liquidity, drawdown, sizing guidance, blacklists, suspension, and market constraints
- integration-shaped local composition from scanner candidates, strategy outputs, backtest reports, and portfolio context into structured signal candidates
- offline regression coverage for conflicting signals, stale inputs, risk-blocked signals, and lifecycle transitions

## Tests

Run focused offline tests only:

- `python3 -m unittest discover -s tests/portfolio -p 'test_*.py'`

You may run broader local tests only if needed to validate imports, but do not run live-enabled tests.

## Network and Data Rules

- Default tests must be offline-safe.
- No live network calls.
- No warehouse reads.
- No DataHub/FeatureHub/Scanner runtime data fetching.
- No credentials, private account data, brokerage sessions, browser/session state, or hidden clock dependency.
- Use caller-provided/local code evidence only.

## Completion Report

Write `coordination/reports/TASK-151_REPORT.md` with:

- files changed
- readiness gate summary, including `phase_closure_ready`, status counts, follow-up queue count, and follow-up batch count
- recommended next executable handoff
- tests run
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence
- deviations from this handoff
- risks or follow-up tasks
