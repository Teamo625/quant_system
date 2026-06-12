"""Offline-safe price technical primitives built from local daily-bar rows."""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from datetime import date, datetime
from math import isfinite, sqrt
from statistics import fmean
from typing import Any, Iterable, Mapping

from quant.datahub.datasets import DatasetName

from .contracts import (
    FEATURE_VALUE_SCHEMA_VERSION,
    FeatureName,
    FeatureValueRecord,
    validate_feature_value_record,
)


@dataclass(frozen=True)
class DailyBarInput:
    """Minimal caller-provided daily bar input for price technical features."""

    symbol: str
    market: str
    trade_date: date
    close: float
    open: float | None = None
    high: float | None = None
    low: float | None = None
    volume: float | None = None
    turnover: float | None = None


@dataclass(frozen=True)
class MacdValue:
    macd_line: float
    signal_line: float
    histogram: float


@dataclass(frozen=True)
class StochasticOscillatorValue:
    percent_k: float
    percent_d: float
    percent_j: float


@dataclass(frozen=True)
class BollingerBandsValue:
    middle_band: float
    upper_band: float
    lower_band: float
    bandwidth: float


def calculate_close_to_close_return(
    rows: Iterable[DailyBarInput | Mapping[str, Any]],
) -> float:
    """Return the latest one-day simple return from trailing close prices."""
    bars = normalize_daily_bars(rows)
    if len(bars) < 2:
        raise ValueError("at least two rows are required for close-to-close return")

    previous_close = bars[-2].close
    current_close = bars[-1].close
    value = (current_close / previous_close) - 1.0
    _validate_finite_output(value=value, name="close-to-close return")
    return value


def calculate_simple_moving_average(
    rows: Iterable[DailyBarInput | Mapping[str, Any]],
    *,
    window: int,
) -> float:
    """Return the trailing simple moving average over close prices."""
    bars = normalize_daily_bars(rows)
    trailing_bars = _trailing_bars(
        bars,
        window=window,
        context="moving-average window",
    )
    value = fmean(bar.close for bar in trailing_bars)
    _validate_finite_output(value=value, name="simple moving average")
    return value


def calculate_exponential_moving_average(
    rows: Iterable[DailyBarInput | Mapping[str, Any]],
    *,
    window: int,
) -> float:
    """Return the latest EMA using an SMA seed over the first trailing window."""
    bars = normalize_daily_bars(rows)
    ema_values = _ema_series(tuple(bar.close for bar in bars), window=window)
    value = ema_values[-1]
    _validate_finite_output(value=value, name="exponential moving average")
    return value


def calculate_realized_volatility(
    rows: Iterable[DailyBarInput | Mapping[str, Any]],
    *,
    window: int,
    annualization_factor: float = 252.0,
) -> float:
    """Return trailing realized volatility from simple close-to-close returns.

    The implementation uses the root-mean-square of trailing simple returns and
    scales it by ``sqrt(annualization_factor)``.
    """

    if not isfinite(annualization_factor) or annualization_factor <= 0:
        raise ValueError("annualization_factor must be a positive finite number")

    bars = normalize_daily_bars(rows)
    trailing_bars = _trailing_bars(
        bars,
        window=window,
        context="realized-volatility window",
        required_extra_rows=1,
    )
    returns = tuple(
        (current.close / previous.close) - 1.0
        for previous, current in zip(trailing_bars, trailing_bars[1:])
    )
    mean_squared_return = fmean(value * value for value in returns)
    value = sqrt(mean_squared_return) * sqrt(annualization_factor)
    _validate_finite_output(value=value, name="realized volatility")
    return value


def calculate_macd(
    rows: Iterable[DailyBarInput | Mapping[str, Any]],
    *,
    short_window: int = 12,
    long_window: int = 26,
    signal_window: int = 9,
) -> MacdValue:
    """Return the latest MACD line, signal line, and histogram."""
    _validate_macd_windows(
        short_window=short_window,
        long_window=long_window,
        signal_window=signal_window,
    )
    bars = normalize_daily_bars(rows)
    closes = tuple(bar.close for bar in bars)

    short_ema = _ema_series(closes, window=short_window)
    long_ema = _ema_series(closes, window=long_window)
    macd_line_values = tuple(
        short_ema[index - (short_window - 1)] - long_ema[index - (long_window - 1)]
        for index in range(long_window - 1, len(closes))
    )
    if len(macd_line_values) < signal_window:
        raise ValueError("insufficient rows for requested MACD signal window")

    signal_line_values = _ema_series(macd_line_values, window=signal_window)
    macd_line = macd_line_values[-1]
    signal_line = signal_line_values[-1]
    histogram = macd_line - signal_line
    for name, value in (
        ("MACD line", macd_line),
        ("MACD signal line", signal_line),
        ("MACD histogram", histogram),
    ):
        _validate_finite_output(value=value, name=name)
    return MacdValue(
        macd_line=macd_line,
        signal_line=signal_line,
        histogram=histogram,
    )


def calculate_relative_strength_index(
    rows: Iterable[DailyBarInput | Mapping[str, Any]],
    *,
    window: int = 14,
) -> float:
    """Return the latest RSI from trailing close-to-close changes."""
    bars = normalize_daily_bars(rows)
    trailing_bars = _trailing_bars(
        bars,
        window=window,
        context="RSI window",
        required_extra_rows=1,
    )
    deltas = tuple(
        current.close - previous.close
        for previous, current in zip(trailing_bars, trailing_bars[1:])
    )
    gains = tuple(max(delta, 0.0) for delta in deltas)
    losses = tuple(max(-delta, 0.0) for delta in deltas)
    average_gain = fmean(gains)
    average_loss = fmean(losses)

    if average_gain == 0.0 and average_loss == 0.0:
        value = 50.0
    elif average_loss == 0.0:
        value = 100.0
    elif average_gain == 0.0:
        value = 0.0
    else:
        relative_strength = average_gain / average_loss
        value = 100.0 - (100.0 / (1.0 + relative_strength))

    _validate_finite_output(value=value, name="relative strength index")
    return value


def calculate_stochastic_oscillator(
    rows: Iterable[DailyBarInput | Mapping[str, Any]],
    *,
    k_window: int = 9,
    d_window: int = 3,
) -> StochasticOscillatorValue:
    """Return the latest stochastic %K/%D and derived KDJ %J values."""
    _validate_positive_window(k_window)
    _validate_positive_window(d_window)
    bars = normalize_daily_bars(rows)
    minimum_rows = k_window + d_window - 1
    if len(bars) < minimum_rows:
        raise ValueError("insufficient rows for requested stochastic windows")

    percent_k_values = tuple(
        _raw_stochastic_value(
            bars[end_index - k_window : end_index],
        )
        for end_index in range(k_window, len(bars) + 1)
    )
    if len(percent_k_values) < d_window:
        raise ValueError("insufficient rows for requested stochastic windows")

    trailing_percent_k = percent_k_values[-d_window:]
    percent_k = trailing_percent_k[-1]
    percent_d = fmean(trailing_percent_k)
    percent_j = (3.0 * percent_k) - (2.0 * percent_d)
    for name, value in (
        ("stochastic %K", percent_k),
        ("stochastic %D", percent_d),
        ("stochastic %J", percent_j),
    ):
        _validate_finite_output(value=value, name=name)
    return StochasticOscillatorValue(
        percent_k=percent_k,
        percent_d=percent_d,
        percent_j=percent_j,
    )


def calculate_bollinger_bands(
    rows: Iterable[DailyBarInput | Mapping[str, Any]],
    *,
    window: int = 20,
    num_std_dev: float = 2.0,
) -> BollingerBandsValue:
    """Return the latest Bollinger middle, upper, and lower bands."""
    if not isfinite(num_std_dev) or num_std_dev <= 0:
        raise ValueError("num_std_dev must be a positive finite number")

    bars = normalize_daily_bars(rows)
    trailing_bars = _trailing_bars(
        bars,
        window=window,
        context="Bollinger-band window",
    )
    closes = tuple(bar.close for bar in trailing_bars)
    middle_band = fmean(closes)
    variance = fmean((close - middle_band) ** 2 for close in closes)
    standard_deviation = sqrt(variance)
    upper_band = middle_band + (num_std_dev * standard_deviation)
    lower_band = middle_band - (num_std_dev * standard_deviation)
    bandwidth = (upper_band - lower_band) / middle_band
    for name, value in (
        ("Bollinger middle band", middle_band),
        ("Bollinger upper band", upper_band),
        ("Bollinger lower band", lower_band),
        ("Bollinger bandwidth", bandwidth),
    ):
        _validate_finite_output(value=value, name=name)
    return BollingerBandsValue(
        middle_band=middle_band,
        upper_band=upper_band,
        lower_band=lower_band,
        bandwidth=bandwidth,
    )


def calculate_average_true_range(
    rows: Iterable[DailyBarInput | Mapping[str, Any]],
    *,
    window: int = 14,
) -> float:
    """Return the latest ATR from trailing true ranges."""
    bars = normalize_daily_bars(rows)
    trailing_bars = _trailing_bars(
        bars,
        window=window,
        context="ATR window",
        required_extra_rows=1,
    )
    true_ranges = tuple(
        _true_range(previous_bar=previous, current_bar=current)
        for previous, current in zip(trailing_bars, trailing_bars[1:])
    )
    value = fmean(true_ranges)
    _validate_finite_output(value=value, name="average true range")
    return value


def calculate_average_volume(
    rows: Iterable[DailyBarInput | Mapping[str, Any]],
    *,
    window: int,
) -> float:
    """Return trailing average volume."""
    bars = normalize_daily_bars(rows)
    trailing_bars = _trailing_bars(
        bars,
        window=window,
        context="average-volume window",
    )
    value = fmean(_require_nonnegative_field(bar, "volume") for bar in trailing_bars)
    _validate_finite_output(value=value, name="average volume")
    return value


def calculate_average_turnover(
    rows: Iterable[DailyBarInput | Mapping[str, Any]],
    *,
    window: int,
) -> float:
    """Return trailing average turnover."""
    bars = normalize_daily_bars(rows)
    trailing_bars = _trailing_bars(
        bars,
        window=window,
        context="average-turnover window",
    )
    value = fmean(_require_nonnegative_field(bar, "turnover") for bar in trailing_bars)
    _validate_finite_output(value=value, name="average turnover")
    return value


def calculate_amihud_illiquidity(
    rows: Iterable[DailyBarInput | Mapping[str, Any]],
    *,
    window: int,
) -> float:
    """Return trailing Amihud-style illiquidity using absolute return over turnover."""
    bars = normalize_daily_bars(rows)
    trailing_bars = _trailing_bars(
        bars,
        window=window,
        context="illiquidity window",
        required_extra_rows=1,
    )
    illiquidity_values = []
    for previous, current in zip(trailing_bars, trailing_bars[1:]):
        turnover = _require_positive_field(current, "turnover")
        absolute_return = abs((current.close / previous.close) - 1.0)
        illiquidity_values.append(absolute_return / turnover)

    value = fmean(illiquidity_values)
    _validate_finite_output(value=value, name="Amihud illiquidity")
    return value


def calculate_gap_return(
    rows: Iterable[DailyBarInput | Mapping[str, Any]],
) -> float:
    """Return the latest open-to-previous-close gap."""
    bars = normalize_daily_bars(rows)
    if len(bars) < 2:
        raise ValueError("at least two rows are required for gap return")

    previous_bar = bars[-2]
    current_bar = bars[-1]
    opening_price = _require_positive_field(current_bar, "open")
    value = (opening_price / previous_bar.close) - 1.0
    _validate_finite_output(value=value, name="gap return")
    return value


def calculate_breakout_ratio(
    rows: Iterable[DailyBarInput | Mapping[str, Any]],
    *,
    window: int = 20,
) -> float:
    """Return the latest close relative to the prior trailing high breakout level."""
    bars = normalize_daily_bars(rows)
    trailing_bars = _trailing_bars(
        bars,
        window=window,
        context="breakout window",
        required_extra_rows=1,
    )
    prior_window = trailing_bars[:-1]
    breakout_level = max(_require_positive_field(bar, "high") for bar in prior_window)
    value = (trailing_bars[-1].close / breakout_level) - 1.0
    _validate_finite_output(value=value, name="breakout ratio")
    return value


def build_close_to_close_return_feature(
    rows: Iterable[DailyBarInput | Mapping[str, Any]],
    *,
    created_at: datetime,
) -> FeatureValueRecord:
    """Build a validated PRICE_TECHNICAL record for the latest one-day return."""
    bars = normalize_daily_bars(rows)
    return _build_feature_record(
        bar=bars[-1],
        value=calculate_close_to_close_return(bars),
        created_at=created_at,
    )


def build_simple_moving_average_feature(
    rows: Iterable[DailyBarInput | Mapping[str, Any]],
    *,
    window: int,
    created_at: datetime,
) -> FeatureValueRecord:
    """Build a validated PRICE_TECHNICAL record for trailing SMA."""
    bars = normalize_daily_bars(rows)
    return _build_feature_record(
        bar=bars[-1],
        value=calculate_simple_moving_average(bars, window=window),
        created_at=created_at,
    )


def build_realized_volatility_feature(
    rows: Iterable[DailyBarInput | Mapping[str, Any]],
    *,
    window: int,
    created_at: datetime,
    annualization_factor: float = 252.0,
) -> FeatureValueRecord:
    """Build a validated PRICE_TECHNICAL record for trailing realized volatility."""
    bars = normalize_daily_bars(rows)
    return _build_feature_record(
        bar=bars[-1],
        value=calculate_realized_volatility(
            bars,
            window=window,
            annualization_factor=annualization_factor,
        ),
        created_at=created_at,
    )


def build_exponential_moving_average_feature(
    rows: Iterable[DailyBarInput | Mapping[str, Any]],
    *,
    window: int,
    created_at: datetime,
) -> FeatureValueRecord:
    """Build a validated PRICE_TECHNICAL record for trailing EMA."""
    bars = normalize_daily_bars(rows)
    return _build_feature_record(
        bar=bars[-1],
        value=calculate_exponential_moving_average(bars, window=window),
        created_at=created_at,
    )


def build_relative_strength_index_feature(
    rows: Iterable[DailyBarInput | Mapping[str, Any]],
    *,
    window: int,
    created_at: datetime,
) -> FeatureValueRecord:
    """Build a validated PRICE_TECHNICAL record for trailing RSI."""
    bars = normalize_daily_bars(rows)
    return _build_feature_record(
        bar=bars[-1],
        value=calculate_relative_strength_index(bars, window=window),
        created_at=created_at,
    )


def build_average_true_range_feature(
    rows: Iterable[DailyBarInput | Mapping[str, Any]],
    *,
    window: int,
    created_at: datetime,
) -> FeatureValueRecord:
    """Build a validated PRICE_TECHNICAL record for trailing ATR."""
    bars = normalize_daily_bars(rows)
    return _build_feature_record(
        bar=bars[-1],
        value=calculate_average_true_range(bars, window=window),
        created_at=created_at,
    )


def normalize_daily_bars(
    rows: Iterable[DailyBarInput | Mapping[str, Any]],
) -> tuple[DailyBarInput, ...]:
    """Normalize daily-bar-like rows into sorted validated inputs."""
    normalized_rows = tuple(_coerce_daily_bar_input(row) for row in rows)
    if not normalized_rows:
        raise ValueError("at least one daily bar row is required")

    normalized_rows = tuple(sorted(normalized_rows, key=lambda row: row.trade_date))
    _validate_bar_series(normalized_rows)
    return normalized_rows


def _coerce_daily_bar_input(row: DailyBarInput | Mapping[str, Any]) -> DailyBarInput:
    payload = _row_mapping(row)

    symbol = payload.get("symbol")
    market = payload.get("market")
    trade_date_value = payload.get("trade_date")
    close_value = payload.get("close")
    open_value = payload.get("open")
    high_value = payload.get("high")
    low_value = payload.get("low")
    volume_value = payload.get("volume")
    turnover_value = payload.get("turnover")

    if not isinstance(symbol, str) or symbol.strip() == "":
        raise ValueError("daily bar symbol must be a non-empty string")
    if not isinstance(market, str) or market.strip() == "":
        raise ValueError("daily bar market must be a non-empty string")

    trade_date = _coerce_trade_date(trade_date_value)
    close = _coerce_positive_close(close_value)
    opening_price = _coerce_optional_positive_number(open_value, "open")
    high = _coerce_optional_positive_number(high_value, "high")
    low = _coerce_optional_positive_number(low_value, "low")
    volume = _coerce_optional_nonnegative_number(volume_value, "volume")
    turnover = _coerce_optional_nonnegative_number(turnover_value, "turnover")
    _validate_price_range_fields(
        open=opening_price,
        high=high,
        low=low,
        close=close,
    )

    return DailyBarInput(
        symbol=symbol.strip(),
        market=market.strip(),
        trade_date=trade_date,
        close=close,
        open=opening_price,
        high=high,
        low=low,
        volume=volume,
        turnover=turnover,
    )


def _row_mapping(row: DailyBarInput | Mapping[str, Any]) -> Mapping[str, Any]:
    if isinstance(row, Mapping):
        return row
    if is_dataclass(row) and not isinstance(row, type):
        return asdict(row)
    raise ValueError("daily bar rows must be mappings or dataclass instances")


def _coerce_trade_date(value: Any) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    raise ValueError("daily bar trade_date must be a date or datetime instance")


def _coerce_positive_close(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("daily bar close must be a positive finite number")

    close = float(value)
    if not isfinite(close) or close <= 0:
        raise ValueError("daily bar close must be a positive finite number")
    return close


def _coerce_optional_positive_number(value: Any, field_name: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"daily bar {field_name} must be a positive finite number")
    numeric_value = float(value)
    if not isfinite(numeric_value) or numeric_value <= 0:
        raise ValueError(f"daily bar {field_name} must be a positive finite number")
    return numeric_value


def _coerce_optional_nonnegative_number(value: Any, field_name: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"daily bar {field_name} must be a non-negative finite number")
    numeric_value = float(value)
    if not isfinite(numeric_value) or numeric_value < 0:
        raise ValueError(f"daily bar {field_name} must be a non-negative finite number")
    return numeric_value


def _validate_price_range_fields(
    *,
    open: float | None,
    high: float | None,
    low: float | None,
    close: float,
) -> None:
    if high is not None and low is not None and low > high:
        raise ValueError("daily bar low must not exceed high")
    if high is not None and close > high:
        raise ValueError("daily bar close must not exceed high")
    if low is not None and close < low:
        raise ValueError("daily bar close must not be below low")
    if open is not None and high is not None and open > high:
        raise ValueError("daily bar open must not exceed high")
    if open is not None and low is not None and open < low:
        raise ValueError("daily bar open must not be below low")


def _validate_bar_series(rows: tuple[DailyBarInput, ...]) -> None:
    first_row = rows[0]
    previous_trade_date: date | None = None

    for row in rows:
        if row.symbol != first_row.symbol:
            raise ValueError("all daily bar rows must share the same symbol")
        if row.market != first_row.market:
            raise ValueError("all daily bar rows must share the same market")
        if previous_trade_date is not None and row.trade_date == previous_trade_date:
            raise ValueError("daily bar rows must have unique trade_date values")
        previous_trade_date = row.trade_date


def _validate_positive_window(window: int) -> None:
    if isinstance(window, bool) or not isinstance(window, int) or window <= 0:
        raise ValueError("window must be a positive integer")


def _trailing_bars(
    bars: tuple[DailyBarInput, ...],
    *,
    window: int,
    context: str,
    required_extra_rows: int = 0,
) -> tuple[DailyBarInput, ...]:
    _validate_positive_window(window)
    required_rows = window + required_extra_rows
    if len(bars) < required_rows:
        raise ValueError(f"insufficient rows for requested {context}")
    return bars[-required_rows:]


def _ema_series(values: tuple[float, ...], *, window: int) -> tuple[float, ...]:
    _validate_positive_window(window)
    if len(values) < window:
        raise ValueError("insufficient values for requested EMA window")

    smoothing_factor = 2.0 / (window + 1.0)
    ema_values = [fmean(values[:window])]
    for value in values[window:]:
        ema_values.append((value * smoothing_factor) + (ema_values[-1] * (1.0 - smoothing_factor)))
    return tuple(ema_values)


def _validate_macd_windows(
    *,
    short_window: int,
    long_window: int,
    signal_window: int,
) -> None:
    _validate_positive_window(short_window)
    _validate_positive_window(long_window)
    _validate_positive_window(signal_window)
    if short_window >= long_window:
        raise ValueError("short_window must be smaller than long_window for MACD")


def _raw_stochastic_value(bars: tuple[DailyBarInput, ...]) -> float:
    highest_high = max(_require_positive_field(bar, "high") for bar in bars)
    lowest_low = min(_require_positive_field(bar, "low") for bar in bars)
    latest_close = bars[-1].close
    if highest_high == lowest_low:
        return 50.0
    value = ((latest_close - lowest_low) / (highest_high - lowest_low)) * 100.0
    _validate_finite_output(value=value, name="raw stochastic value")
    return value


def _true_range(*, previous_bar: DailyBarInput, current_bar: DailyBarInput) -> float:
    high = _require_positive_field(current_bar, "high")
    low = _require_positive_field(current_bar, "low")
    value = max(
        high - low,
        abs(high - previous_bar.close),
        abs(low - previous_bar.close),
    )
    _validate_finite_output(value=value, name="true range")
    return value


def _require_positive_field(bar: DailyBarInput, field_name: str) -> float:
    value = getattr(bar, field_name)
    if value is None:
        raise ValueError(f"daily bar {field_name} is required for this calculation")
    if value <= 0:
        raise ValueError(f"daily bar {field_name} must be a positive finite number")
    return value


def _require_nonnegative_field(bar: DailyBarInput, field_name: str) -> float:
    value = getattr(bar, field_name)
    if value is None:
        raise ValueError(f"daily bar {field_name} is required for this calculation")
    if value < 0:
        raise ValueError(f"daily bar {field_name} must be a non-negative finite number")
    return value


def _validate_finite_output(*, value: float, name: str) -> None:
    if not isfinite(value):
        raise ValueError(f"{name} produced a non-finite output")


def _build_feature_record(
    *,
    bar: DailyBarInput,
    value: float,
    created_at: datetime,
) -> FeatureValueRecord:
    if not isinstance(created_at, datetime):
        raise ValueError("created_at must be a datetime instance")

    record = FeatureValueRecord(
        symbol=bar.symbol,
        market=bar.market,
        trade_date=bar.trade_date,
        feature_name=FeatureName.PRICE_TECHNICAL,
        value=value,
        source_dataset=DatasetName.DAILY_BARS,
        created_at=created_at,
        schema_version=FEATURE_VALUE_SCHEMA_VERSION,
    )
    issues = validate_feature_value_record(record)
    if issues:
        raise ValueError(f"feature record failed validation: {issues!r}")
    return record
