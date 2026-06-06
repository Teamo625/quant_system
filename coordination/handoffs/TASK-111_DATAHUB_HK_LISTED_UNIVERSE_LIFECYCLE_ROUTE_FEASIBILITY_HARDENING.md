# TASK-111: DataHub Hong Kong Listed-Universe and Lifecycle Route Feasibility Hardening

## Task ID

TASK-111

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2.5-P: DataHub Personal Trading Perfection Re-Review

## Context

TASK-110 is closed after accepted Review Agent verification. It added optional `source_route` truth to `DatasetName.INSTRUMENT_MASTER`, normalized HK stock reference records with `source_route="stock_hk_security_profile_em"`, tightened the HK instrument-master live classifier so route/provider tokens alone no longer downgrade repository defects to environment `SKIP`, kept default tests offline-safe, and recorded live-enabled PASS evidence.

`hk_universe_reference` remains conservative at `partial`. TASK-110 improved profile-route provenance, but Review explicitly left the phase-level HK universe breadth and dated lifecycle gaps open. The unresolved TASK-093 queue item is still:

- follow-up id: `hong_kong__hong_kong_capability_readiness__hk_universe_reference`
- capability: `hk_universe_reference`
- current status: `warn`
- disposition: `datahub_hardening`
- remaining theme: expand HK universe breadth and dated delisting/lifecycle metadata coverage where stable no-credential public routes expose source truth

Phase 2.5-P remains open because the DataHub readiness report still has unresolved non-pass follow-up queue items and `phase_closure_ready=False`.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-111_DATAHUB_HK_LISTED_UNIVERSE_LIFECYCLE_ROUTE_FEASIBILITY_HARDENING.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/ROADMAP.md`
- `coordination/reports/TASK-080_REPORT.md`
- `coordination/reviews/TASK-080_REVIEW.md`
- `coordination/reports/TASK-110_REPORT.md`
- `coordination/reviews/TASK-110_REVIEW.md`
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/datasets.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_hk_instrument_master_adapter.py`
- `tests/datahub/test_akshare_hk_instrument_master_live.py`
- `tests/datahub/test_datasets.py`
- `tests/datahub/test_source_capabilities.py`
- related DataHub tests only as needed

## Goal

Harden or truthfully constrain the remaining Hong Kong `hk_universe_reference` gaps beyond per-symbol current profile snapshots.

The task should improve one or more of:

- bounded current-listed HK stock universe/list-route coverage if a stable no-credential public route exists and can be represented as `DatasetName.INSTRUMENT_MASTER`
- explicit route/source provenance for profile, list, or lifecycle source facts so downstream consumers can distinguish route families without guessing
- deterministic reconciliation between current listed-universe/list rows and per-symbol profile rows for requested bounded samples
- listed/delisted/inactive status or dated lifecycle metadata only where a stable public route provides trustworthy source truth
- non-stock taxonomy handling for HK ETF, REIT, warrant, bond, index, or other instruments returned by public HK list routes
- duplicate/conflict handling across list/profile/lifecycle rows, symbols, security types, source routes, and source facts
- live-smoke classifier truthfulness for any newly selected HK list or lifecycle route family
- source capability/catalog wording so remaining public-source limitations are explicit and not silently passed

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
- `coordination/reports/TASK-111_REPORT.md`

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
3. Keep request breadth bounded and explicit. Do not silently perform unbounded full-market collection or historical backfill. If `symbols=None` is supported for a list route, the adapter must have an explicit bounded limit with deterministic ordering and tests.
4. Reject unsupported datasets, malformed payloads, route signature/call-compatibility defects, schema failures, and normalization errors as hard failures.
5. Classify only genuine network/proxy/DNS/TLS/upstream/source availability failures as live `SKIP`.
6. Audit live-unavailable classifiers for any selected HK list/lifecycle route. Route/function tokens and provider names must not by themselves convert payload/schema/normalization/signature defects into environment `SKIP`.
7. Preserve full-batch validation for caller-provided symbols: invalid requested symbols must not produce partial successful batches.
8. Keep non-stock handling truthful. If a public route returns ETF, REIT, warrant, bond, index, or other non-stock instruments outside the proven stock-reference contract, reject or classify them explicitly rather than inventing stock records.
9. For lifecycle metadata, use only source-backed status/date fields. Do not infer delisting dates from absence, latest-only rows, stale profile data, or price availability.
10. Keep default tests offline-safe. No default test may perform real network IO.
11. Do not add credentials, cookies, browser scraping, paid/private sources, Tushare fallback, scheduler/backfill orchestration, FeatureHub features, scanner logic, strategies, backtests, signals, portfolio/risk, AI, notification, UI, or automated trading.

## Public Route Exploration Boundary

Execution may inspect local AKShare callable availability and use deterministic fixtures for selected no-credential public HK reference/universe routes. Candidate route families may include locally available HK profile, spot/list, securities classification, or delisting/lifecycle functions, but only if their rows can be represented truthfully as `DatasetName.INSTRUMENT_MASTER` source facts.

Examples of route families to consider only if locally available and stable:

- HK stock profile routes such as `stock_hk_security_profile_em`
- HK current quote/list/spot routes that expose code/name/type/status fields
- HK delisting, suspension, lifecycle, or listed-company status routes if AKShare exposes no-credential callable source truth

If a route shape is unstable, latest-only without status truth, not symbol-compatible, not date-compatible, not stock-compatible, lacks trustworthy lifecycle dates, or is semantically outside HK universe reference, record the limitation and keep capability truth conservative.

## Offline Tests

Add or update focused offline tests covering the changed behavior:

- new list/lifecycle route normalization and source-route truth if implemented
- bounded `symbols=None` or explicit list-route behavior if implemented
- deterministic sorting and duplicate/conflict handling across list/profile/lifecycle routes
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

Write `coordination/reports/TASK-111_REPORT.md` with:

- files changed
- implementation summary
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence
- whether `hk_universe_reference` capability truth changed
- source route coverage and known HK universe/lifecycle limitations
- non-stock handling and batch/list behavior
- deviations from this handoff
- risks or follow-up tasks
