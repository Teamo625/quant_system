# TASK-124 DataHub ETF/Fund Flow Breadth and History Hardening

## Role

5.3 Execution Window.

## Phase

Phase 2.5-P DataHub Personal Trading Perfection Re-Review.

## Context

TASK-123 is closed after accepted Review Agent verification of the bounded-request rework. It fixed the ETF/fund scale/share blocker by preventing bounded ETF-only `FUND_SCALE_SHARE_SNAPSHOT` requests from invoking Sina full-table snapshot routes once exchange-history rows already cover the requested symbols, removed unrelated NAV adapter helper duplication, preserved default offline safety, recorded live-enabled PASS evidence, and kept `fund_scale_and_share` conservative at `partial`.

Phase 2.5-P remains open under `coordination/PHASE_GATE.md` because `build_default_personal_trading_readiness_report()` still reports `overall_status=blocked`, `phase_closure_ready=False`, status counts `pass=3`, `warn=6`, `blocked=1`, `fail=0`, and 42 non-pass follow-up queue items. The next executable ETF/fund queue item after the accepted scale/share hardening is `fund_flow`.

Current `fund_flow` truth is partial. TASK-085 proved caller-provided multi-symbol bounded exchange ETF/fund scale/share slices under `DatasetName.FUND_FLOW`, but broader net-inflow/subscription/redemption facts, non-exchange fund breadth, longer history continuity, and independent public-route redundancy remain incomplete.

This task stays inside DataHub. It must not reopen FeatureHub, Scanner, StrategyLab, BacktestEngine, portfolio, signal, risk, AI, notification, UI, automated trading, paid credentials, or private data.

## Objective

Harden ETF/fund `DatasetName.FUND_FLOW` source truth beyond bounded exchange scale/share date-window slices by proving stronger stable no-credential public flow facts where feasible, or by truthfully constraining capability/source wording without promotion if stronger public routes are not feasible.

Execution should do one of the following:

1. Add or wire stable no-credential public adapter coverage that emits schema-valid `FUND_FLOW` records for richer flow-like facts such as net inflow, subscription, redemption, share change, or source-equivalent flow metrics with explicit source-route and metric truth; or
2. If no stronger public route is feasible, preserve current implementation behavior and tighten capability/source metadata plus focused tests so the system cannot overclaim ETF/fund flow breadth, history, or route redundancy.

Keep `fund_flow` conservative unless implementation, tests, and gated live evidence genuinely satisfy practical public-source personal trading completeness for ETF/fund flow data.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-124_DATAHUB_ETF_FUND_FLOW_BREADTH_HISTORY_HARDENING.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/ROADMAP.md`
- `coordination/reports/TASK-085_REPORT.md`
- `coordination/reviews/TASK-085_REVIEW.md`
- `coordination/reports/TASK-122_REPORT.md`
- `coordination/reviews/TASK-122_REVIEW.md`
- `coordination/reports/TASK-123_REPORT.md`
- `coordination/reviews/TASK-123_REVIEW.md`
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/datasets.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_fund_flow_adapter.py`
- `tests/datahub/test_akshare_fund_flow_live.py`
- `tests/datahub/test_akshare_fund_scale_share_adapter.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`

Read related ETF/fund DataHub tests only as needed to preserve compatibility.

## Allowed Writes

Only:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/datasets.py` only if a minimal schema-compatible clarification is unavoidable
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_fund_flow_adapter.py`
- `tests/datahub/test_akshare_fund_flow_live.py`
- `tests/datahub/test_akshare_fund_scale_share_adapter.py` only if needed to preserve TASK-123 compatibility
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`
- any new focused `tests/datahub/test_akshare_fund_flow*.py` file needed for this handoff
- `coordination/reports/TASK-124_REPORT.md`

If a tightly related ETF/fund test file must change, document the exact reason in the report. Do not touch unrelated DataHub domains.

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files other than `coordination/reports/TASK-124_REPORT.md`
- `coordination/reviews/**`
- `coordination/integrations/**`
- unrelated DataHub adapters or tests
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

- Preserve accepted `DatasetName.FUND_FLOW` validation compatibility and existing bounded exchange ETF/fund flow behavior from TASK-085.
- Preserve accepted `DatasetName.FUND_SCALE_SHARE_SNAPSHOT` behavior from TASK-122/TASK-123; do not reintroduce unbounded full-table snapshot fetches for already satisfied bounded ETF-only scale/share requests.
- Prefer caller-provided, bounded symbol/date requests. Keep `symbols=None` or an empty symbol list as a clear error; do not silently fetch full-market ETF/fund flow tables.
- Investigate stable no-credential public routes within repository-supported source families that truthfully expose ETF/fund flow, net inflow, subscription, redemption, share change, turnover-like flow, or source-equivalent facts.
- Emit flow records only for source-backed facts. Do not invent net inflow, subscription, redemption, market value, premium/discount, NAV, holdings, or feature fields when a verified source does not provide them.
- Preserve route/source truth with `source`, `source_route`, and any available metric/provenance fields. Route-distinct facts must remain distinguishable when values can differ.
- Honor `start_date` and `end_date` deterministically as bounded windows. If a route is latest-only or snapshot-like, use it only when its source date falls inside the requested window and make that behavior explicit in tests and report.
- Reject malformed, ambiguous, unsupported, A-share stock, Hong Kong stock, and index-like symbols clearly unless a route is explicitly proven to support the fund/ETF family.
- If a batch includes one invalid symbol or one repository-side schema/normalization defect, fail clearly rather than returning partial successful output.
- If a valid requested symbol yields no usable rows while another succeeds for the same bounded request, fail clearly unless execution can classify a source-wide route outage.
- Keep live-environment/source classifiers narrow. Network/proxy/DNS/TLS/upstream/source unavailability may skip; repository-side schema, contract, normalization, duplicate-conflict, route-signature, call-compatibility, or unbounded-fetch defects must fail.
- Update `source_catalog` and `source_capabilities` only to reflect proven public-source truth. Keep `fund_flow` conservative unless full practical public-source breadth, history continuity, and redundancy are genuinely proven.
- If no stable broader no-credential route is feasible, record attempted route names and observed limitations in the report, add tests that prevent overclaiming, and leave capability truth conservative.

## Tests

Required offline/default tests:

- `python3 -m unittest tests.datahub.test_source_capabilities`
- `python3 -m unittest tests.datahub.test_source_catalog`
- `python3 -m unittest tests.datahub.test_akshare_fund_flow_adapter`
- focused ETF/fund adapter tests for every changed adapter/test file
- default-skipped live test path for any new or changed live smoke, run with `env -u QUANT_SYSTEM_LIVE_TESTS`

Live smoke requirement:

- If any real-source ETF/fund flow adapter path is added or materially changed, run the relevant gated live smoke with `QUANT_SYSTEM_LIVE_TESTS=1`.
- The live smoke must be explicitly gated and skipped by default.
- The live-enabled smoke should validate at least two supported ETF/fund symbols and at least one schema-valid `FUND_FLOW` record if the upstream source is available.
- Report PASS, SKIP, or FAIL truthfully with root-cause evidence. If the live smoke skips because of network, proxy, DNS, TLS, upstream, or public-source availability, diagnose and modify allowed code/tests/report where feasible instead of only documenting the skip.

## Completion Report

Write `coordination/reports/TASK-124_REPORT.md` with:

- files changed
- implementation summary
- ETF/fund flow route investigation result
- supported symbol classes, date behavior, metric identity, source-route truth, and deduplication behavior
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence, or explicit `SKIP` only if no real-source adapter path was added or materially changed
- whether `fund_flow` capability truth changed
- confirmation that `FUND_SCALE_SHARE_SNAPSHOT` bounded-request behavior and existing ETF/fund dataset compatibility were preserved
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

The task is complete when:

- ETF/fund flow source truth is stronger through added public-route breadth/history coverage, or capability/catalog wording is truthfully constrained without promotion.
- Any emitted source-backed records validate against `DatasetName.FUND_FLOW`.
- Default tests remain offline-safe and live tests remain skipped by default.
- Any real-source work has gated live evidence or a truthful diagnosed SKIP/FAIL requiring Review/Controller follow-up.
- Capability metadata remains conservative and reflects only proven public-source coverage.
- No inactive downstream module behavior is introduced.
