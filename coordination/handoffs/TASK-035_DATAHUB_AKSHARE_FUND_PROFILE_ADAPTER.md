# TASK-035: DataHub AKShare Fund Profile Adapter

## Task ID

TASK-035

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

TASK-034 has been accepted and integrated. It completed the AKShare one-symbol Hong Kong stock `VALUATION_SNAPSHOT` adapter under source id `akshare_cn_hk_public_family`, with deterministic offline tests, minimal source-catalog alignment for HK valuation coverage, and live-enabled PASS evidence.

Phase 2 remains open. ETF/fund coverage currently includes NAV snapshots and holdings, but fund reference/profile coverage for `DatasetName.FUND_PROFILE` is still missing. The next narrow executable source slice is therefore one-fund profile coverage from a no-credential public AKShare route.

This task must implement only a one-fund China public fund profile slice for `DatasetName.FUND_PROFILE`.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-035_DATAHUB_AKSHARE_FUND_PROFILE_ADAPTER.md`

## Goal

Implement a narrow AKShare-backed fund profile adapter for `DatasetName.FUND_PROFILE`, focused on one requested China public fund code, with deterministic offline tests and mandatory gated live smoke coverage.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-035_REPORT.md`

Suggested implementation locations:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `quant/datahub/source_catalog.py` for minimal catalog alignment if stable AKShare no-credential coverage is implemented
- `tests/datahub/test_akshare_fund_profile_adapter.py`
- `tests/datahub/test_akshare_fund_profile_live.py`
- `tests/datahub/test_source_catalog.py` only if source-catalog expectations change

Do not change `quant/datahub/datasets.py` unless source-truth evidence proves a minimal schema optionality hardening is essential. If such a change is made, it must be tested and truthfully reported.

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

### 1. AKShare fund profile adapter

Add a narrow adapter for:

- source id: `akshare_cn_hk_public_family`
- source display name: `AKShare CN/HK Public Family`
- supported dataset in this task: `DatasetName.FUND_PROFILE`
- market output: `CN`
- initial scope: one requested China public fund code

Known bounded AKShare route available at controller dispatch time:

- `akshare.fund_individual_basic_info_xq(symbol="<6-digit-code>", timeout=<optional>)`
  - observed useful rows for `000001`: `基金代码`, `基金名称`, `基金全称`, `成立时间`, `基金公司`, `基金经理`, `托管银行`, `基金类型`, and related descriptive fields

Optional bounded helper route, if needed only for fund type/name fallback:

- `akshare.fund_name_em()`
  - this is a broad fund-name table, so do not use it as a full ingestion job. If used, it must be bounded to the requested fund code and must not emit records beyond the requested fund.

The adapter should:

- implement the existing `SourceAdapter` protocol
- use lazy/optional AKShare imports
- reject unsupported datasets clearly
- require exactly one requested fund code through `symbols`
- accept source-native bare six-digit fund codes and canonical fund codes such as `000001.FUND_CN`
- reject missing, multiple, empty, malformed, HK stock, A-share stock-only, index, or unsupported market symbols clearly
- normalize output `fund_code` to a stable canonical code, preferably `000001.FUND_CN` for China public fund records
- fetch only the requested single fund profile
- do not perform all-fund universe ingestion
- support DataFrame-like payload and list-of-mapping payload fixtures
- fail clearly on malformed payload, missing required source fields, invalid inception date, invalid fund code, invalid required strings, or non-serializable values

Normalize output records to `FUND_PROFILE` contract fields:

- `fund_code`
- `fund_name`
- `market`: `CN`
- `fund_type`
- `management_company`
- `inception_date`
- `currency`: `CNY`
- optional `benchmark` when truthfully provided by source
- `source`: `akshare_cn_hk_public_family`
- optional `source_ts` when the source exposes a trustworthy timestamp
- `ingested_at`: from injectable clock for deterministic tests
- `schema_version`: from `DatasetRegistry`

Do not invent placeholder fund names, management companies, fund types, currencies, or inception dates.

### 2. Source-truth and route boundary

- Keep route order bounded and explicit.
- Fetch only the requested single fund.
- If the primary route is unavailable for ETF-like codes such as `510300`, do not silently broaden scope; this task may use a stable open-fund code such as `000001` for the initial one-fund slice.
- Network/proxy/DNS/TLS/SSL/upstream/source availability failures may be classified for live skip diagnostics, but DataHub contract/normalization failures must remain hard failures.
- If no bounded route can truthfully provide the current required fields for a valid record, report the source-truth limitation clearly. Do not synthesize fake data.

### 3. Duplicate and identity boundary

- The stable profile key is canonical `fund_code`.
- Benign exact duplicate profile rows may be deterministically deduplicated.
- Conflicting duplicate rows for the same canonical `fund_code` must hard-fail.
- If multiple route rows have the same field with different values, define deterministic precedence only when source meaning is clear; otherwise fail clearly.

### 4. Source catalog alignment

The source catalog currently lists `DatasetName.FUND_PROFILE` under credentialed `tushare_pro_cn_core` and `hkex_disclosure_and_calendar_family`, but not under `akshare_cn_hk_public_family`.

If this task implements stable no-credential AKShare one-fund profile coverage, minimally add `DatasetName.FUND_PROFILE` to `akshare_cn_hk_public_family` dataset coverage and `InformationDomain.ETF_FUND_FULL_DATA` stable datasets. Do not add broad source claims beyond the implemented slice.

If source-catalog expectations change, add or update deterministic offline catalog tests.

### 5. Offline tests

Add deterministic offline tests proving:

- adapter satisfies `SourceAdapter`
- `fetch_source_result(...)` records pass `DatasetRegistry.validate_record(...)`
- source payload conversion from DataFrame-like and list-of-mapping works
- canonical and source-native fund code normalization works
- invalid, ambiguous, HK stock, A-share stock-only, ETF-like unsupported-if-not-supported, and index-like symbol filters fail clearly
- required fields, inception-date parsing, currency, management company, fund type, optional benchmark, `source`, `ingested_at`, and `schema_version` are populated correctly
- duplicate and conflicting-duplicate boundaries are preserved
- malformed payloads and missing required source fields fail clearly
- default tests remain offline-safe

If source-catalog coverage is updated, add or update focused catalog tests.

### 6. Mandatory live smoke test

Because TASK-035 is a real-source adapter task, gated live smoke is mandatory.

Add `tests/datahub/test_akshare_fund_profile_live.py` or equivalent that:

- is skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1`
- uses no credentials
- fetches a minimal bounded live profile sample for a stable fund code such as `000001.FUND_CN`
- validates at least one normalized record via `DatasetRegistry.validate_record(...)`
- asserts `source=akshare_cn_hk_public_family`, `market=CN`, and a canonical fund code
- classifies environment/source unavailability as explicit `skipTest(...)`
- preserves adapter/schema/normalization issues as failures

If live-enabled run fails/skips due to network/proxy/DNS/TLS/SSL/upstream/source availability, the report must include root-cause evidence and feasible repository-level fixes attempted. Controller closure will require the rework/review gate in `AGENTS.md`.

## Do Not Implement

Do not implement:

- broad fund universe ingestion
- ETF-specific profile fallback if the bounded profile route cannot support it cleanly
- fund NAV, holdings, scale/flow, feature engineering, scanner logic, strategy logic, AI reports, notifications, UI, or automated trading
- A-share, HK stock, index, global, macro, policy, news, or announcement expansion
- storage refresh orchestration beyond what is needed for this adapter test surface

## Testing Requirements

Default tests must remain offline.

Run:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Run focused tests, likely:

`python3 -m unittest tests/datahub/test_akshare_fund_profile_adapter.py`

`python3 -m unittest -v tests/datahub/test_akshare_fund_profile_live.py`

Run related regressions if shared AKShare adapter behavior, exports, dataset schema, or source catalog is touched:

`python3 -m unittest tests/datahub/test_akshare_fund_holdings_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_fund_nav_adapter.py`

`python3 -m unittest tests/datahub/test_datasets.py`

`python3 -m unittest tests/datahub/test_source.py`

If source-catalog tests are touched, run:

`python3 -m unittest tests/datahub/test_source_catalog.py`

Run gated live smoke when enabled:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_fund_profile_live.py`

## Acceptance Criteria

The task is acceptable when:

- AKShare-backed `FUND_PROFILE` adapter exists under `quant/datahub/**`
- scope remains limited to one requested China public fund profile record for `DatasetName.FUND_PROFILE`
- source id remains `akshare_cn_hk_public_family`
- no placeholder profile values are invented solely to satisfy schema requiredness
- offline tests pass and remain deterministic
- default tests remain offline-safe
- malformed payload, required-field, duplicate, symbol, date, source-truth, and catalog-alignment boundaries are covered
- gated live smoke exists and result is truthfully recorded
- live-enabled PASS is provided for closure; if live-enabled skip/fail occurs because of network/proxy/DNS/TLS/SSL/upstream/source availability, the report must include root-cause evidence and feasible fixes attempted, and controller closure will require the rework/review gate in `AGENTS.md`
- no future-phase module contains new logic
- report exists at `coordination/reports/TASK-035_REPORT.md`

## Report Path

`coordination/reports/TASK-035_REPORT.md`

## Review Path

`coordination/reviews/TASK-035_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-035_INTEGRATION.md`

## Out of Scope

Everything outside a narrow DataHub AKShare fund profile adapter and tests is out of scope.
