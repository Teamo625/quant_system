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
        recommended_next_handoff_batch_id="scanner_universe_constraints_batch_01",
        recommended_next_handoff_theme=(
            "Universe presets, exclusion lists, and market-constraint hardening"
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
            "custom_watchlist_validation",
            "deterministic_symbol_normalization",
            "membership_snapshot_validation",
            "manual_market_label_preservation",
        ),
        reason=(
            "The current Scanner surface validates caller-provided universe identities "
            "and membership snapshots, but it still treats the market field as a free-form "
            "label and does not model A-share, Hong Kong, ETF/fund, sector, index, or "
            "exclusion-list specific universe semantics."
        ),
        evidence=(
            "TASK-065 accepted quant/scanner/universe.py for declarative universe definitions, symbol normalization, and membership snapshot validation.",
            "quant/scanner/universe.py only requires universe_id, universe_name, market, source, and optional description; it does not distinguish universe families.",
            "tests/scanner/test_universe.py covers deterministic symbol normalization and definition/snapshot mismatch handling, but not exchange-specific presets or exclusion lists.",
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
            "deterministic_contract_ordering",
            "symbol_market_sort_fallback",
        ),
        reason=(
            "Current candidate ordering is only the contract-stable `(symbol, market)` "
            "sort used by the foundation runner and validation layer. There is no "
            "ranking configuration, score output, tie-break logic, or research-priority "
            "ordering suitable for personal trading candidate review."
        ),
        evidence=(
            "quant/scanner/runner.py emits candidates sorted by `(symbol, market)` after conjunctive filter matching.",
            "quant/scanner/contracts.py defines ScanCandidateRecord without rank, score, or ordering metadata fields.",
            "TASK-068 report explicitly records ranking and scoring as out of scope for the foundation slice.",
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
        ),
        reason=(
            "Scanner can already persist validated candidate rows with deterministic "
            "manifests and checksum protection, but the artifact contract still lacks "
            "explicit universe snapshot provenance and richer downstream handoff "
            "metadata needed for repeated personal research workflows."
        ),
        evidence=(
            "TASK-066 accepted quant/scanner/storage.py for deterministic JSONL plus manifest writes with overwrite preflight and content checksums.",
            "quant/scanner/storage.py manifests carry run metadata, feature refs, filters, candidate count, and checksum only.",
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
            "hard_failure_on_missing_symbol_feature_map",
            "hard_failure_on_missing_feature_value",
        ),
        reason=(
            "The current runner truthfully fails when required feature inputs are absent, "
            "but it has no explicit policy for stale features, suspended securities, "
            "limit-up/down constraints, exclusion rules, or market-specific eligibility."
        ),
        evidence=(
            "quant/scanner/runner.py raises MissingSymbolFeatureValuesError when a universe symbol lacks feature values.",
            "quant/scanner/matching.py raises MissingFeatureValueError or InvalidFeatureValueError instead of applying configurable missing/stale handling.",
            "No Scanner contract or runner path references suspension, limit-up/down, exclusion-list, or market-constraint semantics.",
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
        ),
        reason=(
            "Default Scanner tests already cover the current foundation behavior over "
            "multi-symbol fixtures, invalid filters, missing values, deterministic "
            "ordering, and artifact-write safety. They do not yet cover ranking or "
            "market-constraint workflows because those capabilities do not exist."
        ),
        evidence=(
            "tests/scanner/test_runner.py exercises multi-symbol scans, missing symbol feature values, invalid filters, and output validation.",
            "tests/scanner/test_storage.py covers manifest determinism, overwrite safety, and partial-artifact prevention.",
            "There are no Scanner tests for ranking, exclusion lists, stale-feature policy, suspension handling, or limit-up/down eligibility.",
        ),
    ),
)


_FOLLOW_UP_BLUEPRINTS: tuple[_FollowUpBlueprint, ...] = (
    _FollowUpBlueprint(
        follow_up_id="SCN-UNI-001",
        capability_group_id="universe_definition_and_validation",
        disposition=FollowUpDisposition.SCANNER_HARDENING,
        reason=(
            "Add explicit universe-family contracts or validators for A-share, Hong Kong, "
            "ETF/fund, sector, and index scan presets instead of treating all universes "
            "as generic symbol bags."
        ),
        recommended_next_handoff_theme=(
            "Universe presets and market-aware validation for supported scan domains"
        ),
    ),
    _FollowUpBlueprint(
        follow_up_id="SCN-UNI-002",
        capability_group_id="universe_definition_and_validation",
        disposition=FollowUpDisposition.SCANNER_HARDENING,
        reason=(
            "Model exclusion lists as first-class Scanner inputs so watchlists and "
            "broad universes can be trimmed deterministically without manual prefiltering."
        ),
        recommended_next_handoff_theme=(
            "Exclusion-list contracts, validation, and deterministic scan input composition"
        ),
    ),
    _FollowUpBlueprint(
        follow_up_id="SCN-RANK-001",
        capability_group_id="ranking_scoring_and_candidate_ordering",
        disposition=FollowUpDisposition.SCANNER_HARDENING,
        reason=(
            "Introduce explicit ranking/scoring configuration and candidate ordering "
            "semantics so scan output is prioritized for research review instead of "
            "remaining in lexicographic symbol order."
        ),
        recommended_next_handoff_theme=(
            "Ranking, scoring, and tie-break ordering for research candidate prioritization"
        ),
    ),
    _FollowUpBlueprint(
        follow_up_id="SCN-ART-001",
        capability_group_id="candidate_persistence_and_handoff_readiness",
        disposition=FollowUpDisposition.CONTRACT_REPAIR,
        reason=(
            "Expand persisted candidate artifacts with universe snapshot provenance and "
            "downstream handoff metadata while keeping existing JSONL/manifest safety."
        ),
        recommended_next_handoff_theme=(
            "Candidate artifact schema hardening for reproducibility and downstream handoff"
        ),
    ),
    _FollowUpBlueprint(
        follow_up_id="SCN-CONSTRAINT-001",
        capability_group_id="market_constraints_and_missing_data_handling",
        disposition=FollowUpDisposition.SCANNER_HARDENING,
        reason=(
            "Define configurable policies for missing or stale feature inputs instead of "
            "only hard-failing scan execution."
        ),
        recommended_next_handoff_theme=(
            "Missing-feature and stale-feature handling semantics for offline scan workflows"
        ),
    ),
    _FollowUpBlueprint(
        follow_up_id="SCN-CONSTRAINT-002",
        capability_group_id="market_constraints_and_missing_data_handling",
        disposition=FollowUpDisposition.SCANNER_HARDENING,
        reason=(
            "Add first-class eligibility handling for suspension, limit-up/down, and "
            "market-specific constraints so candidate output reflects realistic "
            "personal trading review rules."
        ),
        recommended_next_handoff_theme=(
            "Market-constraint and eligibility filtering for supported markets"
        ),
    ),
    _FollowUpBlueprint(
        follow_up_id="SCN-TEST-001",
        capability_group_id="offline_scan_workflow_regression_coverage",
        disposition=FollowUpDisposition.SCANNER_HARDENING,
        reason=(
            "Broaden default offline regression coverage to the new universe, ranking, "
            "and market-constraint paths once they are implemented."
        ),
        recommended_next_handoff_theme=(
            "End-to-end Scanner workflow regressions for ordering, constraints, and artifacts"
        ),
    ),
)


_BATCHES: tuple[_BatchBlueprint, ...] = (
    _BatchBlueprint(
        batch_id="scanner_universe_constraints_batch_01",
        theme="Universe presets, exclusion lists, and market constraints",
        disposition=FollowUpDisposition.SCANNER_HARDENING,
        item_ids=(
            "SCN-UNI-001",
            "SCN-UNI-002",
            "SCN-CONSTRAINT-001",
            "SCN-CONSTRAINT-002",
        ),
        rationale=(
            "These four items all harden scan-input eligibility and can share contract, "
            "runner, and offline test changes without crossing into ranking or downstream modules."
        ),
    ),
    _BatchBlueprint(
        batch_id="scanner_ranking_workflow_batch_01",
        theme="Ranking, scoring, and workflow regression depth",
        disposition=FollowUpDisposition.SCANNER_HARDENING,
        item_ids=(
            "SCN-RANK-001",
            "SCN-TEST-001",
        ),
        rationale=(
            "Ranking/scoring changes should land with deterministic workflow regression "
            "coverage so ordering semantics are proven offline in the same batch."
        ),
    ),
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
