# TASK-115 DataHub Hong Kong Corporate Actions Taxonomy/History Hardening

## Role

5.3 Execution Window.

## Context

TASK-114 is closed after accepted Review Agent verification. It strengthened Hong Kong daily-bar practical history continuity with an AKShare same-family `stock_hk_daily` fallback, kept default tests offline-safe, recorded live-enabled PASS evidence, and kept `hk_daily_bars` conservative at `partial` because independent public-source redundancy remains unproven.

Phase 2.5-P remains open under `coordination/PHASE_GATE.md` because `build_default_personal_trading_readiness_report()` still reports unresolved non-pass queue items and `phase_closure_ready=False`.

The next TASK-093 queue item is optional `hk_minute_bars` with `disposition=owner_waiver_required`; no owner waiver or explicit feasibility scope has been provided in this controller window, so it is not dispatched as the next executable implementation task.

The next executable TASK-093 queue item is:

- follow-up id: `hong_kong__hong_kong_capability_readiness__hk_corporate_actions`
- capability: `hk_corporate_actions`
- disposition: `datahub_hardening`
- theme: HK corporate-action taxonomy and history coverage

This task stays inside DataHub. It must not reopen FeatureHub, Scanner, StrategyLab, BacktestEngine, portfolio, signal, risk, AI, notification, UI, or automated trading work.

## Objective

Harden Hong Kong `DatasetName.CORPORATE_ACTIONS` source truth beyond the current narrow dividend/distribution slice by doing one of the following:

1. Prove and implement stronger stable no-credential public-source coverage for HK corporate-action event taxonomy, history continuity, route provenance, date filtering, and, where feasible, caller-provided symbol breadth; or
2. If no stable no-credential route can prove stronger coverage, truthfully constrain DataHub source-capability and source-catalog wording without promoting `hk_corporate_actions`.

The result must keep `hk_corporate_actions` conservative unless implementation, tests, and gated live evidence genuinely satisfy practical public-source personal trading completeness for HK corporate actions.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-115_DATAHUB_HK_CORPORATE_ACTIONS_TAXONOMY_HISTORY_HARDENING.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/ROADMAP.md`
- `coordination/reports/TASK-098_REPORT.md`
- `coordination/reviews/TASK-098_REVIEW.md`
- `coordination/reports/TASK-114_REPORT.md`
- `coordination/reviews/TASK-114_REVIEW.md`
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/datasets.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_hk_corporate_actions_adapter.py`
- `tests/datahub/test_akshare_hk_corporate_actions_live.py`
- `tests/datahub/test_source_capabilities.py`
- related DataHub tests only as needed

## Allowed Writes

Only:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/datasets.py` only if a narrowly compatible optional source-truth field is required
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_hk_corporate_actions_adapter.py`
- `tests/datahub/test_akshare_hk_corporate_actions_live.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`
- `tests/datahub/test_datasets.py` only if `datasets.py` changes
- `coordination/reports/TASK-115_REPORT.md`

If a tightly related shared DataHub helper test must change, document the exact reason in the report. Do not touch unrelated DataHub domains.

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files other than the TASK-115 report
- `coordination/reviews/**`
- `coordination/integrations/**`
- `coordination/handoffs/**`
- unrelated DataHub adapters or tests
- `quant/features/**`
- `quant/scanner/**`
- `quant/strategies/**`
- `quant/backtest/**`
- `quant/portfolio/**`
- `quant/notification/**`
- `quant/ai/**`
- `quant/ui/**`

Do not use credentials, cookies, tokens, browser session state, private account data, paid sources, or hidden default live network behavior.

## Implementation Requirements

- Preserve the shared `DatasetName.CORPORATE_ACTIONS` source-fact contract, including explicit `action_family` and `source_route` truth.
- Preserve canonical HK stock symbols, `market="HK"`, schema validation, deterministic sorting, and date-window filtering.
- Preserve clear rejection for malformed HK symbols, unsupported market symbols, ambiguous values, empty symbol lists, and invalid date ranges.
- Investigate stable no-credential public routes available in the repository environment for HK corporate actions, including the existing `stock_hk_dividend_payout_em` primary route and `stock_hk_fhpx_detail_ths` fallback.
- If a stronger route or route combination is implemented:
  - keep route-name-bearing AKShare argument/signature/schema/payload/normalization defects as hard failures;
  - classify only genuine network/proxy/DNS/TLS/upstream/public-source availability failures as live unavailability;
  - make event-family semantics explicit without inventing unproven corporate-action types;
  - keep route-distinct records separate when source facts differ;
  - deduplicate deterministically by at least symbol, event date, action family, source route, and source truth;
  - sort deterministically by symbol, event date, action family, and route;
  - validate returned records through `DatasetRegistry`.
- If caller-provided multi-symbol support is expanded, validate the full requested batch before source calls and avoid partial success for invalid input.
- If no stronger stable no-credential route is feasible:
  - do not add speculative adapter behavior;
  - update `hk_corporate_actions` source-capability and/or source-catalog wording to state proven public-source limits precisely;
  - keep `hk_corporate_actions` at `partial`.
- Do not implement HK minute bars in this task.
- Do not perform full-market local collection or full-history backfill.

## Tests

Required offline/default tests:

- `python3 -m unittest tests/datahub/test_akshare_hk_corporate_actions_adapter.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_hk_corporate_actions_live.py`

Run if touched:

- `python3 -m unittest tests/datahub/test_source_catalog.py`
- `python3 -m unittest tests/datahub/test_datasets.py`

The live smoke file must remain skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1` is set.

Required live-enabled smoke:

- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_corporate_actions_live.py`

The live-enabled smoke should attempt to prove the strongest feasible no-credential HK corporate-action truth for at least one liquid HK stock symbol and, if implemented, any newly selected route or event family. If route availability, proxy, DNS, TLS, upstream behavior, or public-source limits prevent stronger proof, record PASS, SKIP, or FAIL truthfully with root-cause evidence and keep capability truth conservative.

## Completion Report

Write `coordination/reports/TASK-115_REPORT.md` with:

- files changed
- implementation summary
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence
- whether `hk_corporate_actions` capability truth changed
- source route coverage, event-family taxonomy coverage, date-window behavior, history-continuity evidence, and known HK corporate-action limitations
- whether stronger public-source taxonomy/history coverage was implemented, constrained, or unsupported
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

The task is complete when:

- HK corporate-action source truth is either strengthened with deterministic implementation/tests/live evidence or explicitly constrained without promotion;
- default tests remain offline-safe;
- live-enabled evidence is attempted and truthfully reported;
- source-capability/source-catalog wording cannot silently imply closure-grade HK corporate-action breadth when only bounded coverage is proven;
- no downstream modules or paid/private scopes are touched.
