import unittest

from quant.backtest import (
    ReadinessStatus,
    build_strategy_backtest_personal_readiness_gate,
)


class StrategyBacktestPersonalReadinessGateTestCase(unittest.TestCase):
    def test_gate_returns_expected_phase_summary(self) -> None:
        gate = build_strategy_backtest_personal_readiness_gate()
        status_counts = {
            status_count.status: status_count.count for status_count in gate.status_counts
        }

        self.assertEqual(
            gate.phase_id,
            "Phase 5 StrategyLab and BacktestEngine Personal Trading Perfection",
        )
        self.assertTrue(gate.phase_closure_ready)
        self.assertEqual(
            status_counts,
            {
                ReadinessStatus.PASS: 7,
                ReadinessStatus.WARN: 0,
                ReadinessStatus.BLOCKED: 0,
                ReadinessStatus.FAIL: 0,
            },
        )
        self.assertEqual(gate.recommended_next_handoff_batch_id, "")
        self.assertEqual(gate.recommended_next_handoff_theme, "")

    def test_capability_groups_capture_current_phase5_gaps(self) -> None:
        gate = build_strategy_backtest_personal_readiness_gate()
        groups = {group.group_id: group for group in gate.capability_groups}

        self.assertEqual(
            groups["deterministic_historical_replay_over_local_inputs"].status,
            ReadinessStatus.PASS,
        )
        self.assertEqual(
            groups["deterministic_historical_replay_over_local_inputs"].missing_capabilities,
            (),
        )
        self.assertEqual(
            groups["strategy_definition_and_starter_library"].status,
            ReadinessStatus.PASS,
        )
        self.assertEqual(
            groups["strategy_definition_and_starter_library"].missing_capabilities,
            (),
        )
        self.assertEqual(
            groups["parameter_metadata_validation_and_repeatable_experiments"].status,
            ReadinessStatus.PASS,
        )
        self.assertEqual(
            groups["parameter_metadata_validation_and_repeatable_experiments"].missing_capabilities,
            (),
        )
        self.assertEqual(
            groups["replay_assumptions_costs_fills_and_market_calendar"].status,
            ReadinessStatus.PASS,
        )
        self.assertEqual(
            groups["offline_regression_boundaries_and_reproducibility"].missing_capabilities,
            (),
        )
        self.assertEqual(
            groups["result_metrics_drawdown_risk_and_report_outputs"].status,
            ReadinessStatus.PASS,
        )
        self.assertEqual(
            groups["multi_configuration_comparison_workflows"].status,
            ReadinessStatus.PASS,
        )

    def test_follow_up_queue_and_batches_are_deterministic_and_complete(self) -> None:
        first_gate = build_strategy_backtest_personal_readiness_gate()
        second_gate = build_strategy_backtest_personal_readiness_gate()

        self.assertEqual(first_gate.follow_up_queue, second_gate.follow_up_queue)
        self.assertEqual(first_gate.follow_up_batches, second_gate.follow_up_batches)
        self.assertEqual(first_gate.follow_up_queue, ())
        self.assertEqual(first_gate.follow_up_batches, ())

    def test_recommended_batch_is_empty_after_phase5_closure_readiness(self) -> None:
        gate = build_strategy_backtest_personal_readiness_gate()

        self.assertEqual(gate.recommended_next_handoff_batch_id, "")
        self.assertEqual(gate.recommended_next_handoff_theme, "")


if __name__ == "__main__":
    unittest.main()
