# TASK-024 Execution Report (China Macro `is_preliminary` Rework)

## Task

- Task ID: `TASK-024`
- Active Handoff: `coordination/handoffs/TASK-024_DATAHUB_CHINA_MACRO_PRELIMINARY_REWORK.md`
- Dataset Scope: `DatasetName.MACRO_INDICATOR_MASTER`, `DatasetName.MACRO_OBSERVATIONS`
- Module Scope: DataHub only

## Files Changed (This Rework)

- `quant/datahub/adapters/akshare.py`
- `tests/datahub/test_akshare_china_macro_adapter.py`
- `coordination/reports/TASK-024_REPORT.md`

## Rework Summary

This rework fixes the review-blocking `is_preliminary` field mapping issue in `AkshareChinaMacroAdapter`.

Implemented fix:

1. Tightened `is_preliminary` source mapping in macro observation normalization:
   - before: read from `is_preliminary`, `预告`, `初值`
   - after: read only explicit `is_preliminary`
2. Preserved explicit boolean-like normalization for `is_preliminary`:
   - accepts `True`/`False`, `1`/`0`, and clear boolean-like strings
   - invalid explicit `is_preliminary` still hard-fails
3. Preserved all other adapter boundaries:
   - dataset scope unchanged (`MACRO_INDICATOR_MASTER`, `MACRO_OBSERVATIONS`)
   - indicator scope unchanged (`CPI_CN_YOY`, `PPI_CN_YOY`, `GDP_CN_YOY`)
   - source id unchanged (`macro_policy_public_sources`)
   - symbol rejection, date filtering, duplicate handling, payload/field validation unchanged

## Offline Regression Coverage Added

Added focused tests in `tests/datahub/test_akshare_china_macro_adapter.py`:

1. numeric `初值` is ignored for `is_preliminary` and does not fail
2. numeric `预测值` / `预告` are ignored for `is_preliminary` and do not fail
3. explicit boolean-like `is_preliminary` remains normalized correctly
4. existing invalid explicit `is_preliminary` failure behavior remains covered

Review diagnostic reproduction now passes:

- input row: `{"日期": "2024-01-10", "今值": "0.2", "初值": "0.1"}`
- result: record is normalized successfully and does not contain `is_preliminary`

## Tests Run

1. `python3 -m unittest tests/datahub/test_akshare_china_macro_adapter.py`
   - Result: PASS (`Ran 18 tests`)

2. `python3 -m unittest -v tests/datahub/test_akshare_china_macro_live.py`
   - Result: PASS (`Ran 3 tests`, `OK (skipped=1)`)

3. `python3 -m unittest tests/datahub/test_akshare_news_events_adapter.py`
   - Result: PASS (`Ran 15 tests`)

4. `python3 -m unittest tests/datahub/test_akshare_global_equity_snapshot_adapter.py`
   - Result: PASS (`Ran 25 tests`)

5. `python3 -m unittest tests/datahub/test_source.py`
   - Result: PASS (`Ran 20 tests`)

6. `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`
   - Result: PASS (`Ran 337 tests`, `OK (skipped=13)`)

7. `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_china_macro_live.py`
   - Result: PASS (`Ran 3 tests in 4.816s`, `OK`)

## Default Network Behavior

- Default tests remain offline-safe.
- New/updated regression tests use injected payloads only and do not require network.
- Live smoke remains gated by `QUANT_SYSTEM_LIVE_TESTS=1` and skipped by default.

## Live-Enabled Result (Mandatory)

- Live-enabled status: `PASS`
- Evidence:
  - command: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_china_macro_live.py`
  - output tail: `Ran 3 tests in 4.816s`, `OK`

## Deviations From Handoff

- None.

## Risks / Follow-Up

1. Upstream AKShare/Jin10 macro payload structures may evolve; if explicit `is_preliminary` semantics appear under new keys, mapping should be extended only with reliable boolean-like semantics and corresponding offline regression tests.
2. Current slice intentionally does not infer preliminary status from numeric forecast/initial-value fields by design.
