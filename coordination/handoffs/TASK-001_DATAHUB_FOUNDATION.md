# TASK-001: DataHub Foundation Skeleton

## Owner Role

5.3 execution window

## Status

Ready for execution

## Context

Phase 0 has initialized the project governance and architecture documents. The next step is to create the first implementable DataHub foundation without expanding into feature engineering, scanning, strategies, backtesting, AI reports, notifications, automated trading, or UI.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`

## Goal

Create a minimal DataHub package skeleton that can support future local data warehouse work while remaining offline-testable by default.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `pyproject.toml` if needed for test configuration
- `.gitignore` if needed for local data/cache exclusions
- `coordination/reports/TASK-001_REPORT.md`

## Forbidden Files

The execution window must not modify:

- `coordination/PROJECT_STATE.md`
- `coordination/ROADMAP.md`
- `coordination/TASK_BOARD.md`
- `coordination/DECISIONS.md`
- `coordination/RISKS.md`
- `coordination/INTERFACES.md`
- `quant/features/**`
- `quant/strategies/**`
- `quant/backtest/**`
- `quant/scanner/**`
- `quant/portfolio/**`
- `quant/notification/**`
- `quant/ai/**`
- `quant/ui/**`

## Implementation Requirements

Implement only DataHub foundation code.

Minimum expected pieces:

- package marker for `quant/datahub`
- a small configuration object for local DataHub paths
- a dataset name or registry foundation for future contracts
- a source adapter protocol or abstract interface with no real live source implementation
- a local storage path helper that does not fetch data
- offline tests using local temporary directories or fixtures

Do not implement:

- real market data downloading
- technical indicators
- stock selection rules
- strategy logic
- backtest logic
- AI explanation logic
- notification logic
- UI logic
- automated trading

## Testing Requirements

Default tests must be offline.

Live tests are forbidden for TASK-001.

Run the relevant local test command and report the result. If a test runner is not yet configured, create the smallest reasonable test setup needed for DataHub foundation tests.

## Acceptance Criteria

The task is acceptable when:

- DataHub has a clear minimal package skeleton
- no future-phase module contains new logic
- default tests run without live network access
- the report file exists at `coordination/reports/TASK-001_REPORT.md`
- report includes files changed, tests run, network behavior, deviations, and follow-ups

## Report Path

`coordination/reports/TASK-001_REPORT.md`

## Review Path

`coordination/reviews/TASK-001_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-001_INTEGRATION.md`

## Out of Scope

Everything outside DataHub foundation setup is out of scope.
