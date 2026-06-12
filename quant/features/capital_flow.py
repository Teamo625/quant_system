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


@dataclass(frozen=True)
class FundFlowInput:
    """Minimal caller-provided fund-flow input."""

    fund_code: str
    market: str
    trade_date: date
    net_inflow: float | None = None
    subscription_amount: float | None = None
    redemption_amount: float | None = None
    shares_change: float | None = None


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
    _validate_positive_integer(window, name="window")
    snapshots = normalize_capital_flow_snapshots(rows)
    if len(snapshots) < window:
        raise ValueError("insufficient rows for requested main-net-inflow window")

    value = sum(
        _require_main_net_inflow(snapshot.main_net_inflow)
        for snapshot in snapshots[-window:]
    )
    _validate_finite_output(value=value, name="trailing main net inflow sum")
    return value


def calculate_main_net_inflow_change(
    rows: Iterable[CapitalFlowSnapshotInput | Mapping[str, Any]],
    *,
    periods: int = 1,
) -> float:
    """Return the latest main-net-inflow change versus ``periods`` rows ago."""
    _validate_positive_integer(periods, name="periods")
    snapshots = normalize_capital_flow_snapshots(rows)
    if len(snapshots) <= periods:
        raise ValueError("insufficient rows for requested main-net-inflow change")

    latest_value = _require_main_net_inflow(snapshots[-1].main_net_inflow)
    previous_value = _require_main_net_inflow(snapshots[-1 - periods].main_net_inflow)
    value = latest_value - previous_value
    _validate_finite_output(value=value, name="main-net-inflow change")
    return value


def calculate_latest_northbound_net_buy(
    rows: Iterable[CapitalFlowSnapshotInput | Mapping[str, Any]],
) -> float | None:
    """Return the latest northbound net buy value when present."""
    snapshots = normalize_capital_flow_snapshots(rows)
    return snapshots[-1].northbound_net_buy


def calculate_northbound_net_buy_change(
    rows: Iterable[CapitalFlowSnapshotInput | Mapping[str, Any]],
    *,
    periods: int = 1,
) -> float | None:
    """Return the latest northbound-net-buy change when both rows have data."""
    _validate_positive_integer(periods, name="periods")
    snapshots = normalize_capital_flow_snapshots(rows)
    if len(snapshots) <= periods:
        raise ValueError("insufficient rows for requested northbound change")

    latest_value = snapshots[-1].northbound_net_buy
    previous_value = snapshots[-1 - periods].northbound_net_buy
    if latest_value is None or previous_value is None:
        return None

    value = latest_value - previous_value
    _validate_finite_output(value=value, name="northbound change")
    return value


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


def calculate_trailing_turnover_adjusted_main_net_inflow(
    rows: Iterable[CapitalFlowSnapshotInput | Mapping[str, Any]],
    *,
    window: int,
) -> float | None:
    """Return trailing main net inflow normalized by trailing turnover-rate sum."""
    _validate_positive_integer(window, name="window")
    snapshots = normalize_capital_flow_snapshots(rows)
    if len(snapshots) < window:
        raise ValueError("insufficient rows for requested adjusted-flow window")

    trailing_snapshots = snapshots[-window:]
    turnover_rates = [snapshot.turnover_rate for snapshot in trailing_snapshots]
    if any(turnover_rate is None for turnover_rate in turnover_rates):
        return None

    validated_turnover_rates = [
        _require_positive_turnover_rate(turnover_rate)
        for turnover_rate in turnover_rates
    ]
    value = sum(
        _require_main_net_inflow(snapshot.main_net_inflow)
        for snapshot in trailing_snapshots
    ) / sum(validated_turnover_rates)
    _validate_finite_output(
        value=value,
        name="trailing turnover-adjusted main net inflow",
    )
    return value


def calculate_latest_fund_net_inflow(
    rows: Iterable[FundFlowInput | Mapping[str, Any]],
) -> float:
    """Return the latest fund net inflow."""
    snapshots = normalize_fund_flow_inputs(rows)
    return _require_fund_net_inflow(snapshots[-1].net_inflow)


def calculate_trailing_fund_net_inflow_sum(
    rows: Iterable[FundFlowInput | Mapping[str, Any]],
    *,
    window: int,
) -> float:
    """Return the trailing sum of fund net inflow values."""
    _validate_positive_integer(window, name="window")
    snapshots = normalize_fund_flow_inputs(rows)
    if len(snapshots) < window:
        raise ValueError("insufficient rows for requested fund-flow window")

    value = sum(
        _require_fund_net_inflow(snapshot.net_inflow)
        for snapshot in snapshots[-window:]
    )
    _validate_finite_output(value=value, name="trailing fund net inflow sum")
    return value


def calculate_fund_net_inflow_change(
    rows: Iterable[FundFlowInput | Mapping[str, Any]],
    *,
    periods: int = 1,
) -> float:
    """Return the latest fund net inflow change versus ``periods`` rows ago."""
    _validate_positive_integer(periods, name="periods")
    snapshots = normalize_fund_flow_inputs(rows)
    if len(snapshots) <= periods:
        raise ValueError("insufficient rows for requested fund-flow change")

    latest_value = _require_fund_net_inflow(snapshots[-1].net_inflow)
    previous_value = _require_fund_net_inflow(snapshots[-1 - periods].net_inflow)
    value = latest_value - previous_value
    _validate_finite_output(value=value, name="fund-flow change")
    return value


def calculate_fund_flow_activity_intensity(
    rows: Iterable[FundFlowInput | Mapping[str, Any]],
) -> float | None:
    """Return latest net inflow normalized by subscription plus redemption."""
    snapshots = normalize_fund_flow_inputs(rows)
    latest_snapshot = snapshots[-1]
    if (
        latest_snapshot.subscription_amount is None
        or latest_snapshot.redemption_amount is None
    ):
        return None

    subscription_amount = _require_non_negative_flow_amount(
        latest_snapshot.subscription_amount,
        field_name="subscription_amount",
    )
    redemption_amount = _require_non_negative_flow_amount(
        latest_snapshot.redemption_amount,
        field_name="redemption_amount",
    )
    denominator = subscription_amount + redemption_amount
    if denominator <= 0:
        raise ValueError(
            "subscription_amount plus redemption_amount must be positive for fund-flow intensity"
        )

    value = _require_fund_net_inflow(latest_snapshot.net_inflow) / denominator
    _validate_finite_output(value=value, name="fund-flow activity intensity")
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


def normalize_fund_flow_inputs(
    rows: Iterable[FundFlowInput | Mapping[str, Any]],
) -> tuple[FundFlowInput, ...]:
    """Normalize fund-flow-like rows into sorted validated inputs."""
    normalized_rows = tuple(_coerce_fund_flow_input(row) for row in rows)
    if not normalized_rows:
        raise ValueError("at least one fund flow row is required")

    normalized_rows = tuple(sorted(normalized_rows, key=lambda row: row.trade_date))
    _validate_fund_flow_series(normalized_rows)
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


def _coerce_fund_flow_input(
    row: FundFlowInput | Mapping[str, Any],
) -> FundFlowInput:
    payload = _row_mapping(row)

    fund_code = payload.get("fund_code")
    market = payload.get("market")
    trade_date_value = payload.get("trade_date")

    if not isinstance(fund_code, str) or fund_code.strip() == "":
        raise ValueError("fund flow fund_code must be a non-empty string")
    if not isinstance(market, str) or market.strip() == "":
        raise ValueError("fund flow market must be a non-empty string")

    return FundFlowInput(
        fund_code=fund_code.strip(),
        market=market.strip(),
        trade_date=_coerce_trade_date(trade_date_value),
        net_inflow=_coerce_optional_numeric_metric(
            payload.get("net_inflow"),
            field_name="net_inflow",
        ),
        subscription_amount=_coerce_optional_numeric_metric(
            payload.get("subscription_amount"),
            field_name="subscription_amount",
        ),
        redemption_amount=_coerce_optional_numeric_metric(
            payload.get("redemption_amount"),
            field_name="redemption_amount",
        ),
        shares_change=_coerce_optional_numeric_metric(
            payload.get("shares_change"),
            field_name="shares_change",
        ),
    )


def _row_mapping(
    row: CapitalFlowSnapshotInput | FundFlowInput | Mapping[str, Any],
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


def _require_fund_net_inflow(value: float | None) -> float:
    if value is None:
        raise ValueError("net_inflow is required for fund-flow calculation")
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


def _validate_fund_flow_series(rows: tuple[FundFlowInput, ...]) -> None:
    first_row = rows[0]
    previous_trade_date: date | None = None

    for row in rows:
        if row.fund_code != first_row.fund_code:
            raise ValueError("all fund flow rows must share the same fund_code")
        if row.market != first_row.market:
            raise ValueError("all fund flow rows must share the same market")
        if previous_trade_date is not None and row.trade_date == previous_trade_date:
            raise ValueError("fund flow rows must have unique trade_date values")
        previous_trade_date = row.trade_date


def _validate_positive_integer(value: int, *, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")


def _require_positive_turnover_rate(value: float | None) -> float:
    if value is None or value <= 0:
        raise ValueError(
            "turnover_rate must be a positive finite number for adjusted flow"
        )
    return value


def _require_non_negative_flow_amount(value: float, *, field_name: str) -> float:
    if value < 0:
        raise ValueError(
            f"{field_name} must be a non-negative finite number for fund-flow intensity"
        )
    return value


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
