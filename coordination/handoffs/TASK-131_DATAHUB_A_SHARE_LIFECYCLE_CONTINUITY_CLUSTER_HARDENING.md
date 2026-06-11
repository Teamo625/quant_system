# TASK-131 DataHub A-share Lifecycle and Continuity Capability Cluster Hardening

## Role

5.3 Execution Window.

## Phase

Phase 2.5-P DataHub Personal Trading Perfection Re-Review.

## Context

TASK-130 is closed after accepted Review Agent verification. It hardened local-only `DATA_QUALITY_REPORT` coverage KPI metadata, kept default tests offline-safe, and did not require live-source evidence because the task was deterministic readiness observability work.

Phase 2.5-P remains open under `coordination/PHASE_GATE.md` because `build_default_personal_trading_readiness_report()` now reports `overall_status=blocked`, `phase_closure_ready=False`, status counts `pass=4`, `warn=5`, `blocked=1`, `fail=0`, and unresolved non-pass follow-up batches. `index_weight_history` remains an owner paid-credential blocker, and optional `hk_minute_bars` remains owner-waiver-required.

Controller read DataHub readiness `follow_up_batches` after TASK-130. The first executable current-phase capability cluster is:

- batch id: `a_share__datahub_hardening__a_share__batch_01`
- disposition: `datahub_hardening`
- recommended theme: `cluster harden DataHub capabilities: a_share_listing_delisting_st_status, a_share_suspension_resumption, a_share_minute_bars, a_share_adjustment_factors, a_share_corporate_actions, a_share_valuation_history`

Included follow-up items:

- `a_share__a_share_capability_readiness__a_share_listing_delisting_st_status`
- `a_share__a_share_capability_readiness__a_share_suspension_resumption`
- `a_share__a_share_capability_readiness__a_share_minute_bars`
- `a_share__a_share_capability_readiness__a_share_adjustment_factors`
- `a_share__a_share_capability_readiness__a_share_corporate_actions`
- `a_share__a_share_capability_readiness__a_share_valuation_history`

This task stays inside DataHub. It must not reopen FeatureHub, Scanner, StrategyLab, BacktestEngine, portfolio, signal, risk, AI, notification, UI, automated trading, paid credentials, or private data.

## Objective

Harden the public-source A-share lifecycle, event, adjustment, intraday-continuity, and valuation-history cluster for practical personal quant research:

- `a_share_listing_delisting_st_status`: strengthen or truthfully constrain dated ST/*ST continuity, listing/delisting lifecycle taxonomy, terminal date truth, and source-route provenance beyond the currently proven bounded public status-history routes.
- `a_share_suspension_resumption`: strengthen or truthfully constrain suspension/resumption breadth, completed-resumption continuity, event taxonomy, cross-route deduplication, and date-window behavior beyond current Eastmoney plus Baidu coverage.
- `a_share_minute_bars`: strengthen or truthfully constrain 1-minute history, full-market breadth, retention windows, BaoStock/Eastmoney route truth, and longer intraday continuity.
- `a_share_adjustment_factors`: strengthen or truthfully constrain per-trade-date qfq/hfq factor continuity, source-route redundancy, factor semantics, and date-window behavior beyond current AKShare/Sina factor routes.
- `a_share_corporate_actions`: strengthen or truthfully constrain corporate-action taxonomy breadth beyond currently proven dividend/distribution and rights-issue families, with explicit source-backed `action_family` and route provenance.
- `a_share_valuation_history`: strengthen or truthfully constrain long-history continuity, pre-2018 coverage, overlap behavior, Baidu/Eastmoney route truth, and public-source redundancy beyond accepted near-year and 450-day proof.

Execution should add stable no-credential public-source support where feasible. If stronger public routes are not feasible, execution must tighten capability/catalog wording and tests so unresolved public-source limits are explicit and cannot be silently treated as complete.

Keep all included A-share capabilities conservative unless implementation, tests, and gated live evidence genuinely satisfy the practical public-source personal trading completeness standard.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-131_DATAHUB_A_SHARE_LIFECYCLE_CONTINUITY_CLUSTER_HARDENING.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/ROADMAP.md`
- `coordination/reports/TASK-094_REPORT.md`
- `coordination/reviews/TASK-094_REVIEW.md`
- `coordination/reports/TASK-095_REPORT.md`
- `coordination/reviews/TASK-095_REVIEW.md`
- `coordination/reports/TASK-096_REPORT.md`
- `coordination/reviews/TASK-096_REVIEW.md`
- `coordination/reports/TASK-097_REPORT.md`
- `coordination/reviews/TASK-097_REVIEW.md`
- `coordination/reports/TASK-098_REPORT.md`
- `coordination/reviews/TASK-098_REVIEW.md`
- `coordination/reports/TASK-099_REPORT.md`
- `coordination/reviews/TASK-099_REVIEW.md`
- `coordination/reports/TASK-100_REPORT.md`
- `coordination/reviews/TASK-100_REVIEW.md`
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/baostock.py`
- `quant/datahub/datasets.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_a_share_instrument_status_history_adapter.py`
- `tests/datahub/test_akshare_a_share_instrument_status_history_live.py`
- `tests/datahub/test_akshare_a_share_suspension_resumption_adapter.py`
- `tests/datahub/test_akshare_a_share_suspension_resumption_live.py`
- `tests/datahub/test_akshare_a_share_minute_bars_adapter.py`
- `tests/datahub/test_akshare_a_share_minute_bars_live.py`
- `tests/datahub/test_baostock_a_share_minute_bars_adapter.py`
- `tests/datahub/test_baostock_a_share_minute_bars_live.py`
- `tests/datahub/test_akshare_a_share_adjustment_factors_adapter.py`
- `tests/datahub/test_akshare_a_share_adjustment_factors_live.py`
- `tests/datahub/test_akshare_a_share_corporate_actions_adapter.py`
- `tests/datahub/test_akshare_a_share_corporate_actions_live.py`
- `tests/datahub/test_akshare_a_share_valuation_snapshot_adapter.py`
- `tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`

Read related A-share DataHub tests only as needed to preserve compatibility.

## Allowed Writes

Only:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/baostock.py`
- `quant/datahub/adapters/__init__.py` only if an adapter export needs a minimal compatibility update
- `quant/datahub/datasets.py` only if a minimal schema-compatible A-share source-fact clarification is unavoidable
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_a_share_instrument_status_history_adapter.py`
- `tests/datahub/test_akshare_a_share_instrument_status_history_live.py`
- `tests/datahub/test_akshare_a_share_suspension_resumption_adapter.py`
- `tests/datahub/test_akshare_a_share_suspension_resumption_live.py`
- `tests/datahub/test_akshare_a_share_minute_bars_adapter.py`
- `tests/datahub/test_akshare_a_share_minute_bars_live.py`
- `tests/datahub/test_baostock_a_share_minute_bars_adapter.py`
- `tests/datahub/test_baostock_a_share_minute_bars_live.py`
- `tests/datahub/test_akshare_a_share_adjustment_factors_adapter.py`
- `tests/datahub/test_akshare_a_share_adjustment_factors_live.py`
- `tests/datahub/test_akshare_a_share_corporate_actions_adapter.py`
- `tests/datahub/test_akshare_a_share_corporate_actions_live.py`
- `tests/datahub/test_akshare_a_share_valuation_snapshot_adapter.py`
- `tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`
- any new focused `tests/datahub/test_*a_share*.py` file needed for this handoff
- `coordination/reports/TASK-131_REPORT.md`

If a tightly related A-share test file must change, document the exact reason in the report. Do not touch unrelated DataHub domains.

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files other than `coordination/reports/TASK-131_REPORT.md`
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

Do not implement FeatureHub indicators, scanner ranking, strategy/backtest logic, portfolio/signal/risk, AI reports, notification, UI, or automated trading.

## Implementation Requirements

- Preserve accepted TASK-094 through TASK-100 behavior unless a stricter compatible behavior is needed to keep source truth explicit.
- Prefer caller-provided, bounded symbols, date windows, and route selectors. Keep `symbols=None`, empty-symbol requests, or unbounded full-table fetches as clear errors unless a route is explicitly designed and tested as a bounded catalog/list operation.
- Investigate stable no-credential public routes within repository-supported source families for:
  - dated ST/*ST, listing, delisting, inactive, and terminal lifecycle facts;
  - broader suspension/resumption event families and complete resumption pairing;
  - deeper 1-minute intraday history and cross-route minute-bar redundancy;
  - per-trade-date adjustment-factor continuity and qfq/hfq semantic clarity;
  - corporate-action families beyond dividend/distribution and rights issue;
  - longer valuation history, pre-2018 coverage, overlap/conflict handling, and independent public-route redundancy.
- Emit only source-backed facts. Do not invent lifecycle states, event dates, resumption dates, adjustment factors, corporate-action families, valuation metrics, source timestamps, or source-route values when a verified route does not provide them.
- Preserve route/source truth with `source`, `source_route` where supported by the dataset contract, route-local symbol normalization, source-backed date fields, and any available provenance fields.
- Route-distinct facts must remain distinguishable when values can differ.
- Honor `start_date` and `end_date` deterministically. If a route returns wider history, filter to the requested window.
- Reject malformed, ambiguous, unsupported, duplicate-normalized, non-A-share, ETF/fund, Hong Kong stock, and index-like symbols clearly unless a route is explicitly proven to support them for the requested A-share dataset.
- If a batch includes one invalid symbol or one repository-side schema/normalization defect, fail clearly rather than returning partial successful output.
- If a valid requested symbol yields no usable rows while another succeeds for the same bounded request, fail clearly unless execution can classify a source-wide route outage.
- Keep live-environment/source classifiers narrow. Network/proxy/DNS/TLS/upstream/source unavailability may skip; repository-side schema, contract, normalization, duplicate-conflict, route-signature, call-compatibility, unbounded-fetch, or date-window defects must fail.
- Update `source_catalog` and `source_capabilities` only to reflect proven public-source truth. Keep all six included A-share capabilities conservative unless full practical public-source breadth, history continuity, and redundancy are genuinely proven.
- If no stable broader no-credential route is feasible for a capability, record attempted route names and observed limitations in the report, add or preserve tests that prevent overclaiming, and leave capability truth conservative.

## Tests

Required offline/default tests:

- `python3 -m unittest tests.datahub.test_source_capabilities`
- `python3 -m unittest tests.datahub.test_source_catalog`
- `python3 -m unittest tests.datahub.test_akshare_a_share_instrument_status_history_adapter`
- `python3 -m unittest tests.datahub.test_akshare_a_share_suspension_resumption_adapter`
- `python3 -m unittest tests.datahub.test_akshare_a_share_minute_bars_adapter`
- `python3 -m unittest tests.datahub.test_baostock_a_share_minute_bars_adapter`
- `python3 -m unittest tests.datahub.test_akshare_a_share_adjustment_factors_adapter`
- `python3 -m unittest tests.datahub.test_akshare_a_share_corporate_actions_adapter`
- `python3 -m unittest tests.datahub.test_akshare_a_share_valuation_snapshot_adapter`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_a_share_instrument_status_history_live`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_a_share_suspension_resumption_live`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_a_share_minute_bars_live`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_baostock_a_share_minute_bars_live`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_a_share_adjustment_factors_live`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_a_share_corporate_actions_live`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_a_share_valuation_snapshot_live`
- focused A-share tests for every changed adapter/test file

Live smoke requirement:

- If any real-source instrument-status path is added or materially changed, run `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_a_share_instrument_status_history_live`.
- If any real-source suspension/resumption path is added or materially changed, run `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_a_share_suspension_resumption_live`.
- If any real-source AKShare minute-bar path is added or materially changed, run `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_a_share_minute_bars_live`.
- If any real-source BaoStock minute-bar path is added or materially changed, run `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_baostock_a_share_minute_bars_live`.
- If any real-source adjustment-factor path is added or materially changed, run `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_a_share_adjustment_factors_live`.
- If any real-source corporate-action path is added or materially changed, run `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_a_share_corporate_actions_live`.
- If any real-source valuation path is added or materially changed, run `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_a_share_valuation_snapshot_live`.
- Live smokes must be explicitly gated and skipped by default.
- Live-enabled smokes should validate at least one newly supported or materially changed route/capability path when upstream routes are available.
- Report PASS, SKIP, or FAIL truthfully with root-cause evidence. If a live smoke skips because of network, proxy, DNS, TLS, upstream, or public-source availability, diagnose and modify allowed code/tests/report where feasible instead of only documenting the skip.

## Completion Report

Write `coordination/reports/TASK-131_REPORT.md` with:

- files changed
- implementation summary
- selected readiness batch id and included follow-up ids
- A-share route/source-family investigation result for every included capability
- supported symbol classes, date-window behavior, source-route truth, and deduplication behavior
- lifecycle/status source truth and known limitations
- suspension/resumption event taxonomy and known limitations
- minute-bar retention/history/source truth and known limitations
- adjustment-factor semantics/source truth and known limitations
- corporate-action taxonomy/source truth and known limitations
- valuation-history source truth, overlap behavior, and known limitations
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence for each materially changed real-source path
- whether any of the six capability truths changed
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

The task is complete when:

- The A-share lifecycle/continuity cluster has stronger public-source proof or stricter capability/catalog truth for all included follow-up items.
- Any emitted `INSTRUMENT_STATUS_HISTORY`, `SUSPENSION_RESUMPTION_EVENTS`, `MINUTE_BARS`, `ADJUSTMENT_FACTORS`, `CORPORATE_ACTIONS`, or `VALUATION_SNAPSHOT` records validate against their dataset contracts.
- Default tests remain offline-safe and live tests remain skipped by default.
- Any real-source work has gated live evidence or a truthful diagnosed SKIP/FAIL requiring Review/Controller follow-up.
- Capability metadata remains conservative and reflects only proven public-source coverage.
- No inactive downstream module behavior is introduced.
