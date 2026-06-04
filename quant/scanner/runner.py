"""Offline-safe in-memory scan runner primitives."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import asdict, is_dataclass
from typing import Any

from quant.features.contracts import FeatureName

from .contracts import (
    FeatureReference,
    FilterOperator,
    FilterSpec,
    ScanCandidateList,
    ScanCandidateRecord,
    ScanRunMetadata,
    ScannerContractIssue,
    UniverseMembershipInput,
    validate_filter_spec,
    validate_scan_candidate_list,
    validate_scan_run_metadata,
    validate_universe_membership_input,
)
from .matching import (
    InvalidFeatureValueError,
    InvalidFilterSpecError,
    MissingFeatureValueError,
    collect_matched_filter_ids,
)


class ScanRunnerError(ValueError):
    """Base error for offline scan runner failures."""


class InvalidScanRunnerInputError(ScanRunnerError):
    """Raised when caller-supplied runner inputs are malformed."""


class MissingSymbolFeatureValuesError(InvalidScanRunnerInputError):
    """Raised when a universe symbol has no feature-value payload."""


class InvalidScanOutputError(ScanRunnerError):
    """Raised when the generated candidate list fails contract validation."""


def run_scan(
    *,
    metadata: ScanRunMetadata | Mapping[str, Any],
    universe: UniverseMembershipInput | Mapping[str, Any],
    filters: Iterable[FilterSpec | Mapping[str, Any]],
    symbol_feature_values: Mapping[str, Mapping[FeatureReference, Any]],
) -> ScanCandidateList:
    """Build a validated candidate list from caller-supplied in-memory inputs."""
    normalized_metadata = _normalize_metadata(metadata)
    normalized_universe = _normalize_universe(universe)
    normalized_filters = _normalize_filters(filters)
    normalized_symbol_feature_values = _normalize_symbol_feature_values(
        symbol_feature_values,
        universe_symbols=normalized_universe.symbols,
    )

    candidates: list[ScanCandidateRecord] = []
    for symbol in normalized_universe.symbols:
        feature_values = normalized_symbol_feature_values[symbol]
        try:
            matched_filter_ids = collect_matched_filter_ids(
                normalized_filters,
                feature_values,
            )
        except MissingFeatureValueError as error:
            raise MissingFeatureValueError(f"symbol {symbol!r}: {error}") from error
        except InvalidFeatureValueError as error:
            raise InvalidFeatureValueError(f"symbol {symbol!r}: {error}") from error

        if len(matched_filter_ids) != len(normalized_filters):
            continue

        candidates.append(
            ScanCandidateRecord(
                run_id=normalized_metadata.run_id,
                trade_date=normalized_metadata.trade_date,
                symbol=symbol,
                market=normalized_universe.market,
                universe_id=normalized_universe.universe_id,
                matched_filter_ids=matched_filter_ids,
            )
        )

    candidate_list = ScanCandidateList(
        metadata=normalized_metadata,
        feature_refs=_collect_feature_refs(normalized_filters),
        filters=normalized_filters,
        candidates=tuple(sorted(candidates, key=lambda item: (item.symbol, item.market))),
    )
    output_issues = validate_scan_candidate_list(candidate_list)
    if output_issues:
        raise InvalidScanOutputError(
            "generated candidate list failed validation: "
            f"{_format_issue_summary(output_issues)}"
        )
    return candidate_list


def _normalize_metadata(
    metadata: ScanRunMetadata | Mapping[str, Any],
) -> ScanRunMetadata:
    try:
        issues = validate_scan_run_metadata(metadata)
    except TypeError as error:
        raise InvalidScanRunnerInputError(
            "invalid scan metadata: payload must be a dataclass instance or mapping"
        ) from error
    if issues:
        raise InvalidScanRunnerInputError(
            f"invalid scan metadata: {_format_issue_summary(issues)}"
        )

    payload = _as_mapping(metadata)
    return ScanRunMetadata(
        run_id=str(payload["run_id"]),
        scanner_id=str(payload["scanner_id"]),
        trade_date=str(payload["trade_date"]),
        universe_id=str(payload["universe_id"]),
        generated_at=payload["generated_at"],
        schema_version=str(payload["schema_version"]),
    )


def _normalize_universe(
    universe: UniverseMembershipInput | Mapping[str, Any],
) -> UniverseMembershipInput:
    try:
        issues = validate_universe_membership_input(universe)
    except TypeError as error:
        raise InvalidScanRunnerInputError(
            "invalid universe input: payload must be a dataclass instance or mapping"
        ) from error
    if issues:
        raise InvalidScanRunnerInputError(
            f"invalid universe input: {_format_issue_summary(issues)}"
        )

    payload = _as_mapping(universe)
    return UniverseMembershipInput(
        universe_id=str(payload["universe_id"]),
        universe_name=str(payload["universe_name"]),
        market=str(payload["market"]),
        as_of_date=str(payload["as_of_date"]),
        symbols=tuple(str(symbol) for symbol in payload["symbols"]),
    )


def _normalize_filters(
    filters: Iterable[FilterSpec | Mapping[str, Any]],
) -> tuple[FilterSpec, ...]:
    if isinstance(filters, (str, bytes)) or not isinstance(filters, Iterable):
        raise InvalidScanRunnerInputError(
            "filters must be an iterable of FilterSpec instances or mappings"
        )

    normalized_filters: list[FilterSpec] = []
    seen_filter_ids: set[str] = set()

    for index, filter_spec in enumerate(filters):
        normalized_filter = _normalize_filter_spec(filter_spec)
        if normalized_filter.filter_id in seen_filter_ids:
            raise InvalidFilterSpecError(
                "invalid filter spec collection: duplicate filter_id "
                f"{normalized_filter.filter_id!r} at filters[{index}]"
            )
        seen_filter_ids.add(normalized_filter.filter_id)
        normalized_filters.append(normalized_filter)

    return tuple(normalized_filters)


def _normalize_filter_spec(filter_spec: FilterSpec | Mapping[str, Any]) -> FilterSpec:
    try:
        issues = validate_filter_spec(filter_spec)
    except TypeError as error:
        raise InvalidFilterSpecError(
            "invalid filter spec: payload must be a dataclass instance or mapping"
        ) from error
    if issues:
        raise InvalidFilterSpecError(
            f"invalid filter spec: {_format_issue_summary(issues)}"
        )

    payload = _as_mapping(filter_spec)
    feature_ref_payload = _as_mapping(payload["feature_ref"])
    operator = _coerce_filter_operator(payload["operator"])
    threshold = payload["threshold"]

    return FilterSpec(
        filter_id=str(payload["filter_id"]),
        feature_ref=FeatureReference(
            feature_name=_coerce_feature_name(feature_ref_payload["feature_name"]),
            lag_days=int(feature_ref_payload["lag_days"]),
        ),
        operator=operator,
        threshold=(
            (threshold[0], threshold[1])
            if operator is FilterOperator.BETWEEN
            else threshold
        ),
    )


def _normalize_symbol_feature_values(
    symbol_feature_values: Mapping[str, Mapping[FeatureReference, Any]],
    *,
    universe_symbols: tuple[str, ...],
) -> dict[str, dict[FeatureReference, Any]]:
    if not isinstance(symbol_feature_values, Mapping):
        raise InvalidScanRunnerInputError(
            "symbol_feature_values must be a mapping keyed by symbol"
        )

    normalized: dict[str, dict[FeatureReference, Any]] = {}
    for symbol, feature_values in symbol_feature_values.items():
        if not isinstance(symbol, str) or symbol.strip() == "":
            raise InvalidScanRunnerInputError(
                "symbol_feature_values keys must be non-empty strings"
            )
        if not isinstance(feature_values, Mapping):
            raise InvalidScanRunnerInputError(
                f"symbol_feature_values[{symbol!r}] must be a mapping keyed by FeatureReference"
            )

        symbol_values: dict[FeatureReference, Any] = {}
        for feature_ref, value in feature_values.items():
            if not isinstance(feature_ref, FeatureReference):
                raise InvalidScanRunnerInputError(
                    f"symbol_feature_values[{symbol!r}] keys must be FeatureReference instances"
                )
            symbol_values[feature_ref] = value
        normalized[symbol] = symbol_values

    missing_symbols = sorted(
        symbol for symbol in universe_symbols if symbol not in normalized
    )
    if missing_symbols:
        raise MissingSymbolFeatureValuesError(
            "missing symbol feature values for symbols: "
            f"{missing_symbols!r}"
        )

    unexpected_symbols = sorted(
        symbol for symbol in normalized if symbol not in set(universe_symbols)
    )
    if unexpected_symbols:
        raise InvalidScanRunnerInputError(
            "symbol_feature_values contains symbols outside the universe: "
            f"{unexpected_symbols!r}"
        )

    return normalized


def _collect_feature_refs(filters: tuple[FilterSpec, ...]) -> tuple[FeatureReference, ...]:
    feature_refs: list[FeatureReference] = []
    seen: set[FeatureReference] = set()
    for filter_spec in filters:
        if filter_spec.feature_ref in seen:
            continue
        seen.add(filter_spec.feature_ref)
        feature_refs.append(filter_spec.feature_ref)
    return tuple(feature_refs)


def _as_mapping(payload: Any) -> dict[str, Any]:
    if is_dataclass(payload) and not isinstance(payload, type):
        return asdict(payload)
    if isinstance(payload, Mapping):
        return dict(payload)
    raise InvalidScanRunnerInputError(
        "runner payload must be a dataclass instance or mapping"
    )


def _coerce_feature_name(value: Any) -> FeatureName:
    if isinstance(value, FeatureName):
        return value
    return FeatureName(str(value))


def _coerce_filter_operator(value: Any) -> FilterOperator:
    if isinstance(value, FilterOperator):
        return value
    return FilterOperator(str(value))


def _format_issue_summary(issues: tuple[ScannerContractIssue, ...]) -> str:
    return "; ".join(
        f"{issue.field}: {issue.code} ({issue.message})" for issue in issues
    )


__all__ = [
    "InvalidScanOutputError",
    "InvalidScanRunnerInputError",
    "MissingSymbolFeatureValuesError",
    "ScanRunnerError",
    "run_scan",
]
