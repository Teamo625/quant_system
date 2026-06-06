# TASK-125 DataHub ETF/Fund Premium-Discount Breadth and History Hardening

## Role

5.3 Execution Window.

## Phase

Phase 2.5-P DataHub Personal Trading Perfection Re-Review.

## Context

TASK-124 is closed after accepted Review Agent verification. It added optional `source_route` truth to `DatasetName.FUND_FLOW`, preserved route-distinct ETF/fund flow records during deduplication, investigated broader no-credential public flow routes, tightened capability/catalog wording instead of over-promoting, kept default tests offline-safe, recorded live-enabled PASS evidence, and kept `fund_flow` conservative at `partial`.

Phase 2.5-P remains open under `coordination/PHASE_GATE.md` because unresolved DataHub personal trading perfection queue items remain. `index_weight_history` remains an owner paid-credential blocker; optional `hk_minute_bars` remains owner-waiver-required; and ETF/fund premium-discount, index, sector/concept, macro/policy, and quality-report gaps still require accepted DataHub hardening or owner-accepted disposition before FeatureHub can reopen.

The next executable TASK-093 queue item is:

- follow-up id: `etf_fund__etf_fund_capability_readiness__fund_premium_discount`
- capability: `fund_premium_discount`
- disposition: `datahub_hardening`
- theme: expand ETF/fund premium-discount breadth beyond bounded latest-available exchange snapshots into longer history continuity and broader public fund coverage
- reason: TASK-086 added the dedicated `FUND_PREMIUM_DISCOUNT` contract and TASK-087 proved bounded public ETF/fund premium-discount source facts, but current proof remains latest-available snapshot oriented and broader fund breadth, longer history continuity, and independent public-route redundancy remain incomplete.

This task stays inside DataHub. It must not reopen FeatureHub, Scanner, StrategyLab, BacktestEngine, portfolio, signal, risk, AI, notification, UI, automated trading, paid credentials, or private data.

## Objective

Harden ETF/fund `DatasetName.FUND_PREMIUM_DISCOUNT` source truth beyond the accepted bounded latest-available exchange ETF/fund premium-discount slice where stable no-credential public routes expose broader breadth, date history, route/source truth, or redundancy.

Execution should do one of the following:

1. Expand AKShare-backed ETF/fund premium-discount support to additional stable no-credential public routes, fund classes, dated history continuity, or route/source truth while preserving existing accepted behavior; or
2. If no stronger public route is feasible, truthfully constrain `fund_premium_discount` source-capability/catalog wording and add tests/report evidence that prevent overclaiming.

Keep `fund_premium_discount` conservative unless implementation, tests, and gated live evidence genuinely satisfy practical public-source personal trading completeness for ETF/fund premium-discount data.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-125_DATAHUB_ETF_FUND_PREMIUM_DISCOUNT_BREADTH_HISTORY_HARDENING.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/ROADMAP.md`
- `coordination/reports/TASK-086_REPORT.md`
- `coordination/reviews/TASK-086_REVIEW.md`
- `coordination/reports/TASK-087_REPORT.md`
- `coordination/reviews/TASK-087_REVIEW.md`
- `coordination/reports/TASK-124_REPORT.md`
- `coordination/reviews/TASK-124_REVIEW.md`
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/datasets.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_fund_premium_discount_adapter.py`
- `tests/datahub/test_akshare_fund_premium_discount_live.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`
- related ETF/fund DataHub tests only as needed to preserve compatibility

## Allowed Writes

Only:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/datasets.py` only if a minimal schema-compatible clarification is unavoidable
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_fund_premium_discount_adapter.py`
- `tests/datahub/test_akshare_fund_premium_discount_live.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`
- any new focused `tests/datahub/test_akshare_fund_premium_discount*.py` file needed for this handoff
- `coordination/reports/TASK-125_REPORT.md`

If a tightly related ETF/fund test file must change, document the exact reason in the report. Do not touch unrelated DataHub domains.

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files other than `coordination/reports/TASK-125_REPORT.md`
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

- Preserve existing `AkshareETFFundPremiumDiscountAdapter` behavior for accepted bounded multi-symbol premium-discount requests.
- Preserve `DatasetName.FUND_PREMIUM_DISCOUNT` validation compatibility; do not add NAV, OHLCV, holdings, flow, scale/share, or feature fields to premium-discount records unless a source-backed schema-compatible clarification is unavoidable and justified.
- Prefer caller-provided, bounded symbol/date requests. Keep `symbols=None` or empty symbol requests as clear errors; do not silently fetch unbounded full-market ETF/fund premium-discount tables.
- Investigate stable no-credential public routes within repository-supported source families that truthfully expose ETF/fund premium-discount rate, amount, market price versus NAV/IOPV, dated history, broader fund-family coverage, or independent route redundancy.
- Emit premium-discount records only for source-backed facts. Do not invent NAV, IOPV, market price, premium/discount amount, flow, scale/share, or date values when a verified source does not provide them.
- Preserve route/source truth with `source`, `source_route`, route-local reference valuation fields, and any available metric/provenance fields. Route-distinct facts must remain distinguishable when values can differ.
- Honor `start_date` and `end_date` deterministically as bounded windows. If a route is latest-only or snapshot-like, use it only when its source date falls inside the requested window and make that behavior explicit in tests and report.
- Reject malformed, ambiguous, unsupported, A-share stock, Hong Kong stock, and index-like symbols clearly unless a route is explicitly proven to support the fund/ETF family.
- If a batch includes one invalid symbol or one repository-side schema/normalization defect, fail clearly rather than returning partial successful output.
- If a valid requested symbol yields no usable rows while another succeeds for the same bounded request, fail clearly unless execution can classify a source-wide route outage.
- Keep live-environment/source classifiers narrow. Network/proxy/DNS/TLS/upstream/source unavailability may skip; repository-side schema, contract, normalization, duplicate-conflict, route-signature, call-compatibility, unbounded-fetch, or date-window defects must fail.
- Update `source_catalog` and `source_capabilities` only to reflect proven public-source truth. Keep `fund_premium_discount` conservative unless full practical public-source breadth, history continuity, and redundancy are genuinely proven.
- If no stable broader no-credential route is feasible, record attempted route names and observed limitations in the report, add tests that prevent overclaiming, and leave capability truth conservative.

## Tests

Required offline/default tests:

- `python3 -m unittest tests.datahub.test_source_capabilities`
- `python3 -m unittest tests.datahub.test_source_catalog`
- `python3 -m unittest tests.datahub.test_akshare_fund_premium_discount_adapter`
- focused ETF/fund adapter tests for every changed adapter/test file
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_fund_premium_discount_live`

Live smoke requirement:

- If any real-source ETF/fund premium-discount adapter path is added or materially changed, run the relevant gated live smoke with `QUANT_SYSTEM_LIVE_TESTS=1`.
- The live smoke must be explicitly gated and skipped by default.
- The live-enabled smoke should validate at least two supported ETF/fund symbols and at least one schema-valid `FUND_PREMIUM_DISCOUNT` record if the upstream source is available.
- Report PASS, SKIP, or FAIL truthfully with root-cause evidence. If the live smoke skips because of network, proxy, DNS, TLS, upstream, or public-source availability, diagnose and modify allowed code/tests/report where feasible instead of only documenting the skip.

## Completion Report

Write `coordination/reports/TASK-125_REPORT.md` with:

- files changed
- implementation summary
- ETF/fund premium-discount route/source-family investigation result
- supported symbol classes, date behavior, metric identity, source-route truth, and deduplication behavior
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence, or explicit `SKIP` only if no real-source adapter path was added or materially changed
- whether `fund_premium_discount` capability truth changed
- confirmation that existing ETF/fund premium-discount dataset compatibility was preserved
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

The task is complete when:

- ETF/fund premium-discount source truth is stronger through added public-route breadth/history coverage, or capability/catalog wording is truthfully constrained without promotion.
- Any emitted source-backed records validate against `DatasetName.FUND_PREMIUM_DISCOUNT`.
- Default tests remain offline-safe and live tests remain skipped by default.
- Any real-source work has gated live evidence or a truthful diagnosed SKIP/FAIL requiring Review/Controller follow-up.
- Capability metadata remains conservative and reflects only proven public-source coverage.
- No inactive downstream module behavior is introduced.
