# TASK-132 DataHub A-share Northbound Fallback Truth Rework

## Role

5.3 Execution Window.

## Phase

Phase 2.5-P DataHub Personal Trading Perfection Re-Review.

## Context

The Review Agent rejected the current TASK-132 result because `a_share_northbound_flow` source truth is overstated in capability/catalog metadata.

Review finding:

- `coordination/reviews/TASK-132_REVIEW.md` says `quant/datahub/source_capabilities.py` and `quant/datahub/source_catalog.py` describe `stock_hsgt_individual_detail_em` as established fallback coverage.
- `coordination/reports/TASK-132_REPORT.md` says the same fallback route was attempted but the live-enabled northbound smoke skipped because the route is currently upstream-broken with `TypeError: 'NoneType' object is not subscriptable`.
- Therefore capability/catalog truth is stronger than live evidence. Controller closure is not allowed until this is corrected and freshly reviewed.

This is a focused Review rework only. Do not merge it with readiness `follow_up_batches` or other hardening items.

## Objective

Correct TASK-132 northbound fallback truth so metadata, tests, and report all say the same thing:

- primary route: `stock_hsgt_individual_em` remains the only proven no-credential symbol-level northbound route from current TASK-132 evidence;
- fallback route: `stock_hsgt_individual_detail_em` may remain represented only as an attempted / implemented / currently unproven bounded fallback path, not as established coverage;
- live evidence: current TASK-132 live-enabled northbound result remains `SKIP` because the fallback route is upstream-broken and the primary route appears stale for the recent bounded window;
- capability status must remain conservative and must not imply northbound completeness or proven redundancy.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-132_DATAHUB_A_SHARE_NORTHBOUND_FALLBACK_TRUTH_REWORK.md`
- `coordination/handoffs/TASK-132_DATAHUB_A_SHARE_FLOW_LIQUIDITY_FINANCIAL_CLUSTER_HARDENING.md`
- `coordination/reports/TASK-132_REPORT.md`
- `coordination/reviews/TASK-132_REVIEW.md`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`
- `tests/datahub/test_akshare_a_share_northbound_flow_adapter.py`
- `tests/datahub/test_akshare_a_share_northbound_flow_live.py`

Read `quant/datahub/adapters/akshare.py` only if needed to understand current route behavior or preserve existing tests. Do not do a broad implementation review.

## Allowed Writes

Only:

- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`
- `tests/datahub/test_akshare_a_share_northbound_flow_adapter.py` only if an existing assertion now conflicts with corrected truth wording
- `tests/datahub/test_akshare_a_share_northbound_flow_live.py` only if an existing assertion now conflicts with corrected truth wording
- `coordination/reports/TASK-132_REPORT.md`

Do not change adapter behavior unless a test assertion cannot be corrected without exposing a genuine repository-side defect. If such a defect is found, stop the broadening and document the minimal reason in the report.

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files other than `coordination/reports/TASK-132_REPORT.md`
- `coordination/reviews/**`
- `coordination/integrations/**`
- unrelated DataHub domains
- `quant/features/**`
- `quant/scanner/**`
- `quant/strategies/**`
- `quant/backtest/**`
- `quant/portfolio/**`
- `quant/notification/**`
- `quant/ai/**`
- `quant/ui/**`

Do not add paid sources, private credentials, browser/session state, hidden default live network behavior, downstream feature/scanner/strategy/backtest/signal/risk/portfolio/AI/notification/UI logic, or automated trading logic.

## Implementation Requirements

- Rewrite `a_share_northbound_flow` capability/source-catalog wording so `stock_hsgt_individual_detail_em` is explicitly an attempted bounded fallback whose live availability is currently unproven / upstream-broken in TASK-132 evidence.
- Keep `stock_hsgt_individual_em` as the proven primary route only where current evidence supports it.
- Preserve the TASK-132 conservative capability status; do not promote `a_share_northbound_flow`.
- Add or adjust focused tests so future wording cannot again imply proven fallback coverage or redundancy without live evidence.
- Preserve all accepted TASK-132 adapter behavior for limit-up/down and financial statements.
- Preserve default offline safety. Default tests and default live modules must not perform real network calls.
- Do not run a new live smoke unless execution materially changes real-source behavior. For wording/test-only rework, report the prior TASK-132 live-enabled northbound result as `SKIP` with the same root-cause evidence.

## Tests

Required offline/default tests:

- `python3 -m unittest tests.datahub.test_source_capabilities`
- `python3 -m unittest tests.datahub.test_source_catalog`
- `python3 -m unittest tests.datahub.test_akshare_a_share_northbound_flow_adapter`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_a_share_northbound_flow_live`

If any real-source behavior is changed, also run:

- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_a_share_northbound_flow_live`

## Completion Report

Update `coordination/reports/TASK-132_REPORT.md` with a clearly labeled rework section containing:

- files changed
- implementation summary
- exact northbound fallback wording correction
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled result for this rework, including whether the prior `SKIP` was preserved or a new live smoke was run
- deviations from this handoff
- remaining risks or follow-up tasks
