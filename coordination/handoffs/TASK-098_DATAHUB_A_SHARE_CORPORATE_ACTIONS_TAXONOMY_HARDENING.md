# TASK-098 DataHub A-share Corporate-Actions Taxonomy Hardening

## Role

5.3 Execution Window.

## Context

TASK-097 is closed after accepted Review Agent verification. It made A-share adjustment-factor semantics first-class under `DatasetName.ADJUSTMENT_FACTORS`, added no-credential public AKShare/Sina qfq/hfq source coverage, provided gated live PASS evidence, and fixed the adjustment-factor live skip classifier so source/route/data failures mentioning Sina or `stock_zh_a_daily` no longer downgrade to environment `SKIP`.

Phase 2.5-P remains open under the Personal Trading Perfection Standard. The accepted TASK-093 readiness gate still reports non-pass follow-up items, and `index_weight_history` remains an owner credential blocker that must not be promoted unless paid Tushare scope is reopened and a future credentialed live smoke records a real PASS.

The next unclosed executable `datahub_hardening` item in the TASK-093 structured queue is:

- `a_share__a_share_capability_readiness__a_share_corporate_actions`
- theme: corporate-actions event taxonomy completion
- reason: breadth across split/dividend/rights event families remains incomplete

## Objective

Harden A-share `DatasetName.CORPORATE_ACTIONS` semantics and source coverage so corporate-action event taxonomy is explicit and practically usable for downstream personal research.

Execution should complete the smallest stable DataHub source-fact path that distinguishes public-source A-share corporate-action event families instead of treating the current dividend slice as sufficient. Use only no-credential public routes. If stable public routes cannot prove a specific event family, record that limitation explicitly and keep capability metadata conservative.

This task must not implement FeatureHub adjusted-price calculations, scanner logic, strategy/backtest behavior, portfolio/signal/risk logic, AI reports, notifications, UI, or automated trading.

## Allowed Writes

Only:

- `quant/datahub/datasets.py`
- `quant/datahub/source_catalog.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `tests/datahub/test_datasets.py`
- `tests/datahub/test_source_catalog.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_akshare_a_share_corporate_actions_adapter.py`
- `tests/datahub/test_akshare_a_share_corporate_actions_live.py`
- `coordination/reports/TASK-098_REPORT.md`

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files except `coordination/reports/TASK-098_REPORT.md`
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

- Review the existing A-share corporate-actions contract and adapter behavior before editing.
- Make corporate-action event taxonomy explicit in the DataHub source fact. At minimum, preserve the existing dividend path and add stable normalized semantics for any additional public-source event families that are actually proven, such as bonus/share distribution, rights issue, split/consolidation, or other exchange/source-exposed corporate-action categories.
- Preserve source truth. Do not infer corporate actions from price gaps, adjusted prices, or adjustment factors unless the public route directly exposes a defensible event record and the report explains why that mapping is source-backed.
- Keep requests caller-provided and bounded. Do not add full-market collection, unbounded backfill, or hidden broad crawling.
- Preserve strict A-share symbol validation. Reject HK, ETF/fund, index-like, malformed, ambiguous, missing, or unsupported symbols.
- Preserve deterministic sorting and duplicate handling by a stable key that includes at least symbol, event/effective date, event type, source, and any source-provided announcement/ex-rights date needed to disambiguate events.
- Ensure schema validation covers new or clarified corporate-action fields. Optional fields are acceptable when source truth varies by event family, but required fields must not force fabricated values.
- Update `source_catalog` and `source_capabilities` only to reflect proven public-source truth. Keep `a_share_corporate_actions` conservative unless implementation and live evidence justify promotion.
- If no stable no-credential public route can prove more than the current dividend slice, record route investigation evidence in the report, add any useful contract/test clarification, and do not over-promote the capability.

## Tests

Required offline/default tests:

- `python3 -m unittest tests/datahub/test_datasets.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`
- `python3 -m unittest tests/datahub/test_source_catalog.py`
- `python3 -m unittest tests/datahub/test_akshare_a_share_corporate_actions_adapter.py`
- `python3 -m unittest -v tests/datahub/test_akshare_a_share_corporate_actions_live.py`

Live smoke requirement:

- If any real-source corporate-actions adapter path is added or materially changed, run `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_corporate_actions_live.py`.
- The live smoke must be explicitly gated and skipped by default.
- Report PASS, SKIP, or FAIL truthfully with root-cause evidence. If the live smoke skips because of network, proxy, DNS, TLS, upstream, or public-source availability, diagnose and modify allowed code/tests/report where feasible instead of only documenting the skip.

## Completion Report

Write `coordination/reports/TASK-098_REPORT.md` with:

- files changed
- tests run
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence, or explicit `SKIP` only if no real-source adapter path was added or materially changed
- corporate-action taxonomy/profile chosen and why
- public-route investigation result by event family
- whether `a_share_corporate_actions` capability truth changed
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

The task is complete when:

- A-share corporate-action event taxonomy is explicit and test-covered rather than limited to an undocumented dividend slice.
- Source catalog/capability truth reflects only proven public-source coverage.
- Default tests remain offline-safe and live tests remain skipped by default.
- Any real-source work has gated live evidence or a truthful diagnosed SKIP/FAIL requiring Review/Controller follow-up.
- No inactive downstream module behavior is introduced.
