"""Local one-request warehouse refresh runner for DataHub."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from .datasets import DatasetName, DatasetRegistry
from .quality import LocalRefreshQualityHelper
from .source import (
    SourceAdapter,
    SourceRequest,
    build_source_health_details,
    classify_source_health_failure,
    fetch_source_result,
    sanitize_source_health_message,
)
from .storage import LocalStorage


@dataclass(frozen=True)
class LocalWarehouseRefreshResult:
    """Structured output for one local warehouse refresh run."""

    dataset: DatasetName
    source_id: str
    source_name: str
    record_count: int
    refresh_status: str
    success: bool
    raw_path: Path
    curated_path: Path | None
    metadata_path: Path | None
    quality_path: Path
    quality_records: tuple[dict[str, Any], ...]
    fetched_at: datetime
    produced_at: datetime | None


class LocalWarehouseRefreshError(RuntimeError):
    """Raised when local refresh persistence fails."""


def run_local_warehouse_refresh(
    adapter: SourceAdapter,
    request: SourceRequest,
    storage: LocalStorage,
    *,
    registry: DatasetRegistry | None = None,
    quality_helper: LocalRefreshQualityHelper | None = None,
    fetched_at: datetime | None = None,
    now_fn: Callable[[], datetime] | None = None,
    empty_record_status: str = "warn",
) -> LocalWarehouseRefreshResult:
    """Run one adapter/request refresh into local raw, curated, metadata, and quality layers."""
    resolved_registry = registry or DatasetRegistry()
    resolved_now_fn = now_fn or (lambda: datetime.now(timezone.utc))
    resolved_quality_helper = quality_helper or LocalRefreshQualityHelper(
        registry=resolved_registry,
        now_fn=resolved_now_fn,
    )

    started_at = resolved_now_fn()
    source_name = request.source_name or getattr(adapter, "source_name", None) or "unknown_source"
    source_id = request.source_id or request.source_name or source_name
    fetched_timestamp: datetime | None = None
    produced_at: datetime | None = None
    records: list[dict[str, Any]] = []
    record_count = 0
    refresh_status = "failed"
    failure_category = "success"
    secondary_failure_categories: list[str] = []

    raw_path: Path | None = None
    curated_path: Path | None = None
    metadata_path: Path | None = None
    quality_path: Path | None = None

    execution_error: Exception | None = None
    metadata_error: str | None = None
    metadata_written = False

    try:
        source_result = fetch_source_result(adapter, request, fetched_at=fetched_at)
    except Exception as error:  # pragma: no cover - covered by failure-path tests
        execution_error = error
        refresh_status = "failed"
        failure_category = classify_source_health_failure(error, stage="fetch")
    else:
        records = [dict(record) for record in source_result.normalized_records]
        source_name = request.source_name or source_result.source_name
        source_id = request.source_id or request.source_name or source_result.source_name
        fetched_timestamp = source_result.fetched_at
        produced_at = source_result.produced_at
        record_count = len(records)
        refresh_status = _resolve_refresh_status(
            record_count=record_count,
            empty_record_status=empty_record_status,
        )
        failure_category = "success" if record_count > 0 else "empty_result"

        try:
            raw_path = storage.write_records(
                request.dataset,
                records,
                layer="raw",
                ext="jsonl",
                validate_schema=False,
            )
            _validate_records_for_curated_write(
                registry=resolved_registry,
                dataset=request.dataset,
                records=records,
            )
            curated_path = storage.write_records(
                request.dataset,
                records,
                layer="curated",
                ext="jsonl",
                validate_schema=True,
                registry=resolved_registry,
            )
        except ValueError as error:
            execution_error = error
            refresh_status = "failed"
            failure_category = classify_source_health_failure(
                error,
                stage="schema_validation" if _is_schema_validation_error(error) else "persistence",
            )
        except Exception as error:  # pragma: no cover - covered by failure-path tests
            execution_error = error
            refresh_status = "failed"
            failure_category = classify_source_health_failure(error, stage="persistence")

    completed_at = resolved_now_fn()
    source_health_details = build_source_health_details(
        request=request,
        source_name=source_name,
        source_id=source_id,
        failure_category=failure_category,
        normalized_record_count=record_count,
        started_at=started_at,
        fetched_at=fetched_timestamp,
        completed_at=completed_at,
        produced_at=produced_at,
        failure_message=str(execution_error) if execution_error else None,
        secondary_failure_categories=secondary_failure_categories,
    )

    metadata = _build_refresh_metadata(
        quality_helper=resolved_quality_helper,
        request=request,
        source_id=source_id,
        source_name=source_name,
        record_count=record_count,
        refresh_status=refresh_status,
        started_at=started_at,
        completed_at=completed_at,
        raw_path=raw_path,
        curated_path=curated_path,
        fetched_timestamp=fetched_timestamp,
        produced_at=produced_at,
        execution_error=execution_error,
        source_health_details=source_health_details,
    )

    try:
        metadata_path = resolved_quality_helper.persist_refresh_metadata(
            storage=storage,
            dataset=request.dataset,
            metadata=metadata,
        )
        metadata_written = True
    except Exception as error:  # pragma: no cover - hard to deterministically force
        metadata_error = sanitize_source_health_message(str(error))
        refresh_status = "failed"
        if execution_error is None:
            execution_error = error
            failure_category = classify_source_health_failure(error, stage="metadata_write")
        else:
            _append_secondary_failure_category(
                secondary_failure_categories,
                classify_source_health_failure(error, stage="metadata_write"),
            )

        source_health_details = build_source_health_details(
            request=request,
            source_name=source_name,
            source_id=source_id,
            failure_category=failure_category,
            normalized_record_count=record_count,
            started_at=started_at,
            fetched_at=fetched_timestamp,
            completed_at=completed_at,
            produced_at=produced_at,
            failure_message=str(execution_error) if execution_error else metadata_error,
            secondary_failure_categories=secondary_failure_categories,
        )

    quality_records = resolved_quality_helper.build_quality_report_records(
        dataset=request.dataset,
        market=_resolve_market(records),
        trade_date=_resolve_trade_date(
            records=records,
            request=request,
            now_fn=resolved_now_fn,
        ),
        records=records,
        empty_record_status=empty_record_status,
        metadata_written=metadata_written,
        metadata_error=metadata_error,
        source_ts=produced_at,
        source_health_details=source_health_details,
    )

    try:
        quality_path = storage.write_records(
            DatasetName.DATA_QUALITY_REPORT,
            quality_records,
            layer="curated",
            ext="jsonl",
            validate_schema=True,
            registry=resolved_registry,
        )
    except Exception as error:  # pragma: no cover - covered by failure-path tests
        refresh_status = "failed"
        if execution_error is None:
            execution_error = error
            failure_category = classify_source_health_failure(error, stage="persistence")
        else:
            _append_secondary_failure_category(
                secondary_failure_categories,
                classify_source_health_failure(error, stage="persistence"),
            )

        source_health_details = build_source_health_details(
            request=request,
            source_name=source_name,
            source_id=source_id,
            failure_category=failure_category,
            normalized_record_count=record_count,
            started_at=started_at,
            fetched_at=fetched_timestamp,
            completed_at=completed_at,
            produced_at=produced_at,
            failure_message=str(execution_error),
            secondary_failure_categories=secondary_failure_categories,
        )
        _best_effort_rewrite_refresh_metadata(
            storage=storage,
            request=request,
            quality_helper=resolved_quality_helper,
            metadata_written=metadata_written,
            source_id=source_id,
            source_name=source_name,
            record_count=record_count,
            refresh_status=refresh_status,
            started_at=started_at,
            completed_at=completed_at,
            raw_path=raw_path,
            curated_path=curated_path,
            fetched_timestamp=fetched_timestamp,
            produced_at=produced_at,
            execution_error=execution_error,
            source_health_details=source_health_details,
        )

    if execution_error is not None:
        raise LocalWarehouseRefreshError(
            f"Local warehouse refresh failed for dataset={request.dataset.value}: {execution_error}"
        ) from execution_error

    return LocalWarehouseRefreshResult(
        dataset=request.dataset,
        source_id=source_id,
        source_name=source_name,
        record_count=record_count,
        refresh_status=refresh_status,
        success=refresh_status != "failed",
        raw_path=raw_path,
        curated_path=curated_path,
        metadata_path=metadata_path,
        quality_path=quality_path,
        quality_records=tuple(quality_records),
        fetched_at=fetched_timestamp or started_at,
        produced_at=produced_at,
    )


def _resolve_refresh_status(*, record_count: int, empty_record_status: str) -> str:
    if record_count > 0:
        return "success"
    if empty_record_status == "warn":
        return "warning"
    if empty_record_status == "fail":
        return "failed"
    raise ValueError(
        "Unsupported empty_record_status: "
        f"{empty_record_status!r}. Allowed: fail, warn"
    )


def _resolve_market(records: Sequence[Mapping[str, Any]]) -> str:
    if not records:
        return "UNKNOWN"

    first = records[0]
    market = first.get("market")
    if isinstance(market, str) and market.strip():
        return market.strip()

    region = first.get("region")
    if isinstance(region, str) and region.strip():
        return region.strip()

    return "UNKNOWN"


def _resolve_trade_date(
    *,
    records: Sequence[Mapping[str, Any]],
    request: SourceRequest,
    now_fn: Callable[[], datetime],
) -> date:
    candidate_fields = (
        "trade_date",
        "observation_date",
        "publish_date",
        "event_date",
        "in_date",
        "report_date",
        "release_date",
        "publish_time",
    )
    if records:
        first = records[0]
        for key in candidate_fields:
            if key not in first:
                continue
            parsed = _coerce_date(first[key])
            if parsed is not None:
                return parsed

    if request.end_date is not None:
        return request.end_date
    if request.start_date is not None:
        return request.start_date

    return now_fn().date()


def _coerce_date(value: Any) -> date | None:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    if not isinstance(value, str):
        return None

    try:
        return date.fromisoformat(value)
    except ValueError:
        pass

    try:
        return datetime.fromisoformat(value).date()
    except ValueError:
        return None


def _validate_records_for_curated_write(
    *,
    registry: DatasetRegistry,
    dataset: DatasetName,
    records: Sequence[Mapping[str, Any]],
) -> None:
    for index, record in enumerate(records):
        issues = registry.validate_record(dataset, record)
        if not issues:
            continue
        issue_text = "; ".join(f"{item.code}:{item.field}" for item in issues)
        raise ValueError(
            f"Record {index} failed schema validation: {issue_text}"
        )


def _build_refresh_metadata(
    *,
    quality_helper: LocalRefreshQualityHelper,
    request: SourceRequest,
    source_id: str,
    source_name: str,
    record_count: int,
    refresh_status: str,
    started_at: datetime,
    completed_at: datetime,
    raw_path: Path | None,
    curated_path: Path | None,
    fetched_timestamp: datetime | None,
    produced_at: datetime | None,
    execution_error: Exception | None,
    source_health_details: Mapping[str, Any],
) -> dict[str, Any]:
    return quality_helper.build_refresh_metadata(
        request.dataset,
        layer="curated",
        source_id=source_id,
        source_name=source_name,
        record_count=record_count,
        status=refresh_status,
        started_at=started_at,
        completed_at=completed_at,
        details={
            "source_catalog_entry_id": request.source_catalog_entry_id,
            "raw_path": str(raw_path) if raw_path else None,
            "curated_path": str(curated_path) if curated_path else None,
            "fetched_at": fetched_timestamp.isoformat() if fetched_timestamp else None,
            "produced_at": produced_at.isoformat() if produced_at else None,
            "error": sanitize_source_health_message(str(execution_error))
            if execution_error
            else None,
            "source_health": dict(source_health_details),
        },
    )


def _best_effort_rewrite_refresh_metadata(
    *,
    storage: LocalStorage,
    request: SourceRequest,
    quality_helper: LocalRefreshQualityHelper,
    metadata_written: bool,
    source_id: str,
    source_name: str,
    record_count: int,
    refresh_status: str,
    started_at: datetime,
    completed_at: datetime,
    raw_path: Path | None,
    curated_path: Path | None,
    fetched_timestamp: datetime | None,
    produced_at: datetime | None,
    execution_error: Exception | None,
    source_health_details: Mapping[str, Any],
) -> None:
    if not metadata_written:
        return
    metadata = _build_refresh_metadata(
        quality_helper=quality_helper,
        request=request,
        source_id=source_id,
        source_name=source_name,
        record_count=record_count,
        refresh_status=refresh_status,
        started_at=started_at,
        completed_at=completed_at,
        raw_path=raw_path,
        curated_path=curated_path,
        fetched_timestamp=fetched_timestamp,
        produced_at=produced_at,
        execution_error=execution_error,
        source_health_details=source_health_details,
    )
    try:
        quality_helper.persist_refresh_metadata(
            storage=storage,
            dataset=request.dataset,
            metadata=metadata,
        )
    except Exception:
        return


def _append_secondary_failure_category(
    categories: list[str],
    category: str,
) -> None:
    if category not in categories:
        categories.append(category)


def _is_schema_validation_error(error: ValueError) -> bool:
    return "failed schema validation" in str(error)


__all__ = [
    "LocalWarehouseRefreshError",
    "LocalWarehouseRefreshResult",
    "run_local_warehouse_refresh",
]
