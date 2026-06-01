# TASK-046: DataHub AKShare A-share Company Announcements Adapter

## Task ID

TASK-046

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2.5: DataHub Trading-Grade Source Capability

## Context

TASK-045 has been accepted, integrated, and controller-closed after rework. It added a narrow public AKShare A-share margin financing/lending slice and fixed the live skip/fail classification boundary so AKShare argument/signature compatibility errors remain hard failures.

Phase 2.5 remains open because required trading-grade source capabilities still include planned A-share announcement coverage. A stable contract already exists:

- `DatasetName.COMPANY_ANNOUNCEMENTS`

Current source capability truth marks `a_share_company_announcements` as planned and tied to credentialed source coverage. This task should implement the next no-credential public-source DataHub adapter slice using AKShare A-share announcement routes, without using private credentials.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-046_DATAHUB_AKSHARE_A_SHARE_COMPANY_ANNOUNCEMENTS_ADAPTER.md`
- `quant/datahub/datasets.py`
- `quant/datahub/source.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `quant/datahub/adapters/akshare.py`
- relevant existing AKShare and HKEX announcement adapter tests under `tests/datahub/`

## Goal

Implement a narrow AKShare-backed A-share company announcements adapter slice that produces validated records for:

- `DatasetName.COMPANY_ANNOUNCEMENTS`

The task should prove that the existing announcement contract can be populated from a bounded no-credential public A-share source route while preserving deterministic offline tests and gated live smoke behavior.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-046_REPORT.md`

Suggested implementation locations:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py` only if exports need adjustment
- `quant/datahub/source_capabilities.py` only to update A-share announcement capability truth after implementation
- `quant/datahub/source_catalog.py` only for minimal public-source alignment if AKShare announcement coverage is implemented and catalog coverage is inconsistent
- `tests/datahub/test_akshare_a_share_company_announcements_adapter.py`
- `tests/datahub/test_akshare_a_share_company_announcements_live.py`
- focused existing tests under `tests/datahub/` if shared parsing, symbol, or announcement behavior changes

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

### 1. AKShare A-share announcement adapter slice

Add a narrow adapter for:

- source id: `akshare_cn_hk_public_family`
- source display name: `AKShare CN/HK Public Family`
- supported dataset in this task:
  - `DatasetName.COMPANY_ANNOUNCEMENTS`
- initial market scope: bounded A-share symbol and/or date-range announcement query sufficient to return validated A-share announcement records

The adapter should:

- implement the existing `SourceAdapter` protocol and `SourceResult` conventions
- use no credentials, cookies, tokens, browser session state, or private account data
- reject unsupported datasets clearly
- accept canonical exchange-qualified A-share symbols such as `600000.SH`, `000001.SZ`, and `430047.BJ` when supported by the selected route
- accept bare six-digit A-share codes only when existing local adapter style supports them, then normalize output `symbol` to canonical exchange-qualified form
- reject HK, ETF/fund, index, malformed, and missing symbols clearly when a symbol-specific route is used
- set `market=A_SHARE`
- set `source=akshare_cn_hk_public_family`
- set `schema_version` from `DatasetRegistry`
- set `ingested_at` from an injectable clock for deterministic tests
- support DataFrame-like and list-of-mapping payloads in offline fixtures
- normalize available source fields into the existing `COMPANY_ANNOUNCEMENTS` contract without inventing values the source does not provide
- produce stable `announcement_id`, `publish_time`, `announcement_type`, `title`, optional `url`, and source metadata
- sort output deterministically by `publish_time`, `symbol`, and `announcement_id`
- deduplicate exact duplicate rows deterministically
- fail clearly on malformed payloads, missing required source fields, invalid publish times, unsupported datasets, invalid symbols, or incompatible AKShare route signatures

### 2. Route and source boundary

- Prefer no-credential AKShare A-share announcement routes available in the local AKShare version.
- Candidate local AKShare route names observed by the controller include `stock_individual_notice_report` and `stock_notice_report`; the execution window must still verify the selected route shape with deterministic fixtures.
- Route selection must be bounded and explicit. It may use a symbol-specific route or a date/category table route with post-filtering to A-share symbols.
- Do not add Tushare, credentialed fallback, browser scraping, cookies, tokens, or private account data.
- Do not add broad A-share universe ingestion, full announcement history backfill, scheduler logic, storage refresh orchestration, or cross-source fallback.
- Network/proxy/DNS/TLS/upstream/source availability failures may be classified for live skip diagnostics, but adapter/schema/normalization issues must remain hard failures.

### 3. Source capability truth

If the dataset has working offline adapter coverage and gated live smoke evidence, update source capability truth conservatively:

- `a_share_company_announcements`: use `partial` if this task validates only a narrow public-source slice
- update `gap_reason`, `recommended_handoff_theme`, and source-family alignment only as needed to reflect public AKShare coverage and remaining breadth/history limitations
- update `source_catalog.py` only if the implemented public AKShare announcement coverage makes catalog dataset coverage inconsistent
- do not mark the capability `covered` unless the implementation genuinely satisfies the full trading-grade capability definition

Do not change unrelated capabilities except to preserve tests.

### 4. Offline tests

Add deterministic offline tests proving:

- adapter satisfies `SourceAdapter`
- `DatasetName.COMPANY_ANNOUNCEMENTS` is accepted and unsupported datasets fail clearly
- `fetch_source_result(...)` records pass `DatasetRegistry.validate_record(...)`
- canonical and accepted bare A-share symbol handling works when using a symbol route
- invalid HK, ETF, fund, index, malformed, missing, and multiple-symbol cases fail clearly where applicable
- DataFrame-like and list-of-mapping payload conversion works
- required publish-time parsing works and invalid publish times fail clearly
- announcement id, type, title, optional URL, and source metadata are normalized deterministically
- records are sorted and duplicate rows are deduplicated
- malformed payloads and missing required source fields fail clearly
- AKShare route argument/signature compatibility errors are not classified as live environment/source unavailable
- default tests remain offline-safe; patch network helpers where useful

### 5. Mandatory live smoke test

Because TASK-046 is a real-source adapter task, gated live smoke coverage is mandatory.

Add `tests/datahub/test_akshare_a_share_company_announcements_live.py` or equivalent that:

- is skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1`
- uses no credentials
- fetches a minimal bounded live sample for one stable A-share symbol/date range or one bounded A-share announcement table slice supported by the selected public route
- validates at least one record through `DatasetRegistry.validate_record(...)`
- asserts `source=akshare_cn_hk_public_family`, `market=A_SHARE`, and canonical A-share symbol output
- classifies environment/source unavailability as explicit `skipTest(...)`
- preserves adapter/schema/normalization and AKShare function argument/signature issues as failures

If the live-enabled run fails or skips due to network/proxy/DNS/TLS/upstream/source availability, the report must include root-cause evidence and feasible repository-level fixes attempted. Controller closure will require the rework/review gate in `AGENTS.md`.

## Do Not Implement

Do not implement:

- broad A-share universe ingestion
- full announcement history backfill
- Tushare or other credentialed adapters
- source routes requiring private credentials, cookies, or tokens
- storage refresh orchestration
- feature calculations
- scanner ranking or stock picking
- strategy, backtest, portfolio, signal, risk, notification, AI, UI, or automated trading logic

## Testing Requirements

Default tests must remain offline.

Run:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Run focused tests, likely:

`python3 -m unittest tests/datahub/test_akshare_a_share_company_announcements_adapter.py`

`python3 -m unittest -v tests/datahub/test_akshare_a_share_company_announcements_live.py`

Run related regressions if shared AKShare, symbol, or announcement behavior is touched:

`python3 -m unittest tests/datahub/test_hkex_company_announcements_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_adapter.py`

`python3 -m unittest tests/datahub/test_source.py`

Run source-capability/catalog tests if those files change:

`python3 -m unittest tests/datahub/test_source_capabilities.py`

`python3 -m unittest tests/datahub/test_source_catalog.py`

Run gated live smoke when enabled:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_company_announcements_live.py`

If any command cannot run, report the exact command and reason in `coordination/reports/TASK-046_REPORT.md`.

## Acceptance Criteria

The task is acceptable when:

- AKShare A-share company-announcement adapter coverage exists under `quant/datahub/**`
- records for `COMPANY_ANNOUNCEMENTS` validate against `DatasetRegistry`
- scope remains limited to `market=A_SHARE` and `source=akshare_cn_hk_public_family`
- offline tests pass and remain deterministic
- default tests remain offline-safe
- symbol parsing, payload parsing, publish-time parsing, sorting, deduplication, malformed payload, unsupported dataset, route compatibility, and symbol-rejection boundaries are covered
- gated live smoke exists and result is truthfully recorded
- live-enabled PASS is provided for closure; if live-enabled skip/fail occurs because of network/proxy/DNS/TLS/upstream/source availability, the report includes root-cause evidence and feasible fixes attempted, and controller closure requires the rework/review gate in `AGENTS.md`
- no future-phase module contains new logic
- report exists at `coordination/reports/TASK-046_REPORT.md`

## Report Path

`coordination/reports/TASK-046_REPORT.md`

## Review Path

`coordination/reviews/TASK-046_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-046_INTEGRATION.md`
