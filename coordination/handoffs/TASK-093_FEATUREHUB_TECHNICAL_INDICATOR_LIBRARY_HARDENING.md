# TASK-093 FeatureHub Technical Indicator Library Hardening

## Role

5.3 Execution Window.

## Context

Phase 3 FeatureHub Trading-Usable Hardening is reopened after Phase 2.5 DataHub no-paid-credential hardening closed. Existing FeatureHub work provides foundation contracts, a narrow technical primitive slice, valuation primitives, capital-flow primitives, and output persistence/versioning. Under `coordination/ROADMAP.md`, FeatureHub remains trading-usable incomplete until it provides a broader scanner/strategy-ready feature library over validated DataHub-shaped inputs.

This task is the first Phase 3 expansion handoff. It is offline-only and must not perform DataHub source work, Scanner work, strategy/backtest work, or live network access.

## Objective

Expand the offline price/volume technical indicator library in `quant/features/technical.py` beyond the current close-to-close return, SMA, and realized-volatility foundation slice.

The implementation should support a practical core set suitable for downstream Scanner and StrategyLab use over caller-provided daily-bar-like rows:

- EMA
- MACD
- RSI
- KDJ/stochastic-style oscillator
- Bollinger Bands
- ATR or a documented OHLC-dependent volatility/range primitive
- volume, turnover, or liquidity-style primitives when caller-provided rows include those fields
- gap or breakout-style primitives where supported by the normalized input contract

Keep the API conservative and deterministic. Prefer small pure functions and validated record builders that match the style already used in `quant/features/technical.py`.

## Allowed Writes

Only:

- `quant/features/technical.py`
- `quant/features/__init__.py`
- `tests/features/test_technical.py`
- `coordination/reports/TASK-093_REPORT.md`

Use the smallest necessary subset of these files.

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files
- `coordination/reviews/**`
- `coordination/integrations/**`
- `quant/datahub/`
- `tests/datahub/`
- `quant/scanner/`
- `tests/scanner/`
- `quant/strategies/`
- `quant/backtest/`
- `quant/portfolio/`
- `quant/notification/`
- `quant/ai/`
- `quant/ui/`

Do not use credentials, cookies, tokens, browser session state, private account data, or live network access.

## Required Implementation

- Preserve existing public behavior for:
  - `DailyBarInput`
  - `normalize_daily_bars(...)`
  - `calculate_close_to_close_return(...)`
  - `calculate_simple_moving_average(...)`
  - `calculate_realized_volatility(...)`
  - existing feature-record builders
- Extend normalization only as needed for optional OHLCV/turnover fields. Existing close-only rows must keep working.
- Validate invalid input deterministically:
  - non-positive or non-finite prices
  - invalid windows/periods
  - insufficient rows
  - duplicate trade dates
  - mixed symbols or markets
  - malformed optional volume/turnover fields when a requested feature needs them
- Make missing optional fields raise clear `ValueError` messages only when the requested indicator requires those fields.
- Return finite numeric outputs or structured records that pass existing FeatureHub contract validation.
- Avoid pandas/numpy unless the project already depends on them for this module; pure standard-library code is preferred for this narrow handoff.

## Required Tests

Add focused offline tests covering:

- correct EMA and MACD values on a deterministic fixture
- correct RSI behavior on gains, losses, and boundary/flat-input cases
- correct Bollinger Band output and insufficient-window handling
- correct KDJ/stochastic or ATR/range-style output, including required OHLC field validation if applicable
- at least one volume/turnover/liquidity primitive, including missing-field validation
- feature-record builders, if new builders are added, passing `validate_feature_value_record(...)`
- preservation of existing tests and existing close-only row compatibility

Run:

- `python3 -m unittest tests/features/test_technical.py`
- `python3 -m unittest tests/features/test_contracts.py`

Recommended if focused tests pass:

- `python3 -m unittest discover tests/features`

Do not run live-enabled tests and do not set `QUANT_SYSTEM_LIVE_TESTS=1`.

## Completion Report

Write `coordination/reports/TASK-093_REPORT.md` with:

- files changed
- indicators/primitives added
- tests run and results
- default network behavior
- live-enabled result, which must remain `SKIP` because this task is offline-only and live tests are not permitted
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

The task is complete when:

- the FeatureHub technical library has a broader scanner/strategy-ready offline indicator set
- focused offline tests cover success, missing data, invalid parameters, boundary cases, and compatibility with existing close-only rows
- default tests remain offline-safe
- no DataHub, Scanner, strategy, backtest, portfolio, signal, risk, notification, AI, UI, credential, or live-network scope is introduced
