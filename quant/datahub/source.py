"""Source adapter contract primitives for DataHub ingestion."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
import re
from typing import Any, Mapping, Protocol, Sequence, runtime_checkable

from .datasets import DatasetName


@runtime_checkable
class SourceAdapter(Protocol):
    """Adapter contract for source-specific dataset fetching.

    Concrete adapters are intentionally deferred to Phase 2 tasks.
    """

    source_name: str

    def fetch(
        self,
        dataset: DatasetName,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
        symbols: list[str] | None = None,
    ) -> Any:
        """Return dataset payload from a source implementation."""


class SourceAdapterContractError(TypeError):
    """Raised when a source adapter does not satisfy contract expectations."""


class SourcePayloadNormalizationError(ValueError):
    """Raised when adapter payload cannot be normalized into record dictionaries."""


SOURCE_AVAILABILITY_HEALTH_CHECK_NAME = "source_availability_health"
_SOURCE_HEALTH_CATEGORIES: frozenset[str] = frozenset(
    {
        "success",
        "empty_result",
        "schema_validation_failed",
        "fetch_failed",
        "unsupported_request",
        "metadata_write_failed",
        "persistence_failed",
    }
)
_SOURCE_HEALTH_SYMBOL_PREVIEW_LIMIT = 5
_SOURCE_HEALTH_MESSAGE_LIMIT = 240
_UPSTREAM_LIKE_ERROR_HINTS: tuple[str, ...] = (
    "connection",
    "timeout",
    "timed out",
    "dns",
    "tls",
    "ssl",
    "proxy",
    "network",
    "upstream",
    "temporarily unavailable",
    "service unavailable",
    "name or service not known",
    "connection reset",
    "connection refused",
    "remote disconnected",
    "max retries exceeded",
)
_UNSUPPORTED_REQUEST_HINTS: tuple[str, ...] = (
    "unsupported dataset",
    "unsupported request",
    "unexpected keyword argument",
    "required positional argument",
    "positional arguments but",
    "does not match sourcerequest",
    "does not match source request",
    "invalid sourcerequest",
    "invalid source request",
)


@dataclass(frozen=True)
class SourceRequest:
    """Runtime request metadata for one source adapter fetch call."""

    dataset: DatasetName
    source_name: str | None = None
    source_id: str | None = None
    source_catalog_entry_id: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    symbols: Sequence[str] | None = None

    def __post_init__(self) -> None:
        if isinstance(self.symbols, (str, bytes)):
            raise ValueError(
                "SourceRequest symbols must be a sequence of symbols, not bare str/bytes."
            )
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError(
                "Invalid SourceRequest date range: "
                f"start_date={self.start_date.isoformat()} > end_date={self.end_date.isoformat()}"
            )

    def fetch_symbols(self) -> list[str] | None:
        if self.symbols is None:
            return None
        return list(self.symbols)


@dataclass(frozen=True)
class SourceResult:
    """Canonical normalized source-fetch result for adapter contract flow."""

    request: SourceRequest
    source_name: str
    normalized_records: tuple[dict[str, Any], ...]
    record_count: int
    fetched_at: datetime
    produced_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.record_count != len(self.normalized_records):
            raise ValueError(
                "SourceResult record_count mismatch: "
                f"record_count={self.record_count}, records={len(self.normalized_records)}"
            )


def build_source_health_details(
    *,
    request: SourceRequest,
    source_name: str | None,
    source_id: str | None,
    failure_category: str,
    normalized_record_count: int,
    started_at: datetime | None = None,
    fetched_at: datetime | None = None,
    completed_at: datetime | None = None,
    produced_at: datetime | None = None,
    failure_message: str | None = None,
    secondary_failure_categories: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Build a stable source-health details payload for metadata and quality records."""
    if failure_category not in _SOURCE_HEALTH_CATEGORIES:
        allowed = ", ".join(sorted(_SOURCE_HEALTH_CATEGORIES))
        raise ValueError(
            f"Unsupported source health failure category: {failure_category!r}. Allowed: {allowed}"
        )
    if normalized_record_count < 0:
        raise ValueError("normalized_record_count must be non-negative.")

    resolved_source_name = source_name or request.source_name or "unknown_source"
    resolved_source_id = source_id or request.source_id or request.source_name or resolved_source_name
    sanitized_message = sanitize_source_health_message(failure_message)
    secondary_categories = _normalize_secondary_categories(
        secondary_failure_categories,
        primary=failure_category,
    )
    upstream_like = failure_category == "fetch_failed" and _is_upstream_like_message(
        sanitized_message
    )
    schema_like = failure_category == "schema_validation_failed"
    request_like = failure_category == "unsupported_request"
    operator_actionable = _is_operator_actionable(
        failure_category=failure_category,
        upstream_like=upstream_like,
    )

    details: dict[str, Any] = {
        "source_id": resolved_source_id,
        "source_name": resolved_source_name,
        "source_catalog_entry_id": request.source_catalog_entry_id,
        "requested_dataset": request.dataset.value,
        "requested_date_range": {
            "start_date": request.start_date.isoformat() if request.start_date else None,
            "end_date": request.end_date.isoformat() if request.end_date else None,
        },
        "requested_symbols_count": len(request.symbols) if request.symbols is not None else 0,
        "requested_symbols_preview": list(request.symbols[:_SOURCE_HEALTH_SYMBOL_PREVIEW_LIMIT])
        if request.symbols is not None
        else [],
        "normalized_record_count": int(normalized_record_count),
        "fetch_status": _resolve_fetch_status(failure_category),
        "availability_status": _resolve_availability_status(
            failure_category=failure_category,
            upstream_like=upstream_like,
        ),
        "failure_category": failure_category,
        "failure_message": sanitized_message,
        "operator_actionable": operator_actionable,
        "upstream_or_network_like": upstream_like,
        "schema_or_data_quality_like": schema_like,
        "request_or_configuration_like": request_like,
        "started_at": started_at.isoformat() if started_at else None,
        "fetched_at": fetched_at.isoformat() if fetched_at else None,
        "completed_at": completed_at.isoformat() if completed_at else None,
    }
    if produced_at is not None:
        details["produced_at"] = produced_at.isoformat()
    if secondary_categories:
        details["secondary_failure_categories"] = secondary_categories
    return details


def classify_source_health_failure(error: Exception, *, stage: str) -> str:
    """Map a refresh-stage exception to a stable source-health category."""
    if stage == "schema_validation":
        return "schema_validation_failed"
    if stage == "metadata_write":
        return "metadata_write_failed"
    if stage == "persistence":
        return "persistence_failed"
    if stage != "fetch":
        raise ValueError(f"Unsupported source health failure stage: {stage!r}")
    if _is_unsupported_request_error(error):
        return "unsupported_request"
    return "fetch_failed"


def sanitize_source_health_message(message: str | None) -> str | None:
    """Collapse exception text into a bounded, single-line diagnostic string."""
    if message is None:
        return None
    normalized = re.sub(r"\s+", " ", message).strip()
    if normalized == "":
        return None
    if len(normalized) <= _SOURCE_HEALTH_MESSAGE_LIMIT:
        return normalized
    return normalized[: _SOURCE_HEALTH_MESSAGE_LIMIT - 3].rstrip() + "..."


def normalize_source_payload(payload: Any) -> list[dict[str, Any]]:
    """Normalize supported adapter payloads into list[dict] records."""
    if isinstance(payload, SourceResult):
        return _normalize_mapping_records(payload.normalized_records, context="SourceResult")

    if isinstance(payload, list):
        return _normalize_mapping_records(payload, context="payload")

    raise SourcePayloadNormalizationError(
        "Unsupported source payload shape: "
        f"{type(payload).__name__}. Expected SourceResult or list of mapping records."
    )


def fetch_source_result(
    adapter: SourceAdapter,
    request: SourceRequest,
    *,
    fetched_at: datetime | None = None,
) -> SourceResult:
    """Fetch one dataset payload through SourceAdapter and normalize to SourceResult."""
    if not isinstance(adapter, SourceAdapter):
        raise SourceAdapterContractError(
            "Adapter does not satisfy SourceAdapter protocol contract."
        )

    if request.source_name and request.source_name != adapter.source_name:
        raise SourceAdapterContractError(
            "SourceRequest source_name does not match adapter source_name: "
            f"request={request.source_name!r}, adapter={adapter.source_name!r}"
        )

    payload = adapter.fetch(
        request.dataset,
        start_date=request.start_date,
        end_date=request.end_date,
        symbols=request.fetch_symbols(),
    )

    resolved_fetched_at = fetched_at or datetime.now(timezone.utc)
    if isinstance(payload, SourceResult):
        _validate_canonical_result_metadata(
            payload=payload,
            request=request,
            adapter_source_name=adapter.source_name,
        )
        return SourceResult(
            request=request,
            source_name=payload.source_name,
            normalized_records=tuple(normalize_source_payload(payload)),
            record_count=payload.record_count,
            fetched_at=resolved_fetched_at,
            produced_at=payload.produced_at,
        )

    normalized_records = normalize_source_payload(payload)
    return SourceResult(
        request=request,
        source_name=adapter.source_name,
        normalized_records=tuple(normalized_records),
        record_count=len(normalized_records),
        fetched_at=resolved_fetched_at,
        produced_at=None,
    )


def _normalize_mapping_records(
    payload_records: Sequence[Any],
    *,
    context: str,
) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for idx, record in enumerate(payload_records):
        if not isinstance(record, Mapping):
            raise SourcePayloadNormalizationError(
                f"{context} record at index {idx} is not a mapping: {type(record).__name__}"
            )
        normalized.append(dict(record))
    return normalized


def _validate_canonical_result_metadata(
    *,
    payload: SourceResult,
    request: SourceRequest,
    adapter_source_name: str,
) -> None:
    if payload.request.dataset != request.dataset:
        raise SourceAdapterContractError(
            "SourceResult dataset does not match SourceRequest dataset: "
            f"result={payload.request.dataset.value!r}, request={request.dataset.value!r}"
        )

    if payload.source_name != adapter_source_name:
        raise SourceAdapterContractError(
            "SourceResult source_name does not match adapter source_name: "
            f"result={payload.source_name!r}, adapter={adapter_source_name!r}"
        )

    if payload.request.start_date != request.start_date:
        raise SourceAdapterContractError(
            "SourceResult start_date does not match SourceRequest start_date: "
            f"result={payload.request.start_date!r}, request={request.start_date!r}"
        )

    if payload.request.end_date != request.end_date:
        raise SourceAdapterContractError(
            "SourceResult end_date does not match SourceRequest end_date: "
            f"result={payload.request.end_date!r}, request={request.end_date!r}"
        )

    if not _symbols_match(payload.request.symbols, request.symbols):
        raise SourceAdapterContractError(
            "SourceResult symbols do not match SourceRequest symbols: "
            f"result={payload.request.symbols!r}, request={request.symbols!r}"
        )


def _symbols_match(
    left: Sequence[str] | None,
    right: Sequence[str] | None,
) -> bool:
    if left is None and right is None:
        return True
    if left is None or right is None:
        return False
    return tuple(left) == tuple(right)


def _normalize_secondary_categories(
    categories: Sequence[str] | None,
    *,
    primary: str,
) -> list[str]:
    if categories is None:
        return []
    normalized: list[str] = []
    for category in categories:
        if category not in _SOURCE_HEALTH_CATEGORIES:
            allowed = ", ".join(sorted(_SOURCE_HEALTH_CATEGORIES))
            raise ValueError(
                f"Unsupported source health failure category: {category!r}. Allowed: {allowed}"
            )
        if category == primary or category in normalized:
            continue
        normalized.append(category)
    return normalized


def _is_operator_actionable(*, failure_category: str, upstream_like: bool) -> bool:
    if failure_category in {"success", "empty_result"}:
        return False
    if failure_category == "fetch_failed":
        return not upstream_like
    return True


def _resolve_fetch_status(failure_category: str) -> str:
    if failure_category == "success":
        return "success"
    if failure_category == "empty_result":
        return "empty_result"
    return "failed"


def _resolve_availability_status(*, failure_category: str, upstream_like: bool) -> str:
    if failure_category in {"success", "empty_result"}:
        return "available"
    if failure_category == "unsupported_request":
        return "unsupported"
    if failure_category == "fetch_failed" and upstream_like:
        return "unavailable"
    return "degraded"


def _is_unsupported_request_error(error: Exception) -> bool:
    if isinstance(error, SourceAdapterContractError):
        return True

    message = sanitize_source_health_message(str(error)) or ""
    lowered = message.lower()
    if any(hint in lowered for hint in _UNSUPPORTED_REQUEST_HINTS):
        return True

    return isinstance(error, TypeError)


def _is_upstream_like_message(message: str | None) -> bool:
    if message is None:
        return False
    lowered = message.lower()
    return any(hint in lowered for hint in _UPSTREAM_LIKE_ERROR_HINTS)
