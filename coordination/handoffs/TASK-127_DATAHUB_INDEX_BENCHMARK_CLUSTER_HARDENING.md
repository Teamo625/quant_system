# TASK-127 DataHub Index Benchmark Capability Cluster Hardening

## Role

5.3 Execution Window.

## Phase

Phase 2.5-P DataHub Personal Trading Perfection Re-Review.

## Context

TASK-126 is closed after accepted Review Agent verification. It preserved bounded mainland index daily-bar behavior, added major Hong Kong benchmark daily-bar support with explicit `source_route` truth, kept default tests offline-safe, and recorded independently reproduced live-enabled PASS evidence.

Phase 2.5-P remains open under `coordination/PHASE_GATE.md` because `build_default_personal_trading_readiness_report()` still reports `overall_status=blocked`, `phase_closure_ready=False`, status counts `pass=3`, `warn=6`, `blocked=1`, `fail=0`, and unresolved non-pass follow-up batches. `index_weight_history` remains an owner paid-credential blocker, and optional `hk_minute_bars` remains owner-waiver-required.

This handoff applies the current capability-cluster policy. The selected readiness batch is:

- batch id: `index__datahub_hardening__index__batch_01`
- disposition: `datahub_hardening`
- recommended theme: `cluster harden DataHub capabilities: index_daily_bars, index_constituent_history, index_rebalance_effective_dates, index_china_hk_global_benchmarks`

Included follow-up items:

- `index__index_capability_readiness__index_daily_bars`
- `index__index_capability_readiness__index_constituent_history`
- `index__index_capability_readiness__index_rebalance_effective_dates`
- `index__index_capability_readiness__index_china_hk_global_benchmarks`

This task stays inside DataHub. It must not reopen FeatureHub, Scanner, StrategyLab, BacktestEngine, portfolio, signal, risk, AI, notification, UI, automated trading, paid credentials, or private data.

## Objective

Harden the public-source index benchmark capability cluster for practical personal quant research:

- `index_daily_bars`: strengthen or truthfully constrain global benchmark history, non-mainland breadth, route/source truth, and public-route redundancy after TASK-126's mainland plus HK benchmark support.
- `index_constituent_history`: strengthen or truthfully constrain broader benchmark constituent breadth and longer constituent history continuity beyond the bounded core China slice.
- `index_rebalance_effective_dates`: preserve or improve explicit dated membership, effective-date, end-date, and rebalance-calendar truth where stable public routes expose it.
- `index_china_hk_global_benchmarks`: make benchmark universe/source-capability truth explicit for China, Hong Kong, and key global benchmarks without overclaiming exhaustive public-source coverage.

Execution should add stable no-credential public-source support where feasible. If stronger public routes are not feasible, execution must tighten capability/catalog wording and tests so unsupported benchmark families, missing rebalance calendars, or global coverage gaps are not silently treated as complete.

Keep all index capabilities conservative unless implementation, tests, and gated live evidence genuinely satisfy the practical public-source personal trading completeness standard.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-127_DATAHUB_INDEX_BENCHMARK_CLUSTER_HARDENING.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/ROADMAP.md`
- `coordination/reports/TASK-088_REPORT.md`
- `coordination/reviews/TASK-088_REVIEW.md`
- `coordination/reports/TASK-089_REPORT.md`
- `coordination/reviews/TASK-089_REVIEW.md`
- `coordination/reports/TASK-126_REPORT.md`
- `coordination/reviews/TASK-126_REVIEW.md`
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/datasets.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_index_adapter.py`
- `tests/datahub/test_akshare_index_live.py`
- `tests/datahub/test_akshare_index_constituents_adapter.py`
- `tests/datahub/test_akshare_index_constituents_live.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`
- related index DataHub tests only as needed to preserve compatibility

## Allowed Writes

Only:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py` only if an adapter export needs a minimal compatibility update
- `quant/datahub/datasets.py` only if a minimal schema-compatible index source-fact clarification is unavoidable
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_index_adapter.py`
- `tests/datahub/test_akshare_index_live.py`
- `tests/datahub/test_akshare_index_constituents_adapter.py`
- `tests/datahub/test_akshare_index_constituents_live.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`
- any new focused `tests/datahub/test_akshare_index*.py` file needed for this handoff
- `coordination/reports/TASK-127_REPORT.md`

If a tightly related index test file must change, document the exact reason in the report. Do not touch unrelated DataHub domains.

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files other than `coordination/reports/TASK-127_REPORT.md`
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

Do not implement or promote `index_weight_history`; the credentialed Tushare path remains blocked until the owner provides paid scope and a future live PASS is reviewed.

## Implementation Requirements

- Preserve TASK-126 accepted `INDEX_DAILY_BARS` behavior for mainland and Hong Kong benchmark requests.
- Preserve TASK-089 accepted `INDEX_CONSTITUENTS` behavior for bounded caller-provided multi-index constituent requests.
- Prefer caller-provided, bounded symbol/date/index requests. Keep `symbols=None` or empty symbol requests as clear errors unless a route is explicitly designed and tested as a bounded catalog/list operation.
- Investigate stable no-credential public routes within repository-supported source families for:
  - major global benchmark daily bars;
  - broader China/HK benchmark daily bars;
  - broader benchmark constituent coverage;
  - longer constituent history continuity;
  - explicit effective-date, end-date, rebalance-date, or index-level rebalance-calendar facts;
  - independent public-route redundancy.
- Emit only source-backed facts. Do not invent OHLCV, amount, constituent weights, effective dates, end dates, rebalance dates, benchmark family, source timestamps, or source-route values when a verified route does not provide them.
- Preserve route/source truth with `source`, route-local symbol normalization, market suffix, benchmark family where source-backed, and any available source timestamp/provenance fields.
- Route-distinct facts must remain distinguishable when values can differ.
- Honor `start_date` and `end_date` deterministically as bounded windows. If a route returns wider history, filter to the requested window.
- Reject malformed, ambiguous, unsupported, A-share stock, ETF/fund, Hong Kong stock, and non-index symbols clearly unless a route is explicitly proven to support the requested benchmark family.
- If a batch includes one invalid symbol or one repository-side schema/normalization defect, fail clearly rather than returning partial successful output.
- If a valid requested index yields no usable rows while another succeeds for the same bounded request, fail clearly unless execution can classify a source-wide route outage.
- Keep live-environment/source classifiers narrow. Network/proxy/DNS/TLS/upstream/source unavailability may skip; repository-side schema, contract, normalization, duplicate-conflict, route-signature, call-compatibility, unbounded-fetch, or date-window defects must fail.
- Update `source_catalog` and `source_capabilities` only to reflect proven public-source truth. Keep `index_daily_bars`, `index_constituent_history`, `index_rebalance_effective_dates`, and `index_china_hk_global_benchmarks` conservative unless full practical public-source breadth, history continuity, and redundancy are genuinely proven.
- If no stable broader no-credential route is feasible for a capability, record attempted route names and observed limitations in the report, add or preserve tests that prevent overclaiming, and leave capability truth conservative.

## Tests

Required offline/default tests:

- `python3 -m unittest tests.datahub.test_source_capabilities`
- `python3 -m unittest tests.datahub.test_source_catalog`
- `python3 -m unittest tests.datahub.test_akshare_index_adapter`
- `python3 -m unittest tests.datahub.test_akshare_index_constituents_adapter`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_index_live`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_index_constituents_live`
- focused index tests for every changed adapter/test file

Live smoke requirement:

- If any real-source index daily-bar path is added or materially changed, run `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_index_live`.
- If any real-source index constituent/rebalance path is added or materially changed, run `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_index_constituents_live`.
- Live smokes must be explicitly gated and skipped by default.
- Live-enabled smoke should validate at least one newly supported or materially changed benchmark family when upstream routes are available.
- Report PASS, SKIP, or FAIL truthfully with root-cause evidence. If a live smoke skips because of network, proxy, DNS, TLS, upstream, or public-source availability, diagnose and modify allowed code/tests/report where feasible instead of only documenting the skip.

## Completion Report

Write `coordination/reports/TASK-127_REPORT.md` with:

- files changed
- implementation summary
- selected readiness batch id and included follow-up ids
- index route/source-family investigation result
- supported index symbol classes, benchmark families, market suffixes, date behavior, source-route truth, and deduplication behavior
- constituent/effective-date/rebalance source truth and known limitations
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence for daily-bar and constituent/rebalance smokes as applicable
- whether any of the four index capability truths changed
- confirmation that `index_weight_history` remained out of scope and blocked
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

The task is complete when:

- The index benchmark cluster has stronger public-source proof or stricter capability/catalog truth for all included follow-up items.
- Any emitted `INDEX_DAILY_BARS` or `INDEX_CONSTITUENTS` records validate against their dataset contracts.
- Default tests remain offline-safe and live tests remain skipped by default.
- Any real-source work has gated live evidence or a truthful diagnosed SKIP/FAIL requiring Review/Controller follow-up.
- Capability metadata remains conservative and reflects only proven public-source coverage.
- `index_weight_history` remains blocked/planned unless a separate owner credential scope is opened.
- No inactive downstream module behavior is introduced.
