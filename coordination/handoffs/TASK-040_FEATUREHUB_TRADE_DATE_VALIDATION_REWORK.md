# TASK-040 Rework: FeatureHub Trade Date Validation

## Task ID

TASK-040

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 3: FeatureHub

## Context

The initial TASK-040 execution produced FeatureHub foundation contract primitives and offline tests. Review rejected the result with one blocking contract correctness finding:

- `trade_date` validation accepts `datetime` values because `datetime` is a subclass of `date`.
- `tests/features/test_contracts.py` does not cover the invalid `trade_date=datetime(...)` path.

This rework must address only that finding. Do not expand FeatureHub behavior beyond the existing foundation-contract scope.

The execution window must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-040_FEATUREHUB_FOUNDATION_CONTRACTS.md`
- `coordination/reports/TASK-040_REPORT.md`
- `coordination/reviews/TASK-040_REVIEW.md`
- `coordination/handoffs/TASK-040_FEATUREHUB_TRADE_DATE_VALIDATION_REWORK.md`

## Goal

Reject timestamp-bearing `datetime` values for `trade_date` while continuing to accept plain `date` values, and add a deterministic offline regression test for that invalid case.

## Allowed Files

The execution window may modify only:

- `quant/features/contracts.py`
- `tests/features/test_contracts.py`
- `coordination/reports/TASK-040_REPORT.md`

## Forbidden Files

The execution window must not modify:

- `coordination/PROJECT_STATE.md`
- `coordination/ROADMAP.md`
- `coordination/TASK_BOARD.md`
- `coordination/DECISIONS.md`
- `coordination/RISKS.md`
- `coordination/INTERFACES.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/reviews/**`
- `coordination/integrations/**`
- `coordination/handoffs/**`
- `quant/datahub/**`
- `quant/strategies/**`
- `quant/backtest/**`
- `quant/scanner/**`
- `quant/portfolio/**`
- `quant/notification/**`
- `quant/ai/**`
- `quant/ui/**`

## Implementation Requirements

1. Fix `trade_date` validation so `datetime.datetime` values fail validation even though plain `datetime.date` values pass.
2. Add an offline regression test that passes a `datetime(2026, 6, 3, 9, 30, 0)` or equivalent timestamp-bearing value as `trade_date` and asserts validation fails.
3. Keep existing FeatureHub contract shape, field names, schema version, and allowed source-dataset behavior unless a tiny local adjustment is strictly necessary for the review finding.
4. Do not add real feature calculations, DataHub source access, persistence, scheduling, orchestration, scanner ranking, strategy/backtest/signal/risk/portfolio logic, notifications, AI reports, UI, or automated trading behavior.

## Testing Requirements

Run focused tests:

`python3 -m unittest discover -s tests/features -p 'test_*.py'`

Run DataHub default regression because TASK-040 imports DataHub dataset identifiers:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Default tests must remain offline-safe. No live tests are required or allowed for this rework.

## Report Requirements

Update `coordination/reports/TASK-040_REPORT.md` with:

- files changed during rework
- tests run and results
- default network behavior
- live-enabled result as `SKIP` because TASK-040 is not a real-source task and this handoff forbids live tests
- deviations, if any
- risks or follow-up tasks

## Acceptance Criteria

The rework is acceptable when:

- `trade_date=datetime(...)` is rejected by validation
- plain `date(...)` trade dates still pass existing valid-record coverage
- the new negative regression test is present and offline-only
- focused FeatureHub tests pass
- DataHub default regression passes
- no controller-owned state files, DataHub implementation files, or future phase modules are modified by execution

## Report Path

`coordination/reports/TASK-040_REPORT.md`

## Review Path

`coordination/reviews/TASK-040_REVIEW.md`

## Integration Path

No integration is allowed until a fresh Review Agent result accepts this rework and explicitly allows Controller closure or integration.
