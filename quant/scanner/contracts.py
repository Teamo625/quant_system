"""Offline-safe scanner contracts for future screening workflows."""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from datetime import date, datetime
from enum import Enum
from math import isfinite
from typing import Any, Mapping, TypeAlias

from quant.features.contracts import FeatureName


SCANNER_CONTRACT_SCHEMA_VERSION = "1.1.0"
SCANNER_ARTIFACT_TYPE = "scanner_candidate_list"
SCANNER_ARTIFACT_PURPOSE = "research_candidate_handoff"
SCANNER_ARTIFACT_PRODUCER = "scanner"
SCANNER_RANKING_SCORE_FORMULA = "weighted_sum(direction_adjusted_feature_values)"
SCANNER_RANKING_TIE_BREAK_ORDER: tuple[str, ...] = (
    "score_desc",
    "criteria_directional_values",
    "symbol_asc",
    "market_asc",
)

FilterScalar: TypeAlias = str | int | float
FilterThreshold: TypeAlias = FilterScalar | tuple[int | float, int | float]

UNIVERSE_MEMBERSHIP_FIELDS: tuple[str, ...] = (
    "universe_id",
    "universe_name",
    "market",
    "as_of_date",
    "symbols",
)
FEATURE_REFERENCE_FIELDS: tuple[str, ...] = (
    "feature_name",
    "lag_days",
)
FILTER_SPEC_FIELDS: tuple[str, ...] = (
    "filter_id",
    "feature_ref",
    "operator",
    "threshold",
)
RANKING_CRITERION_FIELDS: tuple[str, ...] = (
    "feature_ref",
    "direction",
    "weight",
)
SCAN_RANKING_CONFIG_FIELDS: tuple[str, ...] = ("criteria",)
SCAN_CANDIDATE_FIELDS: tuple[str, ...] = (
    "run_id",
    "trade_date",
    "symbol",
    "market",
    "universe_id",
    "matched_filter_ids",
    "score",
    "rank",
)
SCAN_ARTIFACT_UNIVERSE_SNAPSHOT_FIELDS: tuple[str, ...] = (
    "universe_id",
    "universe_name",
    "market",
    "as_of_date",
    "symbols",
    "source",
    "family",
    "preset",
)
SCAN_ARTIFACT_RANKING_FIELDS: tuple[str, ...] = (
    "criteria",
    "score_formula",
    "tie_break_order",
)
SCAN_ARTIFACT_HANDOFF_FIELDS: tuple[str, ...] = (
    "artifact_type",
    "artifact_purpose",
    "producer_name",
    "intended_consumers",
)
SCAN_ARTIFACT_CONTEXT_FIELDS: tuple[str, ...] = (
    "universe_snapshot",
    "ranking",
    "handoff",
)
SCAN_RUN_METADATA_FIELDS: tuple[str, ...] = (
    "run_id",
    "scanner_id",
    "trade_date",
    "universe_id",
    "generated_at",
    "schema_version",
    "artifact_context",
)
SCAN_CANDIDATE_LIST_FIELDS: tuple[str, ...] = (
    "metadata",
    "feature_refs",
    "filters",
    "candidates",
)


class FilterOperator(str, Enum):
    """Supported declarative filter operators."""

    EQ = "eq"
    NEQ = "neq"
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    BETWEEN = "between"


class UniverseFamily(str, Enum):
    """Supported market-aware Scanner universe families."""

    A_SHARE = "a_share"
    HONG_KONG_STOCK = "hong_kong_stock"
    ETF_FUND = "etf_fund"
    SECTOR = "sector"
    INDEX = "index"
    CUSTOM_WATCHLIST = "custom_watchlist"


class UniversePreset(str, Enum):
    """Supported deterministic preset labels for universe definitions."""

    A_SHARE_ALL = "a_share_all"
    HONG_KONG_STOCK_ALL = "hong_kong_stock_all"
    ETF_FUND_ALL = "etf_fund_all"
    SECTOR_MEMBERS = "sector_members"
    INDEX_CONSTITUENTS = "index_constituents"
    CUSTOM_WATCHLIST = "custom_watchlist"


class RankingDirection(str, Enum):
    """Supported deterministic ordering directions for ranking criteria."""

    ASC = "asc"
    DESC = "desc"


class SymbolDecisionAction(str, Enum):
    """Deterministic symbol decision classes for offline scan workflows."""

    EXCLUDED = "excluded"
    INELIGIBLE = "ineligible"


@dataclass(frozen=True)
class ScannerContractIssue:
    """Structured validation issue for deterministic scanner tests."""

    field: str
    code: str
    message: str


@dataclass(frozen=True)
class SymbolDecision:
    """Trace record for excluded or ineligible scan symbols."""

    symbol: str
    market: str
    action: SymbolDecisionAction
    reason_code: str
    detail: str | None = None


@dataclass(frozen=True)
class UniverseMembershipInput:
    """Universe identity plus one deterministic membership snapshot."""

    universe_id: str
    universe_name: str
    market: str
    as_of_date: str
    symbols: tuple[str, ...]


@dataclass(frozen=True)
class FeatureReference:
    """Declarative pointer to an existing FeatureHub output identifier."""

    feature_name: FeatureName
    lag_days: int = 0


@dataclass(frozen=True)
class FilterSpec:
    """Declarative screening condition without execution behavior."""

    filter_id: str
    feature_ref: FeatureReference
    operator: FilterOperator
    threshold: FilterThreshold


@dataclass(frozen=True)
class RankingCriterion:
    """One explicit research-priority ordering criterion."""

    feature_ref: FeatureReference
    direction: RankingDirection
    weight: float = 1.0


@dataclass(frozen=True)
class ScanRankingConfig:
    """Explicit score/rank configuration for deterministic candidate ordering."""

    criteria: tuple[RankingCriterion, ...]


@dataclass(frozen=True)
class ScanCandidateRecord:
    """One scanner output row with optional deterministic rank/score semantics."""

    run_id: str
    trade_date: str
    symbol: str
    market: str
    universe_id: str
    matched_filter_ids: tuple[str, ...]
    score: float | None = None
    rank: int | None = None


@dataclass(frozen=True)
class ScanArtifactUniverseSnapshot:
    """Universe snapshot provenance required for persisted scanner artifacts."""

    universe_id: str
    universe_name: str
    market: str
    as_of_date: str
    symbols: tuple[str, ...]
    source: str | None = None
    family: UniverseFamily | str | None = None
    preset: UniversePreset | str | None = None


@dataclass(frozen=True)
class ScanArtifactRankingMetadata:
    """Deterministic ranking provenance for persisted ranked artifacts."""

    criteria: tuple[RankingCriterion, ...]
    score_formula: str = SCANNER_RANKING_SCORE_FORMULA
    tie_break_order: tuple[str, ...] = SCANNER_RANKING_TIE_BREAK_ORDER


@dataclass(frozen=True)
class ScanArtifactHandoffMetadata:
    """Consumer-facing scanner artifact identity for downstream handoff."""

    artifact_type: str = SCANNER_ARTIFACT_TYPE
    artifact_purpose: str = SCANNER_ARTIFACT_PURPOSE
    producer_name: str = SCANNER_ARTIFACT_PRODUCER
    intended_consumers: tuple[str, ...] = ("strategy_lab", "signal_engine")


@dataclass(frozen=True)
class ScanArtifactContext:
    """Optional artifact-only metadata for persisted scanner candidate lists."""

    universe_snapshot: ScanArtifactUniverseSnapshot
    ranking: ScanArtifactRankingMetadata | None = None
    handoff: ScanArtifactHandoffMetadata = ScanArtifactHandoffMetadata()


@dataclass(frozen=True)
class ScanRunMetadata:
    """Stable metadata describing one scanner run artifact."""

    run_id: str
    scanner_id: str
    trade_date: str
    universe_id: str
    generated_at: datetime
    schema_version: str = SCANNER_CONTRACT_SCHEMA_VERSION
    artifact_context: ScanArtifactContext | None = None


@dataclass(frozen=True)
class ScanCandidateList:
    """Validated scanner artifact container for downstream consumption."""

    metadata: ScanRunMetadata
    feature_refs: tuple[FeatureReference, ...]
    filters: tuple[FilterSpec, ...]
    candidates: tuple[ScanCandidateRecord, ...]


def validate_universe_membership_input(
    payload: UniverseMembershipInput | Mapping[str, Any],
) -> tuple[ScannerContractIssue, ...]:
    """Return deterministic validation issues for one universe input."""
    record = _record_mapping(payload)
    issues: list[ScannerContractIssue] = []

    issues.extend(
        _validate_required_nonempty_texts(
            record,
            (
                "universe_id",
                "universe_name",
                "market",
            ),
        )
    )
    issues.extend(_validate_expected_fields(record, UNIVERSE_MEMBERSHIP_FIELDS))

    if "as_of_date" not in record or record["as_of_date"] is None:
        issues.append(_missing_required("as_of_date"))
    elif not _is_iso_date_text(record["as_of_date"]):
        issues.append(
            ScannerContractIssue(
                field="as_of_date",
                code="invalid_date_string",
                message="as_of_date must be an ISO date string",
            )
        )

    if "symbols" not in record or record["symbols"] is None:
        issues.append(_missing_required("symbols"))
    else:
        issues.extend(_validate_symbol_sequence(record["symbols"], field_name="symbols"))

    return tuple(issues)


def validate_feature_reference(
    payload: FeatureReference | Mapping[str, Any],
) -> tuple[ScannerContractIssue, ...]:
    """Return deterministic validation issues for one feature reference."""
    record = _record_mapping(payload)
    issues: list[ScannerContractIssue] = []

    issues.extend(_validate_expected_fields(record, FEATURE_REFERENCE_FIELDS))

    if "feature_name" not in record or record["feature_name"] is None:
        issues.append(_missing_required("feature_name"))
    elif _coerce_feature_name(record["feature_name"]) is None:
        issues.append(
            ScannerContractIssue(
                field="feature_name",
                code="unsupported_feature_name",
                message="feature_name must be a supported FeatureName value",
            )
        )

    if "lag_days" not in record or record["lag_days"] is None:
        issues.append(_missing_required("lag_days"))
    else:
        lag_days = record["lag_days"]
        if not isinstance(lag_days, int) or isinstance(lag_days, bool):
            issues.append(
                ScannerContractIssue(
                    field="lag_days",
                    code="invalid_type",
                    message="lag_days must be a non-negative integer",
                )
            )
        elif lag_days < 0:
            issues.append(
                ScannerContractIssue(
                    field="lag_days",
                    code="invalid_value",
                    message="lag_days must be a non-negative integer",
                )
            )

    return tuple(issues)


def validate_filter_spec(
    payload: FilterSpec | Mapping[str, Any],
) -> tuple[ScannerContractIssue, ...]:
    """Return deterministic validation issues for one declarative filter."""
    record = _record_mapping(payload)
    issues: list[ScannerContractIssue] = []

    issues.extend(_validate_expected_fields(record, FILTER_SPEC_FIELDS))
    issues.extend(_validate_required_nonempty_texts(record, ("filter_id",)))

    if "feature_ref" not in record or record["feature_ref"] is None:
        issues.append(_missing_required("feature_ref"))
    else:
        for issue in validate_feature_reference(record["feature_ref"]):
            issues.append(_prefix_issue(issue, prefix="feature_ref"))

    operator = _coerce_filter_operator(record.get("operator"))
    if "operator" not in record or record["operator"] is None:
        issues.append(_missing_required("operator"))
    elif operator is None:
        issues.append(
            ScannerContractIssue(
                field="operator",
                code="unsupported_operator",
                message="operator must be a supported FilterOperator value",
            )
        )

    if "threshold" not in record or record["threshold"] is None:
        issues.append(_missing_required("threshold"))
    elif operator is not None:
        threshold_issue = _validate_threshold_for_operator(
            operator=operator,
            threshold=record["threshold"],
        )
        if threshold_issue is not None:
            issues.append(threshold_issue)

    return tuple(issues)


def validate_ranking_criterion(
    payload: RankingCriterion | Mapping[str, Any],
) -> tuple[ScannerContractIssue, ...]:
    """Return deterministic validation issues for one ranking criterion."""
    record = _record_mapping(payload)
    issues: list[ScannerContractIssue] = []

    issues.extend(_validate_expected_fields(record, RANKING_CRITERION_FIELDS))

    if "feature_ref" not in record or record["feature_ref"] is None:
        issues.append(_missing_required("feature_ref"))
    else:
        for issue in validate_feature_reference(record["feature_ref"]):
            issues.append(_prefix_issue(issue, prefix="feature_ref"))

    direction = _coerce_ranking_direction(record.get("direction"))
    if "direction" not in record or record["direction"] is None:
        issues.append(_missing_required("direction"))
    elif direction is None:
        issues.append(
            ScannerContractIssue(
                field="direction",
                code="unsupported_direction",
                message="direction must be a supported RankingDirection value",
            )
        )

    weight = record.get("weight", 1.0)
    if isinstance(weight, bool) or not isinstance(weight, (int, float)) or not isfinite(weight):
        issues.append(
            ScannerContractIssue(
                field="weight",
                code="invalid_weight",
                message="weight must be a finite positive number",
            )
        )
    elif float(weight) <= 0.0:
        issues.append(
            ScannerContractIssue(
                field="weight",
                code="invalid_weight",
                message="weight must be a finite positive number",
            )
        )

    return tuple(issues)


def validate_scan_ranking_config(
    payload: ScanRankingConfig | Mapping[str, Any],
) -> tuple[ScannerContractIssue, ...]:
    """Return deterministic validation issues for one ranking config."""
    record = _record_mapping(payload)
    issues: list[ScannerContractIssue] = []

    issues.extend(_validate_expected_fields(record, SCAN_RANKING_CONFIG_FIELDS))

    criteria = record.get("criteria")
    if criteria is None:
        issues.append(_missing_required("criteria"))
        return tuple(issues)
    if not isinstance(criteria, (list, tuple)):
        issues.append(
            ScannerContractIssue(
                field="criteria",
                code="invalid_type",
                message="criteria must be a list or tuple",
            )
        )
        return tuple(issues)
    if not criteria:
        issues.append(
            ScannerContractIssue(
                field="criteria",
                code="empty_criteria",
                message="criteria must contain at least one ranking criterion",
            )
        )
        return tuple(issues)

    criterion_payloads = _sequence_mappings(
        criteria,
        field_name="criteria",
        issues=issues,
    )
    for index, criterion in enumerate(criterion_payloads):
        for issue in validate_ranking_criterion(criterion):
            issues.append(_prefix_issue(issue, prefix=f"criteria[{index}]"))
    issues.extend(
        _validate_unique_keys(
            (_extract_ranking_feature_key(item) for item in criterion_payloads),
            field_name="criteria",
            code="duplicate_ranking_feature",
            message=(
                "criteria must not contain duplicate "
                "(feature_name, lag_days) ranking references"
            ),
            skip_none=True,
        )
    )

    return tuple(issues)


def validate_scan_candidate_record(
    payload: ScanCandidateRecord | Mapping[str, Any],
) -> tuple[ScannerContractIssue, ...]:
    """Return deterministic validation issues for one candidate record."""
    record = _record_mapping(payload)
    issues: list[ScannerContractIssue] = []

    issues.extend(_validate_expected_fields(record, SCAN_CANDIDATE_FIELDS))
    issues.extend(
        _validate_required_nonempty_texts(
            record,
            (
                "run_id",
                "symbol",
                "market",
                "universe_id",
            ),
        )
    )

    if "trade_date" not in record or record["trade_date"] is None:
        issues.append(_missing_required("trade_date"))
    elif not _is_iso_date_text(record["trade_date"]):
        issues.append(
            ScannerContractIssue(
                field="trade_date",
                code="invalid_date_string",
                message="trade_date must be an ISO date string",
            )
        )

    if "matched_filter_ids" not in record or record["matched_filter_ids"] is None:
        issues.append(_missing_required("matched_filter_ids"))
    else:
        issues.extend(
            _validate_text_sequence(
                record["matched_filter_ids"],
                field_name="matched_filter_ids",
            )
        )

    rank = record.get("rank")
    score = record.get("score")
    if rank is None and score is None:
        return tuple(issues)
    if rank is None or score is None:
        issues.append(
            ScannerContractIssue(
                field="rank" if rank is None else "score",
                code="ranking_field_pair_required",
                message="rank and score must either both be supplied or both be omitted",
            )
        )
        return tuple(issues)
    if not isinstance(rank, int) or isinstance(rank, bool):
        issues.append(
            ScannerContractIssue(
                field="rank",
                code="invalid_type",
                message="rank must be a positive integer when supplied",
            )
        )
    elif rank <= 0:
        issues.append(
            ScannerContractIssue(
                field="rank",
                code="invalid_value",
                message="rank must be a positive integer when supplied",
            )
        )
    if isinstance(score, bool) or not isinstance(score, (int, float)) or not isfinite(score):
        issues.append(
            ScannerContractIssue(
                field="score",
                code="invalid_type",
                message="score must be a finite numeric value when supplied",
            )
        )

    return tuple(issues)


def validate_scan_artifact_universe_snapshot(
    payload: ScanArtifactUniverseSnapshot | Mapping[str, Any],
) -> tuple[ScannerContractIssue, ...]:
    """Return deterministic validation issues for artifact universe provenance."""
    record = _record_mapping(payload)
    issues: list[ScannerContractIssue] = []

    issues.extend(
        _validate_expected_fields(record, SCAN_ARTIFACT_UNIVERSE_SNAPSHOT_FIELDS)
    )
    issues.extend(
        _validate_required_nonempty_texts(
            record,
            ("universe_id", "universe_name", "market"),
        )
    )

    if "as_of_date" not in record or record["as_of_date"] is None:
        issues.append(_missing_required("as_of_date"))
    elif not _is_iso_date_text(record["as_of_date"]):
        issues.append(
            ScannerContractIssue(
                field="as_of_date",
                code="invalid_date_string",
                message="as_of_date must be an ISO date string",
            )
        )

    if "symbols" not in record or record["symbols"] is None:
        issues.append(_missing_required("symbols"))
    else:
        issues.extend(_validate_symbol_sequence(record["symbols"], field_name="symbols"))

    source = record.get("source")
    if source is not None and not _is_nonempty_text(source):
        issues.append(
            ScannerContractIssue(
                field="source",
                code="invalid_text",
                message="source must be a non-empty string when supplied",
            )
        )

    family = record.get("family")
    if family is not None and _coerce_universe_family(family) is None:
        issues.append(
            ScannerContractIssue(
                field="family",
                code="unsupported_universe_family",
                message="family must be a supported UniverseFamily value",
            )
        )

    preset = record.get("preset")
    if preset is not None and _coerce_universe_preset(preset) is None:
        issues.append(
            ScannerContractIssue(
                field="preset",
                code="unsupported_universe_preset",
                message="preset must be a supported UniversePreset value",
            )
        )

    return tuple(issues)


def validate_scan_artifact_ranking_metadata(
    payload: ScanArtifactRankingMetadata | Mapping[str, Any],
) -> tuple[ScannerContractIssue, ...]:
    """Return deterministic validation issues for ranking provenance metadata."""
    record = _record_mapping(payload)
    issues: list[ScannerContractIssue] = []

    issues.extend(_validate_expected_fields(record, SCAN_ARTIFACT_RANKING_FIELDS))
    issues.extend(validate_scan_ranking_config({"criteria": record.get("criteria")}))

    score_formula = record.get("score_formula")
    if score_formula is None:
        issues.append(_missing_required("score_formula"))
    elif not _is_nonempty_text(score_formula):
        issues.append(
            ScannerContractIssue(
                field="score_formula",
                code="invalid_text",
                message="score_formula must be a non-empty string",
            )
        )

    tie_break_order = record.get("tie_break_order")
    if tie_break_order is None:
        issues.append(_missing_required("tie_break_order"))
    else:
        issues.extend(
            _validate_text_sequence(
                tie_break_order,
                field_name="tie_break_order",
            )
        )
        issues.extend(
            _validate_unique_keys(
                tie_break_order if isinstance(tie_break_order, (list, tuple)) else (),
                field_name="tie_break_order",
                code="duplicate_tie_break_order",
                message="tie_break_order must not contain duplicate entries",
            )
        )

    return tuple(issues)


def validate_scan_artifact_handoff_metadata(
    payload: ScanArtifactHandoffMetadata | Mapping[str, Any],
) -> tuple[ScannerContractIssue, ...]:
    """Return deterministic validation issues for downstream handoff metadata."""
    record = _record_mapping(payload)
    issues: list[ScannerContractIssue] = []

    issues.extend(_validate_expected_fields(record, SCAN_ARTIFACT_HANDOFF_FIELDS))
    issues.extend(
        _validate_required_nonempty_texts(
            record,
            ("artifact_type", "artifact_purpose", "producer_name"),
        )
    )

    if "intended_consumers" not in record or record["intended_consumers"] is None:
        issues.append(_missing_required("intended_consumers"))
    else:
        issues.extend(
            _validate_text_sequence(
                record["intended_consumers"],
                field_name="intended_consumers",
            )
        )
        issues.extend(
            _validate_unique_keys(
                record["intended_consumers"]
                if isinstance(record["intended_consumers"], (list, tuple))
                else (),
                field_name="intended_consumers",
                code="duplicate_intended_consumer",
                message="intended_consumers must not contain duplicate values",
            )
        )

    return tuple(issues)


def validate_scan_artifact_context(
    payload: ScanArtifactContext | Mapping[str, Any],
) -> tuple[ScannerContractIssue, ...]:
    """Return deterministic validation issues for persisted artifact metadata."""
    record = _record_mapping(payload)
    issues: list[ScannerContractIssue] = []

    issues.extend(_validate_expected_fields(record, SCAN_ARTIFACT_CONTEXT_FIELDS))

    universe_snapshot = record.get("universe_snapshot")
    if universe_snapshot is None:
        issues.append(_missing_required("universe_snapshot"))
    else:
        for issue in validate_scan_artifact_universe_snapshot(universe_snapshot):
            issues.append(_prefix_issue(issue, prefix="universe_snapshot"))

    ranking = record.get("ranking")
    if ranking is not None:
        for issue in validate_scan_artifact_ranking_metadata(ranking):
            issues.append(_prefix_issue(issue, prefix="ranking"))

    handoff = record.get("handoff")
    if handoff is None:
        issues.append(_missing_required("handoff"))
    else:
        for issue in validate_scan_artifact_handoff_metadata(handoff):
            issues.append(_prefix_issue(issue, prefix="handoff"))

    return tuple(issues)


def validate_scan_run_metadata(
    payload: ScanRunMetadata | Mapping[str, Any],
) -> tuple[ScannerContractIssue, ...]:
    """Return deterministic validation issues for one scanner run header."""
    record = _record_mapping(payload)
    issues: list[ScannerContractIssue] = []

    issues.extend(_validate_expected_fields(record, SCAN_RUN_METADATA_FIELDS))
    issues.extend(
        _validate_required_nonempty_texts(
            record,
            (
                "run_id",
                "scanner_id",
                "universe_id",
            ),
        )
    )

    if "trade_date" not in record or record["trade_date"] is None:
        issues.append(_missing_required("trade_date"))
    elif not _is_iso_date_text(record["trade_date"]):
        issues.append(
            ScannerContractIssue(
                field="trade_date",
                code="invalid_date_string",
                message="trade_date must be an ISO date string",
            )
        )

    if "generated_at" not in record or record["generated_at"] is None:
        issues.append(_missing_required("generated_at"))
    elif not isinstance(record["generated_at"], datetime):
        issues.append(
            ScannerContractIssue(
                field="generated_at",
                code="invalid_type",
                message="generated_at must be a datetime instance",
            )
        )

    if "schema_version" not in record or record["schema_version"] is None:
        issues.append(_missing_required("schema_version"))
    else:
        schema_version = record["schema_version"]
        if not _is_nonempty_text(schema_version):
            issues.append(
                ScannerContractIssue(
                    field="schema_version",
                    code="invalid_text",
                    message="schema_version must be a non-empty string",
                )
            )
        elif schema_version != SCANNER_CONTRACT_SCHEMA_VERSION:
            issues.append(
                ScannerContractIssue(
                    field="schema_version",
                    code="unsupported_schema_version",
                    message=(
                        "schema_version must match "
                        f"{SCANNER_CONTRACT_SCHEMA_VERSION}"
                    ),
                )
            )

    artifact_context = record.get("artifact_context")
    if artifact_context is not None:
        for issue in validate_scan_artifact_context(artifact_context):
            issues.append(_prefix_issue(issue, prefix="artifact_context"))

    return tuple(issues)


def validate_scan_candidate_list(
    payload: ScanCandidateList | Mapping[str, Any],
) -> tuple[ScannerContractIssue, ...]:
    """Return deterministic validation issues for one candidate-list artifact."""
    record = _record_mapping(payload)
    issues: list[ScannerContractIssue] = []

    issues.extend(_validate_expected_fields(record, SCAN_CANDIDATE_LIST_FIELDS))

    metadata = record.get("metadata")
    if metadata is None:
        issues.append(_missing_required("metadata"))
        metadata_payload: dict[str, Any] | None = None
    else:
        metadata_payload = _record_mapping(metadata)
        for issue in validate_scan_run_metadata(metadata_payload):
            issues.append(_prefix_issue(issue, prefix="metadata"))

    feature_refs = record.get("feature_refs")
    if feature_refs is None:
        issues.append(_missing_required("feature_refs"))
        feature_ref_payloads: tuple[dict[str, Any], ...] = ()
    else:
        feature_ref_payloads = _sequence_mappings(
            feature_refs,
            field_name="feature_refs",
            issues=issues,
        )
        for index, item in enumerate(feature_ref_payloads):
            for issue in validate_feature_reference(item):
                issues.append(_prefix_issue(issue, prefix=f"feature_refs[{index}]"))
        issues.extend(
            _validate_unique_keys(
                (
                    (_coerce_feature_name(item.get("feature_name")), item.get("lag_days"))
                    for item in feature_ref_payloads
                ),
                field_name="feature_refs",
                code="duplicate_feature_reference",
                message=(
                    "feature_refs must not contain duplicate "
                    "(feature_name, lag_days) pairs"
                ),
                skip_none=True,
            )
        )

    filters = record.get("filters")
    if filters is None:
        issues.append(_missing_required("filters"))
        filter_payloads: tuple[dict[str, Any], ...] = ()
    else:
        filter_payloads = _sequence_mappings(
            filters,
            field_name="filters",
            issues=issues,
        )
        for index, item in enumerate(filter_payloads):
            for issue in validate_filter_spec(item):
                issues.append(_prefix_issue(issue, prefix=f"filters[{index}]"))
        issues.extend(
            _validate_unique_keys(
                (item.get("filter_id") for item in filter_payloads),
                field_name="filters",
                code="duplicate_filter_id",
                message="filters must not contain duplicate filter_id values",
                skip_none=True,
            )
        )

    candidates = record.get("candidates")
    if candidates is None:
        issues.append(_missing_required("candidates"))
        candidate_payloads: tuple[dict[str, Any], ...] = ()
    else:
        candidate_payloads = _sequence_mappings(
            candidates,
            field_name="candidates",
            issues=issues,
        )
        for index, item in enumerate(candidate_payloads):
            for issue in validate_scan_candidate_record(item):
                issues.append(_prefix_issue(issue, prefix=f"candidates[{index}]"))

    if metadata_payload is not None:
        metadata_run_id = metadata_payload.get("run_id")
        metadata_trade_date = metadata_payload.get("trade_date")
        metadata_universe_id = metadata_payload.get("universe_id")
        artifact_context_payload = metadata_payload.get("artifact_context")
        artifact_ranking_payload = None
        artifact_universe_snapshot_payload = None
        if isinstance(artifact_context_payload, Mapping):
            artifact_ranking_payload = artifact_context_payload.get("ranking")
            artifact_universe_snapshot_payload = artifact_context_payload.get(
                "universe_snapshot"
            )
        filter_ids = {
            item["filter_id"]
            for item in filter_payloads
            if _is_nonempty_text(item.get("filter_id"))
        }
        candidate_keys: list[tuple[str, str]] = []
        candidate_ranks: list[int] = []
        ranked_candidate_present = False
        unranked_candidate_present = False
        partial_ranking_candidate_present = False

        for index, item in enumerate(candidate_payloads):
            if item.get("run_id") != metadata_run_id:
                issues.append(
                    ScannerContractIssue(
                        field=f"candidates[{index}].run_id",
                        code="metadata_mismatch",
                        message="candidate run_id must match metadata.run_id",
                    )
                )
            if item.get("trade_date") != metadata_trade_date:
                issues.append(
                    ScannerContractIssue(
                        field=f"candidates[{index}].trade_date",
                        code="metadata_mismatch",
                        message="candidate trade_date must match metadata.trade_date",
                    )
                )
            if item.get("universe_id") != metadata_universe_id:
                issues.append(
                    ScannerContractIssue(
                        field=f"candidates[{index}].universe_id",
                        code="metadata_mismatch",
                        message="candidate universe_id must match metadata.universe_id",
                    )
                )

            symbol = item.get("symbol")
            market = item.get("market")
            if _is_nonempty_text(symbol) and _is_nonempty_text(market):
                candidate_keys.append((str(symbol), str(market)))
            rank = item.get("rank")
            score = item.get("score")
            if rank is None and score is None:
                unranked_candidate_present = True
            elif (
                isinstance(rank, int)
                and not isinstance(rank, bool)
                and rank > 0
                and isinstance(score, (int, float))
                and not isinstance(score, bool)
                and isfinite(score)
            ):
                ranked_candidate_present = True
                candidate_ranks.append(rank)
            elif rank is not None or score is not None:
                partial_ranking_candidate_present = True

            matched_filter_ids = item.get("matched_filter_ids")
            if isinstance(matched_filter_ids, (list, tuple)):
                unknown_ids = [
                    value
                    for value in matched_filter_ids
                    if _is_nonempty_text(value) and value not in filter_ids
                ]
                if unknown_ids:
                    issues.append(
                        ScannerContractIssue(
                            field=f"candidates[{index}].matched_filter_ids",
                            code="unknown_filter_id",
                            message=(
                                "matched_filter_ids must reference declared filters: "
                                f"{sorted(set(unknown_ids))!r}"
                            ),
                        )
                    )

        if isinstance(artifact_universe_snapshot_payload, Mapping):
            artifact_universe_id = artifact_universe_snapshot_payload.get("universe_id")
            if artifact_universe_id != metadata_universe_id:
                issues.append(
                    ScannerContractIssue(
                        field="metadata.artifact_context.universe_snapshot.universe_id",
                        code="metadata_mismatch",
                        message=(
                            "artifact universe_snapshot.universe_id must match "
                            "metadata.universe_id"
                        ),
                    )
                )

        issues.extend(
            _validate_unique_keys(
                candidate_keys,
                field_name="candidates",
                code="duplicate_candidate_symbol",
                message="candidates must not contain duplicate (symbol, market) pairs",
            )
        )
        if partial_ranking_candidate_present or (
            ranked_candidate_present and unranked_candidate_present
        ):
            issues.append(
                ScannerContractIssue(
                    field="candidates",
                    code="mixed_ranking_fields",
                    message="candidates must be either all ranked or all unranked",
                )
            )
        if ranked_candidate_present and artifact_context_payload is not None:
            if artifact_ranking_payload is None:
                issues.append(
                    ScannerContractIssue(
                        field="metadata.artifact_context.ranking",
                        code="missing_required_for_ranked_candidates",
                        message=(
                            "artifact_context.ranking is required when candidates "
                            "contain rank and score fields"
                        ),
                    )
                )
        if (
            unranked_candidate_present
            and artifact_context_payload is not None
            and artifact_ranking_payload is not None
        ):
            issues.append(
                ScannerContractIssue(
                    field="metadata.artifact_context.ranking",
                    code="unexpected_for_unranked_candidates",
                    message=(
                        "artifact_context.ranking must be omitted when candidates "
                        "are unranked"
                    ),
                )
            )
        elif ranked_candidate_present:
            issues.extend(
                _validate_unique_keys(
                    candidate_ranks,
                    field_name="candidates",
                    code="duplicate_candidate_rank",
                    message="ranked candidates must not contain duplicate rank values",
                )
            )
            if candidate_ranks and tuple(sorted(candidate_ranks)) != tuple(
                range(1, len(candidate_ranks) + 1)
            ):
                issues.append(
                    ScannerContractIssue(
                        field="candidates",
                        code="non_contiguous_rank",
                        message="ranked candidates must use contiguous ranks starting at 1",
                    )
                )
            ranked_keys = [
                (
                    int(item["rank"]),
                    str(item["symbol"]),
                    str(item["market"]),
                )
                for item in candidate_payloads
                if (
                    isinstance(item.get("rank"), int)
                    and not isinstance(item.get("rank"), bool)
                    and _is_nonempty_text(item.get("symbol"))
                    and _is_nonempty_text(item.get("market"))
                )
            ]
            if ranked_keys and ranked_keys != sorted(ranked_keys):
                issues.append(
                    ScannerContractIssue(
                        field="candidates",
                        code="non_deterministic_order",
                        message="ranked candidates must be sorted by (rank, symbol, market)",
                    )
                )
        elif candidate_keys and candidate_keys != sorted(candidate_keys):
            issues.append(
                ScannerContractIssue(
                    field="candidates",
                    code="non_deterministic_order",
                    message="candidates must be sorted by (symbol, market)",
                )
            )

    return tuple(issues)


def _record_mapping(record: Mapping[str, Any] | Any) -> dict[str, Any]:
    if is_dataclass(record) and not isinstance(record, type):
        return asdict(record)
    if isinstance(record, Mapping):
        return dict(record)
    raise TypeError("scanner contract payload must be a dataclass instance or mapping")


def _is_nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def _is_iso_date_text(value: Any) -> bool:
    if not _is_nonempty_text(value):
        return False
    try:
        parsed = date.fromisoformat(str(value))
    except ValueError:
        return False
    return str(value) == parsed.isoformat()


def _coerce_feature_name(value: Any) -> FeatureName | None:
    if isinstance(value, FeatureName):
        return value
    if isinstance(value, str):
        try:
            return FeatureName(value)
        except ValueError:
            return None
    return None


def _coerce_filter_operator(value: Any) -> FilterOperator | None:
    if isinstance(value, FilterOperator):
        return value
    if isinstance(value, str):
        try:
            return FilterOperator(value)
        except ValueError:
            return None
    return None


def _coerce_ranking_direction(value: Any) -> RankingDirection | None:
    if isinstance(value, RankingDirection):
        return value
    if isinstance(value, str):
        try:
            return RankingDirection(value)
        except ValueError:
            return None
    return None


def _coerce_universe_family(value: Any) -> UniverseFamily | None:
    if isinstance(value, UniverseFamily):
        return value
    if isinstance(value, str):
        try:
            return UniverseFamily(value)
        except ValueError:
            return None
    return None


def _coerce_universe_preset(value: Any) -> UniversePreset | None:
    if isinstance(value, UniversePreset):
        return value
    if isinstance(value, str):
        try:
            return UniversePreset(value)
        except ValueError:
            return None
    return None


def _extract_ranking_feature_key(
    payload: Mapping[str, Any],
) -> tuple[FeatureName | None, Any]:
    feature_ref = payload.get("feature_ref")
    if is_dataclass(feature_ref) and not isinstance(feature_ref, type):
        feature_ref = asdict(feature_ref)
    if not isinstance(feature_ref, Mapping):
        return (None, None)
    feature_ref_payload = dict(feature_ref)
    return (
        _coerce_feature_name(feature_ref_payload.get("feature_name")),
        feature_ref_payload.get("lag_days"),
    )


def _is_supported_filter_scalar(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, str):
        return value.strip() != ""
    if isinstance(value, int):
        return True
    if isinstance(value, float):
        return isfinite(value)
    return False


def _is_supported_numeric_threshold(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return True
    if isinstance(value, float):
        return isfinite(value)
    return False


def _validate_threshold_for_operator(
    *,
    operator: FilterOperator,
    threshold: Any,
) -> ScannerContractIssue | None:
    if operator in {FilterOperator.EQ, FilterOperator.NEQ}:
        if _is_supported_filter_scalar(threshold):
            return None
        return ScannerContractIssue(
            field="threshold",
            code="invalid_threshold",
            message="threshold must be a non-empty string or finite number",
        )

    if operator in {
        FilterOperator.GT,
        FilterOperator.GTE,
        FilterOperator.LT,
        FilterOperator.LTE,
    }:
        if _is_supported_numeric_threshold(threshold):
            return None
        return ScannerContractIssue(
            field="threshold",
            code="invalid_threshold",
            message="threshold must be a finite numeric value for comparison operators",
        )

    if operator is FilterOperator.BETWEEN:
        if not isinstance(threshold, (list, tuple)) or len(threshold) != 2:
            return ScannerContractIssue(
                field="threshold",
                code="invalid_threshold",
                message="threshold must be a two-item numeric range for between",
            )
        lower, upper = threshold
        if not (
            _is_supported_numeric_threshold(lower)
            and _is_supported_numeric_threshold(upper)
        ):
            return ScannerContractIssue(
                field="threshold",
                code="invalid_threshold",
                message="threshold must be a two-item numeric range for between",
            )
        if float(lower) > float(upper):
            return ScannerContractIssue(
                field="threshold",
                code="invalid_threshold",
                message="between threshold lower bound must not exceed upper bound",
            )
        return None

    return ScannerContractIssue(
        field="threshold",
        code="invalid_threshold",
        message="threshold is invalid for the supplied operator",
    )


def _validate_required_nonempty_texts(
    payload: Mapping[str, Any],
    fields: tuple[str, ...],
) -> list[ScannerContractIssue]:
    issues: list[ScannerContractIssue] = []
    for field_name in fields:
        if field_name not in payload or payload[field_name] is None:
            issues.append(_missing_required(field_name))
            continue
        if not _is_nonempty_text(payload[field_name]):
            issues.append(
                ScannerContractIssue(
                    field=field_name,
                    code="invalid_text",
                    message=f"{field_name} must be a non-empty string",
                )
            )
    return issues


def _validate_expected_fields(
    payload: Mapping[str, Any],
    allowed_fields: tuple[str, ...],
) -> list[ScannerContractIssue]:
    issues: list[ScannerContractIssue] = []
    allowed = set(allowed_fields)
    for field_name in payload:
        if field_name in allowed:
            continue
        issues.append(
            ScannerContractIssue(
                field=field_name,
                code="unexpected_field",
                message=f"{field_name} is not part of this declarative scanner contract",
            )
        )
    return issues


def _validate_symbol_sequence(
    value: Any,
    *,
    field_name: str,
) -> list[ScannerContractIssue]:
    issues = _validate_text_sequence(value, field_name=field_name)
    if issues:
        return issues

    sequence = tuple(value)
    if len(set(sequence)) != len(sequence):
        issues.append(
            ScannerContractIssue(
                field=field_name,
                code="duplicate_symbol",
                message=f"{field_name} must not contain duplicate symbols",
            )
        )
    return issues


def _validate_text_sequence(
    value: Any,
    *,
    field_name: str,
) -> list[ScannerContractIssue]:
    if not isinstance(value, (list, tuple)):
        return [
            ScannerContractIssue(
                field=field_name,
                code="invalid_type",
                message=f"{field_name} must be a list or tuple of non-empty strings",
            )
        ]

    issues: list[ScannerContractIssue] = []
    for index, item in enumerate(value):
        if _is_nonempty_text(item):
            continue
        issues.append(
            ScannerContractIssue(
                field=f"{field_name}[{index}]",
                code="invalid_text",
                message=f"{field_name} values must be non-empty strings",
            )
        )
    return issues


def _sequence_mappings(
    value: Any,
    *,
    field_name: str,
    issues: list[ScannerContractIssue],
) -> tuple[dict[str, Any], ...]:
    if not isinstance(value, (list, tuple)):
        issues.append(
            ScannerContractIssue(
                field=field_name,
                code="invalid_type",
                message=f"{field_name} must be a list or tuple",
            )
        )
        return ()

    items: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        try:
            items.append(_record_mapping(item))
        except TypeError:
            issues.append(
                ScannerContractIssue(
                    field=f"{field_name}[{index}]",
                    code="invalid_type",
                    message=f"{field_name} items must be dataclass instances or mappings",
                )
            )
    return tuple(items)


def _validate_unique_keys(
    keys: Any,
    *,
    field_name: str,
    code: str,
    message: str,
    skip_none: bool = False,
) -> list[ScannerContractIssue]:
    issues: list[ScannerContractIssue] = []
    seen: set[Any] = set()
    for key in keys:
        if skip_none and (
            key is None
            or (isinstance(key, tuple) and any(part is None for part in key))
        ):
            continue
        if key in seen:
            issues.append(
                ScannerContractIssue(
                    field=field_name,
                    code=code,
                    message=message,
                )
            )
            break
        seen.add(key)
    return issues


def _prefix_issue(
    issue: ScannerContractIssue,
    *,
    prefix: str,
) -> ScannerContractIssue:
    return ScannerContractIssue(
        field=f"{prefix}.{issue.field}",
        code=issue.code,
        message=issue.message,
    )


def _missing_required(field_name: str) -> ScannerContractIssue:
    return ScannerContractIssue(
        field=field_name,
        code="missing_required",
        message=f"{field_name} is required",
    )


__all__ = [
    "FEATURE_REFERENCE_FIELDS",
    "FILTER_SPEC_FIELDS",
    "RANKING_CRITERION_FIELDS",
    "SCAN_ARTIFACT_CONTEXT_FIELDS",
    "SCAN_ARTIFACT_HANDOFF_FIELDS",
    "SCAN_ARTIFACT_RANKING_FIELDS",
    "SCAN_ARTIFACT_UNIVERSE_SNAPSHOT_FIELDS",
    "SCAN_RANKING_CONFIG_FIELDS",
    "SCAN_CANDIDATE_FIELDS",
    "SCAN_CANDIDATE_LIST_FIELDS",
    "SCAN_RUN_METADATA_FIELDS",
    "SCANNER_ARTIFACT_PRODUCER",
    "SCANNER_ARTIFACT_PURPOSE",
    "SCANNER_ARTIFACT_TYPE",
    "SCANNER_CONTRACT_SCHEMA_VERSION",
    "SCANNER_RANKING_SCORE_FORMULA",
    "SCANNER_RANKING_TIE_BREAK_ORDER",
    "UNIVERSE_MEMBERSHIP_FIELDS",
    "FeatureReference",
    "FilterOperator",
    "FilterSpec",
    "RankingCriterion",
    "RankingDirection",
    "ScanArtifactContext",
    "ScanArtifactHandoffMetadata",
    "ScanArtifactRankingMetadata",
    "ScanArtifactUniverseSnapshot",
    "ScanRankingConfig",
    "ScanCandidateList",
    "ScanCandidateRecord",
    "ScanRunMetadata",
    "ScannerContractIssue",
    "UniverseFamily",
    "UniverseMembershipInput",
    "UniversePreset",
    "validate_scan_artifact_context",
    "validate_scan_artifact_handoff_metadata",
    "validate_scan_artifact_ranking_metadata",
    "validate_scan_artifact_universe_snapshot",
    "validate_feature_reference",
    "validate_filter_spec",
    "validate_ranking_criterion",
    "validate_scan_candidate_list",
    "validate_scan_candidate_record",
    "validate_scan_ranking_config",
    "validate_scan_run_metadata",
    "validate_universe_membership_input",
]
