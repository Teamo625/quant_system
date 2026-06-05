# TASK-086 DataHub ETF/Fund Premium-Discount Contracts

## Role

5.3 Execution Window.

## Context

TASK-085 is closed after accepted Review Agent verification. It hardened ETF/fund `FUND_FLOW` access from one-fund one-date scale/share slices to caller-provided multi-symbol bounded date-window behavior with gated live PASS evidence.

Phase 2.5 remains open because DataHub is still not trading-usable under `coordination/ROADMAP.md`: ETF/fund premium/discount, index, sector, macro/policy, source-health, and blocked paid index-weight gaps still require accepted hardening or explicit owner waiver.

Current `fund_premium_discount` capability truth maps to `DatasetName.DAILY_BARS` and `DatasetName.FUND_NAV_SNAPSHOT` and says premium/discount can be derived, but it lacks a dedicated validated DataHub contract target. Before any adapter or derived source-fact implementation, DataHub needs a canonical premium/discount source-fact contract.

This task must not reopen FeatureHub, Scanner, StrategyLab, BacktestEngine, portfolio, signal, risk, AI, notification, UI, or automated trading work.

## Objective

Add a dedicated DataHub dataset contract for ETF/fund premium-discount source facts, focused on instrument x trade-date premium/discount metrics that downstream modules can consume without overloading `DAILY_BARS` or `FUND_NAV_SNAPSHOT`.

This is a contract-only task. Do not implement live source adapters, route discovery, full-market collection, local warehouse refresh orchestration, downstream feature calculation, scanner ranking, strategy/backtest logic, signal/risk/portfolio logic, AI reports, notifications, UI, or automated trading.

## Allowed Writes

Only:

- `quant/datahub/datasets.py`
- `quant/datahub/source_catalog.py`
- `quant/datahub/source_capabilities.py`
- `tests/datahub/test_datasets.py`
- `tests/datahub/test_source_catalog.py`
- `tests/datahub/test_source_capabilities.py`
- `coordination/reports/TASK-086_REPORT.md`

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files
- `coordination/reviews/**`
- `coordination/integrations/**`
- `quant/datahub/adapters/**`
- `tests/datahub/*live.py`
- `quant/features/`
- `quant/scanner/`
- `quant/strategies/`
- `quant/backtest/`
- `quant/portfolio/`
- `quant/notification/`
- `quant/ai/`
- `quant/ui/`

Do not add live network calls, use credentials, cookies, tokens, browser session state, or private account data.

## Contract Requirements

Add a new canonical dataset contract with a clear name such as `FUND_PREMIUM_DISCOUNT`.

The schema should support source-fact records with fields sufficient for:

- `fund_code`
- `market`
- `trade_date`
- optional close/market price when truthfully available
- optional NAV or IOPV/reference NAV when truthfully available
- at least one premium/discount metric, such as `premium_discount_rate` or equivalent
- optional absolute premium/discount amount
- optional source route/category fields if needed to preserve source truth
- `source`
- optional `source_ts`
- `ingested_at`
- `schema_version`

Keep required fields conservative and source-truth friendly. Do not require every optional price/NAV component if public sources can truthfully provide only a rate or only part of the calculation. Do not invent values.

## Metadata Requirements

Update source catalog/capability metadata narrowly:

- Include the new dataset in relevant ETF/fund public source-family coverage only where the source family plausibly covers ETF premium/discount source facts.
- Update `fund_premium_discount` to map to the new dataset.
- Keep `fund_premium_discount` no higher than `partial` because this task is contract-only.
- Refine `gap_reason` and `recommended_handoff_theme` to say adapter/source-fact implementation remains pending.
- Do not change unrelated capability statuses.

## Tests

Run only offline tests:

- `python3 -m unittest tests/datahub/test_datasets.py`
- `python3 -m unittest tests/datahub/test_source_catalog.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`

No live-enabled smoke is required or allowed because this is contract-only.

## Completion Report

Write `coordination/reports/TASK-086_REPORT.md` with:

- files changed
- tests run
- default network behavior
- live-enabled result
- capability truth changes
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

The task is complete when:

- the new premium-discount dataset exists in the registry and schema map
- schema and semantic validation tests cover valid and invalid premium/discount examples
- source catalog and capability metadata reference the new contract consistently
- `fund_premium_discount` remains conservative and not `covered`
- no adapter or live-fetch logic is added
- default tests pass offline
- the report clearly recommends the next adapter/source hardening task
