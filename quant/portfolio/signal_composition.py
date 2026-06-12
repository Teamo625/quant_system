"""Local/offline structured signal composition primitives for Phase 6."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from math import isfinite
from typing import Iterable

from .contracts import (
    CashExposureSnapshot,
    HoldingSnapshot,
    SignalDecisionStatus,
    SignalIntent,
    SignalRecord,
    SignalSourceLink,
    SignalSourceType,
    WatchlistSnapshot,
    create_signal_record,
)


@dataclass(frozen=True)
class ScannerCandidateInput:
    candidate_id: str
    symbol: str
    market: str
    as_of_date: str
    ranked_at: str
    summary: str
    rank: int | None = None
    score: float | None = None
    source_version: str | None = None

    def __post_init__(self) -> None:
        _require_non_empty(self.candidate_id, "candidate_id")
        _require_non_empty(self.symbol, "symbol")
        _require_non_empty(self.market, "market")
        _require_non_empty(self.summary, "summary")
        _parse_date(self.as_of_date, "as_of_date")
        _parse_datetime(self.ranked_at, "ranked_at")
        if self.rank is not None and self.rank < 0:
            raise ValueError("rank must be >= 0")
        if self.score is not None:
            _ensure_finite_number(self.score, "score")
        if self.source_version is not None:
            _require_non_empty(self.source_version, "source_version")

    @property
    def symbol_key(self) -> tuple[str, str]:
        return (self.symbol, self.market)


@dataclass(frozen=True)
class StrategySignalInput:
    strategy_signal_id: str
    strategy_id: str
    symbol: str
    market: str
    intent: SignalIntent
    as_of_date: str
    generated_at: str
    rationale: str
    conviction_score: float | None = None
    source_version: str | None = None

    def __post_init__(self) -> None:
        _require_non_empty(self.strategy_signal_id, "strategy_signal_id")
        _require_non_empty(self.strategy_id, "strategy_id")
        _require_non_empty(self.symbol, "symbol")
        _require_non_empty(self.market, "market")
        _require_non_empty(self.rationale, "rationale")
        _parse_date(self.as_of_date, "as_of_date")
        _parse_datetime(self.generated_at, "generated_at")
        if self.intent is SignalIntent.HOLD:
            raise ValueError("unsupported intent for structured signal composition: hold")
        if self.conviction_score is not None:
            _ensure_finite_number(self.conviction_score, "conviction_score")
        if self.source_version is not None:
            _require_non_empty(self.source_version, "source_version")

    @property
    def symbol_key(self) -> tuple[str, str]:
        return (self.symbol, self.market)


@dataclass(frozen=True)
class BacktestSupportInput:
    report_id: str
    strategy_id: str
    symbol: str
    market: str
    as_of_date: str
    generated_at: str
    summary: str
    max_drawdown: float | None = None
    win_rate: float | None = None
    support_score: float | None = None
    source_version: str | None = None

    def __post_init__(self) -> None:
        _require_non_empty(self.report_id, "report_id")
        _require_non_empty(self.strategy_id, "strategy_id")
        _require_non_empty(self.symbol, "symbol")
        _require_non_empty(self.market, "market")
        _require_non_empty(self.summary, "summary")
        _parse_date(self.as_of_date, "as_of_date")
        _parse_datetime(self.generated_at, "generated_at")
        if self.max_drawdown is not None:
            _ensure_ratio(self.max_drawdown, "max_drawdown")
        if self.win_rate is not None:
            _ensure_ratio(self.win_rate, "win_rate")
        if self.support_score is not None:
            _ensure_finite_number(self.support_score, "support_score")
        if self.source_version is not None:
            _require_non_empty(self.source_version, "source_version")

    @property
    def symbol_key(self) -> tuple[str, str]:
        return (self.symbol, self.market)


@dataclass(frozen=True)
class StructuredSignalCompositionRequest:
    composition_id: str
    portfolio_id: str
    effective_date: str
    composed_at: str
    scanner_candidates: tuple[ScannerCandidateInput, ...]
    strategy_signals: tuple[StrategySignalInput, ...]
    backtest_support: tuple[BacktestSupportInput, ...] = ()
    watchlist_snapshot: WatchlistSnapshot | None = None
    holding_snapshot: HoldingSnapshot | None = None
    cash_exposure_snapshot: CashExposureSnapshot | None = None
    stale_after_days: int = 5
    signal_ttl_days: int = 5

    def __post_init__(self) -> None:
        _require_non_empty(self.composition_id, "composition_id")
        _require_non_empty(self.portfolio_id, "portfolio_id")
        effective_date = _parse_date(self.effective_date, "effective_date")
        _parse_datetime(self.composed_at, "composed_at")
        if self.stale_after_days < 0:
            raise ValueError("stale_after_days must be >= 0")
        if self.signal_ttl_days < 1:
            raise ValueError("signal_ttl_days must be >= 1")
        if not self.scanner_candidates:
            raise ValueError("scanner_candidates are required")
        if not self.strategy_signals:
            raise ValueError("strategy_signals are required")

        _ensure_unique(
            (candidate.candidate_id for candidate in self.scanner_candidates),
            "scanner candidate ids",
        )
        _ensure_unique(
            (candidate.symbol_key for candidate in self.scanner_candidates),
            "scanner candidate symbols",
        )
        _ensure_unique(
            (signal.strategy_signal_id for signal in self.strategy_signals),
            "strategy signal ids",
        )
        _ensure_unique(
            (signal.symbol_key for signal in self.strategy_signals),
            "strategy signal symbols",
        )
        _ensure_unique(
            (support.report_id for support in self.backtest_support),
            "backtest report ids",
        )
        _ensure_unique(
            (support.symbol_key for support in self.backtest_support),
            "backtest support symbols",
        )

        for candidate in self.scanner_candidates:
            if _parse_date(candidate.as_of_date, "candidate.as_of_date") > effective_date:
                raise ValueError("scanner candidate as_of_date cannot be after effective_date")
        for strategy_signal in self.strategy_signals:
            if _parse_date(strategy_signal.as_of_date, "strategy_signal.as_of_date") > effective_date:
                raise ValueError("strategy signal as_of_date cannot be after effective_date")
        for backtest in self.backtest_support:
            if _parse_date(backtest.as_of_date, "backtest.as_of_date") > effective_date:
                raise ValueError("backtest support as_of_date cannot be after effective_date")

        if self.watchlist_snapshot is not None:
            if _parse_date(self.watchlist_snapshot.as_of_date, "watchlist_snapshot.as_of_date") > effective_date:
                raise ValueError("watchlist_snapshot.as_of_date cannot be after effective_date")
        if self.holding_snapshot is not None:
            if self.holding_snapshot.portfolio_id != self.portfolio_id:
                raise ValueError("holding_snapshot portfolio_id must match composition portfolio_id")
            if _parse_date(self.holding_snapshot.as_of_date, "holding_snapshot.as_of_date") > effective_date:
                raise ValueError("holding_snapshot.as_of_date cannot be after effective_date")
        if self.cash_exposure_snapshot is not None:
            if self.cash_exposure_snapshot.portfolio_id != self.portfolio_id:
                raise ValueError(
                    "cash_exposure_snapshot portfolio_id must match composition portfolio_id"
                )
            if (
                _parse_date(
                    self.cash_exposure_snapshot.as_of_date,
                    "cash_exposure_snapshot.as_of_date",
                )
                > effective_date
            ):
                raise ValueError("cash_exposure_snapshot.as_of_date cannot be after effective_date")


@dataclass(frozen=True)
class StructuredSignalCompositionResult:
    composition_id: str
    signals: tuple[SignalRecord, ...]


def compose_structured_signals(
    request: StructuredSignalCompositionRequest,
) -> StructuredSignalCompositionResult:
    scanner_by_key = {candidate.symbol_key: candidate for candidate in request.scanner_candidates}
    strategy_by_key = {signal.symbol_key: signal for signal in request.strategy_signals}
    backtest_by_key = {support.symbol_key: support for support in request.backtest_support}
    holding_keys = (
        {holding.symbol_key for holding in request.holding_snapshot.holdings}
        if request.holding_snapshot is not None
        else set()
    )

    if set(scanner_by_key) != set(strategy_by_key):
        missing_strategy = tuple(sorted(set(scanner_by_key) - set(strategy_by_key)))
        missing_scanner = tuple(sorted(set(strategy_by_key) - set(scanner_by_key)))
        raise ValueError(
            "scanner and strategy inputs must cover the same symbol set: "
            f"missing_strategy={missing_strategy!r}, missing_scanner={missing_scanner!r}"
        )

    unexpected_backtest = tuple(sorted(set(backtest_by_key) - set(scanner_by_key)))
    if unexpected_backtest:
        raise ValueError(
            "backtest support cannot reference symbols absent from scanner/strategy inputs"
        )

    signals: list[SignalRecord] = []
    signal_ids: set[str] = set()
    for order_index, candidate in enumerate(
        sorted(request.scanner_candidates, key=_scanner_sort_key),
        start=1,
    ):
        strategy_signal = strategy_by_key[candidate.symbol_key]
        backtest_support = backtest_by_key.get(candidate.symbol_key)
        has_holding = candidate.symbol_key in holding_keys
        _validate_strategy_alignment(
            candidate=candidate,
            strategy_signal=strategy_signal,
            backtest_support=backtest_support,
            has_holding=has_holding,
        )

        signal_id = _build_signal_id(candidate, strategy_signal)
        if signal_id in signal_ids:
            raise ValueError(f"duplicate signal ids are not allowed: {signal_id}")
        signal_ids.add(signal_id)

        stale_inputs = _collect_stale_inputs(
            request=request,
            candidate=candidate,
            strategy_signal=strategy_signal,
            backtest_support=backtest_support,
        )
        initial_status = (
            SignalDecisionStatus.WARNED if stale_inputs else SignalDecisionStatus.PASSED
        )
        reason_code = (
            "structured_signal_composed"
            if not stale_inputs
            else "structured_signal_composed_with_stale_inputs"
        )
        reason_summary = _build_reason_summary(
            candidate=candidate,
            strategy_signal=strategy_signal,
            backtest_support=backtest_support,
            stale_inputs=stale_inputs,
        )
        signals.append(
            create_signal_record(
                signal_id=signal_id,
                symbol=candidate.symbol,
                market=candidate.market,
                intent=strategy_signal.intent,
                created_at=request.composed_at,
                effective_date=request.effective_date,
                expires_on=(
                    _parse_date(request.effective_date, "effective_date")
                    + timedelta(days=request.signal_ttl_days)
                ).isoformat(),
                source_links=_build_signal_source_links(
                    request=request,
                    candidate=candidate,
                    strategy_signal=strategy_signal,
                    backtest_support=backtest_support,
                    has_holding=has_holding,
                ),
                reason_code=reason_code,
                reason_summary=reason_summary,
                initial_decision_status=initial_status,
                priority_rank=candidate.rank if candidate.rank is not None else order_index,
                signal_score=_compose_signal_score(
                    candidate_score=candidate.score,
                    conviction_score=strategy_signal.conviction_score,
                    support_score=(
                        backtest_support.support_score
                        if backtest_support is not None
                        else None
                    ),
                ),
            )
        )
    return StructuredSignalCompositionResult(
        composition_id=request.composition_id,
        signals=tuple(signals),
    )


def _validate_strategy_alignment(
    *,
    candidate: ScannerCandidateInput,
    strategy_signal: StrategySignalInput,
    backtest_support: BacktestSupportInput | None,
    has_holding: bool,
) -> None:
    if strategy_signal.symbol_key != candidate.symbol_key:
        raise ValueError("strategy signal symbol/market must match scanner candidate")
    if backtest_support is not None:
        if backtest_support.symbol_key != candidate.symbol_key:
            raise ValueError("backtest support symbol/market must match scanner candidate")
        if backtest_support.strategy_id != strategy_signal.strategy_id:
            raise ValueError("backtest support strategy_id must match strategy signal strategy_id")
    if strategy_signal.intent in (SignalIntent.EXIT, SignalIntent.REDUCE, SignalIntent.INCREASE):
        if not has_holding:
            raise ValueError(
                f"{strategy_signal.intent.value} intent requires an existing holding snapshot entry"
            )
    elif strategy_signal.intent is SignalIntent.ENTER and has_holding:
        raise ValueError("enter intent is inconsistent with an existing holding snapshot entry")


def _collect_stale_inputs(
    *,
    request: StructuredSignalCompositionRequest,
    candidate: ScannerCandidateInput,
    strategy_signal: StrategySignalInput,
    backtest_support: BacktestSupportInput | None,
) -> tuple[str, ...]:
    effective_date = _parse_date(request.effective_date, "effective_date")
    stale_inputs: list[str] = []
    for label, as_of_date in (
        ("scanner_candidate", candidate.as_of_date),
        ("strategy_signal", strategy_signal.as_of_date),
        (
            "backtest_support",
            backtest_support.as_of_date if backtest_support is not None else None,
        ),
        (
            "watchlist_snapshot",
            request.watchlist_snapshot.as_of_date if request.watchlist_snapshot is not None else None,
        ),
        (
            "holding_snapshot",
            request.holding_snapshot.as_of_date if request.holding_snapshot is not None else None,
        ),
        (
            "cash_exposure_snapshot",
            (
                request.cash_exposure_snapshot.as_of_date
                if request.cash_exposure_snapshot is not None
                else None
            ),
        ),
    ):
        if as_of_date is None:
            continue
        age_days = (effective_date - _parse_date(as_of_date, label)).days
        if age_days > request.stale_after_days:
            stale_inputs.append(f"{label}:{age_days}d")
    return tuple(stale_inputs)


def _build_reason_summary(
    *,
    candidate: ScannerCandidateInput,
    strategy_signal: StrategySignalInput,
    backtest_support: BacktestSupportInput | None,
    stale_inputs: tuple[str, ...],
) -> str:
    parts = [
        f"scanner={candidate.candidate_id}",
        f"intent={strategy_signal.intent.value}",
    ]
    if candidate.rank is not None:
        parts.append(f"rank={candidate.rank}")
    if candidate.score is not None:
        parts.append(f"scanner_score={candidate.score:.4f}")
    if strategy_signal.conviction_score is not None:
        parts.append(f"conviction={strategy_signal.conviction_score:.4f}")
    if backtest_support is not None and backtest_support.support_score is not None:
        parts.append(f"backtest_support={backtest_support.support_score:.4f}")
    if stale_inputs:
        parts.append("stale_inputs=" + ",".join(stale_inputs))
    return "; ".join(parts)


def _build_signal_source_links(
    *,
    request: StructuredSignalCompositionRequest,
    candidate: ScannerCandidateInput,
    strategy_signal: StrategySignalInput,
    backtest_support: BacktestSupportInput | None,
    has_holding: bool,
) -> tuple[SignalSourceLink, ...]:
    links = [
        SignalSourceLink(
            link_id=f"scanner:{candidate.candidate_id}",
            source_type=SignalSourceType.SCANNER_CANDIDATE,
            reference_id=candidate.candidate_id,
            recorded_at=candidate.ranked_at,
            summary=candidate.summary,
            source_version=candidate.source_version,
        ),
        SignalSourceLink(
            link_id=f"strategy:{strategy_signal.strategy_signal_id}",
            source_type=SignalSourceType.STRATEGY_DEFINITION,
            reference_id=strategy_signal.strategy_signal_id,
            recorded_at=strategy_signal.generated_at,
            summary=strategy_signal.rationale,
            source_version=strategy_signal.source_version,
        ),
    ]
    if backtest_support is not None:
        links.append(
            SignalSourceLink(
                link_id=f"backtest:{backtest_support.report_id}",
                source_type=SignalSourceType.BACKTEST_REPORT,
                reference_id=backtest_support.report_id,
                recorded_at=backtest_support.generated_at,
                summary=backtest_support.summary,
                source_version=backtest_support.source_version,
            )
        )
    if request.watchlist_snapshot is not None:
        links.append(
            SignalSourceLink(
                link_id=f"watchlist:{request.watchlist_snapshot.snapshot_id}",
                source_type=SignalSourceType.WATCHLIST_SNAPSHOT,
                reference_id=request.watchlist_snapshot.snapshot_id,
                recorded_at=f"{request.watchlist_snapshot.as_of_date}T00:00:00",
                summary="watchlist context attached for local portfolio review",
            )
        )
    if request.holding_snapshot is not None and has_holding:
        links.append(
            SignalSourceLink(
                link_id=(
                    "holding:"
                    f"{request.holding_snapshot.snapshot_id}:{candidate.symbol}:{candidate.market}"
                ),
                source_type=SignalSourceType.PORTFOLIO_HOLDING_SNAPSHOT,
                reference_id=request.holding_snapshot.snapshot_id,
                recorded_at=f"{request.holding_snapshot.as_of_date}T00:00:00",
                summary="existing holding context attached for signal composition",
            )
        )
    if request.cash_exposure_snapshot is not None:
        links.append(
            SignalSourceLink(
                link_id=f"cash:{request.cash_exposure_snapshot.snapshot_id}",
                source_type=SignalSourceType.PORTFOLIO_CASH_EXPOSURE_SNAPSHOT,
                reference_id=request.cash_exposure_snapshot.snapshot_id,
                recorded_at=f"{request.cash_exposure_snapshot.as_of_date}T00:00:00",
                summary="cash and exposure context attached for downstream risk evaluation",
            )
        )
    return tuple(sorted(links, key=lambda link: (link.source_type.value, link.reference_id, link.link_id)))


def _build_signal_id(
    candidate: ScannerCandidateInput,
    strategy_signal: StrategySignalInput,
) -> str:
    return (
        f"signal:{candidate.market}:{candidate.symbol}:"
        f"{strategy_signal.intent.value}:{candidate.candidate_id}:{strategy_signal.strategy_signal_id}"
    )


def _compose_signal_score(
    *,
    candidate_score: float | None,
    conviction_score: float | None,
    support_score: float | None,
) -> float | None:
    scores = tuple(
        score
        for score in (candidate_score, conviction_score, support_score)
        if score is not None
    )
    if not scores:
        return None
    return sum(scores) / len(scores)


def _scanner_sort_key(candidate: ScannerCandidateInput) -> tuple[int, float, str, str, str]:
    rank = candidate.rank if candidate.rank is not None else 10**9
    score = -candidate.score if candidate.score is not None else 0.0
    return (rank, score, candidate.symbol, candidate.market, candidate.candidate_id)


def _ensure_unique(values: Iterable[object], label: str) -> None:
    seen: set[object] = set()
    for value in values:
        if value in seen:
            raise ValueError(f"duplicate {label} are not allowed")
        seen.add(value)


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


def _ensure_ratio(value: float, field_name: str) -> None:
    _ensure_finite_number(value, field_name)
    if not 0 <= value <= 1:
        raise ValueError(f"{field_name} must be between 0 and 1")
