# TASK-097 DataHub A-share Adjustment-Factor Live Classifier Rework

## Role

5.3 Execution Window.

## Context

TASK-097 initial execution added a first-class `DatasetName.ADJUSTMENT_FACTORS` contract and an AKShare/Sina-backed A-share adjustment-factor adapter path. The report records gated live PASS evidence, and Review found no phase-scope or default-network blocker.

Review rejected Controller closure because the new adjustment-factor live skip classifier is too broad:

- `tests/datahub/test_akshare_a_share_adjustment_factors_live.py:57-65` uses `AkshareAShareAdjustmentFactorsAdapter._is_adjustment_factors_network_unavailable()` to convert live exceptions to environment `SKIP`.
- The classifier in `quant/datahub/adapters/akshare.py` treats messages containing `"sina"`, `"finance.sina.com.cn"`, or `"stock_zh_a_daily"` as network-unavailable.
- Review reproduced `True` for `ValueError("sina hfq factor not available")`; that is a real route/data failure and must not be downgraded to environment `SKIP`.

Phase 2.5-P remains active. TASK-097 is not closed, must not enter Integration, and must pass fresh Review before Controller can consider closure.

## Objective

Fix the adjustment-factor live skip classifier so only real environment/source reachability failures are treated as live `SKIP`, while source contract/data/route failures that merely mention Sina, the domain, or the AKShare route name remain hard failures.

This is a focused rework. Do not revisit the broader adjustment-factor contract or adapter design unless the classifier fix exposes a directly related test failure.

## Allowed Writes

Only:

- `quant/datahub/adapters/akshare.py`
- `tests/datahub/test_akshare_a_share_adjustment_factors_adapter.py`
- `tests/datahub/test_akshare_a_share_adjustment_factors_live.py`
- `coordination/reports/TASK-097_REPORT.md`

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files except `coordination/reports/TASK-097_REPORT.md`
- `coordination/reviews/**`
- `coordination/integrations/**`
- `coordination/agent_runs/**`
- `quant/datahub/datasets.py`
- `quant/datahub/source_catalog.py`
- `quant/datahub/source_capabilities.py`
- unrelated adapters or tests
- `quant/features/`
- `quant/scanner/`
- `quant/strategies/`
- `quant/backtest/`
- `quant/portfolio/`
- `quant/notification/`
- `quant/ai/`
- `quant/ui/`

Do not use credentials, cookies, tokens, browser session state, paid APIs, or private account data.

Do not run `git add`, `git commit`, `git reset`, `git checkout`, or other git state-changing commands.

## Implementation Requirements

- Narrow `_is_adjustment_factors_network_unavailable()` so route/source-name-only tokens are not sufficient for a `SKIP` classification.
- Preserve legitimate environment/source availability skips for clear network/proxy/DNS/TLS/timeout/connection/upstream availability failures.
- Add focused offline regression coverage proving these Review examples do not classify as network unavailable:
  - `ValueError("sina hfq factor not available")`
  - a message containing only `finance.sina.com.cn` without network/reachability wording
  - a message containing only `stock_zh_a_daily` without network/reachability wording
- Keep or add coverage proving clear reachability failures still classify as unavailable.
- Keep default tests offline-safe. The live test file must continue to skip by default unless `QUANT_SYSTEM_LIVE_TESTS=1` is set.
- Update `coordination/reports/TASK-097_REPORT.md` truthfully with the rework, tests, default network behavior, and live-enabled PASS/SKIP/FAIL result.

## Tests

Run at minimum:

- `python3 -m unittest tests/datahub/test_akshare_a_share_adjustment_factors_adapter.py`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_adjustment_factors_live.py`

Because TASK-097 includes a real-source adjustment-factor adapter path, also run the gated live smoke where feasible:

- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_adjustment_factors_live.py`

If the gated live smoke skips or fails because of network, proxy, DNS, TLS, timeout, upstream, or public-source availability, diagnose and modify allowed code/tests/report where feasible. Record PASS, SKIP, or FAIL truthfully with root-cause evidence.

## Completion Report

Update `coordination/reports/TASK-097_REPORT.md` with:

- files changed in the rework
- classifier behavior before and after
- regression tests added for Review examples
- tests run
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

The rework is complete when:

- source/route/data failures that mention Sina or `stock_zh_a_daily` no longer classify as environment-unavailable `SKIP`
- clear network/reachability failures still classify as live environment/source availability skips
- focused offline regression tests cover both sides
- default tests remain offline-safe
- the gated live smoke result is reported truthfully
- no inactive downstream module behavior is introduced
