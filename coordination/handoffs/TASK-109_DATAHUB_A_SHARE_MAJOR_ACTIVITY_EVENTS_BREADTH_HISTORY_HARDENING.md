# TASK-109: DataHub A-share Major Activity Events Breadth and History Hardening

## Task ID

TASK-109

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2.5-P: DataHub Personal Trading Perfection Re-Review

## Context

TASK-108 is closed after accepted Review Agent verification. It added bounded multi-symbol A-share `DatasetName.COMPANY_ANNOUNCEMENTS` access with `source_route` truth, fixed the reviewed date-window/fallback blocker, kept default tests offline-safe, and recorded live-enabled PASS evidence. `a_share_company_announcements` remains conservative at `partial` because broader announcement history continuity and no-credential source redundancy remain unproven.

Phase 2.5-P remains open because `build_default_personal_trading_readiness_report()` still reports overall `blocked`, phase closure `false`, and unresolved structured follow-up queue items.

The next unclosed executable TASK-093 queue item is:

- follow-up id: `a_share__a_share_capability_readiness__a_share_major_activity_events`
- capability: `a_share_major_activity_events`
- current status: `warn`
- disposition: `datahub_hardening`
- next handoff theme: expand A-share major-activity breadth and history coverage

Existing TASK-049 work added a narrow no-credential AKShare public `DatasetName.MAJOR_ACTIVITY_EVENTS` adapter slice through `stock_dzjy_mrmx` block-trade detail rows, with bounded single-date requests, deterministic normalization, schema validation, symbol filtering, sorting, deduplication, and gated live smoke evidence. Capability truth remains `partial` because major-activity breadth/history is still narrow for practical A-share workflows.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-109_DATAHUB_A_SHARE_MAJOR_ACTIVITY_EVENTS_BREADTH_HISTORY_HARDENING.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/ROADMAP.md`
- `coordination/reports/TASK-049_REPORT.md`
- `coordination/reviews/TASK-049_REVIEW.md`
- `coordination/reports/TASK-108_REPORT.md`
- `coordination/reviews/TASK-108_REVIEW.md`
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/datasets.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_a_share_major_activity_events_adapter.py`
- `tests/datahub/test_akshare_a_share_major_activity_events_live.py`
- related DataHub tests only as needed

## Goal

Harden A-share major-activity event source coverage beyond the current single block-trade detail route where stable no-credential public routes expose source truth.

The task should improve one or more of:

- route breadth across public block-trade detail/statistics/venue/industry/security routes when local AKShare exposes stable no-credential functions
- bounded date-window or multi-date continuity where route behavior supports deterministic iteration
- event taxonomy and `source_route`/route-family provenance so downstream consumers can distinguish source facts without guessing
- participant, direction, value, volume, summary, venue, and aggregation-field source truth where route rows expose it
- duplicate/conflict handling across dates, symbols, routes, event ids, participants, prices, values, volumes, and summaries
- live-smoke classifier truthfulness for selected major-activity route families
- source capability/catalog wording so remaining public-source limitations are explicit

Do not mark `a_share_major_activity_events` as `covered` unless implementation and live evidence genuinely satisfy full practical public-source breadth/history for personal trading use. Conservative `partial` is expected unless proven otherwise.

## Allowed Files

Execution may create or modify only:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/datasets.py` only if a narrowly compatible optional source-truth field is required
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py` only if implemented source coverage makes catalog truth inconsistent
- `tests/datahub/test_akshare_a_share_major_activity_events_adapter.py`
- `tests/datahub/test_akshare_a_share_major_activity_events_live.py`
- `tests/datahub/test_datasets.py` only if `datasets.py` changes
- `tests/datahub/test_source_capabilities.py` if capability wording/status changes
- `tests/datahub/test_source_catalog.py` if catalog truth changes
- `coordination/reports/TASK-109_REPORT.md`

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

1. Preserve the existing `DatasetName.MAJOR_ACTIVITY_EVENTS` contract unless a narrowly optional source-truth field is needed for route/category provenance.
2. Preserve `market="A_SHARE"`, `source="akshare_cn_hk_public_family"`, canonical A-share symbols, deterministic sorting, schema validation, and source-truth normalization.
3. Keep request breadth bounded. Do not silently fetch full-market/full-history major-activity data beyond explicitly requested bounded route/date parameters.
4. Reject unsupported datasets, invalid symbols, invalid date windows, malformed payloads, route signature/call-compatibility defects, schema failures, and normalization errors as hard failures.
5. Classify only genuine network/proxy/DNS/TLS/upstream/source availability failures as live `SKIP`.
6. Audit existing major-activity live-unavailable classifiers. Route/function tokens and provider names must not by themselves convert repository-side payload/schema/normalization/signature defects into environment `SKIP`.
7. Keep default tests offline-safe. No default test may perform real network IO.
8. Do not add credentials, cookies, browser scraping, paid/private sources, Tushare fallback, scheduler/backfill orchestration, FeatureHub features, scanner logic, strategies, backtests, signals, portfolio/risk, AI, notification, UI, or automated trading.

## Public Route Exploration Boundary

Execution may inspect local AKShare callable availability and use deterministic fixtures for selected no-credential public A-share major-activity routes. Candidate route families may include locally available AKShare functions such as:

- `stock_dzjy_mrmx`
- `stock_dzjy_mrtj`
- `stock_dzjy_sctj`
- `stock_dzjy_hygtj`
- `stock_dzjy_hyyybtj`
- `stock_dzjy_yybph`

Use only routes that can be represented truthfully in `MAJOR_ACTIVITY_EVENTS`. If a route shape is unstable, summary-only, latest-only, not symbol-compatible, not date-window-compatible, not source-compatible, or semantically outside major-activity events, record the limitation and keep capability truth conservative.

## Offline Tests

Add or update focused offline tests covering the changed behavior:

- new route-family normalization and event taxonomy/source-route truth
- bounded date/date-window behavior, including any newly supported multi-date iteration
- deterministic sorting and duplicate/conflict handling across routes/dates/symbols/event facts
- schema validation via `DatasetRegistry`
- malformed payload and missing-field failures
- invalid symbol/date-window failures
- route signature/call-compatibility failures remaining hard failures
- live classifier regression coverage for any newly classified route or upstream token
- source capability/catalog assertions if metadata changes

## Mandatory Live Smoke

Because this is real-source DataHub hardening, run a gated live smoke:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_major_activity_events_live.py`

The live test must:

- skip by default unless `QUANT_SYSTEM_LIVE_TESTS=1`
- use no credentials
- validate at least one live `MAJOR_ACTIVITY_EVENTS` record through `DatasetRegistry` when public routes are reachable
- assert source, market, canonical A-share symbol shape, event type, and any newly added route/provenance field
- fail on adapter/schema/normalization/signature defects
- skip only for genuine environment/upstream/source availability issues, with root-cause evidence

If the live-enabled run fails or skips because of network, proxy, DNS, TLS, upstream, or public-source availability, the report must include root-cause evidence and feasible repository-level fixes attempted. Controller closure will require a fresh review cycle and may require a follow-up rework under `AGENTS.md`.

## Required Test Commands

Run:

- `python3 -m unittest tests/datahub/test_akshare_a_share_major_activity_events_adapter.py`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_major_activity_events_live.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`

Run if touched:

- `python3 -m unittest tests/datahub/test_source_catalog.py`
- `python3 -m unittest tests/datahub/test_datasets.py`

Run gated live:

- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_major_activity_events_live.py`

If shared AKShare behavior changes, run the narrow related regression set needed to prove no collateral breakage.

## Report Requirements

Write `coordination/reports/TASK-109_REPORT.md` with:

- files changed
- implementation summary
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence
- whether `a_share_major_activity_events` capability truth changed
- source route coverage and known major-activity breadth/history limitations
- deviations from this handoff
- risks or follow-up tasks
