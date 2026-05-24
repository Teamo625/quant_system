# TASK-021 Execution Report (Sina KeyError Rework)

## Task

- Task ID: `TASK-021`
- Active Handoff: `coordination/handoffs/TASK-021_DATAHUB_GLOBAL_EQUITY_SINA_KEYERROR_REWORK.md`
- Dataset Scope: `DatasetName.GLOBAL_EQUITY_SNAPSHOT` only
- Module Scope: DataHub only

## Files Changed

- `quant/datahub/adapters/akshare.py`
- `tests/datahub/test_akshare_global_equity_snapshot_adapter.py`
- `tests/datahub/test_akshare_global_equity_snapshot_live.py`
- `coordination/reports/TASK-021_REPORT.md`

## Rework Diagnosis and Fix

Review blocking symptom was `KeyError: 'data'` from Sina route (`stock_us_spot`) in live-enabled execution.

Implemented repository-level fix keeps scope narrow:

1. Added route-aware unavailability classifier in global-equity fallback chain:
   - network failures still classified by existing logic;
   - only `route_name == "stock_us_spot"` plus `KeyError("data")` (including chained causes) is treated as route-unavailable upstream failure.
2. Preserved strict contract behavior:
   - non-`data` KeyError on `stock_us_spot` still hard-fails;
   - parse/validation/contract failures on matched rows still hard-fail.
3. Added deterministic tests for this exact boundary, including route-exhaustion diagnostics and classifier boundaries.
4. Live test environment classifier now explicitly treats adapter route-exhaustion runtime diagnostics (`global-equity fetch routes unavailable`) as environment/source unavailability for skip classification.

## Tests Run

1. `python3 -m unittest tests/datahub/test_akshare_global_equity_snapshot_adapter.py`  
   - Result: PASS (`Ran 25 tests`)

2. `python3 -m unittest -v tests/datahub/test_akshare_global_equity_snapshot_live.py`  
   - Result: PASS (`Ran 3 tests`, `OK (skipped=1)`)

3. `python3 -m unittest tests/datahub/test_akshare_index_constituents_adapter.py tests/datahub/test_akshare_index_adapter.py tests/datahub/test_akshare_hk_adapter.py tests/datahub/test_akshare_fund_nav_adapter.py tests/datahub/test_akshare_adapter.py`  
   - Result: PASS (`Ran 88 tests`)

4. `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`  
   - Result: PASS (`Ran 276 tests`, `OK (skipped=10)`)

5. `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_global_equity_snapshot_live.py`  
   - Result: PASS (`Ran 3 tests in 634.290s`, `OK`)

## Default Network Behavior

- Default paths remain offline-safe.
- New/updated tests for this rework are deterministic and use injected callables or pure helper classification logic.
- Live smoke remains explicitly gated by `QUANT_SYSTEM_LIVE_TESTS=1`.

## Live-Enabled Result (Mandatory)

- Live-enabled status: `PASS`
- Evidence:
  - command: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_global_equity_snapshot_live.py`
  - output tail: `Ran 3 tests in 634.290s` and `OK`
- Notes:
  - runtime still shows slow upstream pagination path in this environment;
  - no adapter contract failure surfaced in this run.

## Exact Root-Cause Evidence for Prior Non-PASS

- Prior review reproduced:
  - `KeyError: 'data'` inside `akshare.stock_us_spot` / Sina path.
- This round addresses that route-internal upstream failure as route-unavailable only for the narrow `stock_us_spot + KeyError("data")` branch, without broad exception swallowing.

## Deviations From Handoff

- None.
- Scope remained within DataHub and `GLOBAL_EQUITY_SNAPSHOT`.

## Risks / Follow-Up

1. Live smoke remains high-latency under some public-route conditions (observed long pagination run).
2. If all public routes become unavailable, live smoke may still `SKIP` with route-level diagnostics; this is expected and now more explicit for reviewer/controller judgment.
