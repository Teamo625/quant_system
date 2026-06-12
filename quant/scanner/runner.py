"""Offline-safe in-memory scan runner primitives."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass, is_dataclass
from datetime import date
from enum import Enum
from typing import Any

from quant.features.contracts import FeatureName

from .contracts import (
    FeatureReference,
    FilterOperator,
    FilterSpec,
    ScanCandidateList,
    ScanCandidateRecord,
    ScanRunMetadata,
    SymbolDecision,
    SymbolDecisionAction,
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
from .universe import UniverseDefinition, UniverseExclusionInput, compose_universe_membership


class MissingFeaturePolicy(str, Enum):
    """Caller-selected handling for absent feature values."""

    FAIL = "fail"
    EXCLUDE = "exclude"


class StaleFeaturePolicy(str, Enum):
    """Caller-selected handling for stale feature values."""

    FAIL = "fail"
    EXCLUDE = "exclude"
    IGNORE = "ignore"


@dataclass(frozen=True)
class FeatureValueSnapshot:
    """Feature value plus caller-provided as-of metadata for freshness checks."""

    value: Any
    as_of_date: str | None = None


@dataclass(frozen=True)
class SymbolMarketState:
    """Caller-provided local market eligibility state for one symbol."""

    symbol: str
    market: str
    trade_date: str
    is_suspended: bool = False
    is_limit_up: bool = False
    is_limit_down: bool = False
    constraint_flags: tuple[str, ...] = ()


@dataclass(frozen=True)
class ScanConstraintPolicies:
    """Deterministic local policies for missing data and market eligibility."""

    missing_feature_policy: MissingFeaturePolicy = MissingFeaturePolicy.FAIL
    stale_feature_policy: StaleFeaturePolicy = StaleFeaturePolicy.FAIL
    max_feature_age_days: int | None = None
    exclude_suspended: bool = False
    exclude_limit_up: bool = False
    exclude_limit_down: bool = False
    blocked_constraint_flags: tuple[str, ...] = ()
    blocked_constraint_flags_by_market: Mapping[str, tuple[str, ...]] | None = None


@dataclass(frozen=True)
class ScanExecutionResult:
    """Candidate list plus deterministic symbol-level exclusion diagnostics."""

    candidate_list: ScanCandidateList
    symbol_decisions: tuple[SymbolDecision, ...]


class ScanRunnerError(ValueError):
    """Base error for offline scan runner failures."""


class InvalidScanRunnerInputError(ScanRunnerError):
    """Raised when caller-supplied runner inputs are malformed."""


class MissingSymbolFeatureValuesError(InvalidScanRunnerInputError):
    """Raised when a universe symbol has no feature-value payload."""


class MissingEligibilityStateError(InvalidScanRunnerInputError):
    """Raised when eligibility policies require symbol market state that is absent."""


class StaleFeatureValueError(ScanRunnerError):
    """Raised when feature freshness fails under fail-fast stale policy."""


class InvalidScanOutputError(ScanRunnerError):
    """Raised when the generated candidate list fails contract validation."""


def run_scan(
    *,
    metadata: ScanRunMetadata | Mapping[str, Any],
    universe: UniverseMembershipInput | Mapping[str, Any],
    filters: Iterable[FilterSpec | Mapping[str, Any]],
    symbol_feature_values: Mapping[str, Mapping[FeatureReference, Any]],
    universe_definition: UniverseDefinition | Mapping[str, Any] | None = None,
    exclusions: Iterable[UniverseExclusionInput | Mapping[str, Any]] = (),
    constraint_policies: ScanConstraintPolicies | Mapping[str, Any] | None = None,
    symbol_market_states: Mapping[str, SymbolMarketState | Mapping[str, Any]] | None = None,
) -> ScanCandidateList:
    """Build a validated candidate list from caller-supplied in-memory inputs."""
    return run_scan_with_diagnostics(
        metadata=metadata,
        universe=universe,
        filters=filters,
        symbol_feature_values=symbol_feature_values,
        universe_definition=universe_definition,
        exclusions=exclusions,
        constraint_policies=constraint_policies,
        symbol_market_states=symbol_market_states,
    ).candidate_list


def run_scan_with_diagnostics(
    *,
    metadata: ScanRunMetadata | Mapping[str, Any],
    universe: UniverseMembershipInput | Mapping[str, Any],
    filters: Iterable[FilterSpec | Mapping[str, Any]],
    symbol_feature_values: Mapping[str, Mapping[FeatureReference, Any]],
    universe_definition: UniverseDefinition | Mapping[str, Any] | None = None,
    exclusions: Iterable[UniverseExclusionInput | Mapping[str, Any]] = (),
    constraint_policies: ScanConstraintPolicies | Mapping[str, Any] | None = None,
    symbol_market_states: Mapping[str, SymbolMarketState | Mapping[str, Any]] | None = None,
) -> ScanExecutionResult:
    """Build a candidate list plus deterministic exclusion diagnostics."""
    normalized_metadata = _normalize_metadata(metadata)
    normalized_universe = _normalize_universe(universe)
    normalized_filters = _normalize_filters(filters)
    normalized_policies = _normalize_constraint_policies(constraint_policies)

    prepared_universe = compose_universe_membership(
        snapshot=normalized_universe,
        definition=universe_definition,
        exclusions=tuple(exclusions),
    )
    normalized_symbol_feature_values = _normalize_symbol_feature_values(
        symbol_feature_values,
        required_symbols=prepared_universe.effective_symbols,
        allowed_symbols=prepared_universe.snapshot.symbols,
    )
    normalized_market_states = _normalize_symbol_market_states(
        symbol_market_states,
        universe_market=prepared_universe.snapshot.market,
        trade_date=normalized_metadata.trade_date,
        required_symbols=prepared_universe.effective_symbols,
        allowed_symbols=prepared_universe.snapshot.symbols,
        policies=normalized_policies,
    )

    candidates: list[ScanCandidateRecord] = []
    symbol_decisions = list(prepared_universe.symbol_decisions)
    for symbol in prepared_universe.effective_symbols:
        market_state = normalized_market_states.get(symbol)
        eligibility_decision = _evaluate_market_eligibility(
            symbol=symbol,
            market=prepared_universe.snapshot.market,
            policies=normalized_policies,
            market_state=market_state,
        )
        if eligibility_decision is not None:
            symbol_decisions.append(eligibility_decision)
            continue

        feature_values = normalized_symbol_feature_values[symbol]
        raw_feature_values, feature_decision = _prepare_feature_values_for_symbol(
            symbol=symbol,
            market=prepared_universe.snapshot.market,
            trade_date=normalized_metadata.trade_date,
            filters=normalized_filters,
            feature_values=feature_values,
            policies=normalized_policies,
        )
        if feature_decision is not None:
            symbol_decisions.append(feature_decision)
            continue

        try:
            matched_filter_ids = collect_matched_filter_ids(
                normalized_filters,
                raw_feature_values,
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
                market=prepared_universe.snapshot.market,
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
    return ScanExecutionResult(
        candidate_list=candidate_list,
        symbol_decisions=tuple(symbol_decisions),
    )


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
    required_symbols: tuple[str, ...],
    allowed_symbols: tuple[str, ...],
) -> dict[str, dict[FeatureReference, FeatureValueSnapshot]]:
    if not isinstance(symbol_feature_values, Mapping):
        raise InvalidScanRunnerInputError(
            "symbol_feature_values must be a mapping keyed by symbol"
        )

    normalized: dict[str, dict[FeatureReference, FeatureValueSnapshot]] = {}
    for symbol, feature_values in symbol_feature_values.items():
        if not isinstance(symbol, str) or symbol.strip() == "":
            raise InvalidScanRunnerInputError(
                "symbol_feature_values keys must be non-empty strings"
            )
        if not isinstance(feature_values, Mapping):
            raise InvalidScanRunnerInputError(
                f"symbol_feature_values[{symbol!r}] must be a mapping keyed by FeatureReference"
            )

        symbol_values: dict[FeatureReference, FeatureValueSnapshot] = {}
        for feature_ref, value in feature_values.items():
            if not isinstance(feature_ref, FeatureReference):
                raise InvalidScanRunnerInputError(
                    f"symbol_feature_values[{symbol!r}] keys must be FeatureReference instances"
                )
            symbol_values[feature_ref] = _normalize_feature_value_snapshot(
                value,
                context=f"symbol_feature_values[{symbol!r}][{feature_ref.feature_name.value!r}]",
            )
        normalized[symbol] = symbol_values

    missing_symbols = sorted(
        symbol for symbol in required_symbols if symbol not in normalized
    )
    if missing_symbols:
        raise MissingSymbolFeatureValuesError(
            "missing symbol feature values for symbols: "
            f"{missing_symbols!r}"
        )

    unexpected_symbols = sorted(
        symbol for symbol in normalized if symbol not in set(allowed_symbols)
    )
    if unexpected_symbols:
        raise InvalidScanRunnerInputError(
            "symbol_feature_values contains symbols outside the declared universe: "
            f"{unexpected_symbols!r}"
        )

    return normalized


def _normalize_feature_value_snapshot(
    payload: Any,
    *,
    context: str,
) -> FeatureValueSnapshot:
    if is_dataclass(payload) and not isinstance(payload, type):
        payload = asdict(payload)

    if isinstance(payload, Mapping):
        if "value" not in payload:
            raise InvalidScanRunnerInputError(
                f"{context} must contain a 'value' field when using mapping payloads"
            )
        as_of_date = payload.get("as_of_date")
        if as_of_date is not None and not _is_iso_date_string(as_of_date):
            raise InvalidScanRunnerInputError(
                f"{context}.as_of_date must be an ISO date string when supplied"
            )
        return FeatureValueSnapshot(
            value=payload["value"],
            as_of_date=str(as_of_date) if as_of_date is not None else None,
        )

    return FeatureValueSnapshot(value=payload, as_of_date=None)


def _normalize_constraint_policies(
    policies: ScanConstraintPolicies | Mapping[str, Any] | None,
) -> ScanConstraintPolicies:
    if policies is None:
        return ScanConstraintPolicies()

    if is_dataclass(policies) and not isinstance(policies, type):
        payload = asdict(policies)
    elif isinstance(policies, Mapping):
        payload = dict(policies)
    else:
        raise InvalidScanRunnerInputError(
            "constraint_policies must be a dataclass instance or mapping"
        )

    missing_feature_policy = _coerce_missing_feature_policy(
        payload.get("missing_feature_policy", MissingFeaturePolicy.FAIL)
    )
    if missing_feature_policy is None:
        raise InvalidScanRunnerInputError(
            "constraint_policies.missing_feature_policy must be a supported policy"
        )
    stale_feature_policy = _coerce_stale_feature_policy(
        payload.get("stale_feature_policy", StaleFeaturePolicy.FAIL)
    )
    if stale_feature_policy is None:
        raise InvalidScanRunnerInputError(
            "constraint_policies.stale_feature_policy must be a supported policy"
        )

    max_feature_age_days = payload.get("max_feature_age_days")
    if max_feature_age_days is not None:
        if not isinstance(max_feature_age_days, int) or isinstance(max_feature_age_days, bool):
            raise InvalidScanRunnerInputError(
                "constraint_policies.max_feature_age_days must be a non-negative integer or None"
            )
        if max_feature_age_days < 0:
            raise InvalidScanRunnerInputError(
                "constraint_policies.max_feature_age_days must be a non-negative integer or None"
            )

    blocked_constraint_flags = _normalize_flag_sequence(
        payload.get("blocked_constraint_flags", ()),
        context="constraint_policies.blocked_constraint_flags",
    )
    blocked_constraint_flags_by_market = _normalize_flags_by_market(
        payload.get("blocked_constraint_flags_by_market"),
    )

    return ScanConstraintPolicies(
        missing_feature_policy=missing_feature_policy,
        stale_feature_policy=stale_feature_policy,
        max_feature_age_days=max_feature_age_days,
        exclude_suspended=bool(payload.get("exclude_suspended", False)),
        exclude_limit_up=bool(payload.get("exclude_limit_up", False)),
        exclude_limit_down=bool(payload.get("exclude_limit_down", False)),
        blocked_constraint_flags=blocked_constraint_flags,
        blocked_constraint_flags_by_market=blocked_constraint_flags_by_market,
    )


def _normalize_symbol_market_states(
    symbol_market_states: Mapping[str, SymbolMarketState | Mapping[str, Any]] | None,
    *,
    universe_market: str,
    trade_date: str,
    required_symbols: tuple[str, ...],
    allowed_symbols: tuple[str, ...],
    policies: ScanConstraintPolicies,
) -> dict[str, SymbolMarketState]:
    if symbol_market_states is None:
        symbol_market_states = {}
    if not isinstance(symbol_market_states, Mapping):
        raise InvalidScanRunnerInputError(
            "symbol_market_states must be a mapping keyed by symbol"
        )

    normalized: dict[str, SymbolMarketState] = {}
    for symbol, payload in symbol_market_states.items():
        if not isinstance(symbol, str) or symbol.strip() == "":
            raise InvalidScanRunnerInputError(
                "symbol_market_states keys must be non-empty strings"
            )
        normalized[symbol] = _normalize_symbol_market_state(
            payload,
            symbol=symbol,
            universe_market=universe_market,
            trade_date=trade_date,
        )

    missing_symbols = sorted(
        symbol for symbol in required_symbols if symbol not in normalized
    )
    if _policies_require_market_state(policies) and missing_symbols:
        raise MissingEligibilityStateError(
            "missing symbol market states for symbols: "
            f"{missing_symbols!r}"
        )

    unexpected_symbols = sorted(
        symbol for symbol in normalized if symbol not in set(allowed_symbols)
    )
    if unexpected_symbols:
        raise InvalidScanRunnerInputError(
            "symbol_market_states contains symbols outside the declared universe: "
            f"{unexpected_symbols!r}"
        )

    return normalized


def _normalize_symbol_market_state(
    payload: SymbolMarketState | Mapping[str, Any],
    *,
    symbol: str,
    universe_market: str,
    trade_date: str,
) -> SymbolMarketState:
    if is_dataclass(payload) and not isinstance(payload, type):
        record = asdict(payload)
    elif isinstance(payload, Mapping):
        record = dict(payload)
    else:
        raise InvalidScanRunnerInputError(
            f"symbol_market_states[{symbol!r}] must be a dataclass instance or mapping"
        )

    for required_field in ("symbol", "market", "trade_date"):
        if required_field not in record or record[required_field] is None:
            raise InvalidScanRunnerInputError(
                f"symbol_market_states[{symbol!r}].{required_field} is required"
            )
    if str(record["symbol"]).strip() != symbol:
        raise InvalidScanRunnerInputError(
            f"symbol_market_states[{symbol!r}].symbol must match the mapping key"
        )
    if str(record["market"]).strip() != universe_market:
        raise InvalidScanRunnerInputError(
            f"symbol_market_states[{symbol!r}].market must match universe market {universe_market!r}"
        )
    if str(record["trade_date"]).strip() != trade_date:
        raise InvalidScanRunnerInputError(
            f"symbol_market_states[{symbol!r}].trade_date must match scan trade_date {trade_date!r}"
        )

    constraint_flags = _normalize_flag_sequence(
        record.get("constraint_flags", ()),
        context=f"symbol_market_states[{symbol!r}].constraint_flags",
    )
    return SymbolMarketState(
        symbol=symbol,
        market=universe_market,
        trade_date=trade_date,
        is_suspended=bool(record.get("is_suspended", False)),
        is_limit_up=bool(record.get("is_limit_up", False)),
        is_limit_down=bool(record.get("is_limit_down", False)),
        constraint_flags=constraint_flags,
    )


def _prepare_feature_values_for_symbol(
    *,
    symbol: str,
    market: str,
    trade_date: str,
    filters: tuple[FilterSpec, ...],
    feature_values: Mapping[FeatureReference, FeatureValueSnapshot],
    policies: ScanConstraintPolicies,
) -> tuple[dict[FeatureReference, Any], SymbolDecision | None]:
    raw_feature_values: dict[FeatureReference, Any] = {}
    required_refs = _collect_feature_refs(filters)
    for feature_ref in required_refs:
        snapshot = feature_values.get(feature_ref)
        if snapshot is None:
            if policies.missing_feature_policy is MissingFeaturePolicy.FAIL:
                raise MissingFeatureValueError(
                    "missing feature value for "
                    f"{feature_ref.feature_name.value}[lag_days={feature_ref.lag_days}]"
                )
            return raw_feature_values, SymbolDecision(
                symbol=symbol,
                market=market,
                action=SymbolDecisionAction.EXCLUDED,
                reason_code="missing_feature",
                detail=f"{feature_ref.feature_name.value}[lag_days={feature_ref.lag_days}]",
            )

        if _is_feature_snapshot_stale(snapshot, trade_date=trade_date, policies=policies):
            detail = (
                f"{feature_ref.feature_name.value}[lag_days={feature_ref.lag_days}]"
                f"@{snapshot.as_of_date}"
            )
            if policies.stale_feature_policy is StaleFeaturePolicy.FAIL:
                raise StaleFeatureValueError(
                    f"symbol {symbol!r}: stale feature value for {detail}"
                )
            if policies.stale_feature_policy is StaleFeaturePolicy.EXCLUDE:
                return raw_feature_values, SymbolDecision(
                    symbol=symbol,
                    market=market,
                    action=SymbolDecisionAction.EXCLUDED,
                    reason_code="stale_feature",
                    detail=detail,
                )

        raw_feature_values[feature_ref] = snapshot.value

    return raw_feature_values, None


def _evaluate_market_eligibility(
    *,
    symbol: str,
    market: str,
    policies: ScanConstraintPolicies,
    market_state: SymbolMarketState | None,
) -> SymbolDecision | None:
    if market_state is None:
        return None

    if policies.exclude_suspended and market_state.is_suspended:
        return SymbolDecision(
            symbol=symbol,
            market=market,
            action=SymbolDecisionAction.INELIGIBLE,
            reason_code="suspended",
            detail="caller_provided_market_state",
        )
    if policies.exclude_limit_up and market_state.is_limit_up:
        return SymbolDecision(
            symbol=symbol,
            market=market,
            action=SymbolDecisionAction.INELIGIBLE,
            reason_code="limit_up",
            detail="caller_provided_market_state",
        )
    if policies.exclude_limit_down and market_state.is_limit_down:
        return SymbolDecision(
            symbol=symbol,
            market=market,
            action=SymbolDecisionAction.INELIGIBLE,
            reason_code="limit_down",
            detail="caller_provided_market_state",
        )

    blocked_flags = set(policies.blocked_constraint_flags)
    blocked_flags.update(
        policies.blocked_constraint_flags_by_market.get(market, ())
        if policies.blocked_constraint_flags_by_market is not None
        else ()
    )
    matched_flags = sorted(blocked_flags.intersection(set(market_state.constraint_flags)))
    if matched_flags:
        return SymbolDecision(
            symbol=symbol,
            market=market,
            action=SymbolDecisionAction.INELIGIBLE,
            reason_code="market_constraint",
            detail=",".join(matched_flags),
        )

    return None


def _collect_feature_refs(filters: tuple[FilterSpec, ...]) -> tuple[FeatureReference, ...]:
    ordered: list[FeatureReference] = []
    seen: set[FeatureReference] = set()
    for filter_spec in filters:
        if filter_spec.feature_ref in seen:
            continue
        seen.add(filter_spec.feature_ref)
        ordered.append(filter_spec.feature_ref)
    return tuple(ordered)


def _is_feature_snapshot_stale(
    snapshot: FeatureValueSnapshot,
    *,
    trade_date: str,
    policies: ScanConstraintPolicies,
) -> bool:
    if snapshot.as_of_date is None or policies.stale_feature_policy is StaleFeaturePolicy.IGNORE:
        return False

    feature_date = date.fromisoformat(snapshot.as_of_date)
    trade_day = date.fromisoformat(trade_date)
    if feature_date > trade_day:
        raise InvalidScanRunnerInputError(
            "feature as_of_date must not be later than scan trade_date"
        )

    allowed_age = (
        policies.max_feature_age_days
        if policies.max_feature_age_days is not None
        else 0
    )
    return (trade_day - feature_date).days > allowed_age


def _policies_require_market_state(policies: ScanConstraintPolicies) -> bool:
    return any(
        (
            policies.exclude_suspended,
            policies.exclude_limit_up,
            policies.exclude_limit_down,
            bool(policies.blocked_constraint_flags),
            bool(policies.blocked_constraint_flags_by_market),
        )
    )


def _normalize_flag_sequence(value: Any, *, context: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, (list, tuple)):
        raise InvalidScanRunnerInputError(
            f"{context} must be a list or tuple of non-empty strings"
        )
    normalized: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or item.strip() == "":
            raise InvalidScanRunnerInputError(
                f"{context}[{index}] must be a non-empty string"
            )
        normalized.append(item.strip())
    return tuple(sorted(set(normalized)))


def _normalize_flags_by_market(
    value: Any,
) -> dict[str, tuple[str, ...]] | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise InvalidScanRunnerInputError(
            "constraint_policies.blocked_constraint_flags_by_market must be a mapping"
        )
    normalized: dict[str, tuple[str, ...]] = {}
    for market, flags in value.items():
        if not isinstance(market, str) or market.strip() == "":
            raise InvalidScanRunnerInputError(
                "constraint_policies.blocked_constraint_flags_by_market keys must be non-empty strings"
            )
        normalized[market.strip()] = _normalize_flag_sequence(
            flags,
            context=(
                "constraint_policies.blocked_constraint_flags_by_market"
                f"[{market!r}]"
            ),
        )
    return normalized


def _coerce_feature_name(value: Any) -> FeatureName:
    if isinstance(value, FeatureName):
        return value
    return FeatureName(str(value))


def _coerce_filter_operator(value: Any) -> FilterOperator:
    if isinstance(value, FilterOperator):
        return value
    return FilterOperator(str(value))


def _coerce_missing_feature_policy(value: Any) -> MissingFeaturePolicy | None:
    if isinstance(value, MissingFeaturePolicy):
        return value
    if isinstance(value, str):
        try:
            return MissingFeaturePolicy(value.strip().lower())
        except ValueError:
            return None
    return None


def _coerce_stale_feature_policy(value: Any) -> StaleFeaturePolicy | None:
    if isinstance(value, StaleFeaturePolicy):
        return value
    if isinstance(value, str):
        try:
            return StaleFeaturePolicy(value.strip().lower())
        except ValueError:
            return None
    return None


def _as_mapping(payload: Any) -> dict[str, Any]:
    if is_dataclass(payload):
        return asdict(payload)
    if isinstance(payload, Mapping):
        return dict(payload)
    raise InvalidScanRunnerInputError(
        "payload must be a dataclass instance or mapping"
    )


def _format_issue_summary(issues: Iterable[Any]) -> str:
    return "; ".join(f"{issue.field}: {issue.code}" for issue in issues)


def _is_iso_date_string(value: Any) -> bool:
    if not isinstance(value, str) or value.strip() == "":
        return False
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        return False
    return value == parsed.isoformat()


__all__ = [
    "FeatureValueSnapshot",
    "InvalidScanOutputError",
    "InvalidScanRunnerInputError",
    "MissingEligibilityStateError",
    "MissingFeaturePolicy",
    "MissingSymbolFeatureValuesError",
    "ScanConstraintPolicies",
    "ScanExecutionResult",
    "ScanRunnerError",
    "StaleFeaturePolicy",
    "StaleFeatureValueError",
    "SymbolMarketState",
    "run_scan",
    "run_scan_with_diagnostics",
]
