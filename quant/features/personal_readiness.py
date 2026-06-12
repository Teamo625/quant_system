"""Deterministic FeatureHub personal-readiness gate for Phase 3-P audits."""

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
    FEATUREHUB_HARDENING = "featurehub_hardening"
    CONTRACT_REPAIR = "contract_repair"
    OWNER_BLOCKER = "owner_blocker"
    BLOCKED_UPSTREAM = "blocked_upstream"


@dataclass(frozen=True)
class ReadinessStatusCount:
    status: ReadinessStatus
    count: int


@dataclass(frozen=True)
class FeatureCapabilityGroupReadiness:
    group_id: str
    label: str
    status: ReadinessStatus
    reason: str
    required_capabilities: tuple[str, ...]
    implemented_capabilities: tuple[str, ...]
    missing_capabilities: tuple[str, ...]
    evidence: tuple[str, ...]


@dataclass(frozen=True)
class FeatureFollowUpItem:
    follow_up_id: str
    capability_group_id: str
    status: ReadinessStatus
    disposition: FollowUpDisposition
    reason: str
    recommended_next_handoff_theme: str


@dataclass(frozen=True)
class FeatureFollowUpBatch:
    batch_id: str
    theme: str
    disposition: FollowUpDisposition
    item_ids: tuple[str, ...]
    rationale: str


@dataclass(frozen=True)
class FeaturePersonalReadinessGate:
    phase_id: str
    phase_closure_ready: bool
    capability_groups: tuple[FeatureCapabilityGroupReadiness, ...]
    status_counts: tuple[ReadinessStatusCount, ...]
    follow_up_queue: tuple[FeatureFollowUpItem, ...]
    follow_up_batches: tuple[FeatureFollowUpBatch, ...]
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


def build_featurehub_personal_readiness_gate() -> FeaturePersonalReadinessGate:
    """Return the deterministic Phase 3-P readiness audit snapshot."""
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

    return FeaturePersonalReadinessGate(
        phase_id="Phase 3-P FeatureHub Personal Trading Perfection Re-Review",
        phase_closure_ready=all(
            group.status is ReadinessStatus.PASS for group in capability_groups
        ),
        capability_groups=capability_groups,
        status_counts=status_counts,
        follow_up_queue=follow_up_queue,
        follow_up_batches=follow_up_batches,
        recommended_next_handoff_batch_id="featurehub_batch_contracts_batch_01",
        recommended_next_handoff_theme=(
            "Introduce FeatureHub batch calculation contracts, downstream-safe "
            "metric identity, and aligned offline regression coverage for the "
            "remaining batch and consumability gaps."
        ),
    )


def summarize_readiness_status_counts(
    capability_groups: tuple[FeatureCapabilityGroupReadiness, ...],
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
) -> FeatureCapabilityGroupReadiness:
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

    return FeatureCapabilityGroupReadiness(
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
    capability_groups: tuple[FeatureCapabilityGroupReadiness, ...],
) -> FeatureFollowUpItem:
    group_by_id = {group.group_id: group for group in capability_groups}
    group = group_by_id[blueprint.capability_group_id]
    if blueprint.blocked:
        status = ReadinessStatus.BLOCKED
    elif group.status is ReadinessStatus.FAIL:
        status = ReadinessStatus.FAIL
    else:
        status = ReadinessStatus.WARN

    return FeatureFollowUpItem(
        follow_up_id=blueprint.follow_up_id,
        capability_group_id=blueprint.capability_group_id,
        status=status,
        disposition=blueprint.disposition,
        reason=blueprint.reason,
        recommended_next_handoff_theme=blueprint.recommended_next_handoff_theme,
    )


def _build_follow_up_batch(blueprint: _BatchBlueprint) -> FeatureFollowUpBatch:
    return FeatureFollowUpBatch(
        batch_id=blueprint.batch_id,
        theme=blueprint.theme,
        disposition=blueprint.disposition,
        item_ids=blueprint.item_ids,
        rationale=blueprint.rationale,
    )


def _validate_follow_up_batches(
    follow_up_queue: tuple[FeatureFollowUpItem, ...],
    follow_up_batches: tuple[FeatureFollowUpBatch, ...],
) -> None:
    queue_ids = {item.follow_up_id for item in follow_up_queue}
    batch_item_ids: set[str] = set()

    for batch in follow_up_batches:
        if len(batch.item_ids) == 1 and batch.disposition is FollowUpDisposition.FEATUREHUB_HARDENING:
            raise ValueError(
                "ordinary feature hardening batches must group at least two follow-up items"
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
        group_id="price_volume_technical_core",
        label="Price/Volume Technical Indicator Core",
        required_capabilities=(
            "returns",
            "moving_averages",
            "ema",
            "macd",
            "rsi",
            "kdj_or_stochastic",
            "bollinger_bands",
            "atr",
            "volatility",
            "volume_turnover_liquidity",
            "gap_breakout_primitives",
            "rolling_window_helpers",
        ),
        implemented_capabilities=(
            "returns",
            "moving_averages",
            "ema",
            "macd",
            "rsi",
            "kdj_or_stochastic",
            "bollinger_bands",
            "atr",
            "volatility",
            "volume_turnover_liquidity",
            "gap_breakout_primitives",
            "rolling_window_helpers",
        ),
        reason=(
            "The current FeatureHub technical core now covers the required practical "
            "price/volume indicator families for this batch, including rolling "
            "window helpers, EMA/MACD/RSI/KDJ-family momentum, Bollinger/ATR "
            "volatility-range indicators, volume-turnover-liquidity features, and "
            "gap/breakout primitives."
        ),
        evidence=(
            "TASK-060 accepted the original return/SMA/realized-volatility slice.",
            "TASK-139 expands quant/features/technical.py with EMA, MACD, RSI, stochastic/KDJ, Bollinger Bands, ATR, volume-turnover-liquidity, and gap/breakout primitives.",
            "tests/features/test_technical.py now covers legacy compatibility plus normal-path, edge-case, invalid-input, and contract-validation regression coverage for the expanded technical batch.",
        ),
    ),
    _CapabilityGroupBlueprint(
        group_id="valuation_features",
        label="Valuation Features",
        required_capabilities=(
            "pe_pb_ps_style_values",
            "earnings_yield",
            "book_to_price",
            "valuation_percentiles",
            "relative_valuation_history",
        ),
        implemented_capabilities=(
            "pe_pb_ps_style_values",
            "earnings_yield",
            "book_to_price",
            "valuation_percentiles",
            "relative_valuation_history",
            "float_market_cap_ratio",
        ),
        reason=(
            "The valuation slice now covers raw PE/PB/PS-style outputs alongside "
            "earnings-yield, book-to-price, and bounded history-aware percentile "
            "or relative valuation helpers over caller-provided rows."
        ),
        evidence=(
            "TASK-061 accepted the original valuation slice.",
            "TASK-140 expands quant/features/valuation.py with raw latest PE/PB/PS outputs plus bounded valuation percentile and relative-history helpers.",
            "tests/features/test_valuation.py now covers raw ratio outputs, bounded valuation windows, missing metric inputs, duplicate dates, and invalid-window or invalid-metric regressions.",
        ),
    ),
    _CapabilityGroupBlueprint(
        group_id="capital_flow_money_flow_features",
        label="Capital-Flow and Money-Flow Features",
        required_capabilities=(
            "main_flow_levels",
            "northbound_levels",
            "fund_flow_levels",
            "rolling_changes",
            "intensity_normalization",
            "missing_source_behavior",
        ),
        implemented_capabilities=(
            "main_flow_levels",
            "northbound_levels",
            "fund_flow_levels",
            "rolling_changes",
            "intensity_normalization",
            "missing_source_behavior",
        ),
        reason=(
            "The flow slice now covers main-flow, northbound, and fund-flow level "
            "features plus deterministic rolling changes and bounded normalization "
            "helpers over caller-provided capital-flow and fund-flow rows."
        ),
        evidence=(
            "TASK-062 accepted the original capital-flow slice.",
            "TASK-140 expands quant/features/capital_flow.py with main-flow and northbound change helpers, trailing turnover-adjusted intensity, and local fund-flow normalization plus feature calculations.",
            "tests/features/test_capital_flow.py now covers rolling changes, bounded adjusted-flow windows, fund-flow normalization, missing-source behavior, invalid numbers, and duplicate-date regressions.",
        ),
    ),
    _CapabilityGroupBlueprint(
        group_id="sector_market_relative_features",
        label="Sector-Relative and Market-Relative Features",
        required_capabilities=(
            "stock_vs_sector_returns",
            "sector_strength",
            "index_relative_performance",
            "breadth_primitives",
            "rotation_primitives",
        ),
        implemented_capabilities=(
            "stock_vs_sector_returns",
            "sector_strength",
            "index_relative_performance",
            "breadth_primitives",
            "rotation_primitives",
        ),
        reason=(
            "The relative-feature slice now covers aligned stock-vs-sector and "
            "index-relative performance plus breadth, sector-strength, and "
            "rotation primitives over caller-provided offline rows."
        ),
        evidence=(
            "TASK-141 adds quant/features/relative.py with deterministic normalization, aligned-window validation, stock-vs-sector spreads, sector strength, index-relative performance, breadth ratios, and sector rotation helpers.",
            "tests/features/test_relative.py now covers aligned-date success paths, mixed-entity and mixed-market failures, duplicate identifiers, insufficient history, and deterministic rotation ordering.",
            "The implementation stays local-only and introduces no DataHub fetches, warehouse reads, or hidden live behavior.",
        ),
    ),
    _CapabilityGroupBlueprint(
        group_id="batch_calculation_apis",
        label="Batch Calculation APIs",
        required_capabilities=(
            "multi_symbol_batch_inputs",
            "consistent_batch_outputs",
            "multi_feature_batch_execution",
        ),
        implemented_capabilities=(),
        reason=(
            "Current FeatureHub primitives are single-series helpers only. There is "
            "no batch API that accepts caller-provided multi-symbol data and returns "
            "consistent multi-feature outputs."
        ),
        evidence=(
            "quant/features/technical.py, valuation.py, and capital_flow.py each normalize one symbol/market series at a time.",
            "quant/features/__init__.py exports no batch orchestration entrypoint.",
            "tests/features/ has no batch calculation coverage.",
        ),
    ),
    _CapabilityGroupBlueprint(
        group_id="persistence_and_downstream_consumability",
        label="Persistence, Versioning, and Downstream Consumability",
        required_capabilities=(
            "feature_output_persistence",
            "versioned_manifest",
            "metric_identity_contract",
            "scanner_consumability",
            "strategylab_consumability",
        ),
        implemented_capabilities=(
            "feature_output_persistence",
            "versioned_manifest",
        ),
        reason=(
            "Local JSONL persistence and manifest versioning are present, but the "
            "current record contract still lacks metric-level identity inside shared "
            "feature families, which limits robust downstream Scanner and StrategyLab "
            "consumption."
        ),
        evidence=(
            "TASK-063 accepted deterministic JSONL plus manifest persistence/versioning.",
            "TASK-060/TASK-061/TASK-062 reports all note missing metric-level identity as a follow-up consideration.",
            "quant/features/storage.py persists records deterministically but does not solve multi-metric family identity.",
        ),
    ),
    _CapabilityGroupBlueprint(
        group_id="offline_test_coverage",
        label="Offline Test Coverage",
        required_capabilities=(
            "success_cases",
            "missing_data_cases",
            "window_boundary_cases",
            "invalid_input_cases",
            "duplicate_date_cases",
            "schema_compatibility_cases",
            "readiness_gate_regression",
            "full_phase_capability_coverage",
        ),
        implemented_capabilities=(
            "success_cases",
            "missing_data_cases",
            "window_boundary_cases",
            "invalid_input_cases",
            "duplicate_date_cases",
            "schema_compatibility_cases",
            "readiness_gate_regression",
        ),
        reason=(
            "The offline suite now covers technical, valuation, flow, and relative "
            "feature slices well, but phase-level coverage remains incomplete because "
            "the batch API and downstream contract gaps still have no dedicated "
            "regression coverage."
        ),
        evidence=(
            "TASK-040 through TASK-063 all closed with offline-safe FeatureHub tests only.",
            "tests/features/test_contracts.py, test_technical.py, test_valuation.py, test_capital_flow.py, test_relative.py, and test_storage.py cover the implemented slices, including TASK-141 relative-feature expansions.",
            "TASK-138 plus later FeatureHub batch closures keep the readiness gate under deterministic offline regression without introducing live behavior.",
        ),
    ),
)


_FOLLOW_UP_BLUEPRINTS: tuple[_FollowUpBlueprint, ...] = (
    _FollowUpBlueprint(
        follow_up_id="FH-BATCH-001",
        capability_group_id="batch_calculation_apis",
        disposition=FollowUpDisposition.CONTRACT_REPAIR,
        reason="Introduce a stable batch calculation API that accepts caller-provided multi-symbol inputs and returns deterministic multi-feature outputs.",
        recommended_next_handoff_theme="FeatureHub batch API contract",
    ),
    _FollowUpBlueprint(
        follow_up_id="FH-CONTRACT-001",
        capability_group_id="persistence_and_downstream_consumability",
        disposition=FollowUpDisposition.CONTRACT_REPAIR,
        reason="Add metric-level identity or equivalent downstream-safe semantics so multiple records within one feature family remain distinguishable.",
        recommended_next_handoff_theme="FeatureHub downstream consumability contract",
    ),
    _FollowUpBlueprint(
        follow_up_id="FH-TEST-001",
        capability_group_id="offline_test_coverage",
        disposition=FollowUpDisposition.FEATUREHUB_HARDENING,
        reason="Expand offline regression coverage alongside each new feature family, batch path, and downstream contract change.",
        recommended_next_handoff_theme="FeatureHub test expansion aligned to new capability batches",
    ),
)


_BATCHES: tuple[_BatchBlueprint, ...] = (
    _BatchBlueprint(
        batch_id="featurehub_batch_contracts_batch_01",
        theme="Batch API, downstream contract, and aligned tests",
        disposition=FollowUpDisposition.CONTRACT_REPAIR,
        item_ids=(
            "FH-BATCH-001",
            "FH-CONTRACT-001",
            "FH-TEST-001",
        ),
        rationale=(
            "Batch orchestration, metric identity, and expanded regression coverage "
            "share the same contract surface and should be designed together."
        ),
    ),
)
