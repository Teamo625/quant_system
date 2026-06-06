# TASK-121 DataHub ETF/Fund Holdings Breadth and History Hardening

## Role

5.3 Execution Window.

## Context

TASK-120 is closed after accepted Review Agent verification. It hardened ETF/fund `DatasetName.FUND_NAV_SNAPSHOT` by adding explicit `FUND_CN` public-fund NAV history support through the same-family open-fund route, preserved accepted exchange ETF behavior, added bounded ETF empty-window fallback, kept default tests offline-safe, recorded live-enabled PASS evidence, and kept `fund_nav` conservative at `partial`.

Phase 2.5-P remains open under `coordination/PHASE_GATE.md` because `build_default_personal_trading_readiness_report()` still reports `overall_status=blocked` and `phase_closure_ready=False`. `index_weight_history` remains an owner credential blocker, optional `hk_minute_bars` remains owner-waiver-required, and unresolved ETF/fund holdings/scale/flow/premium-discount, index, sector/concept, macro/policy, and quality-report warn items still require hardening or explicit owner-accepted disposition.

The next executable TASK-093 queue item is:

- follow-up id: `etf_fund__etf_fund_capability_readiness__fund_holdings_composition`
- capability: `fund_holdings_composition`
- disposition: `datahub_hardening`
- theme: expand ETF/fund holdings breadth and history continuity beyond bounded public report-period coverage
- reason: public AKShare now supports caller-provided multi-symbol bounded report-period fund-holdings access, but broader fund breadth, longer history continuity, and non-exchange public-route coverage remain incomplete.

This task stays inside DataHub. It must not reopen FeatureHub, Scanner, StrategyLab, BacktestEngine, portfolio, signal, risk, AI, notification, UI, automated trading, paid credentials, or private data.

## Objective

Harden ETF/fund `DatasetName.FUND_HOLDINGS` source truth beyond the accepted bounded public report-period holdings slice where stable no-credential public routes expose broader breadth, history, taxonomy, or route/source truth.

Execution should do one of the following:

1. Expand AKShare-backed ETF/fund holdings support to additional stable no-credential public routes, fund classes, report-period continuity, or source-backed holdings taxonomy while preserving existing accepted behavior; or
2. If no stronger public route is feasible, truthfully constrain `fund_holdings_composition` source-capability/catalog wording and add tests/report evidence that prevent overclaiming.

The result must keep `fund_holdings_composition` conservative unless implementation, tests, and gated live evidence genuinely satisfy practical public-source personal trading completeness for ETF/fund holdings/composition.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-121_DATAHUB_ETF_FUND_HOLDINGS_BREADTH_HISTORY_HARDENING.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/ROADMAP.md`
- `coordination/reports/TASK-031_REPORT.md`
- `coordination/reviews/TASK-031_REVIEW.md`
- `coordination/reports/TASK-084_REPORT.md`
- `coordination/reviews/TASK-084_REVIEW.md`
- `coordination/reports/TASK-120_REPORT.md`
- `coordination/reviews/TASK-120_REVIEW.md`
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/datasets.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_fund_holdings_adapter.py`
- `tests/datahub/test_akshare_fund_holdings_live.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`
- related DataHub tests only as needed

## Allowed Writes

Only:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_fund_holdings_adapter.py`
- `tests/datahub/test_akshare_fund_holdings_live.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`
- any new focused `tests/datahub/test_akshare_etf_fund_holdings*.py` file needed for this handoff
- `coordination/reports/TASK-121_REPORT.md`

If a tightly related shared DataHub helper test must change, document the exact reason in the report. Do not touch unrelated DataHub domains.

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files other than `coordination/reports/TASK-121_REPORT.md`
- `coordination/reviews/**`
- `coordination/integrations/**`
- `quant/datahub/datasets.py` unless a reviewed route makes a minimal schema-compatible clarification unavoidable; if so, justify it in the report and keep `DatasetName.FUND_HOLDINGS` compatibility
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

- Preserve existing `AkshareETFFundHoldingsAdapter` behavior for accepted bounded multi-symbol/report-period requests.
- Preserve `DatasetName.FUND_HOLDINGS` validation compatibility; do not add NAV, daily-bar OHLCV, premium/discount, fund-flow, or feature fields to holdings records.
- Investigate only stable no-credential public routes available through repository-supported source families, especially routes that may prove broader China ETF/fund holdings breadth, non-exchange fund holdings/composition, report-period history, or route/source truth.
- Keep `symbols=None` or empty symbol requests as clear errors; do not silently fetch unbounded full-market ETF/fund data.
- Preserve canonical fund/ETF symbols, deterministic sorting, bounded caller-provided requests, report-period/date-window filtering, invalid range rejection, and clear errors for malformed/unsupported/empty symbol requests.
- Reject A-share, Hong Kong stock, index-like, malformed, ambiguous, missing, and unsupported symbols clearly.
- Preserve route/source truth with `source`, `source_route`, or equivalent route-family metadata where the current contract and adapter pattern support it; avoid silently merging route-distinct facts when values can differ.
- Deduplicate deterministically by at least `(fund_code, holding_symbol, report_period, source)` and route identity where route-distinct fields are present.
- If one symbol fails due to invalid input or adapter/schema/normalization behavior, fail clearly rather than returning partial successful batch output.
- If one valid requested symbol yields no usable rows while another succeeds for the same bounded report-period window, fail clearly unless the adapter can classify a source-wide route outage.
- Keep live-environment/source classifiers narrow. Network/proxy/DNS/TLS/upstream/source unavailability may skip; repository-side schema, contract, normalization, duplicate-conflict, or route-signature defects must fail.
- Update `source_catalog` and `source_capabilities` only to reflect proven public-source truth. Keep `fund_holdings_composition` conservative unless implementation and live evidence prove full practical public-source breadth and continuity.
- If no stable broader no-credential route is feasible, preserve implementation behavior, add tests and capability/catalog wording that prevent overclaiming, and record attempted route names plus observed limitations in the report.

## Tests

Required offline/default tests:

- `python3 -m unittest tests/datahub/test_akshare_fund_holdings_adapter.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`
- `python3 -m unittest tests/datahub/test_source_catalog.py`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_fund_holdings_live.py`

If a new focused ETF/fund holdings adapter/live test file is added, also run its offline/default path.

Live smoke requirement:

- If any real-source ETF/fund holdings adapter path is added or materially changed, run the relevant gated live smoke with `QUANT_SYSTEM_LIVE_TESTS=1`.
- The live smoke must be explicitly gated and skipped by default.
- The live-enabled smoke should validate at least two supported ETF/fund symbols and at least one schema-valid holdings record if the upstream source is available.
- Report PASS, SKIP, or FAIL truthfully with root-cause evidence. If the live smoke skips because of network, proxy, DNS, TLS, upstream, or public-source availability, diagnose and modify allowed code/tests/report where feasible instead of only documenting the skip.

## Completion Report

Write `coordination/reports/TASK-121_REPORT.md` with:

- files changed
- implementation summary
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence, or explicit `SKIP` only if no real-source adapter path was added or materially changed
- ETF/fund holdings route/source-family investigation result
- supported symbol classes, report-period granularity, identity, deduplication behavior, and known limitations
- whether `fund_holdings_composition` capability truth changed
- confirmation that existing ETF/fund holdings compatibility was preserved unless explicitly justified
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

The task is complete when:

- ETF/fund holdings source truth is stronger through added public-route breadth/history coverage, or capability/catalog wording is truthfully constrained without promotion.
- Source-backed records validate against `DatasetName.FUND_HOLDINGS`.
- Default tests remain offline-safe and live tests remain skipped by default.
- Any real-source work has gated live evidence or a truthful diagnosed SKIP/FAIL requiring Review/Controller follow-up.
- Capability metadata remains conservative and reflects only proven public-source coverage.
- No inactive downstream module behavior is introduced.
