# TASK-135 DataHub HK minute-bars feasibility and owner-waiver blocker disposition

## Role

5.3 Execution Window.

## Phase

Phase 2.5-P DataHub Personal Trading Perfection Re-Review.

## Context

TASK-134 is closed after accepted Review Agent verification. It completed the Hong Kong `datahub_hardening` readiness batch `hong_kong__datahub_hardening__hong_kong__batch_01` after focused scope rework, preserved default offline safety, recorded gated live PASS evidence, and kept HK capability truth conservative where public-source completeness remains unproven.

Phase 2.5-P remains open under `coordination/PHASE_GATE.md` because `build_default_personal_trading_readiness_report()` still reports `overall_status=blocked`, `phase_closure_ready=False`, status counts `pass=4`, `warn=5`, `blocked=1`, `fail=0`, and unresolved non-pass follow-up batches.

Controller read DataHub readiness `follow_up_batches`. TASK-131 through TASK-134 covered the A-share and Hong Kong `datahub_hardening` batches. The next adjacent readiness batch is:

- batch id: `hong_kong__owner_waiver_required__hong_kong_hong_kong_capability_readiness_hk_minute_bars__batch_01`
- disposition: `owner_waiver_required`
- recommended theme: `evaluate HK minute-bars source feasibility and contract design`

Included follow-up item:

- `hong_kong__hong_kong_capability_readiness__hk_minute_bars`

This is intentionally a single-item handoff. It is not merged with the next ETF/fund `datahub_hardening` batch because `hk_minute_bars` has owner-waiver/blocker disposition, optional capability status, no current dataset mapping, and a potential contract/source boundary distinct from ETF/fund hardening. This single-item dispatch is allowed by `coordination/PHASE_GATE.md` for owner-waiver blockers.

## Objective

Resolve the HK minute-bars readiness blocker as far as a DataHub execution window can without owner-provided paid/private data or downstream scope.

Execution must evaluate whether a stable no-credential public-source path can support Hong Kong `DatasetName.MINUTE_BARS` records under the existing generic minute-bar contract. Based on evidence, do one of:

- implement a minimal, bounded DataHub HK minute-bars source path with focused offline tests and gated live evidence if a stable public route exists and the existing contract is sufficient;
- add or tighten capability/catalog/readiness wording and tests to record why HK minute-bars must remain missing/owner-waiver-required if public route or contract feasibility is not proven;
- record concrete blocker evidence in the report if no repository change is feasible after investigation.

Do not promote `hk_minute_bars` unless implementation, tests, and live evidence prove a practical public-source/no-paid path. Do not treat this optional blocker as phase-complete without explicit Controller/owner disposition in a later closure decision.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-135_DATAHUB_HK_MINUTE_BARS_FEASIBILITY_BLOCKER_DISPOSITION.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/ROADMAP.md`
- `coordination/reports/TASK-042_REPORT.md`
- `coordination/reviews/TASK-042_REVIEW.md`
- `coordination/reports/TASK-050_REPORT.md`
- `coordination/reviews/TASK-050_REVIEW.md`
- `coordination/reports/TASK-078_REPORT.md`
- `coordination/reviews/TASK-078_REVIEW.md`
- `coordination/reports/TASK-096_REPORT.md`
- `coordination/reviews/TASK-096_REVIEW.md`
- `coordination/reports/TASK-134_REPORT.md`
- `coordination/reviews/TASK-134_REVIEW.md`
- `quant/datahub/datasets.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `quant/datahub/personal_readiness.py`
- existing A-share minute-bar adapter/tests as contract examples only
- related HK adapter tests only as needed

## Allowed Writes

Only:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py` only if a new/minimal adapter export is unavoidable
- `quant/datahub/datasets.py` only if a schema-compatible minute-bar clarification is unavoidable
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `quant/datahub/personal_readiness.py` only if the owner-waiver/blocker disposition text must be made more precise
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`
- `tests/datahub/test_personal_readiness.py`
- existing or new focused `tests/datahub/test_akshare_hk*minute*.py` files
- `coordination/reports/TASK-135_REPORT.md`

If a tightly related HK or minute-bar DataHub test must change, document the exact reason in the report. Do not touch unrelated DataHub domains.

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files other than `coordination/reports/TASK-135_REPORT.md`
- `coordination/reviews/**`
- `coordination/integrations/**`
- unrelated DataHub source-domain tests
- `quant/features/**`
- `quant/scanner/**`
- `quant/strategies/**`
- `quant/backtest/**`
- `quant/portfolio/**`
- `quant/notification/**`
- `quant/ai/**`
- `quant/ui/**`

Do not use credentials, tokens, cookies, browser session state, private account data, paid sources, or hidden default live network behavior.

Do not implement FeatureHub indicators, scanner ranking, strategies, backtests, portfolio/signal/risk logic, AI reports, notifications, UI, or automated trading.

## Implementation Requirements

- Reuse the existing `DatasetName.MINUTE_BARS` contract if HK public source facts fit it. Do not introduce a separate HK-only minute schema unless the existing contract is demonstrably insufficient and the change is minimal and backward compatible.
- Prefer bounded caller-provided symbol/date requests. Do not add full-market HK minute-bar collection, unbounded backfill, schedulers, local refresh orchestration, or downstream feature logic.
- Emit only source-backed facts. Do not invent OHLCV, trade timestamps, market suffixes, turnover, amount, source timestamps, or route provenance.
- Reject unsupported, ambiguous, ETF/fund/index, non-HK-stock, or malformed symbols clearly unless a route is proven to support them.
- Keep route/source truth explicit with `source_route` or equivalent provenance where records are emitted.
- If one requested symbol fails because of unsupported input or repository-side schema/normalization defects, fail clearly rather than returning partial success.
- Keep live-environment/source classifiers narrow. Network/proxy/DNS/TLS/upstream/source unavailability may skip; route-signature, call-compatibility, schema, normalization, duplicate-conflict, unbounded-fetch, or date-window defects must fail.
- Keep `hk_minute_bars` `MISSING` / owner-waiver-required unless a stable public-source path is implemented and proven. If feasibility remains unproven, tests should protect the conservative disposition from being silently relaxed.

## Tests

Required offline/default tests:

- `python3 -m unittest tests.datahub.test_source_capabilities`
- `python3 -m unittest tests.datahub.test_source_catalog`
- `python3 -m unittest tests.datahub.test_personal_readiness`
- any focused HK minute-bar tests added or changed
- any existing A-share minute-bar tests changed for shared contract compatibility, if applicable

If a live smoke is added or materially changed, it must be explicitly environment-gated and skipped by default. Run it once with live enabled when feasible:

- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v <focused HK minute-bar live test module>`

Report PASS, SKIP, or FAIL truthfully with root-cause evidence. If a live smoke skips because of network, proxy, DNS, TLS, upstream, or public-source availability, diagnose whether allowed code/tests/report can be improved instead of only documenting the skip.

## Completion Report

Write `coordination/reports/TASK-135_REPORT.md` with:

- files changed
- selected readiness batch id and included follow-up id
- HK minute-bar public-route feasibility investigation result
- whether the existing `DatasetName.MINUTE_BARS` contract is sufficient for proven HK source facts
- implementation summary, or explicit blocker/owner-waiver evidence if no implementation is feasible
- capability/catalog/readiness truth changes, if any
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence, or `SKIP - no live route implemented`
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

The task is complete when:

- HK minute-bars either has a bounded, validated, no-credential public DataHub path with gated live evidence, or the repository has stronger explicit blocker/owner-waiver evidence preventing silent overclaiming.
- Default tests remain offline-safe.
- Any live test remains skipped by default.
- Capability/catalog/readiness wording reflects only proven public-source truth.
- No paid/private source, inactive downstream module, or hidden live network behavior is introduced.
