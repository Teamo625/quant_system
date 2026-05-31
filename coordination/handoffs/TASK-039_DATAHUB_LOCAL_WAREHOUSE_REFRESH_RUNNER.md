# TASK-039: DataHub Local Warehouse Refresh Runner

## Task ID

TASK-039

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

TASK-038 has been accepted, integrated, and closed by the controller. It completed narrow AKShare-backed China ETF exchange-traded `DAILY_BARS` coverage after explicit live-network rework, with live-enabled PASS evidence.

Phase 2 remains open. The next executable gap is local warehouse refresh behavior. The project already has:

- `SourceRequest`, `SourceResult`, and `fetch_source_result(...)` in `quant/datahub/source.py`
- local JSONL/JSON storage primitives in `quant/datahub/storage.py`
- refresh metadata and `DATA_QUALITY_REPORT` helpers in `quant/datahub/quality.py`

There is not yet a narrow local runner that ties these pieces together for one dataset refresh.

This task must remain local-only. It must not fetch real public sources in tests, must not add live tests, and must not implement scheduling or broad orchestration.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-039_DATAHUB_LOCAL_WAREHOUSE_REFRESH_RUNNER.md`

## Goal

Add a small deterministic DataHub local refresh runner that can execute one adapter/request pair, persist raw and curated records locally, write refresh metadata, and emit/persist `DATA_QUALITY_REPORT` records.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-039_REPORT.md`

Suggested implementation locations:

- `quant/datahub/refresh.py` or another narrowly named DataHub-local module
- `quant/datahub/__init__.py` only if exports are added
- `tests/datahub/test_refresh.py`
- `tests/datahub/test_storage.py` only if storage helper behavior changes
- `tests/datahub/test_quality.py` only if quality helper behavior changes

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

### 1. Single-request local refresh runner

Add a DataHub-local helper that accepts at least:

- a `SourceAdapter`
- a `SourceRequest`
- a `LocalStorage`
- optional `DatasetRegistry`
- optional `LocalRefreshQualityHelper`
- optional injectable clock / timestamp inputs as needed for deterministic tests

The helper should:

1. call `fetch_source_result(adapter, request, ...)`
2. obtain normalized records from the returned `SourceResult`
3. write normalized records to the curated layer using `LocalStorage.write_records(..., validate_schema=True)`
4. write raw records to the raw layer using the same deterministic JSONL convention
5. build and persist refresh metadata for the dataset
6. build and persist `DATA_QUALITY_REPORT` records for the refresh
7. return a small structured result object or mapping with paths, counts, status, and quality records

Keep the runner limited to one dataset/request per call.

### 2. Raw and curated persistence semantics

For this task, "raw" may be the adapter-normalized record payload captured from `SourceResult.normalized_records`; do not invent a new source-specific raw payload contract.

Curated writes must validate records against `DatasetRegistry.validate_record(...)`.

If curated validation fails:

- do not silently write invalid curated records
- return or raise a clear failure consistent with existing helper style
- write failure refresh metadata and/or quality records where feasible without hiding the exception

### 3. Refresh metadata and quality output

Use the existing `LocalRefreshQualityHelper` rather than duplicating quality logic.

The runner should create quality records covering at least:

- `record_count`
- `schema_validation`
- `metadata_written`

Persist quality records to `DatasetName.DATA_QUALITY_REPORT` using `LocalStorage.write_records(...)`.

Metadata should include source identity when available from `SourceRequest.source_id`, `SourceRequest.source_name`, or adapter `source_name`.

### 4. Local-only behavior

- This task must not perform real network calls in default tests.
- Do not add live tests.
- Test adapters must be local fixture adapters.
- Patch network connection helpers where useful to prove the runner itself does not open sockets.

### 5. Scope boundaries

Do not implement:

- real-source fetching beyond whatever fixture adapter tests call locally
- cron/scheduling
- broad multi-source orchestration
- retry/backoff frameworks
- dependency graphs
- incremental refresh window planning
- strategy, feature, scanner, AI, notification, UI, or automated trading logic

## Offline Tests

Add deterministic tests proving:

- a fixture adapter/request writes raw records, curated records, refresh metadata, and quality records
- returned refresh result contains dataset, source, record counts, written paths, and success status
- curated records validate through `DatasetRegistry`
- quality records validate through `DatasetRegistry.validate_record(DatasetName.DATA_QUALITY_REPORT, ...)`
- empty fixture results produce the configured record-count warning or failure behavior
- invalid fixture records fail schema validation and do not get silently persisted as curated success
- default behavior is offline-safe and does not open network connections

## Testing Requirements

Run focused tests, likely:

`python3 -m unittest tests/datahub/test_refresh.py`

Run regressions if touched:

`python3 -m unittest tests/datahub/test_storage.py`

`python3 -m unittest tests/datahub/test_quality.py`

`python3 -m unittest tests/datahub/test_source.py`

Run full DataHub default tests:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Live tests are forbidden for this task. Do not run or add `QUANT_SYSTEM_LIVE_TESTS=1` tests for TASK-039.

## Acceptance Criteria

The task is acceptable when:

- a narrow local refresh runner exists under `quant/datahub/**`
- one adapter/request refresh can persist raw records, curated records, metadata, and quality records locally
- deterministic offline tests cover success, empty-result, validation-failure, and offline-safety behavior
- default DataHub tests pass without live network access
- no remote fetch, future-phase module, strategy, scanner, AI, notification, UI, or automated trading logic is introduced
- report exists at `coordination/reports/TASK-039_REPORT.md`

## Report Path

`coordination/reports/TASK-039_REPORT.md`

## Review Path

`coordination/reviews/TASK-039_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-039_INTEGRATION.md`

## Out of Scope

Everything outside a narrow local DataHub one-request warehouse refresh runner is out of scope.
