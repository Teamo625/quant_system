# TASK-118 Report

## files changed
- `quant/datahub/datasets.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `quant/datahub/adapters/akshare.py`
- `tests/datahub/test_datasets.py`
- `tests/datahub/test_source_catalog.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_akshare_hk_adapter.py`
- `tests/datahub/test_akshare_hk_live.py`
- `coordination/reports/TASK-118_REPORT.md`

## implementation summary
- Reused `DatasetName.TURNOVER_LIQUIDITY_SNAPSHOT` as the explicit HK turnover/liquidity source-fact surface instead of leaving HK semantics implicit under `DatasetName.DAILY_BARS`.
- Relaxed the contract truthfully: `turnover_rate` is now optional because accepted HK public routes expose dated `volume` and `amount`, but do not prove turnover-rate/floats/spread facts.
- Extended `AkshareHKDailyBarAdapter` to support both `DAILY_BARS` and `TURNOVER_LIQUIDITY_SNAPSHOT`, preserving existing HK daily-bar normalization while emitting explicit HK liquidity records with `source_route=stock_hk_hist` or `stock_hk_daily`.
- Updated capability/catalog wording so `hk_turnover_liquidity` now maps to the dedicated contract and stays conservative at `partial`.

## tests run
- `python3 -m unittest tests/datahub/test_datasets.py` -> PASS (`Ran 44 tests`)
- `python3 -m unittest tests/datahub/test_source_catalog.py` -> PASS (`Ran 9 tests`)
- `python3 -m unittest tests/datahub/test_source_capabilities.py` -> PASS (`Ran 42 tests`)
- `python3 -m unittest tests/datahub/test_akshare_hk_adapter.py` -> PASS (`Ran 22 tests`)
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_hk_live.py` -> PASS default-skip (`Ran 4 tests`, `skipped=4`)
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_live.py` -> PASS (`Ran 4 tests`)

## default network behavior
- Default/offline tests remain network-safe.
- `tests/datahub/test_akshare_hk_live.py` stays explicitly gated by `QUANT_SYSTEM_LIVE_TESTS=1`.
- No default test performs real network access.

## live-enabled PASS/SKIP/FAIL result and root-cause evidence
- Result: PASS.
- Command: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_live.py`
- Verified turnover/liquidity smoke scope: `DatasetName.TURNOVER_LIQUIDITY_SNAPSHOT`, symbols `00700.HK` and `00005.HK`, bounded window `2019-01-02` to `2019-01-15`.
- Live result detail in this environment:
  - direct `stock_hk_hist("00700")` -> `ConnectionError(ProtocolError(... RemoteDisconnected ...))`
  - direct `stock_hk_hist("00005")` -> same `ConnectionError/RemoteDisconnected`
  - adapter fallback `stock_hk_daily("00700")` returned `5403` rows; bounded rows `10`
  - adapter fallback `stock_hk_daily("00005")` returned `6904` rows; bounded rows `10`
  - normalized turnover/liquidity result `record_count=20`, symbols `['00005.HK', '00700.HK']`, source routes `['stock_hk_daily']`
- Interpretation: current PASS proves the explicit HK turnover/liquidity contract and fallback route provenance work against real public data in this environment; it does not prove primary `stock_hk_hist` availability.

## HK turnover/liquidity contract/profile
- Dataset: `DatasetName.TURNOVER_LIQUIDITY_SNAPSHOT`
- Granularity: `daily`
- Identity: `symbol + trade_date + source + source_route + metric_granularity`
- Required source-backed HK fields now proven here:
  - `symbol`
  - `market="HK"`
  - `trade_date`
  - `metric_granularity="daily"`
  - `volume`
  - `amount`
  - `source`
  - `source_route`
  - `ingested_at`
  - `schema_version`
- Optional/not proven on HK public routes:
  - `turnover_rate`
  - float-share / float-market-value fields
  - spread / bid-ask / VWAP / other microstructure facts

## route/source-family investigation result
- Proven HK turnover/liquidity source facts currently come from the same AKShare HK daily-bar family:
  - primary bounded route: `stock_hk_hist`
  - fallback full-history route with local date filtering: `stock_hk_daily`
- No independent second no-credential public HK turnover/liquidity source was implemented or validated in this handoff.

## capability truth change
- `hk_turnover_liquidity` remains `partial`.
- Dataset mapping changed from implicit `DatasetName.DAILY_BARS` reliance to explicit `DatasetName.TURNOVER_LIQUIDITY_SNAPSHOT`.
- Gap wording now states only dated `volume` and `amount` are source-proven on HK public routes.

## HK daily-bar compatibility
- Preserved.
- `DatasetName.DAILY_BARS` HK behavior, batching, bounded filtering, fallback handling, symbol validation, sorting, and live smoke all remain intact.

## deviations
- None.

## risks/follow-up
- Primary `stock_hk_hist` remained unavailable in this environment; accepted PASS relied on real `stock_hk_daily` fallback.
- HK turnover/liquidity remains same-family only; independent public-source redundancy is still unproven.
- Public HK turnover-rate and deeper liquidity/microstructure facts remain unvalidated and must not be inferred from this task.
