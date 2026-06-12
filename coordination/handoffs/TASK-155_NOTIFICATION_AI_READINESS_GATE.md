# TASK-155 Notification and AIReport Personal Trading Readiness Gate

## Role

5.3 Execution Window.

## Phase

Phase 7: Notification and AIReport Personal Trading Perfection.

## Context

Phase 6 PortfolioMonitor, SignalEngine, and RiskEngine is closed after accepted TASK-154 Review and Controller phase-gate verification. The Phase 6 readiness gate now reports `phase_closure_ready=true`, status counts `pass=6`, `warn=0`, `blocked=0`, `fail=0`, with no remaining follow-up queue or batches.

Phase 7 starts from placeholder notification and AI modules. It must not jump directly into external alert channels or external AI provider calls. The first step is a deterministic local/offline readiness gate that classifies current Notification and AIReport coverage against `coordination/ROADMAP.md`, emits a Controller-ready follow-up queue, and groups later implementation work into coherent capability batches.

## Objective

Create the initial local/offline Phase 7 readiness gate for Notification and AIReport.

This is audit/gate work. It must not implement production alert delivery, external AI calls, paid provider integrations, browser/session workflows, push notifications, email/SMS/IM integrations, scheduled jobs, UI, automated trading, or real data fetching.

## Required Reading

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-155_NOTIFICATION_AI_READINESS_GATE.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/ROADMAP.md`
- `coordination/PHASE_GATE.md`
- `coordination/reports/TASK-151_REPORT.md`
- `coordination/reviews/TASK-151_REVIEW.md`
- `coordination/reports/TASK-152_REPORT.md`
- `coordination/reviews/TASK-152_REVIEW.md`
- `coordination/reports/TASK-153_REPORT.md`
- `coordination/reviews/TASK-153_REVIEW.md`
- `coordination/reports/TASK-154_REPORT.md`
- `coordination/reviews/TASK-154_REVIEW.md`
- `quant/notification/`
- `quant/ai/`

Read upstream contracts under `quant/portfolio/`, `quant/scanner/`, `quant/strategies/`, `quant/backtest/`, `quant/features/`, or `quant/datahub/` only if needed for interface awareness. Do not change upstream files.

Do not read `coordination/agent_runs/**`.

## Allowed Writes

Only:

- `quant/notification/**`
- `quant/ai/**`
- `tests/notification/**`
- `tests/ai/**`
- `coordination/reports/TASK-155_REPORT.md`

If `tests/notification/` or `tests/ai/` does not exist, create it.

Suggested implementation locations:

- `quant/notification/personal_readiness.py`
- `quant/ai/personal_readiness.py`
- `tests/notification/test_personal_readiness.py`
- `tests/ai/test_personal_readiness.py`
- `quant/notification/__init__.py` / `quant/ai/__init__.py` only for minimal exports if needed

## Forbidden Writes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files other than `coordination/reports/TASK-155_REPORT.md`
- `coordination/reviews/**`
- `coordination/integrations/**`
- `coordination/handoffs/**`
- `coordination/agent_runs/**`
- `quant/datahub/**`
- `tests/datahub/**`
- `quant/features/**`
- `tests/features/**`
- `quant/scanner/**`
- `tests/scanner/**`
- `quant/strategies/**`
- `tests/strategies/**`
- `quant/backtest/**`
- `tests/backtest/**`
- `quant/portfolio/**`
- `tests/portfolio/**`
- `quant/ui/**`

## Audit Requirements

The readiness gate must classify Notification and AIReport against the `coordination/ROADMAP.md` Phase 7 Personal Trading Perfection Standard.

At minimum, include capability groups for:

- alert routing, throttling, state, and audit logs
- data-grounded AI explanations that cite DataHub, FeatureHub, Scanner, SignalEngine, RiskEngine, and portfolio inputs rather than inventing hidden analysis
- daily and weekly summaries, signal narratives, risk notes, and source-linked report artifacts
- tests for alert deduplication, blocked alerts, missing data, and explanation grounding

For each group, record whether current implementation is `pass`, `warn`, `blocked`, or `fail`, with evidence based on current Notification/AI files and accepted upstream lifecycle artifacts.

The readiness output must include:

- `phase_closure_ready`
- status counts for `pass`, `warn`, `blocked`, and `fail`
- capability items with stable ids, names, statuses, evidence, limitations, and recommended follow-up disposition
- a deterministic `follow_up_queue`
- coherent `follow_up_batches` suitable for later Controller dispatch, normally grouping 2-6 related items by workflow or contract surface
- a recommended next executable Phase 7 handoff title and rationale

Because Phase 7 starts from placeholder modules, the gate should be conservative. Missing production capability should be represented as `warn` or `blocked` as appropriate and must not be treated as completion.

## Expected Initial Follow-up Themes

Use the roadmap and observed local code state to decide the exact final queue, but the gate should at least consider these coherent Phase 7 themes:

- local alert contract, routing policy, throttle/deduplication state, and audit-log foundation
- deterministic alert approval/blocking behavior over caller-provided structured signal and risk inputs
- grounded explanation and citation contract foundation over caller-provided DataHub/FeatureHub/Scanner/SignalEngine/RiskEngine evidence
- report artifact contracts for daily/weekly summaries, signal narratives, risk notes, and source-linked records
- offline regression coverage for alert deduplication, blocked alerts, missing evidence, and explanation grounding

Single-item batches are allowed only for Review rework, external-provider or credential blockers, cross-phase boundaries, or when no adjacent unresolved item remains.

## Implementation Boundaries

The task may add readiness dataclasses, enums, builders, exports, and deterministic tests.

Do not implement:

- production notification delivery
- external AI/model calls, prompt execution, API clients, or paid provider integrations
- push/email/SMS/IM/webhook delivery
- scheduled/background alert jobs
- report generation beyond readiness/audit classification
- portfolio/signal/risk logic
- Scanner, StrategyLab, BacktestEngine, FeatureHub, or DataHub logic
- local warehouse reads
- browser/session state
- UI or automated trading

## Tests

Required default tests:

- `python3 -m unittest discover -s tests/notification -p 'test_*.py'`
- `python3 -m unittest discover -s tests/ai -p 'test_*.py'`

Run narrower focused tests during development as needed. A broader `python3 -m unittest discover -s tests -p 'test_*.py'` run is allowed if useful and must remain offline-safe.

No live tests are required or allowed. Default tests must be offline-safe.

## Network and Data Rules

- Default tests must be offline-safe.
- No live network calls.
- No external AI/model API calls.
- No alert delivery to real channels.
- No warehouse reads.
- No credentials, private account data, brokerage sessions, browser/session state, or hidden clock dependency.
- Use caller-provided/local code evidence only.

## Completion Report

Write `coordination/reports/TASK-155_REPORT.md` with:

- files changed
- readiness gate summary, including `phase_closure_ready`, status counts, follow-up queue count, and follow-up batch count
- recommended next executable Phase 7 handoff
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled result as `SKIP` because this is local audit-only Notification/AIReport work
- deviations from this handoff
- risks or follow-up tasks
