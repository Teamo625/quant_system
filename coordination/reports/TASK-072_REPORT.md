# TASK-072 Report - DataHub A-share Daily Bars Batch Hardening

## Files Changed

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/source_capabilities.py`
- `tests/datahub/test_akshare_adapter.py`
- `tests/datahub/test_akshare_live.py`
- `tests/datahub/test_source_capabilities.py`
- `coordination/reports/TASK-072_REPORT.md`

## Summary

Implemented caller-provided multi-symbol A-share daily bar access in `AkshareAShareDailyBarAdapter`.

The adapter now:

- accepts one or more requested A-share symbols through `SourceRequest.symbols`
- preserves one-symbol behavior
- rejects missing/empty symbols clearly
- validates symbol formats before fetching
- fetches each requested symbol through the existing public AKShare daily bar route
- combines normalized `DatasetName.DAILY_BARS` records
- deduplicates by `(symbol, trade_date, source)`
- sorts deterministically by symbol, trade date, and source
- preserves date bounds and price-adjustment behavior

Because offline tests and a live-enabled smoke both validate multi-symbol behavior, `a_share_daily_bars` was promoted from `partial` to `covered` in `quant/datahub/source_capabilities.py`. No unrelated capability truth was changed.

## Tests Run

- `python3 -m unittest tests/datahub/test_akshare_adapter.py`
  - PASS: `Ran 10 tests ... OK`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`
  - PASS: `Ran 18 tests ... OK`
- `python3 -m unittest -v tests/datahub/test_akshare_live.py`
  - PASS with default skip: `OK (skipped=1)`
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_live.py`
  - PASS: `Ran 1 test ... OK`

## Default Network Behavior

Default tests remain offline-safe.

`tests/datahub/test_akshare_live.py` still skips unless `QUANT_SYSTEM_LIVE_TESTS=1` is set. Offline adapter tests use injected fake fetch callables and do not perform live network access.

## Live-Enabled PASS/SKIP/FAIL Result

Result: PASS.

Evidence:

- Command: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_live.py`
- Result line: `test_live_akshare_daily_bars_smoke ... ok`
- The live smoke requested two A-share symbols, `000001.SZ` and `600000.SH`, and schema-validated at least one returned `DatasetName.DAILY_BARS` record after confirming both requested symbols produced usable records.

No live-network rework is required.

## Capability Truth Change

Changed: YES.

- `a_share_daily_bars` moved from `CapabilityStatus.PARTIAL` to `CapabilityStatus.COVERED`.
- `gap_reason` and `recommended_handoff_theme` were cleared only for this capability.

Rationale:

- The original gap was one-symbol-only access.
- TASK-072 now supports caller-provided multi-symbol batches.
- Offline tests verify deterministic multi-symbol normalization, dedupe, sorting, date-bound propagation, and schema validation.
- Live-enabled smoke passed against two real A-share symbols.

## Deviations From Handoff

None.

## Risks Or Follow-Up Tasks

- This hardens caller-provided batch access; it does not implement automatic full-market discovery or full-history local backfill.
- Public AKShare upstream availability can still vary, but default tests remain offline-safe and live evidence passed in this execution.
- Remaining DataHub trading-usable gaps still include A-share lifecycle/ST history, valuation/capital-flow/financial history breadth, A-share minute bars, HK daily bars/universe breadth, ETF/fund breadth, index constituent/rebalance history, sector membership history, macro/policy breadth, source-health KPIs, and blocked paid Tushare index weight evidence.
