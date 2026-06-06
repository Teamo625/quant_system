# TASK-122 Report

- files changed:
  - `quant/datahub/datasets.py`
  - `tests/datahub/test_datasets.py`
  - `coordination/reports/TASK-122_REPORT.md`

- rework summary:
  - Replaced the global nonnegative rule on `FUND_SCALE_SHARE_SNAPSHOT.metric_value` with dataset-specific validation.
  - Negative `metric_value` is now accepted when `metric_code` or `observation_type` explicitly indicates a change-style observation.
  - Negative `metric_value` is still rejected for non-change level metrics such as `shares_outstanding`.
  - Added focused offline regression tests for both cases and updated rule-table assertions to match the dataset-specific validator.

- tests run:
  - `python3 -m unittest tests.datahub.test_datasets`
  - Result: `Ran 48 tests` / `OK`
  - `python3 -m unittest tests.datahub.test_datasets tests.datahub.test_source_capabilities tests.datahub.test_source_catalog`
  - Result: `Ran 100 tests` / `OK`

- default network behavior:
  - Offline-only.
  - No adapter code changed.
  - No default test performs live network access.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence for real-source tasks:
  - `SKIP`
  - No live test was required or permitted for this rework because scope stayed schema/test-only and did not modify adapters or source collection behavior.

- deviations:
  - None.

- risks/follow-up:
  - Signed-metric allowance currently depends on stable change-style naming in `metric_code` or `observation_type`; future adapter work should keep that naming explicit or extend the contract deliberately if a new signed metric family is introduced.
  - `fund_scale_and_share` remains conservative at `partial`; this rework does not add new source proof or adapter-backed emission.
