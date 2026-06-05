# TASK-071 DataHub Trading-Usable Gap Audit

## Role

5.3 Execution Window.

## Context

The owner replaced foundation-only phase gates with trading-usable completion gates. The controller has reopened the earliest incomplete prerequisite phase: Phase 2.5 DataHub Trading-Usable Hardening.

`TASK-070` has been deferred back to Backlog. Do not continue Phase 5 work in this task.

## Objective

Audit the current DataHub implementation against the DataHub Trading-Usable Completion Standard in `coordination/ROADMAP.md`.

The output should give the controller a practical, prioritized DataHub hardening queue so the pipeline can keep cycling on DataHub until it is accepted, blocked, or owner-waived before moving to FeatureHub.

## Allowed Writes

Only:

- `coordination/reports/TASK-071_REPORT.md`

## Read Scope

Read as needed:

- `AGENTS.md`
- `coordination/ROADMAP.md`
- `coordination/PHASE_GATE.md`
- `coordination/PROJECT_STATE.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/TASK_BOARD.md`
- `coordination/handoffs/`
- `coordination/reports/`
- `coordination/reviews/`
- `coordination/integrations/`
- `quant/datahub/`
- `tests/datahub/`

Do not read `coordination/agent_runs/**` unless a specific contradiction cannot be resolved from the coordination files above.

## Forbidden Changes

Do not modify:

- `quant/datahub/`
- `tests/datahub/`
- `quant/features/`
- `quant/scanner/`
- `quant/strategies/`
- `quant/backtest/`
- `quant/portfolio/`
- `quant/notification/`
- `quant/ai/`
- `quant/ui/`
- controller-owned coordination files

Do not implement missing capabilities. This task is audit-only.

## Required Audit Coverage

Compare current DataHub code, tests, source catalog/capability metadata, and completed lifecycle artifacts against these DataHub trading-usable capability groups:

- symbol/instrument reference coverage for A-share, Hong Kong stock, ETF/fund, indices, sectors, and concepts
- daily and intraday market data access, freshness, and trading-calendar handling
- corporate actions, listing/delisting/ST, suspension/resumption, limit-up/down, margin financing/lending, capital flow, northbound or major-activity data where available
- financial statements, financial indicators, valuation history, fund holdings/scale/flow, index constituents and weights, sector membership/history
- macro observations, policy documents, news, and announcements
- batch-capable and parameterized source access rather than one-symbol or one-fund examples only
- local raw/normalized persistence, refresh metadata, data-quality reports, source-capability metadata, and failure diagnostics
- gated live evidence for each real-source capability, or an explicit blocked/waived status

## Classification Rules

For each capability group or meaningful sub-capability, classify status as one of:

- `covered`: broad enough for practical DataHub usage and backed by evidence
- `partial`: implemented but narrow, one-symbol/one-fund, limited route, limited history, limited market, or incomplete tests/live evidence
- `planned`: stable contract or metadata exists but practical source coverage is not proven
- `missing`: no meaningful current DataHub implementation or contract support found
- `blocked`: requires paid/private credentials, unavailable upstream access, or owner action

Paid or private credential requirements must be marked `blocked`. Do not use credentials and do not make the phase wait on unprovided credentials unless the owner later opens that scope.

## Required Report Contents

Write `coordination/reports/TASK-071_REPORT.md` with:

- files changed
- tests run
- default network behavior
- live-enabled result
- deviations from the handoff
- risks or follow-up tasks
- a capability matrix with `covered` / `partial` / `planned` / `missing` / `blocked`
- evidence for each status, citing local files or completed task artifacts
- paid/private credential blockers called out explicitly
- a prioritized list of the next DataHub hardening tasks
- one recommended next execution handoff, including:
  - proposed task id/title
  - objective
  - allowed implementation files
  - likely tests
  - why this is the highest-priority next gap

Keep the report practical and controller-ready. Do not paste long source snippets.

## Tests

No code tests are required because this is audit-only.

If you choose to run tests to verify current DataHub behavior, run only offline-safe tests under `tests/datahub/`. Do not run live-enabled tests, do not set live environment variables, and do not use credentials.

## Completion Criteria

The task is complete when `coordination/reports/TASK-071_REPORT.md` clearly tells the controller:

- what DataHub can already do
- what is only partial or planned
- what is missing
- what is blocked by paid/private credentials or external limitations
- which DataHub hardening task should be dispatched next
