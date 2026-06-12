# TASK-132 DataHub A-share Flow, Liquidity, Market-Constraint, and Financial-Statement Capability Cluster Hardening

## Role

5.3 Execution Window.

## Phase

Phase 2.5-P DataHub Personal Trading Perfection Re-Review.

## Context

TASK-131 is closed after accepted Review Agent verification. The original A-share lifecycle/continuity capability cluster was accepted after a focused source-catalog truth rework removed incorrect BaoStock attribution from the AKShare source-family notes. Default tests remained offline-safe, and the live-enabled result is accepted as PASS based on the prior TASK-131 material real-source evidence plus the focused offline catalog regression.

Phase 2.5-P remains open under `coordination/PHASE_GATE.md` because `build_default_personal_trading_readiness_report()` still reports `overall_status=blocked` and `phase_closure_ready=False`. `index_weight_history` remains an owner paid-credential blocker, and optional `hk_minute_bars` remains owner-waiver-required.

Controller read DataHub readiness `follow_up_batches` after TASK-131. TASK-131 covered:

- `a_share__datahub_hardening__a_share__batch_01`

The next executable current-phase capability cluster is:

- batch id: `a_share__datahub_hardening__a_share__batch_02`
- disposition: `datahub_hardening`
- recommended theme: `cluster harden DataHub capabilities: a_share_capital_flow, a_share_northbound_flow, a_share_turnover_liquidity, a_share_limit_up_down, a_share_margin_financing_and_lending, a_share_financial_statements`

Included follow-up items:

- `a_share__a_share_capability_readiness__a_share_capital_flow`
- `a_share__a_share_capability_readiness__a_share_northbound_flow`
- `a_share__a_share_capability_readiness__a_share_turnover_liquidity`
- `a_share__a_share_capability_readiness__a_share_limit_up_down`
- `a_share__a_share_capability_readiness__a_share_margin_financing_and_lending`
- `a_share__a_share_capability_readiness__a_share_financial_statements`

This task stays inside DataHub. It must not reopen FeatureHub, Scanner, StrategyLab, BacktestEngine, portfolio, signal, risk, AI, notification, UI, automated trading, paid credentials, or private data.

## Objective

Harden the public-source A-share flow, liquidity, market-constraint, margin-financing, and financial-statement cluster for practical personal quant research:

- `a_share_capital_flow`: strengthen or truthfully constrain dated symbol-level and market/sector capital-flow breadth, route-source truth, longer continuity, and redundancy beyond the current route-distinct capital-flow facts.
- `a_share_northbound_flow`: strengthen or truthfully constrain northbound net-buy/holding semantics, market/symbol/date granularity, route-source truth, and redundancy beyond current first-class `NORTHBOUND_FLOW_SNAPSHOT` coverage.
- `a_share_turnover_liquidity`: strengthen or truthfully constrain turnover, volume, traded amount, float/share-base assumptions, liquidity semantics, and public-source redundancy beyond current daily-bar-derived source facts.
- `a_share_limit_up_down`: strengthen or truthfully constrain limit-up/down event breadth, history, board/taxonomy coverage, route-source truth, date-window behavior, and classifier boundaries beyond current Eastmoney route coverage.
- `a_share_margin_financing_and_lending`: strengthen or truthfully constrain SSE/SZSE/BSE/BJ margin-financing and securities-lending breadth, symbol/date continuity, exchange summary reconciliation, and route-source truth beyond current bounded SSE/SZSE detail proof.
- `a_share_financial_statements`: strengthen or truthfully constrain statement-family breadth, report-period continuity, metric/source-route truth, long-history support, and public-source redundancy beyond current `stock_financial_report_sina` proof.

Execution should add stable no-credential public-source support where feasible. If stronger public routes are not feasible, execution must tighten capability/catalog wording and tests so unresolved public-source limits are explicit and cannot be silently treated as complete.

Keep all included A-share capabilities conservative unless implementation, tests, and gated live evidence genuinely satisfy the practical public-source personal trading completeness standard.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-132_DATAHUB_A_SHARE_FLOW_LIQUIDITY_FINANCIAL_CLUSTER_HARDENING.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/ROADMAP.md`
- `coordination/reports/TASK-101_REPORT.md`
- `coordination/reviews/TASK-101_REVIEW.md`
- `coordination/reports/TASK-102_REPORT.md`
- `coordination/reviews/TASK-102_REVIEW.md`
- `coordination/reports/TASK-103_REPORT.md`
- `coordination/reviews/TASK-103_REVIEW.md`
- `coordination/reports/TASK-104_REPORT.md`
- `coordination/reviews/TASK-104_REVIEW.md`
- `coordination/reports/TASK-105_REPORT.md`
- `coordination/reviews/TASK-105_REVIEW.md`
- `coordination/reports/TASK-106_REPORT.md`
- `coordination/reviews/TASK-106_REVIEW.md`
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/datasets.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_a_share_capital_flow_snapshot_adapter.py`
- `tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py`
- `tests/datahub/test_akshare_a_share_northbound_flow_adapter.py`
- `tests/datahub/test_akshare_a_share_northbound_flow_live.py`
- `tests/datahub/test_akshare_a_share_turnover_liquidity_adapter.py`
- `tests/datahub/test_akshare_a_share_turnover_liquidity_live.py`
- `tests/datahub/test_akshare_a_share_limit_up_down_adapter.py`
- `tests/datahub/test_akshare_a_share_limit_up_down_live.py`
- `tests/datahub/test_akshare_a_share_margin_financing_lending_adapter.py`
- `tests/datahub/test_akshare_a_share_margin_financing_lending_live.py`
- `tests/datahub/test_akshare_a_share_financial_data_adapter.py`
- `tests/datahub/test_akshare_a_share_financial_data_live.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`

Read related A-share DataHub tests only as needed to preserve compatibility.

## Allowed Writes

Only:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py` only if an adapter export needs a minimal compatibility update
- `quant/datahub/datasets.py` only if a minimal schema-compatible A-share source-fact clarification is unavoidable
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_a_share_capital_flow_snapshot_adapter.py`
- `tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py`
- `tests/datahub/test_akshare_a_share_northbound_flow_adapter.py`
- `tests/datahub/test_akshare_a_share_northbound_flow_live.py`
- `tests/datahub/test_akshare_a_share_turnover_liquidity_adapter.py`
- `tests/datahub/test_akshare_a_share_turnover_liquidity_live.py`
- `tests/datahub/test_akshare_a_share_limit_up_down_adapter.py`
- `tests/datahub/test_akshare_a_share_limit_up_down_live.py`
- `tests/datahub/test_akshare_a_share_margin_financing_lending_adapter.py`
- `tests/datahub/test_akshare_a_share_margin_financing_lending_live.py`
- `tests/datahub/test_akshare_a_share_financial_data_adapter.py`
- `tests/datahub/test_akshare_a_share_financial_data_live.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`
- any new focused `tests/datahub/test_*a_share*.py` file needed for this handoff
- `coordination/reports/TASK-132_REPORT.md`

If a tightly related A-share test file must change, document the exact reason in the report. Do not touch unrelated DataHub domains.

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files other than `coordination/reports/TASK-132_REPORT.md`
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

- Preserve accepted TASK-101 through TASK-106 behavior unless a stricter compatible behavior is needed to keep source truth explicit.
- Prefer caller-provided, bounded symbols, date windows, market/exchange selectors, and route selectors. Keep `symbols=None`, empty-symbol requests, or unbounded full-table fetches as clear errors unless a route is explicitly designed and tested as a bounded catalog/list operation.
- Investigate stable no-credential public routes within repository-supported source families for:
  - richer dated capital-flow history and route redundancy;
  - northbound market/symbol/date facts, holding semantics, and source-route provenance;
  - turnover/liquidity semantics beyond raw volume/amount where source-backed;
  - broader limit-up/down event taxonomy and history;
  - margin financing/lending exchange breadth, symbol continuity, and summary/detail reconciliation;
  - financial-statement family breadth, report-period continuity, and second-route redundancy.
- Emit only source-backed facts. Do not invent flow amounts, holding values, turnover rates, liquidity fields, limit-event states, margin quantities, financial metrics, source timestamps, or source-route values when a verified route does not provide them.
- Preserve route/source truth with `source`, `source_route` where supported by the dataset contract, route-local symbol normalization, source-backed date fields, and any available provenance fields.
- Route-distinct facts must remain distinguishable when values can differ.
- Honor `start_date`, `end_date`, `report_period`, and exchange/market selectors deterministically. If a route returns wider history, filter to the requested window.
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
- `python3 -m unittest tests.datahub.test_akshare_a_share_capital_flow_snapshot_adapter`
- `python3 -m unittest tests.datahub.test_akshare_a_share_northbound_flow_adapter`
- `python3 -m unittest tests.datahub.test_akshare_a_share_turnover_liquidity_adapter`
- `python3 -m unittest tests.datahub.test_akshare_a_share_limit_up_down_adapter`
- `python3 -m unittest tests.datahub.test_akshare_a_share_margin_financing_lending_adapter`
- `python3 -m unittest tests.datahub.test_akshare_a_share_financial_data_adapter`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_a_share_capital_flow_snapshot_live`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_a_share_northbound_flow_live`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_a_share_turnover_liquidity_live`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_a_share_limit_up_down_live`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_a_share_margin_financing_lending_live`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_a_share_financial_data_live`
- focused A-share tests for every changed adapter/test file

Live smoke requirement:

- If any real-source capital-flow path is added or materially changed, run `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_a_share_capital_flow_snapshot_live`.
- If any real-source northbound-flow path is added or materially changed, run `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_a_share_northbound_flow_live`.
- If any real-source turnover/liquidity path is added or materially changed, run `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_a_share_turnover_liquidity_live`.
- If any real-source limit-up/down path is added or materially changed, run `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_a_share_limit_up_down_live`.
- If any real-source margin-financing/lending path is added or materially changed, run `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_a_share_margin_financing_lending_live`.
- If any real-source financial-statement path is added or materially changed, run `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_a_share_financial_data_live`.
- Live smokes must be explicitly gated and skipped by default.
- Live-enabled smokes should validate at least one newly supported or materially changed route/capability path when upstream routes are available.
- Report PASS, SKIP, or FAIL truthfully with root-cause evidence. If a live smoke skips because of network, proxy, DNS, TLS, upstream, or public-source availability, diagnose and modify allowed code/tests/report where feasible instead of only documenting the skip.

## Completion Report

Write `coordination/reports/TASK-132_REPORT.md` with:

- files changed
- implementation summary
- selected readiness batch id and included follow-up ids
- A-share route/source-family investigation result for every included capability
- supported symbol classes, date-window behavior, source-route truth, and deduplication behavior
- capital-flow source truth and known limitations
- northbound-flow source truth and known limitations
- turnover/liquidity semantics and known limitations
- limit-up/down event taxonomy/history and known limitations
- margin-financing/lending exchange/source truth and known limitations
- financial-statement source truth, report-period behavior, and known limitations
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence for materially changed real-source paths
- deviations from the handoff
- risks or follow-up tasks
