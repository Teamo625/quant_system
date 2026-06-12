# TASK-132 Report

## files changed

- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`

## implementation summary

- Tightened `a_share_northbound_flow` capability wording so `stock_hsgt_individual_em` is the only currently proven no-credential symbol-level route from TASK-132 evidence.
- Reworded `stock_hsgt_individual_detail_em` in capability/catalog metadata as an attempted bounded fallback, not established fallback coverage.
- Added focused offline assertions to prevent future wording from implying proven fallback availability or redundancy without live evidence.

## exact northbound fallback wording correction

- Capability truth now says TASK-132 implemented an attempted bounded `stock_hsgt_individual_detail_em` fallback, but current live evidence does not yet prove that fallback because the route is upstream-broken and the primary route appears stale for recent bounded windows.
- Catalog notes now mirror the same truth and no longer describe the detail route as established fallback coverage.

## tests run

- PASS: `python3 -m unittest tests.datahub.test_source_capabilities`
- PASS: `python3 -m unittest tests.datahub.test_source_catalog`
- PASS: `python3 -m unittest tests.datahub.test_akshare_a_share_northbound_flow_adapter`
- PASS: `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_a_share_northbound_flow_live`

## default network behavior

- Default tests remained offline-safe.
- The default live module stayed env-gated; with `QUANT_SYSTEM_LIVE_TESTS` unset, the live smoke path skipped and did not perform real network calls.

## live-enabled PASS/SKIP/FAIL result and root-cause evidence

- Preserved prior live-enabled result: `SKIP`.
- No new live smoke was run because this rework changed wording/tests only and did not change real-source behavior.
- Preserved root-cause evidence from accepted TASK-132 execution context: `stock_hsgt_individual_em` appears stale for the recent bounded window, while bounded `stock_hsgt_individual_detail_em` currently fails upstream with `TypeError: 'NoneType' object is not subscriptable`.

## deviations

- None.

## risks / follow-up

- Current public northbound recent-history continuity remains unresolved; controller/review should continue to treat the detail route as unproven until a fresh live-enabled PASS demonstrates usable bounded fallback behavior.
- Capability status remains intentionally conservative and does not prove completeness or route redundancy.
