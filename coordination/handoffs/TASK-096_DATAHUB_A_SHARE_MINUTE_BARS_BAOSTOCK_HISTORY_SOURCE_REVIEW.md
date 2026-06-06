# TASK-096 DataHub A-share Minute Bars BaoStock History Source Review

## Role

Review Agent.

## Context

TASK-096 remains active in Phase 2.5-P.

The prior Eastmoney-only live PASS rerun path remained blocked because `push2his.eastmoney.com` returned remote disconnect / empty reply in the local environment. The owner explicitly authorized a scope update from an Eastmoney-only rerun to a no-credential public-source replacement path using BaoStock as the primary historical minute-bars source.

Execution has already been completed manually and committed:

- commit: `e3138fe TASK-096 add baostock minute bar history source`
- report: `coordination/reports/TASK-096_REPORT.md`

## Review Objective

Review the BaoStock-backed TASK-096 implementation and decide whether Controller closure is allowed.

Focus on:

- Phase 2.5-P/DataHub scope compliance.
- Whether adding `baostock_public_cn` is consistent with the owner-approved route update.
- Whether default tests remain offline-safe.
- Whether the gated BaoStock live smoke provides truthful live-enabled PASS evidence for A-share `DatasetName.MINUTE_BARS`.
- Whether the adapter preserves source truth and does not over-promote `a_share_minute_bars` beyond `partial`.
- Whether the report truthfully records the deviation from the previous Eastmoney-only rerun handoff and the remaining Eastmoney limitation.

## Files To Review

Read:

- `AGENTS.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/reports/TASK-096_REPORT.md`
- this handoff
- the committed code changes in `e3138fe`

Primary changed files:

- `quant/datahub/adapters/baostock.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `quant/datahub/source_catalog.py`
- `quant/datahub/source_capabilities.py`
- `tests/datahub/test_baostock_a_share_minute_bars_adapter.py`
- `tests/datahub/test_baostock_a_share_minute_bars_live.py`
- `tests/datahub/test_source_catalog.py`
- `tests/datahub/test_source_capabilities.py`
- `coordination/reports/TASK-096_REPORT.md`

## Expected Review Output

Write the review decision to:

- `coordination/reviews/TASK-096_REVIEW.md`

The review file must state:

- Controller closure allowed: Yes/No
- Default tests offline-safe: Yes/No
- Live-enabled result: PASS/SKIP/FAIL, naming BaoStock as the reviewed live source
- Rework required: Yes/No
- Whether phase/scope/contract/test blockers remain

## Closure Standard

TASK-096 may be closure-ready only if Review accepts the owner-approved BaoStock public-source route update, the implementation remains inside DataHub scope, default tests remain offline-safe, and the report's BaoStock live-enabled PASS evidence is sufficient for the current no-credential public-source minute-bars hardening objective.
