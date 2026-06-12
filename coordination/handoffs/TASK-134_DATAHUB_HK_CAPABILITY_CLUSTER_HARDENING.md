# TASK-134 DataHub Hong Kong capability cluster hardening

## Role

5.3 Execution

## Phase

Phase 2.5-P DataHub Personal Trading Perfection Re-Review.

## Context

Controller closed TASK-133 after Review accepted the A-share financial-indicator, announcement, and activity cluster hardening. TASK-133 strengthened `a_share_major_activity_events` with exchange-specific insider holding-change source truth, preserved accepted `a_share_financial_indicators` and `a_share_company_announcements` behavior, kept capability truth conservative, preserved default offline safety, and recorded live-enabled PASS evidence.

Phase 2.5-P remains open under `coordination/PHASE_GATE.md` because `build_default_personal_trading_readiness_report()` still reports `overall_status=blocked`, `phase_closure_ready=False`, and unresolved non-pass readiness batches. The current phase must continue with DataHub hardening before FeatureHub or downstream phases reopen.

Controller read DataHub readiness `follow_up_batches`. TASK-131, TASK-132, and TASK-133 covered:

- `a_share__datahub_hardening__a_share__batch_01`
- `a_share__datahub_hardening__a_share__batch_02`
- `a_share__datahub_hardening__a_share__batch_03`

The next executable current-phase capability cluster is:

- batch id: `hong_kong__datahub_hardening__hong_kong__batch_01`
- disposition: `datahub_hardening`
- capabilities:
  - `hk_universe_reference`
  - `hk_daily_bars`
  - `hk_corporate_actions`
  - `hk_valuation_history`
  - `hk_financial_data`
  - `hk_turnover_liquidity`

This is a coherent Hong Kong stock cluster because the items share the same domain, no-credential public-source breadth/history/source-redundancy theme, and DataHub adapter/source metadata surface. Do not split it into single-item work unless a concrete implementation or live-source blocker forces a focused rework.

The adjacent `hk_minute_bars` readiness batch has `disposition=owner_waiver_required`; no owner waiver or explicit HK minute-bar feasibility scope has been provided, so it is not part of this implementation handoff.

## Objective

Strengthen stable no-credential public-source proof for the Hong Kong stock batch capabilities where feasible, or truthfully constrain DataHub capability/source wording without promotion when public routes remain incomplete.

The work must improve one or more of:

- `hk_universe_reference`: full-market current-listed breadth, profile reconciliation, non-stock taxonomy truth, or lifecycle/delist limitation evidence beyond the accepted bounded stock-only routes.
- `hk_daily_bars`: history continuity, source freshness behavior, or public-source redundancy beyond the accepted `stock_hk_hist` / `stock_hk_daily` behavior.
- `hk_corporate_actions`: non-dividend corporate-action taxonomy breadth, batch behavior, or second-route consistency beyond accepted dividend/distribution routes.
- `hk_valuation_history`: current-dated valuation proof, broader dated history, metric/source-route truth, or redundancy beyond accepted `stock_hk_indicator_eniu` / optional Baidu supplementation limits.
- `hk_financial_data`: broader financial statement/indicator market breadth, report-period continuity, source-route/statement/metric truth, or classifier truthfulness beyond accepted HK financial live-classifier hardening.
- `hk_turnover_liquidity`: turnover-rate, float-share, spread/microstructure facts, dated liquidity semantics, or public-source redundancy beyond accepted volume/traded-amount source truth.

If a route cannot be proven through no-credential public sources, record that truth in capability/catalog wording and tests instead of promoting capability status.

## Allowed files

Execution may modify only:

- `quant/datahub/`
- `tests/datahub/`
- `coordination/reports/TASK-134_REPORT.md`

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
- Preserve accepted TASK-110 through TASK-118 behavior and provenance truth unless a genuine defect is found.
- Keep `hk_minute_bars` outside this handoff unless the owner explicitly provides waiver/feasibility scope in a later controller window.
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

Run the relevant Hong Kong adapter tests for each changed capability path, such as:

- `python3 -m unittest tests.datahub.test_akshare_hk_instrument_master_adapter`
- `python3 -m unittest tests.datahub.test_akshare_hk_adapter`
- `python3 -m unittest tests.datahub.test_akshare_hk_corporate_actions_adapter`
- `python3 -m unittest tests.datahub.test_akshare_hk_valuation_snapshot_adapter`
- `python3 -m unittest tests.datahub.test_akshare_hk_financial_data_adapter`

If a live smoke already exists or is added/updated for any materially changed real-source path, it must be:

- explicitly marked/gated by environment variable
- skipped by default
- run once with live enabled when feasible

Default tests must remain offline-safe.

## Report requirements

Write `coordination/reports/TASK-134_REPORT.md` with:

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
- `hk_minute_bars` remains outside scope unless a later controller handoff explicitly opens it
- no downstream module or future phase is implemented
- `coordination/reports/TASK-134_REPORT.md` is complete
