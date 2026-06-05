# TASK-073 Report

## files changed
- `quant/datahub/datasets.py`
- `quant/datahub/source_catalog.py`
- `quant/datahub/source_capabilities.py`
- `tests/datahub/test_datasets.py`
- `tests/datahub/test_source_catalog.py`
- `tests/datahub/test_source_capabilities.py`
- `coordination/reports/TASK-073_REPORT.md`

## tests run
- `python3 -m unittest tests/datahub/test_datasets.py` -> PASS (`Ran 41 tests`)
- `python3 -m unittest tests/datahub/test_source_catalog.py` -> PASS (`Ran 7 tests`)
- `python3 -m unittest tests/datahub/test_source_capabilities.py` -> PASS (`Ran 19 tests`)

## default network behavior
- Default path remains offline-only.
- This handoff added no adapters, no live test changes, and no network calls.
- The executed unit tests passed without live access.

## live-enabled PASS/SKIP/FAIL result and root-cause evidence
- `SKIP`
- Reason: handoff is contract-only and explicitly forbids live-enabled smoke or source fetching.
- Evidence: only metadata/schema/tests under allowed files changed; `quant/datahub/adapters/` and `tests/datahub/*live.py` were untouched.

## capability truth changes
- Added canonical dataset contract `DatasetName.INSTRUMENT_STATUS_HISTORY`.
- Added schema fields for lifecycle/status history records:
  `symbol`, `market`, `effective_start_date`, optional `effective_end_date`,
  `status_type`, `status`, optional `raw_status`, optional `status_reason`,
  optional `exchange`, optional `board`, `source`, `ingested_at`, `schema_version`.
- Added semantic validation for non-empty status identifiers and ordered effective dates.
- Updated source catalog coverage so `akshare_cn_hk_public_family` and `tushare_pro_cn_core`
  both advertise `INSTRUMENT_STATUS_HISTORY` under A-share full-data coverage.
- Updated capability `a_share_listing_delisting_st_status` to map to
  `INSTRUMENT_STATUS_HISTORY` and remain `partial`.
- Refined the gap text to reflect the new truth: contract exists, adapter hardening is still pending.

## deviations
- None.

## risks/follow-up
- Next recommended task: implement a bounded A-share `INSTRUMENT_STATUS_HISTORY` adapter
  for listing/delisting/ST/*ST/normal status deltas, with gated live smoke evidence.
- Current contract does not yet prove source breadth, taxonomy normalization completeness,
  or historical continuity; capability must stay `partial` until adapter/live evidence exists.
