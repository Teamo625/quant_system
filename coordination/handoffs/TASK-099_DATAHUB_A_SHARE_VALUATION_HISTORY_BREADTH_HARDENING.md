# TASK-099 DataHub A-share Valuation History Breadth Hardening

## Role

5.3 Execution Window.

## Context

TASK-098 is closed after accepted Review Agent verification. It preserved the shared `DatasetName.CORPORATE_ACTIONS` taxonomy contract, fixed HK corporate-actions normalization to satisfy the shared `action_family` / `source_route` requirements, kept default tests offline-safe, and provided HK live-enabled PASS evidence for the rework.

Phase 2.5-P remains open under the Personal Trading Perfection Standard. The accepted TASK-093 readiness gate still reports non-pass follow-up items, and `index_weight_history` remains an owner credential blocker that must not be promoted unless paid Tushare scope is reopened and a future credentialed live smoke records a real PASS.

The next unclosed executable `datahub_hardening` item in the TASK-093 structured queue is:

- `a_share__a_share_capability_readiness__a_share_valuation_history`
- theme: expand valuation history breadth beyond bounded near-year public coverage
- reason: public AKShare currently supports caller-provided multi-symbol bounded near-year valuation date windows, but longer history breadth and standardized pagination beyond the bounded route remain incomplete

## Objective

Harden A-share `DatasetName.VALUATION_SNAPSHOT` valuation-history source coverage beyond the current bounded near-year path where stable no-credential public routes expose source truth.

Execution should investigate and implement the smallest stable repository-side improvement that expands practical valuation-history breadth, date continuity, or route resilience without inventing metrics or adding full-market crawling. If no stable no-credential public route can prove broader history than the current path, preserve the implementation, strengthen tests or metadata where useful, record route evidence truthfully, and keep capability truth conservative.

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
- `coordination/reports/TASK-099_REPORT.md`

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files except `coordination/reports/TASK-099_REPORT.md`
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

- Review the existing A-share valuation schema, adapter, source catalog, capability metadata, and TASK-075 behavior before editing.
- Preserve existing caller-provided multi-symbol bounded request behavior.
- Keep `symbols=None` or empty symbol lists as clear errors; do not silently fetch full-market valuation tables.
- Validate and normalize A-share symbols consistently with the existing valuation adapter.
- Reject HK, ETF/fund, index-like, malformed, ambiguous, missing, and unsupported symbols clearly.
- Use only stable no-credential public routes. Do not add Tushare, paid endpoints, credentialed APIs, browser/session scraping, or private data.
- Expand history breadth only when the source directly exposes dated valuation facts. Do not infer historical PE/PB/PS/market-cap values from prices, financial statements, or adjustment factors.
- Preserve source-truth optionality for fields not reliably exposed by public routes. Do not fabricate valuation metrics.
- Keep normalized records compatible with `DatasetRegistry.validate_record(DatasetName.VALUATION_SNAPSHOT, ...)`.
- Preserve deterministic de-duplication by at least `(symbol, trade_date, source, source_route)` and any route-local metric identity needed to detect conflicting duplicates.
- Preserve deterministic sorting by symbol, trade date, and source route.
- If multiple public routes overlap, merge only source-compatible facts. Conflicting duplicate source facts must remain hard failures with actionable messages.
- Keep route-name-bearing AKShare argument/signature compatibility errors as hard failures, following the existing DataHub live-failure classification policy.
- Update `source_catalog` and `source_capabilities` only to reflect proven public-source truth. Keep `a_share_valuation_history` conservative unless implementation and live evidence prove full personal-trading breadth/history completeness.
- If route investigation finds no stable broader no-credential path, the report must include the attempted route names, observed limitation, and why no capability promotion is justified.

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
- The live-enabled smoke should validate at least two A-share symbols and at least one source-backed dated valuation record if the upstream source is available.
- Report PASS, SKIP, or FAIL truthfully with root-cause evidence. If the live smoke skips because of network, proxy, DNS, TLS, upstream, or public-source availability, diagnose and modify allowed code/tests/report where feasible instead of only documenting the skip.

## Completion Report

Write `coordination/reports/TASK-099_REPORT.md` with:

- files changed
- tests run
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence, or explicit `SKIP` only if no real-source adapter path was added or materially changed
- valuation-history route investigation result by route/source family
- source route coverage and known valuation-history limitations
- whether `a_share_valuation_history` capability truth changed
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

The task is complete when:

- A-share valuation-history breadth is improved where stable no-credential public routes expose source truth, or a truthful route investigation documents why no safe expansion is currently feasible.
- Normalized records validate against `DatasetName.VALUATION_SNAPSHOT`.
- Default tests remain offline-safe and live tests remain skipped by default.
- Any real-source work has gated live evidence or a truthful diagnosed SKIP/FAIL requiring Review/Controller follow-up.
- Capability metadata remains conservative and reflects only proven public-source coverage.
- No inactive downstream module behavior is introduced.
