# TASK-100 DataHub A-share Valuation Long-History Continuity Hardening

## Role

5.3 Execution Window.

## Context

TASK-099 is closed after accepted Review Agent verification. It expanded A-share `DatasetName.VALUATION_SNAPSHOT` valuation-history breadth by selecting Baidu valuation periods based on the requested start date, proved live-enabled PASS evidence for a 450-day two-symbol request, and kept `a_share_valuation_history` conservative at `partial`.

Phase 2.5-P remains open under the Personal Trading Perfection Standard. TASK-099 closed the bounded near-year breadth gap, but its accepted report/review left two unresolved valuation-history risks:

- continuity and payload-shape stability for the longest Baidu selectors (`近十年` / `全部`) are not yet proven
- no stable no-credential second public source for dated A-share valuation history has been validated

`index_weight_history` remains an owner credential blocker and must not be promoted unless paid Tushare scope is reopened and a future credentialed live smoke records a real PASS.

## Objective

Harden A-share `DatasetName.VALUATION_SNAPSHOT` long-history confidence by validating or improving the longest no-credential public valuation-history paths now exposed by TASK-099, and by investigating whether a stable second no-credential dated valuation-history route can provide redundancy.

Execution should implement the smallest stable repository-side improvement that strengthens continuity validation, route selection, conflict handling, or truthful capability metadata for long-history valuation use. If no stable second no-credential dated source exists, preserve implementation truthfully, add regression coverage or metadata/reporting that prevents overclaiming, and keep `a_share_valuation_history` conservative.

This task must not implement FeatureHub valuation features, scanner ranking, strategy/backtest behavior, portfolio/signal/risk logic, AI reports, notifications, UI, or automated trading.

## Allowed Writes

Only:

- `quant/datahub/datasets.py`
- `quant/datahub/source_catalog.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/adapters/akshare.py`
- `tests/datahub/test_datasets.py`
- `tests/datahub/test_source_catalog.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_akshare_a_share_valuation_snapshot_adapter.py`
- `tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`
- `coordination/reports/TASK-100_REPORT.md`

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files except `coordination/reports/TASK-100_REPORT.md`
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

- Read AGENTS.md first, then this handoff.
- Review TASK-075 and TASK-099 valuation behavior before editing.
- Preserve existing caller-provided symbol requirements; `symbols=None` or empty symbol lists must remain clear errors.
- Preserve existing A-share symbol validation and clear rejection of HK, ETF/fund, index-like, malformed, ambiguous, missing, and unsupported symbols.
- Preserve TASK-099 period-selection behavior and add or strengthen deterministic coverage for long-window selector routing (`近三年`, `近五年`, `近十年`, `全部`) where feasible.
- Validate long-history normalized records against `DatasetRegistry.validate_record(DatasetName.VALUATION_SNAPSHOT, ...)`.
- Do not infer historical PE/PB/PS/market-cap values from prices, financial statements, adjustment factors, or latest-only routes.
- Use only stable no-credential public routes. Do not add Tushare, paid endpoints, credentialed APIs, browser/session scraping, or private data.
- If a second dated valuation-history route is added, keep `source_route` distinct, preserve source-truth optionality, and fail on conflicting duplicate source facts rather than silently merging incompatible metrics.
- Preserve deterministic de-duplication by at least `(symbol, trade_date, source, source_route)` and any route-local metric identity needed to detect conflicting duplicates.
- Preserve deterministic sorting by symbol, trade date, and source route.
- Keep route-name-bearing AKShare argument/signature compatibility errors as hard failures, following the existing DataHub live-failure classification policy.
- Update `source_catalog` and `source_capabilities` only to reflect proven public-source truth. Keep `a_share_valuation_history` conservative unless implementation and live evidence prove full personal-trading breadth/history completeness.
- If no stable second source is feasible, the report must include attempted route names, observed limitation, and why no capability promotion is justified.

## Tests

Required offline/default tests:

- `python3 -m unittest tests/datahub/test_datasets.py`
- `python3 -m unittest tests/datahub/test_source_catalog.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`
- `python3 -m unittest tests/datahub/test_akshare_a_share_valuation_snapshot_adapter.py`
- `python3 -m unittest -v tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`

Live smoke requirement:

- If any real-source valuation adapter path is added or materially changed, run `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`.
- The live smoke must be explicitly gated and skipped by default.
- The live-enabled smoke should validate at least two A-share symbols and at least one source-backed dated valuation record from a long-history selector if the upstream source is available.
- Report PASS, SKIP, or FAIL truthfully with root-cause evidence. If the live smoke skips because of network, proxy, DNS, TLS, upstream, or public-source availability, diagnose and modify allowed code/tests/report where feasible instead of only documenting the skip.

## Completion Report

Write `coordination/reports/TASK-100_REPORT.md` with:

- files changed
- tests run
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence, or explicit `SKIP` only if no real-source adapter path was added or materially changed
- long-history selector continuity validation result by selector/source route
- second-source investigation result by route/source family
- source route coverage and known valuation-history limitations
- whether `a_share_valuation_history` capability truth changed
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

The task is complete when:

- Long-history valuation selector behavior is regression-protected or improved where stable no-credential public routes expose source truth.
- Any second-source dated valuation route is either implemented with validated records and gated live evidence, or truthfully rejected as unavailable/unstable with evidence.
- Normalized records validate against `DatasetName.VALUATION_SNAPSHOT`.
- Default tests remain offline-safe and live tests remain skipped by default.
- Any real-source work has gated live evidence or a truthful diagnosed SKIP/FAIL requiring Review/Controller follow-up.
- Capability metadata remains conservative and reflects only proven public-source coverage.
- No inactive downstream module behavior is introduced.
