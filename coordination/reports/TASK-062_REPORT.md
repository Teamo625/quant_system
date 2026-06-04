# TASK-062 Report

## files changed

- `quant/features/capital_flow.py`
- `quant/features/__init__.py`
- `tests/features/test_capital_flow.py`
- `tests/features/test_contracts.py`

## tests run

- `python3 -m py_compile quant/features/capital_flow.py tests/features/test_capital_flow.py`
  - PASS
- `python3 -m unittest discover -s tests/features -p 'test_*.py'`
  - PASS
  - `Ran 37 tests in 0.002s`
- `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`
  - PASS
  - `Ran 846 tests in 2.482s`
  - `OK (skipped=37)`

## default network behavior

- Offline-safe.
- Added capital-flow primitives only normalize caller-provided rows and perform pure in-memory calculations.
- Default test runs used local unittest discovery only and performed no live-source access.

## live-enabled PASS/SKIP/FAIL result and root-cause evidence

- `SKIP`
- TASK-062 is a pure offline FeatureHub primitive task.
- The handoff explicitly forbids live tests for this task, so no live-enabled path was run.

## deviations

- None.

## risks/follow-up

- Current `FeatureValueRecord` has no metric-level identifier inside `FeatureName.CAPITAL_FLOW`.
- To avoid emitting multiple ambiguous `CAPITAL_FLOW` records with indistinguishable meaning, this task only builds a feature record for latest `main_net_inflow`; trailing-sum, northbound, and turnover-adjusted outputs are exposed as validated scalar primitives only.
- If later tasks need multiple capital-flow record variants in the same sink, controller should consider a stable metric identity extension or a separate contract shape.
