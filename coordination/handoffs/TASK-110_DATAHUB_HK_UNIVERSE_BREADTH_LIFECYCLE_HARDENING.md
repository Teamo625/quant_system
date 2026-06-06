# TASK-110: DataHub Hong Kong Universe Breadth and Lifecycle Hardening

## Task ID

TASK-110

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2.5-P: DataHub Personal Trading Perfection Re-Review

## Context

TASK-109 is closed after accepted Review Agent verification. It expanded A-share `DatasetName.MAJOR_ACTIVITY_EVENTS` from single-day block-trade detail coverage to bounded date-window detail plus symbol-date summary coverage with explicit `source_route` truth, kept default tests offline-safe, recorded live-enabled PASS evidence, and kept `a_share_major_activity_events` conservative at `partial`.

Phase 2.5-P remains open because `build_default_personal_trading_readiness_report()` still reports overall `blocked`, phase closure `false`, and unresolved structured follow-up queue items.

The next unclosed executable TASK-093 queue item is:

- follow-up id: `hong_kong__hong_kong_capability_readiness__hk_universe_reference`
- capability: `hk_universe_reference`
- current status: `warn`
- disposition: `datahub_hardening`
- next handoff theme: expand HK universe breadth and dated delisting/lifecycle metadata coverage

Existing TASK-080 work proved caller-provided multi-symbol HK stock reference access through no-credential public AKShare routes. Capability truth remains `partial` because full-market HK universe breadth, non-stock taxonomy coverage, and dated delisting/lifecycle metadata are not yet proven.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-110_DATAHUB_HK_UNIVERSE_BREADTH_LIFECYCLE_HARDENING.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/ROADMAP.md`
- `coordination/reports/TASK-080_REPORT.md`
- `coordination/reviews/TASK-080_REVIEW.md`
- `coordination/reports/TASK-109_REPORT.md`
- `coordination/reviews/TASK-109_REVIEW.md`
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_hk_instrument_master_adapter.py`
- `tests/datahub/test_akshare_hk_instrument_master_live.py`
- related DataHub tests only as needed

## Goal

Harden Hong Kong `hk_universe_reference` coverage beyond caller-provided stock-reference batches where stable no-credential public routes expose source truth.

The task should improve one or more of:

- HK universe breadth across current listed HK stock reference routes, without silently collecting unbounded full-market data unless a bounded/requested route is explicitly designed and tested
- source-route and source-family provenance for `DatasetName.INSTRUMENT_MASTER` records if current output cannot distinguish profile/list routes truthfully
- security-type, listing-status, exchange, board, currency, name, industry, lot-size, or profile-field source truth where public rows expose it
- dated lifecycle metadata only where a stable public route provides trustworthy listing/delisting/status dates
- deterministic rejection or classification of non-stock HK instruments when they are outside the proven stock-reference contract
- duplicate/conflict handling across route rows, requested symbols, security types, and source facts
- live-smoke classifier truthfulness for selected HK universe/reference route families
- source capability/catalog wording so remaining public-source limitations are explicit

Do not mark `hk_universe_reference` as `covered` unless implementation and live evidence genuinely satisfy full practical public-source HK universe breadth and lifecycle metadata for personal trading use. Conservative `partial` is expected unless proven otherwise.

## Allowed Files

Execution may create or modify only:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/datasets.py` only if a narrowly compatible optional source-truth field is required
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py` only if implemented source coverage makes catalog truth inconsistent
- `tests/datahub/test_akshare_hk_instrument_master_adapter.py`
- `tests/datahub/test_akshare_hk_instrument_master_live.py`
- `tests/datahub/test_datasets.py` only if `datasets.py` changes
- `tests/datahub/test_source_capabilities.py` if capability wording/status changes
- `tests/datahub/test_source_catalog.py` if catalog truth changes
- `coordination/reports/TASK-110_REPORT.md`

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

1. Preserve the existing `DatasetName.INSTRUMENT_MASTER` contract unless a narrowly optional source-truth field is needed for route/category provenance.
2. Preserve `market="HK"`, canonical HK symbols, deterministic sorting, schema validation, and source-truth normalization.
3. Keep request breadth bounded and explicit. Do not silently perform unbounded full-market collection or full-history lifecycle reconstruction.
4. Reject unsupported datasets, invalid symbols, malformed payloads, route signature/call-compatibility defects, schema failures, and normalization errors as hard failures.
5. Classify only genuine network/proxy/DNS/TLS/upstream/source availability failures as live `SKIP`.
6. Audit existing HK instrument-master live-unavailable classifiers. Route/function tokens and provider names must not by themselves convert repository-side payload/schema/normalization/signature defects into environment `SKIP`.
7. Preserve full-batch validation: invalid requested symbols must not produce partial successful batches.
8. Keep non-stock handling truthful. If a public route returns ETF, warrant, bond, REIT, index, or other non-stock instruments outside the proven contract, reject or classify them explicitly rather than inventing stock records.
9. Keep default tests offline-safe. No default test may perform real network IO.
10. Do not add credentials, cookies, browser scraping, paid/private sources, Tushare fallback, scheduler/backfill orchestration, FeatureHub features, scanner logic, strategies, backtests, signals, portfolio/risk, AI, notification, UI, or automated trading.

## Public Route Exploration Boundary

Execution may inspect local AKShare callable availability and use deterministic fixtures for selected no-credential public HK reference/universe routes. Candidate route families may include locally available AKShare HK profile, spot/list, or delisting/lifecycle routes, but only if their rows can be represented truthfully as `DatasetName.INSTRUMENT_MASTER` source facts.

If a route shape is unstable, latest-only, not symbol-compatible, not date-compatible, not stock-compatible, lacks lifecycle dates, or is semantically outside HK universe reference, record the limitation and keep capability truth conservative.

## Offline Tests

Add or update focused offline tests covering the changed behavior:

- new route/source provenance or lifecycle-field normalization
- bounded symbol-list or explicit route behavior
- deterministic sorting and duplicate/conflict handling
- schema validation via `DatasetRegistry`
- malformed payload and missing-field failures
- invalid symbol / unsupported non-stock instrument failures
- route signature/call-compatibility failures remaining hard failures
- live classifier regression coverage for any newly classified route or upstream token
- source capability/catalog assertions if metadata changes

## Mandatory Live Smoke

Because this is real-source DataHub hardening, run a gated live smoke:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_instrument_master_live.py`

The live test must:

- skip by default unless `QUANT_SYSTEM_LIVE_TESTS=1`
- use no credentials
- validate at least one live `INSTRUMENT_MASTER` record through `DatasetRegistry` when public routes are reachable
- assert source, market, canonical HK symbol shape, and any newly added route/provenance/lifecycle field
- fail on adapter/schema/normalization/signature defects
- skip only for genuine environment/upstream/source availability issues, with root-cause evidence

If the live-enabled run fails or skips because of network, proxy, DNS, TLS, upstream, or public-source availability, the report must include root-cause evidence and feasible repository-level fixes attempted. Controller closure will require a fresh review cycle and may require a follow-up rework under `AGENTS.md`.

## Required Test Commands

Run:

- `python3 -m unittest tests/datahub/test_akshare_hk_instrument_master_adapter.py`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_hk_instrument_master_live.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`

Run if touched:

- `python3 -m unittest tests/datahub/test_source_catalog.py`
- `python3 -m unittest tests/datahub/test_datasets.py`

Run gated live:

- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_instrument_master_live.py`

If shared AKShare behavior changes, run the narrow related regression set needed to prove no collateral breakage.

## Report Requirements

Write `coordination/reports/TASK-110_REPORT.md` with:

- files changed
- implementation summary
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence
- whether `hk_universe_reference` capability truth changed
- source route coverage and known HK universe/lifecycle limitations
- non-stock handling and batch behavior
- deviations from this handoff
- risks or follow-up tasks
