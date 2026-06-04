import tempfile
from pathlib import Path
import unittest
from unittest import mock

from tools import run_agent_pipeline


class ReviewClassificationTests(unittest.TestCase):
    def classify(self, review_text: str) -> str:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            review = root / "TASK-999_REVIEW.md"
            review.write_text(review_text, encoding="utf-8")
            task = run_agent_pipeline.ActiveTask(
                task_id="TASK-999",
                title="test task",
                status="In Review",
                handoff=root / "handoff.md",
                report=root / "report.md",
                review=review,
                integration=root / "integration.md",
            )
            return run_agent_pipeline.classify_review_result(task)

    def test_accepts_review_with_empty_blocking_findings_section(self) -> None:
        result = self.classify(
            """# TASK-999 Review

## Findings
### Blocking findings
- None.

## Decision
- **ACCEPTED**
"""
        )

        self.assertEqual(run_agent_pipeline.REVIEW_ACCEPTED, result)

    def test_rejects_explicit_rejected_decision(self) -> None:
        result = self.classify(
            """# TASK-999 Review

## Findings
### Blocking findings
- Default tests make a hidden live network call.

## Decision
- **REJECTED**
"""
        )

        self.assertEqual(run_agent_pipeline.REVIEW_REJECTED_OR_BLOCKED, result)

    def test_rejects_changes_requested_decision(self) -> None:
        result = self.classify(
            """# TASK-999 Review

## Findings
- One blocking issue remains.

## Decision
- **CHANGES_REQUESTED**
"""
        )

        self.assertEqual(run_agent_pipeline.REVIEW_REJECTED_OR_BLOCKED, result)

    def test_accepts_non_blocking_observation_text(self) -> None:
        result = self.classify(
            """# TASK-999 Review

## Findings
### Non-blocking observations
- A follow-up would improve maintainability.

## Decision
- ACCEPTED
"""
        )

        self.assertEqual(run_agent_pipeline.REVIEW_ACCEPTED, result)


class ControllerPhaseGateTests(unittest.TestCase):
    def test_agents_phase_consistency_rejects_stale_agents_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            coordination = root / "coordination"
            coordination.mkdir()
            (root / "AGENTS.md").write_text(
                "## Phase Boundary\n\nCurrent implementation phase: Phase 3 FeatureHub.\n",
                encoding="utf-8",
            )
            (coordination / "PROJECT_STATE.md").write_text(
                "# Project State\n\n## Current Phase\n\nPhase 4: Scanner.\n",
                encoding="utf-8",
            )

            with mock.patch.object(run_agent_pipeline, "REPO_ROOT", root):
                with self.assertRaises(run_agent_pipeline.PipelineError):
                    run_agent_pipeline.ensure_agents_phase_consistent()

    def test_controller_prompt_requires_agents_update_on_phase_change(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task = run_agent_pipeline.ActiveTask(
                task_id="TASK-777",
                title="completed task",
                status="Ready",
                handoff=root / "handoff.md",
                report=root / "report.md",
                review=root / "review.md",
                integration=None,
            )

            prompt = run_agent_pipeline.controller_prompt(task)

        self.assertIn("AGENTS.md", prompt)
        self.assertIn("implementation phase", prompt)
        self.assertIn("allowed implementation target", prompt)

    def test_phase_complete_signal_uses_current_phase_gate_decision(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            coordination = root / "coordination"
            coordination.mkdir()
            project_state = coordination / "PROJECT_STATE.md"
            context_snapshot = coordination / "CONTEXT_SNAPSHOT.md"
            task_board = coordination / "TASK_BOARD.md"
            project_state.write_text(
                """# Project State

## Prior Phase Gate Decision

Phase switch: YES, to Phase 2.5.

## Phase Gate Decision

Phase 2.5 is not complete because TASK-048 remains active.

Phase switch: NO.
""",
                encoding="utf-8",
            )
            context_snapshot.write_text("Phase 2.5 is not complete.\n", encoding="utf-8")
            task_board.write_text("# Task Board\n", encoding="utf-8")

            with mock.patch.object(run_agent_pipeline, "REPO_ROOT", root), mock.patch.object(
                run_agent_pipeline, "TASK_BOARD", task_board
            ):
                self.assertFalse(run_agent_pipeline.phase_complete_signal())

    def test_check_controller_prefers_new_active_task_over_stale_phase_switch_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            coordination = root / "coordination"
            handoffs = coordination / "handoffs"
            reports = coordination / "reports"
            reviews = coordination / "reviews"
            integrations = coordination / "integrations"
            for path in [handoffs, reports, reviews, integrations]:
                path.mkdir(parents=True, exist_ok=True)

            task_board = coordination / "TASK_BOARD.md"
            project_state = coordination / "PROJECT_STATE.md"
            next_handoff = handoffs / "TASK-048_HANDOFF.md"
            next_handoff.write_text("# TASK-048\n", encoding="utf-8")

            task_board.write_text("# Task Board\n\n## Active\n\nold\n", encoding="utf-8")
            project_state.write_text("# Project State\n\nold\n", encoding="utf-8")
            before_hashes = {
                task_board: run_agent_pipeline.file_hash(task_board),
                project_state: run_agent_pipeline.file_hash(project_state),
            }

            task_board.write_text(
                """# Task Board

## Active

| Task | Title | Status | Owner | Handoff | Report | Review | Integration | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TASK-048 | Next phase 2.5 task | Ready | 5.3 execution window | `coordination/handoffs/TASK-048_HANDOFF.md` | `coordination/reports/TASK-048_REPORT.md` | `coordination/reviews/TASK-048_REVIEW.md` | `coordination/integrations/TASK-048_INTEGRATION.md` | continue |

## Backlog
""",
                encoding="utf-8",
            )
            project_state.write_text(
                """# Project State

## Prior Phase Gate Decision

Phase switch: YES, to Phase 2.5.

## Phase Gate Decision

Phase 2.5 is not complete because TASK-048 remains active.

Phase switch: NO.
""",
                encoding="utf-8",
            )

            current_task = run_agent_pipeline.ActiveTask(
                task_id="TASK-047",
                title="completed task",
                status="Ready",
                handoff=handoffs / "TASK-047_HANDOFF.md",
                report=reports / "TASK-047_REPORT.md",
                review=reviews / "TASK-047_REVIEW.md",
                integration=integrations / "TASK-047_INTEGRATION.md",
            )

            with mock.patch.object(run_agent_pipeline, "REPO_ROOT", root), mock.patch.object(
                run_agent_pipeline, "TASK_BOARD", task_board
            ):
                next_task = run_agent_pipeline.check_controller(current_task, before_hashes)

            self.assertIsNotNone(next_task)
            assert next_task is not None
            self.assertEqual("TASK-048", next_task.task_id)
            self.assertEqual(next_handoff, next_task.handoff)


class LightweightWorkflowTests(unittest.TestCase):
    def test_parse_active_task_without_integration_column(self) -> None:
        board = """# Task Board

## Active

| Task | Title | Status | Owner | Handoff | Report | Review | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TASK-777 | Lightweight task | Ready | 5.3 execution window | `coordination/handoffs/TASK-777_HANDOFF.md` | `coordination/reports/TASK-777_REPORT.md` | `coordination/reviews/TASK-777_REVIEW.md` | no integration |
"""

        task = run_agent_pipeline.parse_active_task(board)

        self.assertEqual("TASK-777", task.task_id)
        self.assertIsNone(task.integration)

    def test_standard_review_prompt_routes_directly_to_controller(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task = run_agent_pipeline.ActiveTask(
                task_id="TASK-777",
                title="lightweight task",
                status="Ready",
                handoff=root / "handoff.md",
                report=root / "report.md",
                review=root / "review.md",
                integration=None,
            )

            prompt = run_agent_pipeline.review_prompt(
                task,
                "# compact diff",
                False,
                workflow="standard",
            )

        self.assertIn("Closure Readiness", prompt)
        self.assertIn("你是5.5 Controller", prompt)
        self.assertNotIn("你是Integration Agent", prompt)

    def test_strict_review_prompt_routes_to_integration(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            task = run_agent_pipeline.ActiveTask(
                task_id="TASK-777",
                title="strict task",
                status="Ready",
                handoff=root / "handoff.md",
                report=root / "report.md",
                review=root / "review.md",
                integration=root / "integration.md",
            )

            prompt = run_agent_pipeline.review_prompt(
                task,
                "# compact diff",
                False,
                workflow="strict",
            )

        self.assertIn("你是Integration Agent", prompt)
        self.assertIn("integration.md", prompt)

    def test_default_args_use_standard_workflow_and_task_id_counting(self) -> None:
        args = run_agent_pipeline.parse_args([])

        self.assertEqual("standard", args.workflow)
        self.assertEqual("task-id", args.count_by)


if __name__ == "__main__":
    unittest.main()
