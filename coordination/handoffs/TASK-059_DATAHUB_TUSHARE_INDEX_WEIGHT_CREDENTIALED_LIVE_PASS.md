# TASK-059: DataHub Tushare index weight credentialed live PASS

## Role

5.3 Execution Window.

## Required Reading

Read these files first:

- `AGENTS.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- this handoff

Do not read `coordination/agent_runs/**`.

When searching the repository, exclude:

- `coordination/agent_runs/**`
- `.pytest_cache/**`
- `**/__pycache__/**`

## Precondition

This task is blocked until the execution environment has a valid `TUSHARE_TOKEN`.

Do not add, print, commit, or store credentials. The token must be supplied only through the operator's environment.

If `TUSHARE_TOKEN` is unset, stop after confirming the missing precondition and write the report truthfully as `BLOCKED / SKIP: TUSHARE_TOKEN unset`. Do not modify implementation files in that case.

## Context

TASK-055 added the dedicated `DatasetName.INDEX_WEIGHT_HISTORY` contract.

TASK-056 added bounded repository-level Tushare Pro adapter and gated smoke coverage for `INDEX_WEIGHT_HISTORY`, but live execution skipped because local prerequisites were absent.

TASK-057 confirmed the local `tushare` SDK prerequisite is now available, but live execution still skipped because `TUSHARE_TOKEN` is unset.

TASK-058 reconciled stale capability wording while keeping `index_weight_history` conservatively `planned`.

Phase 2.5 cannot close until a credentialed live smoke validates at least one schema-valid `INDEX_WEIGHT_HISTORY` record, or until a fresh execution/review cycle proves a repository-side blocker and fixes it where feasible.

## Objective

Run the credentialed Tushare Pro `INDEX_WEIGHT_HISTORY` live smoke and close the remaining source-coverage evidence gap.

If live smoke passes:

- update `index_weight_history` source capability from `planned` to conservative `partial`
- update focused source-capability tests to pin the promoted status and live-evidence wording
- keep breadth/history limitations explicit

If live smoke fails or skips because of repository code, schema, classifier, request-parameter, route-signature, network/proxy/DNS/TLS, upstream, or source availability behavior:

- diagnose the root cause
- modify allowed code/tests where feasible
- record PASS, SKIP, or FAIL truthfully with evidence
- leave `index_weight_history` as `planned` unless a credentialed live PASS validates at least one record

## Allowed Files

You may modify only:

- `quant/datahub/adapters/tushare.py`
- `quant/datahub/source_capabilities.py`
- `tests/datahub/test_tushare_index_weight_history_adapter.py`
- `tests/datahub/test_tushare_index_weight_history_live.py`
- `tests/datahub/test_source_capabilities.py`
- `coordination/reports/TASK-059_REPORT.md`

Do not edit Controller-owned files.

## Scope Limits

Do not:

- implement public AKShare snapshot fallback for index weights
- broaden into full-market or full-history collection
- add credential storage, config files, tokens, cookies, or account data
- change unrelated DataHub contracts, source IDs, or dataset mappings
- implement FeatureHub, scanner, strategy, backtest, signal, risk, portfolio, notification, AI, UI, automated trading, or derived trading-signal logic

Promote `index_weight_history` only after a credentialed live PASS validates at least one `DatasetName.INDEX_WEIGHT_HISTORY` record through the existing Tushare adapter path.

## Required Work

1. Confirm `TUSHARE_TOKEN` is set without printing its value.
2. Run the default offline Tushare index-weight live test and confirm it remains offline-safe by default.
3. Run the credentialed live smoke.
4. If the credentialed live smoke passes, promote `index_weight_history` to `partial` and update focused source-capability assertions.
5. If the credentialed live smoke skips or fails, diagnose and fix feasible repository-side causes within the allowed files; otherwise document the external/operator blocker truthfully.
6. Write the execution report.

## Allowed Tests

Run:

- `python3 -m unittest -v tests/datahub/test_tushare_index_weight_history_live.py`
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_tushare_index_weight_history_live.py`
- `python3 -m unittest tests/datahub/test_tushare_index_weight_history_adapter.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`

You may also run, if useful:

- `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

## Required Report

Write `coordination/reports/TASK-059_REPORT.md` with:

- files changed
- tests run
- default network behavior
- credential precondition status without revealing the token
- live-enabled PASS/SKIP/FAIL result and root-cause evidence
- whether `index_weight_history` remains `planned` or was promoted to `partial`
- deviations from this handoff
- risks or follow-up tasks
