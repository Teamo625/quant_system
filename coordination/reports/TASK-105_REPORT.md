# TASK-105 Report

## Files changed
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/datasets.py`
- `quant/datahub/source_capabilities.py`
- `tests/datahub/test_akshare_a_share_margin_financing_lending_adapter.py`
- `tests/datahub/test_akshare_a_share_margin_financing_lending_live.py`
- `tests/datahub/test_source_capabilities.py`
- `coordination/reports/TASK-105_REPORT.md`

## Implementation summary
- Expanded `AkshareAShareMarginFinancingLendingAdapter` from one-symbol fetch to caller-provided multi-symbol bounded date-window batches, grouped by validated SSE/SZSE detail routes and deduped by canonical symbol.
- Added emitted source-truth fields `exchange` and `source_route` to normalized margin records and extended the dataset schema with compatible optional fields.
- Tightened live-unavailable classification so `stock_margin_detail_*`, `querymargin.do`, and `ShowReport` tokens alone no longer downgrade payload/schema/signature defects into environment `SKIP`.
- Made BSE/BJ handling truthful: Beijing symbols now fail fast because no validated public AKShare BSE symbol-level margin-detail route is currently proven.
- Updated capability wording for `a_share_margin_financing_and_lending`; status remains `partial`.

## Tests run
- `python3 -m unittest tests/datahub/test_akshare_a_share_margin_financing_lending_adapter.py`
  - `Ran 17 tests ... OK`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_margin_financing_lending_live.py`
  - `Ran 5 tests ... OK (skipped=1)`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`
  - `Ran 38 tests ... OK`
- `python3 -m unittest tests/datahub/test_datasets.py`
  - `Ran 42 tests ... OK`
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_margin_financing_lending_live.py`
  - `Ran 5 tests ... OK`

## Default network behavior
- Default adapter and capability tests are offline-safe.
- The live suite still skips by default unless `QUANT_SYSTEM_LIVE_TESTS=1` is set.
- New regression coverage for classifier truthfulness, multi-symbol batching, BJ rejection, and provenance fields is deterministic and offline-only.

## Live-enabled PASS/SKIP/FAIL result and evidence
- Result: `PASS`
- Command: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_margin_financing_lending_live.py`
- Evidence: live smoke completed successfully in this environment and asserted a real normalized record with:
  - `source == "akshare_cn_hk_public_family"`
  - `market == "A_SHARE"`
  - `exchange == "SSE"`
  - `source_route == "stock_margin_detail_sse"`
  - canonical A-share symbol format and `DatasetRegistry` contract validation
- No environment/upstream skip root cause applied in the final run.

## Capability truth changed?
- `a_share_margin_financing_and_lending` remains `partial`.
- Gap wording now states the stronger truth: validated public AKShare multi-symbol bounded SSE/SZSE detail history with explicit provenance exists, but BSE symbol-level coverage, symbol-compatible summary reconciliation, and longer-history completeness remain unproven.

## Deviations
- None.

## Risks/follow-up
- No validated public AKShare BSE symbol-level margin-detail route is currently implemented; BJ symbols are intentionally rejected until a truthful route is proven.
- Exchange summary routes were not normalized into `MARGIN_FINANCING_LENDING` because their shapes are exchange-level, not symbol-level.
- Live PASS evidence in this task exercised the SSE detail route; SZSE route truth is covered offline but could use separate live proof in a future hardening task if the controller wants exchange-by-exchange live evidence.
