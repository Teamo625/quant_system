# TASK-025: DataHub Local Refresh Metadata and Quality Baseline

## Task ID

TASK-025

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

TASK-024 has been accepted and integrated. It completed the first AKShare-backed China macro slice for `MACRO_INDICATOR_MASTER` and `MACRO_OBSERVATIONS`, including the `is_preliminary` rework and closure-ready live-enabled PASS evidence.

Phase 2 remains open. The next narrow executable slice is the local warehouse refresh metadata and data-quality baseline. The source catalog already includes `local_data_quality_engine` for `DatasetName.DATA_QUALITY_REPORT`, with no live network requirement.

This task must implement only local DataHub refresh metadata and quality-report behavior. It must not fetch remote market data.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-025_DATAHUB_LOCAL_REFRESH_QUALITY_BASELINE.md`

## Goal

Add a small deterministic DataHub-local helper for writing refresh metadata and producing `DATA_QUALITY_REPORT` records from local records and schema validation results.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-025_REPORT.md`

Suggested implementation locations:

- `quant/datahub/quality.py` or another narrowly named DataHub-local module
- `quant/datahub/storage.py` only if small metadata IO helpers are needed
- `quant/datahub/__init__.py` only if exports are added
- `tests/datahub/test_quality.py`
- `tests/datahub/test_storage.py` only if storage helper behavior changes
- `tests/datahub/test_source_catalog.py` only if local quality catalog assertions are aligned

## Forbidden Files

The execution window must not modify:

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
- `quant/strategies/**`
- `quant/backtest/**`
- `quant/scanner/**`
- `quant/portfolio/**`
- `quant/notification/**`
- `quant/ai/**`
- `quant/ui/**`

## Implementation Requirements

### 1. Local refresh metadata

Add a small local DataHub helper that can build and optionally persist deterministic refresh metadata for a dataset.

The metadata should include at least:

- dataset name
- layer, such as `raw` or `curated`
- source id or source name when provided
- record count
- status, such as `success`, `warning`, or `failed`
- started/completed or refreshed timestamp values from an injectable clock
- schema version from `DatasetRegistry`
- optional details object for local diagnostics

Use `LocalStorage.write_metadata(...)` / `read_metadata(...)` where persistence is needed. Keep the file format JSON and deterministic.

### 2. Data quality report records

Add a helper that emits records compatible with `DatasetName.DATA_QUALITY_REPORT`.

At minimum, support these local checks:

- `record_count`: pass when records are present, warn or fail according to an explicit parameter when empty
- `schema_validation`: pass when all records validate through `DatasetRegistry.validate_record(...)`, fail when any record has validation issues
- `metadata_written`: pass when refresh metadata is written successfully, if this helper performs persistence

Each quality record must include:

- `dataset`
- `market`
- `trade_date`
- `check_name`
- `status`
- `severity`
- `details`
- `created_at`
- `source=local_data_quality_engine`
- optional `source_ts`
- `ingested_at`
- `schema_version`

Use an injectable clock and explicit `market` / `trade_date` inputs so tests remain deterministic.

### 3. Local-only behavior

- This task must not perform real network calls.
- Do not add live tests.
- Default tests must remain offline-safe.
- Tests should patch network connection helpers where useful to prove the quality helper is local-only.

### 4. Scope boundaries

Do not implement:

- remote source fetching
- policy document adapters
- feature calculations
- scanner ranking
- trading signals
- AI reports
- UI dashboards
- broad orchestration or scheduling

This is a small local baseline only. Future tasks may expand refresh orchestration, but this task should produce a reviewable foundation.

## Offline Tests

Add deterministic tests proving:

- refresh metadata can be built with an injectable clock
- refresh metadata can be persisted and read back through `LocalStorage`
- quality report records validate through `DatasetRegistry.validate_record(DatasetName.DATA_QUALITY_REPORT, ...)`
- non-empty valid records produce pass status
- empty record collections produce the configured warning/failure behavior
- invalid dataset records produce a schema-validation failure quality record with useful details
- default behavior is offline-safe and does not open network connections

## Testing Requirements

Run focused tests, likely:

`python3 -m unittest tests/datahub/test_quality.py`

Run storage regression tests if `LocalStorage` is touched:

`python3 -m unittest tests/datahub/test_storage.py`

Run dataset/schema and source-catalog regressions if relevant:

`python3 -m unittest tests/datahub/test_datasets.py`

`python3 -m unittest tests/datahub/test_source_catalog.py`

Run full DataHub default tests:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Live tests are forbidden for this task. Do not run or add `QUANT_SYSTEM_LIVE_TESTS=1` tests for TASK-025.

## Acceptance Criteria

The task is acceptable when:

- local refresh metadata helper exists under `quant/datahub/**`
- `DATA_QUALITY_REPORT` records are produced and validate against `DatasetRegistry`
- metadata persistence, record-count checks, schema-validation checks, and offline safety are covered by deterministic tests
- default DataHub tests pass without live network access
- no remote fetch, future-phase module, strategy, scanner, AI, notification, or UI logic is introduced
- report exists at `coordination/reports/TASK-025_REPORT.md`

## Report Path

`coordination/reports/TASK-025_REPORT.md`

## Review Path

`coordination/reviews/TASK-025_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-025_INTEGRATION.md`

## Out of Scope

Everything outside a local DataHub refresh metadata and quality-report baseline is out of scope.
