# TASK-078 Report

## files changed
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/source_capabilities.py`
- `tests/datahub/test_akshare_a_share_minute_bars_adapter.py`
- `tests/datahub/test_akshare_a_share_minute_bars_live.py`
- `tests/datahub/test_source_capabilities.py`

## tests run
- `python3 -m unittest tests/datahub/test_akshare_a_share_minute_bars_adapter.py` -> PASS (`Ran 17 tests`)
- `python3 -m unittest tests/datahub/test_source_capabilities.py` -> PASS (`Ran 23 tests`)
- `python3 -m unittest -v tests/datahub/test_akshare_a_share_minute_bars_live.py` -> PASS (`Ran 5 tests`; live smoke skipped by default)
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_minute_bars_live.py` -> PASS (`Ran 5 tests`)

## default network behavior
- Default adapter tests stay offline-safe by injecting fake AKShare fetch callables.
- The live smoke file still skips the real-source smoke unless `QUANT_SYSTEM_LIVE_TESTS=1` is set.
- No default test path introduced implicit network access.

## live-enabled PASS/SKIP/FAIL result and root-cause evidence
- Result: PASS
- Command: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_minute_bars_live.py`
- Evidence: unittest completed `Ran 5 tests ... OK`.
- Additional sample probe after implementation succeeded on `2026-06-04` for `600000.SH` and `000001.SZ` with `476` normalized minute-bar records; first bar `2026-06-04T09:31:00`, last bar `2026-06-04T15:00:00`.

## capability truth changed
- `a_share_minute_bars` remains `partial`.
- Gap text now reflects validated caller-provided multi-symbol bounded date-window access while keeping broader intraday history continuity and breadth incomplete.

## source route coverage, date-window behavior, known intraday-history limitations
- Primary route: `stock_zh_a_hist_min_em`
- Behavior: validates the full symbol batch first, then fetches each valid A-share symbol with bounded `start_date 09:30:00` to `end_date 15:00:00`.
- Fallback route: `stock_zh_a_minute`
- Fallback behavior: still latest/recent-oriented; adapter filters rows locally by normalized `bar_time` to the requested bounded window.
- Batch normalization remains compatible with `DatasetName.MINUTE_BARS`, deduplicates by `(symbol, bar_time, minute_period, source)`, and sorts deterministically by symbol and `bar_time`.
- Known limitation: public-source proof is still bounded recent intraday coverage, not full historical continuity or full trading-grade breadth across all A-share minute-bar use cases.

## deviations
- None.

## risks/follow-up
- No extra hard cap was added beyond requiring explicit bounded `start_date` and `end_date`; large caller-provided windows could still increase runtime or upstream load.
- The fallback route remains dependent on recent/latest public availability and can legitimately return no rows for older windows even when the request is syntactically valid.
- `a_share_minute_bars` should not be promoted beyond `partial` without broader live evidence on history continuity, stability, and source breadth.
