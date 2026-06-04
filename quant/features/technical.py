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
    _validate_positive_window(window)
    bars = normalize_daily_bars(rows)
    if len(bars) < window:
        raise ValueError("insufficient rows for requested moving-average window")

    value = fmean(bar.close for bar in bars[-window:])
    _validate_finite_output(value=value, name="simple moving average")
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

    _validate_positive_window(window)
    if not isfinite(annualization_factor) or annualization_factor <= 0:
        raise ValueError("annualization_factor must be a positive finite number")

    bars = normalize_daily_bars(rows)
    if len(bars) < window + 1:
        raise ValueError("insufficient rows for requested realized-volatility window")

    trailing_bars = bars[-(window + 1) :]
    returns = tuple(
        (current.close / previous.close) - 1.0
        for previous, current in zip(trailing_bars, trailing_bars[1:])
    )
    mean_squared_return = fmean(value * value for value in returns)
    value = sqrt(mean_squared_return) * sqrt(annualization_factor)
    _validate_finite_output(value=value, name="realized volatility")
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

    if not isinstance(symbol, str) or symbol.strip() == "":
        raise ValueError("daily bar symbol must be a non-empty string")
    if not isinstance(market, str) or market.strip() == "":
        raise ValueError("daily bar market must be a non-empty string")

    trade_date = _coerce_trade_date(trade_date_value)
    close = _coerce_positive_close(close_value)

    return DailyBarInput(
        symbol=symbol.strip(),
        market=market.strip(),
        trade_date=trade_date,
        close=close,
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
