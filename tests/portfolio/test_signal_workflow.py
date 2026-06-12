import unittest

from quant.portfolio import (
    BlacklistRiskRule,
    BlockedInstrument,
    CashExposureSnapshot,
    RiskRuleSet,
    ScannerCandidateInput,
    SignalConflictStatus,
    SignalDecisionStatus,
    SignalIntent,
    SignalLifecycleState,
    SignalMarketContext,
    SignalSourceLink,
    SignalSourceType,
    StrategySignalInput,
    StructuredSignalCompositionRequest,
    WatchlistItem,
    build_watchlist_snapshot,
    compose_structured_signals,
    create_signal_record,
    evaluate_signal_risk,
    reconcile_conflicting_signals,
    transition_signal_state,
)


def _build_single_symbol_request(
    *,
    effective_date: str = "2026-06-12",
    candidate_as_of: str = "2026-06-12",
    strategy_as_of: str = "2026-06-12",
    watchlist_as_of: str = "2026-06-12",
) -> StructuredSignalCompositionRequest:
    return StructuredSignalCompositionRequest(
        composition_id="workflow-composition-1",
        portfolio_id="paper-account",
        effective_date=effective_date,
        composed_at="2026-06-12T10:00:00",
        stale_after_days=2,
        scanner_candidates=(
            ScannerCandidateInput(
                candidate_id="scanner-600519",
                symbol="600519",
                market="CN",
                as_of_date=candidate_as_of,
                ranked_at="2026-06-12T09:20:00",
                summary="scanner ranked the A-share symbol",
                rank=1,
                score=0.9,
            ),
        ),
        strategy_signals=(
            StrategySignalInput(
                strategy_signal_id="strategy-600519",
                strategy_id="breakout-v1",
                symbol="600519",
                market="CN",
                intent=SignalIntent.ENTER,
                as_of_date=strategy_as_of,
                generated_at="2026-06-12T09:25:00",
                rationale="strategy wants a fresh long entry",
                conviction_score=0.7,
            ),
        ),
        watchlist_snapshot=build_watchlist_snapshot(
            snapshot_id="watchlist-1",
            watchlist_id="phase6-watchlist",
            as_of_date=watchlist_as_of,
            items=(
                WatchlistItem(
                    item_id="wl-600519",
                    watchlist_id="phase6-watchlist",
                    symbol="600519",
                    market="CN",
                    added_on="2026-06-01",
                    rank=1,
                ),
            ),
        ),
        cash_exposure_snapshot=CashExposureSnapshot(
            snapshot_id="cash-1",
            portfolio_id="paper-account",
            as_of_date="2026-06-12",
            total_equity=100000.0,
            available_cash=30000.0,
            reserved_cash=5000.0,
            gross_exposure=0.30,
            net_exposure=0.30,
        ),
    )


def _build_blacklist_rule_set() -> RiskRuleSet:
    return RiskRuleSet(
        rule_set_id="rules-blacklist",
        portfolio_id="paper-account",
        blacklist_rules=(
            BlacklistRiskRule(
                rule_id="blacklist-local",
                blocked_instruments=(
                    BlockedInstrument(
                        symbol="600519",
                        market="CN",
                        reason="local personal blacklist",
                    ),
                ),
            ),
        ),
    )


class SignalConflictWorkflowTestCase(unittest.TestCase):
    def test_duplicate_signal_ids_are_rejected_before_conflict_resolution(self) -> None:
        first_signal = create_signal_record(
            signal_id="signal-dup",
            symbol="600519",
            market="CN",
            intent=SignalIntent.ENTER,
            created_at="2026-06-12T09:30:00",
            effective_date="2026-06-12",
            source_links=(),
            reason_code="scanner_strategy_match",
            reason_summary="first duplicated id candidate",
            priority_rank=1,
            signal_score=0.9,
        )
        second_signal = create_signal_record(
            signal_id="signal-dup",
            symbol="600519",
            market="CN",
            intent=SignalIntent.EXIT,
            created_at="2026-06-12T09:31:00",
            effective_date="2026-06-12",
            source_links=(),
            reason_code="risk_exit_match",
            reason_summary="second duplicated id candidate",
            priority_rank=1,
            signal_score=0.9,
        )

        with self.assertRaisesRegex(
            ValueError,
            "duplicate signal ids are not allowed: signal-dup",
        ):
            reconcile_conflicting_signals(
                signals=(first_signal, second_signal),
                resolved_at="2026-06-12T10:00:00",
            )

    def test_competing_same_symbol_signals_are_superseded_deterministically(self) -> None:
        winning_signal = create_signal_record(
            signal_id="signal-enter-a",
            symbol="600519",
            market="CN",
            intent=SignalIntent.ENTER,
            created_at="2026-06-12T09:30:00",
            effective_date="2026-06-12",
            source_links=(),
            reason_code="scanner_strategy_match",
            reason_summary="first entry candidate",
            priority_rank=1,
            signal_score=0.9,
        )
        losing_signal = create_signal_record(
            signal_id="signal-enter-b",
            symbol="600519",
            market="CN",
            intent=SignalIntent.ENTER,
            created_at="2026-06-12T09:31:00",
            effective_date="2026-06-12",
            source_links=(),
            reason_code="scanner_strategy_match",
            reason_summary="second entry candidate",
            priority_rank=2,
            signal_score=0.6,
        )

        result = reconcile_conflicting_signals(
            signals=(winning_signal, losing_signal),
            resolved_at="2026-06-12T10:00:00",
        )

        resolved_winner, resolved_loser = result.signals
        self.assertEqual(resolved_winner.version, 2)
        self.assertEqual(
            resolved_winner.decision_audit[-1].reason_code,
            "signal_supersession_selected",
        )
        self.assertEqual(resolved_winner.conflict_status, SignalConflictStatus.NONE)

        self.assertEqual(resolved_loser.version, 2)
        self.assertEqual(resolved_loser.conflict_status, SignalConflictStatus.SUPERSEDED)
        self.assertEqual(resolved_loser.superseded_by_signal_id, "signal-enter-a")
        self.assertEqual(
            resolved_loser.decision_audit[-1].decision_status,
            SignalDecisionStatus.BLOCKED,
        )
        self.assertEqual(
            resolved_loser.decision_audit[-1].reason_code,
            "signal_superseded",
        )

    def test_opposite_intent_tie_marks_all_candidates_conflicting(self) -> None:
        enter_signal = create_signal_record(
            signal_id="signal-enter",
            symbol="00700",
            market="HK",
            intent=SignalIntent.ENTER,
            created_at="2026-06-12T09:30:00",
            effective_date="2026-06-12",
            source_links=(),
            reason_code="enter_setup",
            reason_summary="entry signal",
            priority_rank=1,
            signal_score=0.8,
        )
        exit_signal = create_signal_record(
            signal_id="signal-exit",
            symbol="00700",
            market="HK",
            intent=SignalIntent.EXIT,
            created_at="2026-06-12T09:30:00",
            effective_date="2026-06-12",
            source_links=(),
            reason_code="exit_setup",
            reason_summary="exit signal",
            priority_rank=1,
            signal_score=0.8,
        )

        result = reconcile_conflicting_signals(
            signals=(enter_signal, exit_signal),
            resolved_at="2026-06-12T10:00:00",
        )

        for signal in result.signals:
            self.assertEqual(signal.lifecycle_state, SignalLifecycleState.UPDATED)
            self.assertEqual(signal.conflict_status, SignalConflictStatus.CONFLICTING)
            self.assertIsNone(signal.superseded_by_signal_id)
            self.assertEqual(
                signal.decision_audit[-1].decision_status,
                SignalDecisionStatus.BLOCKED,
            )
            self.assertEqual(
                signal.decision_audit[-1].reason_code,
                "signal_conflict_detected",
            )


class SignalLifecycleWorkflowTestCase(unittest.TestCase):
    def test_stale_composed_signal_can_update_then_expire_and_reject_invalid_follow_up(self) -> None:
        stale_signal = compose_structured_signals(
            _build_single_symbol_request(
                candidate_as_of="2026-06-08",
                strategy_as_of="2026-06-08",
                watchlist_as_of="2026-06-08",
            )
        ).signals[0]
        refreshed_signal = transition_signal_state(
            signal=stale_signal,
            target_state=SignalLifecycleState.UPDATED,
            transitioned_at="2026-06-12T11:00:00",
            reason_code="portfolio_context_refreshed",
            reason_summary="stale signal kept for manual review after local refresh",
            source_links=(
                SignalSourceLink(
                    link_id="refresh:manual-review",
                    source_type=SignalSourceType.MARKET_CONTEXT_SNAPSHOT,
                    reference_id="CN:600519:2026-06-12",
                    recorded_at="2026-06-12T10:59:00",
                    summary="manual local market context refresh attached",
                ),
            ),
            decision_status=SignalDecisionStatus.WARNED,
        )
        expired_signal = transition_signal_state(
            signal=refreshed_signal,
            target_state=SignalLifecycleState.EXPIRED,
            transitioned_at="2026-06-15T15:00:00",
            reason_code="signal_time_window_elapsed",
            reason_summary="stale signal expired without a fresh aligned workflow",
            expiry_reason="signal freshness window expired",
        )

        self.assertEqual(stale_signal.decision_audit[0].decision_status, SignalDecisionStatus.WARNED)
        self.assertEqual(refreshed_signal.lifecycle_state, SignalLifecycleState.UPDATED)
        self.assertEqual(expired_signal.lifecycle_state, SignalLifecycleState.EXPIRED)
        self.assertEqual(expired_signal.expired_reason, "signal freshness window expired")
        self.assertEqual(len(expired_signal.decision_audit), 3)
        self.assertIn("refresh:manual-review", {link.link_id for link in expired_signal.source_links})
        self.assertIn(
            "scanner:scanner-600519",
            {link.link_id for link in expired_signal.source_links},
        )
        with self.assertRaisesRegex(ValueError, "unsupported signal transition"):
            transition_signal_state(
                signal=expired_signal,
                target_state=SignalLifecycleState.CLOSED,
                transitioned_at="2026-06-15T16:00:00",
                reason_code="should_fail",
                reason_summary="expired signals cannot be closed later",
                closure_reason="invalid close",
            )

    def test_risk_blocked_signal_can_close_with_block_reason_and_provenance(self) -> None:
        composed_signal = compose_structured_signals(_build_single_symbol_request()).signals[0]
        blocked_result = evaluate_signal_risk(
            signal=composed_signal,
            rule_set=_build_blacklist_rule_set(),
            market_context=SignalMarketContext(
                symbol="600519",
                market="CN",
                as_of_date="2026-06-12",
                latest_price=100.0,
                average_daily_value=10_000_000.0,
            ),
            evaluated_at="2026-06-12T10:30:00",
            cash_exposure_snapshot=CashExposureSnapshot(
                snapshot_id="cash-risk-block",
                portfolio_id="paper-account",
                as_of_date="2026-06-12",
                total_equity=100000.0,
                available_cash=30000.0,
                reserved_cash=5000.0,
                gross_exposure=0.30,
                net_exposure=0.30,
            ),
        )
        closed_signal = transition_signal_state(
            signal=blocked_result.signal,
            target_state=SignalLifecycleState.CLOSED,
            transitioned_at="2026-06-12T11:00:00",
            reason_code="manual_close_after_block",
            reason_summary="operator closed the blocked signal after review",
            closure_reason="manual operator close",
        )

        self.assertEqual(blocked_result.overall_status, SignalDecisionStatus.BLOCKED)
        self.assertEqual(
            blocked_result.signal.decision_audit[-1].reason_code,
            "blacklist_block",
        )
        self.assertIn(
            SignalSourceType.RISK_RULE_SET,
            {link.source_type for link in blocked_result.signal.source_links},
        )
        self.assertIn(
            SignalSourceType.MARKET_CONTEXT_SNAPSHOT,
            {link.source_type for link in blocked_result.signal.source_links},
        )
        self.assertEqual(closed_signal.lifecycle_state, SignalLifecycleState.CLOSED)
        self.assertEqual(closed_signal.closed_reason, "manual operator close")
        self.assertEqual(closed_signal.decision_audit[-2].reason_code, "blacklist_block")
        self.assertEqual(
            closed_signal.decision_audit[-1].decision_status,
            SignalDecisionStatus.CLOSED,
        )


if __name__ == "__main__":
    unittest.main()
