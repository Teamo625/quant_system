# TASK-024: DataHub AKShare China Macro Adapter

## Task ID

TASK-024

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

TASK-023 has been accepted and integrated. It completed HKEX `COMPANY_ANNOUNCEMENTS` coverage, including the requested symbol-filter rework and closure-ready live-enabled PASS evidence.

Phase 2 remains open. The next narrow executable source slice is macroeconomic data coverage. `DatasetName.MACRO_INDICATOR_MASTER` and `DatasetName.MACRO_OBSERVATIONS` already have stable contracts and are listed under the no-credential `macro_policy_public_sources` source family.

This task must implement only the first China macro public-source slice for:

- `DatasetName.MACRO_INDICATOR_MASTER`
- `DatasetName.MACRO_OBSERVATIONS`

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-024_DATAHUB_AKSHARE_CHINA_MACRO_ADAPTER.md`

## Goal

Implement a narrow AKShare-backed China macro adapter for selected macro indicator definitions and observations, with deterministic offline tests and mandatory gated live smoke coverage.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-024_REPORT.md`

Suggested implementation locations:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `quant/datahub/source_catalog.py` only if strict catalog assertion alignment is required
- `tests/datahub/test_akshare_china_macro_adapter.py`
- `tests/datahub/test_akshare_china_macro_live.py`
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

### 1. AKShare China macro adapter

Add a narrow adapter for:

- source id: `macro_policy_public_sources`
- source display name: `Macro and Policy Public Sources`
- supported datasets in this task:
  - `DatasetName.MACRO_INDICATOR_MASTER`
  - `DatasetName.MACRO_OBSERVATIONS`
- initial macro scope: selected no-credential China macro indicators available through the installed AKShare version

Recommended initial indicators:

- `CPI_CN_YOY` from `akshare.macro_china_cpi_yearly`
- `PPI_CN_YOY` from `akshare.macro_china_ppi_yearly`
- `GDP_CN_YOY` from `akshare.macro_china_gdp_yearly`

The adapter should:

- implement the existing `SourceAdapter` protocol
- use lazy/optional AKShare imports
- reject unsupported datasets clearly
- reject non-empty `symbols` clearly; macro indicator filtering is not part of the current `SourceAdapter` contract slice
- support `start_date` and `end_date` by filtering normalized `observation_date`
- return deterministic static master records for `MACRO_INDICATOR_MASTER`
- fetch and normalize observation records for `MACRO_OBSERVATIONS`
- normalize output records to the relevant `DatasetRegistry` contract
- set `source=macro_policy_public_sources`
- set `schema_version` from `DatasetRegistry`
- set `ingested_at` from injectable clock for deterministic tests
- support DataFrame-like payload and list-of-mapping payload fixtures
- fail clearly on malformed payload, missing required fields, invalid observation date, invalid numeric value, unsupported dataset, unsupported symbols, or invalid required string fields

### 2. Macro master normalization

For each selected indicator, emit a `MACRO_INDICATOR_MASTER` record with:

- `indicator_id`
- `indicator_name`
- `region=CN`
- `frequency`
- `unit=percent`
- `category`
- `source=macro_policy_public_sources`
- optional `source_ts`
- `ingested_at`
- `schema_version`

Use stable metadata. Suggested values:

- `CPI_CN_YOY`: name `China CPI YoY`, frequency `monthly`, category `inflation`
- `PPI_CN_YOY`: name `China PPI YoY`, frequency `monthly`, category `inflation`
- `GDP_CN_YOY`: name `China GDP YoY`, frequency `quarterly`, category `growth`

### 3. Macro observation normalization

For each source row, emit a `MACRO_OBSERVATIONS` record with:

- `indicator_id`
- `region=CN`
- `observation_date`
- `value`
- optional `release_date`
- optional `is_preliminary`
- `source=macro_policy_public_sources`
- optional `source_ts`
- `ingested_at`
- `schema_version`

Field handling requirements:

- source date should be accepted from common AKShare/Jin10 fields such as `日期`, `date`, or `observation_date`
- source value should be accepted from common fields such as `今值`, `value`, or `actual`
- if the source only provides one date field, use it as `observation_date` and leave `release_date` absent
- do not infer `is_preliminary` unless the source explicitly provides a reliable boolean-like value
- return an empty result only for an exactly empty upstream payload; malformed rows with missing required fields must fail

### 4. Route and duplicate boundary

- Keep route order bounded and explicit.
- Network/proxy/DNS/TLS/upstream/source availability failures may be classified for live skip diagnostics, but DataHub contract/normalization failures must remain hard failures.
- Benign exact duplicate observation rows may be deterministically deduplicated.
- Conflicting duplicate rows for the same `(indicator_id, observation_date)` must hard-fail.

### 5. Source catalog alignment

The catalog already includes `DatasetName.MACRO_INDICATOR_MASTER` and `DatasetName.MACRO_OBSERVATIONS` under `macro_policy_public_sources`.

Do not add broad source claims. Only perform minimal source-catalog assertion or stage updates if required by implemented stable behavior.

### 6. Offline tests

Add deterministic offline tests proving:

- adapter satisfies `SourceAdapter`
- `MACRO_INDICATOR_MASTER` records pass `DatasetRegistry.validate_record(...)`
- `MACRO_OBSERVATIONS` records pass `DatasetRegistry.validate_record(...)`
- source payload conversion from DataFrame-like and list-of-mapping works
- `start_date` / `end_date` filtering is deterministic
- non-empty `symbols` are rejected clearly
- required field, date parsing, optional field, and numeric parsing behavior is covered
- duplicate boundary is preserved
- malformed payloads fail clearly
- default tests remain offline-safe

### 7. Mandatory live smoke test

Because TASK-024 is a real-source adapter task, gated live smoke is mandatory.

Add `tests/datahub/test_akshare_china_macro_live.py` (or equivalent) that:

- is skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1`
- uses no credentials
- fetches a minimal bounded live sample
- validates at least one `MACRO_INDICATOR_MASTER` record via `DatasetRegistry.validate_record(...)`
- validates at least one `MACRO_OBSERVATIONS` record via `DatasetRegistry.validate_record(...)`
- classifies environment/source unavailability as explicit `skipTest(...)`
- preserves adapter/schema issues as failures

If live-enabled run fails/skips due to network/proxy/DNS/TLS/upstream/source availability, report must include root-cause evidence and feasible repository-level fixes attempted.

## Do Not Implement

Do not implement:

- policy document adapters
- additional macro domains beyond the selected China macro indicators above
- trading strategies, signal generation, scanner logic, AI reports, notifications, or UI
- broad macro feature engineering or derived indicators
- storage refresh orchestration beyond what is needed for this adapter test surface

## Testing Requirements

Default tests must remain offline.

Run:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Run focused tests, likely:

`python3 -m unittest tests/datahub/test_akshare_china_macro_adapter.py`

`python3 -m unittest -v tests/datahub/test_akshare_china_macro_live.py`

Run related regressions if shared AKShare adapter behavior or exports are touched:

`python3 -m unittest tests/datahub/test_akshare_news_events_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_global_equity_snapshot_adapter.py`

`python3 -m unittest tests/datahub/test_source.py`

If source-catalog tests are touched, run:

`python3 -m unittest tests/datahub/test_source_catalog.py`

Run gated live smoke when enabled:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_china_macro_live.py`

## Acceptance Criteria

The task is acceptable when:

- AKShare-backed China macro adapter exists under `quant/datahub/**`
- scope remains limited to `DatasetName.MACRO_INDICATOR_MASTER` and `DatasetName.MACRO_OBSERVATIONS`
- offline tests pass and remain deterministic
- default tests remain offline-safe
- malformed payload, required-field, duplicate, symbol rejection, date, numeric, and date-range boundaries are covered
- gated live smoke exists and result is truthfully recorded
- live-enabled PASS is provided for closure; if live-enabled skip/fail occurs because of network/proxy/DNS/TLS/upstream/source availability, the report must include root-cause evidence and feasible fixes attempted, and controller closure will require the rework/review gate in `AGENTS.md`
- no future-phase module contains new logic
- report exists at `coordination/reports/TASK-024_REPORT.md`

## Report Path

`coordination/reports/TASK-024_REPORT.md`

## Review Path

`coordination/reviews/TASK-024_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-024_INTEGRATION.md`

## Out of Scope

Everything outside a narrow DataHub China macro source slice and tests is out of scope.
