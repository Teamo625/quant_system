# TASK-059 Retry Rework: DataHub Tushare index weight credentialed live PASS

## Role

5.3 Execution Window.

## Required Reading

Read these files first:

- `AGENTS.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-059_DATAHUB_TUSHARE_INDEX_WEIGHT_CREDENTIALED_LIVE_PASS.md`
- `coordination/handoffs/TASK-059_DATAHUB_TUSHARE_INDEX_WEIGHT_CREDENTIALED_LIVE_REWORK.md`
- `coordination/reports/TASK-059_REPORT.md`
- `coordination/reviews/TASK-059_REVIEW.md`
- this handoff

Do not read `coordination/agent_runs/**`.

When searching the repository, exclude:

- `coordination/agent_runs/**`
- `.pytest_cache/**`
- `**/__pycache__/**`

## Review Finding to Address

The Review Agent requires another rework because TASK-059 still lacks credentialed live PASS evidence:

- the previous rework stopped truthfully at the `TUSHARE_TOKEN` precondition gate
- no credentialed live smoke ran
- no schema-valid `DatasetName.INDEX_WEIGHT_HISTORY` record was validated through the Tushare adapter path
- `index_weight_history` must remain `planned` until that evidence exists

This handoff is only to resolve that Review finding. Do not broaden the task.

## Precondition

Run this retry only after the operator supplies a valid `TUSHARE_TOKEN` in the execution environment.

Do not print, store, commit, or otherwise expose the token. Confirm only whether it is set.

If `TUSHARE_TOKEN` is still unset:

- stop immediately after confirming the missing precondition
- update `coordination/reports/TASK-059_REPORT.md` truthfully as `BLOCKED / SKIP: TUSHARE_TOKEN unset`
- do not modify implementation or test files
- state clearly that TASK-059 is still not closure-ready and needs another execution after the credential is supplied

## Objective

Produce closure-ready credentialed live evidence for Tushare Pro `INDEX_WEIGHT_HISTORY`, or diagnose and fix feasible repository-side blockers within the allowed files.

If the credentialed live smoke passes:

- confirm at least one schema-valid `DatasetName.INDEX_WEIGHT_HISTORY` record was fetched through the existing Tushare adapter path
- promote `index_weight_history` source capability from `planned` to conservative `partial`
- update focused source-capability tests to pin the promoted status and bounded live-evidence wording
- preserve breadth/history limitations explicitly

If the credentialed live smoke skips or fails:

- diagnose the root cause
- fix feasible repository-side code/test issues within the allowed files
- record PASS, SKIP, or FAIL truthfully with evidence
- leave `index_weight_history` as `planned` unless a credentialed live PASS validates at least one schema-valid record

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
5. If the credentialed live smoke skips or fails, diagnose whether the cause is repository code, schema, classifier behavior, request parameters, route signature, network/proxy/DNS/TLS, upstream/source availability, token permissions, quota, or operator environment.
6. Fix feasible repository-side causes within the allowed files.
7. Write the execution report.

## Allowed Tests

Run:

- `python3 -m unittest -v tests/datahub/test_tushare_index_weight_history_live.py`
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_tushare_index_weight_history_live.py`
- `python3 -m unittest tests/datahub/test_tushare_index_weight_history_adapter.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`

You may also run, if useful:

- `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

## Required Report

Update `coordination/reports/TASK-059_REPORT.md` with:

- files changed
- tests run
- default network behavior
- credential precondition status without revealing the token
- live-enabled PASS/SKIP/FAIL result and root-cause evidence
- whether `index_weight_history` remains `planned` or was promoted to `partial`
- how the TASK-059 Review finding was addressed
- deviations from this handoff
- risks or follow-up tasks

## Closure Gate

TASK-059 must not be closed by Controller until a fresh Review Agent review accepts this retry rework. Do not enter Integration during execution.
