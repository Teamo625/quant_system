# TASK-049: DataHub AKShare A-share Major Activity Events Adapter

## Task ID

TASK-049

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2.5: DataHub Trading-Grade Source Capability

## Context

TASK-048 has been accepted and integrated. It added bounded public AKShare adapter coverage for `DatasetName.LIMIT_UP_DOWN_EVENTS` and moved `a_share_limit_up_down` to `partial`.

Phase 2.5 remains open because required trading-grade source capabilities still include planned or partial DataHub source-capability work. The next executable gap is `a_share_major_activity_events`, which has a stable `DatasetName.MAJOR_ACTIVITY_EVENTS` contract from TASK-042 but still lacks implemented no-credential public-source adapter coverage.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-049_DATAHUB_AKSHARE_A_SHARE_MAJOR_ACTIVITY_EVENTS_ADAPTER.md`
- `quant/datahub/datasets.py`
- `quant/datahub/source.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `quant/datahub/adapters/akshare.py`
- relevant existing AKShare adapter and live-smoke tests under `tests/datahub/`

## Goal

Implement a narrow no-credential AKShare-backed A-share major activity event adapter slice that produces validated source-fact records for:

- `DatasetName.MAJOR_ACTIVITY_EVENTS`

The first source slice should focus on bounded public A-share block-trade event rows if the local AKShare route shape supports it. Candidate route names observed by the controller include `stock_dzjy_mrmx`, `stock_dzjy_mrtj`, `stock_dzjy_sctj`, `stock_dzjy_hygtj`, `stock_dzjy_hyyybtj`, and `stock_dzjy_yybph`; the execution window must verify route shape with deterministic fixtures and choose a bounded, source-truthful route.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-049_REPORT.md`

Suggested implementation locations:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py` only if exports need adjustment
- `quant/datahub/source_capabilities.py` only to update A-share major activity capability truth after implementation
- `quant/datahub/source_catalog.py` only if implemented public AKShare coverage makes catalog truth inconsistent
- `tests/datahub/test_akshare_a_share_major_activity_events_adapter.py`
- `tests/datahub/test_akshare_a_share_major_activity_events_live.py`
- focused existing tests under `tests/datahub/` if shared parsing, symbol, source catalog, or AKShare behavior changes

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

### 1. AKShare A-share major activity event adapter slice

Add a narrow adapter for:

- source id: `akshare_cn_hk_public_family`
- source display name: `AKShare CN/HK Public Family`
- supported dataset in this task:
  - `DatasetName.MAJOR_ACTIVITY_EVENTS`
- initial market scope: bounded A-share event rows for one date or other explicitly bounded route parameter supported by the selected AKShare route

The adapter should:

- implement the existing `SourceAdapter` protocol and `SourceResult` conventions
- use no credentials, cookies, tokens, browser session state, or private account data
- reject unsupported datasets clearly
- require bounded request parameters; reject unbounded requests
- reject multi-day date ranges unless the implementation explicitly and safely supports bounded iteration
- accept canonical exchange-qualified A-share symbols such as `600000.SH`, `000001.SZ`, and `430047.BJ` when symbol filtering is supported by the selected route
- accept bare six-digit A-share codes only when existing local adapter style supports them, then normalize output `symbol` to canonical exchange-qualified form when the source row permits it
- reject HK, ETF/fund, index, malformed, and missing symbols clearly when symbol filtering is requested
- set `market=A_SHARE`
- set `source=akshare_cn_hk_public_family`
- set `schema_version` from `DatasetRegistry`
- set `ingested_at` from an injectable clock for deterministic tests
- support DataFrame-like and list-of-mapping payloads in offline fixtures
- normalize source fields into the `MAJOR_ACTIVITY_EVENTS` contract without inventing values the source does not provide
- emit source-fact fields such as `event_id`, `event_date`, `event_type`, `participant`, `direction`, `event_value`, `event_volume`, `summary`, and source metadata only when truthfully available
- use a stable `event_type` value such as `block_trade` for verified block-trade rows
- sort output deterministically by `event_date`, `symbol`, `event_type`, and `event_id`
- deduplicate exact duplicate rows deterministically
- fail clearly on malformed payloads, missing required source fields, invalid dates, invalid numeric values, unsupported datasets, invalid symbols, route signature incompatibility, or schema/normalization errors

### 2. Route and source boundary

- Prefer no-credential AKShare A-share major-activity routes available in the local AKShare version.
- A bounded daily block-trade detail route with post-filtering is acceptable.
- Do not add Tushare, credentialed fallback, browser scraping, cookies, tokens, or private account data.
- Do not add broad A-share universe ingestion, full-history backfill, scheduler logic, storage refresh orchestration, cross-source fallback, scanner ranking, stock picking, trading signals, or strategy rules.
- Network/proxy/DNS/TLS/upstream/source availability failures may be classified for live skip diagnostics, but adapter/schema/normalization and AKShare function argument/signature issues must remain hard failures.

### 3. Source capability truth

If the dataset has working offline adapter coverage and gated live smoke evidence, update source capability truth conservatively:

- `a_share_major_activity_events`: use `partial` if this task validates only a narrow public-source slice
- update `source_family_ids`, `gap_reason`, and `recommended_handoff_theme` only as needed to reflect public AKShare coverage and remaining breadth/history limitations
- update `source_catalog.py` only if implemented public AKShare coverage makes catalog dataset coverage inconsistent
- do not mark the capability `covered` unless the implementation genuinely satisfies the full trading-grade capability definition

Do not change unrelated capabilities except to preserve tests.

### 4. Offline tests

Add deterministic offline tests proving:

- adapter satisfies `SourceAdapter`
- `DatasetName.MAJOR_ACTIVITY_EVENTS` is accepted and unsupported datasets fail clearly
- `fetch_source_result(...)` records pass `DatasetRegistry.validate_record(...)`
- bounded request behavior works and unbounded or invalid date/request parameters fail clearly
- canonical and accepted bare A-share symbol handling works when symbol filtering is supported
- invalid HK, ETF, fund, index, malformed, and unsupported symbols fail clearly when symbol filtering is requested
- DataFrame-like and list-of-mapping payload conversion works
- required date parsing works and invalid dates fail clearly
- numeric parsing accepts supported source formats and rejects invalid values
- block-trade route rows map to truthful `event_type`, `event_value`, `event_volume`, `participant`, `direction`, and `summary` fields when available
- optional route-specific fields remain optional and source-truth based
- records are sorted and duplicate rows are deduplicated
- malformed payloads and missing required source fields fail clearly
- AKShare route argument/signature compatibility errors are not classified as live environment/source unavailable
- default tests remain offline-safe; patch network helpers where useful

### 5. Mandatory live smoke test

Because TASK-049 is a real-source adapter task, gated live smoke coverage is mandatory.

Add `tests/datahub/test_akshare_a_share_major_activity_events_live.py` or equivalent that:

- is skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1`
- uses no credentials
- fetches a minimal bounded live sample for one recent or stable A-share date/route parameter supported by the selected public route
- validates at least one record through `DatasetRegistry.validate_record(...)`
- asserts `source=akshare_cn_hk_public_family`, `market=A_SHARE`, and A-share symbol output
- classifies environment/source unavailability as explicit `skipTest(...)`
- preserves adapter/schema/normalization and AKShare function argument/signature issues as failures

If the live-enabled run fails or skips due to network/proxy/DNS/TLS/upstream/source availability, the report must include root-cause evidence and feasible repository-level fixes attempted. Controller closure will require the rework/review/integration gate in `AGENTS.md`.

## Do Not Implement

Do not implement:

- Tushare or other credentialed adapters
- source routes requiring private credentials, cookies, or tokens
- broad A-share universe ingestion
- full major-activity history backfill
- storage refresh orchestration
- feature calculations
- scanner ranking or stock picking
- strategy, backtest, portfolio, signal, risk, notification, AI, UI, or automated trading logic

## Testing Requirements

Default tests must remain offline.

Run:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Run focused tests, likely:

`python3 -m unittest tests/datahub/test_akshare_a_share_major_activity_events_adapter.py`

`python3 -m unittest -v tests/datahub/test_akshare_a_share_major_activity_events_live.py`

Run related regressions if shared AKShare parsing, source catalog, source capability, or symbol behavior is touched:

`python3 -m unittest tests/datahub/test_akshare_adapter.py`

`python3 -m unittest tests/datahub/test_source.py`

`python3 -m unittest tests/datahub/test_datasets.py`

`python3 -m unittest tests/datahub/test_source_capabilities.py`

`python3 -m unittest tests/datahub/test_source_catalog.py`

Run gated live smoke when enabled:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_major_activity_events_live.py`

If any command cannot run, report the exact command and reason in `coordination/reports/TASK-049_REPORT.md`.

## Acceptance Criteria

The task is acceptable when:

- AKShare A-share major activity event adapter coverage exists under `quant/datahub/**`
- records for `MAJOR_ACTIVITY_EVENTS` validate against `DatasetRegistry`
- scope remains limited to `market=A_SHARE` and `source=akshare_cn_hk_public_family`
- offline tests pass and remain deterministic
- default tests remain offline-safe
- request bounds, route selection, payload parsing, symbol handling if supported, numeric parsing, sorting, deduplication, malformed payload, unsupported dataset, route compatibility, and source-unavailability boundaries are covered
- gated live smoke exists and result is truthfully recorded
- live-enabled PASS is provided for closure; if live-enabled skip/fail occurs because of network/proxy/DNS/TLS/upstream/source availability, the report includes root-cause evidence and feasible fixes attempted, and controller closure requires the rework/review/integration gate in `AGENTS.md`
- no future-phase module contains new logic
- report exists at `coordination/reports/TASK-049_REPORT.md`

## Report Path

`coordination/reports/TASK-049_REPORT.md`

## Review Path

`coordination/reviews/TASK-049_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-049_INTEGRATION.md`
