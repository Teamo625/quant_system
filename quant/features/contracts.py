"""Stable FeatureHub contracts for future feature outputs."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import date, datetime
from enum import Enum
from math import isfinite
from typing import Any, Mapping, TypeAlias

from quant.datahub.datasets import DatasetName


LEGACY_FEATURE_VALUE_SCHEMA_VERSION = "1.0.0"
FEATURE_VALUE_SCHEMA_VERSION = "1.1.0"
SUPPORTED_FEATURE_VALUE_SCHEMA_VERSIONS: tuple[str, ...] = (
    LEGACY_FEATURE_VALUE_SCHEMA_VERSION,
    FEATURE_VALUE_SCHEMA_VERSION,
)


class FeatureName(str, Enum):
    """Planned top-level feature identifiers for early FeatureHub records."""

    PRICE_TECHNICAL = "price_technical"
    VALUATION = "valuation"
    CAPITAL_FLOW = "capital_flow"
    RELATIVE = "relative"
    MACRO = "macro"


FeatureScalar: TypeAlias = str | int | float

APPROVED_SOURCE_DATASETS: tuple[DatasetName, ...] = (
    DatasetName.INSTRUMENT_MASTER,
    DatasetName.TRADING_CALENDAR,
    DatasetName.DAILY_BARS,
    DatasetName.CORPORATE_ACTIONS,
    DatasetName.VALUATION_SNAPSHOT,
    DatasetName.CAPITAL_FLOW_SNAPSHOT,
    DatasetName.NORTHBOUND_FLOW_SNAPSHOT,
    DatasetName.FUND_FLOW,
    DatasetName.MACRO_OBSERVATIONS,
    DatasetName.INDEX_DAILY_BARS,
    DatasetName.SECTOR_DAILY_BARS,
    DatasetName.SECTOR_MEMBERSHIP,
    DatasetName.DATA_QUALITY_REPORT,
)

CURRENT_REQUIRED_RECORD_FIELDS: tuple[str, ...] = (
    "symbol",
    "market",
    "trade_date",
    "feature_name",
    "metric_name",
    "metric_params",
    "value",
    "source_dataset",
    "created_at",
    "schema_version",
)

LEGACY_REQUIRED_RECORD_FIELDS: tuple[str, ...] = (
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
    supported_schema_versions: tuple[str, ...]
    supported_features: tuple[FeatureName, ...]
    approved_source_datasets: tuple[DatasetName, ...]


FEATURE_VALUE_SCHEMA = FeatureSchemaMetadata(
    schema_version=FEATURE_VALUE_SCHEMA_VERSION,
    supported_schema_versions=SUPPORTED_FEATURE_VALUE_SCHEMA_VERSIONS,
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
    metric_name: str
    value: FeatureScalar
    source_dataset: DatasetName
    created_at: datetime
    metric_params: Mapping[str, FeatureScalar] = field(default_factory=dict)
    schema_version: str = FEATURE_VALUE_SCHEMA_VERSION


def validate_feature_value_record(
    record: FeatureValueRecord | Mapping[str, Any],
) -> tuple[FeatureContractIssue, ...]:
    """Return deterministic validation issues for one feature value record."""
    payload = _record_mapping(record)
    issues: list[FeatureContractIssue] = []
    schema_version = payload.get("schema_version")
    required_fields = _required_record_fields_for_schema(schema_version)

    for field_name in required_fields:
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
        if not _is_nonempty_text(schema_version):
            issues.append(
                FeatureContractIssue(
                    field="schema_version",
                    code="invalid_text",
                    message="schema_version must be a non-empty string",
                )
            )
        elif schema_version not in FEATURE_VALUE_SCHEMA.supported_schema_versions:
            issues.append(
                FeatureContractIssue(
                    field="schema_version",
                    code="unsupported_schema_version",
                    message=(
                        "schema_version must be one of "
                        f"{FEATURE_VALUE_SCHEMA.supported_schema_versions!r}"
                    ),
                )
            )

    feature_name = None
    if "feature_name" in payload:
        feature_name = _coerce_feature_name(payload["feature_name"])
    if "feature_name" in payload and feature_name is None:
        issues.append(
            FeatureContractIssue(
                field="feature_name",
                code="unsupported_feature_name",
                message="feature_name must be one of the supported FeatureName values",
            )
        )

    if "metric_name" in payload:
        if not _is_nonempty_text(payload["metric_name"]):
            issues.append(
                FeatureContractIssue(
                    field="metric_name",
                    code="invalid_text",
                    message="metric_name must be a non-empty string",
                )
            )

    if "metric_params" in payload:
        issues.extend(_validate_metric_params(payload["metric_params"]))

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


def build_feature_metric_identity(
    record: FeatureValueRecord | Mapping[str, Any],
) -> str:
    """Return a deterministic metric identity string for one feature record."""
    payload = _record_mapping(record)
    feature_name = _coerce_feature_name(payload.get("feature_name"))
    if feature_name is None:
        raise ValueError("feature_name must be one of the supported FeatureName values")
    schema_version = payload.get("schema_version")
    metric_name = _resolve_metric_name(
        payload.get("metric_name"),
        schema_version=schema_version,
        feature_name=feature_name,
    )
    metric_params = _resolve_metric_params(
        payload.get("metric_params"),
        schema_version=schema_version,
    )
    serialized_params = json.dumps(
        dict(sorted(metric_params.items())),
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    )
    return f"{feature_name.value}:{metric_name}:{serialized_params}"


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


def _required_record_fields_for_schema(schema_version: Any) -> tuple[str, ...]:
    if schema_version == LEGACY_FEATURE_VALUE_SCHEMA_VERSION:
        return LEGACY_REQUIRED_RECORD_FIELDS
    return CURRENT_REQUIRED_RECORD_FIELDS


def _validate_metric_params(value: Any) -> tuple[FeatureContractIssue, ...]:
    if not isinstance(value, Mapping):
        return (
            FeatureContractIssue(
                field="metric_params",
                code="invalid_type",
                message="metric_params must be a mapping of scalar calculation parameters",
            ),
        )

    issues: list[FeatureContractIssue] = []
    for key, item in value.items():
        if not _is_nonempty_text(key):
            issues.append(
                FeatureContractIssue(
                    field="metric_params",
                    code="invalid_param_key",
                    message="metric_params keys must be non-empty strings",
                )
            )
            continue
        if not _is_supported_feature_value(item):
            issues.append(
                FeatureContractIssue(
                    field=f"metric_params.{key}",
                    code="unsupported_param_value",
                    message="metric_params values must be finite int, float, or string",
                )
            )
    return tuple(issues)


def _resolve_metric_name(
    value: Any,
    *,
    schema_version: Any,
    feature_name: FeatureName,
) -> str:
    if value is None and schema_version == LEGACY_FEATURE_VALUE_SCHEMA_VERSION:
        return feature_name.value
    if not _is_nonempty_text(value):
        raise ValueError("metric_name must be a non-empty string")
    return value.strip()


def _resolve_metric_params(
    value: Any,
    *,
    schema_version: Any,
) -> dict[str, FeatureScalar]:
    if value is None and schema_version == LEGACY_FEATURE_VALUE_SCHEMA_VERSION:
        return {}
    if not isinstance(value, Mapping):
        raise ValueError(
            "metric_params must be a mapping of scalar calculation parameters"
        )

    normalized_params: dict[str, FeatureScalar] = {}
    for key, item in value.items():
        if not _is_nonempty_text(key):
            raise ValueError("metric_params keys must be non-empty strings")
        normalized_key = key.strip()
        if not _is_supported_feature_value(item):
            raise ValueError(
                "metric_params values must be finite int, float, or string"
            )
        normalized_params[normalized_key] = item
    return normalized_params
