# TASK-123 DataHub ETF/Fund Scale/Share Bounded Request Rework

## Role

5.3 Execution Window.

## Phase

Phase 2.5-P DataHub Personal Trading Perfection Re-Review.

## Context

The initial TASK-123 execution report and Review exist:

- `coordination/reports/TASK-123_REPORT.md`
- `coordination/reviews/TASK-123_REVIEW.md`

Review rejected the current result. TASK-123 remains Active and must not be closed, marked Done, or moved to Integration until a fresh Review accepts the rework.

Blocking Review finding:

- `AkshareETFFundFlowAdapter` now unconditionally fetches Sina full-table latest snapshot routes for every `DatasetName.FUND_SCALE_SHARE_SNAPSHOT` request, including bounded ETF-only batches that already have exchange-history routes. This violates the original handoff requirement to prefer caller-provided bounded requests and not silently fetch unbounded full-market ETF/fund data.

Non-blocking Review finding:

- Duplicate scale/share dedupe helpers were added under the unrelated `AkshareETFFundNavSnapshotAdapter`. They are outside the focused adapter surface for TASK-123 and should be removed unless strictly required by the rework.

This is a focused rework only. Do not redo the broader source-breadth task from scratch unless needed to resolve these findings.

## Objective

Resolve the TASK-123 Review findings with the smallest DataHub-only change:

1. Ensure bounded ETF/fund scale/share requests do not silently fetch unbounded full-market Sina snapshot tables by default.
2. Either restrict Sina snapshot route use to an explicitly justified request-scoped fallback that does not violate bounded-request behavior, or remove/revert snapshot expansion and truthfully constrain capability/source wording without promotion.
3. Remove the unrelated duplicate scale/share helper insertion from the NAV adapter unless execution can prove it is directly required for the accepted TASK-123 behavior.

Keep `fund_scale_and_share` conservative and unpromoted unless the reworked implementation, tests, and gated live evidence genuinely prove stronger public-source completeness.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-123_DATAHUB_ETF_FUND_SCALE_SHARE_SOURCE_BREADTH_HARDENING.md`
- `coordination/handoffs/TASK-123_DATAHUB_ETF_FUND_SCALE_SHARE_BOUNDED_REQUEST_REWORK.md`
- `coordination/reports/TASK-123_REPORT.md`
- `coordination/reviews/TASK-123_REVIEW.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/ROADMAP.md`
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_fund_scale_share_adapter.py`
- `tests/datahub/test_akshare_fund_scale_share_live.py`
- `tests/datahub/test_akshare_fund_flow_adapter.py`
- `tests/datahub/test_akshare_fund_flow_live.py`
- `tests/datahub/test_akshare_fund_nav_adapter.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`

Read related ETF/fund DataHub tests only as needed to keep compatibility.

## Allowed Writes

Only:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_fund_scale_share_adapter.py`
- `tests/datahub/test_akshare_fund_scale_share_live.py`
- `tests/datahub/test_akshare_fund_flow_adapter.py`
- `tests/datahub/test_akshare_fund_flow_live.py`
- `tests/datahub/test_akshare_fund_nav_adapter.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`
- `coordination/reports/TASK-123_REPORT.md`

If a tightly related ETF/fund test file must change, document the exact reason in the report. Do not touch unrelated DataHub domains.

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files other than `coordination/reports/TASK-123_REPORT.md`
- `coordination/reviews/**`
- `coordination/integrations/**`
- `quant/datahub/datasets.py`, unless a Review finding cannot be resolved without a minimal schema-compatible clarification; if used, document why in the report
- unrelated adapters or tests
- `quant/features/**`
- `quant/scanner/**`
- `quant/strategies/**`
- `quant/backtest/**`
- `quant/portfolio/**`
- `quant/notification/**`
- `quant/ai/**`
- `quant/ui/**`

Do not use credentials, tokens, cookies, browser session state, private account data, paid sources, or hidden default live network behavior.

## Implementation Requirements

- Preserve TASK-122 `DatasetName.FUND_SCALE_SHARE_SNAPSHOT` validation compatibility, including signed change metrics and nonnegative level metrics.
- Preserve accepted `FUND_FLOW`, `FUND_NAV_SNAPSHOT`, and existing ETF/fund behavior except where the Review findings require a focused fix.
- Do not unconditionally fetch full-table Sina snapshot routes for every bounded scale/share request.
- If keeping any Sina snapshot coverage, make the invocation semantics explicit and bounded in repository behavior. It must be clear from code and tests when those routes are eligible, why they do not silently expand an already satisfiable bounded request, and how invalid non-target rows cannot affect requested-symbol results.
- If no compliant request-scoped snapshot behavior is feasible, remove the adapter-backed snapshot expansion and update capability/catalog wording and tests so no adapter-backed snapshot breadth is overclaimed.
- Keep deterministic sorting and deduplication for any retained scale/share records.
- Keep malformed, ambiguous, unsupported, A-share stock, Hong Kong stock, and index-like symbols rejected clearly.
- Keep live-environment/source classifiers narrow: network/proxy/DNS/TLS/upstream/source unavailability may skip; repository-side schema, contract, normalization, duplicate-conflict, route-signature, or unbounded-fetch behavior defects must fail.
- Remove the duplicate helper code added to `AkshareETFFundNavSnapshotAdapter` unless it is directly required by the reworked accepted path and covered by focused tests.
- Update `source_catalog` and `source_capabilities` only to reflect the reworked proven truth. Do not promote `fund_scale_and_share` from `partial`.

## Tests

Required offline/default tests:

- `python3 -m unittest tests.datahub.test_datasets`
- `python3 -m unittest tests.datahub.test_source_capabilities`
- `python3 -m unittest tests.datahub.test_source_catalog`
- `python3 -m unittest tests.datahub.test_akshare_fund_flow_adapter tests.datahub.test_akshare_fund_nav_adapter tests.datahub.test_akshare_fund_scale_share_adapter`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_fund_flow_live tests.datahub.test_akshare_fund_scale_share_live`

Focused regression coverage must prove the Review blocker is fixed. At minimum, tests should show that a bounded ETF-only scale/share request that can be satisfied by exchange history does not call unbounded Sina snapshot routes.

Live smoke requirement:

- If the rework keeps or materially changes a real-source scale/share adapter path, run the relevant gated live smoke with `QUANT_SYSTEM_LIVE_TESTS=1`.
- If the rework removes snapshot expansion and leaves only already accepted bounded exchange-history behavior, run the existing relevant gated live smoke or document why live evidence is unchanged.
- Report PASS, SKIP, or FAIL truthfully with root-cause evidence.

## Completion Report

Update `coordination/reports/TASK-123_REPORT.md` with:

- files changed
- Review findings addressed
- implementation summary
- final Sina snapshot route disposition: removed, disabled by default, or request-scoped with justification
- confirmation that bounded ETF-only requests no longer silently fetch unbounded full-market data
- whether duplicate NAV adapter helpers were removed or why they remain
- supported symbol classes, date behavior, metric identity, and deduplication behavior after rework
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence
- whether `fund_scale_and_share` capability truth changed
- compatibility confirmation for `FUND_FLOW`, `FUND_NAV_SNAPSHOT`, and `FUND_SCALE_SHARE_SNAPSHOT`
- deviations from this rework handoff
- risks or follow-up tasks

## Completion Criteria

The rework is complete only when:

- The blocking unbounded full-table fetch behavior is fixed or removed.
- Focused offline tests prevent regression of that behavior.
- Unrelated duplicate NAV adapter helper insertion is removed or explicitly justified as required by the accepted path.
- Default tests remain offline-safe and live tests remain skipped by default.
- Any real-source path retained or changed has gated live evidence or a truthful diagnosed result.
- `fund_scale_and_share` remains conservative unless stronger public-source completeness is genuinely proven.
- No inactive downstream module behavior is introduced.
