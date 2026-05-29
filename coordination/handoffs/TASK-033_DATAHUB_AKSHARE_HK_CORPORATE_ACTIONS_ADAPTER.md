# TASK-033: DataHub AKShare Hong Kong Corporate Actions Adapter

## Task ID

TASK-033

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

TASK-032 has been accepted and integrated. It completed the AKShare one-symbol Hong Kong stock `INSTRUMENT_MASTER` adapter under source id `akshare_cn_hk_public_family`, with deterministic offline tests and live-enabled PASS evidence.

Phase 2 remains open. Hong Kong stock full-data coverage now includes HK daily bars, HK company announcements, and HK one-symbol instrument reference coverage. The next narrow executable HK source slice is dividend/corporate-action records for one Hong Kong stock symbol.

This task must implement only the Hong Kong stock dividend/corporate-actions slice of `DatasetName.CORPORATE_ACTIONS`.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-033_DATAHUB_AKSHARE_HK_CORPORATE_ACTIONS_ADAPTER.md`

## Goal

Implement a narrow AKShare-backed Hong Kong stock corporate actions adapter for `DatasetName.CORPORATE_ACTIONS`, focused on dividend/distribution records for one requested HK stock symbol, with deterministic offline tests and mandatory gated live smoke coverage.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-033_REPORT.md`

Suggested implementation locations:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `tests/datahub/test_akshare_hk_corporate_actions_adapter.py`
- `tests/datahub/test_akshare_hk_corporate_actions_live.py`
- existing DataHub tests only as needed for import/export updates

`quant/datahub/source_catalog.py` and `tests/datahub/test_source_catalog.py` may be touched only if strict catalog assertion alignment is required. The catalog already declares `DatasetName.CORPORATE_ACTIONS` under `akshare_cn_hk_public_family`.

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

### 1. AKShare HK corporate actions adapter

Add a narrow adapter for:

- source id: `akshare_cn_hk_public_family`
- source display name: `AKShare CN/HK Public Family`
- supported dataset in this task: `DatasetName.CORPORATE_ACTIONS`
- market output: `HK`
- initial scope: dividend/distribution records for one requested Hong Kong stock symbol

Recommended bounded AKShare route:

- primary: `akshare.stock_hk_dividend_payout_em(symbol="<5-digit-code>")`

Optional bounded fallback, if needed for live-source resilience:

- `akshare.stock_hk_fhpx_detail_ths(symbol="<non-padded-or-source-native-code>")`

At controller dispatch time, the local AKShare version exposes `stock_hk_dividend_payout_em`; a sample call for `00700` returns fields including `最新公告日期`, `财政年度`, `分红方案`, `分配类型`, `除净日`, `截至过户日`, and `发放日`.

The adapter should:

- implement the existing `SourceAdapter` protocol
- use lazy/optional AKShare imports
- reject unsupported datasets clearly
- require exactly one requested HK stock symbol
- accept canonical HK symbols such as `00700.HK` and source-native numeric forms such as `00700`
- reject invalid, A-share, ETF/fund, index, malformed, empty, or unsupported market symbols clearly
- normalize output `symbol` to canonical HK form, such as `00700.HK`
- support `start_date` / `end_date` by deterministic client-side filtering after normalized `event_date`
- support DataFrame-like payload and list-of-mapping payload fixtures
- fail clearly on malformed payload, missing required source fields, invalid event dates, invalid required strings, invalid numeric extraction, or non-serializable values

Normalize output records to `CORPORATE_ACTIONS` contract fields:

- `symbol`: canonical HK symbol, e.g. `00700.HK`
- `market`: `HK`
- `event_date`: prefer source ex-dividend/ex-rights date such as `除净日`; otherwise use announcement or payout date only when source truth supports it
- `event_type`: stable string, initially `dividend`
- `value`: structured object with available dividend/corporate-action details, including cash dividend/distribution text, fiscal year, distribution type, announcement date, register-book period, payout date, raw plan text, parsed cash amount when safely extractable, and raw currency when present
- `raw_payload_ref`: deterministic stable reference derived from canonical symbol, event type, normalized event date, and a stable serialization or hash of the source row
- `source`: `akshare_cn_hk_public_family`
- optional `source_ts` when the source exposes a trustworthy source timestamp, such as announcement date
- `ingested_at`: from injectable clock for deterministic tests
- `schema_version`: from `DatasetRegistry`

Do not invent placeholder dividend amounts or dates. Preserve source-truth text when reliable parsing is not possible.

### 2. Route and duplicate boundary

- Keep route order bounded and explicit.
- Fetch only the requested single HK stock symbol.
- Do not perform broad HK universe ingestion.
- Network/proxy/DNS/TLS/upstream/source availability failures may be classified for live skip diagnostics, but DataHub contract/normalization failures must remain hard failures.
- Benign exact duplicate corporate-action rows may be deterministically deduplicated.
- Conflicting duplicate rows for the same stable corporate-action identity must hard-fail.
- If fallback routes are used, records from multiple routes must not create duplicate logical events without deterministic dedupe or a clear hard failure.

### 3. Source catalog alignment

The source catalog already includes `DatasetName.CORPORATE_ACTIONS` under `akshare_cn_hk_public_family`.

Do not add broad source claims. Only perform minimal source-catalog assertion updates if required by implemented stable behavior.

### 4. Offline tests

Add deterministic offline tests proving:

- adapter satisfies `SourceAdapter`
- `fetch_source_result(...)` records pass `DatasetRegistry.validate_record(...)`
- source payload conversion from DataFrame-like and list-of-mapping works
- symbol normalization accepts canonical and source-native HK numeric forms where feasible
- unsupported and ambiguous symbols fail clearly
- `start_date` / `end_date` filtering uses normalized `event_date`
- event-date fallback order is deterministic
- `event_type`, structured `value`, `raw_payload_ref`, `source`, `ingested_at`, and `schema_version` are populated correctly
- `raw_payload_ref` is deterministic for equivalent source rows
- duplicate and conflicting-duplicate boundaries are preserved
- malformed payloads and missing required source fields fail clearly
- default tests remain offline-safe

### 5. Mandatory live smoke test

Because TASK-033 is a real-source adapter task, gated live smoke is mandatory.

Add `tests/datahub/test_akshare_hk_corporate_actions_live.py` or equivalent that:

- is skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1`
- uses no credentials
- fetches a minimal bounded live sample for a stable dividend-history HK stock such as `00700.HK`
- validates at least one normalized record via `DatasetRegistry.validate_record(...)`
- asserts `source=akshare_cn_hk_public_family`, `market=HK`, `event_type=dividend`, and a canonical HK symbol
- classifies environment/source unavailability as explicit `skipTest(...)`
- preserves adapter/schema/normalization issues as failures

If live-enabled run fails/skips due to network/proxy/DNS/TLS/upstream/source availability, the report must include root-cause evidence and feasible repository-level fixes attempted. Controller closure will require the rework/review gate in `AGENTS.md`.

## Do Not Implement

Do not implement:

- broad HK corporate-action universe ingestion
- HK valuation, HK capital flow, HK trading calendar, HK ETF/fund profile, or broad HK instrument expansion
- A-share, ETF/fund, index, global, macro, policy, news, or announcement expansion
- trading strategies, signal generation, scanner logic, AI reports, notifications, UI, or automated trading
- feature engineering or derived analytics
- storage refresh orchestration beyond what is needed for this adapter test surface

## Testing Requirements

Default tests must remain offline.

Run:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Run focused tests, likely:

`python3 -m unittest tests/datahub/test_akshare_hk_corporate_actions_adapter.py`

`python3 -m unittest -v tests/datahub/test_akshare_hk_corporate_actions_live.py`

Run related regressions if shared AKShare adapter behavior, exports, dataset schema, or source catalog is touched:

`python3 -m unittest tests/datahub/test_akshare_hk_instrument_master_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_a_share_corporate_actions_adapter.py`

`python3 -m unittest tests/datahub/test_datasets.py`

`python3 -m unittest tests/datahub/test_source.py`

If source-catalog tests are touched, run:

`python3 -m unittest tests/datahub/test_source_catalog.py`

Run gated live smoke when enabled:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_corporate_actions_live.py`

## Acceptance Criteria

The task is acceptable when:

- AKShare-backed HK `CORPORATE_ACTIONS` dividend-slice adapter exists under `quant/datahub/**`
- scope remains limited to one-symbol Hong Kong stock dividend/corporate-action records for `DatasetName.CORPORATE_ACTIONS`
- source id remains `akshare_cn_hk_public_family`
- offline tests pass and remain deterministic
- default tests remain offline-safe
- malformed payload, required-field, duplicate, symbol, event-date, value, and raw-payload-ref boundaries are covered
- gated live smoke exists and result is truthfully recorded
- live-enabled PASS is provided for closure; if live-enabled skip/fail occurs because of network/proxy/DNS/TLS/upstream/source availability, the report must include root-cause evidence and feasible fixes attempted, and controller closure will require the rework/review gate in `AGENTS.md`
- no future-phase module contains new logic
- report exists at `coordination/reports/TASK-033_REPORT.md`

## Report Path

`coordination/reports/TASK-033_REPORT.md`

## Review Path

`coordination/reviews/TASK-033_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-033_INTEGRATION.md`

## Out of Scope

Everything outside a narrow DataHub AKShare HK corporate-actions dividend adapter and tests is out of scope.
