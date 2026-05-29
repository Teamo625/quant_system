# TASK-034: DataHub AKShare Hong Kong Valuation Snapshot Adapter

## Task ID

TASK-034

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

TASK-033 has been accepted and integrated. It completed the AKShare one-symbol Hong Kong stock `CORPORATE_ACTIONS` dividend/corporate-action adapter under source id `akshare_cn_hk_public_family`, with deterministic offline tests and live-enabled PASS evidence.

Phase 2 remains open. The roadmap still requires Hong Kong stock valuation coverage where available. The source catalog already lists `DatasetName.VALUATION_SNAPSHOT` under `akshare_cn_hk_public_family`, while HK full-data stable coverage currently includes instrument master, daily bars, and corporate actions. The next narrow executable HK source slice is therefore one-symbol HK valuation snapshot coverage.

This task must implement only the Hong Kong stock one-symbol valuation snapshot slice of `DatasetName.VALUATION_SNAPSHOT`.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-034_DATAHUB_AKSHARE_HK_VALUATION_SNAPSHOT_ADAPTER.md`

## Goal

Implement a narrow AKShare-backed Hong Kong stock valuation snapshot adapter for `DatasetName.VALUATION_SNAPSHOT`, focused on one requested HK stock symbol, with deterministic offline tests and mandatory gated live smoke coverage.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-034_REPORT.md`

Suggested implementation locations:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `quant/datahub/source_catalog.py` only if strict catalog assertion alignment is required
- `tests/datahub/test_akshare_hk_valuation_snapshot_adapter.py`
- `tests/datahub/test_akshare_hk_valuation_snapshot_live.py`
- `tests/datahub/test_source_catalog.py` only if source-catalog expectations change

Do not change `quant/datahub/datasets.py` unless the execution window finds source-truth evidence that an existing optionality boundary is wrong and the minimal change is essential. If such a schema change is made, it must be tested and truthfully reported.

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

### 1. AKShare HK valuation snapshot adapter

Add a narrow adapter for:

- source id: `akshare_cn_hk_public_family`
- source display name: `AKShare CN/HK Public Family`
- supported dataset in this task: `DatasetName.VALUATION_SNAPSHOT`
- market output: `HK`
- initial scope: one requested Hong Kong stock symbol, latest bounded valuation snapshot

Known bounded AKShare routes available at controller dispatch time:

- `akshare.stock_hk_valuation_comparison_em(symbol="<5-digit-code>")`
  - observed useful columns for `00700`: `市盈率-TTM`, `市净率-MRQ`, `市销率-TTM`
- `akshare.stock_hk_indicator_eniu(symbol="hk<5-digit-code>", indicator="<metric>")`
  - useful indicators may include `市盈率`, `市净率`, `市值`, and `股息率`
- `akshare.stock_hk_valuation_baidu(symbol="<5-digit-code>", indicator="<metric>", period="近一年")`
  - may provide `总市值`, `市盈率(TTM)`, and `市净率`, but the controller observed a local SSL certificate failure for this route, so it must be treated as an optional bounded route unless the execution environment proves it reliable

The adapter should:

- implement the existing `SourceAdapter` protocol
- use lazy/optional AKShare imports
- reject unsupported datasets clearly
- require exactly one requested HK stock symbol
- accept canonical HK symbols such as `00700.HK` and source-native numeric forms such as `00700`
- reject invalid, A-share, ETF/fund, index, malformed, empty, or unsupported market symbols clearly
- normalize output `symbol` to canonical HK form, such as `00700.HK`
- produce one bounded valuation snapshot for the requested symbol
- support `start_date` / `end_date` by deterministic client-side filtering after normalized `trade_date`
- support DataFrame-like payload and list-of-mapping payload fixtures
- fail clearly on malformed payload, missing required source fields for emitted metrics, invalid dates, invalid numeric values, invalid required strings, or non-serializable values

Normalize output records to `VALUATION_SNAPSHOT` contract fields:

- `symbol`: canonical HK symbol, e.g. `00700.HK`
- `market`: `HK`
- `trade_date`: source valuation date when present; otherwise deterministic snapshot date from injectable clock
- `pe_ttm`: trailing PE, when truthfully provided by source
- `pb`: price-to-book, when truthfully provided by source
- `ps_ttm`: trailing PS, when truthfully provided by source
- `dividend_yield`: dividend yield, when truthfully provided by source
- `market_cap`: market capitalization, normalized consistently as HKD amount when source units are clear
- `float_market_cap`: float market capitalization, normalized consistently as HKD amount when source units are clear
- `source`: `akshare_cn_hk_public_family`
- optional `source_ts` when the source exposes a trustworthy source timestamp
- `ingested_at`: from injectable clock for deterministic tests
- `schema_version`: from `DatasetRegistry`

Do not invent placeholder valuation or market-cap values solely to satisfy schema requiredness.

### 2. Source-truth and route boundary

- Keep route order bounded and explicit.
- Fetch only the requested single HK stock symbol.
- Do not perform broad HK universe ingestion.
- If multiple bounded routes contribute the same field, define deterministic precedence and test it.
- If a route is unavailable because of network/proxy/DNS/TLS/SSL/upstream/source availability, classify it for live skip diagnostics or fallback only; do not mask adapter/schema bugs.
- Contract or normalization failures for emitted fields must remain hard failures.
- If no bounded route can truthfully provide the currently required fields for a valid record, report the source-truth limitation clearly. Do not synthesize fake data.

### 3. Duplicate and identity boundary

- Prefer one normalized snapshot record for the requested `(symbol, trade_date, source)`.
- Benign exact duplicate route rows may be deterministically deduplicated.
- Conflicting duplicate rows for the same stable valuation identity must hard-fail.
- If multiple route rows have different dates, choose a deterministic latest bounded snapshot only when the fields can be truthfully joined; otherwise fail clearly or emit only a complete valid source-truth record.

### 4. Source catalog alignment

The catalog already includes `DatasetName.VALUATION_SNAPSHOT` under `akshare_cn_hk_public_family`.

If implementation proves stable HK valuation coverage, minimally align `InformationDomain.HK_STOCK_FULL_DATA` to include `DatasetName.VALUATION_SNAPSHOT`. Do not add broad source claims beyond the implemented slice.

### 5. Offline tests

Add deterministic offline tests proving:

- adapter satisfies `SourceAdapter`
- `fetch_source_result(...)` records pass `DatasetRegistry.validate_record(...)`
- source payload conversion from DataFrame-like and list-of-mapping works
- canonical and source-native HK symbol normalization works
- invalid, ambiguous, A-share, ETF/fund, and index-like symbol filters fail clearly
- route symbol conversion is deterministic
- `start_date` / `end_date` filtering uses normalized `trade_date`
- `trade_date`, valuation fields, `market_cap`, optional fields, `source`, `ingested_at`, and `schema_version` are populated correctly
- source unit conversion for market-cap fields is deterministic
- optional metric handling does not invent placeholder values
- route precedence, duplicate, and conflicting-duplicate boundaries are preserved
- malformed payloads and missing required source fields fail clearly
- default tests remain offline-safe

If source-catalog coverage is updated, add or update focused catalog tests.

### 6. Mandatory live smoke test

Because TASK-034 is a real-source adapter task, gated live smoke is mandatory.

Add `tests/datahub/test_akshare_hk_valuation_snapshot_live.py` or equivalent that:

- is skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1`
- uses no credentials
- fetches a minimal bounded live sample for a stable HK stock such as `00700.HK`
- validates at least one normalized record via `DatasetRegistry.validate_record(...)`
- asserts `source=akshare_cn_hk_public_family`, `market=HK`, and a canonical HK symbol
- asserts required emitted valuation/core market-cap fields are numeric
- classifies environment/source unavailability as explicit `skipTest(...)`
- preserves adapter/schema/normalization issues as failures

If live-enabled run fails/skips due to network/proxy/DNS/TLS/SSL/upstream/source availability, the report must include root-cause evidence and feasible repository-level fixes attempted. Controller closure will require the rework/review gate in `AGENTS.md`.

## Do Not Implement

Do not implement:

- broad HK valuation universe ingestion
- HK capital flow, HK trading calendar, HK ETF/fund profile, or broad HK instrument expansion
- A-share, ETF/fund, index, global, macro, policy, news, or announcement expansion
- trading strategies, signal generation, scanner logic, AI reports, notifications, UI, or automated trading
- feature engineering or derived analytics
- storage refresh orchestration beyond what is needed for this adapter test surface

## Testing Requirements

Default tests must remain offline.

Run:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Run focused tests, likely:

`python3 -m unittest tests/datahub/test_akshare_hk_valuation_snapshot_adapter.py`

`python3 -m unittest -v tests/datahub/test_akshare_hk_valuation_snapshot_live.py`

Run related regressions if shared AKShare adapter behavior, exports, dataset schema, or source catalog is touched:

`python3 -m unittest tests/datahub/test_akshare_hk_corporate_actions_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_a_share_valuation_snapshot_adapter.py`

`python3 -m unittest tests/datahub/test_datasets.py`

`python3 -m unittest tests/datahub/test_source.py`

If source-catalog tests are touched, run:

`python3 -m unittest tests/datahub/test_source_catalog.py`

Run gated live smoke when enabled:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_valuation_snapshot_live.py`

## Acceptance Criteria

The task is acceptable when:

- AKShare-backed HK `VALUATION_SNAPSHOT` adapter exists under `quant/datahub/**`
- scope remains limited to one-symbol Hong Kong stock valuation snapshot records for `DatasetName.VALUATION_SNAPSHOT`
- source id remains `akshare_cn_hk_public_family`
- no placeholder valuation or market-cap values are invented solely to satisfy schema requiredness
- offline tests pass and remain deterministic
- default tests remain offline-safe
- malformed payload, required-field, optional-field, duplicate, symbol, date, numeric, source-unit, and route precedence boundaries are covered
- gated live smoke exists and result is truthfully recorded
- live-enabled PASS is provided for closure; if live-enabled skip/fail occurs because of network/proxy/DNS/TLS/SSL/upstream/source availability, the report must include root-cause evidence and feasible fixes attempted, and controller closure will require the rework/review gate in `AGENTS.md`
- no future-phase module contains new logic
- report exists at `coordination/reports/TASK-034_REPORT.md`

## Report Path

`coordination/reports/TASK-034_REPORT.md`

## Review Path

`coordination/reviews/TASK-034_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-034_INTEGRATION.md`

## Out of Scope

Everything outside a narrow DataHub AKShare HK valuation snapshot adapter and tests is out of scope.
