"""Source adapter contract primitives for DataHub ingestion."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
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
