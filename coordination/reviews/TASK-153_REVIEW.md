# TASK-153 Review

## Findings

- Blocking: `quant/portfolio/risk_rules.py:326-382` computes `target_weight` from `sizing_guidance` and silently falls back to `current_weight` when no `PositionSizingRule` exists. That makes `ExposureRiskRule` and `ConcentrationRiskRule` evaluate an `ENTER`/`INCREASE` signal as if portfolio weight will not change, and `MarketConstraintRiskRule` also skips lot-size enforcement when `sizing_guidance is None` at `quant/portfolio/risk_rules.py:489-511`. The handoff defined these as independent rule families; they should not quietly pass on a zero-change assumption for new risk. Current tests only exercise those rule families with an attached sizing rule (`tests/portfolio/test_signal_risk.py:357-417`, `452-583`), so the gap is unprotected.

## Decision

Rejected for rework. Scope stayed within Phase 6 portfolio files, the focused default suite is offline-safe, and the reported local-only `SKIP` live result is acceptable, but the risk evaluator still has a blocking contract/behavior gap.

## Closure Status

- decision: rejected_or_blocked
- controller_closure_allowed: no
- default_tests_offline_safe: yes
- live_enabled_result: SKIP
- rework_required: yes

## Closure Readiness

- Controller must not close `TASK-153` yet.
- Default tests are offline-safe; independent rerun of `python3 -m unittest discover -s tests/portfolio -p 'test_*.py'` passed.
- Live-enabled result is `SKIP` because this handoff is explicitly local/offline-only; rework is required for the repository-side risk-evaluation gap, not for live coverage.
- Blocking items remain in Phase 6 rule semantics and test coverage: exposure/concentration/market-constraint evaluation without sizing guidance must be made explicit and covered by regression tests before closure.
