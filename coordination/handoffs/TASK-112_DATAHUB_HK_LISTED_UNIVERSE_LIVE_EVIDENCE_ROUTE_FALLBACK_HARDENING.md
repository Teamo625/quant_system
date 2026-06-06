# TASK-112: DataHub Hong Kong Listed-Universe Live Evidence and Route Fallback Hardening

## Task ID

TASK-112

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2.5-P: DataHub Personal Trading Perfection Re-Review

## Context

TASK-111 is closed after accepted Review Agent verification. It added a bounded `symbols=None` HK current-listed list path using `stock_hk_spot_em` plus per-symbol `stock_hk_security_profile_em` reconciliation, kept request breadth bounded, preserved default offline safety, and kept `hk_universe_reference` conservative at `partial`.

The TASK-111 live run was PASS overall because the profile-route smoke passed, but the new bounded current-list smoke skipped with genuine upstream/environment unavailability:

- route: `stock_hk_spot_em`
- evidence: `ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))`

Review accepted TASK-111 and did not require same-task repository rework, but Phase 2.5-P cannot close because `hk_universe_reference` still lacks full-market HK universe breadth, stable non-stock taxonomy coverage, and dated delisting/lifecycle metadata proof. This task continues the same unresolved TASK-093 queue item:

- follow-up id: `hong_kong__hong_kong_capability_readiness__hk_universe_reference`
- capability: `hk_universe_reference`
- current status: `warn`
- disposition: `datahub_hardening`
- remaining theme: prove a stable no-credential public HK listed-universe/list route if feasible, or record a truthful public-source limitation without promoting capability truth

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-112_DATAHUB_HK_LISTED_UNIVERSE_LIVE_EVIDENCE_ROUTE_FALLBACK_HARDENING.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/ROADMAP.md`
- `coordination/reports/TASK-111_REPORT.md`
- `coordination/reviews/TASK-111_REVIEW.md`
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/datasets.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_hk_instrument_master_adapter.py`
- `tests/datahub/test_akshare_hk_instrument_master_live.py`
- `tests/datahub/test_source_capabilities.py`
- related DataHub tests only as needed

## Goal

Diagnose and harden the HK bounded current-listed universe/list route evidence path after TASK-111's live upstream skip.

The task should do one of the following, in priority order:

1. Prove a stable no-credential public HK current-listed stock universe/list route with gated live PASS evidence, bounded request behavior, deterministic ordering, schema-valid `DatasetName.INSTRUMENT_MASTER` records, and explicit `source_route` truth.
2. If `stock_hk_spot_em` is intermittently unavailable but another locally available no-credential public route is stable and semantically compatible, add a tightly scoped bounded fallback route with offline tests and gated live evidence.
3. If no stable public list route can be proven, keep implementation conservative and update capability/source wording or tests only as needed so the limitation is explicit and not silently treated as closure-grade.

Do not mark `hk_universe_reference` as `covered` unless full practical HK universe breadth, non-stock taxonomy truth, and dated lifecycle metadata are genuinely source-backed and live-proven. Conservative `partial` is expected unless the evidence is materially stronger than TASK-111.

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
- `coordination/reports/TASK-112_REPORT.md`

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

1. Preserve the existing `DatasetName.INSTRUMENT_MASTER` contract unless a narrowly optional source-truth field is required for route/category/list provenance.
2. Preserve `market="HK"`, canonical `00005.HK`-style symbols, deterministic sorting, schema validation, and source-truth normalization.
3. Keep list/universe requests bounded. Do not add unbounded full-market crawling or historical backfill.
4. If a fallback route is added, keep route-distinct `source_route` truth so downstream consumers can distinguish `stock_hk_spot_em`, profile, and fallback route families.
5. Reject malformed payloads, empty stock yields, unexpected symbols, duplicate conflicts, schema/normalization defects, and route signature/call-compatibility defects as hard failures.
6. Classify only genuine network/proxy/DNS/TLS/upstream/source availability failures as live `SKIP`. Provider or route names alone must not downgrade repository defects to environment unavailability.
7. Preserve full-batch validation for caller-provided symbols. Invalid requested symbols must not produce partial successful batches.
8. Keep non-stock handling truthful. ETF, REIT, warrant, bond, index, or other non-stock instruments returned by a public list route must be explicitly rejected, skipped only after source-backed classification, or modeled only if the existing stock-reference contract truthfully supports them.
9. For lifecycle metadata, use only source-backed status/date fields. Do not infer delisting dates from absence, latest-only rows, stale profile data, or price availability.
10. Keep default tests offline-safe. No default test may perform real network IO.
11. Do not add credentials, cookies, browser scraping, paid/private sources, Tushare fallback, scheduler/backfill orchestration, FeatureHub features, scanner logic, strategies, backtests, signals, portfolio/risk, AI, notification, UI, or automated trading.

## Public Route Exploration Boundary

Execution may inspect local AKShare callable availability and deterministic route shapes for no-credential HK reference/list routes. Candidate route families may include locally available HK spot/list/profile/classification functions, but only if their rows can be represented truthfully as `DatasetName.INSTRUMENT_MASTER` source facts.

If a route is unstable, latest-only without useful list truth, not symbol-compatible, not stock-compatible, lacks deterministic identifiers, lacks trustworthy lifecycle dates, or is semantically outside HK universe reference, record that limitation in the report and keep capability truth conservative.

## Offline Tests

Add or update focused offline tests covering the changed behavior:

- list-route live classifier regression for the TASK-111 `RemoteDisconnected` skip shape and hard-fail repository defect shapes
- fallback route normalization and source-route truth if a fallback is implemented
- deterministic bounded `symbols=None` ordering and duplicate/conflict handling
- schema validation via `DatasetRegistry`
- malformed payload and missing-field failures
- empty stock-yield failure
- unsupported non-stock instrument handling
- route signature/call-compatibility failures remaining hard failures
- source capability/catalog assertions if metadata changes

## Mandatory Live Smoke

Because this is real-source DataHub hardening, run a gated live smoke:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_instrument_master_live.py`

The live test must:

- skip by default unless `QUANT_SYSTEM_LIVE_TESTS=1`
- use no credentials
- validate at least one live `INSTRUMENT_MASTER` record through `DatasetRegistry` when public routes are reachable
- assert source, market, canonical HK symbol shape, and route/provenance fields
- fail on adapter/schema/normalization/signature defects
- skip only for genuine environment/upstream/source availability issues, with root-cause evidence

If the live-enabled list-route smoke fails or skips again because of network, proxy, DNS, TLS, upstream, or public-source availability, the report must include root-cause evidence, any feasible repository-level fixes attempted, and a recommendation on whether the route should remain non-closure-grade or whether another rework is justified.

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

Write `coordination/reports/TASK-112_REPORT.md` with:

- files changed
- implementation summary
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence
- whether the bounded HK listed-universe route is now live-pass-proven
- whether `hk_universe_reference` capability truth changed
- source route coverage and known HK universe/list/lifecycle limitations
- fallback-route feasibility decision, if any
- non-stock handling and batch/list behavior
- deviations from this handoff
- risks or follow-up tasks
