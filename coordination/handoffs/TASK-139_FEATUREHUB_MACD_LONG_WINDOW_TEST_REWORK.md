# TASK-139 FeatureHub MACD long-window invalid-value test rework

## Role

5.3 Execution Window.

## Phase

Phase 3-P FeatureHub Personal Trading Perfection Re-Review.

## Context

TASK-139 remains open after a second Review rejection in `coordination/reviews/TASK-139_REVIEW.md`.

The previous focused test-coverage rework added most missing technical-indicator negative-path coverage and preserved offline-safe default tests. Review accepted the general scope and default network behavior, but found one remaining blocker: `calculate_macd()` validates `long_window` independently, and the test suite still lacks a direct invalid `long_window` regression. The report also currently overstates MACD invalid-window coverage as fully addressed.

This is a very small Review rework. Do not merge it with FeatureHub readiness `follow_up_batches`, valuation/flow work, relative-feature work, batch API work, downstream contract work, or any ordinary FeatureHub hardening item.

## Objective

Add the missing offline regression test for invalid `MACD long_window` values and update the TASK-139 report so it truthfully records the focused rework and no longer overstates the previous MACD invalid-window coverage.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-139_FEATUREHUB_TECHNICAL_INDICATORS_CORE_EXPANSION.md`
- `coordination/handoffs/TASK-139_FEATUREHUB_TECHNICAL_INDICATOR_TEST_COVERAGE_REWORK.md`
- `coordination/handoffs/TASK-139_FEATUREHUB_MACD_LONG_WINDOW_TEST_REWORK.md`
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

- `quant/features/technical.py` only if the newly added test exposes a real implementation defect in `calculate_macd()` validation. If this file is changed, the report must explain exactly which defect was found and why the change was necessary.

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

Add focused coverage for the remaining Review finding:

1. MACD invalid `long_window` value:
   - exercise the public `calculate_macd()` API with an invalid `long_window` value, such as `long_window=0`
   - assert the expected validation error with `assertRaisesRegex`, following the style already used in `tests/features/test_technical.py`
   - keep the test distinct enough that Review can see the independent `long_window` validation branch is covered, not merely invalid short/long ordering or invalid `signal_window`

Update `coordination/reports/TASK-139_REPORT.md` with a new rework section that records:

- the added `MACD long_window` invalid-value regression
- whether any implementation change was needed
- the tests run and their PASS/SKIP/FAIL result
- default network behavior
- live-enabled result as `SKIP` because this is pure offline FeatureHub work
- deviations, if any
- remaining risks or follow-up tasks, if any

Do not change readiness-gate status, follow-up batches, FeatureHub capability truth, or any downstream module state.

## Tests

Required default tests:

- `python3 -m unittest discover -s tests/features -p 'test_*.py'`

Run narrower focused tests during development as needed.

No live tests are required or allowed. Default tests must be offline-safe.

## Acceptance Criteria

The rework is acceptable when:

- `tests/features/test_technical.py` has direct invalid `long_window` regression coverage for `calculate_macd()`
- `coordination/reports/TASK-139_REPORT.md` truthfully records the second focused rework and no longer overstates the MACD invalid-window coverage gap
- the required FeatureHub default suite passes
- no DataHub or downstream module implementation files are changed
- no hidden live/network behavior is introduced

## Report Path

`coordination/reports/TASK-139_REPORT.md`

## Review Path

`coordination/reviews/TASK-139_REVIEW.md`

## Integration Path

N/A. Integration Agent is retired; Review is the closure gate before Controller.
