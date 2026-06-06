# TASK-123 DataHub ETF/Fund Scale/Share Source Breadth Hardening

## Role

5.3 Execution Window.

## Phase

Phase 2.5-P DataHub Personal Trading Perfection Re-Review.

## Context

TASK-122 is closed after accepted Review Agent verification. It added the first-class `DatasetName.FUND_SCALE_SHARE_SNAPSHOT` contract, fixed signed metric semantics so negative change-style observations validate while nonnegative level metrics remain protected, kept default tests offline-safe, and did not change adapter/source collection behavior. `fund_scale_and_share` remains conservative at `partial` because accepted public proof is still limited to overlapping scale/share fields from existing profile/NAV/exchange scale-share routes, not a dedicated adapter-backed scale/share source-fact path with broader public-source breadth, history continuity, and route redundancy.

Phase 2.5-P remains open under `coordination/PHASE_GATE.md` because DataHub still has unresolved personal trading perfection queue items. `index_weight_history` remains an owner credential blocker, optional `hk_minute_bars` remains owner-waiver-required, and unresolved ETF/fund scale/flow/premium-discount, index, sector/concept, macro/policy, and quality-report gaps still require accepted DataHub hardening or explicit owner-accepted disposition.

The next executable DataHub hardening item continues `fund_scale_and_share`:

- capability: `fund_scale_and_share`
- disposition: `datahub_hardening`
- theme: expand ETF/fund scale/share breadth, longer history continuity, and independent route redundancy beyond the current overlapping profile/NAV/exchange scale-share public-source proof
- current truth: `partial`

This task stays inside DataHub. It must not reopen FeatureHub, Scanner, StrategyLab, BacktestEngine, portfolio, signal, risk, AI, notification, UI, automated trading, paid credentials, or private data.

## Objective

Harden ETF/fund `DatasetName.FUND_SCALE_SHARE_SNAPSHOT` source truth beyond the accepted canonical schema by wiring or proving stable no-credential public scale/share facts where feasible, or by truthfully constraining capability/source wording without promotion if stronger public routes are not feasible.

Execution should do one of the following:

1. Add or wire a DataHub adapter path that emits schema-valid `FUND_SCALE_SHARE_SNAPSHOT` records from stable no-credential public ETF/fund scale/share routes, preserving explicit `source_route`, `metric_code`, `metric_name`, `metric_value`, `metric_unit`, and `observation_type` semantics; or
2. If no stronger public route is feasible, preserve current implementation behavior, tighten capability/source metadata and focused tests so the system cannot overclaim adapter-backed scale/share breadth.

Keep `fund_scale_and_share` conservative unless implementation, tests, and gated live evidence genuinely satisfy practical public-source personal trading completeness for ETF/fund scale/share data.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-123_DATAHUB_ETF_FUND_SCALE_SHARE_SOURCE_BREADTH_HARDENING.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/ROADMAP.md`
- `coordination/reports/TASK-051_REPORT.md`
- `coordination/reviews/TASK-051_REVIEW.md`
- `coordination/reports/TASK-085_REPORT.md`
- `coordination/reviews/TASK-085_REVIEW.md`
- `coordination/reports/TASK-120_REPORT.md`
- `coordination/reviews/TASK-120_REVIEW.md`
- `coordination/reports/TASK-122_REPORT.md`
- `coordination/reviews/TASK-122_REVIEW.md`
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/datasets.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_datasets.py`
- `tests/datahub/test_akshare_fund_flow_adapter.py`
- `tests/datahub/test_akshare_fund_flow_live.py`
- `tests/datahub/test_akshare_fund_nav_adapter.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`
- related DataHub ETF/fund tests only as needed

## Allowed Writes

Only:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/datasets.py` only if a minimal schema-compatible clarification is unavoidable
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_datasets.py` only if schema semantics require focused clarification
- `tests/datahub/test_akshare_fund_flow_adapter.py`
- `tests/datahub/test_akshare_fund_flow_live.py`
- `tests/datahub/test_akshare_fund_nav_adapter.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`
- any new focused `tests/datahub/test_akshare_fund_scale_share*.py` file needed for this handoff
- `coordination/reports/TASK-123_REPORT.md`

If a tightly related shared DataHub helper test must change, document the exact reason in the report. Do not touch unrelated DataHub domains.

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files other than `coordination/reports/TASK-123_REPORT.md`
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

- Preserve `DatasetName.FUND_SCALE_SHARE_SNAPSHOT` validation compatibility from TASK-122, including signed change metrics and nonnegative level metrics.
- Preserve accepted `FUND_PROFILE`, `FUND_NAV_SNAPSHOT`, and `FUND_FLOW` behavior unless a minimal compatibility-preserving clarification is required and justified.
- Prefer caller-provided, bounded symbol/date/report-period requests. Do not silently fetch unbounded full-market ETF/fund data.
- Investigate stable no-credential public routes already within repository-supported source families, especially existing AKShare ETF/fund profile, NAV, and exchange scale/share routes that expose fund scale, shares outstanding, share-unit, AUM, or share-change facts.
- Emit scale/share records only for source-backed facts. Do not invent net inflow, subscription, redemption, premium/discount, holdings, NAV, market-price, or feature fields in `FUND_SCALE_SHARE_SNAPSHOT`.
- Preserve route/source truth with `source`, `source_route`, and explicit metric identity. Route-distinct facts must remain distinguishable when values can differ.
- Use deterministic identity and sorting. Deduplicate at least by `(fund_code, as_of_date, source, source_route, metric_code, observation_type)` when those fields are present.
- Reject malformed, ambiguous, unsupported, A-share stock, Hong Kong stock, and index-like symbols clearly unless a route is explicitly proven to support the fund/ETF family.
- If a batch includes one invalid symbol or one repository-side schema/normalization defect, fail clearly rather than returning partial successful output.
- If a valid requested symbol yields no usable rows while another succeeds for the same bounded request, fail clearly unless execution can classify a source-wide route outage.
- Keep live-environment/source classifiers narrow. Network/proxy/DNS/TLS/upstream/source unavailability may skip; repository-side schema, contract, normalization, duplicate-conflict, or route-signature defects must fail.
- Update `source_catalog` and `source_capabilities` only to reflect proven public-source truth. Keep `fund_scale_and_share` conservative unless full practical public-source breadth, history continuity, and redundancy are genuinely proven.
- If no stable broader no-credential route is feasible, record attempted route names and observed limitations in the report, add tests that prevent overclaiming, and leave capability truth conservative.

## Tests

Required offline/default tests:

- `python3 -m unittest tests.datahub.test_datasets`
- `python3 -m unittest tests.datahub.test_source_capabilities`
- `python3 -m unittest tests.datahub.test_source_catalog`
- focused ETF/fund adapter tests for every changed adapter/test file
- default-skipped live test path for any new or changed live smoke, run with `env -u QUANT_SYSTEM_LIVE_TESTS`

Live smoke requirement:

- If any real-source ETF/fund scale/share adapter path is added or materially changed, run the relevant gated live smoke with `QUANT_SYSTEM_LIVE_TESTS=1`.
- The live smoke must be explicitly gated and skipped by default.
- The live-enabled smoke should validate at least two supported ETF/fund symbols and at least one schema-valid `FUND_SCALE_SHARE_SNAPSHOT` record if the upstream source is available.
- Report PASS, SKIP, or FAIL truthfully with root-cause evidence. If the live smoke skips because of network, proxy, DNS, TLS, upstream, or public-source availability, diagnose and modify allowed code/tests/report where feasible instead of only documenting the skip.

## Completion Report

Write `coordination/reports/TASK-123_REPORT.md` with:

- files changed
- implementation summary
- scale/share source-route investigation result
- supported symbol classes, date/report-period behavior, metric identity, signed/nonnegative semantics, and deduplication behavior
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence, or explicit `SKIP` only if no real-source adapter path was added or materially changed
- whether `fund_scale_and_share` capability truth changed
- confirmation that existing ETF/fund dataset compatibility was preserved unless explicitly justified
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

The task is complete when:

- ETF/fund scale/share source truth is stronger through added public-route breadth/history coverage, or capability/catalog wording is truthfully constrained without promotion.
- Any emitted source-backed records validate against `DatasetName.FUND_SCALE_SHARE_SNAPSHOT`.
- Default tests remain offline-safe and live tests remain skipped by default.
- Any real-source work has gated live evidence or a truthful diagnosed SKIP/FAIL requiring Review/Controller follow-up.
- Capability metadata remains conservative and reflects only proven public-source coverage.
- No inactive downstream module behavior is introduced.
