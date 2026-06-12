"""Local/offline signal workflow helpers for conflict reconciliation."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from typing import Iterable

from .contracts import (
    SignalConflictStatus,
    SignalDecisionStatus,
    SignalLifecycleState,
    SignalRecord,
    SignalSourceLink,
    transition_signal_state,
)


@dataclass(frozen=True)
class SignalConflictResolutionResult:
    resolved_at: str
    signals: tuple[SignalRecord, ...]


def reconcile_conflicting_signals(
    *,
    signals: Iterable[SignalRecord],
    resolved_at: str,
    source_links: Iterable[SignalSourceLink] = (),
) -> SignalConflictResolutionResult:
    """Resolve same-symbol active-signal conflicts deterministically."""
    resolved_timestamp = _parse_datetime(resolved_at, "resolved_at")
    base_signals = tuple(signals)
    extra_links = tuple(source_links)
    if not base_signals:
        raise ValueError("signals are required")

    grouped: dict[tuple[str, str], list[SignalRecord]] = {}
    for signal in base_signals:
        if signal.lifecycle_state not in (
            SignalLifecycleState.CREATED,
            SignalLifecycleState.UPDATED,
        ):
            raise ValueError("only active created/updated signals can be reconciled")
        if _parse_datetime(signal.updated_at, "signal.updated_at") > resolved_timestamp:
            raise ValueError("resolved_at cannot be before signal.updated_at")
        grouped.setdefault((signal.symbol, signal.market), []).append(signal)

    resolved_by_id: dict[str, SignalRecord] = {signal.signal_id: signal for signal in base_signals}
    for symbol_key, group in grouped.items():
        if len(group) < 2:
            continue
        winners = sorted(group, key=_conflict_priority_key)
        winner = winners[0]
        runner_up = winners[1]
        if _is_unresolved_conflict(winner=winner, runner_up=runner_up):
            for signal in group:
                resolved_by_id[signal.signal_id] = _mark_conflicting(
                    signal=signal,
                    resolved_at=resolved_at,
                    source_links=extra_links,
                    symbol_key=symbol_key,
                    peer_ids=tuple(sorted(peer.signal_id for peer in group)),
                )
            continue

        loser_ids = tuple(signal.signal_id for signal in winners[1:])
        resolved_by_id[winner.signal_id] = _mark_selected_winner(
            signal=winner,
            resolved_at=resolved_at,
            source_links=extra_links,
            symbol_key=symbol_key,
            loser_ids=loser_ids,
        )
        for signal in winners[1:]:
            resolved_by_id[signal.signal_id] = _mark_superseded(
                signal=signal,
                resolved_at=resolved_at,
                source_links=extra_links,
                symbol_key=symbol_key,
                winner_signal_id=winner.signal_id,
            )

    return SignalConflictResolutionResult(
        resolved_at=resolved_at,
        signals=tuple(resolved_by_id[signal.signal_id] for signal in base_signals),
    )


def _mark_conflicting(
    *,
    signal: SignalRecord,
    resolved_at: str,
    source_links: tuple[SignalSourceLink, ...],
    symbol_key: tuple[str, str],
    peer_ids: tuple[str, ...],
) -> SignalRecord:
    updated = transition_signal_state(
        signal=signal,
        target_state=SignalLifecycleState.UPDATED,
        transitioned_at=resolved_at,
        reason_code="signal_conflict_detected",
        reason_summary=(
            f"conflicting active signals for {symbol_key[1]}:{symbol_key[0]}; "
            f"candidates={','.join(peer_ids)}; no deterministic winner"
        ),
        source_links=source_links,
        decision_status=SignalDecisionStatus.BLOCKED,
    )
    return replace(
        updated,
        conflict_status=SignalConflictStatus.CONFLICTING,
        superseded_by_signal_id=None,
    )


def _mark_selected_winner(
    *,
    signal: SignalRecord,
    resolved_at: str,
    source_links: tuple[SignalSourceLink, ...],
    symbol_key: tuple[str, str],
    loser_ids: tuple[str, ...],
) -> SignalRecord:
    updated = transition_signal_state(
        signal=signal,
        target_state=SignalLifecycleState.UPDATED,
        transitioned_at=resolved_at,
        reason_code="signal_supersession_selected",
        reason_summary=(
            f"selected winning signal for {symbol_key[1]}:{symbol_key[0]}; "
            f"superseded={','.join(loser_ids)}"
        ),
        source_links=source_links,
        decision_status=_active_decision_status(signal),
    )
    return replace(
        updated,
        conflict_status=SignalConflictStatus.NONE,
        superseded_by_signal_id=None,
    )


def _mark_superseded(
    *,
    signal: SignalRecord,
    resolved_at: str,
    source_links: tuple[SignalSourceLink, ...],
    symbol_key: tuple[str, str],
    winner_signal_id: str,
) -> SignalRecord:
    updated = transition_signal_state(
        signal=signal,
        target_state=SignalLifecycleState.UPDATED,
        transitioned_at=resolved_at,
        reason_code="signal_superseded",
        reason_summary=(
            f"superseded by {winner_signal_id} for {symbol_key[1]}:{symbol_key[0]}"
        ),
        source_links=source_links,
        decision_status=SignalDecisionStatus.BLOCKED,
    )
    return replace(
        updated,
        conflict_status=SignalConflictStatus.SUPERSEDED,
        superseded_by_signal_id=winner_signal_id,
    )


def _active_decision_status(signal: SignalRecord) -> SignalDecisionStatus:
    if signal.decision_audit:
        latest = signal.decision_audit[-1].decision_status
        if latest in (
            SignalDecisionStatus.PASSED,
            SignalDecisionStatus.WARNED,
            SignalDecisionStatus.BLOCKED,
        ):
            return latest
    return SignalDecisionStatus.PASSED


def _is_unresolved_conflict(
    *,
    winner: SignalRecord,
    runner_up: SignalRecord,
) -> bool:
    if winner.intent == runner_up.intent:
        return False
    return _conflict_priority_basis(winner) == _conflict_priority_basis(runner_up)


def _conflict_priority_key(signal: SignalRecord) -> tuple[int, float, float, str]:
    return (*_conflict_priority_basis(signal), signal.signal_id)


def _conflict_priority_basis(signal: SignalRecord) -> tuple[int, float, float]:
    rank = signal.priority_rank if signal.priority_rank is not None else 10**9
    score = -(signal.signal_score if signal.signal_score is not None else float("-inf"))
    updated_at = -_parse_datetime(signal.updated_at, "signal.updated_at").timestamp()
    return (rank, score, updated_at)


def _parse_datetime(value: str, field_name: str) -> datetime:
    try:
        return datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a valid ISO datetime") from exc
