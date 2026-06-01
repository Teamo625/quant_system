import tempfile
from pathlib import Path
import unittest

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


if __name__ == "__main__":
    unittest.main()
