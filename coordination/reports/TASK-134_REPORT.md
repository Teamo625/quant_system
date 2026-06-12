# TASK-134 Report

## files changed
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_hk_corporate_actions_adapter.py`
- `tests/datahub/test_akshare_hk_corporate_actions_live.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`

## implementation summary by capability
- `hk_corporate_actions`: extended `AkshareHKCorporateActionsAdapter` from single-symbol fetch to caller-provided multi-symbol batches with per-symbol normalization, deduped symbol requests, and preserved route-distinct primary/fallback history collection.
- `hk_corporate_actions`: added offline regression coverage for multi-symbol batch ordering/deduplication and per-symbol fallback behavior inside a mixed batch.
- `hk_corporate_actions`: updated capability/source-catalog wording from one-symbol proof to bounded multi-symbol dividend/no-distribution proof while keeping status `partial` and explicitly retaining non-dividend taxonomy plus independent-route-redundancy gaps.
- Other HK batch capabilities in this handoff were not changed.

## tests run
- `python3 -m unittest tests.datahub.test_akshare_hk_corporate_actions_adapter tests.datahub.test_source_capabilities tests.datahub.test_source_catalog`
- `python3 -m unittest tests.datahub.test_akshare_hk_corporate_actions_live`
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest tests.datahub.test_akshare_hk_corporate_actions_live`

## default network behavior
- Default tests remain offline-safe.
- Offline adapter tests use injected fixtures; no real network is required.
- Live smoke stays explicitly environment-gated by `QUANT_SYSTEM_LIVE_TESTS=1` and is not enabled by default.

## live-enabled PASS/SKIP/FAIL result and root-cause evidence
- `hk_corporate_actions`: PASS
  - Command: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest tests.datahub.test_akshare_hk_corporate_actions_live`
  - Result: `Ran 4 tests ... OK`
  - Evidence: the live smoke executed without skip, requested `("00700.HK", "00005.HK")`, and now asserts two-symbol batch preservation plus schema-valid normalized records.

## deviations
- None.

## risks/follow-up
- `hk_corporate_actions` is still correctly `partial`: no proof was added for split/rights/consolidation or other non-dividend action families.
- The proof still relies on same-family AKShare public routes; independent public-source redundancy remains unproven.
- `hk_universe_reference`, `hk_daily_bars`, `hk_valuation_history`, `hk_financial_data`, and `hk_turnover_liquidity` remain for later cluster hardening if the controller wants broader TASK-134 scope before closure.
