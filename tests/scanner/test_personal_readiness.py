import unittest

from quant.scanner import (
    FollowUpDisposition,
    ReadinessStatus,
    build_scanner_personal_readiness_gate,
)


class ScannerPersonalReadinessGateTestCase(unittest.TestCase):
    def test_gate_returns_expected_phase_summary(self) -> None:
        gate = build_scanner_personal_readiness_gate()
        status_counts = {
            status_count.status: status_count.count for status_count in gate.status_counts
        }

        self.assertEqual(
            gate.phase_id,
            "Phase 4-P Scanner Personal Trading Perfection Re-Review",
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
            "scanner_artifact_contract_repair_batch_01",
        )

    def test_capability_groups_capture_completed_batch_and_remaining_gaps(self) -> None:
        gate = build_scanner_personal_readiness_gate()
        groups = {group.group_id: group for group in gate.capability_groups}

        self.assertEqual(
            groups["universe_definition_and_validation"].status,
            ReadinessStatus.PASS,
        )
        self.assertEqual(
            groups["market_constraints_and_missing_data_handling"].status,
            ReadinessStatus.PASS,
        )
        self.assertEqual(
            groups["deterministic_batch_filter_evaluation"].status,
            ReadinessStatus.PASS,
        )
        self.assertEqual(
            groups["ranking_scoring_and_candidate_ordering"].status,
            ReadinessStatus.PASS,
        )
        self.assertEqual(
            groups["ranking_scoring_and_candidate_ordering"].missing_capabilities,
            (),
        )
        self.assertIn(
            "downstream_handoff_metadata",
            groups["candidate_persistence_and_handoff_readiness"].missing_capabilities,
        )
        self.assertEqual(
            groups["offline_scan_workflow_regression_coverage"].status,
            ReadinessStatus.PASS,
        )

    def test_follow_up_queue_and_batches_are_deterministic_and_complete(self) -> None:
        gate = build_scanner_personal_readiness_gate()
        follow_up_ids = {item.follow_up_id for item in gate.follow_up_queue}
        batches = {batch.batch_id: batch for batch in gate.follow_up_batches}

        self.assertEqual(
            follow_up_ids,
            {
                "SCN-ART-001",
            },
        )
        self.assertEqual(
            batches["scanner_artifact_contract_repair_batch_01"].disposition,
            FollowUpDisposition.CONTRACT_REPAIR,
        )

    def test_recommended_next_handoff_theme_matches_batch(self) -> None:
        gate = build_scanner_personal_readiness_gate()
        batches = {batch.batch_id: batch for batch in gate.follow_up_batches}
        recommended_batch = batches[gate.recommended_next_handoff_batch_id]

        self.assertEqual(
            gate.recommended_next_handoff_theme,
            "Candidate artifact schema and downstream handoff provenance",
        )
        self.assertEqual(
            recommended_batch.theme,
            "Candidate artifact schema and downstream handoff provenance",
        )


if __name__ == "__main__":
    unittest.main()
