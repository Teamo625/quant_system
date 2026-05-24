# TASK-028: DataHub AKShare A-share Valuation Snapshot Adapter

## Task ID

TASK-028

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

TASK-027 has been accepted and integrated. It completed the AKShare A-share `CORPORATE_ACTIONS` dividend/corporate-action slice with deterministic offline tests and live-enabled PASS evidence.

Phase 2 remains open. The next narrow executable A-share source slice is valuation coverage. `DatasetName.VALUATION_SNAPSHOT` already has a stable contract and is listed under the no-credential `akshare_cn_hk_public_family` source family.

This task must implement only the A-share one-symbol valuation snapshot slice of `DatasetName.VALUATION_SNAPSHOT`.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-028_DATAHUB_AKSHARE_A_SHARE_VALUATION_SNAPSHOT_ADAPTER.md`

## Goal

Implement a narrow AKShare-backed A-share valuation snapshot adapter for `DatasetName.VALUATION_SNAPSHOT`, focused on one requested A-share stock symbol, with deterministic offline tests and mandatory gated live smoke coverage.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-028_REPORT.md`

Suggested implementation locations:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `quant/datahub/datasets.py` only for minimal source-truth optionality hardening described below
- `quant/datahub/source_catalog.py` only if strict catalog assertion alignment is required
- `tests/datahub/test_akshare_a_share_valuation_snapshot_adapter.py`
- `tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`
- `tests/datahub/test_datasets.py` only if minimal schema optionality is changed
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

### 1. AKShare A-share valuation snapshot adapter

Add a narrow adapter for:

- source id: `akshare_cn_hk_public_family`
- source display name: `AKShare CN/HK Public Family`
- supported dataset in this task: `DatasetName.VALUATION_SNAPSHOT`
- initial scope: one requested A-share stock symbol, latest bounded valuation snapshot

Recommended bounded AKShare routes:

- primary valuation metrics: `akshare.stock_zh_valuation_baidu(symbol="<6-digit-code>", indicator="<metric>", period="近一年")`
  - expected useful indicators include `市盈率(TTM)`, `市净率`, and `总市值`
- supplemental market-cap route: `akshare.stock_individual_info_em(symbol="<6-digit-code>")`
  - expected useful items include `总市值` and `流通市值`

Optional bounded route, only if needed and robust for the requested symbol:

- `akshare.stock_zh_valuation_comparison_em(symbol="<SH/SZ-prefixed-code>")`
  - may provide `市销率-TTM` and related peer-comparison metrics
  - missing columns or upstream response-shape changes must be handled as source unavailability for that optional metric, not as silent bad data

Do not add unbounded full-market collection in this task.

The adapter should:

- implement the existing `SourceAdapter` protocol
- use lazy/optional AKShare imports
- reject unsupported datasets clearly
- require exactly one requested A-share stock symbol
- accept canonical and raw 6-digit forms where feasible, such as `600000.SH`, `000001.SZ`, `920000.BJ`, and `600000`
- reject invalid, HK, ETF/fund, index, or ambiguous symbol filters clearly
- infer canonical symbol suffix from A-share code prefix:
  - `.SH` for Shanghai stock codes such as `600000` and `688000`
  - `.SZ` for Shenzhen stock codes such as `000001` and `300000`
  - `.BJ` for Beijing stock codes such as `920000` / `830000`
- convert AKShare route symbol formats deterministically, such as:
  - Baidu/source detail routes: raw 6-digit code
  - Eastmoney comparison route, if used: `SH600000` / `SZ000001` / `BJ920000` when supported by the route
- produce the latest bounded snapshot for the requested symbol
- support `start_date` / `end_date` by deterministic client-side filtering after normalized `trade_date`
- support DataFrame-like payload and list-of-mapping payload fixtures
- fail clearly on malformed payload, missing required source fields for emitted metrics, invalid dates, invalid numeric values, invalid required strings, or non-serializable values

Normalize output records to `VALUATION_SNAPSHOT` contract fields:

- `symbol`: canonical A-share symbol, e.g. `600000.SH`
- `market`: `CN`
- `trade_date`: source valuation date when present; otherwise deterministic snapshot date from injectable clock
- `pe_ttm`: trailing PE, when truthfully provided by source
- `pb`: price-to-book, when truthfully provided by source
- `ps_ttm`: trailing PS, when truthfully provided by source
- `dividend_yield`: dividend yield, when truthfully provided by source
- `market_cap`: market capitalization, normalized consistently as CNY amount when source units are clear
- `float_market_cap`: float market capitalization, normalized consistently as CNY amount when source units are clear
- `source`: `akshare_cn_hk_public_family`
- optional `source_ts` when the source exposes a trustworthy source timestamp
- `ingested_at`: from injectable clock for deterministic tests
- `schema_version`: from `DatasetRegistry`

### 2. Source-truth and schema optionality boundary

Do not synthesize fake valuation values solely to satisfy current required fields.

If a bounded public route cannot truthfully provide an individual-stock valuation metric that is currently required by `DatasetName.VALUATION_SNAPSHOT`, the execution window may make a minimal schema hardening change in `quant/datahub/datasets.py`:

- only change `ps_ttm` and/or `dividend_yield` to `required=False` if source evidence shows they are not reliably available for the bounded routes in this task
- do not remove or rename fields
- do not change `symbol`, `market`, `trade_date`, `pe_ttm`, `pb`, `market_cap`, `float_market_cap`, `source`, `ingested_at`, or `schema_version` requiredness
- update the focused dataset tests if requiredness changes
- record the optionality change and rationale in `coordination/reports/TASK-028_REPORT.md` so the controller can update stable-interface notes after review/integration

Contract or normalization failures for emitted fields must remain hard failures. Environment/source unavailability may be classified for live skip diagnostics, but must not mask adapter bugs.

### 3. Route and duplicate boundary

- Keep route order bounded and explicit.
- Prefer one normalized snapshot record for the requested symbol and selected `trade_date`.
- If multiple routes contribute the same field, define deterministic precedence and test it.
- If multiple route rows produce identical snapshot identities and identical values, deduplicate deterministically.
- Conflicting duplicate rows for the same stable valuation identity must hard-fail. At minimum, conflicts for the same `(symbol, trade_date, source)` must not silently overwrite earlier data.

### 4. Source catalog alignment

The catalog already includes `DatasetName.VALUATION_SNAPSHOT` under `akshare_cn_hk_public_family`.

If needed, minimally align `akshare_cn_hk_public_family` information coverage so `InformationDomain.A_SHARE_FULL_DATA` includes the stable valuation dataset. Do not add broad source claims beyond the implemented slice.

### 5. Offline tests

Add deterministic offline tests proving:

- adapter satisfies `SourceAdapter`
- `fetch_source_result(...)` records pass `DatasetRegistry.validate_record(...)`
- source payload conversion from DataFrame-like and list-of-mapping works
- canonical and raw 6-digit symbol normalization works
- invalid, ambiguous, HK, ETF/fund, and index-like symbol filters fail clearly
- route symbol conversion is deterministic
- `start_date` / `end_date` filtering uses normalized `trade_date`
- `trade_date`, valuation fields, `market_cap`, `float_market_cap`, `source`, `ingested_at`, and `schema_version` are populated correctly
- source unit conversion for market-cap fields is deterministic
- optional metric handling does not invent placeholder values
- duplicate and conflicting-duplicate boundaries are preserved
- malformed payloads and missing required source fields fail clearly
- default tests remain offline-safe

If schema optionality is changed, add or update focused tests proving:

- required field expectations match the minimal source-truth adjustment
- emitted records still validate through `DatasetRegistry.validate_record(...)`
- existing dataset semantic rules still behave correctly

### 6. Mandatory live smoke test

Because TASK-028 is a real-source adapter task, gated live smoke is mandatory.

Add `tests/datahub/test_akshare_a_share_valuation_snapshot_live.py` (or equivalent) that:

- is skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1`
- uses no credentials
- fetches a minimal bounded live sample for a stable A-share symbol such as `600000.SH`
- validates at least one normalized record via `DatasetRegistry.validate_record(...)`
- asserts `source=akshare_cn_hk_public_family`, `market=CN`, and a canonical A-share symbol
- asserts at least the required valuation/core market-cap fields emitted by this adapter are numeric
- classifies environment/source unavailability as explicit `skipTest(...)`
- preserves adapter/schema/normalization issues as failures

If live-enabled run fails/skips due to network/proxy/DNS/TLS/upstream/source availability, report must include root-cause evidence and feasible repository-level fixes attempted.

## Do Not Implement

Do not implement:

- HK, ETF, fund, index, policy, capital-flow, or corporate-action adapters
- broad full-market valuation ingestion
- derived feature logic, scanner filters, strategy logic, AI reports, notifications, or UI
- broad warehouse refresh orchestration beyond preserving existing local helper behavior
- credentialed source behavior

## Testing Requirements

Default tests must remain offline.

Run:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Run focused tests, likely:

`python3 -m unittest tests/datahub/test_akshare_a_share_valuation_snapshot_adapter.py`

`python3 -m unittest -v tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`

Run related regressions if shared AKShare adapter behavior, dataset schema, source catalog, or exports are touched:

`python3 -m unittest tests/datahub/test_akshare_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_a_share_corporate_actions_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_a_share_instrument_master_adapter.py`

`python3 -m unittest tests/datahub/test_datasets.py`

`python3 -m unittest tests/datahub/test_source.py`

`python3 -m unittest tests/datahub/test_quality.py`

If source-catalog tests are touched, run:

`python3 -m unittest tests/datahub/test_source_catalog.py`

Run gated live smoke when enabled:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`

## Acceptance Criteria

The task is acceptable when:

- AKShare A-share `VALUATION_SNAPSHOT` adapter exists under `quant/datahub/**`
- scope remains limited to one-symbol A-share valuation snapshot records for `DatasetName.VALUATION_SNAPSHOT`
- no placeholder valuation values are invented solely to satisfy schema requiredness
- any minimal schema optionality change is justified, tested, and truthfully reported
- offline tests pass and remain deterministic
- default tests remain offline-safe
- malformed payload, required-field, optional-field, duplicate, symbol, date, numeric, source-unit, and route precedence boundaries are covered
- gated live smoke exists and result is truthfully recorded
- live-enabled PASS is provided for closure; if live-enabled skip/fail occurs because of network/proxy/DNS/TLS/upstream/source availability, the report must include root-cause evidence and feasible fixes attempted, and controller closure will require the rework/review gate in `AGENTS.md`
- no future-phase module contains new logic
- report exists at `coordination/reports/TASK-028_REPORT.md`

## Report Path

`coordination/reports/TASK-028_REPORT.md`

## Review Path

`coordination/reviews/TASK-028_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-028_INTEGRATION.md`

## Out of Scope

Everything outside a narrow DataHub A-share valuation snapshot adapter and tests is out of scope.
