# TASK-088 Report

## files changed
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/source_capabilities.py`
- `tests/datahub/test_akshare_index_adapter.py`
- `tests/datahub/test_akshare_index_live.py`
- `tests/datahub/test_source_capabilities.py`

## tests run
- `python3 -m unittest tests/datahub/test_akshare_index_adapter.py` -> PASS
- `python3 -m unittest tests/datahub/test_source_capabilities.py` -> PASS
- `python3 -m unittest tests/datahub/test_source_catalog.py` -> PASS
- `python3 -m unittest -v tests/datahub/test_akshare_index_live.py` -> PASS in current shell
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_index_live.py` -> PASS, live smoke SKIP by default
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_index_live.py` -> PASS

## default network behavior
- Default code path remains offline-safe when `QUANT_SYSTEM_LIVE_TESTS` is unset: the live smoke test is skipped and only classifier unit tests run.
- This shell had `QUANT_SYSTEM_LIVE_TESTS=1` preset, so the bare default command executed live smoke here; the explicit `env -u` rerun confirmed default skip behavior still works.

## live-enabled PASS/SKIP/FAIL result and root-cause evidence
- Result: PASS
- Command: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_index_live.py`
- Evidence:
  - test suite passed with no failures
  - direct readback script returned `record_count=8`
  - returned symbols: `000300.CN_INDEX`, `399001.CN_INDEX`
  - per-symbol bounded coverage in requested window:
    - `000300.CN_INDEX`: 4 rows from `2024-01-02` to `2024-01-05`
    - `399001.CN_INDEX`: 4 rows from `2024-01-02` to `2024-01-05`
- No network/proxy/DNS/TLS/upstream rework was required for this run.

## capability truth changed?
- `index_daily_bars` status did not change.
- It remains `partial`.
- Gap text was refined to reflect proven caller-provided multi-index bounded benchmark access while keeping broader benchmark breadth/history/global coverage conservative.

## source route coverage and known limitations
- Hardened `AkshareIndexDailyBarAdapter` from one-index slice to caller-provided multi-index bounded daily-bar access.
- Supported local symbol forms now include canonical `.CN_INDEX`, bare codes, and supported source-native forms for the bounded core map:
  - `000300` / `sh000300`
  - `000001` / `sh000001`
  - `399001` / `sz399001`
  - `399006` / `sz399006`
- The adapter now:
  - requires both `start_date` and `end_date`
  - filters locally if upstream returns wider history
  - deduplicates deterministically by `(index_code, trade_date, source)`
  - sorts by `index_code` then `trade_date`
  - validates normalized records against `DatasetName.INDEX_DAILY_BARS`
  - fails the whole batch if any requested symbol is invalid or yields no usable bounded rows
  - classifies route-unavailable conditions narrowly for network/proxy/DNS/TLS/public-source outages
- Known limitations:
  - bounded benchmark map is still limited to the core mainland index symbols above
  - broader China benchmark breadth is not yet implemented
  - HK/global benchmark daily-bar coverage is still incomplete
  - no index constituent, weight-history, or rebalance metadata changes were made

## deviations
- None.

## risks/follow-up
- Current public AKShare proof is limited to core mainland benchmarks; expanding to wider China benchmark families still needs explicit hardening and live proof.
- `index_china_hk_global_benchmarks` remains incomplete and should be handled separately from this bounded mainland slice.
- If a future AKShare release changes index route argument names/signatures, the adapter now fails hard with route-qualified errors; that is intentional and should be reviewed rather than skipped.
