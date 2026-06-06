# TASK-103 DataHub A-share Turnover/Liquidity Canonical Field Hardening

## Role

5.3 Execution Window.

## Context

TASK-102 is closed after accepted Review Agent verification. It made A-share northbound-flow semantics first-class through the dedicated `DatasetName.NORTHBOUND_FLOW_SNAPSHOT` profile, kept `a_share_northbound_flow` conservative, recorded live-enabled PASS evidence, and then completed the focused live-classifier rework so AKShare route-signature/call-compatibility defects fail instead of being downgraded to environment `SKIP`.

Phase 2.5-P remains open under the Personal Trading Perfection Standard. The accepted TASK-093 readiness gate still reports non-pass follow-up items, and `index_weight_history` remains an owner credential blocker that must not be promoted unless paid Tushare scope is reopened and a future credentialed live smoke records a real PASS.

The next unclosed executable `datahub_hardening` item from the TASK-093 structured queue is:

- `a_share__a_share_capability_readiness__a_share_turnover_liquidity`
- theme: turnover and liquidity canonical field set
- reason: liquidity fields exist across daily-bar and capital-flow source facts, but they are not yet normalized into one explicit DataHub contract/profile slice

## Objective

Make A-share turnover/liquidity semantics explicit and test-covered in DataHub without implementing downstream liquidity factors.

Execution should define a canonical DataHub contract/profile surface for source-backed A-share turnover/liquidity facts, reconcile existing `DAILY_BARS` and `CAPITAL_FLOW_SNAPSHOT` fields where appropriate, and update source capability/catalog truth conservatively. If a dedicated dataset is added, it must preserve compatibility with existing daily-bar and capital-flow records rather than replacing them.

This task must not implement FeatureHub liquidity indicators, scanner ranking, strategy/backtest behavior, portfolio/signal/risk logic, AI reports, notifications, UI, or automated trading.

## Allowed Writes

Only:

- `quant/datahub/datasets.py`
- `quant/datahub/source_catalog.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/adapters/akshare.py`
- `tests/datahub/test_datasets.py`
- `tests/datahub/test_source_catalog.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_akshare_adapter.py`
- `tests/datahub/test_akshare_a_share_capital_flow_snapshot_adapter.py`
- `tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py`
- any new focused `tests/datahub/test_akshare_a_share_turnover_liquidity*.py` file needed for this handoff
- `coordination/reports/TASK-103_REPORT.md`

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files except `coordination/reports/TASK-103_REPORT.md`
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

Do not use credentials, cookies, tokens, browser session state, paid APIs, private account data, or unbounded crawling.

## Implementation Requirements

- Read `AGENTS.md` first, then this handoff.
- Review existing A-share daily-bar and capital-flow turnover behavior before editing, especially `volume`, `amount`, and `turnover_rate` handling.
- Use only stable no-credential public routes. Do not add Tushare, paid endpoints, credentialed APIs, browser/session scraping, private data, or unbounded full-market collection.
- Define canonical source-fact semantics for A-share turnover/liquidity fields that are actually source-backed, such as trade date, symbol, volume, amount, turnover rate, source, source route, and any clearly available liquidity metric.
- Do not fabricate turnover rate, free-float turnover, market value, float shares, VWAP, liquidity scores, spread estimates, or derived factors unless the source route directly exposes the fact and the field semantics are documented in schema/tests.
- Preserve existing `DatasetName.DAILY_BARS` and `DatasetName.CAPITAL_FLOW_SNAPSHOT` compatibility. Existing consumers and tests must continue to validate records with their current fields.
- If adding a dedicated dataset/profile, use deterministic record identity by at least symbol, trade date, source, source route, and metric granularity. Avoid silently merging route-distinct facts when values can differ.
- Preserve strict A-share symbol validation and bounded caller-provided requests. `symbols=None` or empty symbol lists must remain clear errors for symbol-scoped paths; do not silently fetch full-market tables.
- Preserve source-truth optionality for fields that public routes do not reliably expose.
- Keep route-name-bearing AKShare argument/signature compatibility errors as hard failures following existing DataHub live-failure classification policy.
- Keep live-environment/source classifiers narrow. Network/proxy/DNS/TLS/upstream/source unavailability may skip; repository-side schema, contract, normalization, duplicate-conflict, or route-signature defects must fail.
- Update `source_catalog` and `source_capabilities` only to reflect proven public-source truth. Keep `a_share_turnover_liquidity` conservative unless implementation and live evidence prove full practical public-source breadth and continuity.
- If no stable broader no-credential route is feasible, preserve implementation behavior, add contract/test/reporting clarity that prevents overclaiming, and record attempted route names plus observed limitations in the report.

## Tests

Required offline/default tests:

- `python3 -m unittest tests/datahub/test_datasets.py`
- `python3 -m unittest tests/datahub/test_source_catalog.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`
- `python3 -m unittest tests/datahub/test_akshare_adapter.py`
- `python3 -m unittest tests/datahub/test_akshare_a_share_capital_flow_snapshot_adapter.py`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py`

If a new focused turnover/liquidity adapter/live test file is added, also run its offline/default path.

Live smoke requirement:

- If any real-source turnover/liquidity adapter path is added or materially changed, run the relevant gated live smoke with `QUANT_SYSTEM_LIVE_TESTS=1`.
- The live smoke must be explicitly gated and skipped by default.
- The live-enabled smoke should validate at least two A-share symbols and at least one source-backed dated turnover/liquidity record if the upstream source is available.
- Report PASS, SKIP, or FAIL truthfully with root-cause evidence. If the live smoke skips because of network, proxy, DNS, TLS, upstream, or public-source availability, diagnose and modify allowed code/tests/report where feasible instead of only documenting the skip.

## Completion Report

Write `coordination/reports/TASK-103_REPORT.md` with:

- files changed
- tests run
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence, or explicit `SKIP` only if no real-source adapter path was added or materially changed
- turnover/liquidity contract/profile fields, granularity, identity, and known limitations
- route/source-family investigation result for turnover/liquidity source facts
- whether `a_share_turnover_liquidity` capability truth changed
- confirmation that existing daily-bar and capital-flow compatibility was preserved unless explicitly justified
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

The task is complete when:

- A-share turnover/liquidity semantics are explicit in DataHub through a dedicated schema/profile or equivalent first-class contract surface.
- Source-backed records validate against the relevant DataHub schema.
- Default tests remain offline-safe and live tests remain skipped by default.
- Any real-source work has gated live evidence or a truthful diagnosed SKIP/FAIL requiring Review/Controller follow-up.
- Capability metadata remains conservative and reflects only proven public-source coverage.
- No inactive downstream module behavior is introduced.
