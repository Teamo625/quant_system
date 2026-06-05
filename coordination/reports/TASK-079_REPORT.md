# TASK-079 Report

## files changed
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/source_capabilities.py`
- `tests/datahub/test_akshare_hk_adapter.py`
- `tests/datahub/test_akshare_hk_live.py`
- `tests/datahub/test_source_capabilities.py`
- `coordination/reports/TASK-079_REPORT.md`

## tests run
- `python3 -m unittest tests/datahub/test_akshare_hk_adapter.py` -> PASS
- `python3 -m unittest tests/datahub/test_akshare_hk_instrument_master_adapter.py` -> PASS
- `python3 -m unittest tests/datahub/test_source_capabilities.py` -> PASS
- `python3 -m unittest -v tests/datahub/test_akshare_hk_live.py` -> PASS in this shell because `QUANT_SYSTEM_LIVE_TESTS=1` was already preset externally
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_hk_live.py` -> PASS, `skipped=1`
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_live.py` -> PASS

## default network behavior
- Default offline/unit suites above remain network-safe; tests use injected fakes and explicit socket blocking where applicable.
- The HK live test file is still env-gated and skips when `QUANT_SYSTEM_LIVE_TESTS` is unset.
- Note: the parent shell for this execution had `QUANT_SYSTEM_LIVE_TESTS=1` preset, so the exact default live-file command executed live here; skip-by-default behavior was verified separately by unsetting the variable.

## live-enabled PASS/SKIP/FAIL result and root-cause evidence
- Result: PASS
- Command: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_live.py`
- Smoke scope: `DatasetName.DAILY_BARS`, symbols `00700.HK` and `00005.HK`, bounded window `2024-01-02` to `2024-01-10`
- Evidence:
- `fetch_source_result(...)` succeeded through the real adapter with `record_count=14`
- Returned symbol counts: `00005.HK=7`, `00700.HK=7`
- Sorted bounded sample range observed: first `00005.HK 2024-01-02`, last `00700.HK 2024-01-10`
- First normalized record validated cleanly against `DatasetRegistry.validate_record(DatasetName.DAILY_BARS, ...)`

## capability truth change
- `hk_daily_bars`: status remains `partial`; gap text updated to reflect proven caller-provided multi-symbol bounded date-window access plus bounded fallback filtering, while keeping broader history/redundancy gaps conservative.
- `hk_universe_reference`: unchanged.

## source route/date-window/fallback/limitations
- `AkshareHKDailyBarAdapter` now accepts caller-provided HK stock symbol batches through `SourceRequest.symbols`.
- Full symbol batch is validated before any source call; invalid HK inputs fail early and do not produce partial successful batches.
- Canonical accepted format remains `00700.HK`-style only for this adapter; malformed, missing-suffix, wrong-market, and non-5-digit symbols are rejected clearly.
- Primary route remains `stock_hk_hist(symbol, period, start_date, end_date, adjust)`.
- Fallback route remains `stock_hk_daily(symbol, adjust)`.
- Only network/proxy/DNS/TLS/upstream-style failures on `stock_hk_hist` trigger fallback; route/signature/argument errors still surface as hard failures.
- If both routes are network-unavailable, the adapter now raises a bounded `RuntimeError` with attempted route evidence.
- Because `stock_hk_daily` does not take date parameters, fallback rows are locally filtered by normalized `trade_date`.
- Output is deterministically deduped by `(symbol, trade_date, source, price_adjustment)` and sorted by symbol then `trade_date`.
- Capability remains `partial` because broader HK history continuity and public-source redundancy are still unproven.

## deviations
- No scope deviations.
- No instrument-master code change was required; existing HK instrument reference behavior/tests were left intact.

## risks/follow-up
- `stock_hk_daily` fallback still depends on local post-filtering rather than source-side date bounding.
- Public AKShare HK coverage remains single-source-family dependent; resilience is improved but not yet redundant across independent public routes.
- `hk_universe_reference` is still narrow-slice validated and remains a future hardening target if broader HK symbol coverage becomes necessary.
