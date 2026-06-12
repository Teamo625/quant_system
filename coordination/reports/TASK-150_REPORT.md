# TASK-150 Report

## files changed

- `quant/backtest/comparison.py`
- `quant/backtest/__init__.py`
- `quant/backtest/personal_readiness.py`
- `tests/backtest/test_comparison.py`
- `tests/backtest/test_personal_readiness.py`

## comparison workflow capabilities added

- Added `quant/backtest/comparison.py` with deterministic offline multi-configuration comparison support over caller-provided `RepeatableExperimentConfig`, `ReplayReport`, and `ReplayResult` inputs.
- Added stable `comparison_id` hashing from normalized local inputs with input-order-independent identity.
- Added controlled validation issues for empty/single entry sets, duplicate configuration ids, stale experiment ids, missing replay payloads, mismatched windows, mismatched starting capital, inconsistent report metadata, and missing/invalid comparison metrics.
- Added serialization-friendly comparison output with deterministic ranking policy, per-configuration rows, leader-relative metric deltas, assumption propagation, coverage facts, and artifact-reference carry-through.

## reproducibility and boundary regression coverage added

- Added offline tests proving repeated comparison builds over identical normalized inputs return identical ids, ordering, and payloads.
- Added offline tests proving input order does not change ranking and equal-metric ties resolve deterministically by `configuration_id`.
- Added offline tests for duplicate ids, stale experiment ids, missing metrics, non-finite metrics, mismatched comparison windows, mismatched starting capital, and controlled error raising.
- Added offline tests proving replay assumption fields remain visible in comparison rows and normalized output shape is stable for later controller decisions.

## readiness gate updates

- Updated Phase 5 readiness truth so:
  - `multi_configuration_comparison_workflows` -> `pass`
  - `offline_regression_boundaries_and_reproducibility` -> `pass`
- Current local gate after TASK-150:
  - `phase_closure_ready=true`
  - status counts: `pass=7`, `warn=0`, `blocked=0`, `fail=0`
  - follow-up queue: `0`
  - follow-up batches: `0`

## tests run

- `python3 -m unittest discover -s tests/backtest -p 'test_*.py'` -> PASS (`Ran 38 tests`)

## default network behavior

- Offline-safe only.
- No network calls, live data access, warehouse reads, DataHub/FeatureHub/Scanner reads, credentials, browser/session state, or hidden clock-dependent behavior were added.
- Comparison workflows operate only on caller-provided local experiment/report/result objects already present in memory.

## live-enabled PASS/SKIP/FAIL result and root-cause evidence

- `SKIP`
- Root cause / evidence: this handoff is local/offline StrategyLab and BacktestEngine hardening only; live tests were not required or allowed.

## deviations

- None.

## risks/follow-up

- Comparison ranking is intentionally fixed to `total_return desc -> max_drawdown asc -> win_rate desc -> ending_total_equity desc -> configuration_id asc`; future controller work should keep that contract explicit if additional ranking modes are introduced.
- The workflow compares already-built local replay/report objects; it still does not read persisted artifacts from disk, which keeps TASK-150 offline-safe and within scope.
