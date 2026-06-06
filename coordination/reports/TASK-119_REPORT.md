# TASK-119 Report

- files changed
  - `quant/datahub/adapters/akshare.py`
  - `quant/datahub/source_capabilities.py`
  - `quant/datahub/source_catalog.py`
  - `tests/datahub/test_akshare_etf_daily_bar_adapter.py`
  - `tests/datahub/test_source_capabilities.py`
  - `tests/datahub/test_source_catalog.py`

- implementation summary
  - Applied the minimal conservative fix for the Review blocker.
  - `AkshareETFDailyBarAdapter` no longer accepts all `16` / `18` / `150` / `501` listed-fund prefixes for daily bars.
  - `FUND_CN` daily-bar support is now limited to the explicitly proven listed-fund symbol `161725.FUND_CN`; exchange ETF support such as `510300.ETF_CN` and `159915.ETF_CN` is unchanged.
  - Capability and catalog wording now describe the exact proven listed-fund path instead of implying broader listed-fund family coverage.

- exact Review finding addressed
  - Fixed the truthfulness issue where the adapter accepted unproven listed-fund prefix families even though evidence/tests only covered `161725.FUND_CN`.
  - Added regression coverage that explicitly rejects representative unproven families: `160706.FUND_CN`, `180012.FUND_CN`, `150001.FUND_CN`, `501018.FUND_CN`.

- supported ETF/fund daily-bar symbol families after rework
  - Supported ETF side: previously accepted listed ETF families remain supported (`51` / `56` / `58` / `159`).
  - Supported listed-fund side: only `161725.FUND_CN` is accepted as the proven LOF/listed-fund daily-bar path.
  - Unsupported listed-fund breadth: other `16` / `18` / `150` / `501` codes now fail clearly with an error that points back to the only explicitly proven listed-fund code.

- route/source evidence for accepted listed-fund support or unsupported-family behavior
  - Accepted listed-fund path:
    - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_etf_daily_bar_live.py` -> PASS with `161725.FUND_CN` present in normalized output.
    - Direct adapter probe: `161725.FUND_CN` over `2024-01-02..2024-01-10` -> PASS, `record_count=7`, first record `2024-01-02`, `close=0.921`.
    - Direct route probe in this environment:
      - `fund_lof_hist_em(symbol='161725', ...)` -> `FAIL ConnectionError(RemoteDisconnected(...))`
      - `fund_etf_hist_sina(symbol='sz161725')` -> `PASS rows=1303`, first row date `2021-01-15`
  - Unsupported-family behavior:
    - Offline regression test now proves representative non-`161725` listed-fund families are rejected before any live fetch.

- tests run
  - `python3 -m unittest tests/datahub/test_akshare_etf_daily_bar_adapter.py` -> PASS
  - `python3 -m unittest tests/datahub/test_source_capabilities.py` -> PASS
  - `python3 -m unittest tests/datahub/test_source_catalog.py` -> PASS
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_etf_daily_bar_live.py` -> PASS (`OK`, `skipped=1`)
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_etf_daily_bar_live.py` -> PASS

- default network behavior
  - Default unit tests remain offline-safe.
  - `tests/datahub/test_akshare_etf_daily_bar_live.py` still skips before any source call unless `QUANT_SYSTEM_LIVE_TESTS=1` is explicitly set.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence for real-source tasks
  - Result: PASS
  - Root-cause evidence recorded for route behavior:
    - Primary LOF route `fund_lof_hist_em` was unavailable in this environment due to `ConnectionError` / `RemoteDisconnected`.
    - Bounded fallback `fund_etf_hist_sina` returned source-backed history for `sz161725`.
    - The gated live smoke still passed because the adapter classified the primary-route failure as route unavailability and returned schema-valid daily bars through the fallback.

- whether `fund_daily_bars` capability truth changed
  - Status remains `partial`.
  - Truth wording became narrower and more precise: bounded exchange ETF coverage plus the single proven listed-fund path `161725.FUND_CN`; no broader listed-fund family claim remains.

- confirmation that exchange ETF compatibility was preserved
  - Preserved. Existing ETF behavior and live smoke coverage for `510300.ETF_CN` remain intact.

- deviations
  - None.

- risks/follow-up
  - `fund_daily_bars` must not be widened again from prefix shape alone; each additional listed-fund family needs explicit route evidence plus regression coverage.
  - Broader listed-fund breadth, off-exchange fund daily bars, longer history continuity, and stronger independent public-route redundancy remain unresolved.
