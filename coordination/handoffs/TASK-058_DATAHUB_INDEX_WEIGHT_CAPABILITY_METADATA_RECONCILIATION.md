# TASK-058: DataHub index weight capability metadata reconciliation

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

## Context

TASK-056 added bounded repository-level Tushare Pro adapter coverage and gated smoke-test coverage for `DatasetName.INDEX_WEIGHT_HISTORY`.

TASK-057 completed a live-evidence/prerequisite rework. Review and Integration accepted it as truthful, but the live-enabled result remained `SKIP` because `TUSHARE_TOKEN` is not set. The local `tushare` SDK prerequisite is now available, but credentialed live source coverage is still not proven.

Review and Integration noted a residual metadata risk: `quant/datahub/source_capabilities.py` still describes `index_weight_history` as adapter coverage "not implemented" even though TASK-056 added a bounded adapter slice. This task reconciles that stale wording without changing capability status.

## Objective

Correct stale `index_weight_history` source-capability metadata so it accurately says:

- a bounded Tushare Pro adapter path exists
- live source coverage remains unproven without a credentialed `TUSHARE_TOKEN` live PASS
- the capability must remain `planned` until a credentialed live smoke validates at least one `DatasetName.INDEX_WEIGHT_HISTORY` record

## Allowed Files

You may modify only:

- `quant/datahub/source_capabilities.py`
- `tests/datahub/test_source_capabilities.py`
- `coordination/reports/TASK-058_REPORT.md`

Do not edit Controller-owned files.

## Scope Limits

Do not:

- promote `index_weight_history` from `planned` to `partial`
- change source IDs, dataset mappings, schema contracts, or adapter behavior unless a failing focused test proves the metadata reconciliation cannot be represented otherwise
- add or require credentials
- commit tokens, cookies, private config, or account data
- add public AKShare snapshot fallback for index weights
- implement broad collection, full-history backfill, FeatureHub, scanner, strategy, backtest, signal, risk, notification, AI, UI, automated trading, or derived trading-signal logic

## Required Work

1. Update only the stale source-capability wording for `index_weight_history`.
2. Keep capability status conservative: `planned`.
3. Add or adjust focused source-capability tests if needed so the metadata truth is pinned.
4. Confirm default tests remain offline-safe.
5. Write the execution report.

## Allowed Tests

Run:

- `python3 -m unittest tests/datahub/test_source_capabilities.py`
- `python3 -m unittest -v tests/datahub/test_tushare_index_weight_history_live.py`

You may also run, if useful:

- `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Do not run live-enabled tests for this handoff. This is an offline metadata reconciliation task.

## Required Report

Write `coordination/reports/TASK-058_REPORT.md` with:

- files changed
- tests run
- default network behavior
- live-enabled result: `SKIP / not run by handoff; credentialed live evidence remains pending`
- deviations from this handoff
- risks or follow-up tasks, including that a future credentialed live PASS cycle is still required before `index_weight_history` can move from `planned` to `partial`
