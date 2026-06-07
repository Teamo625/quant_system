# TASK-126 DataHub Index Daily-Bars Breadth and Benchmark Coverage Hardening

## Role

5.3 Execution Window.

## Phase

Phase 2.5-P DataHub Personal Trading Perfection Re-Review.

## Context

TASK-125 is closed after accepted Review Agent verification. It hardened ETF/fund `DatasetName.FUND_PREMIUM_DISCOUNT` breadth/history, then completed the focused live-classifier rework so historical route/function-name tokens such as `fund_etf_hist_em` no longer downgrade route-signature or call-compatibility defects into environment `SKIP`. Default tests remain offline-safe and the gated live-enabled premium-discount smoke passed.

Phase 2.5-P remains open under `coordination/PHASE_GATE.md` because unresolved DataHub personal trading perfection queue items remain. `index_weight_history` remains an owner paid-credential blocker; optional `hk_minute_bars` remains owner-waiver-required; and index, sector/concept, macro/policy, and quality-report gaps still require accepted DataHub hardening or owner-accepted disposition before FeatureHub can reopen.

The next executable TASK-093 queue item is:

- follow-up id: `index__index_capability_readiness__index_daily_bars`
- capability: `index_daily_bars`
- disposition: `datahub_hardening`
- theme: expand benchmark breadth and broader China/HK/global index daily-bar coverage beyond the bounded core benchmark slice
- reason: TASK-088 proved caller-provided multi-index bounded daily-bar access for core China benchmark symbols, but broader benchmark breadth, longer history continuity, and non-mainland/global benchmark coverage remain incomplete.

This task stays inside DataHub. It must not reopen FeatureHub, Scanner, StrategyLab, BacktestEngine, portfolio, signal, risk, AI, notification, UI, automated trading, paid credentials, or private data.

## Objective

Harden public-source `DatasetName.INDEX_DAILY_BARS` source truth beyond the accepted bounded core China benchmark slice where stable no-credential public routes expose broader benchmark breadth, longer history continuity, HK/global index support, route/source truth, or redundancy.

Execution should do one of the following:

1. Expand AKShare-backed index daily-bar support to additional stable no-credential public routes, benchmark families, market suffixes, dated history continuity, or route/source truth while preserving existing accepted China index behavior; or
2. If no stronger public route is feasible, truthfully constrain `index_daily_bars` source-capability/catalog wording and add tests/report evidence that prevent overclaiming.

Keep `index_daily_bars` conservative unless implementation, tests, and gated live evidence genuinely satisfy practical public-source personal trading completeness for index daily-bar and benchmark coverage.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-126_DATAHUB_INDEX_DAILY_BARS_BREADTH_BENCHMARK_HARDENING.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/ROADMAP.md`
- `coordination/reports/TASK-088_REPORT.md`
- `coordination/reviews/TASK-088_REVIEW.md`
- `coordination/reports/TASK-125_REPORT.md`
- `coordination/reviews/TASK-125_REVIEW.md`
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/datasets.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_index_adapter.py`
- `tests/datahub/test_akshare_index_live.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`
- related index DataHub tests only as needed to preserve compatibility

## Allowed Writes

Only:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py` only if an adapter export needs a minimal compatibility update
- `quant/datahub/datasets.py` only if a minimal schema-compatible clarification is unavoidable
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_index_adapter.py`
- `tests/datahub/test_akshare_index_live.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`
- any new focused `tests/datahub/test_akshare_index*.py` file needed for this handoff
- `coordination/reports/TASK-126_REPORT.md`

If a tightly related index test file must change, document the exact reason in the report. Do not touch unrelated DataHub domains.

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files other than `coordination/reports/TASK-126_REPORT.md`
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

- Preserve existing `AkshareIndexDailyBarAdapter` behavior for accepted bounded multi-symbol China index requests such as `000300.CN_INDEX` and `399001.CN_INDEX`.
- Preserve `DatasetName.INDEX_DAILY_BARS` validation compatibility; do not add feature, constituent, weight, rebalance, or downstream benchmark-relative fields to daily-bar records unless a source-backed schema-compatible clarification is unavoidable and justified.
- Prefer caller-provided, bounded symbol/date requests. Keep `symbols=None` or empty symbol requests as clear errors; do not silently fetch unbounded full-market index tables.
- Investigate stable no-credential public routes within repository-supported source families that truthfully expose index OHLCV daily bars for broader China benchmark families, HK benchmark indices, major global benchmarks, longer history continuity, or independent route redundancy.
- Emit records only for source-backed facts. Do not invent OHLCV, amount, date, market, benchmark family, source timestamp, or source-route values when a verified route does not provide them.
- Preserve route/source truth with `source`, route-local symbol normalization, market suffix, and any available source timestamp/provenance fields. Route-distinct facts must remain distinguishable when values can differ.
- Honor `start_date` and `end_date` deterministically as bounded windows. If a route returns wider history, filter to the requested window.
- Reject malformed, ambiguous, unsupported, A-share stock, ETF/fund, Hong Kong stock, and non-index symbols clearly unless a route is explicitly proven to support the benchmark family.
- If a batch includes one invalid symbol or one repository-side schema/normalization defect, fail clearly rather than returning partial successful output.
- If a valid requested symbol yields no usable rows while another succeeds for the same bounded request, fail clearly unless execution can classify a source-wide route outage.
- Keep live-environment/source classifiers narrow. Network/proxy/DNS/TLS/upstream/source unavailability may skip; repository-side schema, contract, normalization, duplicate-conflict, route-signature, call-compatibility, unbounded-fetch, or date-window defects must fail.
- Update `source_catalog` and `source_capabilities` only to reflect proven public-source truth. Keep `index_daily_bars` conservative unless full practical public-source benchmark breadth, history continuity, and redundancy are genuinely proven.
- If no stable broader no-credential route is feasible, record attempted route names and observed limitations in the report, add tests that prevent overclaiming, and leave capability truth conservative.

## Tests

Required offline/default tests:

- `python3 -m unittest tests.datahub.test_source_capabilities`
- `python3 -m unittest tests.datahub.test_source_catalog`
- `python3 -m unittest tests.datahub.test_akshare_index_adapter`
- focused index adapter tests for every changed adapter/test file
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_index_live`

Live smoke requirement:

- If any real-source index daily-bar adapter path is added or materially changed, run the relevant gated live smoke with `QUANT_SYSTEM_LIVE_TESTS=1`.
- The live smoke must be explicitly gated and skipped by default.
- The live-enabled smoke should validate at least two supported index symbols and at least one schema-valid `INDEX_DAILY_BARS` record if the upstream source is available.
- If broader HK/global benchmark support is added, include at least one added benchmark family in the gated live smoke when upstream routes are available.
- Report PASS, SKIP, or FAIL truthfully with root-cause evidence. If the live smoke skips because of network, proxy, DNS, TLS, upstream, or public-source availability, diagnose and modify allowed code/tests/report where feasible instead of only documenting the skip.

## Completion Report

Write `coordination/reports/TASK-126_REPORT.md` with:

- files changed
- implementation summary
- index daily-bar route/source-family investigation result
- supported symbol classes, market suffixes, date behavior, source-route truth, and deduplication behavior
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence, or explicit `SKIP` only if no real-source adapter path was added or materially changed
- whether `index_daily_bars` capability truth changed
- confirmation that existing China index daily-bar dataset compatibility was preserved
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

The task is complete when:

- index daily-bar source truth is stronger through added public-route breadth/history coverage, or capability/catalog wording is truthfully constrained without promotion.
- Any emitted source-backed records validate against `DatasetName.INDEX_DAILY_BARS`.
- Default tests remain offline-safe and live tests remain skipped by default.
- Any real-source work has gated live evidence or a truthful diagnosed SKIP/FAIL requiring Review/Controller follow-up.
- Capability metadata remains conservative and reflects only proven public-source coverage.
- No inactive downstream module behavior is introduced.
