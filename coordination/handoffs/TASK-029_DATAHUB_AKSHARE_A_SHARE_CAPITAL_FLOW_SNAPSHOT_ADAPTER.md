# TASK-029: DataHub AKShare A-share Capital Flow Snapshot Adapter

## Task ID

TASK-029

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

TASK-028 has been accepted and integrated. It completed the AKShare A-share one-symbol `VALUATION_SNAPSHOT` adapter after live-network rework, including live-enabled PASS evidence. During TASK-028, `float_market_cap` was made optional to preserve source-truth behavior when a bounded supplemental route is unavailable.

Phase 2 remains open. The next narrow executable A-share source slice is capital-flow coverage. `DatasetName.CAPITAL_FLOW_SNAPSHOT` already has a stable contract and is listed under the no-credential `akshare_cn_hk_public_family` source family.

This task must implement only the A-share one-symbol capital-flow snapshot slice of `DatasetName.CAPITAL_FLOW_SNAPSHOT`.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-029_DATAHUB_AKSHARE_A_SHARE_CAPITAL_FLOW_SNAPSHOT_ADAPTER.md`

## Goal

Implement a narrow AKShare-backed A-share capital-flow snapshot adapter for `DatasetName.CAPITAL_FLOW_SNAPSHOT`, focused on one requested A-share stock symbol, with deterministic offline tests and mandatory gated live smoke coverage.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-029_REPORT.md`

Suggested implementation locations:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `quant/datahub/datasets.py` only for minimal source-truth optionality hardening described below
- `quant/datahub/source_catalog.py` only if strict catalog assertion alignment is required
- `tests/datahub/test_akshare_a_share_capital_flow_snapshot_adapter.py`
- `tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py`
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

### 1. AKShare A-share capital-flow snapshot adapter

Add a narrow adapter for:

- source id: `akshare_cn_hk_public_family`
- source display name: `AKShare CN/HK Public Family`
- supported dataset in this task: `DatasetName.CAPITAL_FLOW_SNAPSHOT`
- initial scope: one requested A-share stock symbol, recent daily capital-flow snapshots

Recommended bounded AKShare routes:

- primary capital-flow route: `akshare.stock_individual_fund_flow(stock="<6-digit-code>", market="<sh|sz|bj>")`
  - expected useful fields include `日期`, `主力净流入-净额`, `超大单净流入-净额`, `大单净流入-净额`, `中单净流入-净额`, `小单净流入-净额`, and related percentage fields
- supplemental turnover route: `akshare.stock_zh_a_hist(symbol="<6-digit-code>", period="daily", start_date="<YYYYMMDD>", end_date="<YYYYMMDD>", adjust="")`
  - expected useful field: `换手率`
- optional northbound route, only if bounded and robust for the requested symbol:
  - `akshare.stock_hsgt_individual_em(symbol="<6-digit-code>")`
  - expected useful fields may include `持股日期`, `今日增持资金`, or related holding-change fields

Do not add unbounded full-market collection in this task.

The adapter should:

- implement the existing `SourceAdapter` protocol
- use lazy/optional AKShare imports
- reject unsupported datasets clearly
- require exactly one requested A-share stock symbol
- accept canonical and raw 6-digit forms where feasible, such as `600000.SH`, `000001.SZ`, `920000.BJ`, and `600000`
- reject invalid, HK, ETF/fund, index, or ambiguous symbol filters clearly
- infer canonical symbol suffix and AKShare market argument from A-share code prefix:
  - `.SH` / `sh` for Shanghai stock codes such as `600000` and `688000`
  - `.SZ` / `sz` for Shenzhen stock codes such as `000001` and `300000`
  - `.BJ` / `bj` for Beijing stock codes such as `920000` / `830000`
- support `start_date` / `end_date` by deterministic client-side filtering after normalized `trade_date`
- pass bounded `start_date` / `end_date` to supplemental historical routes when supported, but still filter after normalization
- support DataFrame-like payload and list-of-mapping payload fixtures
- fail clearly on malformed payload, missing required source fields for emitted metrics, invalid dates, invalid numeric values, invalid required strings, or non-serializable values

Normalize output records to `CAPITAL_FLOW_SNAPSHOT` contract fields:

- `symbol`: canonical A-share symbol, e.g. `600000.SH`
- `market`: `CN`
- `trade_date`: normalized source flow date
- `net_inflow`: total net inflow only when truthfully provided by source, or from a documented explicit source total field
- `main_net_inflow`: main-force net inflow from source, initially expected from `主力净流入-净额`
- `northbound_net_buy`: northbound net buy only when truthfully provided by a bounded source
- `turnover_rate`: turnover rate only when truthfully provided by source
- `source`: `akshare_cn_hk_public_family`
- optional `source_ts` when the source exposes a trustworthy source timestamp
- `ingested_at`: from injectable clock for deterministic tests
- `schema_version`: from `DatasetRegistry`

### 2. Source-truth and schema optionality boundary

Do not synthesize fake capital-flow values solely to satisfy current required fields.

If a bounded public route cannot truthfully provide an individual-stock capital-flow metric that is currently required by `DatasetName.CAPITAL_FLOW_SNAPSHOT`, the execution window may make a minimal schema hardening change in `quant/datahub/datasets.py`:

- `main_net_inflow` should remain required for this slice unless the primary route cannot provide it
- `net_inflow`, `northbound_net_buy`, and/or `turnover_rate` may be changed to `required=False` if source evidence shows they are not reliably available from bounded one-symbol routes
- do not remove or rename fields
- do not change `symbol`, `market`, `trade_date`, `main_net_inflow`, `source`, `ingested_at`, or `schema_version` requiredness unless live/source evidence proves the primary route cannot support the task
- update focused dataset tests if requiredness changes
- record any optionality change and rationale in `coordination/reports/TASK-029_REPORT.md` so the controller can update stable-interface notes after review/integration

Do not compute `net_inflow` by adding order-size buckets unless the source documentation or payload explicitly defines that computation as total net inflow. Keep detailed order-size values out of the stable contract unless they are included in a structured optional value owned by this adapter's internal tests; do not change the dataset schema to add new fields in this task.

Contract or normalization failures for emitted fields must remain hard failures. Environment/source unavailability may be classified for live skip diagnostics, but must not mask adapter bugs.

### 3. Route and duplicate boundary

- Keep route order bounded and explicit.
- Prefer one normalized record per requested symbol and `trade_date`.
- If multiple routes contribute the same field, define deterministic precedence and test it.
- If multiple route rows produce identical snapshot identities and identical values, deduplicate deterministically.
- Conflicting duplicate rows for the same stable capital-flow identity must hard-fail. At minimum, conflicts for the same `(symbol, trade_date, source)` must not silently overwrite earlier data.
- If supplemental routes are unavailable due network/proxy/DNS/TLS/upstream issues, preserve a valid core record when source-truth required fields are available.

### 4. Source catalog alignment

The catalog already includes `DatasetName.CAPITAL_FLOW_SNAPSHOT` under `akshare_cn_hk_public_family`.

If needed, minimally align `akshare_cn_hk_public_family` information coverage so `InformationDomain.A_SHARE_FULL_DATA` includes the stable capital-flow dataset. Do not add broad source claims beyond the implemented slice.

### 5. Offline tests

Add deterministic offline tests proving:

- adapter satisfies `SourceAdapter`
- `fetch_source_result(...)` records pass `DatasetRegistry.validate_record(...)`
- source payload conversion from DataFrame-like and list-of-mapping works
- canonical and raw 6-digit symbol normalization works
- invalid, ambiguous, HK, ETF/fund, and index-like symbol filters fail clearly
- AKShare route symbol/market conversion is deterministic
- `start_date` / `end_date` filtering uses normalized `trade_date`
- `trade_date`, core flow fields, `source`, `ingested_at`, and `schema_version` are populated correctly
- supplemental turnover/northbound fields are emitted only when truthfully available
- optional metric handling does not invent placeholder values
- duplicate and conflicting-duplicate boundaries are preserved
- malformed payloads and missing required source fields fail clearly
- default tests remain offline-safe

If schema optionality is changed, add or update focused tests proving:

- required field expectations match the minimal source-truth adjustment
- emitted records still validate through `DatasetRegistry.validate_record(...)`
- existing dataset semantic rules still behave correctly

### 6. Mandatory live smoke test

Because TASK-029 is a real-source adapter task, gated live smoke is mandatory.

Add `tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py` (or equivalent) that:

- is skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1`
- uses no credentials
- fetches a minimal bounded live sample for a stable A-share symbol such as `600000.SH`
- validates at least one normalized record via `DatasetRegistry.validate_record(...)`
- asserts `source=akshare_cn_hk_public_family`, `market=CN`, and a canonical A-share symbol
- asserts all required flow fields emitted by this adapter are numeric
- treats unavailable supplemental routes as acceptable only when the final record still validates and source-truth required fields are present
- classifies environment/source unavailability as explicit `skipTest(...)`
- preserves adapter/schema/normalization issues as failures

If live-enabled run fails/skips due to network/proxy/DNS/TLS/upstream/source availability, report must include root-cause evidence and feasible repository-level fixes attempted.

## Do Not Implement

Do not implement:

- HK, ETF, fund, index, policy, valuation, or corporate-action adapters
- broad full-market capital-flow ingestion
- derived feature logic, scanner filters, strategy logic, AI reports, notifications, or UI
- broad warehouse refresh orchestration beyond preserving existing local helper behavior
- credentialed source behavior

## Testing Requirements

Default tests must remain offline.

Run:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Run focused tests, likely:

`python3 -m unittest tests/datahub/test_akshare_a_share_capital_flow_snapshot_adapter.py`

`python3 -m unittest -v tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py`

Run related regressions if shared AKShare adapter behavior, dataset schema, source catalog, or exports are touched:

`python3 -m unittest tests/datahub/test_akshare_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_a_share_valuation_snapshot_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_a_share_corporate_actions_adapter.py`

`python3 -m unittest tests/datahub/test_datasets.py`

`python3 -m unittest tests/datahub/test_source.py`

`python3 -m unittest tests/datahub/test_quality.py`

If source-catalog tests are touched, run:

`python3 -m unittest tests/datahub/test_source_catalog.py`

Run gated live smoke when enabled:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py`

## Acceptance Criteria

The task is acceptable when:

- AKShare A-share `CAPITAL_FLOW_SNAPSHOT` adapter exists under `quant/datahub/**`
- scope remains limited to one-symbol A-share capital-flow snapshot records for `DatasetName.CAPITAL_FLOW_SNAPSHOT`
- no placeholder capital-flow values are invented solely to satisfy schema requiredness
- any minimal schema optionality change is justified, tested, and truthfully reported
- offline tests pass and remain deterministic
- default tests remain offline-safe
- malformed payload, required-field, optional-field, duplicate, symbol, date, numeric, source-unit, and route-precedence boundaries are covered
- gated live smoke exists and result is truthfully recorded
- live-enabled PASS is provided for closure; if live-enabled skip/fail occurs because of network/proxy/DNS/TLS/upstream/source availability, the report must include root-cause evidence and feasible fixes attempted, and controller closure will require the rework/review gate in `AGENTS.md`
- no future-phase module contains new logic
- report exists at `coordination/reports/TASK-029_REPORT.md`

## Report Path

`coordination/reports/TASK-029_REPORT.md`

## Review Path

`coordination/reviews/TASK-029_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-029_INTEGRATION.md`

## Out of Scope

Everything outside a narrow DataHub A-share capital-flow snapshot adapter and tests is out of scope.
