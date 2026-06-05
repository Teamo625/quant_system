# TASK-077 DataHub A-share Financial History Batch Hardening

## Role

5.3 Execution Window.

## Context

TASK-071 audited DataHub against the trading-usable completion standard and found that most real-source capabilities remain narrow slices. TASK-072 closed the A-share daily-bars batch gap. TASK-073 and TASK-074 added contract and bounded adapter coverage for A-share listing/delisting/ST/status history. TASK-075 proved caller-provided multi-symbol bounded A-share valuation access. TASK-076 proved caller-provided multi-symbol bounded A-share capital-flow access while keeping capital-flow and northbound capability truth conservative.

Phase 2.5 remains open because A-share medium/long-term fundamental research inputs are still not trading-usable enough. `a_share_financial_statements` and `a_share_financial_indicators` remain `partial`; the existing `AkshareAShareFinancialDataAdapter` has accepted one-symbol live evidence but still rejects multi-symbol requests and does not yet prove practical batch/history behavior.

This task is the next current-phase hardening slice. It must not reopen FeatureHub, Scanner, StrategyLab, BacktestEngine, portfolio, signal, risk, AI, notification, UI, or automated trading work.

## Objective

Harden AKShare-backed A-share `FINANCIAL_STATEMENTS` and `FINANCIAL_INDICATORS` access from one-symbol slices into deterministic, caller-provided multi-symbol access with bounded report-period/date filtering where public routes expose report-period history.

The adapter should preserve existing one-symbol behavior, reject invalid symbols clearly, normalize records to the existing financial datasets, keep default tests offline-safe, and include gated live smoke evidence that truthfully reports PASS, SKIP, or FAIL with root-cause evidence.

This task does not require full-market collection, full-history backfill, new financial dataset contracts, credentialed Tushare routes, feature calculation, or local warehouse refresh orchestration.

## Allowed Writes

Only:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/source_capabilities.py`
- `tests/datahub/test_akshare_a_share_financial_data_adapter.py`
- `tests/datahub/test_akshare_a_share_financial_data_live.py`
- `tests/datahub/test_source_capabilities.py`
- `coordination/reports/TASK-077_REPORT.md`

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files
- `coordination/reviews/**`
- `coordination/integrations/**`
- `quant/datahub/datasets.py`
- `quant/datahub/source_catalog.py`
- unrelated DataHub adapters or tests
- `quant/features/`
- `quant/scanner/`
- `quant/strategies/`
- `quant/backtest/`
- `quant/portfolio/`
- `quant/notification/`
- `quant/ai/`
- `quant/ui/`

Do not use credentials, cookies, tokens, browser session state, or private account data.

Do not implement downstream feature calculation, scanner ranking, strategy/backtest logic, portfolio/signal/risk, AI reports, notification, UI, or automated trading.

## Implementation Requirements

- Extend `AkshareAShareFinancialDataAdapter` for multiple requested A-share symbols through the existing `SourceRequest.symbols` path.
- Preserve support for exactly one symbol.
- Keep `symbols=None` or an empty symbol list as a clear error; do not silently fetch full-market financial tables.
- Validate and normalize A-share symbol formats consistently with existing A-share AKShare adapter behavior.
- Reject HK, ETF/fund, index-like, malformed, ambiguous, missing, and unsupported symbols clearly.
- Support both `DatasetName.FINANCIAL_STATEMENTS` and `DatasetName.FINANCIAL_INDICATORS` for every requested valid A-share symbol where the selected public routes provide rows.
- Honor `start_date` and `end_date` using normalized report-period or report-date fields where available. If a route exposes only limited or latest public history, apply bounds deterministically and document that limitation.
- Preserve source-truth optionality for fields not reliably exposed by public routes. Do not invent financial metrics.
- Keep records compatible with `DatasetRegistry.validate_record(...)` for the corresponding dataset.
- Deduplicate deterministically by at least `(symbol, report_period, statement_type/source)` for statements and `(symbol, report_period, metric/source)` or the closest existing record identity for indicators.
- Sort output deterministically by symbol, report period, and stable statement/metric dimensions.
- If one symbol fails due to invalid input or adapter/schema/normalization behavior, fail clearly rather than returning a partial successful batch.
- Do not change `DatasetName.FINANCIAL_STATEMENTS` or `DatasetName.FINANCIAL_INDICATORS` schemas in this task.
- Update only `a_share_financial_statements` and/or `a_share_financial_indicators` capability truth if implementation and live evidence justify it. Keep them `partial` unless the adapter demonstrably satisfies the full trading-usable breadth/history standard; otherwise refine the gap text conservatively.

## Tests

Required offline/default tests:

- `python3 -m unittest tests/datahub/test_akshare_a_share_financial_data_adapter.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`
- `python3 -m unittest -v tests/datahub/test_akshare_a_share_financial_data_live.py`

The live smoke file must remain skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1` is set.

Required live-enabled smoke:

- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_financial_data_live.py`

The live-enabled smoke should validate at least two A-share symbols for both `FINANCIAL_STATEMENTS` and `FINANCIAL_INDICATORS` if the upstream public routes are available. If it fails or skips because of network, proxy, DNS, TLS, upstream, or public-source availability, diagnose the root cause and modify allowed code/tests/report where feasible. Report PASS, SKIP, or FAIL truthfully with evidence.

## Completion Report

Write `coordination/reports/TASK-077_REPORT.md` with:

- files changed
- tests run
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence
- whether `a_share_financial_statements` or `a_share_financial_indicators` capability truth changed
- source route coverage and known financial history limitations
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

The task is complete when:

- multi-symbol A-share financial-statement and financial-indicator requests work through the adapter contract in offline tests
- normalized records validate against the correct `DatasetName`
- report-period/date-window behavior is deterministic and tested
- default live tests remain offline-safe and skipped by default
- a live-enabled smoke is attempted and truthfully reported
- capability metadata remains conservative and reflects the actual proven source breadth
