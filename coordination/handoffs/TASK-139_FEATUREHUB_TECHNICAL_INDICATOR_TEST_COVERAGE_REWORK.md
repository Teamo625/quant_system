# TASK-139 FeatureHub technical indicator test coverage rework

## Role

5.3 Execution Window.

## Phase

Phase 3-P FeatureHub Personal Trading Perfection Re-Review.

## Context

TASK-139 execution implemented the assigned `featurehub_technical_indicators_batch_01` technical indicator cluster and wrote `coordination/reports/TASK-139_REPORT.md`.

The Review Agent rejected closure in `coordination/reviews/TASK-139_REVIEW.md` because the handoff-required negative-path regression coverage for the new EMA and momentum oscillator families is incomplete.

This is a focused Review rework. Do not merge it with the next readiness `follow_up_batches`, valuation/flow work, relative-feature work, batch API work, downstream contract work, or any ordinary FeatureHub hardening item.

## Objective

Add the missing offline regression tests required by the original TASK-139 handoff so Review can verify the expanded technical indicator API covers key validation and boundary branches.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-139_FEATUREHUB_TECHNICAL_INDICATORS_CORE_EXPANSION.md`
- `coordination/handoffs/TASK-139_FEATUREHUB_TECHNICAL_INDICATOR_TEST_COVERAGE_REWORK.md`
- `coordination/reports/TASK-139_REPORT.md`
- `coordination/reviews/TASK-139_REVIEW.md`
- `quant/features/technical.py`
- `tests/features/test_technical.py`

Read other `quant/features/` or `tests/features/` files only if needed to preserve local test style. Do not read `coordination/agent_runs/**`.

## Allowed Writes

Only:

- `tests/features/test_technical.py`
- `coordination/reports/TASK-139_REPORT.md`

Conditional minimal implementation write:

- `quant/features/technical.py` only if the newly added tests expose a real implementation defect that prevents the original TASK-139 requirements from being satisfied. If this file is changed, the report must explain exactly which defect was found and why the change was necessary.

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files other than `coordination/reports/TASK-139_REPORT.md`
- `coordination/reviews/**`
- `coordination/integrations/**`
- `coordination/handoffs/**`
- `quant/datahub/**`
- `tests/datahub/**`
- `quant/scanner/**`
- `quant/strategies/**`
- `quant/backtest/**`
- `quant/portfolio/**`
- `quant/notification/**`
- `quant/ai/**`
- `quant/ui/**`

Do not fetch live data, call source adapters, read credentials, use browser/session state, or introduce hidden network behavior.

## Rework Requirements

Add focused tests covering the Review findings:

1. EMA negative paths:
   - insufficient rows for the requested EMA window
   - invalid EMA window values

2. MACD negative paths:
   - insufficient rows for the requested long/signal window path
   - invalid window values, not only invalid short/long ordering

3. RSI negative paths:
   - invalid RSI window values
   - preserve existing insufficient-history behavior coverage or add it explicitly if not already covered by the current test suite

4. Stochastic/KDJ negative paths:
   - insufficient rows for the requested stochastic windows
   - invalid `k_window` and/or `d_window` values

Keep the tests deterministic, pure offline, and aligned with existing `tests/features/test_technical.py` style. Prefer direct `assertRaisesRegex` checks against the public calculation functions.

Do not change readiness-gate status, follow-up batches, or FeatureHub capability truth unless a real implementation defect is found that changes the evidence. This rework is test-completeness focused.

## Tests

Required default tests:

- `python3 -m unittest discover -s tests/features -p 'test_*.py'`

Run narrower focused tests during development as needed.

No live tests are required or allowed. Default tests must be offline-safe.

## Completion Report

Update `coordination/reports/TASK-139_REPORT.md` with a rework section including:

- files changed
- Review findings addressed
- tests added
- implementation changes, if any, and why they were necessary
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled result as `SKIP` because this is pure offline FeatureHub work
- deviations from this rework handoff
- remaining risks or follow-up tasks

## Acceptance Criteria

The rework is acceptable when:

- all missing EMA/MACD/RSI/stochastic negative-path coverage identified by Review is present
- tests pass under the required FeatureHub default suite
- no DataHub or downstream module implementation files are changed
- no hidden live/network behavior is introduced
- the TASK-139 report truthfully records the rework and verification

## Report Path

`coordination/reports/TASK-139_REPORT.md`

## Review Path

`coordination/reviews/TASK-139_REVIEW.md`

## Integration Path

N/A. Integration Agent is retired; Review is the closure gate before Controller.
