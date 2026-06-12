# TASK-153 Phase 6 Structured Signal Composition and Risk Rule Foundation

## Role

5.3 Execution

## Phase

Phase 6: PortfolioMonitor, SignalEngine, and RiskEngine Personal Trading Perfection.

## Objective

Implement the next ordinary Phase 6 hardening batch from the TASK-151/TASK-152 readiness gate:

- `portfolio_signal_risk__personal_trading_hardening__batch_02`
- `phase6__upstream_signal_composition_foundation`
- `phase6__risk_rule_evaluation_foundation`

The goal is to add deterministic local/offline Phase 6 primitives that convert caller-provided Scanner, StrategyLab, BacktestEngine, and portfolio context into structured signal candidates, then evaluate those candidates against explicit personal risk rules.

## Required Reading

- `AGENTS.md`
- `coordination/ROADMAP.md`
- `coordination/PHASE_GATE.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/reports/TASK-151_REPORT.md`
- `coordination/reports/TASK-152_REPORT.md`
- `coordination/reviews/TASK-152_REVIEW.md`
- `quant/portfolio/personal_readiness.py`
- `quant/portfolio/contracts.py`
- this handoff

Do not read `coordination/agent_runs/**`.

## Allowed Writes

- `quant/portfolio/`
- `tests/portfolio/`
- `coordination/reports/TASK-153_REPORT.md`

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

Implement local/offline Phase 6 composition and risk primitives under `quant/portfolio/`.

Required structured signal composition surface:

- Define importable composition input/output contracts or helpers that accept caller-provided local evidence from Scanner candidates, StrategyLab signal intent, BacktestEngine summaries/reports, and portfolio/watchlist/holding context.
- Preserve upstream provenance through existing or extended `SignalSourceLink` / decision-audit structures without importing or executing upstream modules at runtime.
- Produce deterministic structured `SignalRecord` outputs with stable ids, symbol/market identity, intent, priority or score metadata where appropriate, source links, and decision audit records.
- Validate missing or inconsistent symbol/market identity, duplicate candidate ids or signal ids, stale/as-of dates, unsupported intents, and inconsistent upstream evidence.
- Keep composition serialization-friendly and deterministic over caller-provided inputs only.

Required risk rule evaluation surface:

- Define deterministic local risk-rule contracts and evaluation helpers for exposure, concentration, liquidity, drawdown, position sizing guidance, blacklists, suspensions, and market-specific constraints.
- Produce explicit pass/warn/block decisions with stable reason codes and audit records that explain why a signal passed, warned, or was blocked.
- Support caller-provided portfolio context from TASK-152 contracts without warehouse reads or live data.
- Make position sizing guidance bounded and explanatory; do not implement brokerage orders, automated trading, or account execution.
- Validate malformed risk limits, non-finite numeric inputs, duplicate rules, unsupported markets, and internally inconsistent rule configuration.

Readiness gate maintenance:

- Update `quant/portfolio/personal_readiness.py` so TASK-153-completed capabilities are represented truthfully.
- Phase 6 must remain not closure-ready after TASK-153 unless all roadmap groups truly pass.
- Preserve the remaining coherent follow-up batch for conflict/staleness/risk-block/lifecycle regression coverage.

## Out of Scope

Do not implement:

- DataHub, FeatureHub, Scanner, StrategyLab, or BacktestEngine implementation changes
- runtime upstream module execution, warehouse reads, live data fetching, credentials, private account data, brokerage sessions, browser/session state, or hidden clock dependency
- notification, AI report, UI, live brokerage, order execution, or automated trading
- broad regression-only expansion from `portfolio_signal_risk__personal_trading_hardening__batch_03`, except focused tests required to prove the new composition and risk surfaces in this handoff

## Tests

Run focused offline tests:

- `python3 -m unittest discover -s tests/portfolio -p 'test_*.py'`

You may run broader local tests only if needed to validate imports, but do not run live-enabled tests.

Required test coverage should include:

- valid structured signal composition from caller-provided scanner/strategy/backtest/portfolio evidence
- deterministic signal ordering, ids, source links, and decision-audit output
- rejection of duplicate or inconsistent composition inputs
- rejection or warning for stale upstream/context inputs
- risk-rule pass/warn/block outcomes for exposure, concentration, liquidity, drawdown, sizing, blacklist, suspension, and market constraints
- invalid risk configuration and non-finite numeric input handling
- readiness gate truth after TASK-153 changes

## Network and Data Rules

- Default tests must be offline-safe.
- No live network calls.
- No warehouse reads.
- No DataHub/FeatureHub/Scanner/StrategyLab/BacktestEngine runtime fetching or execution.
- No credentials, private account data, brokerage sessions, browser/session state, or hidden clock dependency.
- Use caller-provided/local code evidence only.

## Completion Report

Write `coordination/reports/TASK-153_REPORT.md` with:

- files changed
- implemented TASK-151/TASK-152 batch/follow-up ids
- readiness gate summary after the change, including `phase_closure_ready`, status counts, remaining follow-up queue count, and remaining follow-up batch count
- tests run
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence
- deviations from this handoff
- risks or follow-up tasks
