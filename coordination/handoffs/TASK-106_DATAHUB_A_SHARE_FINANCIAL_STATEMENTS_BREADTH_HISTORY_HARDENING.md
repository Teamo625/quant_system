# TASK-106: DataHub A-share Financial Statements Breadth and History Hardening

## Task ID

TASK-106

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2.5-P: DataHub Personal Trading Perfection Re-Review

## Context

TASK-105 is closed after accepted Review Agent verification of A-share margin financing/lending breadth and history hardening. It proved caller-provided multi-symbol bounded SSE/SZSE margin-detail history with explicit route/exchange provenance and live-enabled PASS evidence, but kept `a_share_margin_financing_and_lending` conservative because BSE symbol-level coverage, symbol-compatible exchange-summary reconciliation, and long-history continuity remain incomplete.

Phase 2.5-P remains open because `build_default_personal_trading_readiness_report()` still reports overall `blocked`, phase closure `false`, and unresolved structured follow-up queue items.

The next unclosed executable TASK-093 queue item is:

- follow-up id: `a_share__a_share_capability_readiness__a_share_financial_statements`
- capability: `a_share_financial_statements`
- current status: `warn`
- disposition: `datahub_hardening`
- next handoff theme: expand A-share financial-statement breadth and history coverage

Existing TASK-044 and TASK-077 work added public AKShare financial-statement coverage through `stock_financial_report_sina` and verified caller-provided multi-symbol bounded report-period access. Capability truth remains `partial` because broader public-source history, statement-family breadth, route-shape resilience, and trading-grade completeness are not yet proven.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-106_DATAHUB_A_SHARE_FINANCIAL_STATEMENTS_BREADTH_HISTORY_HARDENING.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/ROADMAP.md`
- `coordination/reports/TASK-044_REPORT.md`
- `coordination/reviews/TASK-044_REVIEW.md`
- `coordination/reports/TASK-077_REPORT.md`
- `coordination/reviews/TASK-077_REVIEW.md`
- `coordination/reports/TASK-105_REPORT.md`
- `coordination/reviews/TASK-105_REVIEW.md`
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/datasets.py`
- `quant/datahub/source_capabilities.py`
- `tests/datahub/test_akshare_a_share_financial_data_adapter.py`
- `tests/datahub/test_akshare_a_share_financial_data_live.py`
- related DataHub tests only as needed

## Goal

Harden A-share financial-statement source coverage beyond the current bounded report-period slice where stable no-credential public routes expose source truth.

The task should improve one or more of:

- statement-family breadth for balance sheet, income statement, cash-flow statement, or any other public route family that can be normalized truthfully to `DatasetName.FINANCIAL_STATEMENTS`
- history continuity for caller-provided symbols and requested report-period/date windows
- source-route provenance and statement-type truth so downstream consumers can distinguish route families without guessing
- duplicate/conflict handling across statement types, routes, symbols, and report periods
- live-smoke classifier truthfulness for selected financial-statement route families
- source capability gap wording so remaining public-source limitations are explicit

Do not mark `a_share_financial_statements` as `covered` unless implementation and live evidence genuinely satisfy full practical public-source breadth/history for personal trading use. Conservative `partial` is expected unless proven otherwise.

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
- `coordination/reports/TASK-106_REPORT.md`

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

1. Preserve the existing `DatasetName.FINANCIAL_STATEMENTS` contract unless a narrowly optional source-truth field is needed for route or statement-family provenance.
2. Preserve support for `market="A_SHARE"`, `source="akshare_cn_hk_public_family"`, canonical A-share symbols, deterministic sorting, schema validation, and source-truth normalization.
3. Keep `symbols=None` or an empty symbol list as a clear error; do not silently fetch full-market financial tables.
4. Reject unsupported datasets, invalid symbols, invalid report-period/date windows, malformed payloads, route signature/call-compatibility defects, schema failures, and normalization errors as hard failures.
5. Classify only genuine network/proxy/DNS/TLS/upstream/source availability failures as live `SKIP`.
6. Audit existing financial-data live-unavailable classifiers. Route/function tokens such as `stock_financial_report_sina`, `stock_financial_analysis_indicator_em`, or upstream endpoint names must not by themselves convert repository-side payload/schema/normalization/signature defects into environment `SKIP`.
7. Preserve existing `FINANCIAL_INDICATORS` behavior. If shared adapter changes require indicator test updates, keep them narrowly regression-focused and document why.
8. Keep default tests offline-safe. No default test may perform real network IO.
9. Do not add credentials, cookies, browser scraping, paid/private sources, Tushare fallback, scheduler/backfill orchestration, FeatureHub features, scanner logic, strategies, backtests, signals, portfolio/risk, AI, notification, UI, or automated trading.

## Public Route Exploration Boundary

Execution may inspect local AKShare callable availability and use deterministic fixtures for any selected route. Candidate route families may include locally available no-credential public AKShare functions related to A-share financial reports, including the existing `stock_financial_report_sina` route.

Use only routes that can be represented truthfully in `FINANCIAL_STATEMENTS`. If a route shape is unstable, latest-only, metric-only, indicator-only, summary-only, or not source-compatible, record the limitation and keep capability truth conservative.

## Offline Tests

Add or update focused offline tests covering the changed behavior:

- statement-family normalization and source-route/statement-type truth if added
- bounded report-period/date-window behavior and any expanded history iteration
- deterministic sorting and duplicate/conflict handling across symbols, statement types, routes, and report periods
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
- validate at least one live `FINANCIAL_STATEMENTS` record through `DatasetRegistry` when public routes are reachable
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

Write `coordination/reports/TASK-106_REPORT.md` with:

- files changed
- implementation summary
- tests run and results
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence
- whether `a_share_financial_statements` capability truth changed
- source route coverage and known financial-statement history limitations
- deviations from this handoff
- risks or follow-up tasks
