# TASK-135 Report

## files changed
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_hk_minute_bars_adapter.py`
- `tests/datahub/test_akshare_hk_minute_bars_live.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`
- `tests/datahub/test_personal_readiness.py`
- `tests/datahub/test_quality.py`

## selected readiness batch / follow-up
- batch id reviewed from handoff: `hong_kong__owner_waiver_required__hong_kong_hong_kong_capability_readiness_hk_minute_bars__batch_01`
- included follow-up id reviewed from handoff: `hong_kong__hong_kong_capability_readiness__hk_minute_bars`

## HK minute-bar feasibility result
- Feasible public no-credential route confirmed.
- Local investigation verified installed `akshare` exposes `stock_hk_hist_min_em(symbol, period, adjust, start_date, end_date)`.
- Live probes returned bounded HK intraday OHLCV rows for stock samples `00700`, `00941`, and `00005`.
- Existing `DatasetName.MINUTE_BARS` contract is sufficient for proven HK source facts; no HK-only schema change was needed.

## implementation summary
- Added `AkshareHKMinuteBarsAdapter` with bounded `start_date`/`end_date` enforcement and multi-symbol caller batches.
- Reused `DatasetName.MINUTE_BARS`; emitted normalized `trade_date`, `bar_time`, OHLCV, optional `amount`, `source`, `ingested_at`, `schema_version`.
- Added stock-only validation through `stock_hk_security_profile_em` before fetching minute bars.
- Accepted HK symbol formats are canonical `00700.HK` or raw 5-digit codes; malformed/non-HK inputs fail clearly.
- Kept 1-minute history conservative: requests outside a recent trailing window fail up front because `stock_hk_hist_min_em` only proves recent 1-minute history.
- Added focused offline tests and gated live smoke coverage; no default hidden live network path was introduced.

## capability / catalog / readiness truth changes
- `hk_minute_bars` changed from `MISSING` with no dataset mapping to `PARTIAL` mapped to `DatasetName.MINUTE_BARS`.
- `quant/datahub/source_capabilities.py` now records proven `stock_hk_hist_min_em` stock-only public coverage plus remaining limits: no independent second public route, no proven non-stock HK instrument coverage, no full long-history continuity.
- `quant/datahub/source_catalog.py` now links `DatasetName.MINUTE_BARS` into `HK_STOCK_FULL_DATA` stable datasets and records HK minute-bar route truth in AKShare family notes.
- `build_default_personal_trading_readiness_report()` no longer emits the former `owner_waiver_required` HK minute-bars follow-up/batch because the capability is no longer optional+missing; no `personal_readiness.py` code change was needed.

## tests run
- `python3 -m unittest tests.datahub.test_source_capabilities` -> PASS (`Ran 47 tests`)
- `python3 -m unittest tests.datahub.test_source_catalog` -> PASS (`Ran 11 tests`)
- `python3 -m unittest tests.datahub.test_personal_readiness` -> PASS (`Ran 9 tests`)
- `python3 -m unittest tests.datahub.test_akshare_hk_minute_bars_adapter` -> PASS (`Ran 8 tests`)
- `python3 -m unittest -v tests.datahub.test_akshare_hk_minute_bars_live` -> PASS (`Ran 4 tests`; ambient shell executed live smoke)
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_hk_minute_bars_live` -> PASS (`Ran 4 tests`, `skipped=1`)
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_hk_minute_bars_live` -> PASS (`Ran 4 tests`)
- `python3 -m unittest tests.datahub.test_quality` -> PASS (`Ran 10 tests`)

## default network behavior
- Default offline tests remain network-safe.
- The HK minute-bar live smoke is still gated by `QUANT_SYSTEM_LIVE_TESTS=1`.
- `env -u QUANT_SYSTEM_LIVE_TESTS ... test_akshare_hk_minute_bars_live` proved the real-source smoke skips by default.
- Offline adapter tests use injected fetch callables and do not require live network.

## live-enabled PASS/SKIP/FAIL result and root-cause evidence
- Result: `PASS`
- Command: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_hk_minute_bars_live`
- Evidence: unittest completed `Ran 4 tests ... OK`.
- Additional live probe with `AkshareHKMinuteBarsAdapter(minute_period="5")` returned `528` normalized records for `00700.HK` and `00005.HK` across trade dates `2026-06-08` to `2026-06-11`.
- Probe evidence:
  - first bar: `00005.HK 2026-06-08T09:35:00 open=140.8 close=139.8 amount=167281640.0`
  - last bar: `00700.HK 2026-06-11T16:00:00 open=455.6 close=457.2 amount=1226858404.0`

## deviations
- None.

## risks / follow-up
- HK minute-bars proof is stock-only because validation depends on `stock_hk_security_profile_em`; non-stock ETF/fund/index HK instrument coverage is still unproven and intentionally unsupported in this adapter slice.
- 1-minute history remains a recent trailing-window slice; broader long-history intraday continuity is still unproven.
- No independent second no-credential public HK minute-bar route is proven.
- Because current readiness logic only queues optional capabilities when they are `missing`, this capability now disappears from the follow-up queue after moving to `partial`; Controller should decide whether remaining optional-partial gaps need separate future tracking.
