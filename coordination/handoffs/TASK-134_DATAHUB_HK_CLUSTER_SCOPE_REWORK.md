# TASK-134 DataHub Hong Kong cluster scope rework

## Role

5.3 Execution

## Phase

Phase 2.5-P DataHub Personal Trading Perfection Re-Review.

## Context

The initial TASK-134 execution strengthened only `hk_corporate_actions` and recorded gated live PASS evidence for that changed path. Review did not reject that implementation path on its own merits.

Review rejected TASK-134 closure because the original handoff assigned the coherent readiness batch `hong_kong__datahub_hardening__hong_kong__batch_01` and explicitly required the batch not be split into single-item work unless concrete implementation or live-source blockers forced a focused rework. The execution report left these capabilities untouched without blocker evidence:

- `hk_universe_reference`
- `hk_daily_bars`
- `hk_valuation_history`
- `hk_financial_data`
- `hk_turnover_liquidity`

This rework is the minimal follow-up for that Review finding. It must not merge unrelated readiness `follow_up_batches` or ordinary future hardening items.

## Objective

Resolve the TASK-134 Review blocker by completing the original HK batch scope for the five remaining capabilities, or by recording concrete implementation/live-source blocker evidence for any capability that cannot be strengthened in this rework.

For each remaining capability, do one of the following:

- add focused DataHub hardening where stable no-credential public routes make it feasible;
- tighten capability/source-catalog wording and tests so the current limitation is explicit and not over-claimed;
- record concrete blocker evidence in the report if investigation shows no feasible repository change is available in this rework.

Preserve the accepted `hk_corporate_actions` TASK-134 behavior unless the rework exposes a genuine defect.

## Required per-capability coverage

- `hk_universe_reference`: address current-listed breadth, profile reconciliation, non-stock taxonomy truth, or dated lifecycle/delist limitation evidence.
- `hk_daily_bars`: address history continuity, source freshness behavior, or public-source redundancy beyond the accepted `stock_hk_hist` / `stock_hk_daily` behavior.
- `hk_valuation_history`: address current-dated valuation proof, broader dated history, metric/source-route truth, or redundancy beyond the accepted `stock_hk_indicator_eniu` / optional Baidu supplementation limits.
- `hk_financial_data`: address broader statement/indicator market breadth, report-period continuity, source-route/statement/metric truth, or live-classifier truthfulness beyond the accepted classifier-only hardening.
- `hk_turnover_liquidity`: address turnover-rate, float-share, spread/microstructure facts, dated liquidity semantics, or public-source redundancy beyond accepted volume/traded-amount truth.

If a capability cannot be improved with stable no-credential public sources, leave it conservative and provide the specific route/contract/source reason. Do not promote a capability to `covered` without proving the full practical public-source/no-paid breadth required by the readiness reason.

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

- Stay inside DataHub.
- Do not implement FeatureHub indicators, scanner ranking, strategies, backtests, portfolio/signal/risk logic, AI reports, notifications, UI, or automated trading.
- Do not add paid/private credential requirements.
- Do not use cookies, tokens, private accounts, or credentialed endpoints.
- Keep `hk_minute_bars` outside this handoff; it remains owner-waiver-required unless a later controller handoff explicitly opens it.
- Do not remove or weaken the already accepted TASK-134 `hk_corporate_actions` batch behavior unless a genuine defect is found and fixed.
- Keep default tests offline-safe.
- Keep live tests explicitly environment-gated and skipped by default.
- Route-name-bearing signature, payload, schema, normalization, or contract defects introduced or exposed by repository code must remain failures, not environment/source skips.

## Required tests

Run the narrowest relevant offline tests for changed files. At minimum, run:

- `python3 -m unittest tests.datahub.test_source_capabilities`
- `python3 -m unittest tests.datahub.test_source_catalog`

Run relevant HK adapter tests for every changed capability path, such as:

- `python3 -m unittest tests.datahub.test_akshare_hk_instrument_master_adapter`
- `python3 -m unittest tests.datahub.test_akshare_hk_adapter`
- `python3 -m unittest tests.datahub.test_akshare_hk_valuation_snapshot_adapter`
- `python3 -m unittest tests.datahub.test_akshare_hk_financial_data_adapter`

Also rerun the corporate-actions tests if the rework touches shared HK corporate-action behavior or shared catalog/capability wording:

- `python3 -m unittest tests.datahub.test_akshare_hk_corporate_actions_adapter`
- `python3 -m unittest tests.datahub.test_akshare_hk_corporate_actions_live`

If a live smoke exists or is added/updated for a materially changed real-source path, run it once with live enabled when feasible and record PASS/SKIP/FAIL truthfully in the report with root-cause evidence.

## Report requirements

Update `coordination/reports/TASK-134_REPORT.md` with:

- files changed
- implementation or blocker summary for each of the five remaining capabilities
- confirmation that accepted `hk_corporate_actions` behavior is preserved, or a clear description of any genuine defect fixed
- tests run
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence for each materially changed real-source path
- deviations from this handoff
- risks or follow-up tasks

## Closure standard

Review may accept only if:

- the rework stays within Phase 2.5-P DataHub scope and allowed files
- each of the five remaining HK capabilities is either hardened or has concrete blocker/limitation evidence recorded
- no capability/source-catalog wording overstates unproven public-source breadth
- default tests remain offline-safe
- materially changed real-source paths have gated live evidence or truthful live SKIP/FAIL root-cause evidence
- the accepted `hk_corporate_actions` TASK-134 behavior is preserved unless a genuine defect required a focused fix
- `hk_minute_bars` remains outside scope
- no downstream module or future phase is implemented
- `coordination/reports/TASK-134_REPORT.md` is complete enough for fresh Review
