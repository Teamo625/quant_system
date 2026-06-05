# TASK-092 DataHub Source Health Metadata Hardening

## Role

5.3 Execution Window.

## Context

TASK-091 is closed after accepted Review Agent verification. It hardened public macro/policy depth for caller-parameterized macro indicators and policy route selectors, kept default tests offline-safe, and provided gated live smoke PASS evidence for both macro and policy paths.

Phase 2.5 remains open because DataHub is still not trading-usable under `coordination/ROADMAP.md`: source coverage metadata and source availability health remain `partial`, and paid index-weight live proof remains blocked by an unprovided paid credential. The paid path stays in blocked backlog under TASK-059 and must not be promoted in this task.

This task continues the TASK-071 DataHub hardening queue in the source-health / failure-diagnostics domain. It must not reopen FeatureHub, Scanner, StrategyLab, BacktestEngine, portfolio, signal, risk, AI, notification, UI, or automated trading work.

## Objective

Harden DataHub's local source-health metadata and failure diagnostics so source availability, fetch outcomes, and failure states are recorded in a standardized, offline-testable form that downstream controller decisions and future UI/status surfaces can consume without parsing ad hoc exception text.

The implementation should make existing local refresh and quality-report plumbing more trading-usable by adding first-class source-health records within the existing DataHub quality/metadata layer, including deterministic classifications for success, empty result, schema failure, fetch failure, metadata-write failure, and unsupported request/configuration failure.

This task does not require a new real-source adapter, live-network smoke, paid/private source access, full-market refresh scheduling, background jobs, FeatureHub calculations, scanner ranking, strategy/backtest logic, portfolio/signal/risk, AI reports, notification, UI, or automated trading.

## Allowed Writes

Only:

- `quant/datahub/quality.py`
- `quant/datahub/refresh.py`
- `quant/datahub/source.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_quality.py`
- `tests/datahub/test_refresh.py`
- `tests/datahub/test_source.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`
- `coordination/reports/TASK-092_REPORT.md`

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files
- `coordination/reviews/**`
- `coordination/integrations/**`
- real-source adapters under `quant/datahub/adapters/`
- live test files
- dataset contracts unless unavoidable; prefer the existing `DATA_QUALITY_REPORT` contract if it can carry the standardized records through structured `details`
- `quant/features/`
- `quant/scanner/`
- `quant/strategies/`
- `quant/backtest/`
- `quant/portfolio/`
- `quant/notification/`
- `quant/ai/`
- `quant/ui/`

Do not use credentials, cookies, tokens, browser session state, or private account data.

## Implementation Requirements

- Add a deterministic local source-health record builder or equivalent helper under the DataHub quality/source layer.
- Keep records compatible with the existing `DatasetName.DATA_QUALITY_REPORT` schema unless a clearly justified minimal contract extension is necessary.
- Standardize source-health `check_name` and `details` fields so they include, where available:
  - `source_id`
  - `source_name`
  - `source_catalog_entry_id`
  - requested dataset
  - requested date range
  - requested symbols count and a bounded symbols preview
  - normalized record count
  - fetch status / availability status
  - failure category
  - failure message, bounded and sanitized
  - whether the failure is operator-actionable, upstream/network-like, schema/data-quality-like, or request/configuration-like
  - fetched/started/completed timestamps
- Define a small, stable set of failure categories. At minimum cover:
  - success
  - empty_result
  - schema_validation_failed
  - fetch_failed
  - unsupported_request
  - metadata_write_failed
  - persistence_failed
- Do not classify route-name-bearing adapter argument/signature errors as upstream live unavailability. They should remain request/configuration or implementation failures.
- Extend `run_local_warehouse_refresh(...)` so refresh attempts that fail before normalized records are persisted can still produce standardized failure metadata and source-health quality records where feasible.
- Preserve existing success, empty warn, empty fail, invalid curated-record, and metadata-written behavior.
- Avoid broad exception swallowing: if the refresh should fail today, it may still raise after recording standardized metadata/quality evidence.
- Update `source_capabilities.py` and/or `source_catalog.py` only if the implemented source-health records materially improve capability truth. Keep `source_availability_health` conservative unless the task proves a reusable, standardized local health path.
- Do not promote unrelated source capabilities.

## Tests

Required offline/default tests:

- `python3 -m unittest tests/datahub/test_quality.py`
- `python3 -m unittest tests/datahub/test_refresh.py`
- `python3 -m unittest tests/datahub/test_source.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`
- `python3 -m unittest tests/datahub/test_source_catalog.py`

Recommended broader offline check if focused tests pass:

- `python3 -m unittest discover tests/datahub`

Do not run live-enabled tests and do not set `QUANT_SYSTEM_LIVE_TESTS=1`. If live test files are encountered in discovery, they must remain skipped by default.

## Completion Report

Write `coordination/reports/TASK-092_REPORT.md` with:

- files changed
- tests run
- default network behavior
- live-enabled result, which should be `SKIP` because this is local-only and live tests are not permitted
- the standardized source-health categories added
- whether source capability/catalog truth changed
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

The task is complete when:

- source-health / availability outcome records are standardized and schema-valid through the existing DataHub quality layer or a justified minimal contract extension
- refresh success, empty-result, schema-failure, fetch-failure, and metadata-write/persistence failure paths produce deterministic health evidence where feasible
- default tests remain offline-safe
- no live network access, credentials, or real-source adapter changes are introduced
- capability metadata remains conservative and reflects only the implemented source-health breadth
