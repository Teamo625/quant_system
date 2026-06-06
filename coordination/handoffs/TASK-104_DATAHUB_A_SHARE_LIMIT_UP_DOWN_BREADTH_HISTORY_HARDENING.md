# TASK-104: DataHub A-share Limit-Up/Down Breadth and History Hardening

## Task ID

TASK-104

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2.5-P: DataHub Personal Trading Perfection Re-Review

## Context

TASK-103 is closed after accepted Review Agent verification of the turnover/liquidity live-classifier rework. Phase 2.5-P remains open because `build_default_personal_trading_readiness_report()` still reports overall `blocked`, phase closure `false`, and unresolved structured follow-up queue items.

The next unclosed executable TASK-093 queue item is:

- follow-up id: `a_share__a_share_capability_readiness__a_share_limit_up_down`
- capability: `a_share_limit_up_down`
- current status: `warn`
- disposition: `datahub_hardening`
- next handoff theme: expand A-share limit-up/down breadth and history coverage

Existing TASK-048 work added `DatasetName.LIMIT_UP_DOWN_EVENTS` and bounded no-credential AKShare public pool coverage through `stock_zt_pool_em` and `stock_zt_pool_dtgc_em`. Capability truth remains `partial` because trading-grade breadth/history coverage is still incomplete.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-104_DATAHUB_A_SHARE_LIMIT_UP_DOWN_BREADTH_HISTORY_HARDENING.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/ROADMAP.md`
- `coordination/reports/TASK-048_REPORT.md`
- `coordination/reviews/TASK-048_REVIEW.md`
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/datasets.py`
- `quant/datahub/source_capabilities.py`
- `tests/datahub/test_akshare_a_share_limit_up_down_adapter.py`
- `tests/datahub/test_akshare_a_share_limit_up_down_live.py`
- related DataHub tests only as needed

## Goal

Harden A-share limit-up/down source coverage beyond the current bounded pool slice where stable no-credential public routes expose source truth.

The task should improve one or more of:

- route breadth across limit-up, limit-down, strong pool, first/second board, previous-day, broken-board, or sub-new-stock limit pools when the local AKShare version exposes stable public routes
- bounded multi-date history continuity if route behavior supports deterministic iteration
- event taxonomy/source-route truth so downstream consumers can distinguish route families without guessing
- live-smoke classifier truthfulness for the selected limit-up/down route family
- source capability gap wording so remaining public-source limitations are explicit

Do not mark `a_share_limit_up_down` as `covered` unless implementation and live evidence genuinely satisfy full practical public-source breadth/history for personal trading use. Conservative `partial` is expected unless proven otherwise.

## Allowed Files

Execution may create or modify only:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py` only if implemented source coverage makes catalog truth inconsistent
- `tests/datahub/test_akshare_a_share_limit_up_down_adapter.py`
- `tests/datahub/test_akshare_a_share_limit_up_down_live.py`
- `tests/datahub/test_source_capabilities.py` if capability wording/status changes
- `tests/datahub/test_source_catalog.py` if catalog truth changes
- `coordination/reports/TASK-104_REPORT.md`

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

1. Preserve the existing `DatasetName.LIMIT_UP_DOWN_EVENTS` contract.
2. Preserve `market="A_SHARE"`, `source="akshare_cn_hk_public_family"`, deterministic sorting, schema validation, and source-truth normalization.
3. Add source-route or event-family metadata only when it is truthful and contract-compatible. If a new field is needed, update the DataHub dataset schema and tests in the smallest compatible way.
4. Reject unsupported datasets, invalid symbols, invalid date windows, malformed payloads, route signature/call-compatibility defects, schema failures, and normalization errors as hard failures.
5. Classify only genuine network/proxy/DNS/TLS/upstream/source availability failures as live `SKIP`.
6. Keep default tests offline-safe. No default test may perform real network IO.
7. Do not add credentials, cookies, browser scraping, paid/private sources, Tushare fallback, scheduler/backfill orchestration, FeatureHub features, scanner logic, strategies, backtests, signals, portfolio/risk, AI, notification, UI, or automated trading.

## Public Route Exploration Boundary

Execution may inspect local AKShare callable availability and use deterministic fixtures for any selected route. Candidate route families may include locally available AKShare functions such as:

- `stock_zt_pool_em`
- `stock_zt_pool_dtgc_em`
- `stock_zt_pool_zbgc_em`
- `stock_zt_pool_previous_em`
- `stock_zt_pool_strong_em`
- `stock_zt_pool_sub_new_em`

Use only routes that can be represented truthfully in `LIMIT_UP_DOWN_EVENTS`. If route shapes are unstable or not source-compatible, record the limitation and keep capability truth conservative.

## Offline Tests

Add or update focused offline tests covering the changed behavior:

- route-family normalization and event taxonomy/source-route truth
- bounded date behavior, including any newly supported multi-date iteration
- deterministic sorting and duplicate/conflict handling across routes/dates
- schema validation via `DatasetRegistry`
- malformed payload and missing-field failures
- invalid symbol/date failures
- route signature/call-compatibility failures remaining hard failures
- live classifier regression coverage for any newly classified route or upstream token
- source capability/catalog assertions if metadata changes

## Mandatory Live Smoke

Because this is real-source DataHub hardening, run a gated live smoke:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_limit_up_down_live.py`

The live test must:

- skip by default unless `QUANT_SYSTEM_LIVE_TESTS=1`
- use no credentials
- validate at least one live record through `DatasetRegistry` when public routes are reachable
- assert source, market, symbol shape, limit type, and any newly added route/taxonomy field
- fail on adapter/schema/normalization/signature defects
- skip only for genuine environment/upstream/source availability issues, with root-cause evidence

If the live-enabled run fails or skips because of network, proxy, DNS, TLS, upstream, or public-source availability, the report must include root-cause evidence and feasible repository-level fixes attempted. Controller closure will require a fresh review cycle and may require a follow-up rework under `AGENTS.md`.

## Required Test Commands

Run:

- `python3 -m unittest tests/datahub/test_akshare_a_share_limit_up_down_adapter.py`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_limit_up_down_live.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`

Run if touched:

- `python3 -m unittest tests/datahub/test_source_catalog.py`
- `python3 -m unittest tests/datahub/test_datasets.py`

Run gated live:

- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_limit_up_down_live.py`

If shared AKShare behavior changes, run the narrow related regression set needed to prove no collateral breakage.

## Report Requirements

Write `coordination/reports/TASK-104_REPORT.md` with:

- files changed
- implementation summary
- tests run and results
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence
- whether `a_share_limit_up_down` capability truth changed
- deviations from this handoff
- risks/follow-up tasks

