"""Deterministic local persistence helpers for FeatureHub output records."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import date, datetime
from math import isfinite
from os import PathLike
from pathlib import Path
from typing import Any, Iterable, Mapping

from quant.datahub.datasets import DatasetName

from .contracts import (
    APPROVED_SOURCE_DATASETS,
    FEATURE_VALUE_SCHEMA,
    FEATURE_VALUE_SCHEMA_VERSION,
    LEGACY_FEATURE_VALUE_SCHEMA_VERSION,
    FeatureName,
    FeatureValueRecord,
    build_feature_metric_identity,
    validate_feature_value_record,
)

JSONLikeMapping = Mapping[str, Any]
FeatureStoragePath = str | PathLike[str]
FEATURE_OUTPUT_MANIFEST_VERSION = "1.1.0"


@dataclass(frozen=True)
class FeatureOutputManifest:
    """Lightweight metadata describing one persisted feature-output batch."""

    manifest_version: str
    schema_version: str
    record_count: int
    feature_names: tuple[str, ...]
    metric_identities: tuple[str, ...]


def serialize_feature_value_record(
    record: FeatureValueRecord | Mapping[str, Any],
) -> dict[str, Any]:
    """Serialize one validated feature record into a JSON-compatible mapping."""
    feature_record = _coerce_feature_value_record(record)
    return {
        "symbol": feature_record.symbol,
        "market": feature_record.market,
        "trade_date": feature_record.trade_date.isoformat(),
        "feature_name": feature_record.feature_name.value,
        "metric_name": feature_record.metric_name,
        "metric_params": dict(sorted(feature_record.metric_params.items())),
        "value": feature_record.value,
        "source_dataset": feature_record.source_dataset.value,
        "created_at": feature_record.created_at.isoformat(),
        "schema_version": feature_record.schema_version,
    }


def deserialize_feature_value_record(payload: JSONLikeMapping) -> FeatureValueRecord:
    """Deserialize one JSON-compatible mapping into a validated feature record."""
    if not isinstance(payload, Mapping):
        raise TypeError("feature record payload must be a mapping")

    schema_version = _require_schema_version(payload)
    feature_name = _parse_feature_name(payload.get("feature_name"))
    record = FeatureValueRecord(
        symbol=_require_nonempty_text(payload.get("symbol"), field_name="symbol"),
        market=_require_nonempty_text(payload.get("market"), field_name="market"),
        trade_date=_parse_trade_date(payload.get("trade_date")),
        feature_name=feature_name,
        metric_name=_parse_metric_name(
            payload.get("metric_name"),
            schema_version=schema_version,
            feature_name=feature_name,
        ),
        metric_params=_parse_metric_params(
            payload.get("metric_params"),
            schema_version=schema_version,
        ),
        value=_parse_feature_value(payload.get("value")),
        source_dataset=_parse_source_dataset(payload.get("source_dataset")),
        created_at=_parse_created_at(payload.get("created_at")),
        schema_version=schema_version,
    )
    issues = validate_feature_value_record(record)
    if issues:
        raise ValueError(f"feature record failed validation: {issues!r}")
    return record


def build_feature_output_manifest(
    records: Iterable[FeatureValueRecord | Mapping[str, Any]],
) -> FeatureOutputManifest:
    """Return deterministic batch metadata for caller-provided feature records."""
    serialized_records = tuple(
        serialize_feature_value_record(record) for record in records
    )
    feature_names = tuple(
        sorted({payload["feature_name"] for payload in serialized_records})
    )
    metric_identities = tuple(
        sorted({build_feature_metric_identity(payload) for payload in serialized_records})
    )
    return FeatureOutputManifest(
        manifest_version=FEATURE_OUTPUT_MANIFEST_VERSION,
        schema_version=FEATURE_VALUE_SCHEMA_VERSION,
        record_count=len(serialized_records),
        feature_names=feature_names,
        metric_identities=metric_identities,
    )


def serialize_feature_output_manifest(
    manifest: FeatureOutputManifest,
) -> dict[str, Any]:
    """Serialize a feature output manifest into a JSON-compatible mapping."""
    payload = asdict(manifest)
    payload["feature_names"] = list(manifest.feature_names)
    payload["metric_identities"] = list(manifest.metric_identities)
    return payload


def write_feature_records_jsonl(
    path: FeatureStoragePath,
    records: Iterable[FeatureValueRecord | Mapping[str, Any]],
    *,
    overwrite: bool = False,
    manifest_path: FeatureStoragePath | None = None,
) -> FeatureOutputManifest:
    """Write validated feature records to a deterministic local JSONL file."""
    destination = _prepare_output_path(path, overwrite=overwrite)
    if manifest_path is not None:
        _prepare_output_path(manifest_path, overwrite=overwrite)
    serialized_records = tuple(
        serialize_feature_value_record(record) for record in records
    )

    with destination.open("w", encoding="utf-8", newline="\n") as handle:
        for payload in serialized_records:
            handle.write(
                json.dumps(
                    payload,
                    ensure_ascii=True,
                    sort_keys=True,
                    separators=(",", ":"),
                )
            )
            handle.write("\n")

    manifest = build_feature_output_manifest(serialized_records)
    if manifest_path is not None:
        write_feature_output_manifest(
            manifest_path,
            manifest,
            overwrite=overwrite,
        )
    return manifest


def read_feature_records_jsonl(
    path: FeatureStoragePath,
) -> tuple[FeatureValueRecord, ...]:
    """Read validated feature records from a local JSONL file."""
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f"feature records file does not exist: {source}")

    records: list[FeatureValueRecord] = []
    with source.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if line == "":
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"malformed JSONL row at line {line_number}: {exc.msg}"
                ) from exc
            records.append(deserialize_feature_value_record(payload))
    return tuple(records)


def write_feature_output_manifest(
    path: FeatureStoragePath,
    manifest: FeatureOutputManifest,
    *,
    overwrite: bool = False,
) -> None:
    """Write one feature output manifest as deterministic local JSON."""
    destination = _prepare_output_path(path, overwrite=overwrite)
    with destination.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(
            serialize_feature_output_manifest(manifest),
            handle,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
        handle.write("\n")


def _coerce_feature_value_record(
    record: FeatureValueRecord | Mapping[str, Any],
) -> FeatureValueRecord:
    if isinstance(record, FeatureValueRecord):
        issues = validate_feature_value_record(record)
        if issues:
            raise ValueError(f"feature record failed validation: {issues!r}")
        return record
    if isinstance(record, Mapping):
        return deserialize_feature_value_record(record)
    raise TypeError("feature records must be FeatureValueRecord instances or mappings")


def _prepare_output_path(path: FeatureStoragePath, *, overwrite: bool) -> Path:
    destination = Path(path)
    parent = destination.parent
    if not parent.exists():
        raise FileNotFoundError(f"parent directory does not exist: {parent}")
    if destination.exists() and not overwrite:
        raise FileExistsError(f"output file already exists: {destination}")
    return destination


def _require_schema_version(payload: JSONLikeMapping) -> str:
    value = payload.get("schema_version")
    if not isinstance(value, str):
        raise ValueError("schema_version must be a non-empty string")
    schema_version = value.strip()
    if schema_version == "":
        raise ValueError("schema_version must be a non-empty string")
    if schema_version not in FEATURE_VALUE_SCHEMA.supported_schema_versions:
        raise ValueError(
            "unsupported schema_version: "
            f"{schema_version!r}; expected one of "
            f"{FEATURE_VALUE_SCHEMA.supported_schema_versions!r}"
        )
    return schema_version


def _require_nonempty_text(value: Any, *, field_name: str) -> str:
    if not isinstance(value, str) or value.strip() == "":
        raise ValueError(f"{field_name} must be a non-empty string")
    return value.strip()


def _parse_trade_date(value: Any) -> date:
    if not isinstance(value, str):
        raise ValueError("trade_date must be an ISO date string")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("trade_date must be an ISO date string") from exc


def _parse_feature_name(value: Any) -> FeatureName:
    if not isinstance(value, str):
        raise ValueError("feature_name must be a supported FeatureName string")
    try:
        return FeatureName(value)
    except ValueError as exc:
        raise ValueError("feature_name must be a supported FeatureName string") from exc


def _parse_metric_name(
    value: Any,
    *,
    schema_version: str,
    feature_name: FeatureName,
) -> str:
    if value is None and schema_version == LEGACY_FEATURE_VALUE_SCHEMA_VERSION:
        return feature_name.value
    if not isinstance(value, str) or value.strip() == "":
        raise ValueError("metric_name must be a non-empty string")
    return value.strip()


def _parse_metric_params(
    value: Any,
    *,
    schema_version: str,
) -> dict[str, str | int | float]:
    if value is None and schema_version == LEGACY_FEATURE_VALUE_SCHEMA_VERSION:
        return {}
    if not isinstance(value, Mapping):
        raise ValueError("metric_params must be a mapping of scalar calculation parameters")

    normalized_params: dict[str, str | int | float] = {}
    for key, item in value.items():
        if not isinstance(key, str) or key.strip() == "":
            raise ValueError("metric_params keys must be non-empty strings")
        normalized_key = key.strip()
        if isinstance(item, bool):
            raise ValueError(
                "metric_params values must be finite int, float, or string"
            )
        if isinstance(item, str):
            normalized_params[normalized_key] = item
            continue
        if isinstance(item, int):
            normalized_params[normalized_key] = item
            continue
        if isinstance(item, float) and isfinite(item):
            normalized_params[normalized_key] = item
            continue
        raise ValueError("metric_params values must be finite int, float, or string")
    return normalized_params


def _parse_feature_value(value: Any) -> str | int | float:
    if isinstance(value, bool):
        raise ValueError("value must be a finite int, float, or string")
    if isinstance(value, str):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float) and isfinite(value):
        return value
    raise ValueError("value must be a finite int, float, or string")


def _parse_source_dataset(value: Any) -> DatasetName:
    if not isinstance(value, str):
        raise ValueError("source_dataset must be a supported DatasetName string")
    try:
        dataset_name = DatasetName(value)
    except ValueError as exc:
        raise ValueError(
            "source_dataset must be a supported DatasetName string"
        ) from exc
    if dataset_name not in APPROVED_SOURCE_DATASETS:
        raise ValueError("source_dataset must reference an approved DataHub dataset input")
    return dataset_name


def _parse_created_at(value: Any) -> datetime:
    if not isinstance(value, str):
        raise ValueError("created_at must be an ISO datetime string")
    try:
        return datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("created_at must be an ISO datetime string") from exc
