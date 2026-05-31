# TASK-043 Execution Report

## Task ID

TASK-043

## Scope Confirmation

Implemented a narrow `akshare_cn_hk_public_family` Hong Kong financial-data adapter slice under DataHub for one-symbol requests, covering:

- `DatasetName.FINANCIAL_STATEMENTS`
- `DatasetName.FINANCIAL_INDICATORS`

No changes were made outside allowed execution scope (`quant/datahub/**`, `tests/datahub/**`, `coordination/reports/**`).

## Files Changed

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `quant/datahub/source_capabilities.py`
- `tests/datahub/test_akshare_hk_financial_data_adapter.py` (new)
- `tests/datahub/test_akshare_hk_financial_data_live.py` (new)

## Implementation Summary

### 1. New HK financial adapter

Added `AkshareHKFinancialDataAdapter` in `quant/datahub/adapters/akshare.py` with:

- source binding:
  - `source=akshare_cn_hk_public_family`
  - `market=HK`
- supported datasets:
  - `FINANCIAL_STATEMENTS`
  - `FINANCIAL_INDICATORS`
- strict dataset rejection for unsupported dataset requests
- strict one-symbol enforcement
- HK symbol normalization:
  - accepts canonical `NNNNN.HK`
  - accepts bare numeric codes like `00700` and `700`
  - normalizes output symbol to canonical `NNNNN.HK`
- deterministic output behavior:
  - deterministic sort order
  - deterministic dedupe of exact duplicate rows
  - conflict detection for duplicate identity with different numeric payload
- payload handling:
  - accepts DataFrame-like `.to_dict(orient="records")`
  - accepts list-of-mapping payloads
  - rejects malformed payload shapes and non-mapping rows
- parsing and validation:
  - report period/date parsing with explicit failures on invalid values
  - numeric parsing with explicit failures on invalid/non-finite values
  - period-type normalization from `DATE_TYPE_CODE` and report date
  - optional `source_ts`, `currency`, and `unit` normalization
- live-route resolution:
  - `stock_financial_hk_report_em`
  - `stock_financial_hk_analysis_indicator_em`
  - network/source unavailability classifier for live smoke skip logic

### 2. Exports

Wired new adapter into package exports:

- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`

### 3. Capability truth update

Updated `hk_financial_data` in `quant/datahub/source_capabilities.py`:

- status: `planned` -> `partial`
- updated gap reason/recommended handoff to reflect one-symbol implemented slice with remaining breadth/history gap

## Tests Run

### Focused new-task tests

1. `python3 -m unittest tests/datahub/test_akshare_hk_financial_data_adapter.py`
- PASS (`Ran 14 tests ... OK`)

2. `python3 -m unittest -v tests/datahub/test_akshare_hk_financial_data_live.py`
- PASS with default live gate behavior (`Ran 4 tests ... OK (skipped=2)`)

3. `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_financial_data_live.py`
- PASS (`Ran 4 tests ... OK`)
- both live smokes passed:
  - `test_live_akshare_hk_financial_statements_smoke`
  - `test_live_akshare_hk_financial_indicators_smoke`

### Required related regressions

4. `python3 -m unittest tests/datahub/test_akshare_hk_adapter.py`
- PASS (`Ran 16 tests ... OK`)

5. `python3 -m unittest tests/datahub/test_akshare_hk_instrument_master_adapter.py`
- PASS (`Ran 20 tests ... OK`)

6. `python3 -m unittest tests/datahub/test_akshare_hk_valuation_snapshot_adapter.py`
- PASS (`Ran 23 tests ... OK`)

7. `python3 -m unittest tests/datahub/test_source.py`
- PASS (`Ran 20 tests ... OK`)

8. `python3 -m unittest tests/datahub/test_source_capabilities.py`
- PASS (`Ran 9 tests ... OK`)

### Full DataHub default suite

9. `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`
- PASS (`Ran 660 tests ... OK (skipped=27)`)

## Default Network Behavior

Default tests remain offline-safe:

- new live smoke tests are environment-gated and skipped unless `QUANT_SYSTEM_LIVE_TESTS=1`
- offline adapter tests use fixtures/mocks and do not require network

## Live-Enabled Result (Mandatory)

Live-enabled result for TASK-043: **PASS**

Command:

- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_financial_data_live.py`

Observed outcome:

- statements smoke: PASS
- indicators smoke: PASS

During implementation, an initial live run surfaced a conflict-detection false-positive for statement field matching (over-broad keyword match for total-assets family). This was fixed in-repo by tightening statement-item matching to exact/anchored names. Fresh live run after fix passed completely.

## Deviations From Handoff

No scope deviations.

Notes:

- `source_catalog.py` did not require changes because catalog coverage for `FINANCIAL_STATEMENTS` and `FINANCIAL_INDICATORS` under `akshare_cn_hk_public_family` was already aligned.

## Risks / Follow-up Tasks

1. Current slice is intentionally narrow (single-symbol request path). It is suitable for Phase 2.5 capability proof but not full HK-universe ingestion.
2. HK statement metric extraction currently maps core fields (`revenue`, `net_profit`, `total_assets`, `total_liabilities`, `net_cash_operating`) by stable item-name anchors. Further breadth may require additional alias coverage or source-side code mapping hardening across more issuers/history shapes.
3. `hk_financial_data` remains correctly `partial`; follow-up should target breadth/history and batch robustness before any `covered` claim.
