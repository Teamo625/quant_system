# TASK-023 Execution Report (HKEX Symbol Filter Rework)

## Task

- Task ID: `TASK-023`
- Active Handoff: `coordination/handoffs/TASK-023_DATAHUB_HKEX_SYMBOL_FILTER_REWORK.md`
- Dataset Scope: `DatasetName.COMPANY_ANNOUNCEMENTS` only
- Module Scope: DataHub only

## Files Changed (This Rework)

- `quant/datahub/adapters/hkex.py`
- `tests/datahub/test_hkex_company_announcements_adapter.py`
- `coordination/reports/TASK-023_REPORT.md`

## Rework Summary

This rework fixes the review-blocking symbol-filter boundary while preserving HKEX source-row parsing tolerance.

Exact bug fixed:

- Previously, request-side `symbols` validation could accept prefix-polluted inputs (for example `foo700`, `A700.HK`) and normalize them to `00700.HK`, silently changing filter semantics.

Implemented fix:

1. Split symbol handling into two paths:
   - strict request filter normalization: `_normalize_requested_hk_symbol(...)`
   - tolerant source-row normalization: `_normalize_source_hk_symbol(...)`
2. Request-side path now only accepts canonical HK forms:
   - `700`
   - `00700`
   - `00700.HK`
   - plus equivalent 1-5 digit numeric codes with optional `.HK`
3. Source-row path retains tolerance for label-prefixed HKEX cells (for example `Stock Code: 00700`) without leaking this behavior into request validation.
4. Row normalization now uses `_normalize_source_hk_symbol(...)` so HKEX HTML tolerance remains intact.

## Tests Added or Changed

Updated `tests/datahub/test_hkex_company_announcements_adapter.py` with deterministic offline coverage for:

- invalid requested filters hard-fail:
  - `foo700`
  - `A700.HK`
  - `00700HK`
- empty and non-string request symbols hard-fail
- source-row label-prefixed symbol (`Stock Code: 00700`) still normalizes successfully

## Tests Run

1. `python3 -m unittest tests/datahub/test_hkex_company_announcements_adapter.py`
   - Result: PASS (`Ran 19 tests`)

2. `python3 -m unittest -v tests/datahub/test_hkex_company_announcements_live.py`
   - Result: PASS (`Ran 3 tests`, `OK (skipped=1)`)

3. `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`
   - Result: PASS (`Ran 316 tests`, `OK (skipped=12)`)

4. `python3 -m unittest tests/datahub/test_akshare_news_events_adapter.py tests/datahub/test_akshare_global_equity_snapshot_adapter.py tests/datahub/test_akshare_hk_adapter.py tests/datahub/test_source.py`
   - Result: PASS (`Ran 76 tests`)

5. `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_hkex_company_announcements_live.py`
   - Result: PASS (`Ran 3 tests in 6.611s`, `OK`)

## Default Network Behavior

- Default tests remain offline-safe.
- Added/updated adapter tests use injected fixture payloads only.
- Live smoke remains explicitly gated by `QUANT_SYSTEM_LIVE_TESTS=1`.

## Live-Enabled Result (Mandatory)

- Live-enabled status: `PASS`
- Evidence:
  - command: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_hkex_company_announcements_live.py`
  - output tail: `Ran 3 tests in 6.611s`, `OK`

## Deviations From Handoff

- None.

## Risks / Follow-Up

1. HKEX HTML parser still depends on upstream page structure/class names; future markup changes may require parser adjustment.
2. This rework intentionally stays limited to request symbol-filter boundary and source-row tolerance separation.
