"""Offline-safe universe helpers for scanner inputs."""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from datetime import date
from typing import Any, Mapping

from .contracts import (
    ScannerContractIssue,
    SymbolDecision,
    SymbolDecisionAction,
    UniverseFamily,
    UniverseMembershipInput,
    UniversePreset,
    validate_universe_membership_input,
)


UNIVERSE_DEFINITION_FIELDS: tuple[str, ...] = (
    "universe_id",
    "universe_name",
    "market",
    "source",
    "description",
    "family",
    "preset",
)
UNIVERSE_EXCLUSION_FIELDS: tuple[str, ...] = (
    "exclusion_list_id",
    "market",
    "symbols",
    "reason",
)

_SUPPORTED_FAMILY_MARKETS: dict[UniverseFamily, tuple[str, ...]] = {
    UniverseFamily.A_SHARE: ("CN",),
    UniverseFamily.HONG_KONG_STOCK: ("HK",),
    UniverseFamily.ETF_FUND: ("CN", "HK", "FUND"),
    UniverseFamily.SECTOR: ("CN", "HK"),
    UniverseFamily.INDEX: ("CN", "HK", "INDEX"),
    UniverseFamily.CUSTOM_WATCHLIST: ("CN", "HK", "FUND", "INDEX", "MIXED"),
}
_SUPPORTED_PRESETS: dict[UniversePreset, UniverseFamily] = {
    UniversePreset.A_SHARE_ALL: UniverseFamily.A_SHARE,
    UniversePreset.HONG_KONG_STOCK_ALL: UniverseFamily.HONG_KONG_STOCK,
    UniversePreset.ETF_FUND_ALL: UniverseFamily.ETF_FUND,
    UniversePreset.SECTOR_MEMBERS: UniverseFamily.SECTOR,
    UniversePreset.INDEX_CONSTITUENTS: UniverseFamily.INDEX,
    UniversePreset.CUSTOM_WATCHLIST: UniverseFamily.CUSTOM_WATCHLIST,
}


@dataclass(frozen=True)
class UniverseDefinition:
    """Declarative universe identity without data-loading behavior."""

    universe_id: str
    universe_name: str
    market: str
    source: str
    description: str | None = None
    family: UniverseFamily | str | None = None
    preset: UniversePreset | str | None = None


@dataclass(frozen=True)
class UniverseExclusionInput:
    """First-class exclusion list for deterministic universe trimming."""

    exclusion_list_id: str
    market: str
    symbols: tuple[str, ...]
    reason: str | None = None


@dataclass(frozen=True)
class PreparedUniverseMembership:
    """Validated membership snapshot plus deterministic exclusion results."""

    definition: UniverseDefinition | None
    snapshot: UniverseMembershipInput
    effective_symbols: tuple[str, ...]
    symbol_decisions: tuple[SymbolDecision, ...]


def normalize_universe_symbols(symbols: Any) -> tuple[str, ...]:
    """Normalize caller-provided symbols into deterministic sorted order."""
    if not isinstance(symbols, (list, tuple)):
        raise ValueError("symbols must be a list or tuple of non-empty strings")

    normalized: list[str] = []
    for symbol in symbols:
        if not isinstance(symbol, str) or symbol.strip() == "":
            raise ValueError("symbols must contain only non-empty strings")
        normalized.append(symbol.strip().upper())

    if not normalized:
        raise ValueError("symbols must contain at least one symbol")
    if len(set(normalized)) != len(normalized):
        raise ValueError("symbols must be unique after normalization")

    return tuple(sorted(normalized))


def build_universe_membership_snapshot(
    *,
    definition: UniverseDefinition | Mapping[str, Any],
    as_of_date: str,
    symbols: Any,
) -> UniverseMembershipInput:
    """Build a normalized membership snapshot from caller-provided symbols."""
    definition_record = _record_mapping(definition)
    definition_issues = validate_universe_definition(definition_record)
    if definition_issues:
        raise ValueError(_format_issue_summary(definition_issues))

    snapshot = UniverseMembershipInput(
        universe_id=str(definition_record["universe_id"]).strip(),
        universe_name=str(definition_record["universe_name"]).strip(),
        market=str(definition_record["market"]).strip().upper(),
        as_of_date=as_of_date,
        symbols=normalize_universe_symbols(symbols),
    )
    snapshot_issues = validate_universe_membership_input(snapshot)
    if snapshot_issues:
        raise ValueError(_format_issue_summary(snapshot_issues))
    return snapshot


def compose_universe_membership(
    *,
    snapshot: UniverseMembershipInput | Mapping[str, Any],
    definition: UniverseDefinition | Mapping[str, Any] | None = None,
    exclusions: tuple[UniverseExclusionInput | Mapping[str, Any], ...] | list[
        UniverseExclusionInput | Mapping[str, Any]
    ] = (),
) -> PreparedUniverseMembership:
    """Return one deterministic effective universe after exclusions."""
    snapshot_payload = _normalize_universe_snapshot(snapshot)
    normalized_definition = _normalize_definition(definition)
    normalized_exclusions = _normalize_exclusions(exclusions, market=snapshot_payload.market)

    excluded_by_symbol: dict[str, UniverseExclusionInput] = {}
    for exclusion in normalized_exclusions:
        for symbol in exclusion.symbols:
            excluded_by_symbol.setdefault(symbol, exclusion)

    symbol_decisions: list[SymbolDecision] = []
    effective_symbols: list[str] = []
    for symbol in snapshot_payload.symbols:
        exclusion = excluded_by_symbol.get(symbol)
        if exclusion is None:
            effective_symbols.append(symbol)
            continue
        detail = exclusion.exclusion_list_id
        if exclusion.reason:
            detail = f"{detail}:{exclusion.reason}"
        symbol_decisions.append(
            SymbolDecision(
                symbol=symbol,
                market=snapshot_payload.market,
                action=SymbolDecisionAction.EXCLUDED,
                reason_code="universe_exclusion",
                detail=detail,
            )
        )

    normalized_dataclass_definition = None
    if normalized_definition is not None:
        normalized_dataclass_definition = UniverseDefinition(
            universe_id=normalized_definition["universe_id"],
            universe_name=normalized_definition["universe_name"],
            market=normalized_definition["market"],
            source=normalized_definition["source"],
            description=normalized_definition.get("description"),
            family=normalized_definition.get("family"),
            preset=normalized_definition.get("preset"),
        )

    return PreparedUniverseMembership(
        definition=normalized_dataclass_definition,
        snapshot=snapshot_payload,
        effective_symbols=tuple(effective_symbols),
        symbol_decisions=tuple(symbol_decisions),
    )


def validate_universe_definition(
    payload: UniverseDefinition | Mapping[str, Any],
) -> tuple[ScannerContractIssue, ...]:
    """Return deterministic validation issues for one universe definition."""
    record = _record_mapping(payload)
    issues: list[ScannerContractIssue] = []

    allowed_fields = set(UNIVERSE_DEFINITION_FIELDS)
    for field_name in record:
        if field_name not in allowed_fields:
            issues.append(
                ScannerContractIssue(
                    field=field_name,
                    code="unexpected_field",
                    message=f"{field_name} is not part of this universe definition",
                )
            )

    for field_name in ("universe_id", "universe_name", "market", "source"):
        if field_name not in record or record[field_name] is None:
            issues.append(
                ScannerContractIssue(
                    field=field_name,
                    code="missing_required",
                    message=f"{field_name} is required",
                )
            )
        elif not _is_nonempty_text(record[field_name]):
            issues.append(
                ScannerContractIssue(
                    field=field_name,
                    code="invalid_text",
                    message=f"{field_name} must be a non-empty string",
                )
            )

    description = record.get("description")
    if description is not None and not isinstance(description, str):
        issues.append(
            ScannerContractIssue(
                field="description",
                code="invalid_type",
                message="description must be a string when supplied",
            )
        )

    market = _normalize_market(record.get("market"))
    family = _coerce_universe_family(record.get("family"))
    preset = _coerce_universe_preset(record.get("preset"))

    if record.get("family") is not None and family is None:
        issues.append(
            ScannerContractIssue(
                field="family",
                code="unsupported_universe_family",
                message="family must be a supported UniverseFamily value",
            )
        )
    if record.get("preset") is not None and preset is None:
        issues.append(
            ScannerContractIssue(
                field="preset",
                code="unsupported_universe_preset",
                message="preset must be a supported UniversePreset value",
            )
        )

    if family is not None and market is not None:
        allowed_markets = _SUPPORTED_FAMILY_MARKETS[family]
        if market not in allowed_markets:
            issues.append(
                ScannerContractIssue(
                    field="market",
                    code="unsupported_family_market_combo",
                    message=(
                        "market must be one of "
                        f"{allowed_markets!r} for family={family.value!r}"
                    ),
                )
            )

    if preset is not None:
        preset_family = _SUPPORTED_PRESETS[preset]
        if family is not None and preset_family is not family:
            issues.append(
                ScannerContractIssue(
                    field="preset",
                    code="family_preset_mismatch",
                    message=(
                        "preset must align with family; "
                        f"expected family={preset_family.value!r}"
                    ),
                )
            )
        if market is not None:
            allowed_markets = _SUPPORTED_FAMILY_MARKETS[preset_family]
            if market not in allowed_markets:
                issues.append(
                    ScannerContractIssue(
                        field="market",
                        code="unsupported_preset_market_combo",
                        message=(
                            "market must be one of "
                            f"{allowed_markets!r} for preset={preset.value!r}"
                        ),
                    )
                )

    return tuple(issues)


def validate_supported_scan_universe_definition(
    payload: UniverseDefinition | Mapping[str, Any],
) -> tuple[ScannerContractIssue, ...]:
    """Return validation issues for the strict phase-4 supported universe path."""
    record = _record_mapping(payload)
    issues = list(validate_universe_definition(record))

    if record.get("family") is None and record.get("preset") is None:
        issues.append(
            ScannerContractIssue(
                field="family",
                code="missing_required",
                message="family or preset is required for supported scan universes",
            )
        )

    return tuple(issues)


def validate_universe_exclusion_input(
    payload: UniverseExclusionInput | Mapping[str, Any],
) -> tuple[ScannerContractIssue, ...]:
    """Return deterministic validation issues for one exclusion list input."""
    record = _record_mapping(payload)
    issues: list[ScannerContractIssue] = []

    allowed_fields = set(UNIVERSE_EXCLUSION_FIELDS)
    for field_name in record:
        if field_name not in allowed_fields:
            issues.append(
                ScannerContractIssue(
                    field=field_name,
                    code="unexpected_field",
                    message=f"{field_name} is not part of this exclusion input",
                )
            )

    for field_name in ("exclusion_list_id", "market"):
        if field_name not in record or record[field_name] is None:
            issues.append(
                ScannerContractIssue(
                    field=field_name,
                    code="missing_required",
                    message=f"{field_name} is required",
                )
            )
        elif not _is_nonempty_text(record[field_name]):
            issues.append(
                ScannerContractIssue(
                    field=field_name,
                    code="invalid_text",
                    message=f"{field_name} must be a non-empty string",
                )
            )

    if "symbols" not in record or record["symbols"] is None:
        issues.append(
            ScannerContractIssue(
                field="symbols",
                code="missing_required",
                message="symbols is required",
            )
        )
    else:
        try:
            normalize_universe_symbols(record["symbols"])
        except ValueError as error:
            issues.append(
                ScannerContractIssue(
                    field="symbols",
                    code="invalid_symbols",
                    message=str(error),
                )
            )

    reason = record.get("reason")
    if reason is not None and not isinstance(reason, str):
        issues.append(
            ScannerContractIssue(
                field="reason",
                code="invalid_type",
                message="reason must be a string when supplied",
            )
        )

    return tuple(issues)


def validate_universe_membership_snapshot(
    *,
    definition: UniverseDefinition | Mapping[str, Any],
    snapshot: UniverseMembershipInput | Mapping[str, Any],
) -> tuple[ScannerContractIssue, ...]:
    """Validate a membership snapshot against its universe definition."""
    definition_record = _record_mapping(definition)
    snapshot_record = _record_mapping(snapshot)
    issues: list[ScannerContractIssue] = []

    for issue in validate_universe_definition(definition_record):
        issues.append(_prefix_issue(issue, "definition"))
    for issue in validate_universe_membership_input(snapshot_record):
        issues.append(_prefix_issue(issue, "snapshot"))

    for field_name in ("universe_id", "universe_name"):
        if (
            _is_nonempty_text(definition_record.get(field_name))
            and _is_nonempty_text(snapshot_record.get(field_name))
            and str(definition_record[field_name]).strip()
            != str(snapshot_record[field_name]).strip()
        ):
            issues.append(
                ScannerContractIssue(
                    field=f"snapshot.{field_name}",
                    code="definition_mismatch",
                    message=f"snapshot.{field_name} must match definition.{field_name}",
                )
            )

    definition_market = _normalize_market(definition_record.get("market"))
    snapshot_market = _normalize_market(snapshot_record.get("market"))
    if definition_market is not None and snapshot_market is not None:
        if definition_market != snapshot_market:
            issues.append(
                ScannerContractIssue(
                    field="snapshot.market",
                    code="definition_mismatch",
                    message="snapshot.market must match definition.market",
                )
            )

    symbols = snapshot_record.get("symbols")
    if isinstance(symbols, (list, tuple)) and all(_is_nonempty_text(item) for item in symbols):
        normalized = tuple(str(item).strip().upper() for item in symbols)
        if len(set(normalized)) != len(normalized):
            issues.append(
                ScannerContractIssue(
                    field="snapshot.symbols",
                    code="duplicate_symbol",
                    message="snapshot symbols must be unique after normalization",
                )
            )
        if normalized and tuple(symbols) != tuple(sorted(normalized)):
            issues.append(
                ScannerContractIssue(
                    field="snapshot.symbols",
                    code="non_deterministic_order",
                    message="snapshot symbols must be normalized and sorted",
                )
            )

    return tuple(issues)


def _normalize_definition(
    definition: UniverseDefinition | Mapping[str, Any] | None,
) -> dict[str, Any] | None:
    if definition is None:
        return None

    try:
        issues = validate_supported_scan_universe_definition(definition)
    except TypeError as error:
        raise ValueError(
            "invalid universe definition: payload must be a dataclass instance or mapping"
        ) from error
    if issues:
        raise ValueError(f"invalid universe definition: {_format_issue_summary(issues)}")

    record = _record_mapping(definition)
    return {
        "universe_id": str(record["universe_id"]).strip(),
        "universe_name": str(record["universe_name"]).strip(),
        "market": _normalize_market(record["market"]),
        "source": str(record["source"]).strip(),
        "description": record.get("description"),
        "family": _coerce_universe_family(record.get("family")),
        "preset": _coerce_universe_preset(record.get("preset")),
    }


def _normalize_universe_snapshot(
    snapshot: UniverseMembershipInput | Mapping[str, Any],
) -> UniverseMembershipInput:
    try:
        issues = validate_universe_membership_input(snapshot)
    except TypeError as error:
        raise ValueError(
            "invalid universe snapshot: payload must be a dataclass instance or mapping"
        ) from error
    if issues:
        raise ValueError(f"invalid universe snapshot: {_format_issue_summary(issues)}")

    payload = _record_mapping(snapshot)
    return UniverseMembershipInput(
        universe_id=str(payload["universe_id"]).strip(),
        universe_name=str(payload["universe_name"]).strip(),
        market=_normalize_market(payload["market"]) or str(payload["market"]).strip(),
        as_of_date=str(payload["as_of_date"]),
        symbols=tuple(str(symbol) for symbol in payload["symbols"]),
    )


def _normalize_exclusions(
    exclusions: tuple[UniverseExclusionInput | Mapping[str, Any], ...] | list[
        UniverseExclusionInput | Mapping[str, Any]
    ],
    *,
    market: str,
) -> tuple[UniverseExclusionInput, ...]:
    if isinstance(exclusions, (str, bytes)):
        raise ValueError("exclusions must be an iterable of exclusion inputs")

    normalized: list[UniverseExclusionInput] = []
    for index, exclusion in enumerate(exclusions):
        try:
            issues = validate_universe_exclusion_input(exclusion)
        except TypeError as error:
            raise ValueError(
                "invalid universe exclusion input: payload must be a dataclass instance or mapping"
            ) from error
        if issues:
            raise ValueError(
                "invalid universe exclusion input "
                f"at exclusions[{index}]: {_format_issue_summary(issues)}"
            )

        payload = _record_mapping(exclusion)
        normalized_market = _normalize_market(payload["market"])
        if normalized_market != market:
            raise ValueError(
                "invalid universe exclusion input "
                f"at exclusions[{index}]: market must match snapshot market {market!r}"
            )
        normalized.append(
            UniverseExclusionInput(
                exclusion_list_id=str(payload["exclusion_list_id"]).strip(),
                market=normalized_market,
                symbols=normalize_universe_symbols(payload["symbols"]),
                reason=(
                    str(payload["reason"]).strip()
                    if isinstance(payload.get("reason"), str) and payload["reason"].strip()
                    else None
                ),
            )
        )
    return tuple(normalized)


def _record_mapping(record: Mapping[str, Any] | Any) -> dict[str, Any]:
    if is_dataclass(record) and not isinstance(record, type):
        return asdict(record)
    if isinstance(record, Mapping):
        return dict(record)
    raise TypeError("universe payload must be a dataclass instance or mapping")


def _is_nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def _format_issue_summary(issues: tuple[ScannerContractIssue, ...] | list[ScannerContractIssue]) -> str:
    return "; ".join(f"{issue.field}: {issue.code}" for issue in issues)


def _prefix_issue(issue: ScannerContractIssue, prefix: str) -> ScannerContractIssue:
    return ScannerContractIssue(
        field=f"{prefix}.{issue.field}",
        code=issue.code,
        message=issue.message,
    )


def _normalize_market(value: Any) -> str | None:
    if not _is_nonempty_text(value):
        return None
    return str(value).strip().upper()


def _coerce_universe_family(value: Any) -> UniverseFamily | None:
    if value is None:
        return None
    if isinstance(value, UniverseFamily):
        return value
    if isinstance(value, str):
        try:
            return UniverseFamily(value.strip().lower())
        except ValueError:
            return None
    return None


def _coerce_universe_preset(value: Any) -> UniversePreset | None:
    if value is None:
        return None
    if isinstance(value, UniversePreset):
        return value
    if isinstance(value, str):
        try:
            return UniversePreset(value.strip().lower())
        except ValueError:
            return None
    return None


def is_iso_date_string(value: Any) -> bool:
    """Return whether a value follows the project ISO date-string convention."""
    if not _is_nonempty_text(value):
        return False
    try:
        parsed = date.fromisoformat(str(value))
    except ValueError:
        return False
    return str(value) == parsed.isoformat()


__all__ = [
    "PreparedUniverseMembership",
    "UNIVERSE_DEFINITION_FIELDS",
    "UNIVERSE_EXCLUSION_FIELDS",
    "UniverseDefinition",
    "UniverseExclusionInput",
    "build_universe_membership_snapshot",
    "compose_universe_membership",
    "is_iso_date_string",
    "normalize_universe_symbols",
    "validate_supported_scan_universe_definition",
    "validate_universe_definition",
    "validate_universe_exclusion_input",
    "validate_universe_membership_snapshot",
]
