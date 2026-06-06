# TASK-117 DataHub Hong Kong Financial Breadth and History Hardening

## Role

5.3 Execution Window.

## Context

TASK-116 is closed after accepted Review Agent verification. It strengthened Hong Kong `DatasetName.VALUATION_SNAPSHOT` from one-symbol latest valuation coverage into caller-provided HK symbol batches with bounded dated PE/PB/market-cap history from `stock_hk_indicator_eniu`, optional same-date Baidu metric supplementation when reachable, explicit `source_route` truth, deterministic date-window behavior, and conservative capability/source wording. `hk_valuation_history` remains `partial` because current-dated continuity and independent no-credential redundancy remain unproven.

Phase 2.5-P remains open under `coordination/PHASE_GATE.md` because `build_default_personal_trading_readiness_report()` still reports `overall_status=blocked`, `phase_closure_ready=False`, status counts `pass=3`, `warn=6`, `blocked=1`, `fail=0`, and 42 non-pass follow-up queue items. The next executable TASK-093 queue item after `hk_valuation_history` is:

- follow-up id: `hong_kong__hong_kong_capability_readiness__hk_financial_data`
- capability: `hk_financial_data`
- disposition: `datahub_hardening`
- theme: expand HK financial market breadth and history coverage

This task stays inside DataHub. It must not reopen FeatureHub, Scanner, StrategyLab, BacktestEngine, portfolio, signal, risk, AI, notification, UI, automated trading, paid credentials, or private data.

## Objective

Harden Hong Kong `DatasetName.FINANCIAL_STATEMENTS` and `DatasetName.FINANCIAL_INDICATORS` beyond the current bounded multi-symbol route by doing one of the following:

1. Prove and implement stronger stable no-credential public-source HK financial breadth/history coverage, focused on broader stock sample behavior, report-period history continuity, explicit source-route / statement / metric-family truth, deterministic date-window filtering, and route-defect classification; or
2. If no stable no-credential public route can prove stronger coverage, truthfully constrain DataHub source-capability and source-catalog wording without promoting `hk_financial_data`.

The result must keep `hk_financial_data` conservative unless implementation, tests, and gated live evidence genuinely satisfy practical public-source personal trading completeness for HK financial data.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-117_DATAHUB_HK_FINANCIAL_BREADTH_HISTORY_HARDENING.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/ROADMAP.md`
- `coordination/reports/TASK-043_REPORT.md`
- `coordination/reviews/TASK-043_REVIEW.md`
- `coordination/reports/TASK-081_REPORT.md`
- `coordination/reviews/TASK-081_REVIEW.md`
- `coordination/reports/TASK-116_REPORT.md`
- `coordination/reviews/TASK-116_REVIEW.md`
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/datasets.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_hk_financial_data_adapter.py`
- `tests/datahub/test_akshare_hk_financial_data_live.py`
- `tests/datahub/test_source_capabilities.py`
- related DataHub tests only as needed

## Allowed Writes

Only:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/datasets.py` only if a narrowly compatible optional source-truth field or validation rule is required
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_hk_financial_data_adapter.py`
- `tests/datahub/test_akshare_hk_financial_data_live.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`
- `tests/datahub/test_datasets.py` only if `datasets.py` changes
- `coordination/reports/TASK-117_REPORT.md`

If a tightly related shared DataHub helper test must change, document the exact reason in the report. Do not touch unrelated DataHub domains.

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files other than the TASK-117 report
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

Do not use credentials, tokens, cookies, browser session state, private account data, paid sources, or hidden default live network behavior.

## Implementation Requirements

- Preserve `DatasetName.FINANCIAL_STATEMENTS` and `DatasetName.FINANCIAL_INDICATORS` compatibility and validate returned records through `DatasetRegistry`.
- Preserve canonical HK stock symbols, `market="HK"`, deterministic sorting, report-period/date-window filtering, and clear invalid range rejection.
- Preserve clear rejection for malformed HK symbols, unsupported market symbols, ambiguous values, empty symbol lists, and requested symbols that yield no usable rows.
- Investigate stable no-credential public routes available in the repository environment for HK financial statements and indicators, including the existing AKShare `stock_financial_hk_report_em` and `stock_financial_hk_analysis_indicator_em` routes and any same-scope no-credential public alternatives already available through AKShare.
- If stronger route coverage or route combinations are implemented:
  - keep route-name-bearing AKShare argument/signature/schema/payload/normalization defects as hard failures;
  - classify only genuine network/proxy/DNS/TLS/upstream/public-source availability failures as live unavailability;
  - make `source_route` truth explicit for statement and indicator records where records come from a specific public route;
  - preserve statement-type truth for balance sheet, income statement, and cash-flow records;
  - preserve indicator metric truth, and add or tighten `metric_family` only where the source metric family is deterministic and schema-compatible;
  - preserve source-truth optionality for fields not reliably exposed by public routes;
  - keep route-distinct facts separate when source facts differ;
  - deduplicate deterministically by symbol, report period, statement/metric identity, source, and source route.
- If no stronger stable no-credential route is feasible:
  - do not add speculative adapter behavior;
  - update `hk_financial_data` source-capability and/or source-catalog wording to state proven public-source limits precisely;
  - keep `hk_financial_data` at `partial`.
- Do not implement HK liquidity, HK valuation features, FeatureHub fundamentals features, full-market local collection, or full-history backfill.

## Tests

Required offline/default tests:

- `python3 -m unittest tests/datahub/test_akshare_hk_financial_data_adapter.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_hk_financial_data_live.py`

Run if touched:

- `python3 -m unittest tests/datahub/test_source_catalog.py`
- `python3 -m unittest tests/datahub/test_datasets.py`

The live smoke file must remain skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1` is set.

Required live-enabled smoke:

- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_financial_data_live.py`

The live-enabled smoke should attempt to prove the strongest feasible no-credential HK financial-data truth for at least two liquid HK stock symbols and, if implemented, any newly selected route, metric family, statement family, date-window, or symbol-breadth behavior. If route availability, proxy, DNS, TLS, upstream behavior, or public-source limits prevent stronger proof, record PASS, SKIP, or FAIL truthfully with root-cause evidence and keep capability truth conservative.

## Completion Report

Write `coordination/reports/TASK-117_REPORT.md` with:

- files changed
- implementation summary
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence
- whether `hk_financial_data` capability truth changed
- source route coverage, statement-family coverage, metric-family coverage, date-window behavior, history-continuity evidence, and known HK financial-data limitations
- whether stronger public-source HK financial breadth/history coverage was implemented, constrained, or unsupported
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

The task is complete when:

- HK financial-data source truth is either strengthened with deterministic implementation/tests/live evidence or explicitly constrained without promotion;
- default tests remain offline-safe;
- live-enabled evidence is attempted and truthfully reported;
- source-capability/source-catalog wording cannot silently imply closure-grade HK financial breadth/history when only bounded coverage is proven;
- no downstream modules or paid/private scopes are touched.
