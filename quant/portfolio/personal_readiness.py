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
        implemented_capabilities=(),
        reason=(
            "Phase 6 currently has audit scaffolding only. The package still lacks importable "
            "watchlist, holding-state, and cash or exposure contract surfaces."
        ),
        evidence=(
            "quant/portfolio exports readiness-audit primitives only and no watchlist or holding dataclasses.",
            "quant/portfolio/README.md documents future watchlist and holding scope rather than implemented contracts.",
        ),
        limitations=(
            "No structured watchlist records exist for downstream signal routing.",
            "No deterministic holding-state or cash snapshot update surface exists.",
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
        implemented_capabilities=(),
        reason=(
            "No SignalEngine contract or transition surface exists yet, so created, updated, "
            "expired, and closed states cannot be represented or evolved deterministically."
        ),
        evidence=(
            "quant/portfolio contains no lifecycle module or signal-state contract definitions.",
            "No local Phase 6 tests exercise signal creation, expiry, closure, or conflict handling.",
        ),
        limitations=(
            "Signals cannot be persisted or updated with explicit lifecycle truth.",
            "Conflicting entry and exit intents cannot be reconciled deterministically.",
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
        ),
        reason=(
            "Upstream local modules already provide candidate, strategy-definition, and "
            "backtest-summary contracts, but Phase 6 has no composition layer that turns those "
            "inputs into structured signal candidates."
        ),
        evidence=(
            "quant/scanner/contracts.py defines candidate-list and handoff metadata contracts.",
            "quant/strategies/contracts.py defines offline-safe strategy definitions and signal intent metadata.",
            "quant/backtest/contracts.py defines result summary and replay report contracts.",
        ),
        limitations=(
            "There is no local merger surface for scanner, strategy, backtest, and portfolio context.",
            "No structured Phase 6 signal record exists to preserve upstream provenance and ranking context.",
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
        implemented_capabilities=(),
        reason=(
            "RiskEngine is still absent. The repository has no Phase 6 evaluator for exposure, "
            "concentration, liquidity, drawdown, blacklists, suspensions, or market-specific rules."
        ),
        evidence=(
            "quant/portfolio contains no risk evaluation module beyond readiness-audit metadata.",
            "No tests/portfolio workflow coverage exists for blocked signals or sizing guidance behavior.",
        ),
        limitations=(
            "Signals cannot be blocked or sized with explicit personal risk controls.",
            "No market-aware rejection reasons exist for blacklist, suspension, or concentration breaches.",
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
        implemented_capabilities=("upstream_source_reference_capture",),
        reason=(
            "Upstream modules already expose reference metadata that Phase 6 can reuse, but there "
            "is no signal-level audit record for why a signal exists or why it passed or failed risk checks."
        ),
        evidence=(
            "quant/scanner/contracts.py includes handoff metadata and universe snapshot provenance.",
            "quant/backtest/contracts.py includes request and artifact references that can anchor downstream audit trails.",
            "quant/portfolio defines no signal audit record or risk decision log contract yet.",
        ),
        limitations=(
            "A downstream reviewer cannot reconstruct why a signal was admitted, blocked, expired, or closed.",
            "Risk decisions have no deterministic, testable explanation surface.",
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
        implemented_capabilities=(),
        reason=(
            "This task adds readiness-gate tests only. The required Phase 6 workflow regressions "
            "still do not exist because the portfolio, signal, and risk execution surfaces are absent."
        ),
        evidence=(
            "tests/portfolio/test_personal_readiness.py validates audit metadata, not portfolio or signal workflows.",
            "No local Phase 6 tests cover stale inputs, risk blocks, lifecycle transitions, or conflicting signals.",
        ),
        limitations=(
            "Future Phase 6 logic could regress without lifecycle or risk-scenario protections.",
            "There is no offline proof yet that stale or conflicting inputs are handled deterministically.",
        ),
        recommended_follow_up_disposition=FollowUpDisposition.PORTFOLIO_SIGNAL_RISK_HARDENING,
    ),
)


_FOLLOW_UP_BLUEPRINTS: tuple[_FollowUpBlueprint, ...] = (
    _FollowUpBlueprint(
        follow_up_id="phase6__portfolio_watchlist_and_holding_state_contracts",
        capability_group_id="watchlist_and_holding_state_contracts",
        disposition=FollowUpDisposition.PORTFOLIO_SIGNAL_RISK_HARDENING,
        reason=(
            "Add the first offline-safe portfolio state contracts so watchlists, holdings, and "
            "cash or exposure snapshots can be updated deterministically."
        ),
        recommended_next_handoff_title=(
            "Phase 6 portfolio/watchlist and signal lifecycle contract foundation"
        ),
        recommended_next_handoff_theme=(
            "portfolio watchlist, holding-state, and deterministic state-update contracts"
        ),
    ),
    _FollowUpBlueprint(
        follow_up_id="phase6__signal_lifecycle_and_audit_contracts",
        capability_group_id="signal_lifecycle_management",
        disposition=FollowUpDisposition.PORTFOLIO_SIGNAL_RISK_HARDENING,
        reason=(
            "Define structured signal records with created, updated, expired, and closed states "
            "before adding composition or risk evaluation behavior."
        ),
        recommended_next_handoff_title=(
            "Phase 6 portfolio/watchlist and signal lifecycle contract foundation"
        ),
        recommended_next_handoff_theme=(
            "signal lifecycle states, source linkage, and deterministic transition contracts"
        ),
    ),
    _FollowUpBlueprint(
        follow_up_id="phase6__signal_source_link_and_decision_audit_contracts",
        capability_group_id="signal_auditability_and_decision_trace",
        disposition=FollowUpDisposition.PORTFOLIO_SIGNAL_RISK_HARDENING,
        reason=(
            "Capture why a signal exists and why it passed or failed risk checks so later "
            "Phase 6 logic remains auditable rather than opaque."
        ),
        recommended_next_handoff_title=(
            "Phase 6 portfolio/watchlist and signal lifecycle contract foundation"
        ),
        recommended_next_handoff_theme=(
            "signal lifecycle states, source linkage, and deterministic transition contracts"
        ),
    ),
    _FollowUpBlueprint(
        follow_up_id="phase6__upstream_signal_composition_foundation",
        capability_group_id="upstream_context_combination_into_structured_signals",
        disposition=FollowUpDisposition.PORTFOLIO_SIGNAL_RISK_HARDENING,
        reason=(
            "Add an offline composition surface that merges scanner candidates, strategy intent, "
            "backtest context, and portfolio state into structured signal candidates."
        ),
        recommended_next_handoff_title=(
            "Phase 6 structured signal composition and risk rule foundation"
        ),
        recommended_next_handoff_theme=(
            "integration-shaped composition from scanner, strategy, backtest, and portfolio context"
        ),
    ),
    _FollowUpBlueprint(
        follow_up_id="phase6__risk_rule_evaluation_foundation",
        capability_group_id="risk_rule_evaluation_foundation",
        disposition=FollowUpDisposition.PORTFOLIO_SIGNAL_RISK_HARDENING,
        reason=(
            "Implement deterministic personal risk rules for exposure, concentration, liquidity, "
            "drawdown, sizing guidance, blacklists, suspensions, and market constraints."
        ),
        recommended_next_handoff_title=(
            "Phase 6 structured signal composition and risk rule foundation"
        ),
        recommended_next_handoff_theme=(
            "risk rule evaluation for exposure, concentration, liquidity, drawdown, sizing, and market constraints"
        ),
    ),
    _FollowUpBlueprint(
        follow_up_id="phase6__conflicting_and_risk_blocked_signal_regressions",
        capability_group_id="offline_regression_coverage_for_conflicts_staleness_risk_and_lifecycle",
        disposition=FollowUpDisposition.PORTFOLIO_SIGNAL_RISK_HARDENING,
        reason=(
            "Protect the first executable Phase 6 workflow with conflicting-signal and "
            "risk-blocked regression cases."
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
            "Add stale-input and lifecycle-transition regression coverage once the first "
            "signal and risk contracts exist."
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
        batch_id="portfolio_signal_risk__personal_trading_hardening__batch_01",
        title="Phase 6 portfolio/watchlist and signal lifecycle contract foundation",
        theme="portfolio state contracts plus signal lifecycle and audit foundations",
        disposition=FollowUpDisposition.PORTFOLIO_SIGNAL_RISK_HARDENING,
        item_ids=(
            "phase6__portfolio_watchlist_and_holding_state_contracts",
            "phase6__signal_lifecycle_and_audit_contracts",
            "phase6__signal_source_link_and_decision_audit_contracts",
        ),
        rationale=(
            "Phase 6 still starts from a placeholder package, so the highest-priority gap is "
            "establishing stable portfolio-state and signal-state contracts before composition "
            "or risk decisions are implemented."
        ),
    ),
    _BatchBlueprint(
        batch_id="portfolio_signal_risk__personal_trading_hardening__batch_02",
        title="Phase 6 structured signal composition and risk rule foundation",
        theme="upstream context composition and deterministic risk rule evaluation",
        disposition=FollowUpDisposition.PORTFOLIO_SIGNAL_RISK_HARDENING,
        item_ids=(
            "phase6__upstream_signal_composition_foundation",
            "phase6__risk_rule_evaluation_foundation",
        ),
        rationale=(
            "Once contracts exist, the next Phase 6 step is turning scanner, strategy, "
            "backtest, and portfolio context into structured signals and then evaluating them "
            "against explicit personal risk rules."
        ),
    ),
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
            "The first executable Phase 6 workflow must immediately gain offline regression "
            "coverage for conflicting signals, stale inputs, risk blocks, and lifecycle transitions."
        ),
    ),
)
