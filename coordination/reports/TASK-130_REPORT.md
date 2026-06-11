# TASK-130 Report

## files changed
- `quant/datahub/quality.py`
- `quant/datahub/personal_readiness.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_quality.py`
- `tests/datahub/test_personal_readiness.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`

## implementation summary
- Selected readiness batch id: `quality_reports__datahub_hardening__source__batch_01`
- Included follow-up id: `quality_reports__quality_reports_source_coverage_metadata__source_coverage_metadata`
- Added a generic `additional_checks` path to `LocalRefreshQualityHelper.build_quality_report_records(...)` so deterministic local KPI checks can be emitted as schema-valid `DATA_QUALITY_REPORT` records without changing existing baseline behavior.
- Added `build_personal_trading_readiness_quality_kpi_checks(...)` in `quant/datahub/personal_readiness.py` to expose local readiness metadata as four bounded quality-report KPI checks:
  - `personal_trading_readiness_domain_coverage_kpi`
  - `personal_trading_readiness_capability_coverage_kpi`
  - `personal_trading_readiness_follow_up_queue_kpi`
  - `personal_trading_readiness_follow_up_batches_kpi`
- KPI details now cover:
  - domain status counts and domain ids by `pass` / `warn` / `blocked` / `fail`
  - required and optional capability status counts by `covered` / `partial` / `planned` / `missing`
  - required capability readiness counts by `pass` / `warn` / `blocked` / `fail`
  - source-quality capability status counts
  - follow-up status counts and disposition counts
  - owner-action follow-up ids for `owner_credential_blocker` and `owner_waiver_required`
  - follow-up batch counts, full deterministic batch id list, and batch ids split by executable vs owner-action disposition
- Every KPI details payload includes conservative metadata flags:
  - `metadata_scope=local_readiness_observability`
  - `observability_only=true`
  - `proves_adapter_completeness=false`
  - explanatory note that KPI hardening does not prove any real-source adapter became complete

## readiness truth after hardening
- Default readiness domain counts now resolve to `pass=4`, `warn=5`, `blocked=1`, `fail=0`.
- Default follow-up queue now resolves to `41` items:
  - status counts: `warn=40`, `blocked=1`, `fail=0`
  - disposition counts: `datahub_hardening=39`, `owner_credential_blocker=1`, `owner_waiver_required=1`
- Default follow-up batch list now resolves to `10` deterministic batch ids and no longer includes `quality_reports__datahub_hardening__source__batch_01`.

## schema validation behavior
- No `DATA_QUALITY_REPORT` contract change was required.
- New KPI records are emitted through the existing quality-record builder and validate via `DatasetRegistry.validate_record(DatasetName.DATA_QUALITY_REPORT, record)`.
- Tests assert every generated KPI quality record remains schema-valid.

## quality-report capability/source truth changed
- `source_coverage_metadata` in `quant/datahub/source_capabilities.py` changed from `partial` to `covered`.
- `local_data_quality_engine` notes in `quant/datahub/source_catalog.py` were tightened to state that readiness coverage KPIs improve observability only and do not claim source completeness.

## tests run
- `python3 -m unittest tests.datahub.test_quality` -> PASS (`Ran 10 tests`)
- `python3 -m unittest tests.datahub.test_personal_readiness` -> PASS (`Ran 9 tests`)
- `python3 -m unittest tests.datahub.test_source_capabilities` -> PASS (`Ran 46 tests`)
- `python3 -m unittest tests.datahub.test_source_catalog` -> PASS (`Ran 10 tests`)
- `python3 -m py_compile quant/datahub/quality.py quant/datahub/personal_readiness.py quant/datahub/source_capabilities.py quant/datahub/source_catalog.py tests/datahub/test_quality.py tests/datahub/test_personal_readiness.py tests/datahub/test_source_capabilities.py tests/datahub/test_source_catalog.py` -> PASS

## default network behavior
- Default tests remain offline-safe.
- No live flag was enabled.
- No real-source adapter call, credential, token, cookie, or external network path was added.
- KPI generation uses only repository-local readiness/catalog/capability metadata and existing offline smoke evidence.

## live-enabled PASS/SKIP/FAIL result and root-cause evidence for real-source tasks
- `SKIP - not applicable`
- Root-cause evidence: TASK-130 is a local-only quality-report metadata hardening task; the handoff forbids live tests and no real-source code path was changed.

## deviations
- None.

## risks/follow-up
- KPI records are local readiness observability metadata only; they should not be interpreted as proof of trading-grade source completeness.
- If Controller later wants readiness KPI records persisted as a dedicated artifact/run output rather than helper-generated records, that should be dispatched as a separate local-only task.
