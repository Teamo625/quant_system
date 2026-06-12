import unittest

from quant.features import ReadinessStatus, build_featurehub_personal_readiness_gate


class FeaturePersonalReadinessGateTestCase(unittest.TestCase):
    def test_gate_returns_expected_phase_summary(self) -> None:
        gate = build_featurehub_personal_readiness_gate()
        status_counts = {
            status_count.status: status_count.count for status_count in gate.status_counts
        }

        self.assertEqual(
            gate.phase_id,
            "Phase 3-P FeatureHub Personal Trading Perfection Re-Review",
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

    def test_capability_groups_capture_completed_featurehub_surface(self) -> None:
        gate = build_featurehub_personal_readiness_gate()
        groups = {group.group_id: group for group in gate.capability_groups}

        for group_id in (
            "price_volume_technical_core",
            "valuation_features",
            "capital_flow_money_flow_features",
            "sector_market_relative_features",
            "batch_calculation_apis",
            "persistence_and_downstream_consumability",
            "offline_test_coverage",
        ):
            self.assertEqual(groups[group_id].status, ReadinessStatus.PASS)
            self.assertEqual(groups[group_id].missing_capabilities, ())

        self.assertIn(
            "multi_feature_batch_execution",
            groups["batch_calculation_apis"].implemented_capabilities,
        )
        self.assertIn(
            "metric_identity_contract",
            groups["persistence_and_downstream_consumability"].implemented_capabilities,
        )
        self.assertIn(
            "full_phase_capability_coverage",
            groups["offline_test_coverage"].implemented_capabilities,
        )

    def test_follow_up_queue_and_batches_are_empty_after_task_142(self) -> None:
        gate = build_featurehub_personal_readiness_gate()

        self.assertEqual(gate.follow_up_queue, ())
        self.assertEqual(gate.follow_up_batches, ())

    def test_no_next_handoff_is_recommended_after_phase_closure_ready(self) -> None:
        gate = build_featurehub_personal_readiness_gate()

        self.assertEqual(gate.recommended_next_handoff_batch_id, "")
        self.assertEqual(gate.recommended_next_handoff_theme, "")


if __name__ == "__main__":
    unittest.main()
