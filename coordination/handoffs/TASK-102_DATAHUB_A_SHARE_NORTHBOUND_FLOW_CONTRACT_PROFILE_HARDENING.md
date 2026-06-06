# TASK-102 DataHub A-share Northbound-Flow Contract Profile Hardening

## Role

5.3 Execution Window.

## Context

TASK-101 is closed after accepted Review Agent verification. It added route-level truth for A-share `DatasetName.CAPITAL_FLOW_SNAPSHOT`, preserved route-distinct source facts, kept default tests offline-safe, recorded live-enabled PASS evidence, and kept `a_share_capital_flow` conservative because no stable second dated symbol-level capital-flow history route is proven and the datacenter fallback remains latest-only.

Phase 2.5-P remains open under the Personal Trading Perfection Standard. The accepted TASK-093 readiness gate still reports non-pass follow-up items, and `index_weight_history` remains an owner credential blocker that must not be promoted unless paid Tushare scope is reopened and a future credentialed live smoke records a real PASS.

The next unclosed executable `datahub_hardening` item from the TASK-093 structured queue is:

- `a_share__a_share_capability_readiness__a_share_northbound_flow`
- theme: add dedicated northbound-flow contract profile
- reason: northbound-specific fields are not guaranteed as a dedicated contract slice

## Objective

Make A-share northbound-flow semantics first-class in DataHub where stable no-credential public routes expose source truth.

Execution should add a dedicated northbound-flow dataset contract/profile or an equivalent explicit DataHub contract surface, update source capability/catalog truth conservatively, and adapt existing AKShare northbound-route behavior only where needed to emit schema-valid source facts for the dedicated profile.

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
- `tests/datahub/test_akshare_a_share_northbound_flow_adapter.py`
- `tests/datahub/test_akshare_a_share_northbound_flow_live.py`
- `coordination/reports/TASK-102_REPORT.md`

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files except `coordination/reports/TASK-102_REPORT.md`
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
- Review existing TASK-076 and TASK-101 A-share capital-flow/northbound behavior before editing.
- Preserve existing `DatasetName.CAPITAL_FLOW_SNAPSHOT` behavior and compatibility unless a minimal compatibility adjustment is required for the dedicated northbound profile.
- Use only stable no-credential public routes. Do not add Tushare, paid endpoints, credentialed APIs, browser/session scraping, or private data.
- Define dedicated northbound-flow schema fields only for source-backed facts. Do not fabricate `northbound_net_buy`, holdings, turnover, quota, buy/sell amount, ratio, or symbol-level northbound metrics when public routes do not expose them.
- Preserve clear market/date semantics. If the public route is market-level or symbol-level, the contract must say so through required fields and source metadata rather than mixing incompatible granularities silently.
- Preserve strict A-share symbol validation if a symbol-scoped adapter path is exposed. `symbols=None` or empty symbol lists must remain clear errors for symbol-scoped paths; do not silently fetch full-market tables.
- Preserve deterministic record identity by at least trade date, market/symbol granularity, source, and source route.
- Keep route-name-bearing AKShare argument/signature compatibility errors as hard failures following the existing DataHub live-failure classification policy.
- Keep live-environment/source classifiers narrow. Network/proxy/DNS/TLS/upstream/source unavailability may skip; repository-side schema, contract, normalization, duplicate-conflict, or route-signature defects must fail.
- Update `source_catalog` and `source_capabilities` only to reflect proven public-source truth. Keep `a_share_northbound_flow` conservative unless implementation and live evidence prove a complete practical public-source northbound-flow slice.
- If no stable broader dedicated no-credential route is feasible, add only contract/test/reporting hardening that prevents overclaiming and record attempted route names plus observed limitations in the report.

## Tests

Required offline/default tests:

- `python3 -m unittest tests/datahub/test_datasets.py`
- `python3 -m unittest tests/datahub/test_source_catalog.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`
- `python3 -m unittest tests/datahub/test_akshare_a_share_capital_flow_snapshot_adapter.py`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py`

If a new dedicated northbound adapter/live test file is added, also run:

- `python3 -m unittest tests/datahub/test_akshare_a_share_northbound_flow_adapter.py`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_northbound_flow_live.py`

Live smoke requirement:

- If any real-source northbound adapter path is added or materially changed, run the relevant gated live smoke with `QUANT_SYSTEM_LIVE_TESTS=1`.
- The live smoke must be explicitly gated and skipped by default.
- The live-enabled smoke should validate at least one source-backed dated northbound-flow record if the upstream source is available.
- Report PASS, SKIP, or FAIL truthfully with root-cause evidence. If the live smoke skips because of network, proxy, DNS, TLS, upstream, or public-source availability, diagnose and modify allowed code/tests/report where feasible instead of only documenting the skip.

## Completion Report

Write `coordination/reports/TASK-102_REPORT.md` with:

- files changed
- tests run
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence, or explicit `SKIP` only if no real-source adapter path was added or materially changed
- northbound route investigation result by route/source family
- dedicated contract/profile fields, granularity, identity, and known limitations
- whether `a_share_northbound_flow` capability truth changed
- confirmation that `a_share_capital_flow` compatibility and conservative truth were preserved unless explicitly justified
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

The task is complete when:

- A-share northbound-flow semantics are explicit in DataHub through a dedicated schema/profile or equivalent first-class contract surface.
- Source-backed records validate against the relevant DataHub schema.
- Default tests remain offline-safe and live tests remain skipped by default.
- Any real-source work has gated live evidence or a truthful diagnosed SKIP/FAIL requiring Review/Controller follow-up.
- Capability metadata remains conservative and reflects only proven public-source coverage.
- No inactive downstream module behavior is introduced.
