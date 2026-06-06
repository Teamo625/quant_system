# TASK-108: DataHub A-share Company Announcements Breadth and History Hardening

## Task ID

TASK-108

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2.5-P: DataHub Personal Trading Perfection Re-Review

## Context

TASK-107 is closed after accepted Review Agent verification of A-share financial-indicator breadth/history/source-truth hardening. It added optional `source_route` and `metric_family` truth to `DatasetName.FINANCIAL_INDICATORS`, proved schema-valid live records from `stock_financial_analysis_indicator_em`, tightened provenance and duplicate behavior, and kept `a_share_financial_indicators` conservative because second-route redundancy, full long-history continuity, and cross-industry metric-family completeness remain unproven.

Phase 2.5-P remains open because `build_default_personal_trading_readiness_report()` still reports overall `blocked`, phase closure `false`, and unresolved structured follow-up queue items.

The next unclosed executable TASK-093 queue item is:

- follow-up id: `a_share__a_share_capability_readiness__a_share_company_announcements`
- capability: `a_share_company_announcements`
- current status: `warn`
- disposition: `datahub_hardening`
- next handoff theme: expand A-share company-announcement breadth and history coverage

Existing TASK-046 work added a bounded public AKShare A-share `DatasetName.COMPANY_ANNOUNCEMENTS` adapter slice with live-enabled PASS evidence. Capability truth remains `partial` because coverage is still narrow relative to practical A-share announcement workflows: breadth across symbols, announcement categories, date-window/history behavior, source-route truth, and cross-market normalization parity are not yet proven enough for phase closure.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-108_DATAHUB_A_SHARE_COMPANY_ANNOUNCEMENTS_BREADTH_HISTORY_HARDENING.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/ROADMAP.md`
- `coordination/reports/TASK-046_REPORT.md`
- `coordination/reviews/TASK-046_REVIEW.md`
- `coordination/reports/TASK-098_REPORT.md`
- `coordination/reviews/TASK-098_REVIEW.md`
- `coordination/reports/TASK-107_REPORT.md`
- `coordination/reviews/TASK-107_REVIEW.md`
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/datasets.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_a_share_company_announcements_adapter.py`
- `tests/datahub/test_akshare_a_share_company_announcements_live.py`
- `tests/datahub/test_hkex_company_announcements_adapter.py`
- related DataHub tests only as needed

## Goal

Harden A-share company-announcement source coverage beyond the current bounded one-symbol/small-window slice where stable no-credential public routes expose source truth.

The task should improve one or more of:

- caller-provided multi-symbol announcement fetching while keeping request bounds explicit
- date-window/history continuity beyond the original narrow slice, without silently attempting full-market/full-history backfills
- announcement category/type normalization and source-truth preservation for public route fields
- source-route provenance so downstream consumers can distinguish route families without guessing
- duplicate/conflict handling across symbols, announcement ids, titles, routes, publish times, and URLs
- live-smoke classifier truthfulness for selected company-announcement route families
- source capability/catalog wording so remaining public-source limitations are explicit

Do not mark `a_share_company_announcements` as `covered` unless implementation and live evidence genuinely satisfy full practical public-source breadth/history for personal trading use. Conservative `partial` is expected unless proven otherwise.

## Allowed Files

Execution may create or modify only:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/datasets.py` only if a narrowly compatible optional source-truth field is required
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py` only if implemented source coverage makes catalog truth inconsistent
- `tests/datahub/test_akshare_a_share_company_announcements_adapter.py`
- `tests/datahub/test_akshare_a_share_company_announcements_live.py`
- `tests/datahub/test_hkex_company_announcements_adapter.py` only if shared `COMPANY_ANNOUNCEMENTS` contract changes require HK regression protection
- `tests/datahub/test_hkex_company_announcements_live.py` only if shared live classifier/contract behavior requires HK regression protection
- `tests/datahub/test_datasets.py` only if `datasets.py` changes
- `tests/datahub/test_source_capabilities.py` if capability wording/status changes
- `tests/datahub/test_source_catalog.py` if catalog truth changes
- `coordination/reports/TASK-108_REPORT.md`

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

1. Preserve the existing `DatasetName.COMPANY_ANNOUNCEMENTS` contract unless a narrowly optional source-truth field is needed for route/category provenance.
2. Preserve support for `market="A_SHARE"`, `source="akshare_cn_hk_public_family"`, canonical A-share symbols, deterministic sorting, schema validation, and source-truth normalization.
3. Keep `symbols=None` or an empty symbol list as a clear error; do not silently fetch full-market announcements.
4. Keep request breadth bounded. If multi-symbol support is added, require caller-provided symbols and enforce a clear maximum batch size/date-window policy.
5. Reject unsupported datasets, invalid symbols, invalid date windows, malformed payloads, route signature/call-compatibility defects, schema failures, and normalization errors as hard failures.
6. Classify only genuine network/proxy/DNS/TLS/upstream/source availability failures as live `SKIP`.
7. Audit existing company-announcement live-unavailable classifiers. Route/function tokens and provider names must not by themselves convert repository-side payload/schema/normalization/signature defects into environment `SKIP`.
8. Preserve existing HKEX `COMPANY_ANNOUNCEMENTS` behavior unless a shared schema change is narrowly required and regression-protected.
9. Keep default tests offline-safe. No default test may perform real network IO.
10. Do not add credentials, cookies, browser scraping, paid/private sources, Tushare fallback, scheduler/backfill orchestration, FeatureHub features, scanner logic, strategies, backtests, signals, portfolio/risk, AI, notification, UI, or automated trading.

## Public Route Exploration Boundary

Execution may inspect local AKShare callable availability and use deterministic fixtures for any selected no-credential public route related to A-share company announcements.

Use only routes that can be represented truthfully in `COMPANY_ANNOUNCEMENTS`. If a route shape is unstable, latest-only, category-only, summary-only, not symbol-compatible, not date-window-compatible, or not source-compatible, record the limitation and keep capability truth conservative.

## Offline Tests

Add or update focused offline tests covering the changed behavior:

- multi-symbol or expanded bounded date-window behavior if implemented
- source-route/category/type normalization if added
- deterministic sorting and duplicate/conflict handling across symbols, ids, titles, URLs, routes, and publish times
- schema validation via `DatasetRegistry`
- malformed payload and missing-field failures
- invalid symbol/date-window failures
- route signature/call-compatibility failures remaining hard failures
- live classifier regression coverage for any newly classified route or upstream token
- source capability/catalog assertions if metadata changes
- HKEX announcement regression tests if the shared `COMPANY_ANNOUNCEMENTS` contract changes

## Mandatory Live Smoke

Because this is real-source DataHub hardening, run a gated live smoke:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_company_announcements_live.py`

The live test must:

- skip by default unless `QUANT_SYSTEM_LIVE_TESTS=1`
- use no credentials
- validate at least one live `COMPANY_ANNOUNCEMENTS` record through `DatasetRegistry` when public routes are reachable
- assert source, market, canonical A-share symbol, publish time/date-window behavior, and any newly added route/provenance field
- fail on adapter/schema/normalization/signature defects
- skip only for genuine environment/upstream/source availability issues, with root-cause evidence

If the live-enabled run fails or skips because of network, proxy, DNS, TLS, upstream, or public-source availability, the report must include root-cause evidence and feasible repository-level fixes attempted. Controller closure will require a fresh review cycle and may require a follow-up rework under `AGENTS.md`.

## Required Test Commands

Run:

- `python3 -m unittest tests/datahub/test_akshare_a_share_company_announcements_adapter.py`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_company_announcements_live.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`

Run if touched:

- `python3 -m unittest tests/datahub/test_hkex_company_announcements_adapter.py`
- `python3 -m unittest -v tests/datahub/test_hkex_company_announcements_live.py`
- `python3 -m unittest tests/datahub/test_source_catalog.py`
- `python3 -m unittest tests/datahub/test_datasets.py`

Run gated live:

- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_company_announcements_live.py`

If shared AKShare behavior changes, run the narrow related regression set needed to prove no collateral breakage.

## Report Requirements

Write `coordination/reports/TASK-108_REPORT.md` with:

- files changed
- implementation summary
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence
- whether `a_share_company_announcements` capability truth changed
- source route coverage and known announcement breadth/history limitations
- deviations from this handoff
- risks or follow-up tasks
