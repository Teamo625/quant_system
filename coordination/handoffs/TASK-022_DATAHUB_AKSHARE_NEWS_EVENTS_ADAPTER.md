# TASK-022: DataHub AKShare News Events Adapter

## Task ID

TASK-022

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

TASK-021 has been accepted and integrated. It completed the AKShare `GLOBAL_EQUITY_SNAPSHOT` adapter and live-route stability reworks, including closure-ready live-enabled PASS evidence.

Phase 2 remains open. The next narrow executable source slice is public news coverage, which already has a stable `DatasetName.NEWS_EVENTS` contract and is listed under the priority-1 no-credential `akshare_cn_hk_public_family` source family.

This task must implement only `DatasetName.NEWS_EVENTS`.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-022_DATAHUB_AKSHARE_NEWS_EVENTS_ADAPTER.md`

## Goal

Implement a narrow AKShare-backed news events adapter for `DatasetName.NEWS_EVENTS`, with deterministic offline tests and mandatory gated live smoke coverage.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-022_REPORT.md`

Suggested implementation locations:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `quant/datahub/source_catalog.py` only if strict catalog assertion alignment is required
- `tests/datahub/test_akshare_news_events_adapter.py`
- `tests/datahub/test_akshare_news_events_live.py`
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

### 1. AKShare news events adapter

Add a narrow adapter for:

- source id: `akshare_cn_hk_public_family`
- source display name: `AKShare CN/HK Public Family`
- supported dataset in this task: `DatasetName.NEWS_EVENTS`
- initial scope: no-credential public market or stock news metadata available through the installed AKShare version

The adapter should:

- implement the existing `SourceAdapter` protocol
- use lazy/optional AKShare imports
- reject unsupported datasets clearly
- support optional `symbols` when the selected AKShare route supports symbol-specific news; otherwise reject unsupported symbol filters clearly
- normalize output records to `NEWS_EVENTS` contract fields:
  - `news_id`
  - `region`
  - `publish_time`
  - `title`
  - `source_name`
  - optional `related_symbol`
  - optional `sentiment_label`
  - optional `summary`
  - optional `url`
  - `source`
  - optional `source_ts`
  - `ingested_at`
  - `schema_version`
- set `source=akshare_cn_hk_public_family`
- set `schema_version` from `DatasetRegistry`
- set `ingested_at` from injectable clock for deterministic tests
- build a deterministic `news_id` when the source lacks a stable id, using stable source fields such as title, publish time, source name, url, and related symbol
- parse `publish_time` from source payload when present; if the source only provides a date, normalize to a deterministic midnight datetime
- set `region` conservatively from the selected source scope, such as `CN`, `HK`, or `GLOBAL`
- set `source_name` from source payload when reliable, otherwise from a stable route/source label
- keep `sentiment_label` absent unless the source explicitly provides a reliable label
- support DataFrame-like payload and list-of-mapping payload
- fail clearly on malformed payload, missing required fields, invalid publish time, invalid symbol filters, or invalid required string fields

### 2. Route and duplicate boundary

- Prefer a no-credential AKShare public news route available in the installed AKShare version.
- If multiple no-credential routes are used, keep the route order bounded and explicit.
- Network/proxy/DNS/TLS/upstream/source availability failures may be classified for route fallback or live skip diagnostics, but DataHub contract/normalization failures must remain hard failures.
- Benign exact duplicate news rows may be deterministically deduplicated.
- Conflicting duplicates for the same `news_id` must hard-fail.

### 3. Source catalog alignment

The catalog already includes `DatasetName.NEWS_EVENTS` under `akshare_cn_hk_public_family` and `InformationDomain.NEWS`.

Do not add broad source claims. Only perform minimal source-catalog assertion updates if required by implemented stable behavior.

### 4. Offline tests

Add deterministic offline tests proving:

- adapter satisfies `SourceAdapter`
- `fetch_source_result(...)` records pass `DatasetRegistry.validate_record(...)`
- source payload conversion from DataFrame-like and list-of-mapping works
- `news_id` generation is deterministic when source id is missing
- required field, publish-time parsing, optional field, and symbol-filter behavior is explicit
- network/source route fallback behavior is covered if implemented
- duplicate boundary is preserved
- malformed payloads fail clearly
- default tests remain offline-safe

### 5. Mandatory live smoke test

Because TASK-022 is a real-source adapter task, gated live smoke is mandatory.

Add `tests/datahub/test_akshare_news_events_live.py` (or equivalent) that:

- is skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1`
- uses no credentials
- fetches a minimal bounded live sample
- validates at least one record via `DatasetRegistry.validate_record(...)`
- classifies environment/source unavailability as explicit `skipTest(...)`
- preserves adapter/schema issues as failures

If live-enabled run fails/skips due to network/proxy/DNS/TLS/upstream/source availability, report must include root-cause evidence and feasible repository-level fixes attempted.

## Do Not Implement

Do not implement:

- macro, policy, or announcement adapters
- trading strategies, signal generation, scanner logic, AI reports, notifications, or UI
- broad news sentiment analysis or AI classification
- storage refresh orchestration beyond what is needed for this adapter test surface

## Testing Requirements

Default tests must remain offline.

Run:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Run focused tests, likely:

`python3 -m unittest tests/datahub/test_akshare_news_events_adapter.py`

`python3 -m unittest -v tests/datahub/test_akshare_news_events_live.py`

Run related regressions if shared AKShare adapter behavior is touched:

`python3 -m unittest tests/datahub/test_akshare_global_equity_snapshot_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_index_constituents_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_index_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_hk_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_fund_nav_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_adapter.py`

If source-catalog tests are touched, run:

`python3 -m unittest tests/datahub/test_source_catalog.py`

Run gated live smoke when enabled:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_news_events_live.py`

## Acceptance Criteria

The task is acceptable when:

- AKShare `NEWS_EVENTS` adapter exists under `quant/datahub/**`
- scope remains limited to `DatasetName.NEWS_EVENTS`
- offline tests pass and remain deterministic
- default tests remain offline-safe
- duplicate, malformed payload, required-field, and publish-time boundaries are covered
- gated live smoke exists and result is truthfully recorded
- live-enabled PASS is provided for closure; if live-enabled skip/fail occurs because of network/proxy/DNS/TLS/upstream/source availability, the report must include root-cause evidence and feasible fixes attempted, and controller closure will require the rework/review gate in `AGENTS.md`
- no future-phase module contains new logic
- report exists at `coordination/reports/TASK-022_REPORT.md`

## Report Path

`coordination/reports/TASK-022_REPORT.md`

## Review Path

`coordination/reviews/TASK-022_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-022_INTEGRATION.md`

## Out of Scope

Everything outside a narrow DataHub `NEWS_EVENTS` adapter and tests is out of scope.
