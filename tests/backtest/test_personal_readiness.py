import unittest

from quant.backtest import (
    FollowUpDisposition,
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
        self.assertFalse(gate.phase_closure_ready)
        self.assertEqual(
            status_counts,
            {
                ReadinessStatus.PASS: 5,
                ReadinessStatus.WARN: 2,
                ReadinessStatus.BLOCKED: 0,
                ReadinessStatus.FAIL: 0,
            },
        )
        self.assertEqual(
            gate.recommended_next_handoff_batch_id,
            "strategy_backtest__personal_trading_hardening__batch_03",
        )
        self.assertEqual(
            gate.recommended_next_handoff_theme,
            "comparison workflows and reproducibility regression hardening",
        )

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
            ("reproducibility_regressions",),
        )
        self.assertEqual(
            groups["result_metrics_drawdown_risk_and_report_outputs"].status,
            ReadinessStatus.PASS,
        )

    def test_follow_up_queue_and_batches_are_deterministic_and_complete(self) -> None:
        first_gate = build_strategy_backtest_personal_readiness_gate()
        second_gate = build_strategy_backtest_personal_readiness_gate()

        self.assertEqual(first_gate.follow_up_queue, second_gate.follow_up_queue)
        self.assertEqual(first_gate.follow_up_batches, second_gate.follow_up_batches)
        self.assertEqual(
            {item.follow_up_id for item in first_gate.follow_up_queue},
            {
                "phase5__multi_configuration_comparison",
                "phase5__reproducibility_and_boundary_regressions",
            },
        )
        self.assertEqual(
            {batch.batch_id for batch in first_gate.follow_up_batches},
            {"strategy_backtest__personal_trading_hardening__batch_03"},
        )
        for batch in first_gate.follow_up_batches:
            self.assertEqual(
                batch.disposition,
                FollowUpDisposition.STRATEGY_BACKTEST_HARDENING,
            )
            self.assertGreaterEqual(len(batch.item_ids), 2)

    def test_recommended_batch_matches_follow_up_items(self) -> None:
        gate = build_strategy_backtest_personal_readiness_gate()
        batches = {batch.batch_id: batch for batch in gate.follow_up_batches}
        queue_by_id = {item.follow_up_id: item for item in gate.follow_up_queue}

        recommended_batch = batches[gate.recommended_next_handoff_batch_id]
        self.assertEqual(
            recommended_batch.item_ids,
            (
                "phase5__multi_configuration_comparison",
                "phase5__reproducibility_and_boundary_regressions",
            ),
        )
        self.assertTrue(
            all(
                queue_by_id[item_id].recommended_next_handoff_theme
                == gate.recommended_next_handoff_theme
                for item_id in recommended_batch.item_ids
            )
        )


if __name__ == "__main__":
    unittest.main()
