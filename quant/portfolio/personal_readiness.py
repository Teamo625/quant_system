"""Deterministic Portfolio/Signal/Risk personal-readiness gate for Phase 6 audits."""

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
    PORTFOLIO_SIGNAL_RISK_HARDENING = "portfolio_signal_risk_hardening"
    CONTRACT_REPAIR = "contract_repair"
    OWNER_BLOCKER = "owner_blocker"
    BLOCKED_UPSTREAM = "blocked_upstream"


@dataclass(frozen=True)
class ReadinessStatusCount:
    status: ReadinessStatus
    count: int


@dataclass(frozen=True)
class PortfolioSignalRiskCapabilityGroupReadiness:
    group_id: str
    name: str
    status: ReadinessStatus
    reason: str
    required_capabilities: tuple[str, ...]
    implemented_capabilities: tuple[str, ...]
    missing_capabilities: tuple[str, ...]
    evidence: tuple[str, ...]
    limitations: tuple[str, ...]
    recommended_follow_up_disposition: FollowUpDisposition


@dataclass(frozen=True)
class PortfolioSignalRiskFollowUpItem:
    follow_up_id: str
    capability_group_id: str
    status: ReadinessStatus
    disposition: FollowUpDisposition
    reason: str
    recommended_next_handoff_title: str
    recommended_next_handoff_theme: str


@dataclass(frozen=True)
class PortfolioSignalRiskFollowUpBatch:
    batch_id: str
    title: str
    theme: str
    disposition: FollowUpDisposition
    item_ids: tuple[str, ...]
    rationale: str


@dataclass(frozen=True)
class PortfolioSignalRiskPersonalReadinessGate:
    phase_id: str
    phase_closure_ready: bool
    capability_groups: tuple[PortfolioSignalRiskCapabilityGroupReadiness, ...]
    status_counts: tuple[ReadinessStatusCount, ...]
    follow_up_queue: tuple[PortfolioSignalRiskFollowUpItem, ...]
    follow_up_batches: tuple[PortfolioSignalRiskFollowUpBatch, ...]
    recommended_next_handoff_batch_id: str
    recommended_next_handoff_title: str
    recommended_next_handoff_theme: str
    recommended_next_handoff_rationale: str


@dataclass(frozen=True)
class _CapabilityGroupBlueprint:
    group_id: str
    name: str
    required_capabilities: tuple[str, ...]
    implemented_capabilities: tuple[str, ...]
    reason: str
    evidence: tuple[str, ...]
    limitations: tuple[str, ...]
    recommended_follow_up_disposition: FollowUpDisposition
    blocked: bool = False
    failed: bool = False


@dataclass(frozen=True)
class _FollowUpBlueprint:
    follow_up_id: str
    capability_group_id: str
    disposition: FollowUpDisposition
    reason: str
    recommended_next_handoff_title: str
    recommended_next_handoff_theme: str
    blocked: bool = False


@dataclass(frozen=True)
class _BatchBlueprint:
    batch_id: str
    title: str
    theme: str
    disposition: FollowUpDisposition
    item_ids: tuple[str, ...]
    rationale: str


def build_portfolio_signal_risk_personal_readiness_gate(
) -> PortfolioSignalRiskPersonalReadinessGate:
    """Return the deterministic Phase 6 readiness audit snapshot."""
    capability_groups = tuple(
        _build_capability_group(blueprint) for blueprint in _CAPABILITY_GROUP_BLUEPRINTS
    )
    status_counts = summarize_readiness_status_counts(capability_groups)
    follow_up_queue = tuple(
        _build_follow_up_item(blueprint, capability_groups)
        for blueprint in _FOLLOW_UP_BLUEPRINTS
    )
    follow_up_batches = tuple(_build_follow_up_batch(blueprint) for blueprint in _BATCHES)
    _validate_follow_up_plan(capability_groups, follow_up_queue, follow_up_batches)

    recommended_batch = follow_up_batches[0]
    return PortfolioSignalRiskPersonalReadinessGate(
        phase_id="Phase 6 PortfolioMonitor, SignalEngine, and RiskEngine Personal Trading Perfection",
        phase_closure_ready=all(
            group.status is ReadinessStatus.PASS for group in capability_groups
        ),
        capability_groups=capability_groups,
        status_counts=status_counts,
        follow_up_queue=follow_up_queue,
        follow_up_batches=follow_up_batches,
        recommended_next_handoff_batch_id=recommended_batch.batch_id,
        recommended_next_handoff_title=recommended_batch.title,
        recommended_next_handoff_theme=recommended_batch.theme,
        recommended_next_handoff_rationale=recommended_batch.rationale,
    )


def summarize_readiness_status_counts(
    capability_groups: tuple[PortfolioSignalRiskCapabilityGroupReadiness, ...],
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
) -> PortfolioSignalRiskCapabilityGroupReadiness:
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

    return PortfolioSignalRiskCapabilityGroupReadiness(
        group_id=blueprint.group_id,
        name=blueprint.name,
        status=status,
        reason=blueprint.reason,
        required_capabilities=blueprint.required_capabilities,
        implemented_capabilities=implemented,
        missing_capabilities=missing,
        evidence=blueprint.evidence,
        limitations=blueprint.limitations,
        recommended_follow_up_disposition=blueprint.recommended_follow_up_disposition,
    )


def _build_follow_up_item(
    blueprint: _FollowUpBlueprint,
    capability_groups: tuple[PortfolioSignalRiskCapabilityGroupReadiness, ...],
) -> PortfolioSignalRiskFollowUpItem:
    group_by_id = {group.group_id: group for group in capability_groups}
    group = group_by_id[blueprint.capability_group_id]
    if blueprint.blocked:
        status = ReadinessStatus.BLOCKED
    elif group.status is ReadinessStatus.FAIL:
        status = ReadinessStatus.FAIL
    else:
        status = ReadinessStatus.WARN

    return PortfolioSignalRiskFollowUpItem(
        follow_up_id=blueprint.follow_up_id,
        capability_group_id=blueprint.capability_group_id,
        status=status,
        disposition=blueprint.disposition,
        reason=blueprint.reason,
        recommended_next_handoff_title=blueprint.recommended_next_handoff_title,
        recommended_next_handoff_theme=blueprint.recommended_next_handoff_theme,
    )


def _build_follow_up_batch(
    blueprint: _BatchBlueprint,
) -> PortfolioSignalRiskFollowUpBatch:
    return PortfolioSignalRiskFollowUpBatch(
        batch_id=blueprint.batch_id,
        title=blueprint.title,
        theme=blueprint.theme,
        disposition=blueprint.disposition,
        item_ids=blueprint.item_ids,
        rationale=blueprint.rationale,
    )


def _validate_follow_up_plan(
    capability_groups: tuple[PortfolioSignalRiskCapabilityGroupReadiness, ...],
    follow_up_queue: tuple[PortfolioSignalRiskFollowUpItem, ...],
    follow_up_batches: tuple[PortfolioSignalRiskFollowUpBatch, ...],
) -> None:
    group_ids = {group.group_id for group in capability_groups}
    queue_ids = {item.follow_up_id for item in follow_up_queue}
    batch_item_ids: set[str] = set()
    follow_up_group_counts = Counter(item.capability_group_id for item in follow_up_queue)

    for item in follow_up_queue:
        if item.capability_group_id not in group_ids:
            raise ValueError(
                f"unknown capability group referenced by follow-up item: {item.capability_group_id}"
            )

    for group in capability_groups:
        if group.status is ReadinessStatus.PASS:
            if follow_up_group_counts.get(group.group_id, 0):
                raise ValueError(
                    "phase-closure-ready capability groups must not retain follow-up items"
                )
            continue
        if not follow_up_group_counts.get(group.group_id, 0):
            raise ValueError(
                f"non-pass capability group missing follow-up coverage: {group.group_id}"
            )

    for batch in follow_up_batches:
        if (
            len(batch.item_ids) == 1
            and batch.disposition is FollowUpDisposition.PORTFOLIO_SIGNAL_RISK_HARDENING
        ):
            raise ValueError(
                "ordinary portfolio/signal/risk hardening batches must group at least two items"
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
        group_id="watchlist_and_holding_state_contracts",
        name="Watchlist and Holding-State Contracts with Deterministic Updates",
        required_capabilities=(
            "watchlist_contracts",
            "holding_state_contracts",
            "cash_exposure_snapshot_contracts",
            "deterministic_portfolio_update_inputs",
        ),
        implemented_capabilities=(
            "watchlist_contracts",
            "holding_state_contracts",
            "cash_exposure_snapshot_contracts",
            "deterministic_portfolio_update_inputs",
        ),
        reason=(
            "Phase 6 now provides local/offline watchlist, holding-state, and cash or exposure "
            "contracts plus deterministic merge helpers for caller-provided records."
        ),
        evidence=(
            "quant/portfolio/contracts.py defines WatchlistItem, WatchlistSnapshot, HoldingState, HoldingSnapshot, and CashExposureSnapshot.",
            "quant/portfolio/contracts.py exports deterministic build/merge helpers for watchlist and holding snapshots.",
            "tests/portfolio/test_contracts.py covers valid construction, deterministic merge order, and duplicate or malformed portfolio-state rejection.",
        ),
        limitations=(
            "These contracts are still local/offline only and rely on caller-provided inputs.",
            "Broader conflict and lifecycle workflow regressions remain pending in the next batch.",
        ),
        recommended_follow_up_disposition=FollowUpDisposition.PORTFOLIO_SIGNAL_RISK_HARDENING,
    ),
    _CapabilityGroupBlueprint(
        group_id="signal_lifecycle_management",
        name="Signal Lifecycle Management",
        required_capabilities=(
            "signal_record_contracts",
            "created_state",
            "updated_state",
            "expired_state",
            "closed_state",
            "deterministic_state_transition_rules",
            "conflict_resolution_markers",
        ),
        implemented_capabilities=(
            "signal_record_contracts",
            "created_state",
            "updated_state",
            "expired_state",
            "closed_state",
            "deterministic_state_transition_rules",
            "conflict_resolution_markers",
        ),
        reason=(
            "Phase 6 now exposes a local signal contract with explicit lifecycle states, conflict "
            "markers, and deterministic transition validation for created, updated, expired, and closed flows."
        ),
        evidence=(
            "quant/portfolio/contracts.py defines SignalRecord, SignalLifecycleState, SignalConflictStatus, create_signal_record, and transition_signal_state.",
            "tests/portfolio/test_contracts.py covers signal creation, update, expiry, closure, and invalid transition rejection.",
        ),
        limitations=(
            "Conflict supersession remains marker-based until broader workflow regressions are added.",
            "Lifecycle depth beyond the first composed and risk-evaluated workflow remains pending.",
        ),
        recommended_follow_up_disposition=FollowUpDisposition.PORTFOLIO_SIGNAL_RISK_HARDENING,
    ),
    _CapabilityGroupBlueprint(
        group_id="upstream_context_combination_into_structured_signals",
        name="Structured Signal Composition from Scanner, Strategy, Backtest, and Portfolio Context",
        required_capabilities=(
            "scanner_candidate_input_contract",
            "strategy_output_input_contract",
            "backtest_report_input_contract",
            "portfolio_context_merge",
            "structured_signal_output_contract",
        ),
        implemented_capabilities=(
            "scanner_candidate_input_contract",
            "strategy_output_input_contract",
            "backtest_report_input_contract",
            "portfolio_context_merge",
            "structured_signal_output_contract",
        ),
        reason=(
            "Phase 6 now exposes a local/offline composition surface that converts "
            "caller-provided scanner, strategy, backtest, and portfolio context into "
            "deterministic structured SignalRecord outputs."
        ),
        evidence=(
            "quant/portfolio/signal_composition.py defines scanner, strategy, and backtest evidence contracts plus compose_structured_signals().",
            "quant/portfolio/signal_composition.py validates duplicate ids, symbol mismatches, unsupported intents, stale inputs, and holding-intent consistency.",
            "tests/portfolio/test_signal_risk.py covers deterministic signal ids, ordering, source links, stale-input warnings, and inconsistent-evidence rejection.",
        ),
        limitations=(
            "Conflicting multi-signal workflows remain pending for the next regression batch.",
            "Lifecycle regressions beyond the first composed/risk-evaluated workflow remain pending.",
        ),
        recommended_follow_up_disposition=FollowUpDisposition.PORTFOLIO_SIGNAL_RISK_HARDENING,
    ),
    _CapabilityGroupBlueprint(
        group_id="risk_rule_evaluation_foundation",
        name="Risk Rule Evaluation Foundation",
        required_capabilities=(
            "exposure_rules",
            "concentration_rules",
            "liquidity_rules",
            "drawdown_rules",
            "position_sizing_guidance",
            "blacklist_support",
            "suspension_support",
            "market_specific_constraints",
        ),
        implemented_capabilities=(
            "exposure_rules",
            "concentration_rules",
            "liquidity_rules",
            "drawdown_rules",
            "position_sizing_guidance",
            "blacklist_support",
            "suspension_support",
            "market_specific_constraints",
        ),
        reason=(
            "Phase 6 now includes a deterministic local risk-rule evaluator covering exposure, "
            "concentration, liquidity, drawdown, sizing guidance, blacklists, suspensions, and market constraints."
        ),
        evidence=(
            "quant/portfolio/risk_rules.py defines risk contracts, sizing guidance, and evaluate_signal_risk().",
            "quant/portfolio/risk_rules.py emits explicit pass/warn/block outcomes plus updated signal audit records.",
            "tests/portfolio/test_signal_risk.py covers pass, warn, and block outcomes across the required rule families and invalid configuration rejection.",
        ),
        limitations=(
            "Risk evaluation is still local/offline and depends on caller-provided market context only.",
            "Remaining Phase 6 regression work still needs broader conflicting-signal and lifecycle scenario coverage.",
        ),
        recommended_follow_up_disposition=FollowUpDisposition.PORTFOLIO_SIGNAL_RISK_HARDENING,
    ),
    _CapabilityGroupBlueprint(
        group_id="signal_auditability_and_decision_trace",
        name="Signal Auditability and Decision Trace",
        required_capabilities=(
            "upstream_source_reference_capture",
            "signal_reason_capture",
            "risk_check_audit_records",
            "signal_pass_fail_decision_trace",
            "closure_reason_capture",
        ),
        implemented_capabilities=(
            "upstream_source_reference_capture",
            "signal_reason_capture",
            "risk_check_audit_records",
            "signal_pass_fail_decision_trace",
            "closure_reason_capture",
        ),
        reason=(
            "Phase 6 now captures source-link references and decision-audit records so a local "
            "reviewer can reconstruct why a signal exists and why later checks passed, warned, blocked, expired, or closed."
        ),
        evidence=(
            "quant/portfolio/contracts.py defines SignalSourceLink, SignalSourceType, DecisionAuditRecord, and create_decision_audit_record.",
            "quant/portfolio/contracts.py requires closure_reason or expiry_reason when lifecycle state requires them.",
            "tests/portfolio/test_contracts.py validates source-link and decision-audit contract behavior.",
        ),
        limitations=(
            "Audit records remain local/offline truth over caller-provided evidence only.",
            "Broader conflicting-signal and lifecycle workflow regressions remain pending.",
        ),
        recommended_follow_up_disposition=FollowUpDisposition.PORTFOLIO_SIGNAL_RISK_HARDENING,
    ),
    _CapabilityGroupBlueprint(
        group_id="offline_regression_coverage_for_conflicts_staleness_risk_and_lifecycle",
        name="Offline Regression Coverage for Conflicts, Stale Inputs, Risk Blocks, and Lifecycle Transitions",
        required_capabilities=(
            "conflicting_signal_tests",
            "stale_input_tests",
            "risk_blocked_signal_tests",
            "lifecycle_transition_tests",
        ),
        implemented_capabilities=(
            "stale_input_tests",
            "risk_blocked_signal_tests",
            "lifecycle_transition_tests",
        ),
        reason=(
            "TASK-153 adds first executable stale-input and risk-blocked workflow coverage, but "
            "broader conflicting-signal and lifecycle regression depth still remains for the next batch."
        ),
        evidence=(
            "tests/portfolio/test_contracts.py covers lifecycle transition success and invalid transition rejection.",
            "tests/portfolio/test_signal_risk.py covers stale composition warnings and blocked risk-rule workflows.",
        ),
        limitations=(
            "There is still no deterministic end-to-end proof for conflicting signals or supersession handling.",
            "Broader multi-step lifecycle regressions over composed signals remain pending.",
        ),
        recommended_follow_up_disposition=FollowUpDisposition.PORTFOLIO_SIGNAL_RISK_HARDENING,
    ),
)


_FOLLOW_UP_BLUEPRINTS: tuple[_FollowUpBlueprint, ...] = (
    _FollowUpBlueprint(
        follow_up_id="phase6__conflicting_and_risk_blocked_signal_regressions",
        capability_group_id="offline_regression_coverage_for_conflicts_staleness_risk_and_lifecycle",
        disposition=FollowUpDisposition.PORTFOLIO_SIGNAL_RISK_HARDENING,
        reason=(
            "Expand the first executable Phase 6 workflow with explicit conflicting-signal, "
            "supersession, and broader risk-block regression depth."
        ),
        recommended_next_handoff_title=(
            "Phase 6 offline regression coverage for conflict, staleness, risk blocks, and lifecycle transitions"
        ),
        recommended_next_handoff_theme=(
            "offline regressions for conflicting signals, risk blocks, stale data, and lifecycle transitions"
        ),
    ),
    _FollowUpBlueprint(
        follow_up_id="phase6__stale_input_and_lifecycle_transition_regressions",
        capability_group_id="offline_regression_coverage_for_conflicts_staleness_risk_and_lifecycle",
        disposition=FollowUpDisposition.PORTFOLIO_SIGNAL_RISK_HARDENING,
        reason=(
            "Extend stale-input and lifecycle-transition coverage from focused task proofs to "
            "broader end-to-end composed-signal regressions."
        ),
        recommended_next_handoff_title=(
            "Phase 6 offline regression coverage for conflict, staleness, risk blocks, and lifecycle transitions"
        ),
        recommended_next_handoff_theme=(
            "offline regressions for conflicting signals, risk blocks, stale data, and lifecycle transitions"
        ),
    ),
)


_BATCHES: tuple[_BatchBlueprint, ...] = (
    _BatchBlueprint(
        batch_id="portfolio_signal_risk__personal_trading_hardening__batch_03",
        title=(
            "Phase 6 offline regression coverage for conflict, staleness, risk blocks, and lifecycle transitions"
        ),
        theme="workflow regression coverage for signal conflicts, stale inputs, and blocked states",
        disposition=FollowUpDisposition.PORTFOLIO_SIGNAL_RISK_HARDENING,
        item_ids=(
            "phase6__conflicting_and_risk_blocked_signal_regressions",
            "phase6__stale_input_and_lifecycle_transition_regressions",
        ),
        rationale=(
            "Now that Phase 6 has an executable composition and risk workflow, the next batch "
            "should deepen deterministic regressions for conflicting signals, stale inputs, "
            "risk blocks, and lifecycle transitions."
        ),
    ),
)
