# TASK-020 Report

## Task

- Task ID: `TASK-020`
- Handoff: `coordination/handoffs/TASK-020_DATAHUB_AKSHARE_INDEX_CONSTITUENTS_ADAPTER.md`
- Role: 5.3 execution window

## Files Changed

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `tests/datahub/test_akshare_index_constituents_adapter.py`
- `tests/datahub/test_akshare_index_constituents_live.py`
- `coordination/reports/TASK-020_REPORT.md`

## What Was Implemented

### 1) AKShare `INDEX_CONSTITUENTS` narrow adapter

Added `AkshareIndexConstituentsAdapter` in `quant/datahub/adapters/akshare.py`.

Adapter behavior:

- supports only `DatasetName.INDEX_CONSTITUENTS`
- implements `SourceAdapter` protocol shape
- uses lazy/optional AKShare imports
- requires exactly one index identifier in `symbols`
- accepts common identifier variants:
  - canonical: `000300.CN_INDEX`
  - bare code: `000300`
  - source-native: `sh000300`
- resolves source fetch routes with bounded fallback order:
  - `index_stock_cons_weight_csindex`
  - `index_stock_cons_csindex`
  - `index_stock_cons_sina`
  - `index_stock_cons`
- keeps network-unavailable errors classified as network class; non-network parsing/contract issues remain hard failures

### 2) Contract normalization for `INDEX_CONSTITUENTS`

Normalized output fields:

- `index_code` (canonical, e.g. `000300.CN_INDEX`)
- `symbol` (canonicalized A-share symbol, e.g. `600000.SH`)
- `market` = `CN_A`
- `in_date`
- optional `out_date`
- optional `weight`
- `source` = `akshare_cn_hk_public_family`
- optional `source_ts`
- `ingested_at` (injectable clock for deterministic tests)
- `schema_version` from `DatasetRegistry`

Field handling:

- `in_date`: explicit date fields parsed when present; otherwise deterministic fallback `1900-01-01`
- `out_date`: included only when explicit valid value exists
- `weight`: included only when valid; supports `%` string parsing; rejects invalid parse and out-of-range values (`[0, 100]`)

### 3) Duplicate boundary preserved

Implemented strict duplicate handling for `index_code + symbol`:

- benign duplicates (same `in_date`/`out_date`) are deterministically deduped
- when both contain `source_ts`, later `source_ts` wins
- conflicting duplicates (same key but different date semantics) hard-fail with explicit error

### 4) Exports

Exported adapter from:

- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`

## Tests Added

### Offline adapter tests

Added `tests/datahub/test_akshare_index_constituents_adapter.py` covering:

- protocol compatibility
- normalization + `DatasetRegistry.validate_record(...)`
- index identifier validation (missing/empty/multiple/unsupported format/suffix)
- canonicalization stability for symbol/index code
- deterministic `in_date` fallback and optional fields behavior
- `weight` parsing and validation (including out-of-range rejection)
- malformed payload failures (shape/row type/missing required fields)
- duplicate boundary (benign dedupe vs conflicting hard-fail)
- fallback route behavior when primary network route unavailable
- default path offline safety

### Gated live smoke test

Added `tests/datahub/test_akshare_index_constituents_live.py`:

- skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1`
- no credentials
- bounded symbols for smoke
- validates at least one normalized record via `DatasetRegistry.validate_record(...)`
- classifies network/environment unavailability as explicit `skipTest(...)`
- keeps adapter/schema bugs as failures

## Tests Run

### Required full DataHub suite

1. `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`
- Result: `Ran 248 tests`, `OK (skipped=9)`

### Focused TASK-020 tests

1. `python3 -m unittest tests/datahub/test_akshare_index_constituents_adapter.py`
- Result: `Ran 24 tests`, `OK`

2. `python3 -m unittest -v tests/datahub/test_akshare_index_constituents_live.py`
- Result: `Ran 1 test`, `OK (skipped=1)`

### Related regressions (shared AKShare behavior)

1. `python3 -m unittest tests/datahub/test_akshare_index_adapter.py`
- Result: `Ran 21 tests`, `OK`

2. `python3 -m unittest tests/datahub/test_akshare_sector_membership_adapter.py`
- Result: `Ran 26 tests`, `OK`

3. `python3 -m unittest tests/datahub/test_akshare_sector_master_adapter.py`
- Result: `Ran 18 tests`, `OK`

4. `python3 -m unittest tests/datahub/test_akshare_sector_adapter.py`
- Result: `Ran 25 tests`, `OK`

5. `python3 -m unittest tests/datahub/test_akshare_fund_nav_adapter.py`
- Result: `Ran 17 tests`, `OK`

6. `python3 -m unittest tests/datahub/test_akshare_adapter.py`
- Result: `Ran 10 tests`, `OK`

### Mandatory live-enabled command

1. `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_index_constituents_live.py`
- Result:
  - `test_live_akshare_index_constituents_smoke ... ok`
  - `Ran 1 test in 0.964s`
  - `OK`

## Default Network Behavior

- default tests remain offline-safe
- live tests remain explicitly gated by `QUANT_SYSTEM_LIVE_TESTS=1`
- no hidden live network calls added to default test paths

## Live Smoke Status

- default run status: `SKIP` (expected by gate)
- live-enabled run status: `PASS`

## Deviations From Handoff

- No deviations.

## Risks / Follow-up

1. index constituents live data availability depends on upstream source route availability and schema stability.
2. fallback route order is bounded and deterministic; if upstream interfaces change field names materially, a narrow parser update may be needed.
