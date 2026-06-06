# TASK-097 Report

- files changed
  - `quant/datahub/datasets.py`
  - `quant/datahub/source_catalog.py`
  - `quant/datahub/source_capabilities.py`
  - `quant/datahub/adapters/akshare.py`
  - `quant/datahub/adapters/__init__.py`
  - `quant/datahub/__init__.py`
  - `tests/datahub/test_datasets.py`
  - `tests/datahub/test_source_catalog.py`
  - `tests/datahub/test_source_capabilities.py`
  - `tests/datahub/test_akshare_a_share_adjustment_factors_adapter.py`
  - `tests/datahub/test_akshare_a_share_adjustment_factors_live.py`
  - `coordination/reports/TASK-097_REPORT.md`

- contract/profile chosen
  - Added dedicated dataset contract `DatasetName.ADJUSTMENT_FACTORS` instead of overloading `DatasetName.CORPORATE_ACTIONS`.
  - Required stable fields are `symbol`, `market`, `factor_date`, `adjustment_basis`, `adjustment_factor`, `raw_payload_ref`, `source`, optional `source_ts`, `ingested_at`, `schema_version`.
  - Rationale: adjustment factors are symbol x factor-date numeric source facts with explicit qfq/hfq basis, not event-style `value` blobs.

- public-route investigation result
  - Investigated local `akshare` runtime first.
  - Confirmed `ak.stock_zh_a_daily(symbol=..., adjust='qfq-factor'|'hfq-factor')` exists in the installed dependency and returns first-class factor rows rather than adjusted prices.
  - Local live probes returned DataFrame columns `['date', 'qfq_factor']` and `['date', 'hfq_factor']` for `sh600000` / `sz000001`, plus historical factor-change rows including baseline rows such as `1900-01-01`.
  - Implemented a dedicated AKShare adapter on that route with caller-provided symbols, explicit bounded `start_date` / `end_date` filtering, strict A-share symbol validation, deterministic `AKAF|...` raw refs, and stable sort/dedupe by `(symbol, factor_date, source, adjustment_basis)`.

- whether capability truth changed
  - Yes: `a_share_adjustment_factors` now maps to `DatasetName.ADJUSTMENT_FACTORS` instead of `DatasetName.CORPORATE_ACTIONS`.
  - Status remains `partial`.
  - Reason for staying conservative: the public AKShare/Sina route exposes adjustment-factor change-point rows, but full per-trade-date continuity is not guaranteed and no second no-credential public source was validated in this task.

- tests run
  - `python3 -m unittest tests/datahub/test_datasets.py`
  - `python3 -m unittest tests/datahub/test_source_capabilities.py`
  - `python3 -m unittest tests/datahub/test_source_catalog.py`
  - `python3 -m unittest tests/datahub/test_akshare_a_share_adjustment_factors_adapter.py`
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_adjustment_factors_live.py`
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_adjustment_factors_live.py`

- default network behavior
  - Default/offline tests remain network-safe.
  - The new live smoke is gated by `QUANT_SYSTEM_LIVE_TESTS=1`.
  - Verified explicit default behavior with `env -u QUANT_SYSTEM_LIVE_TESTS ...`: classifier tests ran offline and the live smoke skipped.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence
  - PASS.
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_adjustment_factors_live.py` ran `3` tests and all passed.
  - The live smoke fetched real AKShare/Sina adjustment-factor rows for `600000.SH` and `000001.SZ`, validated schema compliance, verified both `qfq` and `hfq` bases, and confirmed returned `factor_date` values stayed inside the bounded request window.

- deviations
  - None.

- risks/follow-up
  - The public Sina-backed factor route appears to expose change-point rows, not guaranteed every-trade-day rows. If downstream consumers need dense daily continuity, a future task should define whether forward-fill materialization belongs in DataHub contract expansion or downstream logic.
  - No no-credential redundant source was added in this task. A future hardening task can look for a second public route or explicitly document single-route operational risk if none is feasible.
