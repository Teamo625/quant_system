"""Repeatable offline experiment configuration for StrategyLab and BacktestEngine."""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from hashlib import sha256
import json
from typing import Any, Mapping

from quant.strategies import (
    StrategyRuleError,
    get_starter_strategy_definition,
    resolve_strategy_parameters,
)

from .contracts import (
    BACKTEST_CONTRACT_SCHEMA_VERSION,
    BacktestRequest,
    SelectionReference,
    StrategyReference,
    validate_backtest_request,
)


EXPERIMENT_CONFIG_SCHEMA_VERSION = "1.0.0"

EXPERIMENT_PARAMETER_FIELDS: tuple[str, ...] = ("name", "value")
REPEATABLE_EXPERIMENT_CONFIG_FIELDS: tuple[str, ...] = (
    "experiment_id",
    "strategy_ref",
    "parameter_set_version",
    "parameter_set_id",
    "parameters",
    "selection_ref",
    "start_trade_date",
    "end_trade_date",
    "starting_capital",
    "transaction_cost_bps",
    "slippage_bps",
    "schema_version",
)


class ExperimentConfigError(ValueError):
    """Controlled error raised for invalid repeatable experiment configuration."""

    def __init__(self, issues: tuple["ExperimentConfigIssue", ...]) -> None:
        message = "; ".join(
            f"{issue.field}:{issue.code}" for issue in issues
        ) or "invalid repeatable experiment configuration"
        super().__init__(message)
        self.issues = issues


@dataclass(frozen=True)
class ExperimentConfigIssue:
    """Structured validation issue for deterministic experiment tests."""

    field: str
    code: str
    message: str


@dataclass(frozen=True)
class ExperimentParameterValue:
    """One serialization-friendly validated parameter value."""

    name: str
    value: str | int | float | bool


@dataclass(frozen=True)
class RepeatableExperimentConfig:
    """Normalized offline experiment configuration with deterministic identity."""

    experiment_id: str
    strategy_ref: StrategyReference
    parameter_set_version: str
    parameter_set_id: str
    parameters: tuple[ExperimentParameterValue, ...]
    selection_ref: SelectionReference
    start_trade_date: str
    end_trade_date: str
    starting_capital: float
    transaction_cost_bps: float
    slippage_bps: float
    schema_version: str = EXPERIMENT_CONFIG_SCHEMA_VERSION

    def to_normalized_mapping(self) -> dict[str, Any]:
        return normalize_repeatable_experiment_config(self)

    def to_backtest_request(self) -> BacktestRequest:
        return BacktestRequest(
            request_id=self.experiment_id,
            strategy_ref=self.strategy_ref,
            selection_ref=self.selection_ref,
            start_trade_date=self.start_trade_date,
            end_trade_date=self.end_trade_date,
            starting_capital=self.starting_capital,
            transaction_cost_bps=self.transaction_cost_bps,
            slippage_bps=self.slippage_bps,
            schema_version=BACKTEST_CONTRACT_SCHEMA_VERSION,
        )


def build_repeatable_experiment_config(
    *,
    strategy_id: str,
    selection_ref: SelectionReference,
    start_trade_date: str,
    end_trade_date: str,
    starting_capital: float,
    transaction_cost_bps: float = 0.0,
    slippage_bps: float = 0.0,
    parameter_overrides: Mapping[str, Any] | None = None,
    parameter_set_version: str = "1.0.0",
) -> RepeatableExperimentConfig:
    """Build one deterministic experiment configuration from local metadata only."""
    strategy_definition = get_starter_strategy_definition(strategy_id)
    try:
        resolved_parameters = resolve_strategy_parameters(
            strategy_id,
            parameter_overrides,
            parameter_set_version=parameter_set_version,
        )
    except StrategyRuleError as exc:
        raise ExperimentConfigError(
            (
                ExperimentConfigIssue(
                    field="parameters",
                    code=exc.code,
                    message=exc.message,
                ),
            )
        ) from exc

    parameters = tuple(
        ExperimentParameterValue(name=parameter.name, value=parameter.value)
        for parameter in resolved_parameters.parameters
    )
    strategy_ref = StrategyReference(
        strategy_id=strategy_definition.strategy_id,
        strategy_version=strategy_definition.strategy_version,
    )
    config_without_id = {
        "strategy_ref": {
            "strategy_id": strategy_ref.strategy_id,
            "strategy_version": strategy_ref.strategy_version,
        },
        "parameter_set_version": resolved_parameters.parameter_set_version,
        "parameter_set_id": resolved_parameters.parameter_set_id,
        "parameters": [
            {"name": parameter.name, "value": parameter.value}
            for parameter in parameters
        ],
        "selection_ref": {
            "reference_kind": selection_ref.reference_kind.value
            if hasattr(selection_ref.reference_kind, "value")
            else selection_ref.reference_kind,
            "reference_id": selection_ref.reference_id,
            "reference_date": selection_ref.reference_date,
            "market": selection_ref.market,
        },
        "start_trade_date": start_trade_date,
        "end_trade_date": end_trade_date,
        "starting_capital": starting_capital,
        "transaction_cost_bps": transaction_cost_bps,
        "slippage_bps": slippage_bps,
        "schema_version": EXPERIMENT_CONFIG_SCHEMA_VERSION,
    }
    experiment_id = _build_experiment_id(config_without_id)
    config = RepeatableExperimentConfig(
        experiment_id=experiment_id,
        strategy_ref=strategy_ref,
        parameter_set_version=resolved_parameters.parameter_set_version,
        parameter_set_id=resolved_parameters.parameter_set_id,
        parameters=parameters,
        selection_ref=selection_ref,
        start_trade_date=start_trade_date,
        end_trade_date=end_trade_date,
        starting_capital=float(starting_capital),
        transaction_cost_bps=float(transaction_cost_bps),
        slippage_bps=float(slippage_bps),
        schema_version=EXPERIMENT_CONFIG_SCHEMA_VERSION,
    )
    issues = validate_repeatable_experiment_config(config)
    if issues:
        raise ExperimentConfigError(issues)
    return config


def normalize_repeatable_experiment_config(
    payload: RepeatableExperimentConfig | Mapping[str, Any],
) -> dict[str, Any]:
    """Return a deterministic serialization-friendly experiment mapping."""
    record = _record_mapping(payload)
    parameters = tuple(record.get("parameters", ()))
    return {
        "experiment_id": record.get("experiment_id"),
        "strategy_ref": _normalize_nested_mapping(record.get("strategy_ref")),
        "parameter_set_version": record.get("parameter_set_version"),
        "parameter_set_id": record.get("parameter_set_id"),
        "parameters": [
            {
                "name": parameter.get("name"),
                "value": parameter.get("value"),
            }
            for parameter in sorted(
                (_record_mapping(parameter) for parameter in parameters),
                key=lambda item: item.get("name", ""),
            )
        ],
        "selection_ref": _normalize_nested_mapping(record.get("selection_ref")),
        "start_trade_date": record.get("start_trade_date"),
        "end_trade_date": record.get("end_trade_date"),
        "starting_capital": record.get("starting_capital"),
        "transaction_cost_bps": record.get("transaction_cost_bps"),
        "slippage_bps": record.get("slippage_bps"),
        "schema_version": record.get("schema_version"),
    }


def validate_repeatable_experiment_config(
    payload: RepeatableExperimentConfig | Mapping[str, Any],
) -> tuple[ExperimentConfigIssue, ...]:
    """Return deterministic validation issues for one repeatable experiment."""
    record = _record_mapping(payload)
    issues: list[ExperimentConfigIssue] = []
    issues.extend(_validate_expected_fields(record, REPEATABLE_EXPERIMENT_CONFIG_FIELDS))

    request_issues = validate_backtest_request(
        {
            "request_id": record.get("experiment_id"),
            "strategy_ref": record.get("strategy_ref"),
            "selection_ref": record.get("selection_ref"),
            "start_trade_date": record.get("start_trade_date"),
            "end_trade_date": record.get("end_trade_date"),
            "starting_capital": record.get("starting_capital"),
            "transaction_cost_bps": record.get("transaction_cost_bps"),
            "slippage_bps": record.get("slippage_bps"),
            "schema_version": BACKTEST_CONTRACT_SCHEMA_VERSION,
        }
    )
    for issue in request_issues:
        normalized_field = "experiment_id" if issue.field == "request_id" else issue.field
        issues.append(
            ExperimentConfigIssue(
                field=normalized_field,
                code=issue.code,
                message=issue.message,
            )
        )

    if "parameter_set_version" not in record or record["parameter_set_version"] is None:
        issues.append(_missing_required("parameter_set_version"))
    elif not _is_nonempty_text(record["parameter_set_version"]):
        issues.append(
            ExperimentConfigIssue(
                field="parameter_set_version",
                code="empty_text",
                message="parameter_set_version must be a non-empty string",
            )
        )

    if "parameter_set_id" not in record or record["parameter_set_id"] is None:
        issues.append(_missing_required("parameter_set_id"))
    elif not _is_nonempty_text(record["parameter_set_id"]):
        issues.append(
            ExperimentConfigIssue(
                field="parameter_set_id",
                code="empty_text",
                message="parameter_set_id must be a non-empty string",
            )
        )

    if "parameters" not in record or record["parameters"] is None:
        issues.append(_missing_required("parameters"))
    else:
        issues.extend(_validate_parameter_values(record["parameters"], record))

    if "schema_version" in record and record["schema_version"] != EXPERIMENT_CONFIG_SCHEMA_VERSION:
        issues.append(
            ExperimentConfigIssue(
                field="schema_version",
                code="unsupported_schema_version",
                message="schema_version must match the repeatable experiment contract schema",
            )
        )

    return tuple(issues)


def _validate_parameter_values(
    payload: Any,
    root_record: Mapping[str, Any],
) -> list[ExperimentConfigIssue]:
    if not isinstance(payload, (list, tuple)) or isinstance(payload, str):
        return [
            ExperimentConfigIssue(
                field="parameters",
                code="invalid_type",
                message="parameters must be a sequence of name/value records",
            )
        ]

    issues: list[ExperimentConfigIssue] = []
    parameter_records = tuple(_record_mapping(parameter) for parameter in payload)
    seen_names: set[str] = set()

    for index, parameter in enumerate(parameter_records):
        issues.extend(
            _prefix_issues(
                _validate_expected_fields(parameter, EXPERIMENT_PARAMETER_FIELDS),
                prefix=f"parameters[{index}]",
            )
        )
        if "name" not in parameter or parameter["name"] is None:
            issues.append(_prefixed_missing_required(f"parameters[{index}]", "name"))
            continue
        if not _is_nonempty_text(parameter["name"]):
            issues.append(
                ExperimentConfigIssue(
                    field=f"parameters[{index}].name",
                    code="empty_text",
                    message="parameter name must be a non-empty string",
                )
            )
            continue
        normalized_name = parameter["name"].strip()
        if normalized_name in seen_names:
            issues.append(
                ExperimentConfigIssue(
                    field=f"parameters[{index}].name",
                    code="duplicate_parameter_name",
                    message="parameter names must be unique",
                )
            )
        else:
            seen_names.add(normalized_name)

    strategy_ref = _record_mapping(root_record.get("strategy_ref"))
    strategy_id = strategy_ref.get("strategy_id")
    if not _is_nonempty_text(strategy_id):
        return issues

    try:
        strategy_definition = get_starter_strategy_definition(strategy_id.strip())
    except StrategyRuleError:
        issues.append(
            ExperimentConfigIssue(
                field="strategy_ref.strategy_id",
                code="unsupported_strategy_id",
                message="strategy_ref.strategy_id must reference a supported starter strategy",
            )
        )
        return issues

    if strategy_ref.get("strategy_version") != strategy_definition.strategy_version:
        issues.append(
            ExperimentConfigIssue(
                field="strategy_ref.strategy_version",
                code="strategy_version_mismatch",
                message="strategy_ref.strategy_version must match the starter strategy definition",
            )
        )
        return issues

    overrides = {
        parameter["name"].strip(): parameter.get("value")
        for parameter in parameter_records
        if _is_nonempty_text(parameter.get("name"))
    }
    expected_parameter_names = [parameter.name for parameter in strategy_definition.parameters]
    provided_parameter_names = sorted(overrides)
    if sorted(expected_parameter_names) != provided_parameter_names:
        missing = sorted(set(expected_parameter_names) - set(provided_parameter_names))
        unknown = sorted(set(provided_parameter_names) - set(expected_parameter_names))
        if missing:
            issues.append(
                ExperimentConfigIssue(
                    field="parameters",
                    code="missing_parameter",
                    message=f"missing required parameter(s): {', '.join(missing)}",
                )
            )
        if unknown:
            issues.append(
                ExperimentConfigIssue(
                    field="parameters",
                    code="unknown_parameter",
                    message=f"unknown parameter(s): {', '.join(unknown)}",
                )
            )
        return issues

    try:
        resolved_parameters = resolve_strategy_parameters(
            strategy_id.strip(),
            overrides,
            parameter_set_version=root_record.get("parameter_set_version") or "",
        )
    except StrategyRuleError as exc:
        issues.append(
            ExperimentConfigIssue(
                field="parameters",
                code=exc.code,
                message=exc.message,
            )
        )
        return issues

    expected_parameter_set_id = resolved_parameters.parameter_set_id
    if root_record.get("parameter_set_id") != expected_parameter_set_id:
        issues.append(
            ExperimentConfigIssue(
                field="parameter_set_id",
                code="parameter_set_id_mismatch",
                message="parameter_set_id must match the normalized strategy parameters",
            )
        )
    return issues


def _build_experiment_id(payload: Mapping[str, Any]) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _validate_expected_fields(
    record: Mapping[str, Any],
    allowed_fields: tuple[str, ...],
) -> list[ExperimentConfigIssue]:
    allowed = set(allowed_fields)
    return [
        ExperimentConfigIssue(
            field=field_name,
            code="unexpected_field",
            message=f"{field_name} is not part of this contract",
        )
        for field_name in record
        if field_name not in allowed
    ]


def _normalize_nested_mapping(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    record = _record_mapping(value)
    return dict(record)


def _record_mapping(payload: Any) -> Mapping[str, Any]:
    if isinstance(payload, Mapping):
        return payload
    if is_dataclass(payload):
        return asdict(payload)
    return {}


def _prefix_issues(
    issues: list[ExperimentConfigIssue],
    *,
    prefix: str,
) -> list[ExperimentConfigIssue]:
    return [
        ExperimentConfigIssue(
            field=f"{prefix}.{issue.field}",
            code=issue.code,
            message=issue.message,
        )
        for issue in issues
    ]


def _prefixed_missing_required(prefix: str, field_name: str) -> ExperimentConfigIssue:
    return ExperimentConfigIssue(
        field=f"{prefix}.{field_name}",
        code="missing_required",
        message=f"{field_name} is required",
    )


def _missing_required(field_name: str) -> ExperimentConfigIssue:
    return ExperimentConfigIssue(
        field=field_name,
        code="missing_required",
        message=f"{field_name} is required",
    )


def _is_nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


__all__ = [
    "EXPERIMENT_CONFIG_SCHEMA_VERSION",
    "EXPERIMENT_PARAMETER_FIELDS",
    "REPEATABLE_EXPERIMENT_CONFIG_FIELDS",
    "ExperimentConfigError",
    "ExperimentConfigIssue",
    "ExperimentParameterValue",
    "RepeatableExperimentConfig",
    "build_repeatable_experiment_config",
    "normalize_repeatable_experiment_config",
    "validate_repeatable_experiment_config",
]
