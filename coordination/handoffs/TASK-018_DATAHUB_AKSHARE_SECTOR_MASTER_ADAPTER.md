# TASK-018: DataHub AKShare Sector Master Adapter

## Task ID

TASK-018

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

TASK-017 is accepted and integrated. It completed a narrow AKShare sector daily-bar adapter (`DatasetName.SECTOR_DAILY_BARS`) with gated live smoke and a validated live PASS path in the current environment.

Phase 2 remains open. The next narrow executable source slice should extend sector-domain coverage from quote history into sector master metadata.

The source catalog already links `akshare_cn_hk_public_family` to `DatasetName.SECTOR_MASTER`, `DatasetName.SECTOR_MEMBERSHIP`, and `DatasetName.SECTOR_DAILY_BARS`. TASK-018 should implement only `DatasetName.SECTOR_MASTER`.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-018_DATAHUB_AKSHARE_SECTOR_MASTER_ADAPTER.md`

## Goal

Implement a narrow AKShare-backed sector master adapter for `DatasetName.SECTOR_MASTER`, with deterministic offline tests and mandatory gated live smoke coverage.

This task should add one small sector-master adapter sibling to existing AKShare adapters. It must not expand into sector membership, scanner, strategy, or future-phase work.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-018_REPORT.md`

Suggested implementation locations:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `quant/datahub/source_catalog.py` only if a stable-coverage assertion truly needs alignment
- `tests/datahub/test_akshare_sector_master_adapter.py`
- `tests/datahub/test_akshare_sector_master_live.py`
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

### 1. AKShare sector master adapter

Add a narrow adapter for:

- source id: `akshare_cn_hk_public_family`
- source display name: `AKShare CN/HK Public Family`
- supported dataset in this task: `DatasetName.SECTOR_MASTER`
- market output: `CN_SECTOR`

The adapter should:

- implement the existing `SourceAdapter` protocol
- use lazy/optional AKShare import, so default offline tests and package imports do not require AKShare
- allow dependency injection of industry/concept master-list fetch functions for offline tests
- reject unsupported datasets clearly
- accept `SourceRequest.symbols` as optional sector-type filter only:
  - allowed filters: `INDUSTRY`, `CONCEPT`
  - no symbols means fetch both types
  - any other symbol value should fail clearly
- normalize records to `DatasetName.SECTOR_MASTER` contract fields:
  - `sector_id` (canonical: `INDUSTRY:<sector_name>` or `CONCEPT:<sector_name>`)
  - `sector_name`
  - `sector_type` (`INDUSTRY` / `CONCEPT`)
  - `market` (`CN_SECTOR`)
  - `is_active` (`True` for fetched snapshot rows)
  - `source`
  - `ingested_at`
  - `schema_version`
- include optional `source_ts` only when valid source timestamp value exists
- set `source` to `akshare_cn_hk_public_family`
- set `schema_version` from `DatasetRegistry`
- set `ingested_at` deterministically in offline tests via injectable clock
- support DataFrame-like payloads (`to_dict(orient="records")`) and list-of-mapping payloads
- fail clearly on malformed payload, missing required source fields, invalid type values, or duplicate canonical `sector_id`

Recommended default live source functions:

- industry list: `stock_board_industry_name_em`
- concept list: `stock_board_concept_name_em`

If list-source live calls fail due to network/proxy/DNS/TLS/upstream issues, classify as live-environment unavailability in the live test. Add repository-level fallback/guard only when feasible and contract-safe.

### 2. Source catalog alignment

The current catalog already includes `DatasetName.SECTOR_MASTER` for `akshare_cn_hk_public_family` and `InformationDomain.INDUSTRY_CONCEPT_SECTOR`.

Do not add broad new catalog claims in TASK-018. If any catalog/export change is necessary, keep it minimal and add deterministic tests.

### 3. Offline tests

Add deterministic offline tests proving:

- adapter satisfies `SourceAdapter`
- `fetch_source_result(...)` returns records that pass `DatasetRegistry.validate_record(...)`
- both `INDUSTRY` and `CONCEPT` list routes work via injected fetch functions
- canonical `sector_id` format is stable (`INDUSTRY:<name>`, `CONCEPT:<name>`)
- symbols filter behavior is correct (`None` => both, explicit single type => filtered)
- unsupported dataset and invalid symbols filter fail clearly
- malformed payload rows fail clearly
- duplicate canonical `sector_id` fails clearly
- default test discovery does not perform live network calls

Use `socket.create_connection` patching where useful to protect default tests.

### 4. Mandatory live smoke test

Because TASK-018 implements a real-source adapter, a gated live smoke test is mandatory.

Add a live test such as `tests/datahub/test_akshare_sector_master_live.py` that:

- is skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1`
- uses no credentials
- fetches a tiny sector-master snapshot sample
- validates at least one record with `DatasetRegistry.validate_record(...)`
- records environment/source unavailability as explicit `skipTest(...)`
- preserves adapter/schema bugs as failures instead of masking them as skips

Follow TASK-012 through TASK-017 evidence style:

- default command result
- live-enabled command result
- skip reason if live-enabled environment cannot reach source
- root-cause evidence if live-enabled run fails/skips due to network/proxy/DNS/TLS/upstream/source availability

If live-enabled smoke fails/skips due to environment, the report must record root-cause evidence and any feasible repository-level fix attempted.

## Do Not Implement

Do not implement:

- `DatasetName.SECTOR_MEMBERSHIP` adapter logic
- sector daily bar changes beyond existing TASK-017 behavior
- index constituents or other index expansion
- macro/policy/news/announcement adapters
- warehouse refresh orchestration/metadata pipeline work
- strategy/backtest/scanner/portfolio/notification/ai/ui logic

## Testing Requirements

Default tests must remain offline.

Run:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Run focused tests for changed modules, likely:

`python3 -m unittest tests/datahub/test_akshare_sector_master_adapter.py`

`python3 -m unittest -v tests/datahub/test_akshare_sector_master_live.py`

Run relevant regression tests if shared AKShare code is touched:

`python3 -m unittest tests/datahub/test_akshare_sector_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_index_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_fund_nav_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_adapter.py`

If source catalog tests are touched, run:

`python3 -m unittest tests/datahub/test_source_catalog.py`

Because TASK-018 is a real-source adapter task, run gated live smoke when explicitly enabled:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_sector_master_live.py`

## Acceptance Criteria

The task is acceptable when:

- an AKShare sector master adapter exists under `quant/datahub/**`
- adapter supports only `DatasetName.SECTOR_MASTER` in this task
- offline tests prove normalization and contract validation pass
- canonical `sector_id` and `sector_type` semantics are stable and tested
- invalid filter/payload cases fail clearly
- default tests remain offline-safe
- live smoke exists, is skipped by default, and is gated by `QUANT_SYSTEM_LIVE_TESTS=1`
- live-enabled PASS/SKIP/FAIL is truthfully recorded with evidence
- no future-phase module contains new logic
- report file exists at `coordination/reports/TASK-018_REPORT.md`
- report includes files changed, tests run, default network behavior, live result, deviations, and risks/follow-up

## Report Path

`coordination/reports/TASK-018_REPORT.md`

## Review Path

`coordination/reviews/TASK-018_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-018_INTEGRATION.md`

## Out of Scope

Everything outside a narrow DataHub AKShare `sector_master` adapter and tests is out of scope.
