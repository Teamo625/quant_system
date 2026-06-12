# TASK-137 DataHub index residual capability cluster hardening

## Role

5.3 Execution Window.

## Phase

Phase 2.5-P DataHub Personal Trading Perfection Re-Review.

## Context

TASK-136 is closed after accepted Review Agent verification. It completed the ETF/fund readiness batch `etf_fund__datahub_hardening__etf_fund__batch_01`, broadened proven listed-fund/LOF support for `fund_daily_bars` and `fund_premium_discount`, preserved default offline safety, recorded gated live PASS evidence, and kept ETF/fund capability truth conservative where no-credential public-source completeness remains unproven.

Phase 2.5-P remains open under `coordination/PHASE_GATE.md`. The current `build_default_personal_trading_readiness_report()` result is still:

- `overall_status=blocked`
- `phase_closure_ready=False`
- status counts: `pass=4`, `warn=5`, `blocked=1`, `fail=0`
- unresolved non-pass `follow_up_batches`

Controller read DataHub readiness `follow_up_batches`. TASK-131 through TASK-136 covered the A-share batches, Hong Kong hardening batch, HK minute-bars blocker-disposition batch, and ETF/fund batch. The next unresolved current-phase capability cluster in deterministic batch order after ETF/fund is:

- batch id: `index__datahub_hardening__index__batch_01`
- disposition: `datahub_hardening`
- recommended theme: `cluster harden DataHub capabilities: index_daily_bars, index_constituent_history, index_rebalance_effective_dates, index_china_hk_global_benchmarks`

Included follow-up items:

- `index__index_capability_readiness__index_daily_bars`
- `index__index_capability_readiness__index_constituent_history`
- `index__index_capability_readiness__index_rebalance_effective_dates`
- `index__index_capability_readiness__index_china_hk_global_benchmarks`

This is a coherent four-item index capability cluster because the items share the same index domain, benchmark breadth/history/source-redundancy theme, AKShare adapter/source metadata surface, and downstream DataHub contract consumers. This is a residual hardening pass after TASK-126 and TASK-127, not permission to over-promote partial public-source coverage.

`index_weight_history` is not included. It remains an owner paid-credential blocker under `index__owner_credential_blocker__index_index_capability_readiness_index_weight_history__batch_01` and must not be promoted without future owner-provided paid Tushare scope plus credentialed live PASS evidence.

## Objective

Strengthen stable no-credential public-source proof for the residual index benchmark batch where feasible, or truthfully constrain DataHub capability/source wording and tests when public routes remain incomplete.

The work must address all included capabilities:

- `index_daily_bars`: improve or truthfully constrain stable major US/global benchmark history, non-mainland breadth, long-history continuity, source-route truth, and public-route redundancy beyond accepted mainland, Hong Kong, and curated global slices.
- `index_constituent_history`: improve or truthfully constrain broader China/HK/global benchmark constituent breadth and longer constituent-history continuity beyond the accepted bounded China benchmark slice.
- `index_rebalance_effective_dates`: prove or truthfully constrain explicit rebalance/effective-date/end-date metadata and index-level rebalance-calendar facts where stable public routes expose them.
- `index_china_hk_global_benchmarks`: improve or truthfully constrain benchmark universe/source-capability truth for China, Hong Kong, major US, and key global benchmarks without claiming exhaustive public-source coverage.

Keep all index capabilities conservative unless implementation, tests, and gated live evidence genuinely satisfy practical public-source/no-paid personal trading completeness.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-137_DATAHUB_INDEX_RESIDUAL_CAPABILITY_CLUSTER_HARDENING.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/ROADMAP.md`
- `coordination/reports/TASK-088_REPORT.md`
- `coordination/reviews/TASK-088_REVIEW.md`
- `coordination/reports/TASK-089_REPORT.md`
- `coordination/reviews/TASK-089_REVIEW.md`
- `coordination/reports/TASK-126_REPORT.md`
- `coordination/reviews/TASK-126_REVIEW.md`
- `coordination/reports/TASK-127_REPORT.md`
- `coordination/reviews/TASK-127_REVIEW.md`
- `coordination/reports/TASK-136_REPORT.md`
- `coordination/reviews/TASK-136_REVIEW.md`
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

Read related index DataHub tests only as needed to preserve compatibility.

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
- `coordination/reports/TASK-137_REPORT.md`

If a tightly related index test file must change, document the exact reason in the report. Do not touch unrelated DataHub domains.

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files other than `coordination/reports/TASK-137_REPORT.md`
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

Do not implement FeatureHub indicators, scanner ranking, strategies, backtests, portfolio/signal/risk logic, AI reports, notifications, UI, or automated trading.

## Implementation Requirements

- Preserve accepted TASK-126 and TASK-127 index daily-bar, benchmark, constituent, and rebalance/effective-date behavior unless a genuine defect is found.
- Prefer caller-provided, bounded symbol/date/index requests. Keep `symbols=None`, empty symbol requests, or unbounded full-market fetches as clear errors unless a route is explicitly bounded, source-backed, tested, and justified.
- Investigate stable no-credential public routes within repository-supported source families for:
  - major US/global benchmark daily-bar history;
  - broader China/HK/global benchmark daily-bar breadth;
  - broader benchmark constituent coverage;
  - longer constituent-history continuity;
  - explicit effective-date, end-date, rebalance-date, or index-level rebalance-calendar facts;
  - independent public-route redundancy.
- Emit only source-backed facts. Do not invent OHLCV, amount, constituent weights, effective dates, end dates, rebalance dates, benchmark families, source timestamps, or route provenance.
- Preserve route/source truth with stable `source_route` or equivalent provenance where records are emitted.
- Route-distinct facts must remain distinguishable when values can differ.
- Honor requested `start_date` and `end_date` deterministically. If a route returns wider history, filter to the requested window.
- Reject malformed, ambiguous, unsupported, A-share stock, ETF/fund, Hong Kong stock, and non-index symbols clearly unless a route is explicitly proven to support the requested benchmark family.
- If a batch includes one invalid symbol or one repository-side schema/normalization defect, fail clearly rather than returning partial successful output.
- If a valid requested index yields no usable rows while another succeeds for the same bounded request, fail clearly unless execution can classify a source-wide route outage.
- Keep live-environment/source classifiers narrow. Network/proxy/DNS/TLS/upstream/source unavailability may skip; repository-side schema, contract, normalization, duplicate-conflict, route-signature, call-compatibility, unbounded-fetch, or date-window defects must fail.
- Update `source_catalog` and `source_capabilities` only to reflect proven public-source truth. Keep included index capabilities conservative unless full practical public-source breadth, history continuity, and redundancy are genuinely proven.
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

Write `coordination/reports/TASK-137_REPORT.md` with:

- files changed
- implementation summary by included capability
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

- The index residual capability cluster has stronger public-source proof or stricter capability/catalog truth for all included follow-up items.
- Any emitted `INDEX_DAILY_BARS` or `INDEX_CONSTITUENTS` records validate against their dataset contracts.
- Default tests remain offline-safe and live tests remain skipped by default.
- Any real-source work has gated live evidence or a truthful diagnosed SKIP/FAIL requiring Review/Controller follow-up.
- Capability metadata remains conservative and reflects only proven public-source coverage.
- `index_weight_history` remains blocked/planned unless a separate owner credential scope is opened.
- No inactive downstream module behavior is introduced.
- `coordination/reports/TASK-137_REPORT.md` is complete.
