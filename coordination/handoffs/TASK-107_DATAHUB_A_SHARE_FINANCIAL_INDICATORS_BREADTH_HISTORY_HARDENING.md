# TASK-107: DataHub A-share Financial Indicators Breadth and History Hardening

## Task ID

TASK-107

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2.5-P: DataHub Personal Trading Perfection Re-Review

## Context

TASK-106 is closed after accepted Review Agent verification of A-share financial-statement breadth/history/source-truth hardening. It added explicit `source_route` truth for `DatasetName.FINANCIAL_STATEMENTS`, proved schema-valid gated live evidence through `stock_financial_report_sina`, and kept `a_share_financial_statements` conservative because no validated second no-credential statement route and no full long-history continuity proof exist.

Phase 2.5-P remains open because `build_default_personal_trading_readiness_report()` still reports overall `blocked`, phase closure `false`, and unresolved structured follow-up queue items.

The next unclosed executable TASK-093 queue item is:

- follow-up id: `a_share__a_share_capability_readiness__a_share_financial_indicators`
- capability: `a_share_financial_indicators`
- current status: `warn`
- disposition: `datahub_hardening`
- next handoff theme: expand A-share financial-indicator breadth and history coverage

Existing TASK-044 and TASK-077 work added public AKShare A-share financial-indicator coverage through `stock_financial_analysis_indicator_em` and verified caller-provided multi-symbol bounded report-period access. Capability truth remains `partial` because broader public-source indicator breadth, history continuity, source-route truth, and trading-grade completeness are not yet proven.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-107_DATAHUB_A_SHARE_FINANCIAL_INDICATORS_BREADTH_HISTORY_HARDENING.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/ROADMAP.md`
- `coordination/reports/TASK-044_REPORT.md`
- `coordination/reviews/TASK-044_REVIEW.md`
- `coordination/reports/TASK-077_REPORT.md`
- `coordination/reviews/TASK-077_REVIEW.md`
- `coordination/reports/TASK-106_REPORT.md`
- `coordination/reviews/TASK-106_REVIEW.md`
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/datasets.py`
- `quant/datahub/source_capabilities.py`
- `tests/datahub/test_akshare_a_share_financial_data_adapter.py`
- `tests/datahub/test_akshare_a_share_financial_data_live.py`
- related DataHub tests only as needed

## Goal

Harden A-share financial-indicator source coverage beyond the current bounded report-period slice where stable no-credential public routes expose source truth.

The task should improve one or more of:

- indicator-family breadth for profitability, growth, leverage, operating efficiency, cash-flow, per-share, return, or other public financial-indicator families that can be normalized truthfully to `DatasetName.FINANCIAL_INDICATORS`
- history continuity for caller-provided symbols and requested report-period/date windows
- source-route provenance and indicator-name/metric truth so downstream consumers can distinguish route families without guessing
- duplicate/conflict handling across indicator names, routes, symbols, and report periods
- live-smoke classifier truthfulness for selected financial-indicator route families
- source capability gap wording so remaining public-source limitations are explicit

Do not mark `a_share_financial_indicators` as `covered` unless implementation and live evidence genuinely satisfy full practical public-source breadth/history for personal trading use. Conservative `partial` is expected unless proven otherwise.

## Allowed Files

Execution may create or modify only:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/datasets.py` only if a narrowly compatible optional source-truth field is required
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py` only if implemented source coverage makes catalog truth inconsistent
- `tests/datahub/test_akshare_a_share_financial_data_adapter.py`
- `tests/datahub/test_akshare_a_share_financial_data_live.py`
- `tests/datahub/test_datasets.py` only if `datasets.py` changes
- `tests/datahub/test_source_capabilities.py` if capability wording/status changes
- `tests/datahub/test_source_catalog.py` if catalog truth changes
- `coordination/reports/TASK-107_REPORT.md`

If a tightly related shared DataHub helper test must change, document the exact reason in the report. Do not touch unrelated DataHub domains.

## Forbidden Files

Execution must not modify:

- `AGENTS.md`
- `coordination/PROJECT_STATE.md`
- `coordination/ROADMAP.md`
- `coordination/TASK_BOARD.md`
- `coordination/DECISIONS.md`
- `coordination/RISKS.md`
- `coordination/INTERFACES.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/reviews/**`
- `coordination/integrations/**`
- `coordination/handoffs/**`
- `quant/features/**`
- `quant/scanner/**`
- `quant/strategies/**`
- `quant/backtest/**`
- `quant/portfolio/**`
- `quant/notification/**`
- `quant/ai/**`
- `quant/ui/**`

## Implementation Requirements

1. Preserve the existing `DatasetName.FINANCIAL_INDICATORS` contract unless a narrowly optional source-truth field is needed for route or indicator-family provenance.
2. Preserve support for `market="A_SHARE"`, `source="akshare_cn_hk_public_family"`, canonical A-share symbols, deterministic sorting, schema validation, and source-truth normalization.
3. Keep `symbols=None` or an empty symbol list as a clear error; do not silently fetch full-market financial indicator tables.
4. Reject unsupported datasets, invalid symbols, invalid report-period/date windows, malformed payloads, route signature/call-compatibility defects, schema failures, and normalization errors as hard failures.
5. Classify only genuine network/proxy/DNS/TLS/upstream/source availability failures as live `SKIP`.
6. Audit existing financial-data live-unavailable classifiers. Route/function tokens such as `stock_financial_analysis_indicator_em`, `stock_financial_report_sina`, or upstream endpoint names must not by themselves convert repository-side payload/schema/normalization/signature defects into environment `SKIP`.
7. Preserve existing `FINANCIAL_STATEMENTS` behavior from TASK-106. If shared adapter changes require statement test updates, keep them narrowly regression-focused and document why.
8. Keep default tests offline-safe. No default test may perform real network IO.
9. Do not add credentials, cookies, browser scraping, paid/private sources, Tushare fallback, scheduler/backfill orchestration, FeatureHub features, scanner logic, strategies, backtests, signals, portfolio/risk, AI, notification, UI, or automated trading.

## Public Route Exploration Boundary

Execution may inspect local AKShare callable availability and use deterministic fixtures for any selected route. Candidate route families may include locally available no-credential public AKShare functions related to A-share financial indicators, including the existing `stock_financial_analysis_indicator_em` route.

Use only routes that can be represented truthfully in `FINANCIAL_INDICATORS`. If a route shape is unstable, latest-only, statement-only, summary-only, not metric-compatible, or not source-compatible, record the limitation and keep capability truth conservative.

## Offline Tests

Add or update focused offline tests covering the changed behavior:

- indicator normalization and source-route/indicator-family truth if added
- bounded report-period/date-window behavior and any expanded history iteration
- deterministic sorting and duplicate/conflict handling across symbols, indicator names, routes, and report periods
- schema validation via `DatasetRegistry`
- malformed payload and missing-field failures
- invalid symbol/date/report-period failures
- route signature/call-compatibility failures remaining hard failures
- live classifier regression coverage for any newly classified route or upstream token
- source capability/catalog assertions if metadata changes

## Mandatory Live Smoke

Because this is real-source DataHub hardening, run a gated live smoke:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_financial_data_live.py`

The live test must:

- skip by default unless `QUANT_SYSTEM_LIVE_TESTS=1`
- use no credentials
- validate at least one live `FINANCIAL_INDICATORS` record through `DatasetRegistry` when public routes are reachable
- assert source, market, canonical A-share symbol, report period/date, and any newly added route/provenance field
- fail on adapter/schema/normalization/signature defects
- skip only for genuine environment/upstream/source availability issues, with root-cause evidence

If the live-enabled run fails or skips because of network, proxy, DNS, TLS, upstream, or public-source availability, the report must include root-cause evidence and feasible repository-level fixes attempted. Controller closure will require a fresh review cycle and may require a follow-up rework under `AGENTS.md`.

## Required Test Commands

Run:

- `python3 -m unittest tests/datahub/test_akshare_a_share_financial_data_adapter.py`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_financial_data_live.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`

Run if touched:

- `python3 -m unittest tests/datahub/test_source_catalog.py`
- `python3 -m unittest tests/datahub/test_datasets.py`

Run gated live:

- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_financial_data_live.py`

If shared AKShare behavior changes, run the narrow related regression set needed to prove no collateral breakage.

## Report Requirements

Write `coordination/reports/TASK-107_REPORT.md` with:

- files changed
- implementation summary
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence
- whether `a_share_financial_indicators` capability truth changed
- source route coverage and known financial-indicator history limitations
- deviations from this handoff
- risks or follow-up tasks
