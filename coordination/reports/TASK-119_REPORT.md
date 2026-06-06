# TASK-119 Report

- files changed
  - `quant/datahub/adapters/akshare.py`
  - `quant/datahub/source_capabilities.py`
  - `quant/datahub/source_catalog.py`
  - `tests/datahub/test_akshare_etf_daily_bar_adapter.py`
  - `tests/datahub/test_akshare_etf_daily_bar_live.py`
  - `tests/datahub/test_source_capabilities.py`
  - `tests/datahub/test_source_catalog.py`

- implementation summary
  - Hardened `AkshareETFDailyBarAdapter` from exchange ETF-only semantics into bounded listed ETF plus listed fund/LOF daily-bar support under the existing `DatasetName.DAILY_BARS` contract.
  - Preserved accepted ETF compatibility for `510300.ETF_CN` / `159915.ETF_CN`.
  - Added symbol-family normalization that now distinguishes `ETF_CN` vs `FUND_CN`, keeps bare ETF codes like `510300` normalized to `ETF_CN`, and normalizes proven listed-fund families like `161725` to `FUND_CN`.
  - Added market-aware primary route selection: `fund_etf_hist_em` for ETF-like codes, `fund_lof_hist_em` for listed-fund/LOF codes, both with bounded `fund_etf_hist_sina` fallback and unchanged deterministic date filtering / duplicate handling.
  - Tightened truthfulness for mismatched suffixes and unsupported non-listed fund families instead of silently labeling non-ETF listed funds as `ETF_CN`.
  - Kept `fund_daily_bars` capability status at `partial`; updated capability/catalog wording to reflect only proven exchange ETF plus listed fund/LOF coverage and to keep off-exchange funds / longer continuity gaps explicit.

- ETF/fund daily-bar route/source-family investigation result
  - Investigated local AKShare route families: `fund_etf_hist_em`, `fund_lof_hist_em`, and `fund_etf_hist_sina`.
  - In the current environment, direct probes showed:
    - `fund_etf_hist_em(symbol='510300', ...)` -> `ConnectionError` with `RemoteDisconnected`
    - `fund_lof_hist_em(symbol='161725', ...)` -> `ConnectionError` with `RemoteDisconnected`
    - `fund_etf_hist_sina(symbol='sh510300')` -> PASS, `rows=3407`, first date `2012-05-28`
    - `fund_etf_hist_sina(symbol='sz161725')` -> PASS, `rows=1303`, first date `2021-01-15`
  - Conclusion: the current live-proof path in this environment is stable bounded Sina fallback history for both an ETF and a listed fund/LOF, while Eastmoney primary routes remain intermittently unavailable and are treated as route unavailability rather than contract success.

- supported symbol classes, granularity, identity, deduplication behavior, and known limitations
  - Proven ETF classes: exchange-listed ETF families normalized to `.ETF_CN`, with tested examples `510300.ETF_CN` and `159915.ETF_CN`.
  - Proven listed-fund classes in this task: listed fund / LOF families normalized to `.FUND_CN`, with tested/live example `161725.FUND_CN`.
  - Granularity remains symbol x trading-day OHLCV under `DatasetName.DAILY_BARS`.
  - Identity remains deterministic by `(symbol, trade_date, source, price_adjustment)`; the adapter still fetches one successful route per symbol and does not merge conflicting route-distinct rows.
  - Known limitations: no off-exchange open-ended fund daily bars, no full public listed-fund taxonomy, no promotion to `covered`, and no proof yet of stronger independent public-route redundancy beyond the Sina fallback used in the accepted live environment.

- whether `fund_daily_bars` capability truth changed
  - Status remains `partial`.
  - Truth changed from “bounded exchange ETF daily-bar access” to “bounded exchange ETF plus listed fund/LOF daily-bar access within the AKShare public family,” while keeping off-exchange funds, longer history continuity, and broader redundancy gaps explicit.

- confirmation of preserved exchange ETF compatibility
  - Preserved. Offline and live validation still cover `510300.ETF_CN`; the accepted ETF daily-bar request shape, schema, sorting, and fallback behavior remain intact.

- tests run
  - `python3 -m unittest tests/datahub/test_akshare_etf_daily_bar_adapter.py` -> PASS
  - `python3 -m unittest tests/datahub/test_source_capabilities.py` -> PASS
  - `python3 -m unittest tests/datahub/test_source_catalog.py` -> PASS
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_etf_daily_bar_live.py` -> PASS (`OK`, `skipped=1`)
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_etf_daily_bar_live.py` -> PASS

- default network behavior
  - Default adapter/unit tests remain offline-safe and use injected fixtures only.
  - `tests/datahub/test_akshare_etf_daily_bar_live.py` remains explicitly gated by `QUANT_SYSTEM_LIVE_TESTS`; with the variable unset it skips before any source call.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence
  - Result: PASS
  - Command: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_etf_daily_bar_live.py`
  - Evidence:
    - The live smoke passed for `510300.ETF_CN` and `161725.FUND_CN`.
    - A direct adapter fetch over `2024-01-02` to `2024-01-10` returned `record_count=14`.
    - Sample normalized records included `161725.FUND_CN FUND_CN 2024-01-02 0.921`.
    - Direct route probes in the same environment reproduced `RemoteDisconnected` on `fund_etf_hist_em` and `fund_lof_hist_em`, while `fund_etf_hist_sina` returned bounded history for both tested symbols; the adapter correctly classified those primary-route failures as route unavailability and succeeded through the bounded fallback.

- deviations
  - No scope deviations.
  - Added direct route-investigation commands beyond the required unittest commands so the report can record concrete EM-vs-Sina evidence for the newly broadened listed-fund path.

- risks/follow-up
  - Bare-code inference remains intentionally conservative to proven listed ETF families and proven listed-fund families; broader listed-fund taxonomy should not be inferred without more route evidence.
  - The accepted live environment still depends on `fund_etf_hist_sina` fallback because both Eastmoney primary daily-history routes were locally reproduced as unavailable.
  - `fund_daily_bars` should not be promoted beyond `partial` until broader listed-fund breadth, off-exchange fund truth, longer continuity, and stronger independent public-route redundancy are proven.
