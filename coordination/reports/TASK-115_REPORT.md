# TASK-115 Report

## files changed
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_hk_corporate_actions_adapter.py`
- `tests/datahub/test_akshare_hk_corporate_actions_live.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`

## implementation summary
- Hardened `AkshareHKCorporateActionsAdapter` to combine proven HK corporate-actions rows from both `stock_hk_dividend_payout_em` and `stock_hk_fhpx_detail_ths` when available, instead of using the THS route only as a network fallback.
- Preserved shared `DatasetName.CORPORATE_ACTIONS` contract, explicit `source_route`, canonical HK symbols, deterministic sorting, and date-window filtering.
- Added explicit HK dividend taxonomy split between `dividend_distribution` and source-backed `dividend_no_distribution` for THS rows such as `方案=不分红`.
- Tightened the HK corporate-actions live classifier so route-name-bearing contract/payload errors no longer downgrade to environment `SKIP`.
- Kept `hk_corporate_actions` conservative at `partial`; only wording changed to reflect proven route/taxonomy/history truth.

## tests run
- `python3 -m unittest tests/datahub/test_akshare_hk_corporate_actions_adapter.py` -> PASS
- `python3 -m unittest tests/datahub/test_source_capabilities.py` -> PASS
- `python3 -m unittest tests/datahub/test_source_catalog.py` -> PASS
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_hk_corporate_actions_live.py` -> PASS (`live` smoke skipped by default)
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_corporate_actions_live.py` -> PASS

## default network behavior
- Default/offline tests remain network-safe.
- Adapter/unit tests use injected fixtures/stubs for both HK routes.
- `tests/datahub/test_akshare_hk_corporate_actions_live.py` is still gated by `QUANT_SYSTEM_LIVE_TESTS=1` and skips by default.

## live-enabled PASS/SKIP/FAIL result and root-cause evidence
- Result: PASS.
- Live smoke for `00700.HK` validated shared-schema HK corporate-actions records, both route names, and both action families under the combined adapter result.
- Direct live route evidence in this environment:
  - `stock_hk_dividend_payout_em("00700")` -> `27` rows; oldest implemented distribution record observed at `除净日=2005-04-19`.
  - `stock_hk_fhpx_detail_ths("0700")` -> `93` rows; oldest decision-history row observed at `公告日期=2004-08-19`, `方案=不分红`, `进度=预案`.
  - Combined adapter fetch for `00700.HK`, `2000-01-01..today` -> `120` normalized route-distinct records, routes `{stock_hk_dividend_payout_em, stock_hk_fhpx_detail_ths}`, families `{dividend_distribution, dividend_no_distribution}`, minimum `event_date=2004-08-19`.
- No network/proxy/DNS/TLS/upstream skip occurred in the enabled rerun.

## capability truth changed
- `hk_corporate_actions` status remains `partial`.
- `quant/datahub/source_capabilities.py` and `quant/datahub/source_catalog.py` wording now states the proven bounded truth:
  - implemented one-symbol dividend/distribution history via `stock_hk_dividend_payout_em`
  - implemented same-family THS dividend-plan / no-distribution decision history via `stock_hk_fhpx_detail_ths`
  - still not promoted to closure-grade HK corporate-actions completeness

## route coverage / taxonomy / history behavior
- Source route coverage now includes both proven no-credential HK routes when available:
  - `stock_hk_dividend_payout_em`
  - `stock_hk_fhpx_detail_ths`
- Event-family taxonomy now explicitly distinguishes:
  - `dividend_distribution`
  - `dividend_no_distribution`
- Date-window behavior remains post-normalization filtering on `event_date`, including THS rows that fall back to announcement-date history when no ex/payout date exists.
- Route-distinct overlapping records are preserved separately with explicit `source_route`; deterministic ordering is by symbol, event date, action family, route, and payload ref.

## stronger taxonomy/history outcome
- Implemented stronger public-source HK dividend-related taxonomy/history coverage.
- Not implemented:
  - caller-provided multi-symbol HK corporate-actions batches
  - non-dividend HK corporate-action families such as split / rights / consolidation
- Because of those limits, capability/catalog truth was tightened but not promoted.

## deviations
- None.

## risks/follow-up
- `hk_corporate_actions` still lacks broader HK corporate-action families beyond dividend-related distribution / no-distribution history.
- The strengthened path is still one-symbol-at-a-time adapter access; batch breadth remains unproven.
- Future hardening should prove whether stable no-credential HK split, rights-issue, consolidation, or other non-dividend event routes exist before any promotion.
