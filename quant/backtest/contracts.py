"""Offline-safe BacktestEngine foundation contracts."""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from datetime import date, datetime
from enum import Enum
from math import isfinite
from typing import Any, Mapping


BACKTEST_CONTRACT_SCHEMA_VERSION = "1.0.0"

STRATEGY_REFERENCE_FIELDS: tuple[str, ...] = (
    "strategy_id",
    "strategy_version",
)
SELECTION_REFERENCE_FIELDS: tuple[str, ...] = (
    "reference_kind",
    "reference_id",
    "reference_date",
    "market",
)
BACKTEST_REQUEST_FIELDS: tuple[str, ...] = (
    "request_id",
    "strategy_ref",
    "selection_ref",
    "start_trade_date",
    "end_trade_date",
    "starting_capital",
    "transaction_cost_bps",
    "slippage_bps",
    "schema_version",
)
RESULT_SUMMARY_FIELDS: tuple[str, ...] = (
    "summary_id",
    "request_id",
    "strategy_id",
    "strategy_version",
    "start_trade_date",
    "end_trade_date",
    "result_status",
    "generated_at",
    "metric_keys",
    "artifact_reference",
)


class SelectionReferenceKind(str, Enum):
    """Supported declarative backtest input reference kinds."""

    UNIVERSE = "universe"
    CANDIDATE_LIST = "candidate_list"


class ResultStatus(str, Enum):
    """Supported summary lifecycle states."""

    DECLARED = "declared"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class BacktestContractIssue:
    """Structured validation issue for deterministic backtest tests."""

    field: str
    code: str
    message: str


@dataclass(frozen=True)
class StrategyReference:
    """Stable identifier for one strategy contract version."""

    strategy_id: str
    strategy_version: str


@dataclass(frozen=True)
class SelectionReference:
    """Universe or candidate-list reference metadata without any reads."""

    reference_kind: SelectionReferenceKind
    reference_id: str
    reference_date: str | None = None
    market: str | None = None


@dataclass(frozen=True)
class BacktestRequest:
    """Declarative backtest request contract with no replay behavior."""

    request_id: str
    strategy_ref: StrategyReference
    selection_ref: SelectionReference
    start_trade_date: str
    end_trade_date: str
    starting_capital: float
    transaction_cost_bps: float = 0.0
    slippage_bps: float = 0.0
    schema_version: str = BACKTEST_CONTRACT_SCHEMA_VERSION


@dataclass(frozen=True)
class BacktestResultSummary:
    """Result summary metadata placeholder for future replay outputs."""

    summary_id: str
    request_id: str
    strategy_id: str
    strategy_version: str
    start_trade_date: str
    end_trade_date: str
    result_status: ResultStatus
    generated_at: datetime
    metric_keys: tuple[str, ...] = ()
    artifact_reference: str | None = None


def validate_strategy_reference(
    payload: StrategyReference | Mapping[str, Any],
) -> tuple[BacktestContractIssue, ...]:
    """Return deterministic validation issues for one strategy reference."""
    record = _record_mapping(payload)
    issues: list[BacktestContractIssue] = []
    issues.extend(_validate_expected_fields(record, STRATEGY_REFERENCE_FIELDS))
    issues.extend(
        _validate_required_nonempty_texts(
            record,
            ("strategy_id", "strategy_version"),
        )
    )
    return tuple(issues)


def validate_selection_reference(
    payload: SelectionReference | Mapping[str, Any],
) -> tuple[BacktestContractIssue, ...]:
    """Return deterministic validation issues for universe/candidate references."""
    record = _record_mapping(payload)
    issues: list[BacktestContractIssue] = []
    issues.extend(_validate_expected_fields(record, SELECTION_REFERENCE_FIELDS))

    if "reference_kind" not in record or record["reference_kind"] is None:
        issues.append(_missing_required("reference_kind"))
    elif _coerce_selection_reference_kind(record["reference_kind"]) is None:
        issues.append(
            BacktestContractIssue(
                field="reference_kind",
                code="unsupported_reference_kind",
                message="reference_kind must be a supported SelectionReferenceKind value",
            )
        )

    issues.extend(_validate_required_nonempty_texts(record, ("reference_id",)))

    if "reference_date" in record and record["reference_date"] is not None:
        if not _is_iso_date_text(record["reference_date"]):
            issues.append(
                BacktestContractIssue(
                    field="reference_date",
                    code="invalid_date_string",
                    message="reference_date must be an ISO date string when provided",
                )
            )

    if "market" in record and record["market"] is not None and not _is_nonempty_text(record["market"]):
        issues.append(
            BacktestContractIssue(
                field="market",
                code="empty_text",
                message="market must be a non-empty string when provided",
            )
        )

    return tuple(issues)


def validate_backtest_request(
    payload: BacktestRequest | Mapping[str, Any],
) -> tuple[BacktestContractIssue, ...]:
    """Return deterministic validation issues for one backtest request."""
    record = _record_mapping(payload)
    issues: list[BacktestContractIssue] = []
    issues.extend(_validate_expected_fields(record, BACKTEST_REQUEST_FIELDS))

    if "request_id" not in record or record["request_id"] is None:
        issues.append(_missing_required("request_id"))
    elif not _is_nonempty_text(record["request_id"]):
        issues.append(
            BacktestContractIssue(
                field="request_id",
                code="empty_text",
                message="request_id must be a non-empty string",
            )
        )

    if "strategy_ref" not in record or record["strategy_ref"] is None:
        issues.append(_missing_required("strategy_ref"))
    else:
        nested_issues = validate_strategy_reference(record["strategy_ref"])
        if nested_issues:
            for issue in nested_issues:
                issues.append(_prefix_issue(issue, prefix="strategy_ref"))

    if "selection_ref" not in record or record["selection_ref"] is None:
        issues.append(_missing_required("selection_ref"))
    else:
        for issue in validate_selection_reference(record["selection_ref"]):
            issues.append(_prefix_issue(issue, prefix="selection_ref"))

    issues.extend(
        _validate_trade_date_range(
            record,
            start_field="start_trade_date",
            end_field="end_trade_date",
        )
    )

    if "starting_capital" not in record or record["starting_capital"] is None:
        issues.append(_missing_required("starting_capital"))
    elif not _is_positive_number(record["starting_capital"]):
        issues.append(
            BacktestContractIssue(
                field="starting_capital",
                code="invalid_value",
                message="starting_capital must be a positive finite number",
            )
        )

    for field_name in ("transaction_cost_bps", "slippage_bps"):
        if field_name not in record or record[field_name] is None:
            issues.append(_missing_required(field_name))
        elif not _is_non_negative_number(record[field_name]):
            issues.append(
                BacktestContractIssue(
                    field=field_name,
                    code="invalid_value",
                    message=f"{field_name} must be a non-negative finite number",
                )
            )

    if "schema_version" in record and record["schema_version"] != BACKTEST_CONTRACT_SCHEMA_VERSION:
        issues.append(
            BacktestContractIssue(
                field="schema_version",
                code="unsupported_schema_version",
                message="schema_version must match the BacktestEngine contract schema",
            )
        )

    return tuple(issues)


def validate_backtest_result_summary(
    payload: BacktestResultSummary | Mapping[str, Any],
) -> tuple[BacktestContractIssue, ...]:
    """Return deterministic validation issues for one summary placeholder."""
    record = _record_mapping(payload)
    issues: list[BacktestContractIssue] = []
    issues.extend(_validate_expected_fields(record, RESULT_SUMMARY_FIELDS))
    issues.extend(
        _validate_required_nonempty_texts(
            record,
            (
                "summary_id",
                "request_id",
                "strategy_id",
                "strategy_version",
            ),
        )
    )
    issues.extend(
        _validate_trade_date_range(
            record,
            start_field="start_trade_date",
            end_field="end_trade_date",
        )
    )

    if "result_status" not in record or record["result_status"] is None:
        issues.append(_missing_required("result_status"))
    elif _coerce_result_status(record["result_status"]) is None:
        issues.append(
            BacktestContractIssue(
                field="result_status",
                code="unsupported_result_status",
                message="result_status must be a supported ResultStatus value",
            )
        )

    if "generated_at" not in record or record["generated_at"] is None:
        issues.append(_missing_required("generated_at"))
    elif not isinstance(record["generated_at"], datetime):
        issues.append(
            BacktestContractIssue(
                field="generated_at",
                code="invalid_type",
                message="generated_at must be a datetime instance",
            )
        )

    if "metric_keys" not in record or record["metric_keys"] is None:
        issues.append(_missing_required("metric_keys"))
    else:
        issues.extend(
            _validate_text_sequence(
                record["metric_keys"],
                field_name="metric_keys",
                duplicate_code="duplicate_metric_key",
            )
        )

    if (
        "artifact_reference" in record
        and record["artifact_reference"] is not None
        and not _is_nonempty_text(record["artifact_reference"])
    ):
        issues.append(
            BacktestContractIssue(
                field="artifact_reference",
                code="empty_text",
                message="artifact_reference must be a non-empty string when provided",
            )
        )

    return tuple(issues)


def _validate_trade_date_range(
    record: Mapping[str, Any],
    *,
    start_field: str,
    end_field: str,
) -> list[BacktestContractIssue]:
    issues: list[BacktestContractIssue] = []
    start_date = _coerce_iso_date(record.get(start_field))
    end_date = _coerce_iso_date(record.get(end_field))

    if start_field not in record or record[start_field] is None:
        issues.append(_missing_required(start_field))
    elif start_date is None:
        issues.append(
            BacktestContractIssue(
                field=start_field,
                code="invalid_date_string",
                message=f"{start_field} must be an ISO date string",
            )
        )

    if end_field not in record or record[end_field] is None:
        issues.append(_missing_required(end_field))
    elif end_date is None:
        issues.append(
            BacktestContractIssue(
                field=end_field,
                code="invalid_date_string",
                message=f"{end_field} must be an ISO date string",
            )
        )

    if start_date is not None and end_date is not None and start_date > end_date:
        issues.append(
            BacktestContractIssue(
                field=end_field,
                code="invalid_date_order",
                message=f"{end_field} must not be earlier than {start_field}",
            )
        )
    return issues


def _validate_text_sequence(
    payload: Any,
    *,
    field_name: str,
    duplicate_code: str,
) -> list[BacktestContractIssue]:
    if not isinstance(payload, (list, tuple)) or isinstance(payload, str):
        return [
            BacktestContractIssue(
                field=field_name,
                code="invalid_type",
                message=f"{field_name} must be a sequence of non-empty strings",
            )
        ]

    issues: list[BacktestContractIssue] = []
    seen_values: set[str] = set()
    for value in payload:
        if not _is_nonempty_text(value):
            issues.append(
                BacktestContractIssue(
                    field=field_name,
                    code="invalid_value",
                    message=f"{field_name} must contain only non-empty strings",
                )
            )
            continue
        normalized_value = value.strip()
        if normalized_value in seen_values:
            issues.append(
                BacktestContractIssue(
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
) -> list[BacktestContractIssue]:
    issues: list[BacktestContractIssue] = []
    for field_name in fields:
        if field_name not in record or record[field_name] is None:
            issues.append(_missing_required(field_name))
        elif not _is_nonempty_text(record[field_name]):
            issues.append(
                BacktestContractIssue(
                    field=field_name,
                    code="empty_text",
                    message=f"{field_name} must be a non-empty string",
                )
            )
    return issues


def _validate_expected_fields(
    record: Mapping[str, Any],
    allowed_fields: tuple[str, ...],
) -> list[BacktestContractIssue]:
    allowed = set(allowed_fields)
    return [
        BacktestContractIssue(
            field=field_name,
            code="unexpected_field",
            message=f"{field_name} is not part of this contract",
        )
        for field_name in record
        if field_name not in allowed
    ]


def _coerce_selection_reference_kind(value: Any) -> SelectionReferenceKind | None:
    if isinstance(value, SelectionReferenceKind):
        return value
    if isinstance(value, str):
        try:
            return SelectionReferenceKind(value)
        except ValueError:
            return None
    return None


def _coerce_result_status(value: Any) -> ResultStatus | None:
    if isinstance(value, ResultStatus):
        return value
    if isinstance(value, str):
        try:
            return ResultStatus(value)
        except ValueError:
            return None
    return None


def _coerce_iso_date(value: Any) -> date | None:
    if not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _is_iso_date_text(value: Any) -> bool:
    return _coerce_iso_date(value) is not None


def _is_positive_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and isfinite(value) and value > 0


def _is_non_negative_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and isfinite(value) and value >= 0


def _is_nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def _missing_required(field_name: str) -> BacktestContractIssue:
    return BacktestContractIssue(
        field=field_name,
        code="missing_required",
        message=f"{field_name} is required",
    )


def _prefix_issue(issue: BacktestContractIssue, *, prefix: str) -> BacktestContractIssue:
    return BacktestContractIssue(
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
