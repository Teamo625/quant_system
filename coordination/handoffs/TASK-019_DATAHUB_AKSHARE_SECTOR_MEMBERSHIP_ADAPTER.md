# TASK-019: DataHub AKShare Sector Membership Adapter

## Task ID

TASK-019

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

TASK-018 has been accepted and integrated. It completed the AKShare `SECTOR_MASTER` adapter and resolved the live duplicate canonical `sector_id` blocker.

Phase 2 remains open. The next narrow executable source slice is sector membership coverage, which is required by current contracts and source-catalog scope.

This task should implement only `DatasetName.SECTOR_MEMBERSHIP`.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-019_DATAHUB_AKSHARE_SECTOR_MEMBERSHIP_ADAPTER.md`

## Goal

Implement a narrow AKShare-backed sector membership adapter for `DatasetName.SECTOR_MEMBERSHIP`, with deterministic offline tests and mandatory gated live smoke coverage.

This task must not expand into index constituents, macro/policy/news, strategy, scanner, or future-phase modules.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-019_REPORT.md`

Suggested implementation locations:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `quant/datahub/source_catalog.py` only if strict catalog assertion alignment is required
- `tests/datahub/test_akshare_sector_membership_adapter.py`
- `tests/datahub/test_akshare_sector_membership_live.py`
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

### 1. AKShare sector membership adapter

Add a narrow adapter for:

- source id: `akshare_cn_hk_public_family`
- source display name: `AKShare CN/HK Public Family`
- supported dataset in this task: `DatasetName.SECTOR_MEMBERSHIP`
- market output baseline: `CN_A`

The adapter should:

- implement the existing `SourceAdapter` protocol
- use lazy/optional AKShare imports
- reject unsupported datasets clearly
- accept exactly one typed sector identifier in `symbols`, with stable format:
  - `INDUSTRY:<sector_name>`
  - `CONCEPT:<sector_name>`
- route industry/concept membership fetch by sector type
- normalize records to `SECTOR_MEMBERSHIP` schema fields:
  - `sector_id`
  - `symbol`
  - `market`
  - `in_date`
  - optional `out_date`
  - `source`
  - optional `source_ts`
  - `ingested_at`
  - `schema_version`
- set `sector_id` canonical form to typed identifier (`INDUSTRY:<name>` / `CONCEPT:<name>`)
- normalize `symbol` to canonical code format currently used in DataHub stock scope when feasible; if only source-native code is available, keep deterministic and documented normalization
- default `in_date` policy in this first slice:
  - if source contains explicit entry date, parse and use it
  - otherwise use deterministic fallback date `1900-01-01` (as “membership exists but in-date unavailable” baseline) and keep this behavior tested/documented
- keep `out_date` absent unless source provides valid explicit value
- set `source=akshare_cn_hk_public_family`
- set `schema_version` from `DatasetRegistry`
- set `ingested_at` via injectable clock for deterministic tests
- support DataFrame-like payload and list-of-mapping payload
- fail clearly on malformed payload, missing required fields, invalid symbol/date values, and conflicting duplicate membership rows

### 2. Duplicate handling boundary

Membership payloads may contain repeat rows. Handle with strict boundary:

- benign exact duplicates (same canonical `sector_id`, `symbol`, date fields) may be deterministically de-duplicated
- conflicting duplicates (same `sector_id` + `symbol` but conflicting date semantics) must remain hard-fail

### 3. Source catalog alignment

The catalog already includes `DatasetName.SECTOR_MEMBERSHIP` under `akshare_cn_hk_public_family` and `InformationDomain.INDUSTRY_CONCEPT_SECTOR`.

Do not add broad new claims. If any catalog assertion update is necessary, keep it minimal and add tests.

### 4. Offline tests

Add deterministic offline tests proving:

- adapter satisfies `SourceAdapter`
- `fetch_source_result(...)` produces records that pass `DatasetRegistry.validate_record(...)`
- typed identifier routing works for `INDUSTRY` and `CONCEPT`
- identifier validation failures are explicit (missing/empty/untyped/unsupported/multiple)
- symbol normalization and market assignment are stable
- `in_date` explicit parse + fallback behavior are correct
- optional `out_date`/`source_ts` behavior is correct
- benign duplicates are deduped deterministically
- conflicting duplicates are hard-fail
- malformed payload rows fail clearly
- default tests do not perform network access

Use `socket.create_connection` patching where useful.

### 5. Mandatory live smoke test

Because TASK-019 is a real-source adapter task, a gated live smoke test is mandatory.

Add `tests/datahub/test_akshare_sector_membership_live.py` (or equivalent) that:

- is skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1`
- uses no credentials
- fetches a small bounded sample via one typed sector identifier
- validates at least one record with `DatasetRegistry.validate_record(...)`
- classifies environment/source unavailability as explicit `skipTest(...)`
- preserves adapter/schema bugs as failures

If live-enabled run fails/skips due to network/proxy/DNS/TLS/upstream/source availability, report must include root-cause evidence and feasible repository-level fixes attempted.

## Do Not Implement

Do not implement:

- index constituents adapter
- broad sector master rework beyond current TASK-018 behavior
- sector daily bars rework beyond current TASK-017 behavior
- macro/policy/news/announcement adapters
- strategy/backtest/scanner/portfolio/notification/ai/ui logic

## Testing Requirements

Default tests must remain offline.

Run:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Run focused tests, likely:

`python3 -m unittest tests/datahub/test_akshare_sector_membership_adapter.py`

`python3 -m unittest -v tests/datahub/test_akshare_sector_membership_live.py`

Run relevant regression tests if shared AKShare behavior is touched:

`python3 -m unittest tests/datahub/test_akshare_sector_master_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_sector_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_index_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_fund_nav_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_adapter.py`

If source-catalog tests are touched, run:

`python3 -m unittest tests/datahub/test_source_catalog.py`

Run gated live smoke when enabled:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_sector_membership_live.py`

## Acceptance Criteria

The task is acceptable when:

- AKShare `SECTOR_MEMBERSHIP` adapter exists under `quant/datahub/**`
- scope remains limited to `DatasetName.SECTOR_MEMBERSHIP`
- offline normalization/validation tests pass deterministically
- duplicate handling boundary (benign dedupe vs conflict hard-fail) is covered by tests
- default tests remain offline-safe
- live smoke is present, gated, and truthfully recorded
- live-enabled PASS/SKIP/FAIL result and evidence are documented
- no future-phase module contains new logic
- report exists at `coordination/reports/TASK-019_REPORT.md`

## Report Path

`coordination/reports/TASK-019_REPORT.md`

## Review Path

`coordination/reviews/TASK-019_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-019_INTEGRATION.md`

## Out of Scope

Everything outside a narrow DataHub `SECTOR_MEMBERSHIP` adapter and tests is out of scope.
