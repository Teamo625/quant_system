# TASK-152 Portfolio/Signal Duplicate Update Rework

## Role

5.3 Execution

## Phase

Phase 6: PortfolioMonitor, SignalEngine, and RiskEngine Personal Trading Perfection.

## Objective

Fix the focused TASK-152 Review finding only.

Review rejected Controller closure because `merge_watchlist_snapshot()` and `merge_holding_snapshot()` do not reject duplicate symbols inside the caller-provided `updates` iterable. The helpers currently materialize updates into a dict keyed by symbol, so later duplicate updates silently overwrite earlier ones. This violates the original TASK-152 requirement to validate duplicate symbols in deterministic update/merge helpers.

This rework must make duplicate symbols in update inputs fail deterministically and add focused offline regression coverage for both merge helpers.

## Required Reading

- `AGENTS.md`
- `coordination/handoffs/TASK-152_PORTFOLIO_SIGNAL_LIFECYCLE_CONTRACTS.md`
- `coordination/reports/TASK-152_REPORT.md`
- `coordination/reviews/TASK-152_REVIEW.md`
- `quant/portfolio/contracts.py`
- focused existing portfolio tests relevant to merge/update behavior

Do not read `coordination/agent_runs/**`.

## Allowed Writes

- `quant/portfolio/contracts.py`
- focused `tests/portfolio/` files that cover the duplicate-update regression
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

Implement the minimal fix required by Review:

- `merge_watchlist_snapshot()` must reject duplicate symbols in the `updates` iterable before any last-write-wins overwrite can occur.
- `merge_holding_snapshot()` must reject duplicate symbols in the `updates` iterable before any last-write-wins overwrite can occur.
- Regression tests must prove duplicate update symbols fail for both helpers.
- Preserve existing valid merge behavior, deterministic ordering, existing contract validation, and serialization-friendly local/offline behavior.
- Keep the original TASK-152 readiness truth conservative. Do not promote Phase 6 closure readiness beyond what the code and readiness gate truthfully support.

## Out of Scope

Do not implement:

- Scanner/StrategyLab/BacktestEngine composition behavior
- executable risk-rule evaluation, exposure limits, sizing advice, blacklist/suspension checks, or market-constraint blocking
- broader portfolio/risk/signal hardening beyond this duplicate-update Review finding
- readiness `follow_up_batches` for composition/risk/regression coverage
- notification, AI report, UI, live brokerage, order execution, automated trading, credentials, private account data, warehouse reads, browser/session state, or live network behavior
- DataHub, FeatureHub, Scanner, StrategyLab, or BacktestEngine implementation changes

## Tests

Run focused offline tests:

- `python3 -m unittest discover -s tests/portfolio -p 'test_*.py'`

You may run narrower portfolio test targets first while iterating, but the final report must include the focused portfolio discovery command above.

Do not run live-enabled tests.

## Network and Data Rules

- Default tests must be offline-safe.
- No live network calls.
- No warehouse reads.
- No DataHub/FeatureHub/Scanner runtime data fetching.
- No credentials, private account data, brokerage sessions, browser/session state, or hidden clock dependency.
- Use caller-provided/local code evidence only.

## Completion Report

Update `coordination/reports/TASK-152_REPORT.md` with a rework section that includes:

- files changed by the rework
- the Review finding addressed
- tests run
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence
- deviations from this rework handoff
- risks or follow-up tasks

