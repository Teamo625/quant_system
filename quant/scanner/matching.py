"""Offline-safe filter matching primitives for declarative scanner filters."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from math import isfinite
from typing import Any, Iterable, Mapping

from quant.features.contracts import FeatureName

from .contracts import FeatureReference, FilterOperator, FilterSpec, validate_filter_spec


class FilterMatchingError(ValueError):
    """Base error for deterministic filter matching failures."""


class InvalidFilterSpecError(FilterMatchingError):
    """Raised when a supplied filter spec fails validation."""


class MissingFeatureValueError(FilterMatchingError):
    """Raised when a required feature reference is absent from caller inputs."""


class InvalidFeatureValueError(FilterMatchingError):
    """Raised when a caller-provided feature value cannot be evaluated."""


def match_filter_spec(
    filter_spec: FilterSpec | Mapping[str, Any],
    feature_values: Mapping[FeatureReference, Any],
) -> bool:
    """Evaluate one declarative filter against caller-provided feature values."""
    normalized_feature_values = _normalize_feature_values(feature_values)
    normalized_spec = _normalize_filter_spec(filter_spec)
    return _evaluate_filter_spec(
        filter_spec=normalized_spec,
        feature_values=normalized_feature_values,
    )


def collect_matched_filter_ids(
    filters: Iterable[FilterSpec | Mapping[str, Any]],
    feature_values: Mapping[FeatureReference, Any],
) -> tuple[str, ...]:
    """Return matched filter ids in caller-supplied filter order."""
    normalized_feature_values = _normalize_feature_values(feature_values)
    matched_filter_ids: list[str] = []
    seen_filter_ids: set[str] = set()

    for index, filter_spec in enumerate(filters):
        normalized_spec = _normalize_filter_spec(filter_spec)
        if normalized_spec.filter_id in seen_filter_ids:
            raise InvalidFilterSpecError(
                "invalid filter spec collection: duplicate filter_id "
                f"{normalized_spec.filter_id!r} at filters[{index}]"
            )
        seen_filter_ids.add(normalized_spec.filter_id)
        if _evaluate_filter_spec(
            filter_spec=normalized_spec,
            feature_values=normalized_feature_values,
        ):
            matched_filter_ids.append(normalized_spec.filter_id)

    return tuple(matched_filter_ids)


def _evaluate_filter_spec(
    *,
    filter_spec: FilterSpec,
    feature_values: Mapping[FeatureReference, Any],
) -> bool:
    if filter_spec.feature_ref not in feature_values:
        raise MissingFeatureValueError(
            "missing feature value for "
            f"{_format_feature_ref(filter_spec.feature_ref)} "
            f"required by filter_id={filter_spec.filter_id!r}"
        )

    value = feature_values[filter_spec.feature_ref]
    operator = filter_spec.operator
    threshold = filter_spec.threshold

    if operator in {
        FilterOperator.GT,
        FilterOperator.GTE,
        FilterOperator.LT,
        FilterOperator.LTE,
        FilterOperator.BETWEEN,
    }:
        numeric_value = _coerce_numeric_feature_value(
            value,
            feature_ref=filter_spec.feature_ref,
        )
        if operator is FilterOperator.GT:
            return numeric_value > float(threshold)
        if operator is FilterOperator.GTE:
            return numeric_value >= float(threshold)
        if operator is FilterOperator.LT:
            return numeric_value < float(threshold)
        if operator is FilterOperator.LTE:
            return numeric_value <= float(threshold)
        lower, upper = threshold
        return float(lower) <= numeric_value <= float(upper)

    if isinstance(threshold, str):
        text_value = _coerce_text_feature_value(
            value,
            feature_ref=filter_spec.feature_ref,
        )
        return (
            text_value == threshold
            if operator is FilterOperator.EQ
            else text_value != threshold
        )

    numeric_value = _coerce_numeric_feature_value(
        value,
        feature_ref=filter_spec.feature_ref,
    )
    return (
        numeric_value == float(threshold)
        if operator is FilterOperator.EQ
        else numeric_value != float(threshold)
    )


def _normalize_filter_spec(filter_spec: FilterSpec | Mapping[str, Any]) -> FilterSpec:
    issues = validate_filter_spec(filter_spec)
    if issues:
        details = "; ".join(
            f"{issue.field}: {issue.code} ({issue.message})" for issue in issues
        )
        raise InvalidFilterSpecError(f"invalid filter spec: {details}")

    payload = _as_mapping(filter_spec)
    feature_ref_payload = _as_mapping(payload["feature_ref"])
    threshold = payload["threshold"]

    return FilterSpec(
        filter_id=str(payload["filter_id"]),
        feature_ref=FeatureReference(
            feature_name=_coerce_feature_name(feature_ref_payload["feature_name"]),
            lag_days=int(feature_ref_payload["lag_days"]),
        ),
        operator=_coerce_filter_operator(payload["operator"]),
        threshold=(
            (threshold[0], threshold[1])
            if _coerce_filter_operator(payload["operator"]) is FilterOperator.BETWEEN
            else threshold
        ),
    )


def _normalize_feature_values(
    feature_values: Mapping[FeatureReference, Any],
) -> dict[FeatureReference, Any]:
    if not isinstance(feature_values, Mapping):
        raise InvalidFeatureValueError(
            "feature_values must be a mapping keyed by FeatureReference"
        )

    normalized: dict[FeatureReference, Any] = {}
    for key, value in feature_values.items():
        if not isinstance(key, FeatureReference):
            raise InvalidFeatureValueError(
                "feature_values keys must be FeatureReference instances"
            )
        normalized[key] = value

    return normalized


def _coerce_numeric_feature_value(
    value: Any,
    *,
    feature_ref: FeatureReference,
) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
        raise InvalidFeatureValueError(
            "feature value for "
            f"{_format_feature_ref(feature_ref)} "
            "must be a finite numeric value"
        )
    return float(value)


def _coerce_text_feature_value(
    value: Any,
    *,
    feature_ref: FeatureReference,
) -> str:
    if not isinstance(value, str) or value.strip() == "":
        raise InvalidFeatureValueError(
            "feature value for "
            f"{_format_feature_ref(feature_ref)} "
            "must be a non-empty string"
        )
    return value


def _as_mapping(payload: Any) -> dict[str, Any]:
    if is_dataclass(payload):
        return asdict(payload)
    if isinstance(payload, Mapping):
        return dict(payload)
    raise InvalidFilterSpecError("invalid filter spec: payload must be a dataclass or mapping")


def _coerce_feature_name(value: Any) -> FeatureName:
    if isinstance(value, FeatureName):
        return value
    return FeatureName(str(value))


def _coerce_filter_operator(value: Any) -> FilterOperator:
    if isinstance(value, FilterOperator):
        return value
    return FilterOperator(str(value))


def _format_feature_ref(feature_ref: FeatureReference) -> str:
    return f"{feature_ref.feature_name.value}[lag_days={feature_ref.lag_days}]"


__all__ = [
    "FilterMatchingError",
    "InvalidFeatureValueError",
    "InvalidFilterSpecError",
    "MissingFeatureValueError",
    "collect_matched_filter_ids",
    "match_filter_spec",
]
