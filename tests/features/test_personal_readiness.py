import unittest

from quant.features import (
    FollowUpDisposition,
    ReadinessStatus,
    build_featurehub_personal_readiness_gate,
)


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
        self.assertFalse(gate.phase_closure_ready)
        self.assertEqual(
            status_counts,
            {
                ReadinessStatus.PASS: 3,
                ReadinessStatus.WARN: 4,
                ReadinessStatus.BLOCKED: 0,
                ReadinessStatus.FAIL: 0,
            },
        )

    def test_capability_groups_capture_current_featurehub_gaps(self) -> None:
        gate = build_featurehub_personal_readiness_gate()
        groups = {group.group_id: group for group in gate.capability_groups}

        technical_group = groups["price_volume_technical_core"]
        self.assertEqual(technical_group.status, ReadinessStatus.PASS)
        self.assertEqual(
            technical_group.implemented_capabilities,
            (
                "atr",
                "bollinger_bands",
                "ema",
                "gap_breakout_primitives",
                "kdj_or_stochastic",
                "macd",
                "moving_averages",
                "returns",
                "rolling_window_helpers",
                "rsi",
                "volatility",
                "volume_turnover_liquidity",
            ),
        )
        self.assertEqual(technical_group.missing_capabilities, ())

        valuation_group = groups["valuation_features"]
        self.assertEqual(valuation_group.status, ReadinessStatus.PASS)
        self.assertIn("pe_pb_ps_style_values", valuation_group.implemented_capabilities)
        self.assertIn("valuation_percentiles", valuation_group.implemented_capabilities)
        self.assertEqual(valuation_group.missing_capabilities, ())

        flow_group = groups["capital_flow_money_flow_features"]
        self.assertEqual(flow_group.status, ReadinessStatus.PASS)
        self.assertIn("fund_flow_levels", flow_group.implemented_capabilities)
        self.assertIn("rolling_changes", flow_group.implemented_capabilities)
        self.assertEqual(flow_group.missing_capabilities, ())

        persistence_group = groups["persistence_and_downstream_consumability"]
        self.assertEqual(persistence_group.status, ReadinessStatus.WARN)
        self.assertIn("metric_identity_contract", persistence_group.missing_capabilities)
        self.assertTrue(
            any("TASK-063" in evidence for evidence in persistence_group.evidence)
        )

    def test_follow_up_queue_and_batches_are_controller_ready(self) -> None:
        gate = build_featurehub_personal_readiness_gate()
        queue_by_id = {item.follow_up_id: item for item in gate.follow_up_queue}
        batch_item_ids = {
            follow_up_id
            for batch in gate.follow_up_batches
            for follow_up_id in batch.item_ids
        }

        self.assertEqual(set(queue_by_id), batch_item_ids)
        self.assertEqual(len(queue_by_id), 5)
        self.assertNotIn("FH-VAL-001", queue_by_id)
        self.assertNotIn("FH-FLOW-001", queue_by_id)

        for batch in gate.follow_up_batches:
            if batch.disposition is FollowUpDisposition.FEATUREHUB_HARDENING:
                self.assertGreaterEqual(len(batch.item_ids), 2)

        self.assertEqual(
            queue_by_id["FH-BATCH-001"].disposition,
            FollowUpDisposition.CONTRACT_REPAIR,
        )
        self.assertEqual(
            queue_by_id["FH-CONTRACT-001"].capability_group_id,
            "persistence_and_downstream_consumability",
        )

    def test_next_handoff_recommendation_targets_relative_features(self) -> None:
        gate = build_featurehub_personal_readiness_gate()
        batch_ids = {batch.batch_id for batch in gate.follow_up_batches}

        self.assertEqual(
            gate.recommended_next_handoff_batch_id,
            "featurehub_relative_features_batch_01",
        )
        self.assertIn(gate.recommended_next_handoff_batch_id, batch_ids)
        self.assertIn("sector-relative", gate.recommended_next_handoff_theme.lower())
        self.assertIn("market-relative", gate.recommended_next_handoff_theme.lower())


if __name__ == "__main__":
    unittest.main()
