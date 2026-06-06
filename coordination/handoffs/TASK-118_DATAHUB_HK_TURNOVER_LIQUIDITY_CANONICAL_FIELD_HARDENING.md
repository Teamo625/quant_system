# TASK-118 DataHub Hong Kong Turnover/Liquidity Canonical Field Hardening

## Role

5.3 Execution Window.

## Context

TASK-117 is closed after accepted Review Agent verification of the focused Hong Kong financial live-classifier rework. The final review accepted default offline-safe tests and live-enabled PASS evidence, and confirmed HK financial route-name-bearing signature/schema/payload/normalization defects now remain hard failures instead of being downgraded to environment `SKIP`. The rework was classifier-only and did not promote `hk_financial_data`.

Phase 2.5-P remains open under `coordination/PHASE_GATE.md` because `build_default_personal_trading_readiness_report()` still reports `overall_status=blocked`, `phase_closure_ready=False`, and 42 non-pass follow-up queue items. `index_weight_history` remains an owner credential blocker, and optional `hk_minute_bars` remains owner-waiver-required.

The next executable TASK-093 queue item is:

- follow-up id: `hong_kong__hong_kong_capability_readiness__hk_turnover_liquidity`
- capability: `hk_turnover_liquidity`
- disposition: `datahub_hardening`
- theme: HK liquidity canonical field definitions and checks
- reason: turnover metrics are available through existing HK daily-bar source facts, but they are not normalized or documented as an explicit liquidity/turnover contract surface.

This task stays inside DataHub. It must not reopen FeatureHub, Scanner, StrategyLab, BacktestEngine, portfolio, signal, risk, AI, notification, UI, automated trading, paid credentials, or private data.

## Objective

Make Hong Kong turnover/liquidity semantics explicit and test-covered in DataHub without implementing downstream liquidity factors.

Execution should do one of the following:

1. Define a canonical source-fact contract/profile surface for source-backed HK turnover/liquidity facts, using only fields truthfully exposed by stable no-credential public routes; or
2. If no stronger explicit contract is justified, truthfully constrain `hk_turnover_liquidity` source-capability/catalog wording and add tests that prevent overclaiming.

The result must keep `hk_turnover_liquidity` conservative unless implementation, tests, and gated live evidence genuinely satisfy practical public-source personal trading completeness for HK turnover/liquidity data.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-118_DATAHUB_HK_TURNOVER_LIQUIDITY_CANONICAL_FIELD_HARDENING.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/ROADMAP.md`
- `coordination/reports/TASK-079_REPORT.md`
- `coordination/reviews/TASK-079_REVIEW.md`
- `coordination/reports/TASK-114_REPORT.md`
- `coordination/reviews/TASK-114_REVIEW.md`
- `coordination/reports/TASK-103_REPORT.md`
- `coordination/reviews/TASK-103_REVIEW.md`
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/datasets.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_hk_adapter.py`
- `tests/datahub/test_akshare_hk_live.py`
- `tests/datahub/test_source_capabilities.py`
- related DataHub tests only as needed

## Allowed Writes

Only:

- `quant/datahub/datasets.py`
- `quant/datahub/source_catalog.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/adapters/akshare.py`
- `tests/datahub/test_datasets.py`
- `tests/datahub/test_source_catalog.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_akshare_hk_adapter.py`
- `tests/datahub/test_akshare_hk_live.py`
- any new focused `tests/datahub/test_akshare_hk_turnover_liquidity*.py` file needed for this handoff
- `coordination/reports/TASK-118_REPORT.md`

If a tightly related shared DataHub helper test must change, document the exact reason in the report. Do not touch unrelated DataHub domains.

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files other than `coordination/reports/TASK-118_REPORT.md`
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

- Preserve existing `DatasetName.DAILY_BARS` compatibility for HK daily-bar records.
- Review existing HK daily-bar source truth before editing, especially `volume`, `amount`, `source`, date-window behavior, `stock_hk_hist`, and `stock_hk_daily` fallback handling.
- Use only stable no-credential public routes. Do not add Tushare, paid endpoints, credentialed APIs, browser/session scraping, private data, or unbounded full-market collection.
- Define canonical source-fact semantics only for source-backed HK turnover/liquidity fields, such as symbol, trade date, volume, traded amount, source, source route, route family, and any additional liquidity metric directly exposed by the route.
- Do not fabricate turnover rate, free-float turnover, market value, float shares, VWAP, liquidity scores, spread estimates, bid/ask metrics, or derived factors unless a public route directly exposes the fact and the field semantics are documented in schema/tests.
- If adding a dedicated dataset/profile, use deterministic record identity by at least symbol, trade date, source, source route or route family, and metric granularity. Avoid silently merging route-distinct facts when values can differ.
- Preserve canonical HK stock symbols, `market="HK"`, deterministic sorting, bounded caller-provided requests, date-window filtering, invalid range rejection, and clear errors for malformed/unsupported/empty symbol requests.
- Preserve source-truth optionality for fields that public routes do not reliably expose.
- Keep route-name-bearing AKShare argument/signature compatibility errors as hard failures following existing DataHub live-failure classification policy.
- Keep live-environment/source classifiers narrow. Network/proxy/DNS/TLS/upstream/source unavailability may skip; repository-side schema, contract, normalization, duplicate-conflict, or route-signature defects must fail.
- Update `source_catalog` and `source_capabilities` only to reflect proven public-source truth. Keep `hk_turnover_liquidity` conservative unless implementation and live evidence prove full practical public-source breadth and continuity.
- If no stable broader no-credential route is feasible, preserve implementation behavior, add contract/test/reporting clarity that prevents overclaiming, and record attempted route names plus observed limitations in the report.

## Tests

Required offline/default tests:

- `python3 -m unittest tests/datahub/test_datasets.py`
- `python3 -m unittest tests/datahub/test_source_catalog.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`
- `python3 -m unittest tests/datahub/test_akshare_hk_adapter.py`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_hk_live.py`

If a new focused HK turnover/liquidity adapter/live test file is added, also run its offline/default path.

Live smoke requirement:

- If any real-source HK turnover/liquidity adapter path is added or materially changed, run the relevant gated live smoke with `QUANT_SYSTEM_LIVE_TESTS=1`.
- The live smoke must be explicitly gated and skipped by default.
- The live-enabled smoke should validate at least two HK stock symbols and at least one source-backed dated turnover/liquidity record if the upstream source is available.
- Report PASS, SKIP, or FAIL truthfully with root-cause evidence. If the live smoke skips because of network, proxy, DNS, TLS, upstream, or public-source availability, diagnose and modify allowed code/tests/report where feasible instead of only documenting the skip.

## Completion Report

Write `coordination/reports/TASK-118_REPORT.md` with:

- files changed
- implementation summary
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence, or explicit `SKIP` only if no real-source adapter path was added or materially changed
- HK turnover/liquidity contract/profile fields, granularity, identity, and known limitations
- route/source-family investigation result for HK turnover/liquidity source facts
- whether `hk_turnover_liquidity` capability truth changed
- confirmation that existing HK daily-bar compatibility was preserved unless explicitly justified
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

The task is complete when:

- HK turnover/liquidity semantics are explicit in DataHub through a dedicated schema/profile or equivalent first-class contract surface, or capability/catalog wording is truthfully constrained without promotion.
- Source-backed records validate against the relevant DataHub schema.
- Default tests remain offline-safe and live tests remain skipped by default.
- Any real-source work has gated live evidence or a truthful diagnosed SKIP/FAIL requiring Review/Controller follow-up.
- Capability metadata remains conservative and reflects only proven public-source coverage.
- No inactive downstream module behavior is introduced.
