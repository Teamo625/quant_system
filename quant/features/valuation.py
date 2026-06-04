"""Offline-safe valuation primitives built from local valuation snapshot rows."""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from datetime import date, datetime
from math import isfinite
from typing import Any, Iterable, Mapping

from quant.datahub.datasets import DatasetName

from .contracts import (
    FEATURE_VALUE_SCHEMA_VERSION,
    FeatureName,
    FeatureValueRecord,
    validate_feature_value_record,
)


@dataclass(frozen=True)
class ValuationSnapshotInput:
    """Minimal caller-provided valuation snapshot input for valuation features."""

    symbol: str
    market: str
    trade_date: date
    pe_ttm: float | None = None
    pb: float | None = None
    market_cap: float | None = None
    float_market_cap: float | None = None


def calculate_earnings_yield(
    rows: Iterable[ValuationSnapshotInput | Mapping[str, Any]],
) -> float:
    """Return the latest earnings yield from ``pe_ttm``."""
    snapshots = normalize_valuation_snapshots(rows)
    pe_ttm = _require_ratio_input(snapshots[-1].pe_ttm, field_name="pe_ttm")
    value = 1.0 / pe_ttm
    _validate_finite_output(value=value, name="earnings yield")
    return value


def calculate_book_to_price(
    rows: Iterable[ValuationSnapshotInput | Mapping[str, Any]],
) -> float:
    """Return the latest book-to-price ratio from ``pb``."""
    snapshots = normalize_valuation_snapshots(rows)
    pb = _require_ratio_input(snapshots[-1].pb, field_name="pb")
    value = 1.0 / pb
    _validate_finite_output(value=value, name="book-to-price")
    return value


def calculate_float_market_cap_ratio(
    rows: Iterable[ValuationSnapshotInput | Mapping[str, Any]],
) -> float:
    """Return the latest float-market-cap ratio from market-cap inputs."""
    snapshots = normalize_valuation_snapshots(rows)
    latest_snapshot = snapshots[-1]
    if latest_snapshot.float_market_cap is None:
        raise ValueError(
            "float_market_cap is required for float-market-cap ratio calculation"
        )

    float_market_cap = _coerce_non_negative_cap(
        latest_snapshot.float_market_cap,
        field_name="float_market_cap",
    )
    market_cap = _require_positive_cap(
        latest_snapshot.market_cap,
        field_name="market_cap",
    )
    value = float_market_cap / market_cap
    _validate_finite_output(value=value, name="float-market-cap ratio")
    return value


def build_earnings_yield_feature(
    rows: Iterable[ValuationSnapshotInput | Mapping[str, Any]],
    *,
    created_at: datetime,
) -> FeatureValueRecord:
    """Build a validated VALUATION record for the latest earnings yield."""
    snapshots = normalize_valuation_snapshots(rows)
    return _build_feature_record(
        snapshot=snapshots[-1],
        value=calculate_earnings_yield(snapshots),
        created_at=created_at,
    )


def build_book_to_price_feature(
    rows: Iterable[ValuationSnapshotInput | Mapping[str, Any]],
    *,
    created_at: datetime,
) -> FeatureValueRecord:
    """Build a validated VALUATION record for the latest book-to-price ratio."""
    snapshots = normalize_valuation_snapshots(rows)
    return _build_feature_record(
        snapshot=snapshots[-1],
        value=calculate_book_to_price(snapshots),
        created_at=created_at,
    )


def build_float_market_cap_ratio_feature(
    rows: Iterable[ValuationSnapshotInput | Mapping[str, Any]],
    *,
    created_at: datetime,
) -> FeatureValueRecord:
    """Build a validated VALUATION record for the latest float-market-cap ratio."""
    snapshots = normalize_valuation_snapshots(rows)
    return _build_feature_record(
        snapshot=snapshots[-1],
        value=calculate_float_market_cap_ratio(snapshots),
        created_at=created_at,
    )


def normalize_valuation_snapshots(
    rows: Iterable[ValuationSnapshotInput | Mapping[str, Any]],
) -> tuple[ValuationSnapshotInput, ...]:
    """Normalize valuation-snapshot-like rows into sorted validated inputs."""
    normalized_rows = tuple(_coerce_valuation_snapshot_input(row) for row in rows)
    if not normalized_rows:
        raise ValueError("at least one valuation snapshot row is required")

    normalized_rows = tuple(sorted(normalized_rows, key=lambda row: row.trade_date))
    _validate_snapshot_series(normalized_rows)
    return normalized_rows


def _coerce_valuation_snapshot_input(
    row: ValuationSnapshotInput | Mapping[str, Any],
) -> ValuationSnapshotInput:
    payload = _row_mapping(row)

    symbol = payload.get("symbol")
    market = payload.get("market")
    trade_date_value = payload.get("trade_date")

    if not isinstance(symbol, str) or symbol.strip() == "":
        raise ValueError("valuation snapshot symbol must be a non-empty string")
    if not isinstance(market, str) or market.strip() == "":
        raise ValueError("valuation snapshot market must be a non-empty string")

    return ValuationSnapshotInput(
        symbol=symbol.strip(),
        market=market.strip(),
        trade_date=_coerce_trade_date(trade_date_value),
        pe_ttm=_coerce_optional_numeric_metric(
            payload.get("pe_ttm"),
            field_name="pe_ttm",
        ),
        pb=_coerce_optional_numeric_metric(payload.get("pb"), field_name="pb"),
        market_cap=_coerce_optional_numeric_metric(
            payload.get("market_cap"),
            field_name="market_cap",
        ),
        float_market_cap=_coerce_optional_numeric_metric(
            payload.get("float_market_cap"),
            field_name="float_market_cap",
        ),
    )


def _row_mapping(
    row: ValuationSnapshotInput | Mapping[str, Any],
) -> Mapping[str, Any]:
    if isinstance(row, Mapping):
        return row
    if is_dataclass(row) and not isinstance(row, type):
        return asdict(row)
    raise ValueError(
        "valuation snapshot rows must be mappings or dataclass instances"
    )


def _coerce_trade_date(value: Any) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    raise ValueError(
        "valuation snapshot trade_date must be a date or datetime instance"
    )


def _coerce_optional_numeric_metric(
    value: Any,
    *,
    field_name: str,
) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be a finite number when provided")

    numeric_value = float(value)
    if not isfinite(numeric_value):
        raise ValueError(f"{field_name} must be a finite number when provided")
    return numeric_value


def _validate_snapshot_series(rows: tuple[ValuationSnapshotInput, ...]) -> None:
    first_row = rows[0]
    previous_trade_date: date | None = None

    for row in rows:
        if row.symbol != first_row.symbol:
            raise ValueError("all valuation snapshot rows must share the same symbol")
        if row.market != first_row.market:
            raise ValueError("all valuation snapshot rows must share the same market")
        if previous_trade_date is not None and row.trade_date == previous_trade_date:
            raise ValueError(
                "valuation snapshot rows must have unique trade_date values"
            )
        previous_trade_date = row.trade_date


def _require_ratio_input(value: float | None, *, field_name: str) -> float:
    if value is None:
        raise ValueError(f"{field_name} is required for valuation ratio calculation")
    if value == 0.0:
        raise ValueError(f"{field_name} must be a non-zero finite number")
    return value


def _coerce_non_negative_cap(value: Any, *, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be a non-negative finite number")

    numeric_value = float(value)
    if not isfinite(numeric_value) or numeric_value < 0:
        raise ValueError(f"{field_name} must be a non-negative finite number")
    return numeric_value


def _require_positive_cap(value: float | None, *, field_name: str) -> float:
    if value is None:
        raise ValueError(
            f"{field_name} is required for float-market-cap ratio calculation"
        )
    if value <= 0:
        raise ValueError(f"{field_name} must be a positive finite number")
    return value


def _validate_finite_output(*, value: float, name: str) -> None:
    if not isfinite(value):
        raise ValueError(f"{name} produced a non-finite output")


def _build_feature_record(
    *,
    snapshot: ValuationSnapshotInput,
    value: float,
    created_at: datetime,
) -> FeatureValueRecord:
    if not isinstance(created_at, datetime):
        raise ValueError("created_at must be a datetime instance")

    record = FeatureValueRecord(
        symbol=snapshot.symbol,
        market=snapshot.market,
        trade_date=snapshot.trade_date,
        feature_name=FeatureName.VALUATION,
        value=value,
        source_dataset=DatasetName.VALUATION_SNAPSHOT,
        created_at=created_at,
        schema_version=FEATURE_VALUE_SCHEMA_VERSION,
    )
    issues = validate_feature_value_record(record)
    if issues:
        raise ValueError(f"feature record failed validation: {issues!r}")
    return record
