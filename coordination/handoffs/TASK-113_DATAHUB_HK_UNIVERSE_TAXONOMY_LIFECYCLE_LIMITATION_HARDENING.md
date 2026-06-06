# TASK-113: DataHub Hong Kong Universe Taxonomy and Lifecycle Limitation Hardening

## Task ID

TASK-113

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2.5-P: DataHub Personal Trading Perfection Re-Review

## Context

TASK-112 is closed after accepted Review Agent verification. It added a bounded HK listed-universe fallback path in `AkshareHKInstrumentMasterAdapter`: primary `stock_hk_spot_em`, fallback `sina_hk_stock_spot_page1`, both reconciled through per-symbol `stock_hk_security_profile_em`. Default tests stayed offline-safe and the gated live run passed.

`hk_universe_reference` remains conservative at `partial`. TASK-112 proves only bounded current-listed sample access, not full practical Hong Kong universe closure. The unresolved TASK-093 queue item is still:

- follow-up id: `hong_kong__hong_kong_capability_readiness__hk_universe_reference`
- capability: `hk_universe_reference`
- current status: `warn`
- disposition: `datahub_hardening`
- remaining theme: expand HK universe breadth, non-stock taxonomy truth, and dated delisting/lifecycle metadata coverage

Phase 2.5-P remains open because `build_default_personal_trading_readiness_report()` still reports overall `blocked`, phase closure `false`, and unresolved non-pass follow-up queue items.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-113_DATAHUB_HK_UNIVERSE_TAXONOMY_LIFECYCLE_LIMITATION_HARDENING.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/ROADMAP.md`
- `coordination/reports/TASK-110_REPORT.md`
- `coordination/reviews/TASK-110_REVIEW.md`
- `coordination/reports/TASK-111_REPORT.md`
- `coordination/reviews/TASK-111_REVIEW.md`
- `coordination/reports/TASK-112_REPORT.md`
- `coordination/reviews/TASK-112_REVIEW.md`
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/datasets.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_hk_instrument_master_adapter.py`
- `tests/datahub/test_akshare_hk_instrument_master_live.py`
- `tests/datahub/test_source_capabilities.py`
- related DataHub tests only as needed

## Goal

Harden or truthfully constrain the remaining Hong Kong `hk_universe_reference` gaps after TASK-112's bounded current-list live PASS.

The task should focus on the residual non-list-route limitations:

1. Prove source-backed HK non-stock taxonomy truth if a stable no-credential public route exposes ETF, REIT, warrant, bond, index, or other instrument classification that can be represented safely under `DatasetName.INSTRUMENT_MASTER`.
2. Prove source-backed listed/delisted/inactive status or dated lifecycle metadata if a stable no-credential public route exposes trustworthy HK listing, delisting, suspension, or inactive-date truth.
3. If no stable no-credential taxonomy or dated lifecycle route exists, make the limitation explicit in source capability/catalog wording and tests so bounded current-stock reference coverage is not silently treated as full HK universe closure-grade.

Do not mark `hk_universe_reference` as `covered` unless implementation and live evidence genuinely satisfy full practical public-source HK universe breadth, non-stock taxonomy truth, and dated lifecycle metadata for personal trading use. Conservative `partial` is expected unless materially stronger evidence is proven.

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
- `coordination/reports/TASK-113_REPORT.md`

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

1. Preserve the existing `DatasetName.INSTRUMENT_MASTER` contract unless a narrowly optional source-truth field is needed for route/category/lifecycle provenance.
2. Preserve `market="HK"`, canonical `00005.HK`-style symbols, deterministic sorting, schema validation, and source-truth normalization.
3. Keep request breadth bounded and explicit. Do not add unbounded full-market crawling or historical backfill.
4. Preserve route-distinct `source_route` truth for profile, Eastmoney list, Sina fallback, and any newly selected taxonomy/lifecycle route.
5. Reject malformed payloads, empty stock yields, unexpected symbols, duplicate conflicts, schema/normalization defects, and route signature/call-compatibility defects as hard failures.
6. Classify only genuine network/proxy/DNS/TLS/upstream/source availability failures as live `SKIP`. Provider or route names alone must not downgrade repository defects to environment unavailability.
7. Preserve full-batch validation for caller-provided symbols. Invalid requested symbols must not produce partial successful batches.
8. Keep non-stock handling truthful. Non-stock HK instruments may be represented only when source-backed classification is explicit and the existing contract can model the source fact without inventing stock records.
9. For lifecycle metadata, use only source-backed status/date fields. Do not infer listing, delisting, suspension, or inactive dates from absence, latest-only rows, stale profile data, quote availability, or price history gaps.
10. If route exploration finds no stable no-credential taxonomy/lifecycle path, update capability/source wording conservatively and document root-cause evidence in the report.
11. Keep default tests offline-safe. No default test may perform real network IO.
12. Do not add credentials, cookies, browser scraping, paid/private sources, Tushare fallback, scheduler/backfill orchestration, FeatureHub features, scanner logic, strategies, backtests, signals, portfolio/risk, AI, notification, UI, or automated trading.

## Public Route Exploration Boundary

Execution may inspect local AKShare callable availability and deterministic route shapes for no-credential HK reference, list, taxonomy, and lifecycle routes. Candidate route families may include locally available HK profile, spot/list, security-classification, delisting, suspension, lifecycle, or listed-company status functions, but only if their rows can be represented truthfully as `DatasetName.INSTRUMENT_MASTER` source facts.

If a route is unstable, latest-only without useful taxonomy/lifecycle truth, not symbol-compatible, not date-compatible, not stock/reference-compatible, lacks deterministic identifiers, lacks trustworthy lifecycle dates, or is semantically outside HK universe reference, record that limitation and keep capability truth conservative.

## Offline Tests

Add or update focused offline tests covering changed behavior:

- source-backed taxonomy normalization and route truth if a taxonomy route is implemented
- source-backed lifecycle/status/date normalization and route truth if a lifecycle route is implemented
- deterministic bounded behavior and duplicate/conflict handling across list/profile/taxonomy/lifecycle routes
- schema validation via `DatasetRegistry`
- malformed payload and missing-field failures
- unsupported or ambiguous non-stock instrument handling
- lifecycle/date fields not inferred from absence or quote availability
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
- assert source, market, canonical HK symbol shape, and any newly added route/provenance/taxonomy/lifecycle field
- fail on adapter/schema/normalization/signature defects
- skip only for genuine environment/upstream/source availability issues, with root-cause evidence

If live-enabled taxonomy or lifecycle proof fails or skips because of network, proxy, DNS, TLS, upstream, or public-source availability, the report must include root-cause evidence and feasible repository-level fixes attempted. Controller closure will require a fresh review cycle and may require a focused rework if the skip/failure is on a route selected as closure-relevant.

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

Write `coordination/reports/TASK-113_REPORT.md` with:

- files changed
- implementation summary
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence
- whether HK non-stock taxonomy truth is source-backed, constrained, or unsupported by proven no-credential routes
- whether HK listed/delisted/inactive lifecycle truth is source-backed, constrained, or unsupported by proven no-credential routes
- whether `hk_universe_reference` capability truth changed
- source route coverage and known HK universe/taxonomy/lifecycle limitations
- deviations from this handoff
- risks or follow-up tasks
