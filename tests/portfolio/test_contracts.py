import unittest

from quant.portfolio import (
    CashExposureSnapshot,
    HoldingState,
    SignalDecisionStatus,
    SignalIntent,
    SignalLifecycleState,
    SignalSourceLink,
    SignalSourceType,
    WatchlistItem,
    build_holding_snapshot,
    build_watchlist_snapshot,
    create_decision_audit_record,
    create_signal_record,
    merge_holding_snapshot,
    merge_watchlist_snapshot,
    transition_signal_state,
)


class PortfolioContractTestCase(unittest.TestCase):
    def test_watchlist_and_holding_snapshots_merge_deterministically(self) -> None:
        watchlist = build_watchlist_snapshot(
            snapshot_id="watchlist-snapshot-1",
            watchlist_id="growth-list",
            as_of_date="2026-06-12",
            items=(
                WatchlistItem(
                    item_id="wl-2",
                    watchlist_id="growth-list",
                    symbol="00700",
                    market="HK",
                    added_on="2026-06-10",
                    rank=2,
                ),
                WatchlistItem(
                    item_id="wl-1",
                    watchlist_id="growth-list",
                    symbol="600519",
                    market="CN",
                    added_on="2026-06-09",
                    rank=1,
                ),
            ),
        )
        merged_watchlist = merge_watchlist_snapshot(
            current=watchlist,
            updates=(
                WatchlistItem(
                    item_id="wl-3",
                    watchlist_id="growth-list",
                    symbol="000001",
                    market="CN",
                    added_on="2026-06-11",
                    rank=0,
                ),
                WatchlistItem(
                    item_id="wl-4",
                    watchlist_id="growth-list",
                    symbol="600519",
                    market="CN",
                    added_on="2026-06-12",
                    rank=3,
                ),
            ),
            snapshot_id="watchlist-snapshot-2",
            as_of_date="2026-06-12",
        )

        self.assertEqual(
            [item.symbol for item in watchlist.items],
            ["600519", "00700"],
        )
        self.assertEqual(
            [(item.symbol, item.rank, item.item_id) for item in merged_watchlist.items],
            [
                ("000001", 0, "wl-3"),
                ("00700", 2, "wl-2"),
                ("600519", 3, "wl-4"),
            ],
        )

        holding_snapshot = build_holding_snapshot(
            snapshot_id="holding-snapshot-1",
            portfolio_id="paper-account",
            as_of_date="2026-06-12",
            holdings=(
                HoldingState(
                    holding_id="holding-2",
                    portfolio_id="paper-account",
                    symbol="00700",
                    market="HK",
                    quantity=100,
                    average_cost=320.0,
                    cost_basis=32000.0,
                    updated_at="2026-06-12T09:30:00",
                ),
                HoldingState(
                    holding_id="holding-1",
                    portfolio_id="paper-account",
                    symbol="600519",
                    market="CN",
                    quantity=10,
                    average_cost=1500.0,
                    cost_basis=15000.0,
                    portfolio_weight=0.4,
                    updated_at="2026-06-12T09:31:00",
                ),
            ),
        )
        merged_holdings = merge_holding_snapshot(
            current=holding_snapshot,
            updates=(
                HoldingState(
                    holding_id="holding-3",
                    portfolio_id="paper-account",
                    symbol="000001",
                    market="CN",
                    quantity=500,
                    average_cost=12.0,
                    cost_basis=6000.0,
                    portfolio_weight=0.15,
                    updated_at="2026-06-12T10:00:00",
                ),
                HoldingState(
                    holding_id="holding-4",
                    portfolio_id="paper-account",
                    symbol="600519",
                    market="CN",
                    quantity=12,
                    average_cost=1510.0,
                    cost_basis=18120.0,
                    portfolio_weight=0.45,
                    updated_at="2026-06-12T10:05:00",
                ),
            ),
            snapshot_id="holding-snapshot-2",
            as_of_date="2026-06-12",
        )

        self.assertEqual(
            [holding.symbol for holding in merged_holdings.holdings],
            ["000001", "00700", "600519"],
        )
        self.assertEqual(merged_holdings.holdings[-1].quantity, 12)
        self.assertEqual(merged_holdings.holdings[-1].holding_id, "holding-4")

        exposure = CashExposureSnapshot(
            snapshot_id="cash-1",
            portfolio_id="paper-account",
            as_of_date="2026-06-12",
            total_equity=100000.0,
            available_cash=30000.0,
            reserved_cash=5000.0,
            gross_exposure=0.7,
            net_exposure=0.7,
        )
        self.assertEqual(exposure.available_cash, 30000.0)

    def test_portfolio_contracts_reject_duplicates_and_invalid_values(self) -> None:
        with self.assertRaisesRegex(ValueError, "duplicate watchlist symbols"):
            build_watchlist_snapshot(
                snapshot_id="watchlist-snapshot-1",
                watchlist_id="growth-list",
                as_of_date="2026-06-12",
                items=(
                    WatchlistItem(
                        item_id="wl-1",
                        watchlist_id="growth-list",
                        symbol="600519",
                        market="CN",
                        added_on="2026-06-10",
                    ),
                    WatchlistItem(
                        item_id="wl-2",
                        watchlist_id="growth-list",
                        symbol="600519",
                        market="CN",
                        added_on="2026-06-11",
                    ),
                ),
            )

        with self.assertRaisesRegex(ValueError, "quantity must be > 0"):
            HoldingState(
                holding_id="holding-1",
                portfolio_id="paper-account",
                symbol="600519",
                market="CN",
                quantity=0,
                average_cost=1500.0,
                updated_at="2026-06-12T09:30:00",
            )

        with self.assertRaisesRegex(ValueError, "cost_basis must equal average_cost"):
            HoldingState(
                holding_id="holding-2",
                portfolio_id="paper-account",
                symbol="00700",
                market="HK",
                quantity=10,
                average_cost=300.0,
                cost_basis=2000.0,
                updated_at="2026-06-12T09:30:00",
            )

        with self.assertRaisesRegex(ValueError, "absolute net_exposure cannot exceed gross_exposure"):
            CashExposureSnapshot(
                snapshot_id="cash-1",
                portfolio_id="paper-account",
                as_of_date="2026-06-12",
                total_equity=100000.0,
                available_cash=30000.0,
                reserved_cash=5000.0,
                gross_exposure=0.5,
                net_exposure=0.8,
            )


class SignalContractTestCase(unittest.TestCase):
    def test_signal_lifecycle_transitions_are_deterministic(self) -> None:
        base_signal = create_signal_record(
            signal_id="signal-1",
            symbol="600519",
            market="CN",
            intent=SignalIntent.ENTER,
            created_at="2026-06-12T09:30:00",
            effective_date="2026-06-12",
            source_links=(
                SignalSourceLink(
                    link_id="source-2",
                    source_type=SignalSourceType.STRATEGY_DEFINITION,
                    reference_id="strategy-breakout-v1",
                    recorded_at="2026-06-12T09:29:00",
                    summary="strategy configuration selected this setup",
                ),
                SignalSourceLink(
                    link_id="source-1",
                    source_type=SignalSourceType.SCANNER_CANDIDATE,
                    reference_id="scanner-candidate-001",
                    recorded_at="2026-06-12T09:28:00",
                    summary="scanner ranked the symbol inside the top bucket",
                ),
            ),
            reason_code="scanner_and_strategy_aligned",
            reason_summary="scanner rank and strategy intent both support an entry candidate",
            expires_on="2026-06-20",
        )
        updated_signal = transition_signal_state(
            signal=base_signal,
            target_state=SignalLifecycleState.UPDATED,
            transitioned_at="2026-06-12T10:00:00",
            reason_code="portfolio_context_refreshed",
            reason_summary="position and cash context were refreshed for the same signal",
            source_links=(
                SignalSourceLink(
                    link_id="source-3",
                    source_type=SignalSourceType.PORTFOLIO_HOLDING_SNAPSHOT,
                    reference_id="holding-snapshot-2",
                    recorded_at="2026-06-12T09:59:00",
                    summary="portfolio holdings were refreshed before the signal update",
                ),
            ),
        )
        expired_signal = transition_signal_state(
            signal=updated_signal,
            target_state=SignalLifecycleState.EXPIRED,
            transitioned_at="2026-06-20T15:00:00",
            reason_code="time_window_elapsed",
            reason_summary="entry window elapsed without a valid execution path",
            expiry_reason="signal freshness window expired",
        )
        closed_signal = transition_signal_state(
            signal=base_signal,
            target_state=SignalLifecycleState.CLOSED,
            transitioned_at="2026-06-13T11:00:00",
            reason_code="manual_close",
            reason_summary="owner closed the signal after review",
            closure_reason="manual operator close",
        )

        self.assertEqual(base_signal.lifecycle_state, SignalLifecycleState.CREATED)
        self.assertEqual(base_signal.version, 1)
        self.assertEqual(
            [link.link_id for link in base_signal.source_links],
            ["source-1", "source-2"],
        )
        self.assertEqual(
            base_signal.decision_audit[0].decision_status,
            SignalDecisionStatus.PASSED,
        )

        self.assertEqual(updated_signal.lifecycle_state, SignalLifecycleState.UPDATED)
        self.assertEqual(updated_signal.version, 2)
        self.assertEqual(len(updated_signal.source_links), 3)
        self.assertEqual(updated_signal.decision_audit[-1].reason_code, "portfolio_context_refreshed")

        self.assertEqual(expired_signal.lifecycle_state, SignalLifecycleState.EXPIRED)
        self.assertEqual(expired_signal.expired_reason, "signal freshness window expired")
        self.assertEqual(
            expired_signal.decision_audit[-1].decision_status,
            SignalDecisionStatus.EXPIRED,
        )

        self.assertEqual(closed_signal.lifecycle_state, SignalLifecycleState.CLOSED)
        self.assertEqual(closed_signal.closed_reason, "manual operator close")
        self.assertEqual(
            closed_signal.decision_audit[-1].decision_status,
            SignalDecisionStatus.CLOSED,
        )

    def test_signal_contracts_reject_invalid_transitions_and_reason_rules(self) -> None:
        signal = create_signal_record(
            signal_id="signal-2",
            symbol="00700",
            market="HK",
            intent=SignalIntent.EXIT,
            created_at="2026-06-12T09:30:00",
            effective_date="2026-06-12",
            source_links=(),
            reason_code="exit_signal",
            reason_summary="strategy generated an exit candidate",
            initial_decision_status=SignalDecisionStatus.WARNED,
        )
        closed_signal = transition_signal_state(
            signal=signal,
            target_state=SignalLifecycleState.CLOSED,
            transitioned_at="2026-06-12T11:00:00",
            reason_code="closed",
            reason_summary="review closed the signal",
            closure_reason="review close",
        )

        with self.assertRaisesRegex(ValueError, "unsupported signal transition"):
            transition_signal_state(
                signal=closed_signal,
                target_state=SignalLifecycleState.UPDATED,
                transitioned_at="2026-06-12T12:00:00",
                reason_code="should_fail",
                reason_summary="closed signals cannot be updated",
            )

        with self.assertRaisesRegex(ValueError, "expired lifecycle_state requires expiry_reason"):
            create_decision_audit_record(
                audit_id="audit-1",
                signal_id="signal-2",
                lifecycle_state=SignalLifecycleState.EXPIRED,
                decision_status=SignalDecisionStatus.EXPIRED,
                recorded_at="2026-06-13T10:00:00",
                reason_code="expired",
                reason_summary="signal expired",
                source_links=(),
            )

        with self.assertRaisesRegex(ValueError, "closed lifecycle_state requires closure_reason"):
            transition_signal_state(
                signal=signal,
                target_state=SignalLifecycleState.CLOSED,
                transitioned_at="2026-06-12T12:00:00",
                reason_code="missing_close_reason",
                reason_summary="closure reason is required",
            )

    def test_source_links_and_decision_audit_validate_local_references(self) -> None:
        audit = create_decision_audit_record(
            audit_id="audit-2",
            signal_id="signal-3",
            lifecycle_state=SignalLifecycleState.CREATED,
            decision_status=SignalDecisionStatus.BLOCKED,
            recorded_at="2026-06-12T09:35:00",
            reason_code="liquidity_guard_pending",
            reason_summary="liquidity rule is pending implementation so the signal stays blocked for review",
            source_links=(
                SignalSourceLink(
                    link_id="source-2",
                    source_type=SignalSourceType.BACKTEST_REPORT,
                    reference_id="backtest-report-11",
                    recorded_at="2026-06-12T09:34:00",
                    summary="backtest summary provides historical context",
                ),
                SignalSourceLink(
                    link_id="source-1",
                    source_type=SignalSourceType.WATCHLIST_SNAPSHOT,
                    reference_id="watchlist-snapshot-2",
                    recorded_at="2026-06-12T09:33:00",
                    summary="watchlist membership kept the symbol in scope",
                ),
            ),
        )

        self.assertEqual(audit.decision_status, SignalDecisionStatus.BLOCKED)
        self.assertEqual([link.link_id for link in audit.source_links], ["source-2", "source-1"])


if __name__ == "__main__":
    unittest.main()
