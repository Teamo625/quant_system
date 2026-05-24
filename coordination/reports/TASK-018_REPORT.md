# TASK-018 Report (Live Duplicate Rework)

## Task

- Task ID: `TASK-018`
- Handoff: `coordination/handoffs/TASK-018_DATAHUB_SECTOR_MASTER_LIVE_DUPLICATE_REWORK.md`
- Role: 5.3 execution window

## Files Changed

- `quant/datahub/adapters/akshare.py`
- `tests/datahub/test_akshare_sector_master_adapter.py`
- `coordination/reports/TASK-018_REPORT.md`

## Root-Cause Investigation

### 1) Blocking failure reproduction

- Command:
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_sector_master_live.py`
- Observed error (pre-fix):
  - `ValueError: Duplicate canonical sector_id detected: 'INDUSTRY:煤炭开采'`

### 2) Route-level duplicate diagnostics

Live inspection against AKShare route families showed:

- `INDUSTRY_EM` (`stock_board_industry_name_em`): duplicates exist in returned rows
- `INDUSTRY_THS` (`stock_board_industry_name_ths`): no duplicates observed
- `CONCEPT_EM` (`stock_board_concept_name_em`): no duplicates observed
- `CONCEPT_THS` (`stock_board_concept_name_ths`): no duplicates observed

### 3) Duplicate shape and conflict assessment

For duplicated `INDUSTRY_EM` names, duplicated rows carried the same `板块代码` (same source sector code), while quote/rank-like fields varied between rows.

This indicates a benign source noise pattern for `SECTOR_MASTER` (same canonical sector entity repeated), not a true canonical-identity conflict.

## Rework Implemented

### 1) Deterministic benign-duplicate handling in `AkshareSectorMasterAdapter`

In `quant/datahub/adapters/akshare.py` (`_normalize_sector_master_rows`):

- Added deterministic dedup for duplicate canonical `sector_id` **within the same sector-type route** when duplicates are compatible.
- Added optional source code extraction/normalization from:
  - `板块代码`
  - `sector_code`
  - `code`
- Duplicate resolution rule:
  - if duplicate `sector_id` has **same** normalized source code (or one side missing code), treat as benign duplicate and merge deterministically
  - keep deterministic preferred record:
    - prefer record with valid `source_ts`
    - if both have `source_ts`, prefer lexicographically later normalized `source_ts`
    - otherwise keep first

### 2) Conflict hard-fail kept (required)

- If duplicate canonical `sector_id` has **conflicting non-empty source codes**, adapter now raises hard failure:
  - `Conflicting duplicate canonical sector_id detected: ...`
- This preserves contract bug visibility and avoids masking semantic conflicts.

### 3) Existing safety behavior preserved

- Non-network exceptions are still not converted into fallback/skip.
- Default tests remain offline-safe.
- Live behavior remains explicitly gated by `QUANT_SYSTEM_LIVE_TESTS=1`.

## Offline Regression Tests Added/Updated

Updated `tests/datahub/test_akshare_sector_master_adapter.py`:

- Replaced strict duplicate-reject test with benign duplicate dedup test:
  - same canonical sector + same source code => deduplicated record count is 1
  - deterministic `source_ts` preference verified
- Added explicit conflict test:
  - same canonical sector + different source codes => hard failure

## Tests Run

### Required task tests

1. `python3 -m unittest tests/datahub/test_akshare_sector_master_adapter.py`
   - Result: `Ran 18 tests`, `OK`

2. `python3 -m unittest -v tests/datahub/test_akshare_sector_master_live.py`
   - Result: `Ran 1 test`, `OK (skipped=1)`
   - Default gate behavior confirmed.

3. `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`
   - Result: `Ran 196 tests`, `OK (skipped=7)`

### Required regressions (shared AKShare behavior)

1. `python3 -m unittest tests/datahub/test_akshare_sector_adapter.py`
   - Result: `Ran 25 tests`, `OK`

2. `python3 -m unittest tests/datahub/test_akshare_index_adapter.py`
   - Result: `Ran 21 tests`, `OK`

3. `python3 -m unittest tests/datahub/test_akshare_fund_nav_adapter.py`
   - Result: `Ran 17 tests`, `OK`

4. `python3 -m unittest tests/datahub/test_akshare_adapter.py`
   - Result: `Ran 10 tests`, `OK`

### Required live-enabled evidence

1. `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_sector_master_live.py`
   - Result:
     - `test_live_akshare_sector_master_smoke ... ok`
     - `Ran 1 test in 5.922s`
     - `OK`

## Default Network Behavior

- Default test runs remain offline-safe.
- Live tests remain gated and skipped by default.
- No hidden live network calls introduced in default test paths.

## Live Smoke Status

- Default run status: `SKIP` (expected by gate)
- Live-enabled final status: `PASS`

## Deviations From Handoff

- No deviations.

## Risks / Follow-up

- `INDUSTRY_EM` upstream may continue producing duplicate rows intermittently; current dedup logic handles same-entity duplicate noise deterministically.
- If upstream begins returning same-name rows with different source codes, adapter now fails fast by design; that should trigger a new rework with source-level conflict analysis.
