# TASK-122 Report

- files changed:
  - `quant/datahub/datasets.py`
  - `quant/datahub/source_capabilities.py`
  - `quant/datahub/source_catalog.py`
  - `tests/datahub/test_datasets.py`
  - `tests/datahub/test_source_capabilities.py`
  - `tests/datahub/test_source_catalog.py`

- contract/schema summary:
  - Added `DatasetName.FUND_SCALE_SHARE_SNAPSHOT` as the first-class ETF/fund scale/share canonical contract.
  - Required fields: `fund_code`, `market`, `observation_date`, `observation_type`, `metric_code`, `metric_value`, `source`, `ingested_at`, `schema_version`.
  - Optional provenance/context fields: `metric_unit`, `value_currency`, `source_route`, `source_ts`.
  - Added semantic rules requiring non-empty `fund_code`/`market`/`observation_type`/`metric_code` and non-negative `metric_value`.

- compatibility confirmation for existing ETF/fund datasets:
  - `FUND_NAV_SNAPSHOT` remains unchanged and still accepts optional overlapping `shares_outstanding` / `fund_scale`.
  - `FUND_FLOW` remains unchanged and still accepts optional overlapping `shares_change`.
  - `FUND_PROFILE` remains unchanged.
  - Added regression coverage so the new canonical contract does not make overlap fields required in older ETF/fund datasets.

- capability truth changes:
  - `fund_scale_and_share` now maps to `FUND_SCALE_SHARE_SNAPSHOT`.
  - Status remains `partial`.
  - Gap text now states that the contract exists, but accepted source proof is still limited to overlapping profile/NAV/exchange scale-share facts; broader fund-class breadth, longer history continuity, richer share-change coverage, and route redundancy remain incomplete.
  - Source catalog ETF/fund coverage now includes the new canonical dataset under the existing accepted AKShare/Tushare source families.

- tests run:
  - `python3 -m unittest tests.datahub.test_datasets tests.datahub.test_source_capabilities tests.datahub.test_source_catalog`
  - Result: `Ran 99 tests in 0.019s` / `OK`

- default network behavior:
  - Offline-only.
  - No adapter code changed.
  - No default test performs live network access.
  - Existing catalog/capability offline guards remain covered, including the socket-blocked catalog test.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence:
  - No live test required.
  - Reason: this execution was contract/capability/source-metadata only; no real-source adapter behavior or live smoke path was changed.

- deviations:
  - None.

- risks/follow-up:
  - The new canonical contract is not yet emitted directly by any adapter; current source truth still comes from overlapping existing ETF/fund routes.
  - Future hardening should add adapter-backed emission only when a controller handoff explicitly reopens real-source implementation and live smoke requirements for this dataset.
