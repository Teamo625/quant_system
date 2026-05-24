# TASK-023: DataHub HKEX Company Announcements Adapter

## Task ID

TASK-023

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

TASK-022 has been accepted and integrated. It completed the AKShare `NEWS_EVENTS` adapter with closure-ready live-enabled PASS evidence.

Phase 2 remains open. The next narrow executable source slice is listed-company announcement coverage. `DatasetName.COMPANY_ANNOUNCEMENTS` already has a stable contract and is listed under the priority-1 no-credential `hkex_disclosure_and_calendar_family` source family.

This task must implement only `DatasetName.COMPANY_ANNOUNCEMENTS`.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-023_DATAHUB_HKEX_COMPANY_ANNOUNCEMENTS_ADAPTER.md`

## Goal

Implement a narrow HKEX-backed company announcements adapter for `DatasetName.COMPANY_ANNOUNCEMENTS`, with deterministic offline tests and mandatory gated live smoke coverage.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-023_REPORT.md`

Suggested implementation locations:

- `quant/datahub/adapters/hkex.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `quant/datahub/source_catalog.py` only if strict catalog assertion alignment is required
- `tests/datahub/test_hkex_company_announcements_adapter.py`
- `tests/datahub/test_hkex_company_announcements_live.py`
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

### 1. HKEX company announcements adapter

Add a narrow adapter for:

- source id: `hkex_disclosure_and_calendar_family`
- source display name: `HKEX Disclosure and Calendar Family`
- supported dataset in this task: `DatasetName.COMPANY_ANNOUNCEMENTS`
- initial market scope: Hong Kong listed-company announcement metadata

The adapter should:

- implement the existing `SourceAdapter` protocol
- use no credentials, cookies, tokens, or private account data
- reject unsupported datasets clearly
- support optional `symbols` for HK symbols when feasible, such as `00700.HK`; if the selected HKEX public route cannot filter server-side, apply a deterministic client-side filter after normalization
- normalize output records to `COMPANY_ANNOUNCEMENTS` contract fields:
  - `announcement_id`
  - `symbol`
  - `market`
  - `publish_time`
  - `announcement_type`
  - `title`
  - optional `url`
  - `source`
  - optional `source_ts`
  - `ingested_at`
  - `schema_version`
- set `market=HK`
- set `source=hkex_disclosure_and_calendar_family`
- set `schema_version` from `DatasetRegistry`
- set `ingested_at` from injectable clock for deterministic tests
- build a deterministic `announcement_id` when the source lacks a stable id, using stable source fields such as symbol, publish time, title, type, and url
- parse `publish_time` from source payload when present; if the source only provides a date, normalize to a deterministic midnight datetime
- normalize HK symbols to canonical 5-digit `.HK` form, e.g. `700`, `00700`, or `00700.HK` -> `00700.HK`
- set `announcement_type` from source payload when reliable; otherwise use a conservative stable value such as `general`
- support DataFrame-like payload and list-of-mapping payload fixtures
- fail clearly on malformed payload, missing required fields, invalid publish time, invalid symbol, invalid filters, or invalid required string fields

### 2. Route and duplicate boundary

- Prefer a no-credential HKEX public disclosure or announcement route.
- Keep any route order bounded and explicit.
- Network/proxy/DNS/TLS/upstream/source availability failures may be classified for route fallback or live skip diagnostics, but DataHub contract/normalization failures must remain hard failures.
- Benign exact duplicate announcement rows may be deterministically deduplicated.
- Conflicting duplicates for the same `announcement_id` must hard-fail.

### 3. Source catalog alignment

The catalog already includes `DatasetName.COMPANY_ANNOUNCEMENTS` under `hkex_disclosure_and_calendar_family` and `InformationDomain.ANNOUNCEMENT`.

Do not add broad source claims. Only perform minimal source-catalog assertion updates if required by implemented stable behavior.

### 4. Offline tests

Add deterministic offline tests proving:

- adapter satisfies `SourceAdapter`
- `fetch_source_result(...)` records pass `DatasetRegistry.validate_record(...)`
- source payload conversion from DataFrame-like and list-of-mapping works
- `announcement_id` generation is deterministic when source id is missing
- HK symbol normalization and optional symbol filter behavior is explicit
- required field, publish-time parsing, optional field, and announcement type behavior is covered
- network/source route fallback behavior is covered if implemented
- duplicate boundary is preserved
- malformed payloads fail clearly
- default tests remain offline-safe

### 5. Mandatory live smoke test

Because TASK-023 is a real-source adapter task, gated live smoke is mandatory.

Add `tests/datahub/test_hkex_company_announcements_live.py` (or equivalent) that:

- is skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1`
- uses no credentials
- fetches a minimal bounded live sample
- validates at least one record via `DatasetRegistry.validate_record(...)`
- classifies environment/source unavailability as explicit `skipTest(...)`
- preserves adapter/schema issues as failures

If live-enabled run fails/skips due to network/proxy/DNS/TLS/upstream/source availability, report must include root-cause evidence and feasible repository-level fixes attempted.

## Do Not Implement

Do not implement:

- macro or policy adapters
- news behavior changes beyond preserving TASK-022 compatibility
- trading strategies, signal generation, scanner logic, AI reports, notifications, or UI
- broad disclosure scraping outside bounded HKEX public announcement metadata
- storage refresh orchestration beyond what is needed for this adapter test surface

## Testing Requirements

Default tests must remain offline.

Run:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Run focused tests, likely:

`python3 -m unittest tests/datahub/test_hkex_company_announcements_adapter.py`

`python3 -m unittest -v tests/datahub/test_hkex_company_announcements_live.py`

Run related regressions if shared DataHub or adapter export behavior is touched:

`python3 -m unittest tests/datahub/test_akshare_news_events_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_global_equity_snapshot_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_hk_adapter.py`

`python3 -m unittest tests/datahub/test_source.py`

If source-catalog tests are touched, run:

`python3 -m unittest tests/datahub/test_source_catalog.py`

Run gated live smoke when enabled:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_hkex_company_announcements_live.py`

## Acceptance Criteria

The task is acceptable when:

- HKEX `COMPANY_ANNOUNCEMENTS` adapter exists under `quant/datahub/**`
- scope remains limited to `DatasetName.COMPANY_ANNOUNCEMENTS`
- offline tests pass and remain deterministic
- default tests remain offline-safe
- duplicate, malformed payload, required-field, symbol, and publish-time boundaries are covered
- gated live smoke exists and result is truthfully recorded
- live-enabled PASS is provided for closure; if live-enabled skip/fail occurs because of network/proxy/DNS/TLS/upstream/source availability, the report must include root-cause evidence and feasible fixes attempted, and controller closure will require the rework/review gate in `AGENTS.md`
- no future-phase module contains new logic
- report exists at `coordination/reports/TASK-023_REPORT.md`

## Report Path

`coordination/reports/TASK-023_REPORT.md`

## Review Path

`coordination/reviews/TASK-023_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-023_INTEGRATION.md`

## Out of Scope

Everything outside a narrow DataHub `COMPANY_ANNOUNCEMENTS` adapter and tests is out of scope.
