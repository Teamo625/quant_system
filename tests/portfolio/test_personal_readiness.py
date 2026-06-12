import unittest

from quant.portfolio import (
    ReadinessStatus,
    build_portfolio_signal_risk_personal_readiness_gate,
)


class PortfolioSignalRiskPersonalReadinessGateTestCase(unittest.TestCase):
    def test_gate_returns_expected_phase_summary(self) -> None:
        gate = build_portfolio_signal_risk_personal_readiness_gate()
        status_counts = {
            status_count.status: status_count.count for status_count in gate.status_counts
        }

        self.assertEqual(
            gate.phase_id,
            "Phase 6 PortfolioMonitor, SignalEngine, and RiskEngine Personal Trading Perfection",
        )
        self.assertFalse(gate.phase_closure_ready)
        self.assertEqual(
            status_counts,
            {
                ReadinessStatus.PASS: 5,
                ReadinessStatus.WARN: 1,
                ReadinessStatus.BLOCKED: 0,
                ReadinessStatus.FAIL: 0,
            },
        )
        self.assertEqual(
            gate.recommended_next_handoff_batch_id,
            "portfolio_signal_risk__personal_trading_hardening__batch_03",
        )
        self.assertEqual(
            gate.recommended_next_handoff_title,
            "Phase 6 offline regression coverage for conflict, staleness, risk blocks, and lifecycle transitions",
        )

    def test_capability_groups_capture_current_phase6_gaps(self) -> None:
        gate = build_portfolio_signal_risk_personal_readiness_gate()
        groups = {group.group_id: group for group in gate.capability_groups}

        self.assertEqual(
            groups["watchlist_and_holding_state_contracts"].status,
            ReadinessStatus.PASS,
        )
        self.assertEqual(
            groups["watchlist_and_holding_state_contracts"].implemented_capabilities,
            (
                "cash_exposure_snapshot_contracts",
                "deterministic_portfolio_update_inputs",
                "holding_state_contracts",
                "watchlist_contracts",
            ),
        )
        self.assertEqual(
            groups["signal_lifecycle_management"].status,
            ReadinessStatus.PASS,
        )
        self.assertEqual(
            groups["upstream_context_combination_into_structured_signals"].status,
            ReadinessStatus.PASS,
        )
        self.assertEqual(
            groups["upstream_context_combination_into_structured_signals"].implemented_capabilities,
            (
                "backtest_report_input_contract",
                "portfolio_context_merge",
                "scanner_candidate_input_contract",
                "strategy_output_input_contract",
                "structured_signal_output_contract",
            ),
        )
        self.assertEqual(
            groups["risk_rule_evaluation_foundation"].status,
            ReadinessStatus.PASS,
        )
        self.assertEqual(
            groups["signal_auditability_and_decision_trace"].implemented_capabilities,
            (
                "closure_reason_capture",
                "risk_check_audit_records",
                "signal_pass_fail_decision_trace",
                "signal_reason_capture",
                "upstream_source_reference_capture",
            ),
        )
        self.assertEqual(
            groups["offline_regression_coverage_for_conflicts_staleness_risk_and_lifecycle"].status,
            ReadinessStatus.WARN,
        )
        self.assertEqual(
            groups["offline_regression_coverage_for_conflicts_staleness_risk_and_lifecycle"].implemented_capabilities,
            (
                "lifecycle_transition_tests",
                "risk_blocked_signal_tests",
                "stale_input_tests",
            ),
        )

    def test_follow_up_queue_and_batches_are_deterministic_and_complete(self) -> None:
        first_gate = build_portfolio_signal_risk_personal_readiness_gate()
        second_gate = build_portfolio_signal_risk_personal_readiness_gate()

        self.assertEqual(first_gate.follow_up_queue, second_gate.follow_up_queue)
        self.assertEqual(first_gate.follow_up_batches, second_gate.follow_up_batches)

        follow_up_ids = {item.follow_up_id for item in first_gate.follow_up_queue}
        batch_item_ids = {
            item_id
            for batch in first_gate.follow_up_batches
            for item_id in batch.item_ids
        }

        self.assertEqual(
            follow_up_ids,
            {
                "phase6__conflicting_and_risk_blocked_signal_regressions",
                "phase6__stale_input_and_lifecycle_transition_regressions",
            },
        )
        self.assertEqual(follow_up_ids, batch_item_ids)
        self.assertEqual(len(first_gate.follow_up_batches), 1)

    def test_recommended_next_handoff_matches_first_batch_priority(self) -> None:
        gate = build_portfolio_signal_risk_personal_readiness_gate()
        first_batch = gate.follow_up_batches[0]

        self.assertEqual(gate.recommended_next_handoff_batch_id, first_batch.batch_id)
        self.assertEqual(gate.recommended_next_handoff_title, first_batch.title)
        self.assertEqual(gate.recommended_next_handoff_theme, first_batch.theme)
        self.assertEqual(gate.recommended_next_handoff_rationale, first_batch.rationale)
        self.assertEqual(
            first_batch.item_ids,
            (
                "phase6__conflicting_and_risk_blocked_signal_regressions",
                "phase6__stale_input_and_lifecycle_transition_regressions",
            ),
        )


if __name__ == "__main__":
    unittest.main()
