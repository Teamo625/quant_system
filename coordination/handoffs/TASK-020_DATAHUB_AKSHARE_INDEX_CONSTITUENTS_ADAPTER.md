# TASK-020: DataHub AKShare Index Constituents Adapter

## Task ID

TASK-020

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

TASK-019 has been accepted and integrated. It completed the AKShare `SECTOR_MEMBERSHIP` adapter with strict live PASS evidence.

Phase 2 remains open. The next narrow executable source slice should extend index-domain coverage from `INDEX_DAILY_BARS` to `INDEX_CONSTITUENTS`, which is already part of current DataHub dataset contracts and source catalog planning.

This task must implement only `DatasetName.INDEX_CONSTITUENTS`.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-020_DATAHUB_AKSHARE_INDEX_CONSTITUENTS_ADAPTER.md`

## Goal

Implement a narrow AKShare-backed index constituents adapter for `DatasetName.INDEX_CONSTITUENTS`, with deterministic offline tests and mandatory gated live smoke coverage.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-020_REPORT.md`

Suggested implementation locations:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `quant/datahub/source_catalog.py` only if strict alignment assertion updates are necessary
- `tests/datahub/test_akshare_index_constituents_adapter.py`
- `tests/datahub/test_akshare_index_constituents_live.py`
- `tests/datahub/test_source_catalog.py` only if source-catalog expectations change

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

### 1. AKShare index constituents adapter

Add a narrow adapter for:

- source id: `akshare_cn_hk_public_family`
- source display name: `AKShare CN/HK Public Family`
- supported dataset in this task: `DatasetName.INDEX_CONSTITUENTS`
- market output baseline: `CN_A`

The adapter should:

- implement the existing `SourceAdapter` protocol
- use lazy/optional AKShare imports
- reject unsupported datasets clearly
- require exactly one index identifier in `symbols`
- accept canonical and source-native inputs when feasible, e.g.:
  - canonical: `000300.CN_INDEX`
  - source-native: `sh000300`
- normalize output records to `INDEX_CONSTITUENTS` contract fields:
  - `index_code`
  - `symbol`
  - `market`
  - `in_date`
  - optional `out_date`
  - optional `weight`
  - `source`
  - optional `source_ts`
  - `ingested_at`
  - `schema_version`
- use deterministic fallback policy where source lacks explicit membership dates:
  - set `in_date` to `1900-01-01`
  - keep `out_date` absent unless explicit valid value exists
- normalize `weight` only when valid; keep absent otherwise
- set `source=akshare_cn_hk_public_family`
- set `schema_version` from `DatasetRegistry`
- set `ingested_at` from injectable clock for deterministic tests
- support DataFrame-like payload and list-of-mapping payload
- fail clearly on malformed payload, missing required fields, invalid symbol/date/weight, and conflicting duplicates

### 2. Duplicate handling boundary

- benign exact duplicates may be deterministically deduplicated
- conflicting duplicates must remain hard-fail

### 3. Source catalog alignment

Do not add broad new claims. Only perform minimal source-catalog assertion updates if required by implemented stable behavior.

### 4. Offline tests

Add deterministic offline tests proving:

- adapter satisfies `SourceAdapter`
- `fetch_source_result(...)` records pass `DatasetRegistry.validate_record(...)`
- index identifier validation behavior is explicit (missing/empty/multiple/unsupported)
- code normalization and market assignment are stable
- `in_date` fallback and optional fields behave correctly
- duplicate boundary (benign dedupe vs conflict hard-fail) is preserved
- malformed payloads fail clearly
- default tests remain offline-safe

### 5. Mandatory live smoke test

Because TASK-020 is a real-source adapter task, gated live smoke is mandatory.

Add `tests/datahub/test_akshare_index_constituents_live.py` (or equivalent) that:

- is skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1`
- uses no credentials
- fetches a minimal bounded sample for one index
- validates at least one record via `DatasetRegistry.validate_record(...)`
- classifies environment/source unavailability as explicit `skipTest(...)`
- preserves adapter/schema issues as failures

If live-enabled run fails/skips due to network/proxy/DNS/TLS/upstream/source availability, report must include root-cause evidence and feasible repository-level fixes attempted.

## Do Not Implement

Do not implement:

- macro/policy/news/announcement adapters
- sector master/membership/daily bars behavior changes beyond existing TASK-017~019
- strategy/backtest/scanner/portfolio/notification/ai/ui logic

## Testing Requirements

Default tests must remain offline.

Run:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Run focused tests, likely:

`python3 -m unittest tests/datahub/test_akshare_index_constituents_adapter.py`

`python3 -m unittest -v tests/datahub/test_akshare_index_constituents_live.py`

Run related regressions if shared AKShare behavior is touched:

`python3 -m unittest tests/datahub/test_akshare_index_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_sector_membership_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_sector_master_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_sector_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_fund_nav_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_adapter.py`

If source-catalog tests are touched, run:

`python3 -m unittest tests/datahub/test_source_catalog.py`

Run gated live smoke when enabled:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_index_constituents_live.py`

## Acceptance Criteria

The task is acceptable when:

- AKShare `INDEX_CONSTITUENTS` adapter exists under `quant/datahub/**`
- scope remains limited to `DatasetName.INDEX_CONSTITUENTS`
- offline tests pass and remain deterministic
- duplicate boundary is covered and preserved
- default tests remain offline-safe
- gated live smoke exists and result is truthfully recorded
- no future-phase module contains new logic
- report exists at `coordination/reports/TASK-020_REPORT.md`

## Report Path

`coordination/reports/TASK-020_REPORT.md`

## Review Path

`coordination/reviews/TASK-020_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-020_INTEGRATION.md`

## Out of Scope

Everything outside a narrow DataHub `INDEX_CONSTITUENTS` adapter and tests is out of scope.
