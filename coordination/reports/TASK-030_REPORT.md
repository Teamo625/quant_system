# TASK-030 Report

## Task
- TASK-030_DATAHUB_POLICY_DOCUMENTS_ADAPTER

## Files Changed
- quant/datahub/adapters/policy.py
- quant/datahub/adapters/__init__.py
- quant/datahub/__init__.py
- tests/datahub/test_policy_documents_adapter.py
- tests/datahub/test_policy_documents_live.py

## Implementation Summary
- Added `MacroPolicyDocumentsAdapter` for `DatasetName.POLICY_DOCUMENTS` under source id `macro_policy_public_sources`.
- Implemented bounded, explicit route order for official public policy metadata search:
  - `zhengcelibrary_gw` (国务院文件)
  - `zhengcelibrary_bm` (国务院部门文件)
- Enforced adapter boundaries:
  - reject unsupported datasets
  - reject non-empty `symbols`
  - normalize and filter by `publish_date` (`start_date`/`end_date`)
- Normalized contract fields:
  - required: `policy_id`, `region`, `publish_date`, `title`, `authority`, `document_type`, `source`, `ingested_at`, `schema_version`
  - optional: `summary`, `url`, `source_ts`
- Implemented deterministic `policy_id` behavior:
  - use stable source id when present (`GOVCN-{id}`)
  - fallback deterministic hash id (`GOVPOL-{sha1-prefix}`) from title/publish_date/authority/document_type/url
- Implemented duplicate boundaries:
  - benign exact duplicates deduped deterministically
  - conflicting duplicates for same `policy_id` hard-fail
- Added payload compatibility and failure boundaries:
  - supports DataFrame-like payloads and list-of-mapping payloads
  - supports gov-search response mapping payloads
  - clear failures for malformed payloads, missing required fields, invalid date/datetime, invalid required strings
- Added optional TLS-verify fallback only when certificate-verification failure is detected on the same official route.

## Tests Run

### Required default/offline runs
1. `python3 -m unittest tests/datahub/test_policy_documents_adapter.py`
- PASS (15 tests)

2. `python3 -m unittest -v tests/datahub/test_policy_documents_live.py`
- PASS (classifier tests)
- live smoke skipped by default as designed

3. `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`
- PASS (464 tests, 18 skipped)

### Related regressions
4. `python3 -m unittest tests/datahub/test_datasets.py`
- PASS (27 tests)

5. `python3 -m unittest tests/datahub/test_source.py`
- PASS (20 tests)

6. `python3 -m unittest tests/datahub/test_akshare_china_macro_adapter.py`
- PASS (18 tests)

7. `python3 -m unittest tests/datahub/test_akshare_news_events_adapter.py`
- PASS (15 tests)

## Default Network Behavior
- Default test runs remain offline-safe.
- No live network access is required for default adapter tests (`test_policy_documents_adapter.py` uses injected fixtures/mocks).
- Live source test remains gated by environment variable and skipped by default unless explicitly enabled.

## Live-Enabled Result (Mandatory)
- Command: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_policy_documents_live.py`
- Result: PASS
  - classifier tests PASS
  - live smoke PASS
- Evidence summary:
  - adapter fetched bounded live sample from official public source route(s)
  - at least one `POLICY_DOCUMENTS` record validated by `DatasetRegistry.validate_record(...)` with no issues

## Deviations From Handoff
- None.

## Risks / Follow-up
- Upstream public route response shape can change; current implementation fails fast on contract-breaking changes.
- Environment-specific TLS interception may still require operational trust decisions; fallback is only triggered for certificate-verification failures on the same official endpoint.
- Scope remains intentionally narrow to `POLICY_DOCUMENTS` metadata only (no policy body parsing, sentiment, AI summarization, or downstream module logic).
