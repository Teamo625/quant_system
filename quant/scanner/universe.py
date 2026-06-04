"""Offline-safe universe helpers for scanner inputs."""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from datetime import date
from typing import Any, Mapping

from .contracts import (
    ScannerContractIssue,
    UniverseMembershipInput,
    validate_universe_membership_input,
)


UNIVERSE_DEFINITION_FIELDS: tuple[str, ...] = (
    "universe_id",
    "universe_name",
    "market",
    "source",
    "description",
)


@dataclass(frozen=True)
class UniverseDefinition:
    """Declarative universe identity without data-loading behavior."""

    universe_id: str
    universe_name: str
    market: str
    source: str
    description: str | None = None


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
        market=str(definition_record["market"]).strip(),
        as_of_date=as_of_date,
        symbols=normalize_universe_symbols(symbols),
    )
    snapshot_issues = validate_universe_membership_input(snapshot)
    if snapshot_issues:
        raise ValueError(_format_issue_summary(snapshot_issues))
    return snapshot


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

    for field_name in ("universe_id", "universe_name", "market"):
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


def _record_mapping(record: Mapping[str, Any] | Any) -> dict[str, Any]:
    if is_dataclass(record) and not isinstance(record, type):
        return asdict(record)
    if isinstance(record, Mapping):
        return dict(record)
    raise TypeError("universe payload must be a dataclass instance or mapping")


def _is_nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def _format_issue_summary(issues: tuple[ScannerContractIssue, ...]) -> str:
    return "; ".join(f"{issue.field}: {issue.code}" for issue in issues)


def _prefix_issue(issue: ScannerContractIssue, prefix: str) -> ScannerContractIssue:
    return ScannerContractIssue(
        field=f"{prefix}.{issue.field}",
        code=issue.code,
        message=issue.message,
    )


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
    "UNIVERSE_DEFINITION_FIELDS",
    "UniverseDefinition",
    "build_universe_membership_snapshot",
    "is_iso_date_string",
    "normalize_universe_symbols",
    "validate_universe_definition",
    "validate_universe_membership_snapshot",
]
