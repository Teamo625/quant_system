# TASK-139 Report

## files changed

- `quant/features/technical.py`
- `quant/features/__init__.py`
- `quant/features/personal_readiness.py`
- `tests/features/test_technical.py`
- `tests/features/test_personal_readiness.py`
- `coordination/reports/TASK-139_REPORT.md`

## implemented technical indicator families

- Preserved existing TASK-060 behavior for normalized daily bars, close-to-close return, SMA, realized volatility, duplicate-date rejection, mixed symbol/market rejection, and non-positive close rejection.
- Extended `DailyBarInput` conservatively with optional `open/high/low/volume/turnover` fields while keeping close-only callers valid.
- Added shared rolling/window semantics through existing positive-window validation plus reusable trailing-row and EMA-series helpers.
- Added EMA-family primitive: `calculate_exponential_moving_average`, with SMA seed over the first valid window of the provided series.
- Added momentum oscillators:
  - `calculate_macd` returning `MacdValue(macd_line, signal_line, histogram)`
  - `calculate_relative_strength_index`
  - `calculate_stochastic_oscillator` returning `StochasticOscillatorValue(percent_k, percent_d, percent_j)`
- Added bands/range primitives:
  - `calculate_bollinger_bands` returning `BollingerBandsValue(middle_band, upper_band, lower_band, bandwidth)`
  - `calculate_average_true_range`
- Added volume/turnover/liquidity primitives:
  - `calculate_average_volume`
  - `calculate_average_turnover`
  - `calculate_amihud_illiquidity`
- Added gap/breakout primitives:
  - `calculate_gap_return`
  - `calculate_breakout_ratio`
- Added conservative scalar `FeatureValueRecord` builders for EMA, RSI, and ATR.
- Intentionally deferred broad multi-indicator record emission. Multi-output families stay as typed calculation results because metric-level identity remains a later contract task.

## readiness gate changes

- Updated `price_volume_technical_core` from `warn` to `pass`.
- Updated the readiness snapshot to reflect the implemented technical families and expanded offline regression evidence.
- Remaining groups stay conservative:
  - `valuation_features`: `warn`
  - `capital_flow_money_flow_features`: `warn`
  - `sector_market_relative_features`: `warn`
  - `batch_calculation_apis`: `warn`
  - `persistence_and_downstream_consumability`: `warn`
  - `offline_test_coverage`: `warn`
- New readiness summary:
  - `pass=1`
  - `warn=6`
  - `blocked=0`
  - `fail=0`
  - `phase_closure_ready=false`
- Recommended next batch now moves to `featurehub_valuation_flow_batch_01`.

## tests run

- `python3 -m unittest tests.features.test_technical`
  - PASS
  - `Ran 25 tests in 0.002s`
- `python3 -m unittest tests.features.test_personal_readiness`
  - PASS
  - `Ran 4 tests in 0.000s`
- `python3 -m unittest discover -s tests/features -p 'test_*.py'`
  - PASS
  - `Ran 65 tests in 0.007s`

## default network behavior

- Offline-safe only.
- All added technical calculations are pure functions over caller-provided inputs.
- No live data fetches, DataHub adapter calls, credentials, browser/session state, or hidden network behavior were added.

## live-enabled PASS/SKIP/FAIL result and root-cause evidence for real-source tasks

- `SKIP`
- TASK-139 is pure offline FeatureHub work.
- The handoff forbids live tests, and this execution added no live-capable path.

## deviations

- None.

## risks/follow-up

- Multi-indicator families now calculate correctly offline, but durable downstream persistence still lacks metric-level identity inside shared `PRICE_TECHNICAL` records. That remains `FH-CONTRACT-001`.
- Batch multi-symbol/multi-feature orchestration is still absent. That remains `FH-BATCH-001`.
- Valuation, flow, and sector/market-relative FeatureHub groups remain incomplete and should stay in Phase 3-P follow-up dispatch order.
