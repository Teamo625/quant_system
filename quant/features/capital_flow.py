"""Offline-safe capital-flow primitives built from local snapshot rows."""

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
class CapitalFlowSnapshotInput:
    """Minimal caller-provided capital-flow snapshot input."""

    symbol: str
    market: str
    trade_date: date
    main_net_inflow: float | None = None
    northbound_net_buy: float | None = None
    turnover_rate: float | None = None


def calculate_latest_main_net_inflow(
    rows: Iterable[CapitalFlowSnapshotInput | Mapping[str, Any]],
) -> float:
    """Return the latest main net inflow."""
    snapshots = normalize_capital_flow_snapshots(rows)
    return _require_main_net_inflow(snapshots[-1].main_net_inflow)


def calculate_trailing_main_net_inflow_sum(
    rows: Iterable[CapitalFlowSnapshotInput | Mapping[str, Any]],
    *,
    window: int,
) -> float:
    """Return the trailing sum of main net inflow values."""
    _validate_positive_window(window)
    snapshots = normalize_capital_flow_snapshots(rows)
    if len(snapshots) < window:
        raise ValueError("insufficient rows for requested main-net-inflow window")

    value = sum(
        _require_main_net_inflow(snapshot.main_net_inflow)
        for snapshot in snapshots[-window:]
    )
    _validate_finite_output(value=value, name="trailing main net inflow sum")
    return value


def calculate_latest_northbound_net_buy(
    rows: Iterable[CapitalFlowSnapshotInput | Mapping[str, Any]],
) -> float | None:
    """Return the latest northbound net buy value when present."""
    snapshots = normalize_capital_flow_snapshots(rows)
    return snapshots[-1].northbound_net_buy


def calculate_turnover_adjusted_main_net_inflow(
    rows: Iterable[CapitalFlowSnapshotInput | Mapping[str, Any]],
) -> float | None:
    """Return latest main net inflow divided by turnover rate when available."""
    snapshots = normalize_capital_flow_snapshots(rows)
    latest_snapshot = snapshots[-1]
    turnover_rate = latest_snapshot.turnover_rate
    if turnover_rate is None:
        return None
    if turnover_rate <= 0:
        raise ValueError(
            "turnover_rate must be a positive finite number for adjusted flow"
        )

    value = _require_main_net_inflow(latest_snapshot.main_net_inflow) / turnover_rate
    _validate_finite_output(value=value, name="turnover-adjusted main net inflow")
    return value


def build_latest_main_net_inflow_feature(
    rows: Iterable[CapitalFlowSnapshotInput | Mapping[str, Any]],
    *,
    created_at: datetime,
) -> FeatureValueRecord:
    """Build a validated CAPITAL_FLOW record for latest main net inflow."""
    snapshots = normalize_capital_flow_snapshots(rows)
    return _build_feature_record(
        snapshot=snapshots[-1],
        value=calculate_latest_main_net_inflow(snapshots),
        created_at=created_at,
    )


def normalize_capital_flow_snapshots(
    rows: Iterable[CapitalFlowSnapshotInput | Mapping[str, Any]],
) -> tuple[CapitalFlowSnapshotInput, ...]:
    """Normalize capital-flow-like rows into sorted validated inputs."""
    normalized_rows = tuple(_coerce_capital_flow_snapshot_input(row) for row in rows)
    if not normalized_rows:
        raise ValueError("at least one capital flow snapshot row is required")

    normalized_rows = tuple(sorted(normalized_rows, key=lambda row: row.trade_date))
    _validate_snapshot_series(normalized_rows)
    return normalized_rows


def _coerce_capital_flow_snapshot_input(
    row: CapitalFlowSnapshotInput | Mapping[str, Any],
) -> CapitalFlowSnapshotInput:
    payload = _row_mapping(row)

    symbol = payload.get("symbol")
    market = payload.get("market")
    trade_date_value = payload.get("trade_date")

    if not isinstance(symbol, str) or symbol.strip() == "":
        raise ValueError("capital flow snapshot symbol must be a non-empty string")
    if not isinstance(market, str) or market.strip() == "":
        raise ValueError("capital flow snapshot market must be a non-empty string")

    return CapitalFlowSnapshotInput(
        symbol=symbol.strip(),
        market=market.strip(),
        trade_date=_coerce_trade_date(trade_date_value),
        main_net_inflow=_coerce_optional_numeric_metric(
            payload.get("main_net_inflow"),
            field_name="main_net_inflow",
        ),
        northbound_net_buy=_coerce_optional_numeric_metric(
            payload.get("northbound_net_buy"),
            field_name="northbound_net_buy",
        ),
        turnover_rate=_coerce_optional_numeric_metric(
            payload.get("turnover_rate"),
            field_name="turnover_rate",
        ),
    )


def _row_mapping(
    row: CapitalFlowSnapshotInput | Mapping[str, Any],
) -> Mapping[str, Any]:
    if isinstance(row, Mapping):
        return row
    if is_dataclass(row) and not isinstance(row, type):
        return asdict(row)
    raise ValueError(
        "capital flow snapshot rows must be mappings or dataclass instances"
    )


def _coerce_trade_date(value: Any) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    raise ValueError(
        "capital flow snapshot trade_date must be a date or datetime instance"
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


def _require_main_net_inflow(value: float | None) -> float:
    if value is None:
        raise ValueError(
            "main_net_inflow is required for main-net-inflow calculation"
        )
    return value


def _validate_snapshot_series(rows: tuple[CapitalFlowSnapshotInput, ...]) -> None:
    first_row = rows[0]
    previous_trade_date: date | None = None

    for row in rows:
        if row.symbol != first_row.symbol:
            raise ValueError(
                "all capital flow snapshot rows must share the same symbol"
            )
        if row.market != first_row.market:
            raise ValueError(
                "all capital flow snapshot rows must share the same market"
            )
        if previous_trade_date is not None and row.trade_date == previous_trade_date:
            raise ValueError(
                "capital flow snapshot rows must have unique trade_date values"
            )
        previous_trade_date = row.trade_date


def _validate_positive_window(window: int) -> None:
    if isinstance(window, bool) or not isinstance(window, int) or window <= 0:
        raise ValueError("window must be a positive integer")


def _validate_finite_output(*, value: float, name: str) -> None:
    if not isfinite(value):
        raise ValueError(f"{name} produced a non-finite output")


def _build_feature_record(
    *,
    snapshot: CapitalFlowSnapshotInput,
    value: float,
    created_at: datetime,
) -> FeatureValueRecord:
    if not isinstance(created_at, datetime):
        raise ValueError("created_at must be a datetime instance")

    record = FeatureValueRecord(
        symbol=snapshot.symbol,
        market=snapshot.market,
        trade_date=snapshot.trade_date,
        feature_name=FeatureName.CAPITAL_FLOW,
        value=value,
        source_dataset=DatasetName.CAPITAL_FLOW_SNAPSHOT,
        created_at=created_at,
        schema_version=FEATURE_VALUE_SCHEMA_VERSION,
    )
    issues = validate_feature_value_record(record)
    if issues:
        raise ValueError(f"feature record failed validation: {issues!r}")
    return record
