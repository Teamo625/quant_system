# TASK-105: DataHub A-share Margin Financing/Lending Breadth and History Hardening

## Task ID

TASK-105

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2.5-P: DataHub Personal Trading Perfection Re-Review

## Context

TASK-104 is closed after accepted Review Agent verification of the A-share limit-up/down breadth/history work and focused live-classifier truthfulness rework. Phase 2.5-P remains open because `build_default_personal_trading_readiness_report()` still reports overall `blocked`, phase closure `false`, and unresolved structured follow-up queue items.

The next unclosed executable TASK-093 queue item is:

- follow-up id: `a_share__a_share_capability_readiness__a_share_margin_financing_and_lending`
- capability: `a_share_margin_financing_and_lending`
- current status: `warn`
- disposition: `datahub_hardening`
- next handoff theme: expand A-share margin financing/lending breadth and history coverage

Existing TASK-045 work added bounded no-credential AKShare public margin financing/lending adapter coverage for `DatasetName.MARGIN_FINANCING_LENDING` through the SSE/SZSE margin-detail routes. Capability truth remains `partial` because trading-grade breadth/history coverage remains incomplete.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-105_DATAHUB_A_SHARE_MARGIN_FINANCING_LENDING_BREADTH_HISTORY_HARDENING.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/ROADMAP.md`
- `coordination/reports/TASK-045_REPORT.md`
- `coordination/reviews/TASK-045_REVIEW.md`
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/datasets.py`
- `quant/datahub/source_capabilities.py`
- `tests/datahub/test_akshare_a_share_margin_financing_lending_adapter.py`
- `tests/datahub/test_akshare_a_share_margin_financing_lending_live.py`
- related DataHub tests only as needed

## Goal

Harden A-share margin financing and securities lending source coverage beyond the current bounded one-symbol detail slice where stable no-credential public routes expose source truth.

The task should improve one or more of:

- history continuity for requested date windows when public route behavior supports deterministic iteration
- route breadth across SSE/SZSE/BJ-compatible public margin routes, including exchange-level summary/detail routes when they can be normalized truthfully
- source-route or exchange provenance so downstream consumers can distinguish route families without guessing
- securities-lending field coverage when the public source exposes those metrics
- live-smoke classifier truthfulness for the selected margin route family
- source capability gap wording so remaining public-source limitations are explicit

Do not mark `a_share_margin_financing_and_lending` as `covered` unless implementation and live evidence genuinely satisfy full practical public-source breadth/history for personal trading use. Conservative `partial` is expected unless proven otherwise.

## Allowed Files

Execution may create or modify only:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/datasets.py` only if a narrowly compatible optional source-truth field is required
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py` only if implemented source coverage makes catalog truth inconsistent
- `tests/datahub/test_akshare_a_share_margin_financing_lending_adapter.py`
- `tests/datahub/test_akshare_a_share_margin_financing_lending_live.py`
- `tests/datahub/test_datasets.py` only if `datasets.py` changes
- `tests/datahub/test_source_capabilities.py` if capability wording/status changes
- `tests/datahub/test_source_catalog.py` if catalog truth changes
- `coordination/reports/TASK-105_REPORT.md`

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

1. Preserve the existing `DatasetName.MARGIN_FINANCING_LENDING` contract unless a narrowly optional source-truth field is needed for route/exchange provenance.
2. Preserve `market="A_SHARE"`, `source="akshare_cn_hk_public_family"`, deterministic sorting, schema validation, and source-truth normalization.
3. Reject unsupported datasets, invalid symbols, invalid date windows, malformed payloads, route signature/call-compatibility defects, schema failures, and normalization errors as hard failures.
4. Classify only genuine network/proxy/DNS/TLS/upstream/source availability failures as live `SKIP`.
5. Audit the existing margin live-unavailable classifiers. Route or endpoint tokens such as `stock_margin_detail_sse`, `stock_margin_detail_szse`, `querymargin.do`, or `showreport` must not by themselves convert repository-side payload/schema/normalization/signature defects into environment `SKIP`.
6. Keep default tests offline-safe. No default test may perform real network IO.
7. Do not add credentials, cookies, browser scraping, paid/private sources, Tushare fallback, scheduler/backfill orchestration, FeatureHub features, scanner logic, strategies, backtests, signals, portfolio/risk, AI, notification, UI, or automated trading.

## Public Route Exploration Boundary

Execution may inspect local AKShare callable availability and use deterministic fixtures for any selected route. Candidate route families may include locally available AKShare functions such as:

- `stock_margin_detail_sse`
- `stock_margin_detail_szse`
- `stock_margin_sse`
- `stock_margin_szse`
- `stock_margin_account_info`
- `stock_margin_underlying_info_szse`

Use only routes that can be represented truthfully in `MARGIN_FINANCING_LENDING`. If route shapes are unstable, latest-only, exchange-summary-only, or not source-compatible, record the limitation and keep capability truth conservative.

## Offline Tests

Add or update focused offline tests covering the changed behavior:

- route-family normalization and source-route/exchange truth if added
- bounded date behavior and any expanded multi-date iteration
- deterministic sorting and duplicate/conflict handling across routes/dates
- schema validation via `DatasetRegistry`
- malformed payload and missing-field failures
- invalid symbol/date failures
- route signature/call-compatibility failures remaining hard failures
- live classifier regression coverage for any newly classified route or upstream token
- source capability/catalog assertions if metadata changes

## Mandatory Live Smoke

Because this is real-source DataHub hardening, run a gated live smoke:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_margin_financing_lending_live.py`

The live test must:

- skip by default unless `QUANT_SYSTEM_LIVE_TESTS=1`
- use no credentials
- validate at least one live record through `DatasetRegistry` when public routes are reachable
- assert source, market, canonical A-share symbol, and any newly added route/provenance field
- fail on adapter/schema/normalization/signature defects
- skip only for genuine environment/upstream/source availability issues, with root-cause evidence

If the live-enabled run fails or skips because of network, proxy, DNS, TLS, upstream, or public-source availability, the report must include root-cause evidence and feasible repository-level fixes attempted. Controller closure will require a fresh review cycle and may require a follow-up rework under `AGENTS.md`.

## Required Test Commands

Run:

- `python3 -m unittest tests/datahub/test_akshare_a_share_margin_financing_lending_adapter.py`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_margin_financing_lending_live.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`

Run if touched:

- `python3 -m unittest tests/datahub/test_source_catalog.py`
- `python3 -m unittest tests/datahub/test_datasets.py`

Run gated live:

- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_margin_financing_lending_live.py`

If shared AKShare behavior changes, run the narrow related regression set needed to prove no collateral breakage.

## Report Requirements

Write `coordination/reports/TASK-105_REPORT.md` with:

- files changed
- implementation summary
- tests run and results
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence
- whether `a_share_margin_financing_and_lending` capability truth changed
- deviations from this handoff
- risks/follow-up tasks

