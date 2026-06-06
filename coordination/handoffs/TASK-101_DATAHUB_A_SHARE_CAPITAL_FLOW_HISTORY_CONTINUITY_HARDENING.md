# TASK-101 DataHub A-share Capital-Flow History Continuity Hardening

## Role

5.3 Execution Window.

## Context

TASK-100 is closed after accepted Review Agent verification. It strengthened A-share `DatasetName.VALUATION_SNAPSHOT` long-history valuation behavior, preserved Baidu/Eastmoney route-distinct overlap/gap source truth, classified Baidu upstream non-JSON responses truthfully as route unavailable, kept default tests offline-safe, and recorded live-enabled PASS evidence. `a_share_valuation_history` remains conservative at `partial`.

Phase 2.5-P remains open under the Personal Trading Perfection Standard. The accepted TASK-093 readiness gate still reports non-pass follow-up items, and `index_weight_history` remains an owner credential blocker that must not be promoted unless paid Tushare scope is reopened and a future credentialed live smoke records a real PASS.

The next executable `datahub_hardening` item from the TASK-093 structured queue is:

- `a_share__a_share_capability_readiness__a_share_capital_flow`
- theme: expand capital-flow history continuity beyond bounded public routes and latest-snapshot fallback coverage
- reason: public AKShare supports caller-provided multi-symbol capital-flow batches with deterministic bounded date-window filtering, but broader historical continuity and latest-only fallback dependence remain incomplete

## Objective

Harden A-share `DatasetName.CAPITAL_FLOW_SNAPSHOT` capital-flow history continuity and route truthfulness beyond the current bounded public route behavior.

Execution should investigate stable no-credential public AKShare routes for broader dated symbol-level capital-flow history, improve adapter/test behavior where source truth is available, and keep capability metadata conservative where public routes remain latest-only, bounded, unstable, or incomplete.

This task must not implement FeatureHub money-flow features, scanner ranking, strategy/backtest behavior, portfolio/signal/risk logic, AI reports, notifications, UI, or automated trading.

## Allowed Writes

Only:

- `quant/datahub/datasets.py`
- `quant/datahub/source_catalog.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/adapters/akshare.py`
- `tests/datahub/test_datasets.py`
- `tests/datahub/test_source_catalog.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_akshare_a_share_capital_flow_snapshot_adapter.py`
- `tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py`
- `coordination/reports/TASK-101_REPORT.md`

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files except `coordination/reports/TASK-101_REPORT.md`
- `coordination/reviews/**`
- `coordination/integrations/**`
- unrelated DataHub adapters or tests
- `quant/features/`
- `quant/scanner/`
- `quant/strategies/`
- `quant/backtest/`
- `quant/portfolio/`
- `quant/notification/`
- `quant/ai/`
- `quant/ui/`

Do not use credentials, cookies, tokens, browser session state, paid APIs, or private account data.

## Implementation Requirements

- Read `AGENTS.md` first, then this handoff.
- Review existing TASK-076 A-share capital-flow behavior before editing.
- Preserve caller-provided symbol behavior. `symbols=None` or empty symbol lists must remain clear errors; do not silently fetch full-market tables.
- Preserve strict A-share symbol validation and clear rejection of HK, ETF/fund, index-like, malformed, ambiguous, missing, and unsupported symbols.
- Use only stable no-credential public routes. Do not add Tushare, paid endpoints, credentialed APIs, browser/session scraping, private data, or unbounded crawling.
- Investigate whether the local AKShare dependency exposes stable dated symbol-level capital-flow routes beyond the currently implemented bounded history/latest fallback behavior.
- Expand history continuity only when a route directly exposes dated capital-flow source facts. Do not infer capital-flow metrics from prices, turnover, financial statements, or snapshots.
- Preserve source-truth optionality for fields that public routes do not reliably expose. Do not fabricate `net_inflow`, `main_net_inflow`, `small_order_net_inflow`, `northbound_net_buy`, turnover, or ratio fields.
- Preserve deterministic record identity by at least `(symbol, trade_date, source, source_route)` when multiple public routes can overlap.
- If multiple public routes overlap, preserve compatible route-distinct source facts or detect conflicting duplicate source facts deterministically. Do not silently prefer a later route when metric values disagree.
- Preserve deterministic sorting by symbol, trade date, and source route.
- Keep route-name-bearing AKShare argument/signature compatibility errors as hard failures following the existing DataHub live-failure classification policy.
- Keep live-environment/source classifiers narrow. Network/proxy/DNS/TLS/upstream/source unavailability may skip; repository-side schema, contract, normalization, duplicate-conflict, or route-signature defects must fail.
- Update `source_catalog` and `source_capabilities` only to reflect proven public-source truth. Keep `a_share_capital_flow` conservative unless implementation and live evidence prove full practical history continuity and route breadth.
- Do not add the dedicated northbound-flow contract profile in this task; `a_share_northbound_flow` is a separate queue item unless a minimal compatibility adjustment is strictly required to preserve existing `CAPITAL_FLOW_SNAPSHOT` behavior.
- If no stable broader no-credential route is feasible, preserve the implementation, add regression coverage or metadata/reporting that prevents overclaiming, and record attempted route names plus observed limitations in the report.

## Tests

Required offline/default tests:

- `python3 -m unittest tests/datahub/test_datasets.py`
- `python3 -m unittest tests/datahub/test_source_catalog.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`
- `python3 -m unittest tests/datahub/test_akshare_a_share_capital_flow_snapshot_adapter.py`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py`

Live smoke requirement:

- If any real-source capital-flow adapter path is added or materially changed, run `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py`.
- The live smoke must be explicitly gated and skipped by default.
- The live-enabled smoke should validate at least two A-share symbols and at least one source-backed dated capital-flow record if the upstream source is available.
- Report PASS, SKIP, or FAIL truthfully with root-cause evidence. If the live smoke skips because of network, proxy, DNS, TLS, upstream, or public-source availability, diagnose and modify allowed code/tests/report where feasible instead of only documenting the skip.

## Completion Report

Write `coordination/reports/TASK-101_REPORT.md` with:

- files changed
- tests run
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence, or explicit `SKIP` only if no real-source adapter path was added or materially changed
- capital-flow route investigation result by route/source family
- source route coverage, overlap/conflict policy, and known capital-flow history limitations
- whether `a_share_capital_flow` capability truth changed
- confirmation that `a_share_northbound_flow` was not promoted or changed unless explicitly justified by a minimal compatibility need
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

The task is complete when:

- A-share capital-flow history continuity is improved where stable no-credential public routes expose source truth, or a truthful route investigation documents why no safe expansion is currently feasible.
- Normalized records validate against `DatasetName.CAPITAL_FLOW_SNAPSHOT`.
- Default tests remain offline-safe and live tests remain skipped by default.
- Any real-source work has gated live evidence or a truthful diagnosed SKIP/FAIL requiring Review/Controller follow-up.
- Capability metadata remains conservative and reflects only proven public-source coverage.
- No inactive downstream module behavior is introduced.
