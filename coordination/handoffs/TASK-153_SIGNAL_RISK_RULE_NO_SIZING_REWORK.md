# TASK-153 Signal Risk Rule No-Sizing Rework

## Role

5.3 Execution

## Phase

Phase 6: PortfolioMonitor, SignalEngine, and RiskEngine Personal Trading Perfection.

## Objective

Fix the focused Review-blocking risk-rule semantics gap from `coordination/reviews/TASK-153_REVIEW.md`.

TASK-153 is not closed. This rework must make exposure, concentration, and market-constraint evaluation explicit when an `ENTER` or `INCREASE` signal has no applicable `PositionSizingRule` / sizing guidance. These rule families must not silently pass by assuming zero portfolio-weight change for new risk.

## Required Reading

- `AGENTS.md`
- `coordination/ROADMAP.md`
- `coordination/PHASE_GATE.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-153_STRUCTURED_SIGNAL_RISK_FOUNDATION.md`
- `coordination/reports/TASK-153_REPORT.md`
- `coordination/reviews/TASK-153_REVIEW.md`
- `quant/portfolio/risk_rules.py`
- `tests/portfolio/test_signal_risk.py`
- this handoff

Do not read `coordination/agent_runs/**`.

## Allowed Writes

- `quant/portfolio/risk_rules.py`
- `tests/portfolio/test_signal_risk.py`
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

Keep this as a minimal Review rework only. Do not merge it with readiness `follow_up_batches`, TASK-153 ordinary feature expansion beyond the Review finding, or the later Phase 6 regression batch.

Required behavior:

- Exposure and concentration rules must not evaluate `ENTER` / `INCREASE` signals as if target weight equals current weight merely because sizing guidance is missing.
- Market-specific constraints such as lot-size checks must not silently skip for actionable `ENTER` / `INCREASE` signals merely because sizing guidance is missing.
- The evaluator must produce explicit, auditable PASS/WARN/BLOCK behavior with stable reason codes when a rule cannot evaluate required projected exposure, concentration, or lot-size facts from caller-provided inputs.
- Preserve deterministic local/offline behavior over caller-provided signal, portfolio, market, and rule inputs only.
- Preserve existing valid behavior when a `PositionSizingRule` exists and sizing guidance is available.
- Preserve existing valid behavior for non-actionable intents where sizing guidance is not required.

Required tests:

- Add focused offline regression coverage for `ENTER` or `INCREASE` signals without a sizing rule/guidance proving exposure and concentration do not silently pass on a zero-change assumption.
- Add focused offline regression coverage proving market-constraint lot-size behavior is explicit when sizing guidance is missing for actionable signals.
- Keep existing TASK-153 risk-rule tests passing.

## Out of Scope

Do not implement:

- new signal composition features
- broad conflict/staleness/risk-block/lifecycle regression coverage from `portfolio_signal_risk__personal_trading_hardening__batch_03`
- DataHub, FeatureHub, Scanner, StrategyLab, or BacktestEngine implementation changes
- runtime upstream module execution, warehouse reads, live data fetching, credentials, private account data, brokerage sessions, browser/session state, or hidden clock dependency
- notification, AI report, UI, live brokerage, order execution, or automated trading

## Tests

Run focused offline tests:

- `python3 -m unittest discover -s tests/portfolio -p 'test_*.py'`

You may run a narrower `tests/portfolio/test_signal_risk.py` test command while iterating, but the completion report must include the full focused portfolio test command above.

Do not run live-enabled tests.

## Network and Data Rules

- Default tests must be offline-safe.
- No live network calls.
- No warehouse reads.
- No DataHub/FeatureHub/Scanner/StrategyLab/BacktestEngine runtime fetching or execution.
- No credentials, private account data, brokerage sessions, browser/session state, or hidden clock dependency.

## Completion Report

Update `coordination/reports/TASK-153_REPORT.md` with a clear rework section including:

- files changed for this rework
- Review finding addressed
- exact risk-rule behavior chosen for missing sizing guidance
- tests run
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence
- deviations from this handoff
- remaining risks or follow-up tasks
