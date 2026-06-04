"""Offline-safe StrategyLab foundation contracts."""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from enum import Enum
from math import isfinite
from typing import Any, Mapping


STRATEGY_CONTRACT_SCHEMA_VERSION = "1.0.0"

PARAMETER_DEFINITION_FIELDS: tuple[str, ...] = (
    "name",
    "parameter_type",
    "default",
    "min_value",
    "max_value",
    "choices",
)
STRATEGY_DEFINITION_FIELDS: tuple[str, ...] = (
    "strategy_id",
    "strategy_name",
    "strategy_version",
    "input_features",
    "parameters",
    "output_intent",
    "signal_kind",
    "schema_version",
)


class ParameterType(str, Enum):
    """Supported declarative parameter types."""

    INTEGER = "integer"
    FLOAT = "float"
    STRING = "string"
    BOOLEAN = "boolean"


class SignalIntent(str, Enum):
    """Supported declarative output intents."""

    ENTRY = "entry_signal"
    EXIT = "exit_signal"
    SCORE = "score_series"
    LABEL = "label_series"


@dataclass(frozen=True)
class StrategyContractIssue:
    """Structured validation issue for deterministic StrategyLab tests."""

    field: str
    code: str
    message: str


@dataclass(frozen=True)
class ParameterDefinition:
    """Declarative strategy parameter metadata with no execution behavior."""

    name: str
    parameter_type: ParameterType
    default: str | int | float | bool | None = None
    min_value: int | float | None = None
    max_value: int | float | None = None
    choices: tuple[str | int | float | bool, ...] = ()


@dataclass(frozen=True)
class StrategyDefinition:
    """Offline-safe strategy research definition contract."""

    strategy_id: str
    strategy_name: str
    strategy_version: str
    input_features: tuple[str, ...]
    parameters: tuple[ParameterDefinition, ...]
    output_intent: SignalIntent
    signal_kind: str
    schema_version: str = STRATEGY_CONTRACT_SCHEMA_VERSION


def validate_parameter_definition(
    payload: ParameterDefinition | Mapping[str, Any],
) -> tuple[StrategyContractIssue, ...]:
    """Return deterministic validation issues for one parameter declaration."""
    record = _record_mapping(payload)
    issues: list[StrategyContractIssue] = []

    issues.extend(_validate_expected_fields(record, PARAMETER_DEFINITION_FIELDS))
    issues.extend(_validate_required_nonempty_texts(record, ("name",)))

    parameter_type = _coerce_parameter_type(record.get("parameter_type"))
    if "parameter_type" not in record or record["parameter_type"] is None:
        issues.append(_missing_required("parameter_type"))
    elif parameter_type is None:
        issues.append(
            StrategyContractIssue(
                field="parameter_type",
                code="unsupported_parameter_type",
                message="parameter_type must be a supported ParameterType value",
            )
        )
        return tuple(issues)

    issues.extend(
        _validate_parameter_constraints(
            parameter_type=parameter_type,
            default=record.get("default"),
            min_value=record.get("min_value"),
            max_value=record.get("max_value"),
            choices=record.get("choices"),
        )
    )
    return tuple(issues)


def validate_strategy_definition(
    payload: StrategyDefinition | Mapping[str, Any],
) -> tuple[StrategyContractIssue, ...]:
    """Return deterministic validation issues for one strategy declaration."""
    record = _record_mapping(payload)
    issues: list[StrategyContractIssue] = []

    issues.extend(_validate_expected_fields(record, STRATEGY_DEFINITION_FIELDS))
    issues.extend(
        _validate_required_nonempty_texts(
            record,
            (
                "strategy_id",
                "strategy_name",
                "strategy_version",
                "signal_kind",
            ),
        )
    )

    if "input_features" not in record or record["input_features"] is None:
        issues.append(_missing_required("input_features"))
    else:
        issues.extend(
            _validate_text_sequence(
                record["input_features"],
                field_name="input_features",
                duplicate_code="duplicate_feature_name",
            )
        )

    if "parameters" not in record or record["parameters"] is None:
        issues.append(_missing_required("parameters"))
    else:
        issues.extend(_validate_parameter_sequence(record["parameters"]))

    if "output_intent" not in record or record["output_intent"] is None:
        issues.append(_missing_required("output_intent"))
    elif _coerce_signal_intent(record["output_intent"]) is None:
        issues.append(
            StrategyContractIssue(
                field="output_intent",
                code="unsupported_output_intent",
                message="output_intent must be a supported SignalIntent value",
            )
        )

    if "schema_version" in record and record["schema_version"] != STRATEGY_CONTRACT_SCHEMA_VERSION:
        issues.append(
            StrategyContractIssue(
                field="schema_version",
                code="unsupported_schema_version",
                message="schema_version must match the StrategyLab contract schema",
            )
        )

    return tuple(issues)


def _validate_parameter_sequence(payload: Any) -> list[StrategyContractIssue]:
    if not isinstance(payload, (list, tuple)):
        return [
            StrategyContractIssue(
                field="parameters",
                code="invalid_type",
                message="parameters must be a sequence of parameter definitions",
            )
        ]

    issues: list[StrategyContractIssue] = []
    seen_names: set[str] = set()
    for index, item in enumerate(payload):
        for issue in validate_parameter_definition(item):
            issues.append(_prefix_issue(issue, prefix=f"parameters[{index}]"))

        item_record = _record_mapping(item)
        name = item_record.get("name")
        if not _is_nonempty_text(name):
            continue
        normalized_name = name.strip()
        if normalized_name in seen_names:
            issues.append(
                StrategyContractIssue(
                    field=f"parameters[{index}].name",
                    code="duplicate_parameter_name",
                    message="parameter names must be unique within one strategy definition",
                )
            )
        else:
            seen_names.add(normalized_name)
    return issues


def _validate_parameter_constraints(
    *,
    parameter_type: ParameterType,
    default: Any,
    min_value: Any,
    max_value: Any,
    choices: Any,
) -> list[StrategyContractIssue]:
    issues: list[StrategyContractIssue] = []

    if min_value is not None or max_value is not None:
        if parameter_type not in {ParameterType.INTEGER, ParameterType.FLOAT}:
            issues.append(
                StrategyContractIssue(
                    field="min_value",
                    code="inconsistent_constraints",
                    message="min_value/max_value are only allowed for numeric parameter types",
                )
            )
        elif min_value is not None and not _is_valid_parameter_value(min_value, parameter_type):
            issues.append(
                StrategyContractIssue(
                    field="min_value",
                    code="invalid_constraint_value",
                    message="min_value must match the declared numeric parameter type",
                )
            )
        if (
            parameter_type in {ParameterType.INTEGER, ParameterType.FLOAT}
            and max_value is not None
            and not _is_valid_parameter_value(max_value, parameter_type)
        ):
            issues.append(
                StrategyContractIssue(
                    field="max_value",
                    code="invalid_constraint_value",
                    message="max_value must match the declared numeric parameter type",
                )
            )
        if (
            _is_valid_parameter_value(min_value, parameter_type)
            and _is_valid_parameter_value(max_value, parameter_type)
            and min_value > max_value
        ):
            issues.append(
                StrategyContractIssue(
                    field="min_value",
                    code="inconsistent_constraints",
                    message="min_value must not be greater than max_value",
                )
            )

    normalized_choices: tuple[Any, ...] = ()
    if choices not in (None, ()):
        if not isinstance(choices, (list, tuple)) or isinstance(choices, str):
            issues.append(
                StrategyContractIssue(
                    field="choices",
                    code="invalid_type",
                    message="choices must be a sequence when provided",
                )
            )
        else:
            normalized_choices = tuple(choices)
            if not normalized_choices:
                issues.append(
                    StrategyContractIssue(
                        field="choices",
                        code="inconsistent_constraints",
                        message="choices must not be empty when provided",
                    )
                )
            seen_choices: set[str] = set()
            for choice in normalized_choices:
                if not _is_valid_parameter_value(choice, parameter_type):
                    issues.append(
                        StrategyContractIssue(
                            field="choices",
                            code="invalid_choice_value",
                            message="each choice must match the declared parameter type",
                        )
                    )
                    break
                marker = repr(choice)
                if marker in seen_choices:
                    issues.append(
                        StrategyContractIssue(
                            field="choices",
                            code="duplicate_choice_value",
                            message="choices must not contain duplicates",
                        )
                    )
                    break
                seen_choices.add(marker)

    if default is not None:
        if not _is_valid_parameter_value(default, parameter_type):
            issues.append(
                StrategyContractIssue(
                    field="default",
                    code="invalid_default_value",
                    message="default must match the declared parameter type",
                )
            )
        if normalized_choices and default not in normalized_choices:
            issues.append(
                StrategyContractIssue(
                    field="default",
                    code="inconsistent_constraints",
                    message="default must be one of the declared choices",
                )
            )
        if (
            parameter_type in {ParameterType.INTEGER, ParameterType.FLOAT}
            and _is_valid_parameter_value(default, parameter_type)
        ):
            if _is_valid_parameter_value(min_value, parameter_type) and default < min_value:
                issues.append(
                    StrategyContractIssue(
                        field="default",
                        code="inconsistent_constraints",
                        message="default must be greater than or equal to min_value",
                    )
                )
            if _is_valid_parameter_value(max_value, parameter_type) and default > max_value:
                issues.append(
                    StrategyContractIssue(
                        field="default",
                        code="inconsistent_constraints",
                        message="default must be less than or equal to max_value",
                    )
                )

    return issues


def _validate_text_sequence(
    payload: Any,
    *,
    field_name: str,
    duplicate_code: str,
) -> list[StrategyContractIssue]:
    if not isinstance(payload, (list, tuple)) or isinstance(payload, str):
        return [
            StrategyContractIssue(
                field=field_name,
                code="invalid_type",
                message=f"{field_name} must be a sequence of non-empty strings",
            )
        ]

    issues: list[StrategyContractIssue] = []
    seen_values: set[str] = set()
    for value in payload:
        if not _is_nonempty_text(value):
            issues.append(
                StrategyContractIssue(
                    field=field_name,
                    code="invalid_value",
                    message=f"{field_name} must contain only non-empty strings",
                )
            )
            continue
        normalized_value = value.strip()
        if normalized_value in seen_values:
            issues.append(
                StrategyContractIssue(
                    field=field_name,
                    code=duplicate_code,
                    message=f"{field_name} must not contain duplicates",
                )
            )
        else:
            seen_values.add(normalized_value)
    return issues


def _validate_required_nonempty_texts(
    record: Mapping[str, Any],
    fields: tuple[str, ...],
) -> list[StrategyContractIssue]:
    issues: list[StrategyContractIssue] = []
    for field_name in fields:
        if field_name not in record or record[field_name] is None:
            issues.append(_missing_required(field_name))
        elif not _is_nonempty_text(record[field_name]):
            issues.append(
                StrategyContractIssue(
                    field=field_name,
                    code="empty_text",
                    message=f"{field_name} must be a non-empty string",
                )
            )
    return issues


def _validate_expected_fields(
    record: Mapping[str, Any],
    allowed_fields: tuple[str, ...],
) -> list[StrategyContractIssue]:
    allowed = set(allowed_fields)
    return [
        StrategyContractIssue(
            field=field_name,
            code="unexpected_field",
            message=f"{field_name} is not part of this contract",
        )
        for field_name in record
        if field_name not in allowed
    ]


def _coerce_parameter_type(value: Any) -> ParameterType | None:
    if isinstance(value, ParameterType):
        return value
    if isinstance(value, str):
        try:
            return ParameterType(value)
        except ValueError:
            return None
    return None


def _coerce_signal_intent(value: Any) -> SignalIntent | None:
    if isinstance(value, SignalIntent):
        return value
    if isinstance(value, str):
        try:
            return SignalIntent(value)
        except ValueError:
            return None
    return None


def _is_valid_parameter_value(value: Any, parameter_type: ParameterType) -> bool:
    if value is None:
        return False
    if parameter_type is ParameterType.INTEGER:
        return isinstance(value, int) and not isinstance(value, bool)
    if parameter_type is ParameterType.FLOAT:
        return isinstance(value, (int, float)) and not isinstance(value, bool) and isfinite(value)
    if parameter_type is ParameterType.STRING:
        return isinstance(value, str) and value.strip() != ""
    if parameter_type is ParameterType.BOOLEAN:
        return isinstance(value, bool)
    return False


def _is_nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def _missing_required(field_name: str) -> StrategyContractIssue:
    return StrategyContractIssue(
        field=field_name,
        code="missing_required",
        message=f"{field_name} is required",
    )


def _prefix_issue(issue: StrategyContractIssue, *, prefix: str) -> StrategyContractIssue:
    return StrategyContractIssue(
        field=f"{prefix}.{issue.field}",
        code=issue.code,
        message=issue.message,
    )


def _record_mapping(payload: Any) -> Mapping[str, Any]:
    if isinstance(payload, Mapping):
        return payload
    if is_dataclass(payload):
        return asdict(payload)
    return {}
