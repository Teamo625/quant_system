"""Stable FeatureHub contracts for future feature outputs."""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from datetime import date, datetime
from enum import Enum
from math import isfinite
from typing import Any, Mapping, TypeAlias

from quant.datahub.datasets import DatasetName


FEATURE_VALUE_SCHEMA_VERSION = "1.0.0"


class FeatureName(str, Enum):
    """Planned top-level feature identifiers for early FeatureHub records."""

    PRICE_TECHNICAL = "price_technical"
    VALUATION = "valuation"
    CAPITAL_FLOW = "capital_flow"
    MACRO = "macro"


FeatureScalar: TypeAlias = str | int | float

APPROVED_SOURCE_DATASETS: tuple[DatasetName, ...] = (
    DatasetName.INSTRUMENT_MASTER,
    DatasetName.TRADING_CALENDAR,
    DatasetName.DAILY_BARS,
    DatasetName.CORPORATE_ACTIONS,
    DatasetName.VALUATION_SNAPSHOT,
    DatasetName.CAPITAL_FLOW_SNAPSHOT,
    DatasetName.MACRO_OBSERVATIONS,
    DatasetName.DATA_QUALITY_REPORT,
)

REQUIRED_RECORD_FIELDS: tuple[str, ...] = (
    "symbol",
    "market",
    "trade_date",
    "feature_name",
    "value",
    "source_dataset",
    "created_at",
    "schema_version",
)


@dataclass(frozen=True)
class FeatureSchemaMetadata:
    """Lightweight schema metadata for one feature record contract."""

    schema_version: str
    supported_features: tuple[FeatureName, ...]
    approved_source_datasets: tuple[DatasetName, ...]


FEATURE_VALUE_SCHEMA = FeatureSchemaMetadata(
    schema_version=FEATURE_VALUE_SCHEMA_VERSION,
    supported_features=tuple(FeatureName),
    approved_source_datasets=APPROVED_SOURCE_DATASETS,
)


@dataclass(frozen=True)
class FeatureContractIssue:
    """Structured validation issue for deterministic offline tests."""

    field: str
    code: str
    message: str


@dataclass(frozen=True)
class FeatureValueRecord:
    """Single validated feature output record."""

    symbol: str
    market: str
    trade_date: date
    feature_name: FeatureName
    value: FeatureScalar
    source_dataset: DatasetName
    created_at: datetime
    schema_version: str = FEATURE_VALUE_SCHEMA_VERSION


def validate_feature_value_record(
    record: FeatureValueRecord | Mapping[str, Any],
) -> tuple[FeatureContractIssue, ...]:
    """Return deterministic validation issues for one feature value record."""
    payload = _record_mapping(record)
    issues: list[FeatureContractIssue] = []

    for field_name in REQUIRED_RECORD_FIELDS:
        if field_name not in payload or payload[field_name] is None:
            issues.append(
                FeatureContractIssue(
                    field=field_name,
                    code="missing_required",
                    message=f"{field_name} is required",
                )
            )

    if "symbol" in payload and not _is_nonempty_text(payload["symbol"]):
        issues.append(
            FeatureContractIssue(
                field="symbol",
                code="invalid_text",
                message="symbol must be a non-empty string",
            )
        )

    if "market" in payload and not _is_nonempty_text(payload["market"]):
        issues.append(
            FeatureContractIssue(
                field="market",
                code="invalid_text",
                message="market must be a non-empty string",
            )
        )

    if "trade_date" in payload and not _is_plain_date(payload["trade_date"]):
        issues.append(
            FeatureContractIssue(
                field="trade_date",
                code="invalid_type",
                message="trade_date must be a date instance",
            )
        )

    if "created_at" in payload and not isinstance(payload["created_at"], datetime):
        issues.append(
            FeatureContractIssue(
                field="created_at",
                code="invalid_type",
                message="created_at must be a datetime instance",
            )
        )

    if "schema_version" in payload:
        schema_version = payload["schema_version"]
        if not _is_nonempty_text(schema_version):
            issues.append(
                FeatureContractIssue(
                    field="schema_version",
                    code="invalid_text",
                    message="schema_version must be a non-empty string",
                )
            )
        elif schema_version != FEATURE_VALUE_SCHEMA.schema_version:
            issues.append(
                FeatureContractIssue(
                    field="schema_version",
                    code="unsupported_schema_version",
                    message=(
                        "schema_version must match "
                        f"{FEATURE_VALUE_SCHEMA.schema_version}"
                    ),
                )
            )

    if "feature_name" in payload and _coerce_feature_name(payload["feature_name"]) is None:
        issues.append(
            FeatureContractIssue(
                field="feature_name",
                code="unsupported_feature_name",
                message="feature_name must be one of the supported FeatureName values",
            )
        )

    if "value" in payload and not _is_supported_feature_value(payload["value"]):
        issues.append(
            FeatureContractIssue(
                field="value",
                code="unsupported_value_type",
                message="value must be a finite int, float, or string",
            )
        )

    if (
        "source_dataset" in payload
        and _coerce_approved_source_dataset(payload["source_dataset"]) is None
    ):
        issues.append(
            FeatureContractIssue(
                field="source_dataset",
                code="unsupported_source_dataset",
                message=(
                    "source_dataset must reference an approved DataHub dataset input"
                ),
            )
        )

    return tuple(issues)


def _record_mapping(record: FeatureValueRecord | Mapping[str, Any]) -> dict[str, Any]:
    if is_dataclass(record) and not isinstance(record, type):
        return asdict(record)
    return dict(record)


def _is_nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def _is_plain_date(value: Any) -> bool:
    return isinstance(value, date) and not isinstance(value, datetime)


def _coerce_feature_name(value: Any) -> FeatureName | None:
    if isinstance(value, FeatureName):
        return value
    if isinstance(value, str):
        try:
            return FeatureName(value)
        except ValueError:
            return None
    return None


def _coerce_approved_source_dataset(value: Any) -> DatasetName | None:
    dataset_name: DatasetName | None = None
    if isinstance(value, DatasetName):
        dataset_name = value
    elif isinstance(value, str):
        try:
            dataset_name = DatasetName(value)
        except ValueError:
            return None

    if dataset_name not in FEATURE_VALUE_SCHEMA.approved_source_datasets:
        return None
    return dataset_name


def _is_supported_feature_value(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, str):
        return True
    if isinstance(value, int):
        return True
    if isinstance(value, float):
        return isfinite(value)
    return False
