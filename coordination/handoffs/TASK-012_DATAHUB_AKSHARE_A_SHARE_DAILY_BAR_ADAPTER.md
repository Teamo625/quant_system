# TASK-012: DataHub AKShare A-share Daily Bar Adapter

## Task ID

TASK-012

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

TASK-011 has been reviewed and integrated as accepted. It established the reusable source adapter contract foundation:

- `SourceRequest`
- `SourceResult`
- `normalize_source_payload(...)`
- `fetch_source_result(...)`
- offline contract tests through `DatasetRegistry.validate_record(...)`

TASK-011 review also left two non-blocking hardening follow-ups that should be addressed before real adapters multiply:

- `SourceRequest.symbols` should explicitly reject `str`/`bytes` so a single string is not split into characters.
- canonical `SourceResult` metadata should reject request/result mismatches beyond dataset/source-name, especially date range and symbols.

The next Phase 2 step is to introduce the first real source-family adapter in a narrow, reviewable slice. Use the prioritized no-credential catalog source family `akshare_cn_hk_public_family`, but implement only the A-share `daily_bars` dataset in this task.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-012_DATAHUB_AKSHARE_A_SHARE_DAILY_BAR_ADAPTER.md`

## Goal

Implement a small AKShare-backed A-share daily bar adapter seed that proves the real-source adapter path while keeping default tests fully offline and deterministic.

This task should produce one production adapter for `DatasetName.DAILY_BARS` only, plus contract hardening from TASK-011 review.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-012_REPORT.md`

Suggested implementation locations:

- `quant/datahub/source.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/adapters/akshare.py` or another clearly named DataHub adapter module
- `tests/datahub/test_source.py`
- `tests/datahub/test_akshare_adapter.py`
- `tests/datahub/test_akshare_live.py` or equivalent explicitly gated live smoke coverage; this is required for TASK-012

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
- `quant/features/**`
- `quant/strategies/**`
- `quant/backtest/**`
- `quant/scanner/**`
- `quant/portfolio/**`
- `quant/notification/**`
- `quant/ai/**`
- `quant/ui/**`

## Implementation Requirements

### 1. Contract hardening

Strengthen the TASK-011 contract foundation before adding the first real adapter:

- `SourceRequest` must reject `symbols` when it is a bare `str` or `bytes` value.
- Add tests proving a single string such as `"000001.SZ"` is rejected rather than converted to a character list.
- Extend canonical `SourceResult` metadata validation so `fetch_source_result(...)` rejects mismatches between the outer request and canonical result request for:
  - `start_date`
  - `end_date`
  - `symbols`
- Add deterministic failure-path tests for those metadata mismatches.
- Preserve existing `SourceAdapter` protocol shape unless a very small backward-compatible extension is unavoidable.

### 2. AKShare A-share daily bar adapter

Add a narrow adapter for the catalog source family:

- source id: `akshare_cn_hk_public_family`
- source name: `AKShare CN/HK Public Family`
- supported dataset in this task: `DatasetName.DAILY_BARS`
- market output: `CN`
- asset scope in this task: A-share stock daily bars only

The adapter should:

- implement the existing `SourceAdapter` protocol
- use lazy/optional AKShare access so importing `quant.datahub` and running default tests does not require AKShare to be installed
- allow dependency injection of a fake client/function for offline tests
- reject unsupported datasets with a clear exception
- require exactly one symbol for the first implementation, unless the implementation can safely and simply handle multiple symbols without increasing scope
- convert normalized symbols such as `600000.SH` / `000001.SZ` to the source-native AKShare symbol format when needed
- normalize AKShare/source-native rows into `DatasetName.DAILY_BARS` records compatible with `DatasetRegistry.validate_record(...)`
- include all required fields for `daily_bars`:
  - `symbol`
  - `market`
  - `trade_date`
  - `open`
  - `high`
  - `low`
  - `close`
  - `volume`
  - `amount`
  - `adj_factor`
  - `price_adjustment`
  - `source`
  - `ingested_at`
  - `schema_version`
- set `source` to `akshare_cn_hk_public_family`
- set `schema_version` from the registry/schema contract or explicitly to `v1` if no helper exists
- set `ingested_at` deterministically in offline tests, for example by injecting a clock or timestamp
- set `adj_factor` to `1.0` when the selected source payload does not provide an adjustment factor
- set `price_adjustment` consistently with the adapter request/default, for example `raw`, `qfq`, or `hfq`
- handle DataFrame-like payloads by converting them to records, but do not add pandas as a required dependency for default tests

The adapter may support a small list-of-mapping source-native fixture shape in tests, for example records with AKShare-style fields such as date/open/high/low/close/volume/amount. Keep any source-column mapping explicit and covered by tests.

### 3. Offline tests

Add deterministic offline tests using fake AKShare clients or fixture payloads. They must prove:

- adapter satisfies `SourceAdapter`
- `fetch_source_result(...)` works with the adapter and `SourceRequest`
- normalized `daily_bars` records pass `DatasetRegistry.validate_record(...)`
- symbol conversion preserves canonical output symbols
- unsupported datasets fail clearly
- missing symbols or invalid symbol shape fail clearly
- malformed source rows fail clearly enough for a future adapter author to debug
- default test discovery performs no live network calls

Use `socket.create_connection` patching where useful to protect default tests from accidental network access.

### 4. Mandatory live smoke test policy

Live smoke coverage is required for TASK-012. It must be implemented as an explicitly gated test and is acceptable only if all of the following are true:

- the test is explicitly named/marked as live
- it is skipped by default
- it requires `QUANT_SYSTEM_LIVE_TESTS=1`
- it does not require credentials
- it uses only AKShare/public network access
- it fetches a tiny bounded sample, such as one A-share symbol over a short historical date range

The required live smoke test must be skipped by default during normal test discovery unless the environment variable is set.

The execution window must create the live smoke test. It must run the live smoke command when the local environment explicitly enables it. If `QUANT_SYSTEM_LIVE_TESTS=1` is not set, AKShare is not installed, or public network access is unavailable, report that fact clearly in `coordination/reports/TASK-012_REPORT.md`; do not make default tests depend on live access.

## Do Not Implement

Do not implement:

- Tushare Pro adapters or token handling
- credentials, cookies, browser automation, or private account flows
- full-market ingestion jobs
- scheduled crawling
- local warehouse refresh orchestration
- raw payload persistence beyond tiny local unit-test fixtures
- Hong Kong stock adapters
- ETF/fund adapters
- index adapters
- macro/policy/news/announcement adapters
- data quality engine logic beyond existing validation reuse
- technical indicators
- stock selection rules
- strategy logic
- backtest logic
- AI explanation logic
- notification logic
- UI logic
- automated trading

## Testing Requirements

Default tests must be offline.

Run:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Also run focused tests for changed modules, likely:

`python3 -m unittest tests/datahub/test_source.py`

`python3 -m unittest tests/datahub/test_akshare_adapter.py`

Because TASK-012 is a real-source adapter task, add the gated live smoke test. When the environment explicitly enables it, run:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest tests/datahub/test_akshare_live.py`

If any command cannot run, report the exact reason in `coordination/reports/TASK-012_REPORT.md`.

## Acceptance Criteria

The task is acceptable when:

- TASK-011 review follow-ups for symbol-shape and canonical metadata mismatch are covered by tests
- an AKShare A-share `daily_bars` adapter exists under `quant/datahub/**`
- the adapter implements `SourceAdapter` without requiring AKShare during default imports/tests
- offline fixture-based tests prove `fetch_source_result(...) -> normalized records -> DatasetRegistry.validate_record(...)` succeeds
- unsupported dataset and malformed request/source-payload paths fail clearly
- default tests do not perform live network access
- the required live smoke test exists, is skipped by default, and is gated by `QUANT_SYSTEM_LIVE_TESTS=1`
- no future-phase module contains new logic
- the report file exists at `coordination/reports/TASK-012_REPORT.md`
- the report includes files changed, tests run, default network behavior, live smoke test implementation and run/skip status, deviations from the handoff, and follow-up risks/tasks

## Report Path

`coordination/reports/TASK-012_REPORT.md`

## Review Path

`coordination/reviews/TASK-012_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-012_INTEGRATION.md`

## Out of Scope

Everything outside DataHub contract hardening and the first narrow AKShare A-share daily bar adapter is out of scope.
