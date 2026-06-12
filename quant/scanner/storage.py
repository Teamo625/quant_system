"""Deterministic local persistence helpers for Scanner artifacts."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from os import PathLike
from pathlib import Path
from typing import Any

from .contracts import (
    SCANNER_CONTRACT_SCHEMA_VERSION,
    FeatureReference,
    FilterSpec,
    ScanCandidateList,
    ScanCandidateRecord,
    ScanRunMetadata,
    validate_scan_candidate_list,
)


ScannerStoragePath = str | PathLike[str]
SCANNER_CANDIDATE_LIST_MANIFEST_VERSION = "1.0.0"


@dataclass(frozen=True)
class ScannerCandidateListManifest:
    """Metadata describing one persisted Scanner candidate-list artifact."""

    manifest_version: str
    schema_version: str
    run_id: str
    scanner_id: str
    trade_date: str
    universe_id: str
    generated_at: str
    candidate_count: int
    content_checksum: str
    feature_refs: tuple[dict[str, Any], ...]
    filters: tuple[dict[str, Any], ...]


def serialize_scan_run_metadata(metadata: ScanRunMetadata) -> dict[str, Any]:
    """Serialize Scanner run metadata into a JSON-compatible mapping."""
    return {
        "run_id": metadata.run_id,
        "scanner_id": metadata.scanner_id,
        "trade_date": metadata.trade_date,
        "universe_id": metadata.universe_id,
        "generated_at": metadata.generated_at.isoformat(),
        "schema_version": metadata.schema_version,
    }


def serialize_feature_reference(reference: FeatureReference) -> dict[str, Any]:
    """Serialize one declarative FeatureHub reference."""
    return {
        "feature_name": reference.feature_name.value,
        "lag_days": reference.lag_days,
    }


def serialize_filter_spec(filter_spec: FilterSpec) -> dict[str, Any]:
    """Serialize one declarative Scanner filter spec."""
    return {
        "filter_id": filter_spec.filter_id,
        "feature_ref": serialize_feature_reference(filter_spec.feature_ref),
        "operator": filter_spec.operator.value,
        "threshold": _serialize_threshold(filter_spec.threshold),
    }


def serialize_scan_candidate_record(record: ScanCandidateRecord) -> dict[str, Any]:
    """Serialize one Scanner candidate row into a JSON-compatible mapping."""
    payload = {
        "run_id": record.run_id,
        "trade_date": record.trade_date,
        "symbol": record.symbol,
        "market": record.market,
        "universe_id": record.universe_id,
        "matched_filter_ids": list(record.matched_filter_ids),
    }
    if record.score is not None:
        payload["score"] = record.score
    if record.rank is not None:
        payload["rank"] = record.rank
    return payload


def build_scanner_candidate_list_manifest(
    candidate_list: ScanCandidateList,
) -> ScannerCandidateListManifest:
    """Build deterministic manifest metadata for one candidate-list artifact."""
    _validate_candidate_list_or_raise(candidate_list)
    rows = tuple(
        serialize_scan_candidate_record(record)
        for record in candidate_list.candidates
    )
    metadata = serialize_scan_run_metadata(candidate_list.metadata)
    return ScannerCandidateListManifest(
        manifest_version=SCANNER_CANDIDATE_LIST_MANIFEST_VERSION,
        schema_version=SCANNER_CONTRACT_SCHEMA_VERSION,
        run_id=metadata["run_id"],
        scanner_id=metadata["scanner_id"],
        trade_date=metadata["trade_date"],
        universe_id=metadata["universe_id"],
        generated_at=metadata["generated_at"],
        candidate_count=len(rows),
        content_checksum=checksum_scan_candidate_rows(rows),
        feature_refs=tuple(
            serialize_feature_reference(reference)
            for reference in candidate_list.feature_refs
        ),
        filters=tuple(
            serialize_filter_spec(filter_spec)
            for filter_spec in candidate_list.filters
        ),
    )


def serialize_scanner_candidate_list_manifest(
    manifest: ScannerCandidateListManifest,
) -> dict[str, Any]:
    """Serialize a Scanner candidate-list manifest into JSON-compatible data."""
    payload = asdict(manifest)
    payload["feature_refs"] = list(manifest.feature_refs)
    payload["filters"] = list(manifest.filters)
    return payload


def checksum_scan_candidate_rows(rows: tuple[dict[str, Any], ...]) -> str:
    """Return a deterministic SHA-256 checksum for serialized candidate rows."""
    digest = hashlib.sha256()
    for row in rows:
        digest.update(_canonical_json(row).encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()


def write_scan_candidate_list_jsonl(
    path: ScannerStoragePath,
    candidate_list: ScanCandidateList,
    *,
    overwrite: bool = False,
    manifest_path: ScannerStoragePath | None = None,
) -> ScannerCandidateListManifest:
    """Write a validated Scanner candidate-list artifact to local JSONL."""
    _validate_candidate_list_or_raise(candidate_list)
    destination, prepared_manifest_path = _prepare_artifact_paths(
        path,
        manifest_path,
        overwrite=overwrite,
    )

    rows = tuple(
        serialize_scan_candidate_record(record)
        for record in candidate_list.candidates
    )
    with destination.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(_canonical_json(row))
            handle.write("\n")

    manifest = build_scanner_candidate_list_manifest(candidate_list)
    if prepared_manifest_path is not None:
        write_scanner_candidate_list_manifest(
            prepared_manifest_path,
            manifest,
            overwrite=overwrite,
        )
    return manifest


def write_scanner_candidate_list_manifest(
    path: ScannerStoragePath,
    manifest: ScannerCandidateListManifest,
    *,
    overwrite: bool = False,
) -> None:
    """Write one Scanner candidate-list manifest as deterministic local JSON."""
    destination = _prepare_output_path(path, overwrite=overwrite)
    with destination.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(_canonical_json(serialize_scanner_candidate_list_manifest(manifest)))
        handle.write("\n")


def _validate_candidate_list_or_raise(candidate_list: ScanCandidateList) -> None:
    if not isinstance(candidate_list, ScanCandidateList):
        raise TypeError("candidate_list must be a ScanCandidateList instance")
    issues = validate_scan_candidate_list(candidate_list)
    if issues:
        raise ValueError(f"candidate list failed validation: {issues!r}")


def _prepare_output_path(path: ScannerStoragePath, *, overwrite: bool) -> Path:
    destination = Path(path)
    parent = destination.parent
    if not parent.exists():
        raise FileNotFoundError(f"parent directory does not exist: {parent}")
    if destination.exists() and not overwrite:
        raise FileExistsError(f"output file already exists: {destination}")
    return destination


def _prepare_artifact_paths(
    records_path: ScannerStoragePath,
    manifest_path: ScannerStoragePath | None,
    *,
    overwrite: bool,
) -> tuple[Path, Path | None]:
    prepared_records_path = _prepare_output_path(records_path, overwrite=overwrite)
    if manifest_path is None:
        return prepared_records_path, None

    prepared_manifest_path = _prepare_output_path(manifest_path, overwrite=overwrite)
    if prepared_records_path == prepared_manifest_path:
        raise ValueError("records path and manifest path must be different")
    return prepared_records_path, prepared_manifest_path


def _canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(
        payload,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    )


def _serialize_threshold(value: Any) -> Any:
    if isinstance(value, tuple):
        return list(value)
    return value


__all__ = [
    "SCANNER_CANDIDATE_LIST_MANIFEST_VERSION",
    "ScannerCandidateListManifest",
    "build_scanner_candidate_list_manifest",
    "checksum_scan_candidate_rows",
    "serialize_feature_reference",
    "serialize_filter_spec",
    "serialize_scan_candidate_record",
    "serialize_scan_run_metadata",
    "serialize_scanner_candidate_list_manifest",
    "write_scan_candidate_list_jsonl",
    "write_scanner_candidate_list_manifest",
]
