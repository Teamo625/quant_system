# TASK-100 DataHub A-share Valuation Baidu Live Failure Rework

## Role

5.3 Execution Window.

## Context

TASK-100 remains open. The prior overlap-conflict rework removed the first-Eastmoney-date cutover and Review found the offline overlap/gap behavior adequate. However, Review independently reran:

- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`

and observed a live-enabled `FAIL`, not the reported `PASS`. The failure reached the Baidu valuation route in `quant/datahub/adapters/akshare.py` and raised `requests.exceptions.JSONDecodeError` from upstream non-JSON content. The current live classifier did not classify that path as environment/source unavailability, so the repository truth must be reworked and reported accurately.

This is a focused same-task rework. Do not close TASK-100, do not enter Integration, and do not move to a new domain.

## Objective

Diagnose and fix the TASK-100 Baidu live failure path so the gated A-share valuation-history live smoke reports truthful `PASS`, `SKIP`, or `FAIL` behavior.

The smallest acceptable rework is:

- determine whether Baidu non-JSON responses are an upstream/source availability condition that should be deterministically classified as live `SKIP`, or a repository-side handling gap that should remain/fail or be fixed
- adjust the allowed adapter/live-test handling only as needed for truthful behavior
- preserve the accepted overlap-conflict behavior from the prior rework unless the live failure reveals a directly related defect
- update `coordination/reports/TASK-100_REPORT.md` with fresh live truth and root-cause evidence

Keep `a_share_valuation_history` conservative unless fresh source-backed evidence proves materially stronger public-source completeness. This rework alone should not promote it to `covered`.

## Allowed Writes

Only:

- `quant/datahub/adapters/akshare.py`
- `tests/datahub/test_akshare_a_share_valuation_snapshot_adapter.py`
- `tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`
- `coordination/reports/TASK-100_REPORT.md`

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files except `coordination/reports/TASK-100_REPORT.md`
- `coordination/reviews/**`
- `coordination/integrations/**`
- source catalog or capability truth files unless a future Controller handoff explicitly allows it
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

## Required Rework

- Read `AGENTS.md`, this handoff, and `coordination/reviews/TASK-100_REVIEW.md` before editing.
- Reproduce or rerun the gated valuation live smoke when feasible and capture the current Baidu failure mode.
- Inspect the Baidu valuation live failure path around the reported adapter lines and the live-test classifier around the reported live-test lines.
- If upstream non-JSON content is a source/network/proxy/upstream availability condition, make the live smoke classify it deterministically as `SKIP` without hiding repository-side contract/data/schema defects.
- If the non-JSON response indicates a repository-side parser/adapter gap that can be fixed within the allowed files, fix it and keep the live smoke failing on incompatible source truth.
- Add focused offline/default regression coverage for any classifier or adapter handling change so source-route/data/contract failures are not broadly downgraded to environment `SKIP`.
- Preserve the accepted TASK-100 overlap policy:
  - cross-route Baidu/Eastmoney same-date disagreements remain visible as route-distinct facts, or are rejected deterministically if implementation changes make preservation impossible
  - Baidu records are not dropped solely because their trade date is on or after Eastmoney's earliest date
  - Eastmoney gaps after its earliest date do not delete Baidu-backed dates
- Preserve default offline behavior: live tests must remain skipped unless `QUANT_SYSTEM_LIVE_TESTS=1` is explicitly set.
- Keep normalized successful records schema-valid under `DatasetRegistry.validate_record(DatasetName.VALUATION_SNAPSHOT, ...)`.

## Tests

Required offline/default tests:

- `python3 -m unittest tests/datahub/test_datasets.py`
- `python3 -m unittest tests/datahub/test_source_catalog.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`
- `python3 -m unittest tests/datahub/test_akshare_a_share_valuation_snapshot_adapter.py`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`

Live smoke requirement:

- Rerun `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`.
- The live smoke must remain explicitly gated and skipped by default.
- Report PASS, SKIP, or FAIL truthfully with root-cause evidence.
- If the live smoke skips or fails because of network, proxy, DNS, TLS, upstream, public-source availability, or non-JSON upstream content, diagnose and modify allowed code/tests/report where feasible instead of only documenting the skip.

## Completion Report

Update `coordination/reports/TASK-100_REPORT.md` with:

- files changed
- tests run
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence
- whether the Review-observed Baidu non-JSON failure reproduced
- final classifier/adapter policy for Baidu non-JSON or equivalent upstream responses
- evidence that repository-side contract/data/schema failures are not broadly misclassified as environment/source unavailability
- confirmation that the previously accepted Baidu/Eastmoney overlap and gap behavior remains intact
- whether normalized successful records validate against `DatasetName.VALUATION_SNAPSHOT`
- whether `a_share_valuation_history` capability truth changed
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

This rework is complete only when:

- the Review-observed live failure path is diagnosed and handled truthfully
- default tests remain offline-safe and live tests remain skipped by default
- gated live evidence is recorded truthfully as PASS, SKIP, or FAIL with root-cause evidence
- classifier/adapter changes do not mask repository-side source-route, contract, data, or schema failures
- the prior offline overlap/gap regressions still pass
- TASK-100 remains within Phase 2.5-P DataHub scope and does not modify inactive downstream modules
