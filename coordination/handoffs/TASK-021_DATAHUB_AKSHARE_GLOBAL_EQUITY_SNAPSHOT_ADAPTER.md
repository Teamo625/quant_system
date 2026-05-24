# TASK-021: DataHub AKShare Global Equity Snapshot Adapter

## Task ID

TASK-021

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

TASK-020 has been accepted and integrated. It completed the AKShare `INDEX_CONSTITUENTS` adapter with closure-ready live PASS evidence.

Phase 2 remains open. The next narrow executable source slice is concise global equity coverage, which already has a stable `DatasetName.GLOBAL_EQUITY_SNAPSHOT` contract and is listed under the priority-1 no-credential `akshare_cn_hk_public_family` source family.

This task must implement only `DatasetName.GLOBAL_EQUITY_SNAPSHOT`.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-021_DATAHUB_AKSHARE_GLOBAL_EQUITY_SNAPSHOT_ADAPTER.md`

## Goal

Implement a narrow AKShare-backed global equity snapshot adapter for `DatasetName.GLOBAL_EQUITY_SNAPSHOT`, with deterministic offline tests and mandatory gated live smoke coverage.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-021_REPORT.md`

Suggested implementation locations:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `quant/datahub/source_catalog.py` only if strict catalog assertion alignment is required
- `tests/datahub/test_akshare_global_equity_snapshot_adapter.py`
- `tests/datahub/test_akshare_global_equity_snapshot_live.py`
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

### 1. AKShare global equity snapshot adapter

Add a narrow adapter for:

- source id: `akshare_cn_hk_public_family`
- source display name: `AKShare CN/HK Public Family`
- supported dataset in this task: `DatasetName.GLOBAL_EQUITY_SNAPSHOT`
- initial market scope: concise no-credential global equity snapshot coverage, preferably US equity spot/snapshot data if available through the installed AKShare version

The adapter should:

- implement the existing `SourceAdapter` protocol
- use lazy/optional AKShare imports
- reject unsupported datasets clearly
- accept optional `symbols` filters
- support common canonical/source-native symbol forms for the implemented source slice, such as `AAPL.US`, `MSFT.US`, `AAPL`, or AKShare source-native values when the route uses them
- normalize output records to `GLOBAL_EQUITY_SNAPSHOT` contract fields:
  - `symbol`
  - `market`
  - `trade_date`
  - `close`
  - `change_pct`
  - `currency`
  - `exchange`
  - `region`
  - `source`
  - optional `source_ts`
  - `ingested_at`
  - `schema_version`
- set `source=akshare_cn_hk_public_family`
- set `schema_version` from `DatasetRegistry`
- set `ingested_at` from injectable clock for deterministic tests
- set `trade_date` from source payload when reliable, otherwise from injectable clock date with this fallback documented in tests/report
- normalize `change_pct` whether the source provides percent strings or numeric values
- support DataFrame-like payload and list-of-mapping payload
- fail clearly on malformed payload, missing required fields, invalid symbol/date/numeric values, and unsupported market filters

### 2. Filtering and duplicate boundary

- If `symbols` are provided, return only requested instruments after canonicalization.
- If no `symbols` are provided, return a bounded deterministic subset when feasible to avoid an unexpectedly huge normalized result in tests.
- Benign exact duplicate source rows may be deterministically deduplicated.
- Conflicting duplicates for the same canonical `symbol` and `trade_date` must hard-fail.

### 3. Source catalog alignment

The catalog already includes `DatasetName.GLOBAL_EQUITY_SNAPSHOT` under `akshare_cn_hk_public_family` and `InformationDomain.GLOBAL_EQUITY_CONCISE`.

Do not add broad source claims. Only perform minimal source-catalog assertion updates if required by implemented stable behavior.

### 4. Offline tests

Add deterministic offline tests proving:

- adapter satisfies `SourceAdapter`
- `fetch_source_result(...)` records pass `DatasetRegistry.validate_record(...)`
- supported symbol input forms normalize consistently
- optional/missing symbol filter behavior is explicit and bounded
- `trade_date` fallback from injectable clock is deterministic when the source lacks a reliable date
- `change_pct`, `close`, and optional `source_ts` parsing behavior is covered
- malformed payloads fail clearly
- duplicate boundary is preserved
- default tests remain offline-safe

### 5. Mandatory live smoke test

Because TASK-021 is a real-source adapter task, gated live smoke is mandatory.

Add `tests/datahub/test_akshare_global_equity_snapshot_live.py` (or equivalent) that:

- is skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1`
- uses no credentials
- fetches a minimal bounded live sample for one implemented global equity symbol or a tiny built-in candidate set
- validates at least one record via `DatasetRegistry.validate_record(...)`
- classifies environment/source unavailability as explicit `skipTest(...)`
- preserves adapter/schema issues as failures

If live-enabled run fails/skips due to network/proxy/DNS/TLS/upstream/source availability, report must include root-cause evidence and feasible repository-level fixes attempted.

## Do Not Implement

Do not implement:

- news, policy, macro, or announcement adapters
- additional A-share/HK/ETF/fund behavior beyond what is required for this adapter
- index daily bars or index constituents changes beyond regression compatibility
- strategy/backtest/scanner/portfolio/notification/ai/ui logic

## Testing Requirements

Default tests must remain offline.

Run:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Run focused tests, likely:

`python3 -m unittest tests/datahub/test_akshare_global_equity_snapshot_adapter.py`

`python3 -m unittest -v tests/datahub/test_akshare_global_equity_snapshot_live.py`

Run related regressions if shared AKShare behavior is touched:

`python3 -m unittest tests/datahub/test_akshare_index_constituents_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_index_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_hk_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_fund_nav_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_adapter.py`

If source-catalog tests are touched, run:

`python3 -m unittest tests/datahub/test_source_catalog.py`

Run gated live smoke when enabled:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_global_equity_snapshot_live.py`

## Acceptance Criteria

The task is acceptable when:

- AKShare `GLOBAL_EQUITY_SNAPSHOT` adapter exists under `quant/datahub/**`
- scope remains limited to `DatasetName.GLOBAL_EQUITY_SNAPSHOT`
- offline tests pass and remain deterministic
- default tests remain offline-safe
- duplicate and malformed payload boundaries are covered
- gated live smoke exists and result is truthfully recorded
- live-enabled PASS is provided for closure; if live-enabled skip/fail occurs because of network/proxy/DNS/TLS/upstream/source availability, the report must include root-cause evidence and feasible fixes attempted, and controller closure will require the rework/review gate in `AGENTS.md`
- no future-phase module contains new logic
- report exists at `coordination/reports/TASK-021_REPORT.md`

## Report Path

`coordination/reports/TASK-021_REPORT.md`

## Review Path

`coordination/reviews/TASK-021_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-021_INTEGRATION.md`

## Out of Scope

Everything outside a narrow DataHub `GLOBAL_EQUITY_SNAPSHOT` adapter and tests is out of scope.
