# TASK-122 - DataHub ETF/fund scale/share signed metric rework

## Role

5.3 Execution

## Phase

Phase 2.5-P DataHub Personal Trading Perfection Re-Review.

## Context

The initial TASK-122 execution added `DatasetName.FUND_SCALE_SHARE_SNAPSHOT` and kept `fund_scale_and_share` conservative at `partial`. Review rejected closure because the new canonical contract globally requires `metric_value` to be nonnegative, while the original handoff explicitly allowed scale/share change facts. Valid share-change observations can be negative, and the accepted legacy `FUND_FLOW.shares_change` field is already sign-bearing.

This is a focused rework. Do not redo the broader schema/capability implementation and do not expand into adapter work.

## Objective

Fix the `FUND_SCALE_SHARE_SNAPSHOT` metric-value semantics so the canonical ETF/fund scale/share contract can represent legitimate negative change metrics without weakening validation for inherently nonnegative level metrics such as fund scale, AUM, shares outstanding, or share units.

## Allowed Files

Execution may modify only:

- `quant/datahub/datasets.py`
- `tests/datahub/test_datasets.py`
- `coordination/reports/TASK-122_REPORT.md`

Do not edit controller-owned coordination state files.

## Required Work

1. Adjust the `FUND_SCALE_SHARE_SNAPSHOT` semantic validation.
   - Negative `metric_value` must be accepted for explicit change-style metrics, such as share-change or scale/share-change observations.
   - Inherently nonnegative level metrics must still reject negative `metric_value`.
   - The rule must be deterministic and based on stable contract fields such as `metric_code` and/or `observation_type`.
   - Do not remove required identity/date/source fields.

2. Add focused dataset tests.
   - Cover a valid negative share-change-style `FUND_SCALE_SHARE_SNAPSHOT` record.
   - Cover rejection of a negative nonnegative-level metric.
   - Preserve existing valid/invalid coverage for required fields and existing ETF/fund dataset compatibility.

3. Preserve scope.
   - Do not change adapters.
   - Do not change source catalog or capability status unless the test fix exposes a directly necessary schema reference correction.
   - Do not promote `fund_scale_and_share`.
   - Do not introduce hidden default live network calls.

4. Update `coordination/reports/TASK-122_REPORT.md`.
   - Add a rework section summarizing the signed-metric fix.
   - List files changed.
   - List tests run and results.
   - State default network behavior.
   - State that no live test was required because this rework remains schema/test-only and does not change adapters.
   - Record deviations and residual risks/follow-ups.

## Tests

Run focused offline tests covering the changed files:

- `python3 -m unittest tests.datahub.test_datasets`

Also rerun the original TASK-122 focused set unless there is a clear local blocker:

- `python3 -m unittest tests.datahub.test_datasets tests.datahub.test_source_capabilities tests.datahub.test_source_catalog`

No live smoke is required or permitted for this rework because adapter behavior is not in scope.

## Guardrails

- Stay inside DataHub schema/test/report scope listed above.
- Do not implement FeatureHub, Scanner, StrategyLab, BacktestEngine, portfolio/signal/risk, AI, notification, UI, or automated trading logic.
- Do not use credentials, tokens, cookies, or private account data.
- Do not introduce hidden default live network calls.
- Do not mark `fund_scale_and_share` covered from this contract/test rework.
