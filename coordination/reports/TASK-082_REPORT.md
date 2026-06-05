# TASK-082 Report

- files changed
  - `quant/datahub/adapters/akshare.py`
  - `quant/datahub/source_capabilities.py`
  - `tests/datahub/test_akshare_etf_daily_bar_adapter.py`
  - `tests/datahub/test_akshare_etf_daily_bar_live.py`
  - `tests/datahub/test_source_capabilities.py`

- implementation summary
  - Hardened `AkshareETFDailyBarAdapter` from one-symbol fetches to caller-provided multi-symbol bounded date-window batches.
  - Added ETF/fund symbol normalization and rejection for A-share-like, index-like, malformed, empty, and unsupported-prefix inputs.
  - Preserved primary `fund_etf_hist_em` route with `fund_etf_hist_sina` fallback, then enforced deterministic filtering, de-duplication, and sorted output by symbol then trade date.
  - Added clear failure when any requested symbol yields no usable rows, preventing partial batch success.

- tests run
  - `python3 -m unittest tests/datahub/test_akshare_etf_daily_bar_adapter.py`
  - `python3 -m unittest tests/datahub/test_source_capabilities.py`
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_etf_daily_bar_live.py`
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_etf_daily_bar_live.py`

- default network behavior
  - Offline-safe when `QUANT_SYSTEM_LIVE_TESTS` is unset: the live smoke test skips before any source call.
  - Evidence: `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_etf_daily_bar_live.py` -> `OK (skipped=1)`.

- live-enabled result
  - PASS.
  - Evidence: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_etf_daily_bar_live.py` -> `Ran 1 test ... OK`.
  - The live smoke now requests `510300.ETF_CN` and `159915.ETF_CN`, validates `DatasetName.DAILY_BARS`, and asserts both symbols are present in normalized output.

- fund_daily_bars capability truth
  - Status remains `partial`.
  - Updated wording only: capability metadata now reflects proven multi-symbol bounded date-window ETF daily-bar access while keeping broader breadth/history gaps explicit.

- source route coverage and known limitations
  - Proven public routes: primary `fund_etf_hist_em`; bounded fallback `fund_etf_hist_sina`.
  - Proven scope: caller-provided exchange ETF/fund codes with supported exchange-style prefixes (`5`/`1`), bounded date windows, deterministic normalized `DAILY_BARS` output.
  - Remaining limitations: broader fund breadth, longer history continuity, and non-ETF public-route coverage are still unproven; no full-market collection was added.

- deviations
  - The shell environment had `QUANT_SYSTEM_LIVE_TESTS=1` preset, so the handoff's default live-file command would not demonstrate skip behavior in this session.
  - To verify true default offline behavior, I added the explicit `env -u QUANT_SYSTEM_LIVE_TESTS ...` run above. No code or scope deviation beyond that.

- risks/follow-up
  - ETF/fund symbol acceptance is intentionally conservative to exchange ETF-style prefixes proven by current public routes; broader listed-fund code families need separate validation before expansion.
  - `fund_daily_bars` should not be promoted to `covered` until broader public-source breadth and longer-history continuity are demonstrated with additional live evidence.
