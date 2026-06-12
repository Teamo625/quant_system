"""Local/offline portfolio and signal contracts for Phase 6."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from math import isfinite
from typing import Iterable


class SignalLifecycleState(str, Enum):
    CREATED = "created"
    UPDATED = "updated"
    EXPIRED = "expired"
    CLOSED = "closed"


class SignalDecisionStatus(str, Enum):
    PASSED = "passed"
    WARNED = "warned"
    BLOCKED = "blocked"
    EXPIRED = "expired"
    CLOSED = "closed"


class SignalIntent(str, Enum):
    ENTER = "enter"
    EXIT = "exit"
    REDUCE = "reduce"
    INCREASE = "increase"
    HOLD = "hold"


class SignalConflictStatus(str, Enum):
    NONE = "none"
    CONFLICTING = "conflicting"
    SUPERSEDED = "superseded"


class SignalSourceType(str, Enum):
    SCANNER_CANDIDATE = "scanner_candidate"
    STRATEGY_DEFINITION = "strategy_definition"
    BACKTEST_REPORT = "backtest_report"
    PORTFOLIO_HOLDING_SNAPSHOT = "portfolio_holding_snapshot"
    PORTFOLIO_CASH_EXPOSURE_SNAPSHOT = "portfolio_cash_exposure_snapshot"
    WATCHLIST_SNAPSHOT = "watchlist_snapshot"
    MARKET_CONTEXT_SNAPSHOT = "market_context_snapshot"
    RISK_RULE_SET = "risk_rule_set"


@dataclass(frozen=True)
class WatchlistItem:
    item_id: str
    watchlist_id: str
    symbol: str
    market: str
    added_on: str
    rank: int = 0
    note: str | None = None
    tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _require_non_empty(self.item_id, "item_id")
        _require_non_empty(self.watchlist_id, "watchlist_id")
        _require_non_empty(self.symbol, "symbol")
        _require_non_empty(self.market, "market")
        _parse_date(self.added_on, "added_on")
        if self.rank < 0:
            raise ValueError("rank must be >= 0")
        _ensure_normalized_tags(self.tags)

    @property
    def symbol_key(self) -> tuple[str, str]:
        return (self.symbol, self.market)


@dataclass(frozen=True)
class WatchlistSnapshot:
    snapshot_id: str
    watchlist_id: str
    as_of_date: str
    items: tuple[WatchlistItem, ...]

    def __post_init__(self) -> None:
        _require_non_empty(self.snapshot_id, "snapshot_id")
        _require_non_empty(self.watchlist_id, "watchlist_id")
        as_of = _parse_date(self.as_of_date, "as_of_date")
        _ensure_unique((item.item_id for item in self.items), "watchlist item ids")
        _ensure_unique((item.symbol_key for item in self.items), "watchlist symbols")

        for item in self.items:
            if item.watchlist_id != self.watchlist_id:
                raise ValueError("watchlist item watchlist_id must match snapshot watchlist_id")
            if _parse_date(item.added_on, "added_on") > as_of:
                raise ValueError("watchlist item added_on cannot be after snapshot as_of_date")


@dataclass(frozen=True)
class HoldingState:
    holding_id: str
    portfolio_id: str
    symbol: str
    market: str
    quantity: float
    average_cost: float | None = None
    cost_basis: float | None = None
    portfolio_weight: float | None = None
    updated_at: str = ""

    def __post_init__(self) -> None:
        _require_non_empty(self.holding_id, "holding_id")
        _require_non_empty(self.portfolio_id, "portfolio_id")
        _require_non_empty(self.symbol, "symbol")
        _require_non_empty(self.market, "market")
        _parse_datetime(self.updated_at, "updated_at")

        if self.quantity <= 0:
            raise ValueError("quantity must be > 0")
        if self.average_cost is None and self.cost_basis is None:
            raise ValueError("average_cost or cost_basis is required")
        if self.average_cost is not None and self.average_cost < 0:
            raise ValueError("average_cost must be >= 0")
        if self.cost_basis is not None and self.cost_basis < 0:
            raise ValueError("cost_basis must be >= 0")
        if self.portfolio_weight is not None and not 0 <= self.portfolio_weight <= 1:
            raise ValueError("portfolio_weight must be between 0 and 1")
        if self.average_cost is not None and self.cost_basis is not None:
            implied_cost_basis = self.average_cost * self.quantity
            if abs(implied_cost_basis - self.cost_basis) > 1e-9:
                raise ValueError("cost_basis must equal average_cost * quantity when both are provided")

    @property
    def symbol_key(self) -> tuple[str, str]:
        return (self.symbol, self.market)


@dataclass(frozen=True)
class HoldingSnapshot:
    snapshot_id: str
    portfolio_id: str
    as_of_date: str
    holdings: tuple[HoldingState, ...]

    def __post_init__(self) -> None:
        _require_non_empty(self.snapshot_id, "snapshot_id")
        _require_non_empty(self.portfolio_id, "portfolio_id")
        as_of = _parse_date(self.as_of_date, "as_of_date")
        _ensure_unique((holding.holding_id for holding in self.holdings), "holding ids")
        _ensure_unique((holding.symbol_key for holding in self.holdings), "holding symbols")

        for holding in self.holdings:
            if holding.portfolio_id != self.portfolio_id:
                raise ValueError("holding portfolio_id must match snapshot portfolio_id")
            if _parse_datetime(holding.updated_at, "updated_at").date() > as_of:
                raise ValueError("holding updated_at cannot be after snapshot as_of_date")


@dataclass(frozen=True)
class CashExposureSnapshot:
    snapshot_id: str
    portfolio_id: str
    as_of_date: str
    total_equity: float
    available_cash: float
    reserved_cash: float
    gross_exposure: float
    net_exposure: float

    def __post_init__(self) -> None:
        _require_non_empty(self.snapshot_id, "snapshot_id")
        _require_non_empty(self.portfolio_id, "portfolio_id")
        _parse_date(self.as_of_date, "as_of_date")
        if self.total_equity <= 0:
            raise ValueError("total_equity must be > 0")
        if self.available_cash < 0:
            raise ValueError("available_cash must be >= 0")
        if self.reserved_cash < 0:
            raise ValueError("reserved_cash must be >= 0")
        if self.gross_exposure < 0:
            raise ValueError("gross_exposure must be >= 0")
        if abs(self.net_exposure) > self.gross_exposure:
            raise ValueError("absolute net_exposure cannot exceed gross_exposure")
        if self.available_cash + self.reserved_cash > self.total_equity:
            raise ValueError("cash cannot exceed total_equity")


@dataclass(frozen=True)
class SignalSourceLink:
    link_id: str
    source_type: SignalSourceType
    reference_id: str
    recorded_at: str
    summary: str
    source_version: str | None = None

    def __post_init__(self) -> None:
        _require_non_empty(self.link_id, "link_id")
        _require_non_empty(self.reference_id, "reference_id")
        _require_non_empty(self.summary, "summary")
        _parse_datetime(self.recorded_at, "recorded_at")
        if self.source_version is not None:
            _require_non_empty(self.source_version, "source_version")


@dataclass(frozen=True)
class DecisionAuditRecord:
    audit_id: str
    signal_id: str
    lifecycle_state: SignalLifecycleState
    decision_status: SignalDecisionStatus
    recorded_at: str
    reason_code: str
    reason_summary: str
    source_links: tuple[SignalSourceLink, ...]
    closure_reason: str | None = None
    expiry_reason: str | None = None

    def __post_init__(self) -> None:
        _require_non_empty(self.audit_id, "audit_id")
        _require_non_empty(self.signal_id, "signal_id")
        _require_non_empty(self.reason_code, "reason_code")
        _require_non_empty(self.reason_summary, "reason_summary")
        _parse_datetime(self.recorded_at, "recorded_at")
        _ensure_unique((link.link_id for link in self.source_links), "audit source link ids")
        _validate_lifecycle_reason_requirements(
            lifecycle_state=self.lifecycle_state,
            closure_reason=self.closure_reason,
            expiry_reason=self.expiry_reason,
        )

        if self.decision_status is SignalDecisionStatus.EXPIRED:
            if self.lifecycle_state is not SignalLifecycleState.EXPIRED:
                raise ValueError("expired audit decisions require expired lifecycle_state")
        elif self.decision_status is SignalDecisionStatus.CLOSED:
            if self.lifecycle_state is not SignalLifecycleState.CLOSED:
                raise ValueError("closed audit decisions require closed lifecycle_state")
        elif self.decision_status in (
            SignalDecisionStatus.PASSED,
            SignalDecisionStatus.WARNED,
            SignalDecisionStatus.BLOCKED,
        ) and self.lifecycle_state not in (
            SignalLifecycleState.CREATED,
            SignalLifecycleState.UPDATED,
        ):
            raise ValueError(
                "passed, warned, and blocked audit decisions require created or updated lifecycle_state"
            )


@dataclass(frozen=True)
class SignalRecord:
    signal_id: str
    symbol: str
    market: str
    intent: SignalIntent
    lifecycle_state: SignalLifecycleState
    created_at: str
    updated_at: str
    effective_date: str
    version: int
    source_links: tuple[SignalSourceLink, ...]
    decision_audit: tuple[DecisionAuditRecord, ...]
    expires_on: str | None = None
    expired_at: str | None = None
    expired_reason: str | None = None
    closed_at: str | None = None
    closed_reason: str | None = None
    conflict_status: SignalConflictStatus = SignalConflictStatus.NONE
    superseded_by_signal_id: str | None = None
    priority_rank: int | None = None
    signal_score: float | None = None

    def __post_init__(self) -> None:
        _require_non_empty(self.signal_id, "signal_id")
        _require_non_empty(self.symbol, "symbol")
        _require_non_empty(self.market, "market")
        created_at = _parse_datetime(self.created_at, "created_at")
        updated_at = _parse_datetime(self.updated_at, "updated_at")
        effective_date = _parse_date(self.effective_date, "effective_date")

        if updated_at < created_at:
            raise ValueError("updated_at cannot be before created_at")
        if self.version < 1:
            raise ValueError("version must be >= 1")
        if self.priority_rank is not None and self.priority_rank < 0:
            raise ValueError("priority_rank must be >= 0")
        if self.signal_score is not None:
            _ensure_finite_number(self.signal_score, "signal_score")

        if self.expires_on is not None:
            if _parse_date(self.expires_on, "expires_on") < effective_date:
                raise ValueError("expires_on cannot be before effective_date")

        _ensure_unique((link.link_id for link in self.source_links), "signal source link ids")
        _ensure_unique((record.audit_id for record in self.decision_audit), "signal audit ids")
        _validate_lifecycle_reason_requirements(
            lifecycle_state=self.lifecycle_state,
            closure_reason=self.closed_reason,
            expiry_reason=self.expired_reason,
        )

        if self.lifecycle_state is SignalLifecycleState.EXPIRED:
            if self.expired_at is None:
                raise ValueError("expired signals require expired_at")
            if _parse_datetime(self.expired_at, "expired_at") < created_at:
                raise ValueError("expired_at cannot be before created_at")
        elif self.expired_at is not None:
            raise ValueError("expired_at is allowed only for expired signals")

        if self.lifecycle_state is SignalLifecycleState.CLOSED:
            if self.closed_at is None:
                raise ValueError("closed signals require closed_at")
            if _parse_datetime(self.closed_at, "closed_at") < created_at:
                raise ValueError("closed_at cannot be before created_at")
        elif self.closed_at is not None:
            raise ValueError("closed_at is allowed only for closed signals")

        for record in self.decision_audit:
            if record.signal_id != self.signal_id:
                raise ValueError("decision_audit signal_id must match signal_id")
            if _parse_datetime(record.recorded_at, "recorded_at") < created_at:
                raise ValueError("decision audit cannot predate signal creation")

        if self.superseded_by_signal_id is not None:
            _require_non_empty(self.superseded_by_signal_id, "superseded_by_signal_id")
            if self.conflict_status is SignalConflictStatus.NONE:
                raise ValueError("superseded_by_signal_id requires a non-none conflict_status")


def build_watchlist_snapshot(
    snapshot_id: str,
    watchlist_id: str,
    as_of_date: str,
    items: Iterable[WatchlistItem],
) -> WatchlistSnapshot:
    return WatchlistSnapshot(
        snapshot_id=snapshot_id,
        watchlist_id=watchlist_id,
        as_of_date=as_of_date,
        items=tuple(sorted(items, key=_watchlist_item_sort_key)),
    )


def merge_watchlist_snapshot(
    current: WatchlistSnapshot,
    updates: Iterable[WatchlistItem],
    snapshot_id: str,
    as_of_date: str,
) -> WatchlistSnapshot:
    update_items = tuple(updates)
    _ensure_unique((item.symbol_key for item in update_items), "watchlist update symbols")
    merged: dict[tuple[str, str], WatchlistItem] = {
        item.symbol_key: item for item in current.items
    }
    for item in update_items:
        merged[item.symbol_key] = item
    return build_watchlist_snapshot(
        snapshot_id=snapshot_id,
        watchlist_id=current.watchlist_id,
        as_of_date=as_of_date,
        items=merged.values(),
    )


def build_holding_snapshot(
    snapshot_id: str,
    portfolio_id: str,
    as_of_date: str,
    holdings: Iterable[HoldingState],
) -> HoldingSnapshot:
    return HoldingSnapshot(
        snapshot_id=snapshot_id,
        portfolio_id=portfolio_id,
        as_of_date=as_of_date,
        holdings=tuple(sorted(holdings, key=_holding_state_sort_key)),
    )


def merge_holding_snapshot(
    current: HoldingSnapshot,
    updates: Iterable[HoldingState],
    snapshot_id: str,
    as_of_date: str,
) -> HoldingSnapshot:
    update_holdings = tuple(updates)
    _ensure_unique((holding.symbol_key for holding in update_holdings), "holding update symbols")
    merged: dict[tuple[str, str], HoldingState] = {
        holding.symbol_key: holding for holding in current.holdings
    }
    for holding in update_holdings:
        merged[holding.symbol_key] = holding
    return build_holding_snapshot(
        snapshot_id=snapshot_id,
        portfolio_id=current.portfolio_id,
        as_of_date=as_of_date,
        holdings=merged.values(),
    )


def create_decision_audit_record(
    audit_id: str,
    signal_id: str,
    lifecycle_state: SignalLifecycleState,
    decision_status: SignalDecisionStatus,
    recorded_at: str,
    reason_code: str,
    reason_summary: str,
    source_links: Iterable[SignalSourceLink],
    closure_reason: str | None = None,
    expiry_reason: str | None = None,
) -> DecisionAuditRecord:
    return DecisionAuditRecord(
        audit_id=audit_id,
        signal_id=signal_id,
        lifecycle_state=lifecycle_state,
        decision_status=decision_status,
        recorded_at=recorded_at,
        reason_code=reason_code,
        reason_summary=reason_summary,
        source_links=tuple(sorted(source_links, key=_signal_source_link_sort_key)),
        closure_reason=closure_reason,
        expiry_reason=expiry_reason,
    )


def create_signal_record(
    signal_id: str,
    symbol: str,
    market: str,
    intent: SignalIntent,
    created_at: str,
    effective_date: str,
    source_links: Iterable[SignalSourceLink],
    reason_code: str,
    reason_summary: str,
    expires_on: str | None = None,
    conflict_status: SignalConflictStatus = SignalConflictStatus.NONE,
    superseded_by_signal_id: str | None = None,
    initial_decision_status: SignalDecisionStatus = SignalDecisionStatus.PASSED,
    priority_rank: int | None = None,
    signal_score: float | None = None,
) -> SignalRecord:
    if initial_decision_status not in (
        SignalDecisionStatus.PASSED,
        SignalDecisionStatus.WARNED,
        SignalDecisionStatus.BLOCKED,
    ):
        raise ValueError("initial_decision_status must be passed, warned, or blocked")
    normalized_links = tuple(sorted(source_links, key=_signal_source_link_sort_key))
    initial_audit = create_decision_audit_record(
        audit_id=f"{signal_id}:audit:1",
        signal_id=signal_id,
        lifecycle_state=SignalLifecycleState.CREATED,
        decision_status=initial_decision_status,
        recorded_at=created_at,
        reason_code=reason_code,
        reason_summary=reason_summary,
        source_links=normalized_links,
    )
    return SignalRecord(
        signal_id=signal_id,
        symbol=symbol,
        market=market,
        intent=intent,
        lifecycle_state=SignalLifecycleState.CREATED,
        created_at=created_at,
        updated_at=created_at,
        effective_date=effective_date,
        version=1,
        source_links=normalized_links,
        decision_audit=(initial_audit,),
        expires_on=expires_on,
        conflict_status=conflict_status,
        superseded_by_signal_id=superseded_by_signal_id,
        priority_rank=priority_rank,
        signal_score=signal_score,
    )


def transition_signal_state(
    signal: SignalRecord,
    target_state: SignalLifecycleState,
    transitioned_at: str,
    reason_code: str,
    reason_summary: str,
    source_links: Iterable[SignalSourceLink] = (),
    decision_status: SignalDecisionStatus | None = None,
    closure_reason: str | None = None,
    expiry_reason: str | None = None,
) -> SignalRecord:
    allowed_transitions = {
        SignalLifecycleState.CREATED: {
            SignalLifecycleState.UPDATED,
            SignalLifecycleState.EXPIRED,
            SignalLifecycleState.CLOSED,
        },
        SignalLifecycleState.UPDATED: {
            SignalLifecycleState.UPDATED,
            SignalLifecycleState.EXPIRED,
            SignalLifecycleState.CLOSED,
        },
        SignalLifecycleState.EXPIRED: set(),
        SignalLifecycleState.CLOSED: set(),
    }
    if target_state not in allowed_transitions[signal.lifecycle_state]:
        raise ValueError(
            f"unsupported signal transition: {signal.lifecycle_state.value} -> {target_state.value}"
        )

    transitioned_timestamp = _parse_datetime(transitioned_at, "transitioned_at")
    if transitioned_timestamp < _parse_datetime(signal.updated_at, "signal.updated_at"):
        raise ValueError("transitioned_at cannot be before current signal updated_at")

    merged_links = _merge_source_links(signal.source_links, source_links)
    resolved_decision_status = decision_status or _default_decision_status_for_state(target_state)
    next_version = signal.version + 1
    next_audit = create_decision_audit_record(
        audit_id=f"{signal.signal_id}:audit:{next_version}",
        signal_id=signal.signal_id,
        lifecycle_state=target_state,
        decision_status=resolved_decision_status,
        recorded_at=transitioned_at,
        reason_code=reason_code,
        reason_summary=reason_summary,
        source_links=merged_links,
        closure_reason=closure_reason,
        expiry_reason=expiry_reason,
    )

    kwargs = {
        "signal_id": signal.signal_id,
        "symbol": signal.symbol,
        "market": signal.market,
        "intent": signal.intent,
        "lifecycle_state": target_state,
        "created_at": signal.created_at,
        "updated_at": transitioned_at,
        "effective_date": signal.effective_date,
        "version": next_version,
        "source_links": merged_links,
        "decision_audit": (*signal.decision_audit, next_audit),
        "expires_on": signal.expires_on,
        "conflict_status": signal.conflict_status,
        "superseded_by_signal_id": signal.superseded_by_signal_id,
        "priority_rank": signal.priority_rank,
        "signal_score": signal.signal_score,
    }
    if target_state is SignalLifecycleState.EXPIRED:
        kwargs["expired_at"] = transitioned_at
        kwargs["expired_reason"] = expiry_reason
        kwargs["closed_at"] = None
        kwargs["closed_reason"] = None
    elif target_state is SignalLifecycleState.CLOSED:
        kwargs["closed_at"] = transitioned_at
        kwargs["closed_reason"] = closure_reason
        kwargs["expired_at"] = None
        kwargs["expired_reason"] = None
    else:
        kwargs["expired_at"] = None
        kwargs["expired_reason"] = None
        kwargs["closed_at"] = None
        kwargs["closed_reason"] = None

    return SignalRecord(**kwargs)


def _default_decision_status_for_state(
    target_state: SignalLifecycleState,
) -> SignalDecisionStatus:
    if target_state is SignalLifecycleState.EXPIRED:
        return SignalDecisionStatus.EXPIRED
    if target_state is SignalLifecycleState.CLOSED:
        return SignalDecisionStatus.CLOSED
    return SignalDecisionStatus.PASSED


def _merge_source_links(
    current: tuple[SignalSourceLink, ...],
    updates: Iterable[SignalSourceLink],
) -> tuple[SignalSourceLink, ...]:
    merged: dict[str, SignalSourceLink] = {link.link_id: link for link in current}
    for link in updates:
        merged[link.link_id] = link
    return tuple(sorted(merged.values(), key=_signal_source_link_sort_key))


def _watchlist_item_sort_key(item: WatchlistItem) -> tuple[int, str, str, str]:
    return (item.rank, item.symbol, item.market, item.item_id)


def _holding_state_sort_key(holding: HoldingState) -> tuple[str, str, str]:
    return (holding.symbol, holding.market, holding.holding_id)


def _signal_source_link_sort_key(
    link: SignalSourceLink,
) -> tuple[str, str, str]:
    return (link.source_type.value, link.reference_id, link.link_id)


def _validate_lifecycle_reason_requirements(
    lifecycle_state: SignalLifecycleState,
    closure_reason: str | None,
    expiry_reason: str | None,
) -> None:
    if lifecycle_state is SignalLifecycleState.EXPIRED:
        if not expiry_reason:
            raise ValueError("expired lifecycle_state requires expiry_reason")
        if closure_reason is not None:
            raise ValueError("expired lifecycle_state cannot include closure_reason")
        return
    if lifecycle_state is SignalLifecycleState.CLOSED:
        if not closure_reason:
            raise ValueError("closed lifecycle_state requires closure_reason")
        if expiry_reason is not None:
            raise ValueError("closed lifecycle_state cannot include expiry_reason")
        return
    if closure_reason is not None:
        raise ValueError("closure_reason is allowed only for closed lifecycle_state")
    if expiry_reason is not None:
        raise ValueError("expiry_reason is allowed only for expired lifecycle_state")


def _ensure_unique(values: Iterable[object], label: str) -> None:
    seen: set[object] = set()
    for value in values:
        if value in seen:
            raise ValueError(f"duplicate {label} are not allowed")
        seen.add(value)


def _ensure_normalized_tags(tags: tuple[str, ...]) -> None:
    _ensure_unique(tags, "watchlist tags")
    for tag in tags:
        _require_non_empty(tag, "tag")


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
