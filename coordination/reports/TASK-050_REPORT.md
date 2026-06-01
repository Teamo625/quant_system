# TASK-050 Report - DataHub AKShare A-share Minute Bars Adapter

## Task ID

TASK-050

## Summary

Implemented a narrow public AKShare A-share minute-bars adapter slice for `DatasetName.MINUTE_BARS` under source `akshare_cn_hk_public_family`.

Key scope implemented:

- Added `AkshareAShareMinuteBarsAdapter` with one-symbol, bounded one-trade-date request constraints.
- Added deterministic normalization into `MINUTE_BARS` contract fields (`trade_date`, `bar_time`, `open/high/low/close/volume`, optional `amount/vwap/source_ts`).
- Added deterministic sort and dedup by `(symbol, bar_time)` with conflict detection.
- Added primary/fallback AKShare route support:
  - primary: `stock_zh_a_hist_min_em`
  - fallback: `stock_zh_a_minute`
- Added strict symbol validation/normalization for A-share only (SH/SZ/BJ; rejects HK/ETF/index/malformed/multi-symbol).
- Added route-signature compatibility hard-failure behavior (not classified as environment unavailability).
- Updated capability and catalog truth to reflect public AKShare minute-bars partial coverage.
- Added offline adapter tests and gated live smoke tests.

## Files Changed

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_a_share_minute_bars_adapter.py` (new)
- `tests/datahub/test_akshare_a_share_minute_bars_live.py` (new)
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`

## Tests Run

### Required / focused

1. `python3 -m unittest tests/datahub/test_akshare_a_share_minute_bars_adapter.py`
- Result: PASS (`Ran 14 tests ... OK`)

2. `python3 -m unittest -v tests/datahub/test_akshare_a_share_minute_bars_live.py`
- Result: PASS with default live gate behavior (`Ran 5 tests ... OK (skipped=1)`)
- Default skip reason observed: `Live source tests are disabled. Set QUANT_SYSTEM_LIVE_TESTS=1 to enable.`

3. `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_minute_bars_live.py`
- Result: PASS (`Ran 5 tests ... OK`)
- Live smoke case `test_live_akshare_a_share_minute_bars_smoke` passed.

### Related regression commands from handoff

4. `python3 -m unittest tests/datahub/test_akshare_adapter.py`
- Result: PASS (`Ran 10 tests ... OK`)

5. `python3 -m unittest tests/datahub/test_akshare_a_share_daily_bar_adapter.py`
- Result: FAIL to run (module not found)
- Evidence: `ModuleNotFoundError: No module named 'tests/datahub/test_akshare_a_share_daily_bar_adapter'`
- Note: file does not exist in repository; nearest existing file is `tests/datahub/test_akshare_adapter.py` and was executed.

6. `python3 -m unittest tests/datahub/test_source.py`
- Result: PASS (`Ran 20 tests ... OK`)

7. `python3 -m unittest tests/datahub/test_datasets.py`
- Result: PASS (`Ran 31 tests ... OK`)

8. `python3 -m unittest tests/datahub/test_source_capabilities.py`
- Result: PASS (`Ran 14 tests ... OK`)

9. `python3 -m unittest tests/datahub/test_source_catalog.py`
- Result: PASS (`Ran 6 tests ... OK`)

### Full DataHub default suite

10. `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`
- Result: PASS (`Ran 779 tests ... OK (skipped=34)`)

## Default Network Behavior

- Default test execution remains offline-safe.
- New live smoke test is gated by `QUANT_SYSTEM_LIVE_TESTS=1` and skipped by default.
- Offline adapter tests use injected fetch functions/fixtures and do not require live network.

## Live-Enabled Result (Mandatory for real-source task)

- Live-enabled status: **PASS**
- Command: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_minute_bars_live.py`
- Evidence: `test_live_akshare_a_share_minute_bars_smoke ... ok`

## Handoff Compliance Notes

- Phase boundary respected: only `quant/datahub/**` and `tests/datahub/**` changed, plus this report file.
- No credential/cookie/token/private-account logic added.
- Adapter enforces bounded one-day slice and one-symbol scope; rejects broad/unbounded requests.

## Deviations from Handoff

- The suggested command `python3 -m unittest tests/datahub/test_akshare_a_share_daily_bar_adapter.py` could not run because that test module does not exist in the repository. All other required/suggested commands were executed.

## Risks / Follow-up

1. Current minute-bars coverage is intentionally narrow (`partial`): one symbol per request, one trade date per request.
2. Upstream AKShare minute routes have inherent recency/history limits (especially 1-minute data windows); broader trading-grade breadth/history coverage remains open follow-up work.
3. Future expansion likely needs batch symbol support, wider time-window handling, and stronger upstream fallback behavior while preserving hard-failure boundaries for signature/contract issues.
