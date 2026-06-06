# TASK-116 Report

## files changed
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_hk_valuation_snapshot_adapter.py`
- `tests/datahub/test_akshare_hk_valuation_snapshot_live.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`

## implementation summary
- Hardened `AkshareHKValuationSnapshotAdapter` from a one-symbol latest snapshot into caller-provided HK symbol batches with bounded dated history from `stock_hk_indicator_eniu`.
- Preserved `DatasetName.VALUATION_SNAPSHOT`, canonical `xxxxx.HK` symbols, `market="HK"`, deterministic sorting, and explicit invalid-symbol / invalid-range rejection.
- Default no-window fetch now returns the latest proven dated record per requested symbol; explicit `start_date` / `end_date` returns filtered dated history records.
- Added explicit `source_route` truth:
  - `stock_hk_indicator_eniu` for dated PE/PB/market-cap history
  - `stock_hk_indicator_eniu+stock_hk_valuation_baidu` only when same-date Baidu optional metrics (`ps_ttm`, `float_market_cap`, optional `dividend_yield`) are actually merged
- Stopped mixing undated `stock_hk_valuation_comparison_em` snapshot fields into dated history records.
- Tightened capability/catalog wording to match proven public-source truth instead of implying closure-grade HK valuation breadth.

## tests run
- `python3 -m unittest tests/datahub/test_akshare_hk_valuation_snapshot_adapter.py` -> PASS
- `python3 -m unittest tests/datahub/test_source_capabilities.py` -> PASS
- `python3 -m unittest tests/datahub/test_source_catalog.py` -> PASS
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_hk_valuation_snapshot_live.py` -> PASS (`live` smoke skipped by default)
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_valuation_snapshot_live.py` -> PASS

## default network behavior
- Default/offline tests remain network-safe.
- Adapter/unit tests use injected fixtures/stubs.
- `tests/datahub/test_akshare_hk_valuation_snapshot_live.py` remains gated by `QUANT_SYSTEM_LIVE_TESTS=1` and skips by default.

## live-enabled PASS/SKIP/FAIL result and root-cause evidence
- Result: PASS.
- Live-enabled smoke proved bounded multi-symbol dated history for `00700.HK` and `00005.HK` on `2022-07-13`.
- Direct adapter probe in this environment after the code change:
  - open-ended fetch for `("00700.HK", "00005.HK")` -> `2` normalized latest records, both with `trade_date=2022-07-13`, `source_route=stock_hk_indicator_eniu`
  - bounded history fetch for `00700.HK`, `2022-07-11..2022-07-13` -> `3` normalized dated records
  - bounded history fetch for `00700.HK`, `2000-01-01..today` -> `4009` normalized records, min/max `trade_date=2006-03-23..2022-07-13`
- Supporting route evidence gathered during execution:
  - `stock_hk_indicator_eniu(symbol="hk00700", indicator="市盈率")` returned a long dated series
  - `stock_hk_valuation_comparison_em(symbol="00700")` returned one undated comparison row only
  - `stock_hk_valuation_baidu(symbol="00700", indicator="市销率(TTM)", period="近一年")` failed here with `SSLCertVerificationError: certificate verify failed`

## capability truth changed
- `hk_valuation_history` remains `partial`; it was not promoted.
- Truth improved from vague “snapshot exists” wording to explicit bounded dated-history wording.

## source route coverage / metric taxonomy / date-window / continuity
- Proven required dated metrics:
  - `pe_ttm`
  - `pb`
  - `market_cap`
  - primary route: `stock_hk_indicator_eniu`
- Proven optional dated metrics when same-date Baidu rows are reachable:
  - `ps_ttm`
  - `float_market_cap`
  - optional `dividend_yield`
- Date-window behavior is post-normalization filtering on `trade_date`, with explicit `start_date > end_date` rejection.
- Deterministic ordering is by `symbol`, `trade_date`, `source_route`.
- History continuity evidence is improved but still bounded/stale: accepted live environment proved dated series through `2022-07-13`, not current-dated continuity.

## stronger public-source valuation-history outcome
- Implemented stronger public-source HK valuation-history coverage via caller-provided multi-symbol bounded dated Eniu history.
- Truthfully constrained what remains unproven:
  - current-dated HK valuation continuity
  - reliable Baidu availability in this environment
  - independent second-source redundancy for closure-grade HK valuation history
  - undated comparison rows as a valid history source

## deviations
- None.

## risks/follow-up
- `hk_valuation_history` still cannot be treated as trading-perfect because proven public history in this environment is stale through `2022-07-13`.
- `stock_hk_valuation_baidu` is optional only; current environment hit SSL certificate failure, so optional same-date supplementation is not yet dependable.
- `stock_hk_valuation_comparison_em` remains undated snapshot truth and should not be reused as dated history without a route exposing explicit dates.
