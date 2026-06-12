"""Local/offline deterministic risk-rule primitives for Phase 6."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from math import floor, isfinite

from .contracts import (
    CashExposureSnapshot,
    HoldingSnapshot,
    SignalDecisionStatus,
    SignalIntent,
    SignalLifecycleState,
    SignalRecord,
    SignalSourceLink,
    SignalSourceType,
    transition_signal_state,
)

_SUPPORTED_MARKETS = frozenset({"CN", "HK", "ETF_CN", "FUND_CN"})


class RiskRuleType(str, Enum):
    EXPOSURE = "exposure"
    CONCENTRATION = "concentration"
    LIQUIDITY = "liquidity"
    DRAWDOWN = "drawdown"
    POSITION_SIZING = "position_sizing"
    BLACKLIST = "blacklist"
    SUSPENSION = "suspension"
    MARKET_CONSTRAINT = "market_constraint"


class RiskRuleOutcomeStatus(str, Enum):
    PASS = "pass"
    WARN = "warn"
    BLOCK = "block"


@dataclass(frozen=True)
class ExposureRiskRule:
    rule_id: str
    max_gross_exposure: float
    max_net_exposure_abs: float
    warn_gross_exposure: float | None = None
    warn_net_exposure_abs: float | None = None

    def __post_init__(self) -> None:
        _require_non_empty(self.rule_id, "rule_id")
        _ensure_ratio(self.max_gross_exposure, "max_gross_exposure")
        _ensure_ratio(self.max_net_exposure_abs, "max_net_exposure_abs")
        if self.warn_gross_exposure is not None:
            _ensure_ratio(self.warn_gross_exposure, "warn_gross_exposure")
            if self.warn_gross_exposure > self.max_gross_exposure:
                raise ValueError("warn_gross_exposure cannot exceed max_gross_exposure")
        if self.warn_net_exposure_abs is not None:
            _ensure_ratio(self.warn_net_exposure_abs, "warn_net_exposure_abs")
            if self.warn_net_exposure_abs > self.max_net_exposure_abs:
                raise ValueError("warn_net_exposure_abs cannot exceed max_net_exposure_abs")


@dataclass(frozen=True)
class ConcentrationRiskRule:
    rule_id: str
    max_position_weight: float
    warn_position_weight: float | None = None

    def __post_init__(self) -> None:
        _require_non_empty(self.rule_id, "rule_id")
        _ensure_ratio(self.max_position_weight, "max_position_weight")
        if self.warn_position_weight is not None:
            _ensure_ratio(self.warn_position_weight, "warn_position_weight")
            if self.warn_position_weight > self.max_position_weight:
                raise ValueError("warn_position_weight cannot exceed max_position_weight")


@dataclass(frozen=True)
class LiquidityRiskRule:
    rule_id: str
    min_average_daily_value: float
    max_participation_rate: float
    warn_min_average_daily_value: float | None = None
    warn_max_participation_rate: float | None = None

    def __post_init__(self) -> None:
        _require_non_empty(self.rule_id, "rule_id")
        _ensure_positive_number(self.min_average_daily_value, "min_average_daily_value")
        _ensure_ratio(self.max_participation_rate, "max_participation_rate")
        if self.warn_min_average_daily_value is not None:
            _ensure_positive_number(
                self.warn_min_average_daily_value,
                "warn_min_average_daily_value",
            )
            if self.warn_min_average_daily_value < self.min_average_daily_value:
                raise ValueError(
                    "warn_min_average_daily_value cannot be below min_average_daily_value"
                )
        if self.warn_max_participation_rate is not None:
            _ensure_ratio(self.warn_max_participation_rate, "warn_max_participation_rate")
            if self.warn_max_participation_rate > self.max_participation_rate:
                raise ValueError(
                    "warn_max_participation_rate cannot exceed max_participation_rate"
                )


@dataclass(frozen=True)
class DrawdownRiskRule:
    rule_id: str
    max_drawdown: float
    warn_drawdown: float | None = None

    def __post_init__(self) -> None:
        _require_non_empty(self.rule_id, "rule_id")
        _ensure_ratio(self.max_drawdown, "max_drawdown")
        if self.warn_drawdown is not None:
            _ensure_ratio(self.warn_drawdown, "warn_drawdown")
            if self.warn_drawdown > self.max_drawdown:
                raise ValueError("warn_drawdown cannot exceed max_drawdown")


@dataclass(frozen=True)
class PositionSizingRule:
    rule_id: str
    min_target_weight: float
    default_target_weight: float
    max_target_weight: float
    increment_weight: float

    def __post_init__(self) -> None:
        _require_non_empty(self.rule_id, "rule_id")
        _ensure_ratio(self.min_target_weight, "min_target_weight")
        _ensure_ratio(self.default_target_weight, "default_target_weight")
        _ensure_ratio(self.max_target_weight, "max_target_weight")
        _ensure_ratio(self.increment_weight, "increment_weight")
        if self.min_target_weight > self.default_target_weight:
            raise ValueError("min_target_weight cannot exceed default_target_weight")
        if self.default_target_weight > self.max_target_weight:
            raise ValueError("default_target_weight cannot exceed max_target_weight")


@dataclass(frozen=True)
class BlockedInstrument:
    symbol: str
    market: str
    reason: str

    def __post_init__(self) -> None:
        _require_non_empty(self.symbol, "symbol")
        _validate_market(self.market, "market")
        _require_non_empty(self.reason, "reason")

    @property
    def symbol_key(self) -> tuple[str, str]:
        return (self.symbol, self.market)


@dataclass(frozen=True)
class BlacklistRiskRule:
    rule_id: str
    blocked_instruments: tuple[BlockedInstrument, ...]

    def __post_init__(self) -> None:
        _require_non_empty(self.rule_id, "rule_id")
        _ensure_unique(
            (instrument.symbol_key for instrument in self.blocked_instruments),
            "blacklist instruments",
        )


@dataclass(frozen=True)
class SuspensionRiskRule:
    rule_id: str
    block_suspended: bool = True
    warn_suspended: bool = False

    def __post_init__(self) -> None:
        _require_non_empty(self.rule_id, "rule_id")
        if not self.block_suspended and not self.warn_suspended:
            raise ValueError("suspension rule must either block or warn suspended symbols")


@dataclass(frozen=True)
class MarketLotConstraint:
    market: str
    lot_size: int
    allow_fractional: bool = False

    def __post_init__(self) -> None:
        _validate_market(self.market, "market")
        if self.lot_size <= 0:
            raise ValueError("lot_size must be > 0")


@dataclass(frozen=True)
class MarketConstraintRiskRule:
    rule_id: str
    allowed_markets: tuple[str, ...]
    lot_constraints: tuple[MarketLotConstraint, ...] = ()

    def __post_init__(self) -> None:
        _require_non_empty(self.rule_id, "rule_id")
        if not self.allowed_markets:
            raise ValueError("allowed_markets are required")
        for market in self.allowed_markets:
            _validate_market(market, "allowed_markets")
        _ensure_unique(self.allowed_markets, "allowed markets")
        _ensure_unique(
            (constraint.market for constraint in self.lot_constraints),
            "market lot constraints",
        )


@dataclass(frozen=True)
class SignalMarketContext:
    symbol: str
    market: str
    as_of_date: str
    latest_price: float
    average_daily_value: float
    current_drawdown: float | None = None
    is_suspended: bool = False

    def __post_init__(self) -> None:
        _require_non_empty(self.symbol, "symbol")
        _validate_market(self.market, "market")
        _parse_date(self.as_of_date, "as_of_date")
        _ensure_positive_number(self.latest_price, "latest_price")
        _ensure_positive_number(self.average_daily_value, "average_daily_value")
        if self.current_drawdown is not None:
            _ensure_ratio(self.current_drawdown, "current_drawdown")

    @property
    def symbol_key(self) -> tuple[str, str]:
        return (self.symbol, self.market)


@dataclass(frozen=True)
class RiskRuleSet:
    rule_set_id: str
    portfolio_id: str
    exposure_rules: tuple[ExposureRiskRule, ...] = ()
    concentration_rules: tuple[ConcentrationRiskRule, ...] = ()
    liquidity_rules: tuple[LiquidityRiskRule, ...] = ()
    drawdown_rules: tuple[DrawdownRiskRule, ...] = ()
    position_sizing_rules: tuple[PositionSizingRule, ...] = ()
    blacklist_rules: tuple[BlacklistRiskRule, ...] = ()
    suspension_rules: tuple[SuspensionRiskRule, ...] = ()
    market_constraint_rules: tuple[MarketConstraintRiskRule, ...] = ()

    def __post_init__(self) -> None:
        _require_non_empty(self.rule_set_id, "rule_set_id")
        _require_non_empty(self.portfolio_id, "portfolio_id")
        _ensure_unique(self.rule_ids, "risk rule ids")

    @property
    def rule_ids(self) -> tuple[str, ...]:
        return tuple(
            rule.rule_id
            for rule in (
                *self.exposure_rules,
                *self.concentration_rules,
                *self.liquidity_rules,
                *self.drawdown_rules,
                *self.position_sizing_rules,
                *self.blacklist_rules,
                *self.suspension_rules,
                *self.market_constraint_rules,
            )
        )


@dataclass(frozen=True)
class PositionSizingGuidance:
    rule_id: str
    target_weight: float
    estimated_order_value: float
    estimated_order_shares: int
    capped_by_cash: bool
    capped_by_rule_limit: bool
    explanation: str


@dataclass(frozen=True)
class RiskRuleOutcome:
    rule_id: str
    rule_type: RiskRuleType
    status: RiskRuleOutcomeStatus
    reason_code: str
    reason_summary: str


@dataclass(frozen=True)
class SignalRiskEvaluationResult:
    signal: SignalRecord
    overall_status: SignalDecisionStatus
    sizing_guidance: PositionSizingGuidance | None
    rule_outcomes: tuple[RiskRuleOutcome, ...]


def evaluate_signal_risk(
    *,
    signal: SignalRecord,
    rule_set: RiskRuleSet,
    market_context: SignalMarketContext,
    evaluated_at: str,
    holding_snapshot: HoldingSnapshot | None = None,
    cash_exposure_snapshot: CashExposureSnapshot | None = None,
) -> SignalRiskEvaluationResult:
    evaluated_timestamp = _parse_datetime(evaluated_at, "evaluated_at")
    if evaluated_timestamp < _parse_datetime(signal.updated_at, "signal.updated_at"):
        raise ValueError("evaluated_at cannot be before signal.updated_at")
    if market_context.symbol_key != (signal.symbol, signal.market):
        raise ValueError("market_context symbol/market must match signal")
    if _parse_date(market_context.as_of_date, "market_context.as_of_date") < _parse_date(
        signal.effective_date,
        "signal.effective_date",
    ):
        raise ValueError("market_context.as_of_date cannot be before signal.effective_date")
    if holding_snapshot is not None and holding_snapshot.portfolio_id != rule_set.portfolio_id:
        raise ValueError("holding_snapshot portfolio_id must match rule_set portfolio_id")
    if cash_exposure_snapshot is not None and cash_exposure_snapshot.portfolio_id != rule_set.portfolio_id:
        raise ValueError("cash_exposure_snapshot portfolio_id must match rule_set portfolio_id")

    current_weight = _current_position_weight(signal, holding_snapshot)
    sizing_guidance = _build_sizing_guidance(
        signal=signal,
        rule_set=rule_set,
        current_weight=current_weight,
        market_context=market_context,
        cash_exposure_snapshot=cash_exposure_snapshot,
    )
    actionable_without_sizing_guidance = _requires_projected_sizing(signal) and sizing_guidance is None
    target_weight = (
        None
        if actionable_without_sizing_guidance
        else (
            sizing_guidance.target_weight
            if sizing_guidance is not None
            else current_weight
        )
    )
    projected_gross = None
    projected_net = None
    if cash_exposure_snapshot is not None and target_weight is not None:
        projected_gross = max(
            0.0,
            cash_exposure_snapshot.gross_exposure - current_weight + target_weight,
        )
        projected_net = cash_exposure_snapshot.net_exposure - current_weight + target_weight

    outcomes: list[RiskRuleOutcome] = []
    for rule in rule_set.exposure_rules:
        if cash_exposure_snapshot is None:
            raise ValueError("cash_exposure_snapshot is required for exposure rules")
        if projected_gross is None or projected_net is None:
            status = RiskRuleOutcomeStatus.BLOCK
            reason_code = "exposure_missing_sizing_guidance"
            reason_summary = (
                f"projected exposure unavailable without sizing guidance for "
                f"actionable {signal.intent.value} signal"
            )
        else:
            gross_status = _threshold_status(
                value=projected_gross,
                warn_threshold=rule.warn_gross_exposure,
                block_threshold=rule.max_gross_exposure,
            )
            net_status = _threshold_status(
                value=abs(projected_net),
                warn_threshold=rule.warn_net_exposure_abs,
                block_threshold=rule.max_net_exposure_abs,
            )
            status = _max_status(gross_status, net_status)
            reason_code = f"exposure_{status.value}"
            reason_summary = (
                f"projected gross={projected_gross:.4f}, net_abs={abs(projected_net):.4f}"
            )
        outcomes.append(
            RiskRuleOutcome(
                rule_id=rule.rule_id,
                rule_type=RiskRuleType.EXPOSURE,
                status=status,
                reason_code=reason_code,
                reason_summary=reason_summary,
            )
        )
    for rule in rule_set.concentration_rules:
        if target_weight is None:
            status = RiskRuleOutcomeStatus.BLOCK
            reason_code = "concentration_missing_sizing_guidance"
            reason_summary = (
                f"projected position weight unavailable without sizing guidance for "
                f"actionable {signal.intent.value} signal"
            )
        else:
            status = _threshold_status(
                value=target_weight,
                warn_threshold=rule.warn_position_weight,
                block_threshold=rule.max_position_weight,
            )
            reason_code = f"concentration_{status.value}"
            reason_summary = f"projected position weight={target_weight:.4f}"
        outcomes.append(
            RiskRuleOutcome(
                rule_id=rule.rule_id,
                rule_type=RiskRuleType.CONCENTRATION,
                status=status,
                reason_code=reason_code,
                reason_summary=reason_summary,
            )
        )
    for rule in rule_set.liquidity_rules:
        if cash_exposure_snapshot is None or sizing_guidance is None:
            raise ValueError("cash_exposure_snapshot is required for liquidity rules")
        participation_rate = (
            sizing_guidance.estimated_order_value / market_context.average_daily_value
            if market_context.average_daily_value
            else 0.0
        )
        status = _max_status(
            _inverse_threshold_status(
                value=market_context.average_daily_value,
                warn_threshold=rule.warn_min_average_daily_value,
                block_threshold=rule.min_average_daily_value,
            ),
            _threshold_status(
                value=participation_rate,
                warn_threshold=rule.warn_max_participation_rate,
                block_threshold=rule.max_participation_rate,
            ),
        )
        outcomes.append(
            RiskRuleOutcome(
                rule_id=rule.rule_id,
                rule_type=RiskRuleType.LIQUIDITY,
                status=status,
                reason_code=f"liquidity_{status.value}",
                reason_summary=(
                    "average_daily_value="
                    f"{market_context.average_daily_value:.2f}, participation={participation_rate:.4f}"
                ),
            )
        )
    for rule in rule_set.drawdown_rules:
        if market_context.current_drawdown is None:
            raise ValueError("current_drawdown is required for drawdown rules")
        status = _threshold_status(
            value=market_context.current_drawdown,
            warn_threshold=rule.warn_drawdown,
            block_threshold=rule.max_drawdown,
        )
        outcomes.append(
            RiskRuleOutcome(
                rule_id=rule.rule_id,
                rule_type=RiskRuleType.DRAWDOWN,
                status=status,
                reason_code=f"drawdown_{status.value}",
                reason_summary=f"current_drawdown={market_context.current_drawdown:.4f}",
            )
        )
    for rule in rule_set.position_sizing_rules:
        if sizing_guidance is None:
            raise ValueError("position sizing guidance is required for position sizing rules")
        status = (
            RiskRuleOutcomeStatus.WARN
            if sizing_guidance.capped_by_cash or sizing_guidance.capped_by_rule_limit
            else RiskRuleOutcomeStatus.PASS
        )
        outcomes.append(
            RiskRuleOutcome(
                rule_id=rule.rule_id,
                rule_type=RiskRuleType.POSITION_SIZING,
                status=status,
                reason_code=f"position_sizing_{status.value}",
                reason_summary=sizing_guidance.explanation,
            )
        )
    for rule in rule_set.blacklist_rules:
        blocked = next(
            (
                instrument
                for instrument in rule.blocked_instruments
                if instrument.symbol_key == market_context.symbol_key
            ),
            None,
        )
        status = RiskRuleOutcomeStatus.BLOCK if blocked is not None else RiskRuleOutcomeStatus.PASS
        reason_summary = blocked.reason if blocked is not None else "symbol is not blacklisted"
        outcomes.append(
            RiskRuleOutcome(
                rule_id=rule.rule_id,
                rule_type=RiskRuleType.BLACKLIST,
                status=status,
                reason_code=f"blacklist_{status.value}",
                reason_summary=reason_summary,
            )
        )
    for rule in rule_set.suspension_rules:
        if market_context.is_suspended and rule.block_suspended:
            status = RiskRuleOutcomeStatus.BLOCK
        elif market_context.is_suspended and rule.warn_suspended:
            status = RiskRuleOutcomeStatus.WARN
        else:
            status = RiskRuleOutcomeStatus.PASS
        outcomes.append(
            RiskRuleOutcome(
                rule_id=rule.rule_id,
                rule_type=RiskRuleType.SUSPENSION,
                status=status,
                reason_code=f"suspension_{status.value}",
                reason_summary=(
                    "symbol is suspended" if market_context.is_suspended else "symbol is tradable"
                ),
            )
        )
    for rule in rule_set.market_constraint_rules:
        if signal.market not in rule.allowed_markets:
            status = RiskRuleOutcomeStatus.BLOCK
            summary = f"market {signal.market} is not allowed by rule"
            reason_code = f"market_constraint_{status.value}"
        else:
            lot_constraint = next(
                (constraint for constraint in rule.lot_constraints if constraint.market == signal.market),
                None,
            )
            if (
                lot_constraint is not None
                and not lot_constraint.allow_fractional
                and actionable_without_sizing_guidance
            ):
                status = RiskRuleOutcomeStatus.BLOCK
                summary = (
                    f"lot-size evaluation unavailable without sizing guidance for "
                    f"actionable {signal.intent.value} signal"
                )
                reason_code = "market_constraint_missing_sizing_guidance"
            elif (
                lot_constraint is not None
                and not lot_constraint.allow_fractional
                and sizing_guidance is not None
                and sizing_guidance.estimated_order_shares % lot_constraint.lot_size != 0
            ):
                status = RiskRuleOutcomeStatus.BLOCK
                summary = (
                    f"estimated shares {sizing_guidance.estimated_order_shares} "
                    f"do not satisfy lot size {lot_constraint.lot_size}"
                )
                reason_code = f"market_constraint_{status.value}"
            else:
                status = RiskRuleOutcomeStatus.PASS
                summary = "market constraints satisfied"
                reason_code = f"market_constraint_{status.value}"
        outcomes.append(
            RiskRuleOutcome(
                rule_id=rule.rule_id,
                rule_type=RiskRuleType.MARKET_CONSTRAINT,
                status=status,
                reason_code=reason_code,
                reason_summary=summary,
            )
        )

    overall_status = _resolve_overall_status(outcomes)
    audit_reason_code, audit_reason_summary = _build_audit_reason(outcomes)
    updated_signal = transition_signal_state(
        signal=signal,
        target_state=SignalLifecycleState.UPDATED,
        transitioned_at=evaluated_at,
        reason_code=audit_reason_code,
        reason_summary=audit_reason_summary,
        source_links=_build_risk_source_links(
            rule_set=rule_set,
            market_context=market_context,
            holding_snapshot=holding_snapshot,
            cash_exposure_snapshot=cash_exposure_snapshot,
            evaluated_at=evaluated_at,
        ),
        decision_status=overall_status,
    )
    return SignalRiskEvaluationResult(
        signal=updated_signal,
        overall_status=overall_status,
        sizing_guidance=sizing_guidance,
        rule_outcomes=tuple(outcomes),
    )


def _build_sizing_guidance(
    *,
    signal: SignalRecord,
    rule_set: RiskRuleSet,
    current_weight: float,
    market_context: SignalMarketContext,
    cash_exposure_snapshot: CashExposureSnapshot | None,
) -> PositionSizingGuidance | None:
    if not rule_set.position_sizing_rules:
        return None
    if cash_exposure_snapshot is None:
        raise ValueError("cash_exposure_snapshot is required for position sizing rules")
    rule = rule_set.position_sizing_rules[0]
    if signal.intent is SignalIntent.ENTER:
        target_weight = rule.default_target_weight
    elif signal.intent is SignalIntent.INCREASE:
        target_weight = min(rule.max_target_weight, current_weight + rule.increment_weight)
    elif signal.intent is SignalIntent.REDUCE:
        target_weight = max(0.0, current_weight - rule.increment_weight)
    elif signal.intent is SignalIntent.EXIT:
        target_weight = 0.0
    else:
        raise ValueError(f"unsupported signal intent: {signal.intent.value}")

    capped_by_rule_limit = False
    if target_weight > rule.max_target_weight:
        target_weight = rule.max_target_weight
        capped_by_rule_limit = True
    if target_weight and target_weight < rule.min_target_weight:
        target_weight = rule.min_target_weight
        capped_by_rule_limit = True

    available_weight = cash_exposure_snapshot.available_cash / cash_exposure_snapshot.total_equity
    if signal.intent in (SignalIntent.ENTER, SignalIntent.INCREASE):
        cash_cap = current_weight + available_weight
        capped_by_cash = target_weight > cash_cap
        if capped_by_cash:
            target_weight = max(current_weight, cash_cap)
    else:
        capped_by_cash = False

    order_weight = abs(target_weight - current_weight)
    estimated_order_value = order_weight * cash_exposure_snapshot.total_equity
    estimated_order_shares = int(floor(estimated_order_value / market_context.latest_price))
    explanation = (
        f"current_weight={current_weight:.4f}; target_weight={target_weight:.4f}; "
        f"order_value={estimated_order_value:.2f}; shares={estimated_order_shares}"
    )
    return PositionSizingGuidance(
        rule_id=rule.rule_id,
        target_weight=target_weight,
        estimated_order_value=estimated_order_value,
        estimated_order_shares=estimated_order_shares,
        capped_by_cash=capped_by_cash,
        capped_by_rule_limit=capped_by_rule_limit,
        explanation=explanation,
    )


def _current_position_weight(
    signal: SignalRecord,
    holding_snapshot: HoldingSnapshot | None,
) -> float:
    if holding_snapshot is None:
        return 0.0
    for holding in holding_snapshot.holdings:
        if holding.symbol_key == (signal.symbol, signal.market):
            return holding.portfolio_weight or 0.0
    return 0.0


def _requires_projected_sizing(signal: SignalRecord) -> bool:
    return signal.intent in (SignalIntent.ENTER, SignalIntent.INCREASE)


def _build_risk_source_links(
    *,
    rule_set: RiskRuleSet,
    market_context: SignalMarketContext,
    holding_snapshot: HoldingSnapshot | None,
    cash_exposure_snapshot: CashExposureSnapshot | None,
    evaluated_at: str,
) -> tuple[SignalSourceLink, ...]:
    links = [
        SignalSourceLink(
            link_id=f"risk-rule-set:{rule_set.rule_set_id}",
            source_type=SignalSourceType.RISK_RULE_SET,
            reference_id=rule_set.rule_set_id,
            recorded_at=evaluated_at,
            summary="local deterministic risk rule set applied to signal",
        ),
        SignalSourceLink(
            link_id=f"market-context:{market_context.market}:{market_context.symbol}:{market_context.as_of_date}",
            source_type=SignalSourceType.MARKET_CONTEXT_SNAPSHOT,
            reference_id=f"{market_context.market}:{market_context.symbol}:{market_context.as_of_date}",
            recorded_at=f"{market_context.as_of_date}T00:00:00",
            summary="caller-provided market context for liquidity, drawdown, and suspension checks",
        ),
    ]
    if holding_snapshot is not None:
        links.append(
            SignalSourceLink(
                link_id=f"holding:{holding_snapshot.snapshot_id}",
                source_type=SignalSourceType.PORTFOLIO_HOLDING_SNAPSHOT,
                reference_id=holding_snapshot.snapshot_id,
                recorded_at=f"{holding_snapshot.as_of_date}T00:00:00",
                summary="holding snapshot used for current weight checks",
            )
        )
    if cash_exposure_snapshot is not None:
        links.append(
            SignalSourceLink(
                link_id=f"cash:{cash_exposure_snapshot.snapshot_id}",
                source_type=SignalSourceType.PORTFOLIO_CASH_EXPOSURE_SNAPSHOT,
                reference_id=cash_exposure_snapshot.snapshot_id,
                recorded_at=f"{cash_exposure_snapshot.as_of_date}T00:00:00",
                summary="cash and exposure snapshot used for sizing and exposure checks",
            )
        )
    return tuple(sorted(links, key=lambda link: (link.source_type.value, link.reference_id, link.link_id)))


def _threshold_status(
    *,
    value: float,
    warn_threshold: float | None,
    block_threshold: float,
) -> RiskRuleOutcomeStatus:
    if value > block_threshold:
        return RiskRuleOutcomeStatus.BLOCK
    if warn_threshold is not None and value > warn_threshold:
        return RiskRuleOutcomeStatus.WARN
    return RiskRuleOutcomeStatus.PASS


def _inverse_threshold_status(
    *,
    value: float,
    warn_threshold: float | None,
    block_threshold: float,
) -> RiskRuleOutcomeStatus:
    if value < block_threshold:
        return RiskRuleOutcomeStatus.BLOCK
    if warn_threshold is not None and value < warn_threshold:
        return RiskRuleOutcomeStatus.WARN
    return RiskRuleOutcomeStatus.PASS


def _max_status(
    left: RiskRuleOutcomeStatus,
    right: RiskRuleOutcomeStatus,
) -> RiskRuleOutcomeStatus:
    order = {
        RiskRuleOutcomeStatus.PASS: 0,
        RiskRuleOutcomeStatus.WARN: 1,
        RiskRuleOutcomeStatus.BLOCK: 2,
    }
    return left if order[left] >= order[right] else right


def _resolve_overall_status(outcomes: list[RiskRuleOutcome]) -> SignalDecisionStatus:
    if any(outcome.status is RiskRuleOutcomeStatus.BLOCK for outcome in outcomes):
        return SignalDecisionStatus.BLOCKED
    if any(outcome.status is RiskRuleOutcomeStatus.WARN for outcome in outcomes):
        return SignalDecisionStatus.WARNED
    return SignalDecisionStatus.PASSED


def _build_audit_reason(outcomes: list[RiskRuleOutcome]) -> tuple[str, str]:
    primary_block = next(
        (outcome for outcome in outcomes if outcome.status is RiskRuleOutcomeStatus.BLOCK),
        None,
    )
    if primary_block is not None:
        return (
            primary_block.reason_code,
            f"primary_block={primary_block.rule_id}; {_summarize_outcomes(outcomes)}",
        )

    primary_warn = next(
        (outcome for outcome in outcomes if outcome.status is RiskRuleOutcomeStatus.WARN),
        None,
    )
    if primary_warn is not None:
        return (
            primary_warn.reason_code,
            f"primary_warn={primary_warn.rule_id}; {_summarize_outcomes(outcomes)}",
        )

    return ("risk_evaluation_passed", _summarize_outcomes(outcomes))


def _summarize_outcomes(outcomes: list[RiskRuleOutcome]) -> str:
    blocked = sum(outcome.status is RiskRuleOutcomeStatus.BLOCK for outcome in outcomes)
    warned = sum(outcome.status is RiskRuleOutcomeStatus.WARN for outcome in outcomes)
    passed = sum(outcome.status is RiskRuleOutcomeStatus.PASS for outcome in outcomes)
    return f"risk outcomes: pass={passed}, warn={warned}, block={blocked}"


def _require_non_empty(value: str, field_name: str) -> None:
    if not value:
        raise ValueError(f"{field_name} is required")


def _parse_date(value: str, field_name: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a valid ISO date") from exc


def _parse_datetime(value: str, field_name: str) -> datetime:
    try:
        return datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a valid ISO datetime") from exc


def _ensure_finite_number(value: float, field_name: str) -> None:
    if not isfinite(value):
        raise ValueError(f"{field_name} must be finite")


def _ensure_positive_number(value: float, field_name: str) -> None:
    _ensure_finite_number(value, field_name)
    if value <= 0:
        raise ValueError(f"{field_name} must be > 0")


def _ensure_ratio(value: float, field_name: str) -> None:
    _ensure_finite_number(value, field_name)
    if not 0 <= value <= 1:
        raise ValueError(f"{field_name} must be between 0 and 1")


def _ensure_unique(values, label: str) -> None:
    seen: set[object] = set()
    for value in values:
        if value in seen:
            raise ValueError(f"duplicate {label} are not allowed")
        seen.add(value)


def _validate_market(value: str, field_name: str) -> None:
    if value not in _SUPPORTED_MARKETS:
        raise ValueError(f"{field_name} must be one of {sorted(_SUPPORTED_MARKETS)!r}")
