# TASK-031 Report

## Task
- TASK-031_DATAHUB_AKSHARE_ETF_FUND_HOLDINGS_ADAPTER

## Files Changed
- quant/datahub/adapters/akshare.py
- quant/datahub/adapters/__init__.py
- quant/datahub/__init__.py
- quant/datahub/source_catalog.py
- tests/datahub/test_akshare_fund_holdings_adapter.py
- tests/datahub/test_akshare_fund_holdings_live.py

## Implementation Summary
- Added `AkshareETFFundHoldingsAdapter` for `DatasetName.FUND_HOLDINGS` under source id `akshare_cn_hk_public_family`.
- Scope is restricted to exactly one requested ETF/fund code and one bounded reporting-period holdings slice.

Adapter behavior implemented:
- Dataset boundary:
  - accepts only `DatasetName.FUND_HOLDINGS`
  - rejects unsupported datasets clearly
- Symbol boundary:
  - requires exactly one symbol
  - accepts bare 6-digit fund code and canonical `*.ETF_CN`
  - normalizes output `fund_code` to canonical `XXXXXX.ETF_CN`
  - rejects empty, multiple, malformed, and unsupported suffixes (for example `.SH`, `.HK`)
- Route behavior:
  - uses bounded AKShare holdings route resolution (primary `fund_portfolio_hold_em`, compatibility fallback `fund_em_portfolio_hold`)
  - performs bounded year attempts only (current/request year and previous year)
  - no broad all-fund crawl
- Normalization to `FUND_HOLDINGS` contract:
  - required: `fund_code`, `symbol`, `market`, `report_date`, `weight`, `source`, `ingested_at`, `schema_version`
  - optional: `shares`, `position_value`, `source_ts`
  - `source=akshare_cn_hk_public_family`
  - `market=CN` for normalized holding rows
  - `schema_version` from `DatasetRegistry`
  - `ingested_at` from injectable clock
- Holdings symbol normalization:
  - deterministic A-share normalization to `*.SH` / `*.SZ` / `*.BJ`
  - rejects unsupported/invalid holding symbols (including index-like unsupported prefixes where applicable)
- Report date normalization:
  - supports direct dates (`YYYY-MM-DD`, `YYYYMMDD`) and quarter-text strings like `2025年1季度股票投资明细`
  - quarter text converted to quarter-end report dates
- Weight/numeric boundaries:
  - `weight` normalized as percentage in [0, 100]
  - optional `shares` and `position_value` must be numeric and nonnegative
  - malformed numeric/date payload values fail clearly
- Duplicate boundary:
  - dedupe key includes `(fund_code, symbol, report_date)`
  - benign exact duplicates are deduped deterministically
  - conflicting duplicates hard-fail
- Slice boundary:
  - after normalization and date filtering, keeps only one latest reporting-period slice with bounded record count

Source catalog alignment:
- Added `DatasetName.FUND_HOLDINGS` to `akshare_cn_hk_public_family.dataset_coverage`.
- Added `DatasetName.FUND_HOLDINGS` to AKShare `ETF_FUND_FULL_DATA` stable dataset set.
- No broad source claims beyond this implemented narrow slice.

## Tests Run

### Focused TASK-031 tests
1. `python3 -m unittest tests/datahub/test_akshare_fund_holdings_adapter.py`
- PASS (20 tests)

2. `python3 -m unittest -v tests/datahub/test_akshare_fund_holdings_live.py`
- PASS (classifier tests)
- live smoke skipped by default as designed

### Required default/offline run
3. `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`
- PASS (487 tests, 19 skipped)

### Related regressions
4. `python3 -m unittest tests/datahub/test_akshare_fund_nav_adapter.py`
- PASS (17 tests)

5. `python3 -m unittest tests/datahub/test_datasets.py`
- PASS (27 tests)

6. `python3 -m unittest tests/datahub/test_source.py`
- PASS (20 tests)

7. `python3 -m unittest tests/datahub/test_source_catalog.py`
- PASS (6 tests)

## Default Network Behavior
- Default tests remain offline-safe.
- `test_akshare_fund_holdings_adapter.py` is deterministic and uses injected payload fixtures/mocks.
- Live test file remains environment-gated and is skipped by default unless explicitly enabled.

## Live-Enabled Result (Mandatory)
- Command: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_fund_holdings_live.py`
- Result: PASS
  - classifier tests PASS
  - live smoke PASS
- Evidence summary:
  - adapter fetched bounded live holdings sample for one fund code
  - at least one normalized record validated by `DatasetRegistry.validate_record(DatasetName.FUND_HOLDINGS, ...)` with no issues

## Deviations From Handoff
- None.

## Risks / Follow-up
- Upstream AKShare route schema or column naming can change; current implementation fails fast on contract-breaking changes.
- Holdings quantity/value units are preserved as source-truth numeric values; downstream consumers should interpret units consistently with source documentation.
- Current slice intentionally targets CN ETF/fund one-symbol holdings only; broader fund profile/universe ingestion remains out of scope.
