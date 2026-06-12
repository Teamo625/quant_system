"""Deterministic Scanner personal-readiness gate for Phase 4-P audits."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import Enum


class ReadinessStatus(str, Enum):
    PASS = "pass"
    WARN = "warn"
    BLOCKED = "blocked"
    FAIL = "fail"


class FollowUpDisposition(str, Enum):
    SCANNER_HARDENING = "scanner_hardening"
    CONTRACT_REPAIR = "contract_repair"
    OWNER_BLOCKER = "owner_blocker"
    BLOCKED_UPSTREAM = "blocked_upstream"


@dataclass(frozen=True)
class ReadinessStatusCount:
    status: ReadinessStatus
    count: int


@dataclass(frozen=True)
class ScannerCapabilityGroupReadiness:
    group_id: str
    label: str
    status: ReadinessStatus
    reason: str
    required_capabilities: tuple[str, ...]
    implemented_capabilities: tuple[str, ...]
    missing_capabilities: tuple[str, ...]
    evidence: tuple[str, ...]


@dataclass(frozen=True)
class ScannerFollowUpItem:
    follow_up_id: str
    capability_group_id: str
    status: ReadinessStatus
    disposition: FollowUpDisposition
    reason: str
    recommended_next_handoff_theme: str


@dataclass(frozen=True)
class ScannerFollowUpBatch:
    batch_id: str
    theme: str
    disposition: FollowUpDisposition
    item_ids: tuple[str, ...]
    rationale: str


@dataclass(frozen=True)
class ScannerPersonalReadinessGate:
    phase_id: str
    phase_closure_ready: bool
    capability_groups: tuple[ScannerCapabilityGroupReadiness, ...]
    status_counts: tuple[ReadinessStatusCount, ...]
    follow_up_queue: tuple[ScannerFollowUpItem, ...]
    follow_up_batches: tuple[ScannerFollowUpBatch, ...]
    recommended_next_handoff_batch_id: str
    recommended_next_handoff_theme: str


@dataclass(frozen=True)
class _CapabilityGroupBlueprint:
    group_id: str
    label: str
    required_capabilities: tuple[str, ...]
    implemented_capabilities: tuple[str, ...]
    reason: str
    evidence: tuple[str, ...]
    blocked: bool = False
    failed: bool = False


@dataclass(frozen=True)
class _FollowUpBlueprint:
    follow_up_id: str
    capability_group_id: str
    disposition: FollowUpDisposition
    reason: str
    recommended_next_handoff_theme: str
    blocked: bool = False


@dataclass(frozen=True)
class _BatchBlueprint:
    batch_id: str
    theme: str
    disposition: FollowUpDisposition
    item_ids: tuple[str, ...]
    rationale: str


def build_scanner_personal_readiness_gate() -> ScannerPersonalReadinessGate:
    """Return the deterministic Phase 4-P readiness audit snapshot."""
    capability_groups = tuple(
        _build_capability_group(blueprint) for blueprint in _CAPABILITY_GROUP_BLUEPRINTS
    )
    status_counts = summarize_readiness_status_counts(capability_groups)
    follow_up_queue = tuple(
        _build_follow_up_item(blueprint, capability_groups)
        for blueprint in _FOLLOW_UP_BLUEPRINTS
    )
    follow_up_batches = tuple(_build_follow_up_batch(blueprint) for blueprint in _BATCHES)
    _validate_follow_up_batches(follow_up_queue, follow_up_batches)

    return ScannerPersonalReadinessGate(
        phase_id="Phase 4-P Scanner Personal Trading Perfection Re-Review",
        phase_closure_ready=all(
            group.status is ReadinessStatus.PASS for group in capability_groups
        ),
        capability_groups=capability_groups,
        status_counts=status_counts,
        follow_up_queue=follow_up_queue,
        follow_up_batches=follow_up_batches,
        recommended_next_handoff_batch_id="scanner_artifact_contract_repair_batch_01",
        recommended_next_handoff_theme=(
            "Candidate artifact schema and downstream handoff provenance"
        ),
    )


def summarize_readiness_status_counts(
    capability_groups: tuple[ScannerCapabilityGroupReadiness, ...],
) -> tuple[ReadinessStatusCount, ...]:
    """Return deterministic counts for every readiness status."""
    counts = Counter(group.status for group in capability_groups)
    return tuple(
        ReadinessStatusCount(status=status, count=counts.get(status, 0))
        for status in (
            ReadinessStatus.PASS,
            ReadinessStatus.WARN,
            ReadinessStatus.BLOCKED,
            ReadinessStatus.FAIL,
        )
    )


def _build_capability_group(
    blueprint: _CapabilityGroupBlueprint,
) -> ScannerCapabilityGroupReadiness:
    implemented = tuple(sorted(set(blueprint.implemented_capabilities)))
    missing = tuple(
        capability
        for capability in blueprint.required_capabilities
        if capability not in implemented
    )
    if blueprint.failed:
        status = ReadinessStatus.FAIL
    elif blueprint.blocked:
        status = ReadinessStatus.BLOCKED
    elif missing:
        status = ReadinessStatus.WARN
    else:
        status = ReadinessStatus.PASS

    return ScannerCapabilityGroupReadiness(
        group_id=blueprint.group_id,
        label=blueprint.label,
        status=status,
        reason=blueprint.reason,
        required_capabilities=blueprint.required_capabilities,
        implemented_capabilities=implemented,
        missing_capabilities=missing,
        evidence=blueprint.evidence,
    )


def _build_follow_up_item(
    blueprint: _FollowUpBlueprint,
    capability_groups: tuple[ScannerCapabilityGroupReadiness, ...],
) -> ScannerFollowUpItem:
    group_by_id = {group.group_id: group for group in capability_groups}
    group = group_by_id[blueprint.capability_group_id]
    if blueprint.blocked:
        status = ReadinessStatus.BLOCKED
    elif group.status is ReadinessStatus.FAIL:
        status = ReadinessStatus.FAIL
    else:
        status = ReadinessStatus.WARN

    return ScannerFollowUpItem(
        follow_up_id=blueprint.follow_up_id,
        capability_group_id=blueprint.capability_group_id,
        status=status,
        disposition=blueprint.disposition,
        reason=blueprint.reason,
        recommended_next_handoff_theme=blueprint.recommended_next_handoff_theme,
    )


def _build_follow_up_batch(blueprint: _BatchBlueprint) -> ScannerFollowUpBatch:
    return ScannerFollowUpBatch(
        batch_id=blueprint.batch_id,
        theme=blueprint.theme,
        disposition=blueprint.disposition,
        item_ids=blueprint.item_ids,
        rationale=blueprint.rationale,
    )


def _validate_follow_up_batches(
    follow_up_queue: tuple[ScannerFollowUpItem, ...],
    follow_up_batches: tuple[ScannerFollowUpBatch, ...],
) -> None:
    queue_ids = {item.follow_up_id for item in follow_up_queue}
    batch_item_ids: set[str] = set()

    for batch in follow_up_batches:
        if (
            len(batch.item_ids) == 1
            and batch.disposition is FollowUpDisposition.SCANNER_HARDENING
        ):
            raise ValueError(
                "ordinary scanner hardening batches must group at least two follow-up items"
            )
        for follow_up_id in batch.item_ids:
            if follow_up_id not in queue_ids:
                raise ValueError(f"unknown follow-up id referenced by batch: {follow_up_id}")
            if follow_up_id in batch_item_ids:
                raise ValueError(f"duplicate follow-up id across batches: {follow_up_id}")
            batch_item_ids.add(follow_up_id)

    if queue_ids != batch_item_ids:
        missing = tuple(sorted(queue_ids - batch_item_ids))
        raise ValueError(f"follow-up queue items missing from batches: {missing!r}")


_CAPABILITY_GROUP_BLUEPRINTS: tuple[_CapabilityGroupBlueprint, ...] = (
    _CapabilityGroupBlueprint(
        group_id="universe_definition_and_validation",
        label="Universe Definition and Validation",
        required_capabilities=(
            "a_share_universe_validation",
            "hong_kong_universe_validation",
            "etf_fund_universe_validation",
            "sector_universe_validation",
            "index_universe_validation",
            "custom_watchlist_validation",
            "exclusion_list_support",
        ),
        implemented_capabilities=(
            "a_share_universe_validation",
            "hong_kong_universe_validation",
            "etf_fund_universe_validation",
            "sector_universe_validation",
            "index_universe_validation",
            "custom_watchlist_validation",
            "exclusion_list_support",
            "deterministic_symbol_normalization",
            "membership_snapshot_validation",
            "market_aware_definition_validation",
        ),
        reason=(
            "Scanner now supports explicit universe-family and preset validation for the "
            "supported current-phase scan domains, plus first-class exclusion-list "
            "composition over caller-provided membership snapshots."
        ),
        evidence=(
            "quant/scanner/universe.py now validates supported Scanner universe families/presets, rejects inconsistent family-market combinations, and composes first-class exclusion lists without mutating the original snapshot.",
            "PreparedUniverseMembership keeps deterministic effective symbol order plus symbol-level exclusion decisions suitable for later artifact work.",
            "tests/scanner/test_universe.py covers strict family/preset validation, exclusion-list composition, and mismatch handling without network access.",
        ),
    ),
    _CapabilityGroupBlueprint(
        group_id="deterministic_batch_filter_evaluation",
        label="Deterministic Batch Filter Evaluation",
        required_capabilities=(
            "multi_symbol_batch_filter_evaluation",
            "deterministic_feature_reference_matching",
            "stable_all_filters_selection",
            "invalid_filter_rejection",
            "missing_feature_error_surface",
        ),
        implemented_capabilities=(
            "multi_symbol_batch_filter_evaluation",
            "deterministic_feature_reference_matching",
            "stable_all_filters_selection",
            "invalid_filter_rejection",
            "missing_feature_error_surface",
        ),
        reason=(
            "Scanner foundation work already supports deterministic in-memory "
            "filter evaluation over caller-supplied multi-symbol batches and "
            "surfaces invalid filter or missing feature inputs without hidden IO."
        ),
        evidence=(
            "TASK-067 accepted quant/scanner/matching.py for declarative filter evaluation and deterministic matched filter ordering.",
            "TASK-068 accepted quant/scanner/runner.py for multi-symbol in-memory scan execution with stable candidate ordering.",
            "tests/scanner/test_matching.py and tests/scanner/test_runner.py cover duplicate filter ids, invalid operators, missing feature values, and deterministic candidate output order.",
        ),
    ),
    _CapabilityGroupBlueprint(
        group_id="ranking_scoring_and_candidate_ordering",
        label="Ranking, Scoring, and Candidate Ordering",
        required_capabilities=(
            "explicit_ranking_configuration",
            "deterministic_candidate_ordering_policy",
            "score_output_fields",
            "tie_breaking_rules",
            "research_priority_sorting",
        ),
        implemented_capabilities=(
            "explicit_ranking_configuration",
            "deterministic_candidate_ordering_policy",
            "score_output_fields",
            "tie_breaking_rules",
            "research_priority_sorting",
            "symbol_market_sort_fallback",
        ),
        reason=(
            "Scanner now supports explicit ranking criteria with direction-aware weighted "
            "scores, deterministic candidate ranks, and stable tie-breaking that falls "
            "back to `(symbol, market)` only after score and criterion comparisons."
        ),
        evidence=(
            "quant/scanner/runner.py now accepts explicit ScanRankingConfig input, computes deterministic direction-aware weighted scores over caller-provided feature values, and emits ranked candidate rows with stable tie-break ordering.",
            "quant/scanner/contracts.py now validates optional candidate rank/score fields plus explicit ranking criterion/config contracts while preserving unranked fallback behavior.",
            "tests/scanner/test_runner.py covers descending and ascending ranking behavior, score output, stable tie-breaking, and invalid ranking config/data paths offline.",
        ),
    ),
    _CapabilityGroupBlueprint(
        group_id="candidate_persistence_and_handoff_readiness",
        label="Candidate Persistence and Handoff Readiness",
        required_capabilities=(
            "candidate_jsonl_persistence",
            "manifest_metadata",
            "reproducibility_checksum",
            "feature_and_filter_traceability",
            "universe_snapshot_provenance",
            "downstream_handoff_metadata",
            "overwrite_safety",
        ),
        implemented_capabilities=(
            "candidate_jsonl_persistence",
            "manifest_metadata",
            "reproducibility_checksum",
            "feature_and_filter_traceability",
            "overwrite_safety",
            "rank_score_row_persistence",
        ),
        reason=(
            "Scanner can already persist validated candidate rows with deterministic "
            "manifests and checksum protection, and ranked rows now serialize score/rank "
            "fields. The artifact contract still lacks explicit universe snapshot "
            "provenance and richer downstream handoff metadata needed for repeated "
            "personal research workflows."
        ),
        evidence=(
            "TASK-066 accepted quant/scanner/storage.py for deterministic JSONL plus manifest writes with overwrite preflight and content checksums.",
            "quant/scanner/storage.py now preserves optional rank/score row fields while manifests still carry only run metadata, feature refs, filters, candidate count, and checksum.",
            "quant/scanner/contracts.py metadata does not retain universe snapshot as_of_date/source details or downstream consumer-facing handoff fields.",
        ),
    ),
    _CapabilityGroupBlueprint(
        group_id="market_constraints_and_missing_data_handling",
        label="Market Constraints and Missing-Data Handling",
        required_capabilities=(
            "missing_feature_policy",
            "stale_feature_policy",
            "suspension_handling",
            "limit_up_down_handling",
            "market_specific_constraints",
            "exclusion_rule_application",
        ),
        implemented_capabilities=(
            "missing_feature_policy",
            "stale_feature_policy",
            "suspension_handling",
            "limit_up_down_handling",
            "market_specific_constraints",
            "exclusion_rule_application",
            "hard_failure_on_missing_symbol_feature_map",
            "hard_failure_on_missing_feature_value",
        ),
        reason=(
            "Scanner runner now supports caller-selected missing/stale feature policies, "
            "first-class suspension and limit-up/down handling, market-specific blocked "
            "constraint flags, and deterministic symbol-level reason codes."
        ),
        evidence=(
            "quant/scanner/runner.py adds ScanConstraintPolicies, SymbolMarketState, and ScanExecutionResult while preserving run_scan backward compatibility.",
            "Missing feature and stale feature handling can now fail or exclude deterministically, and eligibility constraints are traceable through SymbolDecision records.",
            "tests/scanner/test_runner.py covers missing/stale policies, universe exclusions, suspension handling, and market-specific constraint flags offline.",
        ),
    ),
    _CapabilityGroupBlueprint(
        group_id="offline_scan_workflow_regression_coverage",
        label="Offline Scan Workflow Regression Coverage",
        required_capabilities=(
            "realistic_multi_symbol_scans",
            "invalid_filter_regressions",
            "missing_value_regressions",
            "deterministic_order_regressions",
            "artifact_safety_regressions",
            "ranking_workflow_regressions",
            "market_constraint_regressions",
        ),
        implemented_capabilities=(
            "realistic_multi_symbol_scans",
            "invalid_filter_regressions",
            "missing_value_regressions",
            "deterministic_order_regressions",
            "artifact_safety_regressions",
            "ranking_workflow_regressions",
            "market_constraint_regressions",
        ),
        reason=(
            "Default Scanner tests now cover the current foundation behavior over "
            "multi-symbol fixtures, invalid filters, missing values, deterministic "
            "ordering, artifact safety, universe/constraint workflows, and the new "
            "ranking/regression paths."
        ),
        evidence=(
            "tests/scanner/test_runner.py now exercises multi-symbol scans, exclusions, missing/stale feature policies, market eligibility handling, and ranked ordering semantics.",
            "tests/scanner/test_storage.py covers manifest determinism, overwrite safety, partial-artifact prevention, and ranked-row serialization safety.",
            "tests/scanner/test_contracts.py validates explicit ranking config contracts and ranked candidate ordering constraints without network access.",
        ),
    ),
)


_FOLLOW_UP_BLUEPRINTS: tuple[_FollowUpBlueprint, ...] = (
    _FollowUpBlueprint(
        follow_up_id="SCN-ART-001",
        capability_group_id="candidate_persistence_and_handoff_readiness",
        disposition=FollowUpDisposition.CONTRACT_REPAIR,
        reason=(
            "Expand persisted candidate artifacts with universe snapshot provenance, "
            "ranking-configuration reproducibility, and downstream handoff metadata "
            "while keeping existing JSONL/manifest safety."
        ),
        recommended_next_handoff_theme=(
            "Candidate artifact schema hardening for reproducibility and downstream handoff"
        ),
    ),
)


_BATCHES: tuple[_BatchBlueprint, ...] = (
    _BatchBlueprint(
        batch_id="scanner_artifact_contract_repair_batch_01",
        theme="Candidate artifact schema and downstream handoff provenance",
        disposition=FollowUpDisposition.CONTRACT_REPAIR,
        item_ids=("SCN-ART-001",),
        rationale=(
            "Artifact-schema expansion changes persisted contracts and should stay isolated "
            "from ordinary hardening so review can focus on compatibility and reproducibility risk."
        ),
    ),
)


__all__ = [
    "FollowUpDisposition",
    "ReadinessStatus",
    "ReadinessStatusCount",
    "ScannerCapabilityGroupReadiness",
    "ScannerFollowUpBatch",
    "ScannerFollowUpItem",
    "ScannerPersonalReadinessGate",
    "build_scanner_personal_readiness_gate",
    "summarize_readiness_status_counts",
]
