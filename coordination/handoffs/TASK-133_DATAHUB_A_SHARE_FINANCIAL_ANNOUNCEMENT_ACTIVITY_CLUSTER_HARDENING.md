# TASK-133 DataHub A-share financial-indicator, announcement, and activity cluster hardening

## Role

5.3 Execution

## Phase

Phase 2.5-P DataHub Personal Trading Perfection Re-Review.

## Context

Controller closed TASK-132 after Review accepted the focused northbound fallback truth rework. Phase 2.5-P remains open under `coordination/PHASE_GATE.md` because `build_default_personal_trading_readiness_report()` still reports `overall_status=blocked`, `phase_closure_ready=False`, and unresolved non-pass follow-up batches.

Controller read DataHub readiness `follow_up_batches`. TASK-131 covered:

- `a_share__datahub_hardening__a_share__batch_01`

TASK-132 covered:

- `a_share__datahub_hardening__a_share__batch_02`

The next executable current-phase capability cluster is:

- batch id: `a_share__datahub_hardening__a_share__batch_03`
- disposition: `datahub_hardening`
- capabilities:
  - `a_share_financial_indicators`
  - `a_share_company_announcements`
  - `a_share_major_activity_events`

This is a coherent A-share cluster because the items share the same domain, public-source breadth/history/source-redundancy theme, and DataHub adapter/source metadata surface. Do not split it into single-item work unless a concrete implementation or live-source blocker forces a focused rework.

## Objective

Strengthen stable no-credential public-source proof for the A-share batch_03 capabilities where feasible, or truthfully constrain DataHub capability/source wording without promotion when public routes remain incomplete.

The work must improve one or more of:

- `a_share_financial_indicators`: broader indicator family coverage, longer report-period continuity, or public-source redundancy beyond the current Eastmoney `stock_financial_analysis_indicator_em` route and currently proven indicator-family coverage.
- `a_share_company_announcements`: announcement category breadth, broader history continuity, or public-source redundancy beyond the currently proven bounded AKShare routes.
- `a_share_major_activity_events`: major-activity taxonomy breadth, longer-history continuity, or public-source redundancy beyond the current bounded AKShare block-trade detail and symbol-date summary routes.

If a route cannot be proven through no-credential public sources, record that truth in capability/catalog wording and tests instead of promoting capability status.

## Allowed files

Execution may modify only:

- `quant/datahub/`
- `tests/datahub/`
- `coordination/reports/TASK-133_REPORT.md`

Execution must not modify:

- `AGENTS.md`
- `coordination/PROJECT_STATE.md`
- `coordination/ROADMAP.md`
- `coordination/TASK_BOARD.md`
- `coordination/DECISIONS.md`
- `coordination/RISKS.md`
- `coordination/INTERFACES.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- any downstream module outside DataHub

## Scope constraints

- Stay inside DataHub. Do not implement FeatureHub indicators, scanner ranking, strategies, backtests, portfolio/signal/risk logic, AI reports, notifications, UI, or automated trading.
- Do not add paid/private credential requirements.
- Do not use cookies, tokens, private accounts, or credentialed endpoints.
- Preserve accepted TASK-107 financial-indicator behavior and provenance truth unless a genuine defect is found.
- Preserve accepted TASK-108 announcement date-window/fallback truth unless a genuine defect is found.
- Preserve accepted TASK-109 major-activity event behavior and source-route truth unless a genuine defect is found.
- Keep capability states conservative. Do not mark a capability `covered` unless the implementation proves the full practical public-source/no-paid breadth required by the readiness reason.

## Required implementation guidance

- Prefer existing adapter/source-catalog/source-capability patterns over new abstractions.
- Use structured route APIs and schema validation already present in DataHub.
- Add or update focused offline tests for any changed source normalization, fallback, capability wording, catalog wording, or validation behavior.
- If live-route evidence exposes upstream unavailability, diagnose whether repository code/tests can be improved. Truthfully classify the live result as PASS, SKIP, or FAIL in the report with root-cause evidence.
- Route-name-bearing signature, payload, schema, normalization, or contract defects introduced or exposed by repository code must remain failures, not environment/source skips.

## Required tests

Run the narrowest relevant offline tests for changed files. At minimum, run capability/catalog tests if source metadata changes:

- `python3 -m unittest tests.datahub.test_source_capabilities`
- `python3 -m unittest tests.datahub.test_source_catalog`

Run the relevant adapter tests for each changed capability path. If a live smoke already exists or is added/updated for any materially changed real-source path, it must be:

- explicitly marked/gated by environment variable
- skipped by default
- run once with live enabled when feasible

Default tests must remain offline-safe.

## Report requirements

Write `coordination/reports/TASK-133_REPORT.md` with:

- files changed
- implementation summary by capability
- tests run
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence for each materially changed real-source path
- deviations from this handoff
- risks or follow-up tasks

## Closure standard

Review may accept only if:

- changes stay within the allowed DataHub scope
- default tests remain offline-safe
- real-source changes have gated live evidence or truthful live SKIP/FAIL root-cause evidence
- source/capability/catalog wording does not overstate unproven public-source breadth
- no downstream module or future phase is implemented
- `coordination/reports/TASK-133_REPORT.md` is complete
