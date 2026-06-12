# TASK-131 Report

## files changed
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_source_catalog.py`
- `coordination/reports/TASK-131_REPORT.md`

## exact source-catalog truth correction made
- Removed the misleading `BaoStock 5/15/30/60-minute history` wording from `akshare_cn_hk_public_family` minute-bar notes.
- Kept AKShare-family minute-bar truth limited to `stock_zh_a_hist_min_em`, direct Eastmoney kline fallback, and limited recent `stock_zh_a_minute` fallback.
- Preserved BaoStock minute-bar history truth only under `baostock_public_cn`.
- Added a focused regression asserting the AKShare-family notes do not mention `BaoStock`, while the separate BaoStock catalog-entry test remains in place.

## tests run
- `python3 -m unittest tests.datahub.test_source_catalog` -> PASS

## default network behavior
- Offline-safe only.
- No default test path performs live network access.
- No live test entrypoint or environment-gated live path was changed.

## live-enabled PASS/SKIP/FAIL result and root-cause evidence
- Not rerun / not required for this source-catalog-only rework.
- Review already accepted live-enabled PASS for the materially changed real-source paths in the earlier TASK-131 execution.
- This rework changes catalog wording and an offline regression only; no adapter behavior or live path changed.

## deviations
- None.

## risks/follow-up
- Review should confirm `akshare_cn_hk_public_family` no longer attributes BaoStock minute-bar coverage and that `baostock_public_cn` remains the only BaoStock source-family record for that truth.
