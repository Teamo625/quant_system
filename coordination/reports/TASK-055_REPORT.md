# TASK-055 Report

- files changed
  - `quant/datahub/datasets.py`
  - `quant/datahub/source_capabilities.py`
  - `quant/datahub/source_catalog.py`
  - `tests/datahub/test_datasets.py`
  - `tests/datahub/test_source_capabilities.py`
  - `tests/datahub/test_source_catalog.py`

- implementation summary
  - Added dedicated `DatasetName.INDEX_WEIGHT_HISTORY` registry entry, schema, and semantic rules.
  - Kept `INDEX_CONSTITUENTS` unchanged for membership timeline semantics.
  - Remapped capability `index_weight_history` to the explicit weight-history dataset and kept status `planned`.
  - Added conservative source-catalog coverage only under credentialed source family `tushare_pro_cn_core`.

- tests run
  - `python3 -m unittest tests/datahub/test_datasets.py`
    - PASS (`Ran 38 tests`)
  - `python3 -m unittest tests/datahub/test_source_capabilities.py`
    - PASS (`Ran 17 tests`)
  - `python3 -m unittest tests/datahub/test_source_catalog.py`
    - PASS (`Ran 7 tests`)
  - `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`
    - PASS (`Ran 822 tests`, `skipped=36`)

- default network behavior
  - Offline-only. No live fetch logic or adapter code was added.
  - Default tests remained local and deterministic.
  - Existing offline guards in source-capability/source-catalog tests still passed.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence
  - `SKIP`
  - TASK-055 handoff forbids live tests.
  - This task is contract/catalog/capability-only and introduced no real-source adapter or live fetch behavior.

- deviations
  - None.

- risks/follow-up
  - `index_weight_history` remains `planned`; bounded adapter implementation is still required in a later handoff.
  - Current catalog truth intentionally exposes `INDEX_WEIGHT_HISTORY` only via credentialed `tushare_pro_cn_core`; no public-source coverage is implied.
  - Upstream routes may express weights with different units; the contract preserves this conservatively through optional `weight_unit`.
