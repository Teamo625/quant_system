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
    ScanArtifactContext,
    ScanArtifactHandoffMetadata,
    ScanArtifactRankingMetadata,
    ScanArtifactUniverseSnapshot,
    ScanCandidateList,
    ScanCandidateRecord,
    ScanRunMetadata,
    validate_scan_candidate_list,
)


ScannerStoragePath = str | PathLike[str]
SCANNER_CANDIDATE_LIST_MANIFEST_VERSION = "1.1.0"


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
    universe_snapshot: dict[str, Any]
    ranking: dict[str, Any] | None
    downstream_handoff: dict[str, Any]


def serialize_scan_run_metadata(metadata: ScanRunMetadata) -> dict[str, Any]:
    """Serialize Scanner run metadata into a JSON-compatible mapping."""
    payload = {
        "run_id": metadata.run_id,
        "scanner_id": metadata.scanner_id,
        "trade_date": metadata.trade_date,
        "universe_id": metadata.universe_id,
        "generated_at": metadata.generated_at.isoformat(),
        "schema_version": metadata.schema_version,
    }
    if metadata.artifact_context is not None:
        payload["artifact_context"] = serialize_scan_artifact_context(
            metadata.artifact_context,
        )
    return payload


def serialize_scan_artifact_universe_snapshot(
    snapshot: ScanArtifactUniverseSnapshot,
) -> dict[str, Any]:
    """Serialize universe snapshot provenance for manifest persistence."""
    payload = {
        "universe_id": snapshot.universe_id,
        "universe_name": snapshot.universe_name,
        "market": snapshot.market,
        "as_of_date": snapshot.as_of_date,
        "symbols": list(snapshot.symbols),
    }
    if snapshot.source is not None:
        payload["source"] = snapshot.source
    if snapshot.family is not None:
        payload["family"] = (
            snapshot.family.value if hasattr(snapshot.family, "value") else snapshot.family
        )
    if snapshot.preset is not None:
        payload["preset"] = (
            snapshot.preset.value if hasattr(snapshot.preset, "value") else snapshot.preset
        )
    return payload


def serialize_scan_artifact_ranking_metadata(
    ranking: ScanArtifactRankingMetadata,
) -> dict[str, Any]:
    """Serialize ranking reproducibility metadata for ranked artifacts."""
    return {
        "criteria": [
            serialize_ranking_criterion(criterion) for criterion in ranking.criteria
        ],
        "score_formula": ranking.score_formula,
        "tie_break_order": list(ranking.tie_break_order),
    }


def serialize_scan_artifact_handoff_metadata(
    handoff: ScanArtifactHandoffMetadata,
) -> dict[str, Any]:
    """Serialize downstream handoff metadata for later local consumers."""
    return {
        "artifact_type": handoff.artifact_type,
        "artifact_purpose": handoff.artifact_purpose,
        "producer_name": handoff.producer_name,
        "intended_consumers": list(handoff.intended_consumers),
    }


def serialize_scan_artifact_context(
    artifact_context: ScanArtifactContext,
) -> dict[str, Any]:
    """Serialize optional artifact context embedded in scan metadata."""
    payload = {
        "universe_snapshot": serialize_scan_artifact_universe_snapshot(
            artifact_context.universe_snapshot,
        ),
        "handoff": serialize_scan_artifact_handoff_metadata(artifact_context.handoff),
    }
    if artifact_context.ranking is not None:
        payload["ranking"] = serialize_scan_artifact_ranking_metadata(
            artifact_context.ranking,
        )
    return payload


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


def serialize_ranking_criterion(criterion: Any) -> dict[str, Any]:
    """Serialize one ranking criterion into a JSON-compatible mapping."""
    return {
        "feature_ref": serialize_feature_reference(criterion.feature_ref),
        "direction": criterion.direction.value,
        "weight": criterion.weight,
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
    artifact_context = _require_artifact_context(candidate_list)
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
        universe_snapshot=serialize_scan_artifact_universe_snapshot(
            artifact_context.universe_snapshot,
        ),
        ranking=(
            serialize_scan_artifact_ranking_metadata(artifact_context.ranking)
            if artifact_context.ranking is not None
            else None
        ),
        downstream_handoff=_build_downstream_handoff_payload(
            handoff=artifact_context.handoff,
            metadata=candidate_list.metadata,
            candidate_list=candidate_list,
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
    manifest = build_scanner_candidate_list_manifest(candidate_list)

    rows = tuple(
        serialize_scan_candidate_record(record)
        for record in candidate_list.candidates
    )
    with destination.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(_canonical_json(row))
            handle.write("\n")

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


def _require_artifact_context(candidate_list: ScanCandidateList) -> ScanArtifactContext:
    artifact_context = candidate_list.metadata.artifact_context
    if artifact_context is None:
        raise ValueError(
            "candidate list artifact metadata missing: metadata.artifact_context "
            "is required for persisted scanner artifacts"
        )

    ranked_candidates_present = any(
        candidate.rank is not None or candidate.score is not None
        for candidate in candidate_list.candidates
    )
    if ranked_candidates_present and artifact_context.ranking is None:
        raise ValueError(
            "candidate list artifact metadata missing: metadata.artifact_context.ranking "
            "is required for persisted ranked artifacts"
        )
    if not ranked_candidates_present and artifact_context.ranking is not None:
        raise ValueError(
            "candidate list artifact metadata invalid: metadata.artifact_context.ranking "
            "must be omitted for unranked artifacts"
        )
    return artifact_context


def _build_downstream_handoff_payload(
    *,
    handoff: ScanArtifactHandoffMetadata,
    metadata: ScanRunMetadata,
    candidate_list: ScanCandidateList,
) -> dict[str, Any]:
    payload = serialize_scan_artifact_handoff_metadata(handoff)
    payload["producer_run_id"] = metadata.run_id
    payload["producer_scanner_id"] = metadata.scanner_id
    payload["schema_version"] = metadata.schema_version
    payload["manifest_version"] = SCANNER_CANDIDATE_LIST_MANIFEST_VERSION
    payload["ranked"] = any(
        candidate.rank is not None or candidate.score is not None
        for candidate in candidate_list.candidates
    )
    return payload


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
    "serialize_scan_artifact_context",
    "serialize_scan_artifact_handoff_metadata",
    "serialize_scan_artifact_ranking_metadata",
    "serialize_scan_artifact_universe_snapshot",
    "serialize_feature_reference",
    "serialize_filter_spec",
    "serialize_ranking_criterion",
    "serialize_scan_candidate_record",
    "serialize_scan_run_metadata",
    "serialize_scanner_candidate_list_manifest",
    "write_scan_candidate_list_jsonl",
    "write_scanner_candidate_list_manifest",
]
