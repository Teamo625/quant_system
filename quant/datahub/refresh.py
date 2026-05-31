"""Local one-request warehouse refresh runner for DataHub."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from .datasets import DatasetName, DatasetRegistry
from .quality import LocalRefreshQualityHelper
from .source import SourceAdapter, SourceRequest, fetch_source_result
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
    source_result = fetch_source_result(adapter, request, fetched_at=fetched_at)
    records = [dict(record) for record in source_result.normalized_records]

    source_name = request.source_name or source_result.source_name
    source_id = request.source_id or request.source_name or source_result.source_name

    record_count = len(records)
    refresh_status = _resolve_refresh_status(
        record_count=record_count,
        empty_record_status=empty_record_status,
    )

    raw_path: Path | None = None
    curated_path: Path | None = None
    metadata_path: Path | None = None
    quality_path: Path | None = None

    execution_error: Exception | None = None

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
    except Exception as error:  # pragma: no cover - covered by failure-path tests
        execution_error = error
        refresh_status = "failed"

    completed_at = resolved_now_fn()
    metadata_error: str | None = None
    metadata_written = False

    metadata = resolved_quality_helper.build_refresh_metadata(
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
            "fetched_at": source_result.fetched_at.isoformat(),
            "produced_at": source_result.produced_at.isoformat()
            if source_result.produced_at
            else None,
            "error": str(execution_error) if execution_error else None,
        },
    )

    try:
        metadata_path = resolved_quality_helper.persist_refresh_metadata(
            storage=storage,
            dataset=request.dataset,
            metadata=metadata,
        )
        metadata_written = True
    except Exception as error:  # pragma: no cover - hard to deterministically force
        metadata_error = str(error)
        refresh_status = "failed"
        if execution_error is None:
            execution_error = error

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
        source_ts=source_result.produced_at,
    )

    quality_path = storage.write_records(
        DatasetName.DATA_QUALITY_REPORT,
        quality_records,
        layer="curated",
        ext="jsonl",
        validate_schema=True,
        registry=resolved_registry,
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
        fetched_at=source_result.fetched_at,
        produced_at=source_result.produced_at,
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


__all__ = [
    "LocalWarehouseRefreshError",
    "LocalWarehouseRefreshResult",
    "run_local_warehouse_refresh",
]
