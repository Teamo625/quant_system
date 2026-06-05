# TASK-086 Report

- files changed:
  - `quant/datahub/datasets.py`
  - `quant/datahub/source_catalog.py`
  - `quant/datahub/source_capabilities.py`
  - `tests/datahub/test_datasets.py`
  - `tests/datahub/test_source_catalog.py`
  - `tests/datahub/test_source_capabilities.py`

- tests run:
  - `python3 -m unittest tests/datahub/test_datasets.py` -> PASS
  - `python3 -m unittest tests/datahub/test_source_catalog.py` -> PASS
  - `python3 -m unittest tests/datahub/test_source_capabilities.py` -> PASS

- default network behavior:
  - Offline-only.
  - No live adapters, no live source fetches, no credential use, no default-network regression introduced.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence:
  - SKIP
  - Reason: handoff is contract-only and explicitly forbids live-enabled smoke or source fetching.

- capability truth changes:
  - Added canonical `DatasetName.FUND_PREMIUM_DISCOUNT` contract with required fields: `fund_code`, `market`, `trade_date`, `premium_discount_rate`, `source`, `ingested_at`, `schema_version`.
  - Added optional source-truth fields for `market_price`, `nav`, `iopv`, `premium_discount_amount`, `source_route`, and `source_category`.
  - Added semantic validation so `market_price` / `nav` / `iopv` must be nonnegative when present, while negative `premium_discount_rate` remains allowed for true discount records.
  - Updated `fund_premium_discount` capability mapping from derived `DAILY_BARS` + `FUND_NAV_SNAPSHOT` linkage to dedicated `FUND_PREMIUM_DISCOUNT`.
  - `fund_premium_discount` remains `partial`; metadata now states adapter/source-fact implementation is still pending.
  - Updated source catalog coverage only for relevant public ETF/fund family: `akshare_cn_hk_public_family`.

- deviations:
  - None.

- risks/follow-up:
  - Next handoff should implement a bounded public ETF/fund premium-discount source-fact adapter targeting `FUND_PREMIUM_DISCOUNT`.
  - That follow-up should add gated live smoke evidence when controller reopens real-source work.
  - Contract intentionally stays conservative: price/NAV components remain optional because public routes may expose only the rate or only partial calculation inputs.
