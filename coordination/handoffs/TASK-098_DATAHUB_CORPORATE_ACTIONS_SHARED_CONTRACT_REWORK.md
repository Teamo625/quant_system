# TASK-098 DataHub Corporate-Actions Shared Contract Rework

## Role

5.3 Execution Window.

## Context

TASK-098 initial execution hardened A-share `DatasetName.CORPORATE_ACTIONS` taxonomy by making `action_family` and `source_route` required top-level fields and by adding no-credential public rights-issue coverage.

The Review Agent rejected closure because this shared `CORPORATE_ACTIONS` contract change regressed existing Hong Kong corporate-actions coverage. HK corporate-actions records emitted by `AkshareHKCorporateActionsAdapter` still lack the newly required top-level fields, so existing HK corporate-actions adapter and live tests fail schema validation.

Review file:

- `coordination/reviews/TASK-098_REVIEW.md`

Blocking findings to address:

- `DatasetName.CORPORATE_ACTIONS` now globally requires `action_family` and `source_route`.
- HK corporate-actions records do not emit those required top-level fields.
- `tests/datahub/test_akshare_hk_corporate_actions_adapter.py` and `tests/datahub/test_akshare_hk_corporate_actions_live.py` fail with missing required fields.
- The execution report does not yet acknowledge or resolve the cross-suite regression.

## Objective

Fix the smallest stable DataHub-only contract rollout issue so both A-share and HK `DatasetName.CORPORATE_ACTIONS` records validate consistently after the TASK-098 taxonomy hardening.

The preferred path is to preserve explicit corporate-action taxonomy where source-backed while making existing HK corporate-actions records satisfy the shared schema. If implementation analysis shows the fields should not be globally required, narrow the schema requirement instead, but the result must preserve A-share TASK-098 taxonomy value and must not hide the HK regression.

This is a same-task rework. Do not close TASK-098, do not enter Integration, and do not dispatch a new domain task.

## Allowed Writes

Only:

- `quant/datahub/datasets.py`
- `quant/datahub/adapters/akshare.py`
- `tests/datahub/test_datasets.py`
- `tests/datahub/test_akshare_a_share_corporate_actions_adapter.py`
- `tests/datahub/test_akshare_a_share_corporate_actions_live.py`
- `tests/datahub/test_akshare_hk_corporate_actions_adapter.py`
- `tests/datahub/test_akshare_hk_corporate_actions_live.py`
- `coordination/reports/TASK-098_REPORT.md`

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files except `coordination/reports/TASK-098_REPORT.md`
- `coordination/reviews/**`
- `coordination/integrations/**`
- unrelated DataHub adapters or tests
- `quant/features/`
- `quant/scanner/`
- `quant/strategies/`
- `quant/backtest/`
- `quant/portfolio/`
- `quant/notification/`
- `quant/ai/`
- `quant/ui/`

Do not use credentials, cookies, tokens, browser session state, paid APIs, or private account data.

## Implementation Requirements

- Read the Review findings first and fix only the shared corporate-actions contract regression they identify.
- Preserve the A-share corporate-actions taxonomy hardening from the initial TASK-098 work unless a narrower schema requirement is necessary to fix the shared contract safely.
- Ensure HK corporate-actions records either emit source-backed `action_family` and `source_route` values or the shared schema no longer globally requires fields HK cannot truthfully supply.
- Do not fabricate event dates, source routes, announcement dates, ex-dates, record dates, or event-family details. Use source-backed values or optional fields.
- Preserve deterministic sorting and duplicate handling already present in the A-share and HK adapters.
- Preserve strict symbol validation behavior for both A-share and HK paths.
- Keep default tests offline-safe and live tests skipped by default unless their explicit environment gate is enabled.
- Update `coordination/reports/TASK-098_REPORT.md` with the cross-suite regression, the chosen fix, tests run, default network behavior, and live-enabled PASS/SKIP/FAIL evidence.

## Tests

Required offline/default tests:

- `python3 -m unittest tests/datahub/test_datasets.py`
- `python3 -m unittest tests/datahub/test_akshare_a_share_corporate_actions_adapter.py`
- `python3 -m unittest -v tests/datahub/test_akshare_a_share_corporate_actions_live.py`
- `python3 -m unittest tests/datahub/test_akshare_hk_corporate_actions_adapter.py`
- `python3 -m unittest -v tests/datahub/test_akshare_hk_corporate_actions_live.py`

If the fix changes source catalog or source capability truth despite this focused handoff, stop and explain the deviation in the report; otherwise do not touch those files.

Live smoke requirements:

- Re-run `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_corporate_actions_live.py` if the A-share real-source path or shared schema behavior affecting A-share validation changed.
- Re-run `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_corporate_actions_live.py` if the HK adapter real-source path or shared schema behavior affecting HK validation changed.
- Report PASS, SKIP, or FAIL truthfully with root-cause evidence.
- If a live-enabled smoke skips because of network, proxy, DNS, TLS, upstream, or public-source availability, diagnose and modify allowed code/tests/report where feasible instead of only documenting the skip.

## Completion Report

Update `coordination/reports/TASK-098_REPORT.md` with:

- files changed
- tests run
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence for A-share and HK corporate-actions smokes as applicable
- the Review regression and how it was fixed
- whether the shared `CORPORATE_ACTIONS` schema remains globally required for `action_family` / `source_route` or was narrowed
- whether A-share TASK-098 taxonomy evidence remains intact
- whether HK corporate-actions records now validate
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

The rework is complete when:

- The Review-identified HK corporate-actions schema regression is fixed or the shared schema is safely narrowed.
- A-share corporate-actions taxonomy hardening remains explicit and test-covered.
- Required A-share and HK corporate-actions default tests pass without hidden live network calls.
- Required gated live evidence is recorded truthfully.
- `coordination/reports/TASK-098_REPORT.md` contains the cross-suite regression result and fix evidence.
- No inactive downstream module behavior is introduced.
