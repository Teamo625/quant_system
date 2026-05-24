"""Local refresh metadata and data-quality helpers for DataHub."""

from __future__ import annotations

from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from .datasets import DatasetName, DatasetRegistry, ValidationIssue
from .storage import LocalStorage

LOCAL_QUALITY_SOURCE_ID = "local_data_quality_engine"
LOCAL_QUALITY_SOURCE_NAME = "Local Data Quality Engine"

_REFRESH_STATUSES: frozenset[str] = frozenset({"success", "warning", "failed"})
_EMPTY_RECORD_STATUSES: frozenset[str] = frozenset({"warn", "fail"})


class LocalRefreshQualityHelper:
    """Build and evaluate local-only refresh metadata and quality records."""

    def __init__(
        self,
        *,
        registry: DatasetRegistry | None = None,
        now_fn: Callable[[], datetime] | None = None,
    ) -> None:
        self._registry = registry or DatasetRegistry()
        self._now_fn = now_fn or (lambda: datetime.now(timezone.utc))

    def build_refresh_metadata(
        self,
        dataset: DatasetName,
        *,
        layer: str,
        source_id: str | None = None,
        source_name: str | None = None,
        record_count: int = 0,
        status: str = "success",
        started_at: datetime | None = None,
        completed_at: datetime | None = None,
        details: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        if status not in _REFRESH_STATUSES:
            allowed = ", ".join(sorted(_REFRESH_STATUSES))
            raise ValueError(f"Unsupported refresh status: {status!r}. Allowed: {allowed}")
        if not isinstance(layer, str) or layer.strip() == "":
            raise ValueError("layer must be a non-empty string.")
        if record_count < 0:
            raise ValueError("record_count must be non-negative.")

        now = self._now_fn()
        resolved_started = started_at or now
        resolved_completed = completed_at or now
        schema_version = self._registry.get(dataset).schema_version

        metadata: dict[str, Any] = {
            "dataset": dataset.value,
            "layer": layer.strip(),
            "record_count": int(record_count),
            "status": status,
            "started_at": resolved_started.isoformat(),
            "completed_at": resolved_completed.isoformat(),
            "refreshed_at": resolved_completed.isoformat(),
            "schema_version": schema_version,
        }
        if source_id is not None:
            metadata["source_id"] = source_id
        if source_name is not None:
            metadata["source_name"] = source_name
        if details is not None:
            metadata["details"] = dict(details)
        return metadata

    def persist_refresh_metadata(
        self,
        *,
        storage: LocalStorage,
        dataset: DatasetName,
        metadata: Mapping[str, Any],
        layer: str = "meta",
        ext: str = "json",
    ) -> Path:
        return storage.write_metadata(dataset, metadata, layer=layer, ext=ext)

    def read_refresh_metadata(
        self,
        *,
        storage: LocalStorage,
        dataset: DatasetName,
        layer: str = "meta",
        ext: str = "json",
        on_missing: str = "empty",
    ) -> dict[str, Any]:
        return storage.read_metadata(
            dataset,
            layer=layer,
            ext=ext,
            on_missing=on_missing,
        )

    def build_quality_report_records(
        self,
        *,
        dataset: DatasetName,
        market: str,
        trade_date: date,
        records: Sequence[Mapping[str, Any]],
        empty_record_status: str = "warn",
        metadata_written: bool | None = None,
        metadata_error: str | None = None,
        source_ts: datetime | None = None,
    ) -> list[dict[str, Any]]:
        if empty_record_status not in _EMPTY_RECORD_STATUSES:
            allowed = ", ".join(sorted(_EMPTY_RECORD_STATUSES))
            raise ValueError(
                f"Unsupported empty_record_status: {empty_record_status!r}. Allowed: {allowed}"
            )
        if not isinstance(market, str) or market.strip() == "":
            raise ValueError("market must be a non-empty string.")

        created_at = self._now_fn().isoformat()
        quality_schema_version = self._registry.get(
            DatasetName.DATA_QUALITY_REPORT
        ).schema_version
        trade_date_text = trade_date.isoformat()

        def quality_record(
            *,
            check_name: str,
            status: str,
            severity: str,
            details: Mapping[str, Any],
        ) -> dict[str, Any]:
            record: dict[str, Any] = {
                "dataset": dataset.value,
                "market": market.strip(),
                "trade_date": trade_date_text,
                "check_name": check_name,
                "status": status,
                "severity": severity,
                "details": dict(details),
                "created_at": created_at,
                "source": LOCAL_QUALITY_SOURCE_ID,
                "ingested_at": created_at,
                "schema_version": quality_schema_version,
            }
            if source_ts is not None:
                record["source_ts"] = source_ts.isoformat()
            return record

        quality_records: list[dict[str, Any]] = []
        record_count = len(records)
        if record_count > 0:
            quality_records.append(
                quality_record(
                    check_name="record_count",
                    status="pass",
                    severity="low",
                    details={"record_count": record_count},
                )
            )
        else:
            quality_records.append(
                quality_record(
                    check_name="record_count",
                    status=empty_record_status,
                    severity="medium" if empty_record_status == "warn" else "high",
                    details={
                        "record_count": 0,
                        "empty_record_status": empty_record_status,
                    },
                )
            )

        quality_records.append(
            self._schema_validation_record(
                dataset=dataset,
                records=records,
                quality_record=quality_record,
            )
        )

        if metadata_written is not None:
            metadata_status = "pass" if metadata_written else "fail"
            metadata_severity = "low" if metadata_written else "high"
            metadata_details: dict[str, Any] = {"metadata_written": metadata_written}
            if metadata_error is not None:
                metadata_details["metadata_error"] = metadata_error
            quality_records.append(
                quality_record(
                    check_name="metadata_written",
                    status=metadata_status,
                    severity=metadata_severity,
                    details=metadata_details,
                )
            )

        return quality_records

    def _schema_validation_record(
        self,
        *,
        dataset: DatasetName,
        records: Sequence[Mapping[str, Any]],
        quality_record: Callable[..., dict[str, Any]],
    ) -> dict[str, Any]:
        issues_by_record: list[dict[str, Any]] = []
        for record_index, record in enumerate(records):
            issues = self._registry.validate_record(dataset, record)
            if not issues:
                continue
            issues_by_record.append(
                {
                    "record_index": record_index,
                    "issues": [self._issue_to_dict(item) for item in issues],
                }
            )

        if not issues_by_record:
            return quality_record(
                check_name="schema_validation",
                status="pass",
                severity="low",
                details={
                    "validated_records": len(records),
                    "invalid_record_count": 0,
                    "issue_count": 0,
                },
            )

        issue_count = sum(len(item["issues"]) for item in issues_by_record)
        return quality_record(
            check_name="schema_validation",
            status="fail",
            severity="high",
            details={
                "validated_records": len(records),
                "invalid_record_count": len(issues_by_record),
                "issue_count": issue_count,
                "invalid_records": issues_by_record,
            },
        )

    def _issue_to_dict(self, issue: ValidationIssue) -> dict[str, str]:
        return {
            "field": issue.field,
            "code": issue.code,
            "message": issue.message,
        }


__all__ = [
    "LOCAL_QUALITY_SOURCE_ID",
    "LOCAL_QUALITY_SOURCE_NAME",
    "LocalRefreshQualityHelper",
]
