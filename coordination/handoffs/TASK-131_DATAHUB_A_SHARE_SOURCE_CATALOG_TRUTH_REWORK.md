# TASK-131 DataHub A-share Source Catalog Truth Rework

## Role

5.3 Execution Window.

## Phase

Phase 2.5-P DataHub Personal Trading Perfection Re-Review.

## Context

`TASK-131` execution completed the A-share lifecycle and continuity capability-cluster handoff and wrote `coordination/reports/TASK-131_REPORT.md`.

Review rejected Controller closure for one focused source-truth issue:

- `coordination/reviews/TASK-131_REVIEW.md` says `quant/datahub/source_catalog.py` records "BaoStock 5/15/30/60-minute history" inside the `akshare_cn_hk_public_family` notes. BaoStock has its own `baostock_public_cn` catalog entry, so this wording attributes cross-source coverage to the wrong source family and violates the handoff requirement that `source_catalog` reflect proven source truth.

Review also recorded:

- Controller closure allowed: no
- Default tests offline-safe: yes
- Live-enabled result: PASS for the materially changed real-source paths
- Rework required: yes
- No live-network rework is required

This rework must stay minimal. Do not merge this with readiness `follow_up_batches`, broader A-share hardening, or any ordinary future hardening item.

## Objective

Correct the TASK-131 source-catalog truth statement so AKShare-family catalog notes no longer claim BaoStock minute-bar coverage.

The resulting catalog wording must keep:

- AKShare/Eastmoney minute-bar truth under the AKShare public family only.
- BaoStock `5/15/30/60` minute-bar history truth under the BaoStock public family only.
- All A-share capability statuses conservative and unpromoted unless already proven by accepted implementation and Review.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-131_DATAHUB_A_SHARE_SOURCE_CATALOG_TRUTH_REWORK.md`
- `coordination/reports/TASK-131_REPORT.md`
- `coordination/reviews/TASK-131_REVIEW.md`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_source_catalog.py`

Read `coordination/handoffs/TASK-131_DATAHUB_A_SHARE_LIFECYCLE_CONTINUITY_CLUSTER_HARDENING.md` only if needed to confirm original scope. Do not read `coordination/agent_runs/**`.

## Allowed Writes

Only:

- `quant/datahub/source_catalog.py`
- `tests/datahub/test_source_catalog.py`
- `coordination/reports/TASK-131_REPORT.md`

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files other than `coordination/reports/TASK-131_REPORT.md`
- `coordination/reviews/**`
- `coordination/integrations/**`
- `quant/datahub/adapters/**`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/datasets.py`
- unrelated tests
- `quant/features/**`
- `quant/scanner/**`
- `quant/strategies/**`
- `quant/backtest/**`
- `quant/portfolio/**`
- `quant/notification/**`
- `quant/ai/**`
- `quant/ui/**`

Do not use credentials, tokens, cookies, browser session state, private account data, paid sources, or hidden default live network behavior.

Do not implement FeatureHub indicators, scanner ranking, strategy/backtest logic, portfolio/signal/risk, AI reports, notification, UI, or automated trading.

## Implementation Requirements

- Remove or rewrite the misleading `akshare_cn_hk_public_family` note so it does not attribute BaoStock minute-bar history to AKShare.
- Preserve source-family separation: AKShare/Eastmoney facts belong to the AKShare catalog entry, and BaoStock facts belong to `baostock_public_cn`.
- If `tests/datahub/test_source_catalog.py` lacks a focused regression for this source-family separation, add one.
- Do not change adapter behavior.
- Do not promote any capability status.
- Do not broaden the task into route investigation, live testing, or readiness queue processing.

## Tests

Required default/offline tests:

- `python3 -m unittest tests.datahub.test_source_catalog`

Run only additional focused offline tests if directly needed for changed files.

Live tests are not required for this rework because Review accepted live-enabled PASS evidence and the blocker is catalog wording accuracy only.

## Completion Report

Update `coordination/reports/TASK-131_REPORT.md` with a rework section that includes:

- files changed in the rework
- exact source-catalog truth correction made
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled result: not rerun / not required for this source-catalog-only rework, with reference to Review's accepted live PASS
- deviations, if any
- risks or follow-up tasks, if any

## Completion Criteria

The rework is complete when:

- `akshare_cn_hk_public_family` no longer claims BaoStock minute-bar coverage.
- BaoStock minute-bar history remains represented only under the BaoStock source family.
- Focused default/offline test coverage passes.
- `coordination/reports/TASK-131_REPORT.md` truthfully records the rework and test result.
- No inactive downstream module, paid/private source, hidden live network path, or broader readiness batch work is introduced.
