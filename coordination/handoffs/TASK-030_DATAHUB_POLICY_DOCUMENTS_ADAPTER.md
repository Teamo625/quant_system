# TASK-030: DataHub Policy Documents Adapter

## Task ID

TASK-030

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

TASK-029 has been accepted and integrated. It completed A-share `CAPITAL_FLOW_SNAPSHOT` coverage, including live-network rework closure and live-enabled PASS evidence. The accepted implementation keeps the AKShare primary route preferred and uses a bounded one-symbol datacenter fallback only when the primary source route is unavailable.

Phase 2 remains open. The next narrow executable source slice is policy document metadata. `DatasetName.POLICY_DOCUMENTS` already has a stable contract and is listed under the no-credential `macro_policy_public_sources` source family.

This task must implement only `DatasetName.POLICY_DOCUMENTS`.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-030_DATAHUB_POLICY_DOCUMENTS_ADAPTER.md`

## Goal

Implement a narrow no-credential public policy documents adapter for `DatasetName.POLICY_DOCUMENTS`, with deterministic offline tests and mandatory gated live smoke coverage.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-030_REPORT.md`

Suggested implementation locations:

- `quant/datahub/adapters/akshare.py` if extending the existing macro/policy source-family module is the smallest local change
- `quant/datahub/adapters/policy.py` if a separate policy adapter module is cleaner
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `quant/datahub/source_catalog.py` only if strict catalog assertion alignment is required
- `tests/datahub/test_policy_documents_adapter.py` or `tests/datahub/test_macro_policy_documents_adapter.py`
- `tests/datahub/test_policy_documents_live.py` or equivalent
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

### 1. Policy documents adapter

Add a narrow adapter for:

- source id: `macro_policy_public_sources`
- source display name: `Macro and Policy Public Sources`
- supported dataset in this task: `DatasetName.POLICY_DOCUMENTS`
- initial source scope: bounded no-credential public policy document metadata from an official or public policy-document listing/search route

The adapter should:

- implement the existing `SourceAdapter` protocol
- use lazy/optional network/source imports
- reject unsupported datasets clearly
- reject non-empty `symbols` clearly; symbol filtering is not part of this policy document slice
- support optional `start_date` and `end_date` by filtering normalized `publish_date`
- fetch only a bounded sample/page by default; do not crawl the full policy corpus
- normalize output records to `POLICY_DOCUMENTS` contract fields:
  - `policy_id`
  - `region`
  - `publish_date`
  - `title`
  - `authority`
  - `document_type`
  - optional `summary`
  - optional `url`
  - `source`
  - optional `source_ts`
  - `ingested_at`
  - `schema_version`
- set `source=macro_policy_public_sources`
- set `schema_version` from `DatasetRegistry`
- set `ingested_at` from an injectable clock for deterministic tests
- build a deterministic `policy_id` when the source lacks a stable id, using stable source fields such as title, publish date, authority, document type, and url
- set `region` conservatively from the selected source scope, such as `CN` for China policy documents or `GLOBAL` only if the route truly covers global policy metadata
- keep `summary` absent unless the source provides a reliable short abstract/snippet
- support DataFrame-like payloads and list-of-mapping payload fixtures where feasible
- fail clearly on malformed payload, missing required fields, invalid publish date, invalid required strings, unsupported dataset, or unsupported symbol filters

### 2. Source route guidance

Prefer a no-credential official or public policy route that returns metadata suitable for this contract. A suitable first candidate is the China government policy document library/search surface, but implementation must be based on a live route that can be bounded and tested without credentials.

Route rules:

- keep route order bounded and explicit
- do not crawl unlimited result pages
- do not fetch or parse full policy body text unless it is unavoidable for a small bounded metadata smoke
- classify network/proxy/DNS/TLS/upstream/source availability failures for live skip diagnostics
- keep contract/normalization failures as hard failures
- do not silently fabricate policy fields when source metadata is missing

### 3. Duplicate and identity boundary

- Benign exact duplicate policy rows may be deterministically deduplicated.
- Conflicting duplicate rows for the same `policy_id` must hard-fail.
- If source ids are unstable or absent, deterministic generated ids must be stable across runs for the same source record.
- Do not use a title-only id; include publish date and at least one additional stable field such as authority, document type, or url.

### 4. Source catalog alignment

The catalog already includes `DatasetName.POLICY_DOCUMENTS` under `macro_policy_public_sources` and `InformationDomain.POLICY`.

Do not add broad source claims. Only perform minimal source-catalog assertion or stage updates if required by implemented stable behavior.

### 5. Offline tests

Add deterministic offline tests proving:

- adapter satisfies `SourceAdapter`
- `fetch_source_result(...)` records pass `DatasetRegistry.validate_record(...)`
- source payload conversion from DataFrame-like and list-of-mapping fixtures works where supported
- `start_date` / `end_date` filtering is deterministic
- non-empty `symbols` are rejected clearly
- deterministic `policy_id` generation works when source id is missing
- required field, invalid publish date, optional field, and invalid required string behavior is covered
- duplicate and conflicting duplicate boundaries are preserved
- malformed payloads fail clearly
- default tests remain offline-safe

### 6. Mandatory live smoke test

Because TASK-030 is a real-source adapter task, gated live smoke is mandatory.

Add `tests/datahub/test_policy_documents_live.py` or equivalent that:

- is skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1`
- uses no credentials
- fetches a minimal bounded live sample
- validates at least one `POLICY_DOCUMENTS` record via `DatasetRegistry.validate_record(...)`
- classifies environment/source unavailability as explicit `skipTest(...)`
- preserves adapter/schema/normalization issues as failures

If live-enabled run fails/skips due to network/proxy/DNS/TLS/upstream/source availability, the report must include root-cause evidence and feasible repository-level fixes attempted. Controller closure will require the rework/review gate in `AGENTS.md`.

## Do Not Implement

Do not implement:

- macro observations or macro indicator expansion
- news or company announcement adapters
- policy body text mining, policy sentiment, policy entity extraction, AI summarization, or feature engineering
- trading strategies, signal generation, scanner logic, AI reports, notifications, or UI
- broad storage refresh orchestration beyond what is needed for this adapter test surface

## Testing Requirements

Default tests must remain offline.

Run:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Run focused tests, likely:

`python3 -m unittest tests/datahub/test_policy_documents_adapter.py`

`python3 -m unittest -v tests/datahub/test_policy_documents_live.py`

Run related regressions if shared adapter exports, dataset schema, source catalog, or source contract behavior is touched:

`python3 -m unittest tests/datahub/test_datasets.py`

`python3 -m unittest tests/datahub/test_source.py`

`python3 -m unittest tests/datahub/test_akshare_china_macro_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_news_events_adapter.py`

If source-catalog tests are touched, run:

`python3 -m unittest tests/datahub/test_source_catalog.py`

Run gated live smoke when enabled:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_policy_documents_live.py`

## Acceptance Criteria

The task is acceptable when:

- policy documents adapter exists under `quant/datahub/**`
- scope remains limited to `DatasetName.POLICY_DOCUMENTS`
- source id remains `macro_policy_public_sources`
- offline tests pass and remain deterministic
- default tests remain offline-safe
- duplicate, conflicting duplicate, malformed payload, required-field, date, generated-id, and symbol rejection boundaries are covered
- gated live smoke exists and result is truthfully recorded
- live-enabled PASS is provided for closure; if live-enabled skip/fail occurs because of network/proxy/DNS/TLS/upstream/source availability, the report must include root-cause evidence and feasible fixes attempted, and controller closure will require the rework/review gate in `AGENTS.md`
- no future-phase module contains new logic
- report exists at `coordination/reports/TASK-030_REPORT.md`

## Report Path

`coordination/reports/TASK-030_REPORT.md`

## Review Path

`coordination/reviews/TASK-030_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-030_INTEGRATION.md`

## Out of Scope

Everything outside a narrow DataHub `POLICY_DOCUMENTS` adapter and tests is out of scope.
