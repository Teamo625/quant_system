# TASK-122 - DataHub ETF/fund scale/share canonical schema

## Role

5.3 Execution

## Phase

Phase 2.5-P DataHub Personal Trading Perfection Re-Review.

## Context

TASK-121 is closed after accepted Review Agent verification. It strengthened ETF/fund `DatasetName.FUND_HOLDINGS` symbol-family truth for exchange ETFs plus explicit `FUND_CN` domestic-equity funds, kept default tests offline-safe, recorded live-enabled PASS evidence, and kept `fund_holdings_composition` conservative at `partial`.

Phase 2.5-P remains open under `coordination/PHASE_GATE.md` because `build_default_personal_trading_readiness_report()` still reports `overall_status=blocked` and `phase_closure_ready=False`. The next executable TASK-093 follow-up queue item is `fund_scale_and_share`, with theme `fund scale/share canonical schema extension`.

Current `fund_scale_and_share` truth is partial because ETF/fund AUM/scale/share facts are not represented as a dedicated normalized contract slice. Existing facts appear indirectly in `FUND_PROFILE`, `FUND_NAV_SNAPSHOT`, or exchange scale/share-style `FUND_FLOW` rows, which is not strong enough for downstream personal trading workflows that need unambiguous instrument x date scale/share source facts.

## Objective

Add a first-class DataHub canonical schema contract for ETF/fund scale and share source facts, then reconcile DataHub capability/source metadata and focused tests to that contract.

This task should not over-promote `fund_scale_and_share`. Keep it conservative unless the implementation proves the full public-source/no-paid personal trading standard, which is not expected from a schema-extension handoff alone.

## Allowed Files

Execution may modify only:

- `quant/datahub/`
- `tests/datahub/`
- `coordination/reports/TASK-122_REPORT.md`

Do not edit controller-owned coordination state files.

## Required Work

1. Add a canonical dataset contract for ETF/fund scale/share facts.
   - Prefer a dedicated `DatasetName` if that matches existing registry patterns.
   - The contract must represent at least:
     - fund/instrument identity
     - observation date or report/trade date
     - source id
     - at least one source-backed scale/share metric, such as AUM/fund scale, shares outstanding, share units, scale/share change, or equivalent public-source fact
   - Include source-route/provenance fields where existing DataHub source-fact patterns support them.
   - Do not invent net inflow, subscription, redemption, or market-value fields when a verified source does not provide them.

2. Preserve existing contracts.
   - Do not break accepted `FUND_PROFILE`, `FUND_NAV_SNAPSHOT`, or `FUND_FLOW` validation.
   - If overlapping fields remain in older datasets, document their compatibility and update tests to prevent schema drift.

3. Reconcile capability and source metadata.
   - Update `fund_scale_and_share` to map to the new canonical contract.
   - Keep the capability `partial` unless the full breadth/history/source-redundancy standard is genuinely proven.
   - Clarify gap text so the remaining limitation is explicit: public-source breadth, long-history continuity, richer flow metrics, and/or route redundancy as appropriate.
   - Update source catalog coverage only to the extent supported by accepted public-source truth or the new local contract.

4. Add focused offline tests.
   - Dataset registry tests for valid and invalid scale/share records.
   - Capability tests proving `fund_scale_and_share` maps to the canonical contract and remains conservatively partial.
   - Source catalog tests if source metadata changes.
   - Regression tests ensuring default tests do not perform live network calls.

5. Adapter work is optional and only if necessary.
   - If execution wires an existing real-source adapter to emit the new dataset, add deterministic offline adapter tests and a gated live smoke test.
   - The live smoke must remain skipped by default and enabled only by `QUANT_SYSTEM_LIVE_TESTS=1`.
   - Any route-signature/schema/payload/normalization defect must fail, not be downgraded to environment `SKIP`.
   - If no adapter is changed, record that no live smoke was required because the task was contract/capability-only.

## Tests

Run the focused offline tests that cover every changed file.

Minimum expected tests:

- dataset registry/schema tests covering the new scale/share contract
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py` if source catalog changes

If adapter work is added, also run the focused adapter tests and both default-skipped and explicitly enabled live smoke tests.

## Report Requirements

Write `coordination/reports/TASK-122_REPORT.md` with:

- files changed
- contract/schema summary
- compatibility confirmation for existing ETF/fund datasets
- tests run
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence if adapter work is added; otherwise state no live test was required and why
- capability truth changes
- deviations from this handoff
- risks or follow-up tasks

## Guardrails

- Stay inside DataHub only.
- Do not implement FeatureHub, Scanner, StrategyLab, BacktestEngine, portfolio/signal/risk, AI, notification, UI, or automated trading logic.
- Do not use credentials, tokens, cookies, or private account data.
- Do not introduce hidden default live network calls.
- Do not mark `fund_scale_and_share` covered from a contract-only or narrow-source slice.
