# TASK-063: FeatureHub Output Persistence/Versioning Rework

## Task ID

TASK-063

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 3: FeatureHub

## Context

TASK-063 execution produced a FeatureHub local output persistence/versioning layer, but Review rejected closure because `write_feature_records_jsonl(...)` can partially update the records JSONL file before failing on an existing manifest path when `overwrite=False`.

This is a narrow rework handoff. Do not redo the full implementation. Fix only the Review findings and keep Phase 3 boundaries intact.

The execution window must read:

- `AGENTS.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-063_FEATUREHUB_OUTPUT_PERSISTENCE_VERSIONING.md`
- `coordination/handoffs/TASK-063_FEATUREHUB_OUTPUT_PERSISTENCE_VERSIONING_REWORK.md`
- `coordination/reports/TASK-063_REPORT.md`
- `coordination/reviews/TASK-063_REVIEW.md`
- `quant/features/storage.py`
- `tests/features/test_storage.py`

## Goal

Make the combined records-plus-manifest write path deterministic and non-partial for the Review-identified `manifest_path` conflict case, then add focused offline regression coverage.

## Allowed Files

The execution window may modify only:

- `quant/features/storage.py`
- `tests/features/test_storage.py`
- `coordination/reports/TASK-063_REPORT.md`

## Forbidden Files

The execution window must not modify:

- `coordination/PROJECT_STATE.md`
- `coordination/ROADMAP.md`
- `coordination/TASK_BOARD.md`
- `coordination/DECISIONS.md`
- `coordination/RISKS.md`
- `coordination/INTERFACES.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/reviews/**`
- `coordination/integrations/**`
- `coordination/handoffs/**`
- `quant/datahub/**`
- `quant/strategies/**`
- `quant/backtest/**`
- `quant/scanner/**`
- `quant/portfolio/**`
- `quant/notification/**`
- `quant/ai/**`
- `quant/ui/**`

## Required Rework

Address the Review findings in `coordination/reviews/TASK-063_REVIEW.md`:

1. Ensure `write_feature_records_jsonl(...)` preflights both output targets before any write, or otherwise guarantees the records JSONL file is not replaced when `manifest_path` already exists and `overwrite=False`.
2. Preserve existing behavior for valid writes, explicit `overwrite=True`, missing parent directories, malformed inputs, and manifest generation.
3. Add a focused offline test proving that an existing `manifest_path` with `overwrite=False` raises before changing the records JSONL file.

Do not widen the `FeatureValueRecord` contract and do not add batch/run lineage, partitioning, orchestration, DataHub warehouse reads, scanner ranking, strategy/backtest/signal/risk/portfolio logic, live data access, AI, notification, UI, or automated trading behavior.

## Testing Requirements

Run:

`python3 -m unittest discover -s tests/features -p 'test_*.py'`

Run DataHub default regression as requested by Review:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Default tests must remain offline-safe. No live tests are required or allowed for this rework.

## Report Requirements

Update `coordination/reports/TASK-063_REPORT.md` with:

- files changed in the rework
- tests run and results
- default network behavior
- live-enabled result as `SKIP` because TASK-063 is not a real-source task and live tests are forbidden
- deviations from this rework handoff
- risks or follow-up tasks
- explicit note that the Review-identified manifest conflict path was fixed or, if not fixed, the exact blocker

## Acceptance Criteria

The rework is acceptable when:

- `write_feature_records_jsonl(...)` no longer leaves a replaced records JSONL file behind when manifest creation is blocked by `manifest_path` already existing with `overwrite=False`
- focused offline coverage proves the conflict path
- FeatureHub and DataHub default test suites pass offline
- no DataHub implementation files or future-phase modules are changed
- the updated report truthfully records the rework and test results

## Report Path

`coordination/reports/TASK-063_REPORT.md`

## Review Path

`coordination/reviews/TASK-063_REVIEW.md`

## Integration Path

N/A until Review acceptance. Controller has not closed TASK-063 and has not requested integration.
