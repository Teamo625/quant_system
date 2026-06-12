"""Deterministic StrategyLab/BacktestEngine personal-readiness gate for Phase 5 audits."""

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
    STRATEGY_BACKTEST_HARDENING = "strategy_backtest_hardening"
    CONTRACT_REPAIR = "contract_repair"
    OWNER_BLOCKER = "owner_blocker"
    BLOCKED_UPSTREAM = "blocked_upstream"


@dataclass(frozen=True)
class ReadinessStatusCount:
    status: ReadinessStatus
    count: int


@dataclass(frozen=True)
class StrategyBacktestCapabilityGroupReadiness:
    group_id: str
    label: str
    status: ReadinessStatus
    reason: str
    required_capabilities: tuple[str, ...]
    implemented_capabilities: tuple[str, ...]
    missing_capabilities: tuple[str, ...]
    evidence: tuple[str, ...]


@dataclass(frozen=True)
class StrategyBacktestFollowUpItem:
    follow_up_id: str
    capability_group_id: str
    status: ReadinessStatus
    disposition: FollowUpDisposition
    reason: str
    recommended_next_handoff_theme: str


@dataclass(frozen=True)
class StrategyBacktestFollowUpBatch:
    batch_id: str
    theme: str
    disposition: FollowUpDisposition
    item_ids: tuple[str, ...]
    rationale: str


@dataclass(frozen=True)
class StrategyBacktestPersonalReadinessGate:
    phase_id: str
    phase_closure_ready: bool
    capability_groups: tuple[StrategyBacktestCapabilityGroupReadiness, ...]
    status_counts: tuple[ReadinessStatusCount, ...]
    follow_up_queue: tuple[StrategyBacktestFollowUpItem, ...]
    follow_up_batches: tuple[StrategyBacktestFollowUpBatch, ...]
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


def build_strategy_backtest_personal_readiness_gate() -> StrategyBacktestPersonalReadinessGate:
    """Return the deterministic Phase 5 readiness audit snapshot."""
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

    return StrategyBacktestPersonalReadinessGate(
        phase_id="Phase 5 StrategyLab and BacktestEngine Personal Trading Perfection",
        phase_closure_ready=all(
            group.status is ReadinessStatus.PASS for group in capability_groups
        ),
        capability_groups=capability_groups,
        status_counts=status_counts,
        follow_up_queue=follow_up_queue,
        follow_up_batches=follow_up_batches,
        recommended_next_handoff_batch_id=(
            follow_up_batches[0].batch_id if follow_up_batches else ""
        ),
        recommended_next_handoff_theme=(follow_up_batches[0].theme if follow_up_batches else ""),
    )


def summarize_readiness_status_counts(
    capability_groups: tuple[StrategyBacktestCapabilityGroupReadiness, ...],
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
) -> StrategyBacktestCapabilityGroupReadiness:
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

    return StrategyBacktestCapabilityGroupReadiness(
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
    capability_groups: tuple[StrategyBacktestCapabilityGroupReadiness, ...],
) -> StrategyBacktestFollowUpItem:
    group_by_id = {group.group_id: group for group in capability_groups}
    group = group_by_id[blueprint.capability_group_id]
    if blueprint.blocked:
        status = ReadinessStatus.BLOCKED
    elif group.status is ReadinessStatus.FAIL:
        status = ReadinessStatus.FAIL
    else:
        status = ReadinessStatus.WARN

    return StrategyBacktestFollowUpItem(
        follow_up_id=blueprint.follow_up_id,
        capability_group_id=blueprint.capability_group_id,
        status=status,
        disposition=blueprint.disposition,
        reason=blueprint.reason,
        recommended_next_handoff_theme=blueprint.recommended_next_handoff_theme,
    )


def _build_follow_up_batch(blueprint: _BatchBlueprint) -> StrategyBacktestFollowUpBatch:
    return StrategyBacktestFollowUpBatch(
        batch_id=blueprint.batch_id,
        theme=blueprint.theme,
        disposition=blueprint.disposition,
        item_ids=blueprint.item_ids,
        rationale=blueprint.rationale,
    )


def _validate_follow_up_batches(
    follow_up_queue: tuple[StrategyBacktestFollowUpItem, ...],
    follow_up_batches: tuple[StrategyBacktestFollowUpBatch, ...],
) -> None:
    queue_ids = {item.follow_up_id for item in follow_up_queue}
    batch_item_ids: set[str] = set()

    for batch in follow_up_batches:
        if (
            len(batch.item_ids) == 1
            and batch.disposition is FollowUpDisposition.STRATEGY_BACKTEST_HARDENING
        ):
            raise ValueError(
                "ordinary strategy/backtest hardening batches must group at least two follow-up items"
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
        group_id="strategy_definition_and_starter_library",
        label="Strategy Definition, Rule Evaluation, and Starter Library",
        required_capabilities=(
            "strategy_definition_contracts",
            "concrete_strategy_rule_evaluation",
            "owner_approved_starter_strategy_library",
            "strategy_input_output_metadata",
        ),
        implemented_capabilities=(
            "strategy_definition_contracts",
            "concrete_strategy_rule_evaluation",
            "owner_approved_starter_strategy_library",
            "strategy_input_output_metadata",
        ),
        reason=(
            "StrategyLab now exposes deterministic offline starter strategy execution over "
            "caller-provided rows, with stable starter definitions, parameter identities, "
            "and dated replay-ready signal rows."
        ),
        evidence=(
            "quant/strategies/rules.py adds stable starter strategy ids, versions, parameter-set identity, row validation, and deterministic rule evaluation for moving-average crossover and RSI mean-reversion baselines.",
            "quant/strategies/README.md now documents the local/offline starter strategy library scope and the continued ban on warehouse, network, portfolio, and live-trading behavior.",
            "tests/strategies/test_rules.py covers library exports, deterministic evaluation, parameter override validation, empty/missing input handling, and duplicate-date rejection offline.",
        ),
    ),
    _CapabilityGroupBlueprint(
        group_id="parameter_metadata_validation_and_repeatable_experiments",
        label="Parameter Metadata, Validation, Versioning, and Repeatable Experiments",
        required_capabilities=(
            "parameter_metadata_validation",
            "strategy_schema_versioning",
            "repeatable_experiment_configuration",
            "parameter_set_versioning",
        ),
        implemented_capabilities=(
            "parameter_metadata_validation",
            "repeatable_experiment_configuration",
            "parameter_set_versioning",
            "strategy_schema_versioning",
        ),
        reason=(
            "Phase 5 now includes a first-class repeatable experiment configuration that "
            "binds strategy reference, validated parameter values, selection metadata, "
            "date window, and cost/slippage assumptions under a deterministic digest."
        ),
        evidence=(
            "quant/strategies/contracts.py still validates ParameterDefinition bounds, choices, and schema_version for StrategyDefinition records.",
            "quant/backtest/experiments.py adds RepeatableExperimentConfig, normalized serialization, parameter-set/version validation, deterministic experiment_id generation, and BacktestRequest conversion without external reads.",
            "tests/backtest/test_experiments.py covers deterministic normalization, reproducible experiment ids, parameter validation failures, and invalid date/capital/cost input rejection offline.",
        ),
    ),
    _CapabilityGroupBlueprint(
        group_id="deterministic_historical_replay_over_local_inputs",
        label="Deterministic Historical Replay Over Local Inputs",
        required_capabilities=(
            "caller_provided_local_market_data",
            "validated_trade_intents",
            "deterministic_replay_execution",
            "portfolio_snapshots",
            "replay_summary_output",
        ),
        implemented_capabilities=(
            "caller_provided_local_market_data",
            "validated_trade_intents",
            "deterministic_replay_execution",
            "portfolio_snapshots",
            "replay_summary_output",
        ),
        reason=(
            "BacktestEngine already supports deterministic historical replay over "
            "caller-provided market bars and trade intents with portfolio snapshots "
            "and summary output, all without hidden IO."
        ),
        evidence=(
            "quant/backtest/replay.py replays validated local MarketBar and TradeIntent inputs without persistence, DataHub reads, or network access.",
            "TASK-070 accepted the side-coercion rework so validated 'buy'/'sell' TradeIntent.side values execute with the same semantics as TradeSide enums.",
            "tests/backtest/test_replay.py covers cash/equity tracking, rejected intents, invalid replay-window inputs, and supported string-side execution offline.",
        ),
    ),
    _CapabilityGroupBlueprint(
        group_id="replay_assumptions_costs_fills_and_market_calendar",
        label="Cost, Slippage, Fill, Cash, Position, and Calendar Assumptions",
        required_capabilities=(
            "transaction_cost_assumptions",
            "slippage_assumptions",
            "cash_accounting",
            "position_accounting",
            "basic_fill_rules",
            "market_calendar_assumptions",
            "corporate_action_assumptions",
        ),
        implemented_capabilities=(
            "transaction_cost_assumptions",
            "slippage_assumptions",
            "cash_accounting",
            "position_accounting",
            "basic_fill_rules",
            "market_calendar_assumptions",
            "corporate_action_assumptions",
        ),
        reason=(
            "Replay now records explicit assumption metadata for caller-owned market-calendar, "
            "missing-bar, unusable-bar, fill, cash-carry, and corporate-action semantics while "
            "staying fully local over caller-provided bars."
        ),
        evidence=(
            "quant/backtest/contracts.py defines ReplayAssumptions on ReplayConfig so adjusted/unadjusted/as-provided price semantics, caller-owned corporate-action handling, and calendar/fill policies are explicit in config and result outputs.",
            "quant/backtest/replay.py now iterates every calendar day in the requested window, rejects intents on missing or unusable bars deterministically, and carries cash/positions forward without inferring upstream calendars or adjustments.",
            "tests/backtest/test_replay.py covers missing-bar dates, zero-volume unusable bars, same-day close fill behavior, and caller-declared corporate-action price assumptions offline.",
        ),
    ),
    _CapabilityGroupBlueprint(
        group_id="result_metrics_drawdown_risk_and_report_outputs",
        label="Result Summaries, Metrics, Drawdown/Risk, and Report Outputs",
        required_capabilities=(
            "performance_metrics",
            "drawdown_metrics",
            "risk_metrics",
            "report_ready_outputs",
            "artifact_report_linkage",
        ),
        implemented_capabilities=(
            "performance_metrics",
            "drawdown_metrics",
            "risk_metrics",
            "report_ready_outputs",
            "artifact_report_linkage",
        ),
        reason=(
            "Replay now emits broader deterministic metrics and a serialization-friendly report payload "
            "covering assumptions, coverage, end-state facts, rejection breakdown, and artifact-reference validation."
        ),
        evidence=(
            "quant/backtest/contracts.py extends ReplaySummary with turnover, exposure, win/loss, end-state, and coverage metrics, and adds ReplayReport with optional artifact_reference validation.",
            "quant/backtest/replay.py builds deterministic ReplayCoverage, ReplayEndState, and rejection breakdown sections so later comparison workflows can consume a stable normalized payload.",
            "tests/backtest/test_replay.py and tests/backtest/test_contracts.py assert report serialization shape, deterministic metrics, and invalid artifact/reference handling offline.",
        ),
    ),
    _CapabilityGroupBlueprint(
        group_id="multi_configuration_comparison_workflows",
        label="Multi-Configuration Comparison Workflows",
        required_capabilities=(
            "multiple_strategy_configuration_execution",
            "normalized_comparison_outputs",
            "deterministic_comparison_ordering",
        ),
        implemented_capabilities=(
            "multiple_strategy_configuration_execution",
            "normalized_comparison_outputs",
            "deterministic_comparison_ordering",
        ),
        reason=(
            "Phase 5 now includes a first-class deterministic comparison workflow over "
            "repeatable experiment configs plus replay reports/results, with stable ranking, "
            "stable digests, and serialization-friendly multi-configuration output."
        ),
        evidence=(
            "quant/backtest/comparison.py adds MultiConfigurationComparison, controlled validation issues, deterministic digests, and stable ranking/tie-break rules over local experiment/report inputs only.",
            "The comparison workflow reuses existing RepeatableExperimentConfig and ReplayReport contracts instead of introducing warehouse, DataHub, or live-source dependencies.",
            "tests/backtest/test_comparison.py covers deterministic identity, input-order stability, tie-breaking, invalid duplicate/mismatched comparisons, and assumption propagation offline.",
        ),
    ),
    _CapabilityGroupBlueprint(
        group_id="offline_regression_boundaries_and_reproducibility",
        label="Offline Regression Coverage, Boundaries, and Reproducibility",
        required_capabilities=(
            "invalid_config_regressions",
            "date_boundary_regressions",
            "missing_bar_regressions",
            "corporate_action_assumption_regressions",
            "reproducibility_regressions",
        ),
        implemented_capabilities=(
            "invalid_config_regressions",
            "date_boundary_regressions",
            "missing_bar_regressions",
            "corporate_action_assumption_regressions",
            "reproducibility_regressions",
        ),
        reason=(
            "The default Phase 5 tests now cover deterministic comparison reruns, input-order stability, "
            "tie-breaking, stale experiment ids, mismatched windows/capital, missing or non-finite report metrics, "
            "and caller-declared corporate-action/source assumption propagation."
        ),
        evidence=(
            "tests/strategies/test_contracts.py covers invalid strategy definitions and parameter validation offline.",
            "tests/backtest/test_contracts.py covers invalid replay inputs, bad date order, and supported string trade-side validation.",
            "tests/backtest/test_replay.py covers missing bars, zero-volume bars, deterministic side coercion regressions, and caller-declared corporate-action adjustment assumptions offline.",
            "tests/backtest/test_comparison.py adds reproducibility reruns, input-order stability, stale-id boundary failures, missing/non-finite metric validation, and normalized comparison payload assertions offline.",
        ),
    ),
)


_FOLLOW_UP_BLUEPRINTS: tuple[_FollowUpBlueprint, ...] = ()


_BATCHES: tuple[_BatchBlueprint, ...] = ()


__all__ = [
    "FollowUpDisposition",
    "ReadinessStatus",
    "ReadinessStatusCount",
    "StrategyBacktestCapabilityGroupReadiness",
    "StrategyBacktestFollowUpBatch",
    "StrategyBacktestFollowUpItem",
    "StrategyBacktestPersonalReadinessGate",
    "build_strategy_backtest_personal_readiness_gate",
    "summarize_readiness_status_counts",
]
