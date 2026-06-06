# TASK-116 DataHub Hong Kong Valuation History Contract Hardening

## Role

5.3 Execution Window.

## Context

TASK-115 is closed after accepted Review Agent verification. It strengthened Hong Kong `DatasetName.CORPORATE_ACTIONS` dividend-related taxonomy/history coverage by combining `stock_hk_dividend_payout_em` and `stock_hk_fhpx_detail_ths`, kept default tests offline-safe, recorded live-enabled PASS evidence, and kept `hk_corporate_actions` conservative at `partial` because non-dividend corporate-action families and batch breadth remain unproven.

Phase 2.5-P remains open under `coordination/PHASE_GATE.md` because `build_default_personal_trading_readiness_report()` still reports unresolved non-pass queue items and `phase_closure_ready=False`.

The next executable TASK-093 queue item is:

- follow-up id: `hong_kong__hong_kong_capability_readiness__hk_valuation_history`
- capability: `hk_valuation_history`
- disposition: `datahub_hardening`
- theme: HK valuation history contract hardening

This task stays inside DataHub. It must not reopen FeatureHub, Scanner, StrategyLab, BacktestEngine, portfolio, signal, risk, AI, notification, UI, or automated trading work.

## Objective

Harden Hong Kong `DatasetName.VALUATION_SNAPSHOT` valuation-history source truth beyond the current narrow one-symbol valuation snapshot path by doing one of the following:

1. Prove and implement stronger stable no-credential public-source HK valuation history coverage, focused on dated valuation facts, metric-family/source-route truth, date filtering, and, where feasible, caller-provided symbol breadth; or
2. If no stable no-credential public route can prove stronger coverage, truthfully constrain DataHub source-capability and source-catalog wording without promoting `hk_valuation_history`.

The result must keep `hk_valuation_history` conservative unless implementation, tests, and gated live evidence genuinely satisfy practical public-source personal trading completeness for HK valuation history.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-116_DATAHUB_HK_VALUATION_HISTORY_CONTRACT_HARDENING.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/ROADMAP.md`
- `coordination/reports/TASK-034_REPORT.md`
- `coordination/reviews/TASK-034_REVIEW.md`
- `coordination/reports/TASK-115_REPORT.md`
- `coordination/reviews/TASK-115_REVIEW.md`
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/datasets.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_hk_valuation_snapshot_adapter.py`
- `tests/datahub/test_akshare_hk_valuation_snapshot_live.py`
- `tests/datahub/test_source_capabilities.py`
- related DataHub tests only as needed

## Allowed Writes

Only:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/datasets.py` only if a narrowly compatible optional source-truth field is required
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_hk_valuation_snapshot_adapter.py`
- `tests/datahub/test_akshare_hk_valuation_snapshot_live.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`
- `tests/datahub/test_datasets.py` only if `datasets.py` changes
- `coordination/reports/TASK-116_REPORT.md`

If a tightly related shared DataHub helper test must change, document the exact reason in the report. Do not touch unrelated DataHub domains.

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files other than the TASK-116 report
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

Do not use credentials, cookies, tokens, browser session state, private account data, paid sources, or hidden default live network behavior.

## Implementation Requirements

- Preserve `DatasetName.VALUATION_SNAPSHOT` compatibility and validate returned records through `DatasetRegistry`.
- Preserve canonical HK stock symbols, `market="HK"`, deterministic sorting, and date-window filtering.
- Preserve clear rejection for malformed HK symbols, unsupported market symbols, ambiguous values, empty symbol lists, and invalid date ranges.
- Investigate stable no-credential public routes available in the repository environment for HK valuation facts, including the existing `stock_hk_valuation_comparison_em`, `stock_hk_eniu_indicator`, and Baidu valuation fallback logic already represented in `AkshareHKValuationSnapshotAdapter`.
- If a stronger route or route combination is implemented:
  - keep route-name-bearing AKShare argument/signature/schema/payload/normalization defects as hard failures;
  - classify only genuine network/proxy/DNS/TLS/upstream/public-source availability failures as live unavailability;
  - make source-route and metric-family truth explicit without inventing unproven valuation metrics;
  - preserve source-truth optionality for fields not reliably exposed by public routes;
  - keep route-distinct facts separate when source facts differ;
  - deduplicate deterministically by at least symbol, trade date, source, source route, and metric identity;
  - sort deterministically by symbol, trade date, source route, and metric identity.
- If caller-provided multi-symbol support is expanded, validate the full requested batch before source calls and avoid partial success for invalid input.
- Do not infer valuation history from prices, financial statements, corporate actions, or FeatureHub logic; only source-backed dated valuation facts are in scope.
- If no stronger stable no-credential route is feasible:
  - do not add speculative adapter behavior;
  - update `hk_valuation_history` source-capability and/or source-catalog wording to state proven public-source limits precisely;
  - keep `hk_valuation_history` at `partial`.
- Do not implement HK liquidity, HK financial data, FeatureHub valuation features, full-market local collection, or full-history backfill.

## Tests

Required offline/default tests:

- `python3 -m unittest tests/datahub/test_akshare_hk_valuation_snapshot_adapter.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_hk_valuation_snapshot_live.py`

Run if touched:

- `python3 -m unittest tests/datahub/test_source_catalog.py`
- `python3 -m unittest tests/datahub/test_datasets.py`

The live smoke file must remain skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1` is set.

Required live-enabled smoke:

- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_valuation_snapshot_live.py`

The live-enabled smoke should attempt to prove the strongest feasible no-credential HK valuation-history truth for at least one liquid HK stock symbol and, if implemented, any newly selected route, metric family, or symbol-breadth behavior. If route availability, proxy, DNS, TLS, upstream behavior, or public-source limits prevent stronger proof, record PASS, SKIP, or FAIL truthfully with root-cause evidence and keep capability truth conservative.

## Completion Report

Write `coordination/reports/TASK-116_REPORT.md` with:

- files changed
- implementation summary
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence
- whether `hk_valuation_history` capability truth changed
- source route coverage, metric taxonomy coverage, date-window behavior, history-continuity evidence, and known HK valuation limitations
- whether stronger public-source valuation-history coverage was implemented, constrained, or unsupported
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

The task is complete when:

- HK valuation-history source truth is either strengthened with deterministic implementation/tests/live evidence or explicitly constrained without promotion;
- default tests remain offline-safe;
- live-enabled evidence is attempted and truthfully reported;
- source-capability/source-catalog wording cannot silently imply closure-grade HK valuation breadth when only bounded coverage is proven;
- no downstream modules or paid/private scopes are touched.
