"""Deterministic offline starter strategies for StrategyLab research baselines."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from hashlib import sha256
import json
from math import isfinite
from typing import Any, Iterable, Mapping

from .contracts import (
    ParameterDefinition,
    ParameterType,
    SignalIntent,
    StrategyDefinition,
)


PARAMETER_SET_SCHEMA_VERSION = "1.0.0"


class StrategyRuleError(ValueError):
    """Controlled error raised for invalid starter-strategy inputs or config."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


@dataclass(frozen=True)
class StrategyParameterValue:
    """One normalized starter-strategy parameter value."""

    name: str
    value: str | int | float | bool


@dataclass(frozen=True)
class ResolvedStrategyParameters:
    """Validated parameter values plus deterministic starter-strategy identity."""

    strategy_id: str
    strategy_version: str
    parameter_set_version: str
    parameter_set_id: str
    parameters: tuple[StrategyParameterValue, ...]

    def as_mapping(self) -> dict[str, str | int | float | bool]:
        return {parameter.name: parameter.value for parameter in self.parameters}


@dataclass(frozen=True)
class StrategySignal:
    """Deterministic offline strategy output suitable for replay preparation."""

    signal_id: str
    strategy_id: str
    strategy_version: str
    parameter_set_version: str
    parameter_set_id: str
    symbol: str
    trade_date: str
    intent: str
    signal_value: float
    reason: str


@dataclass(frozen=True)
class StrategyEvaluationResult:
    """Starter-strategy evaluation output over caller-provided rows."""

    strategy_definition: StrategyDefinition
    resolved_parameters: ResolvedStrategyParameters
    signals: tuple[StrategySignal, ...]


@dataclass(frozen=True)
class _NormalizedRow:
    symbol: str
    trade_date: str
    values: dict[str, float]


@dataclass(frozen=True)
class _StarterStrategySpec:
    definition: StrategyDefinition


_STARTER_STRATEGIES: tuple[_StarterStrategySpec, ...] = (
    _StarterStrategySpec(
        definition=StrategyDefinition(
            strategy_id="ma_crossover_long",
            strategy_name="Moving Average Crossover Long",
            strategy_version="1.0.0",
            input_features=("close", "fast_ma", "slow_ma"),
            parameters=(
                ParameterDefinition(
                    name="entry_buffer",
                    parameter_type=ParameterType.FLOAT,
                    default=0.0,
                    min_value=0.0,
                    max_value=10.0,
                ),
                ParameterDefinition(
                    name="exit_buffer",
                    parameter_type=ParameterType.FLOAT,
                    default=0.0,
                    min_value=0.0,
                    max_value=10.0,
                ),
            ),
            output_intent=SignalIntent.ENTRY_EXIT,
            signal_kind="dated_trade_intent",
        )
    ),
    _StarterStrategySpec(
        definition=StrategyDefinition(
            strategy_id="rsi_mean_reversion_long",
            strategy_name="RSI Mean Reversion Long",
            strategy_version="1.0.0",
            input_features=("close", "rsi_14"),
            parameters=(
                ParameterDefinition(
                    name="entry_rsi_max",
                    parameter_type=ParameterType.FLOAT,
                    default=30.0,
                    min_value=1.0,
                    max_value=50.0,
                ),
                ParameterDefinition(
                    name="exit_rsi_min",
                    parameter_type=ParameterType.FLOAT,
                    default=55.0,
                    min_value=30.0,
                    max_value=99.0,
                ),
            ),
            output_intent=SignalIntent.ENTRY_EXIT,
            signal_kind="dated_trade_intent",
        )
    ),
)

_STRATEGY_SPECS_BY_ID = {
    spec.definition.strategy_id: spec for spec in _STARTER_STRATEGIES
}


def list_starter_strategies() -> tuple[StrategyDefinition, ...]:
    """Return stable starter-strategy definitions in deterministic order."""
    return tuple(spec.definition for spec in _STARTER_STRATEGIES)


def get_starter_strategy_definition(strategy_id: str) -> StrategyDefinition:
    """Return one starter-strategy definition or raise a controlled error."""
    spec = _STRATEGY_SPECS_BY_ID.get(strategy_id)
    if spec is None:
        raise StrategyRuleError(
            "unsupported_strategy_id",
            f"unsupported starter strategy id: {strategy_id!r}",
        )
    return spec.definition


def resolve_strategy_parameters(
    strategy_id: str,
    parameter_overrides: Mapping[str, Any] | None = None,
    *,
    parameter_set_version: str = PARAMETER_SET_SCHEMA_VERSION,
) -> ResolvedStrategyParameters:
    """Validate parameter overrides and return deterministic normalized values."""
    strategy_definition = get_starter_strategy_definition(strategy_id)
    if not isinstance(parameter_set_version, str) or parameter_set_version.strip() == "":
        raise StrategyRuleError(
            "invalid_parameter_set_version",
            "parameter_set_version must be a non-empty string",
        )
    if parameter_overrides is not None and not isinstance(parameter_overrides, Mapping):
        raise StrategyRuleError(
            "invalid_parameter_overrides",
            "parameter_overrides must be a mapping when provided",
        )

    overrides = dict(parameter_overrides or {})
    known_names = {parameter.name for parameter in strategy_definition.parameters}
    unknown_names = sorted(name for name in overrides if name not in known_names)
    if unknown_names:
        raise StrategyRuleError(
            "unknown_parameter",
            f"unknown strategy parameter override(s): {', '.join(unknown_names)}",
        )

    normalized_parameters: list[StrategyParameterValue] = []
    for parameter in strategy_definition.parameters:
        raw_value = overrides.get(parameter.name, parameter.default)
        normalized_value = _normalize_parameter_value(parameter, raw_value)
        normalized_parameters.append(
            StrategyParameterValue(name=parameter.name, value=normalized_value)
        )

    parameter_set_id = _build_parameter_set_id(
        strategy_id=strategy_definition.strategy_id,
        strategy_version=strategy_definition.strategy_version,
        parameter_set_version=parameter_set_version,
        parameters=normalized_parameters,
    )
    return ResolvedStrategyParameters(
        strategy_id=strategy_definition.strategy_id,
        strategy_version=strategy_definition.strategy_version,
        parameter_set_version=parameter_set_version.strip(),
        parameter_set_id=parameter_set_id,
        parameters=tuple(normalized_parameters),
    )


def evaluate_starter_strategy(
    strategy_id: str,
    rows: Iterable[Mapping[str, Any]],
    parameter_overrides: Mapping[str, Any] | None = None,
    *,
    parameter_set_version: str = PARAMETER_SET_SCHEMA_VERSION,
) -> StrategyEvaluationResult:
    """Evaluate one starter strategy over caller-provided ordered rows only."""
    strategy_definition = get_starter_strategy_definition(strategy_id)
    resolved_parameters = resolve_strategy_parameters(
        strategy_id,
        parameter_overrides,
        parameter_set_version=parameter_set_version,
    )
    normalized_rows = _normalize_rows(strategy_definition, rows)

    if strategy_id == "ma_crossover_long":
        signals = _evaluate_ma_crossover(normalized_rows, resolved_parameters)
    elif strategy_id == "rsi_mean_reversion_long":
        signals = _evaluate_rsi_mean_reversion(normalized_rows, resolved_parameters)
    else:
        raise StrategyRuleError(
            "unsupported_strategy_id",
            f"unsupported starter strategy id: {strategy_id!r}",
        )

    return StrategyEvaluationResult(
        strategy_definition=strategy_definition,
        resolved_parameters=resolved_parameters,
        signals=tuple(signals),
    )


def _normalize_rows(
    strategy_definition: StrategyDefinition,
    rows: Iterable[Mapping[str, Any]],
) -> tuple[_NormalizedRow, ...]:
    materialized_rows = tuple(rows)
    if not materialized_rows:
        raise StrategyRuleError("empty_input", "strategy evaluation requires at least one row")

    normalized_rows: list[_NormalizedRow] = []
    seen_symbol_dates: set[tuple[str, str]] = set()
    last_trade_date_by_symbol: dict[str, str] = {}
    required_fields = ("symbol", "trade_date", *strategy_definition.input_features)

    for index, row in enumerate(materialized_rows):
        if not isinstance(row, Mapping):
            raise StrategyRuleError(
                "invalid_row_type",
                f"row {index} must be a mapping of strategy inputs",
            )

        missing_fields = [field_name for field_name in required_fields if field_name not in row]
        if missing_fields:
            raise StrategyRuleError(
                "missing_required_input",
                f"row {index} is missing required fields: {', '.join(missing_fields)}",
            )

        symbol = row["symbol"]
        trade_date = row["trade_date"]
        if not isinstance(symbol, str) or symbol.strip() == "":
            raise StrategyRuleError(
                "invalid_symbol",
                f"row {index} has an empty symbol",
            )
        if not _is_iso_date(trade_date):
            raise StrategyRuleError(
                "invalid_trade_date",
                f"row {index} trade_date must be an ISO date string",
            )

        normalized_symbol = symbol.strip()
        normalized_trade_date = trade_date
        symbol_date = (normalized_symbol, normalized_trade_date)
        if symbol_date in seen_symbol_dates:
            raise StrategyRuleError(
                "duplicate_trade_date",
                f"duplicate trade_date for symbol {normalized_symbol}: {normalized_trade_date}",
            )
        prior_trade_date = last_trade_date_by_symbol.get(normalized_symbol)
        if prior_trade_date is not None and normalized_trade_date <= prior_trade_date:
            raise StrategyRuleError(
                "unsorted_trade_dates",
                f"rows for {normalized_symbol} must be strictly increasing by trade_date",
            )
        seen_symbol_dates.add(symbol_date)
        last_trade_date_by_symbol[normalized_symbol] = normalized_trade_date

        values: dict[str, float] = {}
        for feature_name in strategy_definition.input_features:
            values[feature_name] = _coerce_row_number(
                row=row,
                row_index=index,
                field_name=feature_name,
            )

        normalized_rows.append(
            _NormalizedRow(
                symbol=normalized_symbol,
                trade_date=normalized_trade_date,
                values=values,
            )
        )

    return tuple(normalized_rows)


def _evaluate_ma_crossover(
    rows: tuple[_NormalizedRow, ...],
    resolved_parameters: ResolvedStrategyParameters,
) -> tuple[StrategySignal, ...]:
    parameter_map = resolved_parameters.as_mapping()
    entry_buffer = float(parameter_map["entry_buffer"])
    exit_buffer = float(parameter_map["exit_buffer"])
    signals: list[StrategySignal] = []

    for symbol_rows in _group_rows_by_symbol(rows).values():
        for previous_row, current_row in zip(symbol_rows, symbol_rows[1:]):
            previous_spread = previous_row.values["fast_ma"] - previous_row.values["slow_ma"]
            current_spread = current_row.values["fast_ma"] - current_row.values["slow_ma"]

            if previous_spread <= entry_buffer and current_spread > entry_buffer:
                signals.append(
                    _build_signal(
                        resolved_parameters=resolved_parameters,
                        symbol=current_row.symbol,
                        trade_date=current_row.trade_date,
                        intent="enter_long",
                        signal_value=current_spread,
                        reason="fast_ma crossed above slow_ma",
                    )
                )
            elif previous_spread >= -exit_buffer and current_spread < -exit_buffer:
                signals.append(
                    _build_signal(
                        resolved_parameters=resolved_parameters,
                        symbol=current_row.symbol,
                        trade_date=current_row.trade_date,
                        intent="exit_long",
                        signal_value=current_spread,
                        reason="fast_ma crossed below slow_ma",
                    )
                )

    return tuple(signals)


def _evaluate_rsi_mean_reversion(
    rows: tuple[_NormalizedRow, ...],
    resolved_parameters: ResolvedStrategyParameters,
) -> tuple[StrategySignal, ...]:
    parameter_map = resolved_parameters.as_mapping()
    entry_rsi_max = float(parameter_map["entry_rsi_max"])
    exit_rsi_min = float(parameter_map["exit_rsi_min"])
    signals: list[StrategySignal] = []

    for row in rows:
        rsi_value = row.values["rsi_14"]
        if rsi_value <= entry_rsi_max:
            signals.append(
                _build_signal(
                    resolved_parameters=resolved_parameters,
                    symbol=row.symbol,
                    trade_date=row.trade_date,
                    intent="enter_long",
                    signal_value=entry_rsi_max - rsi_value,
                    reason="rsi_14 is below the configured mean-reversion entry threshold",
                )
            )
        elif rsi_value >= exit_rsi_min:
            signals.append(
                _build_signal(
                    resolved_parameters=resolved_parameters,
                    symbol=row.symbol,
                    trade_date=row.trade_date,
                    intent="exit_long",
                    signal_value=rsi_value - exit_rsi_min,
                    reason="rsi_14 is above the configured mean-reversion exit threshold",
                )
            )

    return tuple(signals)


def _group_rows_by_symbol(
    rows: tuple[_NormalizedRow, ...],
) -> dict[str, list[_NormalizedRow]]:
    grouped: dict[str, list[_NormalizedRow]] = {}
    for row in rows:
        grouped.setdefault(row.symbol, []).append(row)
    return grouped


def _build_signal(
    *,
    resolved_parameters: ResolvedStrategyParameters,
    symbol: str,
    trade_date: str,
    intent: str,
    signal_value: float,
    reason: str,
) -> StrategySignal:
    signal_id = sha256(
        json.dumps(
            {
                "strategy_id": resolved_parameters.strategy_id,
                "strategy_version": resolved_parameters.strategy_version,
                "parameter_set_id": resolved_parameters.parameter_set_id,
                "symbol": symbol,
                "trade_date": trade_date,
                "intent": intent,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    return StrategySignal(
        signal_id=signal_id,
        strategy_id=resolved_parameters.strategy_id,
        strategy_version=resolved_parameters.strategy_version,
        parameter_set_version=resolved_parameters.parameter_set_version,
        parameter_set_id=resolved_parameters.parameter_set_id,
        symbol=symbol,
        trade_date=trade_date,
        intent=intent,
        signal_value=float(signal_value),
        reason=reason,
    )


def _build_parameter_set_id(
    *,
    strategy_id: str,
    strategy_version: str,
    parameter_set_version: str,
    parameters: list[StrategyParameterValue],
) -> str:
    payload = {
        "strategy_id": strategy_id,
        "strategy_version": strategy_version,
        "parameter_set_version": parameter_set_version.strip(),
        "parameters": [
            {"name": parameter.name, "value": parameter.value}
            for parameter in parameters
        ],
    }
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _normalize_parameter_value(
    definition: ParameterDefinition,
    value: Any,
) -> str | int | float | bool:
    if value is None:
        raise StrategyRuleError(
            "missing_parameter_value",
            f"parameter {definition.name!r} requires a value",
        )

    if definition.parameter_type is ParameterType.INTEGER:
        if not isinstance(value, int) or isinstance(value, bool):
            raise StrategyRuleError(
                "invalid_parameter_type",
                f"parameter {definition.name!r} must be an integer",
            )
        normalized: str | int | float | bool = value
    elif definition.parameter_type is ParameterType.FLOAT:
        if not isinstance(value, (int, float)) or isinstance(value, bool) or not isfinite(value):
            raise StrategyRuleError(
                "invalid_parameter_type",
                f"parameter {definition.name!r} must be a finite float",
            )
        normalized = float(value)
    elif definition.parameter_type is ParameterType.STRING:
        if not isinstance(value, str) or value.strip() == "":
            raise StrategyRuleError(
                "invalid_parameter_type",
                f"parameter {definition.name!r} must be a non-empty string",
            )
        normalized = value.strip()
    elif definition.parameter_type is ParameterType.BOOLEAN:
        if not isinstance(value, bool):
            raise StrategyRuleError(
                "invalid_parameter_type",
                f"parameter {definition.name!r} must be a boolean",
            )
        normalized = value
    else:
        raise StrategyRuleError(
            "unsupported_parameter_type",
            f"unsupported parameter type for {definition.name!r}",
        )

    if definition.min_value is not None and normalized < definition.min_value:
        raise StrategyRuleError(
            "parameter_below_min",
            f"parameter {definition.name!r} must be >= {definition.min_value}",
        )
    if definition.max_value is not None and normalized > definition.max_value:
        raise StrategyRuleError(
            "parameter_above_max",
            f"parameter {definition.name!r} must be <= {definition.max_value}",
        )
    if definition.choices and normalized not in definition.choices:
        raise StrategyRuleError(
            "parameter_choice_violation",
            f"parameter {definition.name!r} must be one of {definition.choices!r}",
        )
    return normalized


def _coerce_row_number(
    *,
    row: Mapping[str, Any],
    row_index: int,
    field_name: str,
) -> float:
    value = row[field_name]
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not isfinite(value):
        raise StrategyRuleError(
            "invalid_input_value",
            f"row {row_index} field {field_name!r} must be a finite number",
        )
    return float(value)


def _is_iso_date(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


__all__ = [
    "PARAMETER_SET_SCHEMA_VERSION",
    "ResolvedStrategyParameters",
    "StrategyEvaluationResult",
    "StrategyParameterValue",
    "StrategyRuleError",
    "StrategySignal",
    "evaluate_starter_strategy",
    "get_starter_strategy_definition",
    "list_starter_strategies",
    "resolve_strategy_parameters",
]
