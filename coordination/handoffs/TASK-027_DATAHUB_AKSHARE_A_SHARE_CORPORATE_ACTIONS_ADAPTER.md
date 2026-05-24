# TASK-027: DataHub AKShare A-share Corporate Actions Adapter

## Task ID

TASK-027

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

TASK-026 has been accepted and integrated. It completed the AKShare A-share active stock `INSTRUMENT_MASTER` adapter with deterministic offline coverage and live-enabled PASS evidence.

Phase 2 remains open. The next narrow executable A-share source slice is corporate actions, starting with dividend/corporate-action records for individual A-share symbols. `DatasetName.CORPORATE_ACTIONS` already has a stable contract and is listed under the no-credential `akshare_cn_hk_public_family` source family.

This task must implement only the A-share corporate-actions dividend slice of `DatasetName.CORPORATE_ACTIONS`.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-027_DATAHUB_AKSHARE_A_SHARE_CORPORATE_ACTIONS_ADAPTER.md`

## Goal

Implement a narrow AKShare-backed A-share corporate actions adapter for `DatasetName.CORPORATE_ACTIONS`, focused on dividend/cash/share distribution event records for one requested A-share symbol, with deterministic offline tests and mandatory gated live smoke coverage.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-027_REPORT.md`

Suggested implementation locations:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `quant/datahub/source_catalog.py` only if strict catalog assertion alignment is required
- `tests/datahub/test_akshare_a_share_corporate_actions_adapter.py`
- `tests/datahub/test_akshare_a_share_corporate_actions_live.py`
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

### 1. AKShare A-share corporate actions adapter

Add a narrow adapter for:

- source id: `akshare_cn_hk_public_family`
- source display name: `AKShare CN/HK Public Family`
- supported dataset in this task: `DatasetName.CORPORATE_ACTIONS`
- initial scope: A-share dividend/corporate-action records for one requested stock symbol

Recommended bounded AKShare route:

- primary: `akshare.stock_dividend_cninfo(symbol="<6-digit-code>")`

Optional bounded fallback, if needed for live-source resilience:

- `akshare.stock_history_dividend_detail(symbol="<6-digit-code>", indicator="分红")`

Do not add unbounded full-market collection in this task.

The adapter should:

- implement the existing `SourceAdapter` protocol
- use lazy/optional AKShare imports
- reject unsupported datasets clearly
- require exactly one requested A-share stock symbol
- accept canonical and raw 6-digit forms where feasible, such as `600000.SH` and `600000`
- reject invalid, HK, ETF/fund, index, or ambiguous symbol filters clearly
- infer canonical symbol suffix from A-share code prefix:
  - `.SH` for Shanghai stock codes such as `600000` and `688000`
  - `.SZ` for Shenzhen stock codes such as `000001` and `300000`
  - `.BJ` for Beijing stock codes such as `920000` / `830000`
- support `start_date` / `end_date` by deterministic client-side filtering after normalized `event_date`
- support DataFrame-like payload and list-of-mapping payload fixtures
- fail clearly on malformed payload, missing required source fields, invalid event dates, invalid required strings, or non-serializable values

Normalize output records to `CORPORATE_ACTIONS` contract fields:

- `symbol`: canonical A-share symbol, e.g. `600000.SH`
- `market`: `CN`
- `event_date`: prefer source ex-dividend/ex-rights date when present; otherwise use record date or announcement date
- `event_type`: stable string, initially `dividend`
- `value`: structured object with available dividend/corporate-action details, including cash dividend, bonus-share ratio, transfer-share ratio, progress/status, report period, and raw unit/explanation fields when present
- `raw_payload_ref`: deterministic stable reference derived from canonical symbol, event type, normalized event date, and a stable serialization or hash of the source row
- `source`: `akshare_cn_hk_public_family`
- optional `source_ts` when the source exposes a trustworthy source timestamp
- `ingested_at`: from injectable clock for deterministic tests
- `schema_version`: from `DatasetRegistry`

### 2. Route and duplicate boundary

- Keep route order bounded and explicit.
- Network/proxy/DNS/TLS/upstream/source availability failures may be classified for live skip diagnostics, but DataHub contract/normalization failures must remain hard failures.
- Benign exact duplicate corporate-action rows may be deterministically deduplicated.
- Conflicting duplicate rows for the same stable corporate-action identity must hard-fail. At minimum, conflicts for the same `(symbol, event_type, event_date, raw_payload_ref)` must not silently overwrite earlier data.
- If fallback routes are used, records from multiple routes must not create duplicate logical events without deterministic dedupe or a clear hard failure.

### 3. Source catalog alignment

The catalog already includes `DatasetName.CORPORATE_ACTIONS` under `akshare_cn_hk_public_family`.

Do not add broad source claims. Only perform minimal source-catalog assertion updates if required by implemented stable behavior.

### 4. Offline tests

Add deterministic offline tests proving:

- adapter satisfies `SourceAdapter`
- `fetch_source_result(...)` records pass `DatasetRegistry.validate_record(...)`
- source payload conversion from DataFrame-like and list-of-mapping works
- symbol normalization accepts canonical and raw 6-digit forms where feasible
- unsupported and ambiguous symbols fail clearly
- `start_date` / `end_date` filtering uses normalized `event_date`
- event-date fallback order is deterministic
- `event_type`, structured `value`, `raw_payload_ref`, `source`, `ingested_at`, and `schema_version` are populated correctly
- `raw_payload_ref` is deterministic for equivalent source rows
- duplicate and conflicting-duplicate boundaries are preserved
- malformed payloads and missing required source fields fail clearly
- default tests remain offline-safe

### 5. Mandatory live smoke test

Because TASK-027 is a real-source adapter task, gated live smoke is mandatory.

Add `tests/datahub/test_akshare_a_share_corporate_actions_live.py` (or equivalent) that:

- is skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1`
- uses no credentials
- fetches a minimal bounded live sample for a stable dividend-history A-share symbol such as `600000.SH`
- validates at least one normalized record via `DatasetRegistry.validate_record(...)`
- asserts `source=akshare_cn_hk_public_family`, `market=CN`, `event_type=dividend`, and a canonical A-share symbol
- classifies environment/source unavailability as explicit `skipTest(...)`
- preserves adapter/schema/normalization issues as failures

If live-enabled run fails/skips due to network/proxy/DNS/TLS/upstream/source availability, report must include root-cause evidence and feasible repository-level fixes attempted.

## Do Not Implement

Do not implement:

- HK, ETF, fund, index, policy, valuation, capital-flow, or full-market corporate-action adapters
- trading strategy, scanner, AI report, notification, or UI logic
- broad warehouse refresh orchestration beyond preserving existing local helper behavior
- credentialed source behavior

## Testing Requirements

Default tests must remain offline.

Run:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Run focused tests, likely:

`python3 -m unittest tests/datahub/test_akshare_a_share_corporate_actions_adapter.py`

`python3 -m unittest -v tests/datahub/test_akshare_a_share_corporate_actions_live.py`

Run related regressions if shared AKShare adapter behavior or exports are touched:

`python3 -m unittest tests/datahub/test_akshare_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_a_share_instrument_master_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_a_share_instrument_master_live.py`

`python3 -m unittest tests/datahub/test_source.py`

`python3 -m unittest tests/datahub/test_quality.py`

If source-catalog tests are touched, run:

`python3 -m unittest tests/datahub/test_source_catalog.py`

Run gated live smoke when enabled:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_corporate_actions_live.py`

## Acceptance Criteria

The task is acceptable when:

- AKShare A-share `CORPORATE_ACTIONS` dividend-slice adapter exists under `quant/datahub/**`
- scope remains limited to one-symbol A-share corporate-action/dividend records for `DatasetName.CORPORATE_ACTIONS`
- offline tests pass and remain deterministic
- default tests remain offline-safe
- malformed payload, required-field, duplicate, symbol, event-date, value, and raw-payload-ref boundaries are covered
- gated live smoke exists and result is truthfully recorded
- live-enabled PASS is provided for closure; if live-enabled skip/fail occurs because of network/proxy/DNS/TLS/upstream/source availability, the report must include root-cause evidence and feasible fixes attempted, and controller closure will require the rework/review gate in `AGENTS.md`
- no future-phase module contains new logic
- report exists at `coordination/reports/TASK-027_REPORT.md`

## Report Path

`coordination/reports/TASK-027_REPORT.md`

## Review Path

`coordination/reviews/TASK-027_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-027_INTEGRATION.md`

## Out of Scope

Everything outside a narrow DataHub A-share corporate-actions dividend adapter and tests is out of scope.
