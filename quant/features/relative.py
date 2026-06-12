"""Offline-safe relative-feature primitives built from local caller-provided rows."""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from datetime import date, datetime
from math import isfinite
from statistics import fmean
from typing import Any, Iterable, Mapping


@dataclass(frozen=True)
class RelativePriceInput:
    """Minimal price input for stock, sector, index, or fund relative features."""

    entity_id: str
    market: str
    trade_date: date
    close: float


@dataclass(frozen=True)
class EntityReturnInput:
    """Minimal dated return input for one sector/index-like entity."""

    entity_id: str
    market: str
    trade_date: date
    return_value: float


@dataclass(frozen=True)
class MemberReturnInput:
    """Minimal one-date constituent return input for breadth calculations."""

    universe_id: str
    market: str
    trade_date: date
    member_id: str
    return_value: float


@dataclass(frozen=True)
class SectorRotationRanking:
    """Deterministic sector rotation ranking output."""

    sector_id: str
    market: str
    trade_date: date
    trailing_return: float
    rank: int


def calculate_stock_vs_sector_return_spread(
    stock_rows: Iterable[RelativePriceInput | Mapping[str, Any]],
    sector_rows: Iterable[RelativePriceInput | Mapping[str, Any]],
    *,
    window: int,
) -> float:
    """Return stock trailing return minus sector trailing return over aligned dates."""
    stock_series, sector_series = _aligned_price_series(
        stock_rows,
        sector_rows,
        window=window,
        context="stock-vs-sector window",
    )
    value = _trailing_return_from_aligned_series(stock_series) - _trailing_return_from_aligned_series(
        sector_series
    )
    _validate_finite_output(value=value, name="stock-vs-sector return spread")
    return value


def calculate_sector_strength(
    sector_rows: Iterable[RelativePriceInput | Mapping[str, Any]],
    *,
    window: int,
) -> float:
    """Return trailing sector price strength over the requested window."""
    series = normalize_relative_price_series(sector_rows)
    trailing_rows = _require_price_window(
        series,
        window=window,
        context="sector-strength window",
    )
    value = _trailing_return_from_aligned_series(trailing_rows)
    _validate_finite_output(value=value, name="sector strength")
    return value


def calculate_sector_strength_from_returns(
    sector_rows: Iterable[EntityReturnInput | Mapping[str, Any]],
    *,
    window: int,
) -> float:
    """Return compounded sector strength from trailing dated sector returns."""
    series = normalize_entity_return_series(sector_rows)
    trailing_rows = _require_return_window(
        series,
        window=window,
        context="sector-strength return window",
    )
    compounded = 1.0
    for row in trailing_rows:
        compounded *= 1.0 + row.return_value
    value = compounded - 1.0
    _validate_finite_output(value=value, name="sector strength from returns")
    return value


def calculate_index_relative_performance(
    asset_rows: Iterable[RelativePriceInput | Mapping[str, Any]],
    index_rows: Iterable[RelativePriceInput | Mapping[str, Any]],
    *,
    window: int,
) -> float:
    """Return asset trailing return minus index trailing return over aligned dates."""
    asset_series, index_series = _aligned_price_series(
        asset_rows,
        index_rows,
        window=window,
        context="index-relative window",
    )
    value = _trailing_return_from_aligned_series(asset_series) - _trailing_return_from_aligned_series(
        index_series
    )
    _validate_finite_output(value=value, name="index-relative performance")
    return value


def calculate_positive_return_ratio(
    rows: Iterable[MemberReturnInput | Mapping[str, Any]],
) -> float:
    """Return the one-date positive-return breadth ratio."""
    normalized_rows = normalize_member_return_rows(rows)
    positive_count = sum(row.return_value > 0.0 for row in normalized_rows)
    value = positive_count / len(normalized_rows)
    _validate_finite_output(value=value, name="positive return ratio")
    return value


def calculate_above_threshold_return_ratio(
    rows: Iterable[MemberReturnInput | Mapping[str, Any]],
    *,
    threshold: float,
) -> float:
    """Return the one-date breadth ratio above a caller-provided threshold."""
    if isinstance(threshold, bool) or not isinstance(threshold, (int, float)):
        raise ValueError("threshold must be a finite number")

    numeric_threshold = float(threshold)
    if not isfinite(numeric_threshold):
        raise ValueError("threshold must be a finite number")

    normalized_rows = normalize_member_return_rows(rows)
    positive_count = sum(row.return_value > numeric_threshold for row in normalized_rows)
    value = positive_count / len(normalized_rows)
    _validate_finite_output(value=value, name="above-threshold return ratio")
    return value


def calculate_sector_return_rankings(
    rows: Iterable[RelativePriceInput | Mapping[str, Any]],
    *,
    window: int,
) -> tuple[SectorRotationRanking, ...]:
    """Return deterministic sector rankings from aligned trailing sector returns."""
    aligned_panel = _aligned_price_panel(rows, window=window)
    market = next(iter(aligned_panel.values()))[0].market
    trade_date = next(iter(aligned_panel.values()))[-1].trade_date
    ranked_items = sorted(
        (
            (
                sector_id,
                _trailing_return_from_aligned_series(series),
            )
            for sector_id, series in aligned_panel.items()
        ),
        key=lambda item: (-item[1], item[0]),
    )
    return tuple(
        SectorRotationRanking(
            sector_id=sector_id,
            market=market,
            trade_date=trade_date,
            trailing_return=trailing_return,
            rank=index,
        )
        for index, (sector_id, trailing_return) in enumerate(ranked_items, start=1)
    )


def calculate_relative_sector_momentum(
    rows: Iterable[RelativePriceInput | Mapping[str, Any]],
    *,
    target_sector_id: str,
    window: int,
) -> float:
    """Return target-sector trailing return minus the cross-sectional mean."""
    if not isinstance(target_sector_id, str) or target_sector_id.strip() == "":
        raise ValueError("target_sector_id must be a non-empty string")

    target_sector_id = target_sector_id.strip()
    rankings = calculate_sector_return_rankings(rows, window=window)
    ranking_by_sector = {ranking.sector_id: ranking for ranking in rankings}
    if target_sector_id not in ranking_by_sector:
        raise ValueError("target_sector_id must exist in the sector rotation input rows")

    cross_section_mean = fmean(ranking.trailing_return for ranking in rankings)
    value = ranking_by_sector[target_sector_id].trailing_return - cross_section_mean
    _validate_finite_output(value=value, name="relative sector momentum")
    return value


def calculate_top_bottom_sector_spread(
    rows: Iterable[RelativePriceInput | Mapping[str, Any]],
    *,
    window: int,
) -> float:
    """Return top-ranked sector trailing return minus bottom-ranked trailing return."""
    rankings = calculate_sector_return_rankings(rows, window=window)
    if len(rankings) < 2:
        raise ValueError("at least two sector series are required for sector spread")

    value = rankings[0].trailing_return - rankings[-1].trailing_return
    _validate_finite_output(value=value, name="top-bottom sector spread")
    return value


def normalize_relative_price_series(
    rows: Iterable[RelativePriceInput | Mapping[str, Any]],
) -> tuple[RelativePriceInput, ...]:
    """Normalize one entity price series into sorted validated rows."""
    normalized_rows = tuple(_coerce_relative_price_input(row) for row in rows)
    if not normalized_rows:
        raise ValueError("at least one relative price row is required")

    normalized_rows = tuple(sorted(normalized_rows, key=lambda row: row.trade_date))
    _validate_relative_price_series(normalized_rows)
    return normalized_rows


def normalize_entity_return_series(
    rows: Iterable[EntityReturnInput | Mapping[str, Any]],
) -> tuple[EntityReturnInput, ...]:
    """Normalize one entity return series into sorted validated rows."""
    normalized_rows = tuple(_coerce_entity_return_input(row) for row in rows)
    if not normalized_rows:
        raise ValueError("at least one entity return row is required")

    normalized_rows = tuple(sorted(normalized_rows, key=lambda row: row.trade_date))
    _validate_entity_return_series(normalized_rows)
    return normalized_rows


def normalize_member_return_rows(
    rows: Iterable[MemberReturnInput | Mapping[str, Any]],
) -> tuple[MemberReturnInput, ...]:
    """Normalize one-date constituent return rows for breadth calculations."""
    normalized_rows = tuple(_coerce_member_return_input(row) for row in rows)
    if not normalized_rows:
        raise ValueError("at least one member return row is required")

    normalized_rows = tuple(
        sorted(normalized_rows, key=lambda row: (row.trade_date, row.member_id))
    )
    _validate_member_return_rows(normalized_rows)
    return normalized_rows


def _coerce_relative_price_input(
    row: RelativePriceInput | Mapping[str, Any],
) -> RelativePriceInput:
    payload = _row_mapping(row)
    entity_id = payload.get("entity_id")
    market = payload.get("market")
    trade_date_value = payload.get("trade_date")

    if not isinstance(entity_id, str) or entity_id.strip() == "":
        raise ValueError("relative price entity_id must be a non-empty string")
    if not isinstance(market, str) or market.strip() == "":
        raise ValueError("relative price market must be a non-empty string")

    return RelativePriceInput(
        entity_id=entity_id.strip(),
        market=market.strip(),
        trade_date=_coerce_trade_date(trade_date_value, context="relative price"),
        close=_coerce_positive_number(payload.get("close"), field_name="close"),
    )


def _coerce_entity_return_input(
    row: EntityReturnInput | Mapping[str, Any],
) -> EntityReturnInput:
    payload = _row_mapping(row)
    entity_id = payload.get("entity_id")
    market = payload.get("market")
    trade_date_value = payload.get("trade_date")

    if not isinstance(entity_id, str) or entity_id.strip() == "":
        raise ValueError("entity return entity_id must be a non-empty string")
    if not isinstance(market, str) or market.strip() == "":
        raise ValueError("entity return market must be a non-empty string")

    return EntityReturnInput(
        entity_id=entity_id.strip(),
        market=market.strip(),
        trade_date=_coerce_trade_date(trade_date_value, context="entity return"),
        return_value=_coerce_finite_number(
            payload.get("return_value"),
            field_name="return_value",
            context="entity return",
        ),
    )


def _coerce_member_return_input(
    row: MemberReturnInput | Mapping[str, Any],
) -> MemberReturnInput:
    payload = _row_mapping(row)
    universe_id = payload.get("universe_id")
    market = payload.get("market")
    member_id = payload.get("member_id")
    trade_date_value = payload.get("trade_date")

    if not isinstance(universe_id, str) or universe_id.strip() == "":
        raise ValueError("member return universe_id must be a non-empty string")
    if not isinstance(market, str) or market.strip() == "":
        raise ValueError("member return market must be a non-empty string")
    if not isinstance(member_id, str) or member_id.strip() == "":
        raise ValueError("member return member_id must be a non-empty string")

    return MemberReturnInput(
        universe_id=universe_id.strip(),
        market=market.strip(),
        trade_date=_coerce_trade_date(trade_date_value, context="member return"),
        member_id=member_id.strip(),
        return_value=_coerce_finite_number(
            payload.get("return_value"),
            field_name="return_value",
            context="member return",
        ),
    )


def _row_mapping(
    row: RelativePriceInput | EntityReturnInput | MemberReturnInput | Mapping[str, Any],
) -> Mapping[str, Any]:
    if isinstance(row, Mapping):
        return row
    if is_dataclass(row) and not isinstance(row, type):
        return asdict(row)
    raise ValueError("relative feature rows must be mappings or dataclass instances")


def _coerce_trade_date(value: Any, *, context: str) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    raise ValueError(f"{context} trade_date must be a date or datetime instance")


def _coerce_positive_number(value: Any, *, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"relative price {field_name} must be a positive finite number")

    numeric_value = float(value)
    if not isfinite(numeric_value) or numeric_value <= 0.0:
        raise ValueError(f"relative price {field_name} must be a positive finite number")
    return numeric_value


def _coerce_finite_number(
    value: Any,
    *,
    field_name: str,
    context: str,
) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{context} {field_name} must be a finite number")

    numeric_value = float(value)
    if not isfinite(numeric_value):
        raise ValueError(f"{context} {field_name} must be a finite number")
    return numeric_value


def _validate_relative_price_series(rows: tuple[RelativePriceInput, ...]) -> None:
    first_row = rows[0]
    previous_trade_date: date | None = None

    for row in rows:
        if row.entity_id != first_row.entity_id:
            raise ValueError("all relative price rows must share the same entity_id")
        if row.market != first_row.market:
            raise ValueError("all relative price rows must share the same market")
        if previous_trade_date is not None and row.trade_date == previous_trade_date:
            raise ValueError("relative price rows must have unique trade_date values")
        previous_trade_date = row.trade_date


def _validate_entity_return_series(rows: tuple[EntityReturnInput, ...]) -> None:
    first_row = rows[0]
    previous_trade_date: date | None = None

    for row in rows:
        if row.entity_id != first_row.entity_id:
            raise ValueError("all entity return rows must share the same entity_id")
        if row.market != first_row.market:
            raise ValueError("all entity return rows must share the same market")
        if previous_trade_date is not None and row.trade_date == previous_trade_date:
            raise ValueError("entity return rows must have unique trade_date values")
        previous_trade_date = row.trade_date


def _validate_member_return_rows(rows: tuple[MemberReturnInput, ...]) -> None:
    first_row = rows[0]
    seen_member_ids: set[str] = set()

    for row in rows:
        if row.universe_id != first_row.universe_id:
            raise ValueError("all member return rows must share the same universe_id")
        if row.market != first_row.market:
            raise ValueError("all member return rows must share the same market")
        if row.trade_date != first_row.trade_date:
            raise ValueError("all member return rows must share the same trade_date")
        if row.member_id in seen_member_ids:
            raise ValueError("member return rows must have unique member_id values")
        seen_member_ids.add(row.member_id)


def _require_relative_window(window: int) -> None:
    if not isinstance(window, int) or isinstance(window, bool) or window < 2:
        raise ValueError("window must be an integer greater than or equal to 2")


def _require_price_window(
    rows: tuple[RelativePriceInput, ...],
    *,
    window: int,
    context: str,
) -> tuple[RelativePriceInput, ...]:
    _require_relative_window(window)
    if len(rows) < window:
        raise ValueError(f"insufficient rows for requested {context}")
    return rows[-window:]


def _require_return_window(
    rows: tuple[EntityReturnInput, ...],
    *,
    window: int,
    context: str,
) -> tuple[EntityReturnInput, ...]:
    _require_relative_window(window)
    if len(rows) < window:
        raise ValueError(f"insufficient rows for requested {context}")
    return rows[-window:]


def _aligned_price_series(
    left_rows: Iterable[RelativePriceInput | Mapping[str, Any]],
    right_rows: Iterable[RelativePriceInput | Mapping[str, Any]],
    *,
    window: int,
    context: str,
) -> tuple[tuple[RelativePriceInput, ...], tuple[RelativePriceInput, ...]]:
    _require_relative_window(window)
    left_series = normalize_relative_price_series(left_rows)
    right_series = normalize_relative_price_series(right_rows)
    if left_series[0].market != right_series[0].market:
        raise ValueError("relative comparison rows must share the same market")
    common_dates = sorted(
        {row.trade_date for row in left_series} & {row.trade_date for row in right_series}
    )
    if not common_dates:
        raise ValueError("no common trade dates are available for aligned relative calculation")
    if len(common_dates) < window:
        raise ValueError(f"insufficient aligned rows for requested {context}")

    trailing_dates = set(common_dates[-window:])
    left_by_date = {row.trade_date: row for row in left_series if row.trade_date in trailing_dates}
    right_by_date = {
        row.trade_date: row for row in right_series if row.trade_date in trailing_dates
    }
    aligned_dates = tuple(sorted(trailing_dates))
    return (
        tuple(left_by_date[trade_date] for trade_date in aligned_dates),
        tuple(right_by_date[trade_date] for trade_date in aligned_dates),
    )


def _aligned_price_panel(
    rows: Iterable[RelativePriceInput | Mapping[str, Any]],
    *,
    window: int,
) -> dict[str, tuple[RelativePriceInput, ...]]:
    _require_relative_window(window)
    normalized_rows = tuple(_coerce_relative_price_input(row) for row in rows)
    if not normalized_rows:
        raise ValueError("at least one relative price row is required")

    market = normalized_rows[0].market
    panel: dict[str, list[RelativePriceInput]] = {}
    seen_keys: set[tuple[str, date]] = set()
    for row in sorted(normalized_rows, key=lambda item: (item.entity_id, item.trade_date)):
        if row.market != market:
            raise ValueError("all sector rotation rows must share the same market")
        key = (row.entity_id, row.trade_date)
        if key in seen_keys:
            raise ValueError(
                "sector rotation rows must have unique entity_id/trade_date pairs"
            )
        seen_keys.add(key)
        panel.setdefault(row.entity_id, []).append(row)

    if len(panel) < 2:
        raise ValueError("at least two sector series are required for sector rotation calculations")

    common_dates: set[date] | None = None
    normalized_panel: dict[str, tuple[RelativePriceInput, ...]] = {}
    for entity_id, entity_rows in panel.items():
        series = normalize_relative_price_series(entity_rows)
        normalized_panel[entity_id] = series
        entity_dates = {row.trade_date for row in series}
        common_dates = entity_dates if common_dates is None else common_dates & entity_dates

    if not common_dates:
        raise ValueError("no common trade dates are available for sector rotation calculations")
    common_dates = set(sorted(common_dates))
    if len(common_dates) < window:
        raise ValueError("insufficient aligned rows for requested sector rotation window")

    trailing_dates = tuple(sorted(common_dates)[-window:])
    trailing_date_set = set(trailing_dates)
    return {
        entity_id: tuple(
            row for row in series if row.trade_date in trailing_date_set
        )
        for entity_id, series in normalized_panel.items()
    }


def _trailing_return_from_aligned_series(rows: tuple[RelativePriceInput, ...]) -> float:
    value = (rows[-1].close / rows[0].close) - 1.0
    _validate_finite_output(value=value, name="trailing return")
    return value


def _validate_finite_output(*, value: float, name: str) -> None:
    if not isfinite(value):
        raise ValueError(f"{name} produced a non-finite output")
