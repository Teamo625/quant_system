# Phase Gate Policy

## Purpose
Provide a reusable decision policy for the controller:
1) evaluate whether current phase is complete
2) branch to next task in current phase OR open next phase

## Controller Inputs
- AGENTS.md
- coordination/ROADMAP.md
- coordination/TASK_BOARD.md
- coordination/PROJECT_STATE.md
- coordination/CONTEXT_SNAPSHOT.md
- current task review/integration files

## Completion Check (Generic)
A phase is considered complete only if all are true:

1. All tasks labeled for the current phase are `Done`.
2. No task of the current phase remains in:
   - `Ready`
   - `In Progress`
   - `In Review`
   - `Ready to Integrate`
3. Each phase task has full lifecycle artifacts:
   - handoff
   - report
   - review
   - integration
4. No phase task has review result `Rejected` or unresolved blocking findings.
5. Any real-source task with a live-enabled network/proxy/DNS/TLS/upstream failure or skip has a completed execution rework, accepted review, and integration result for the diagnosis/fix before it is counted as done.

## Branching Rule
If phase complete:
- switch PROJECT_STATE current phase to next phase
- update ROADMAP status:
  - current phase -> `Completed`
  - next phase -> `In progress`
- set first next-phase task to `Ready`
- create next-phase handoff file
- update CONTEXT_SNAPSHOT

If phase not complete:
- stay in current phase
- create/assign next executable task in current phase
- update TASK_BOARD / PROJECT_STATE / CONTEXT_SNAPSHOT

## Required Outputs Per Decision
Controller must write:
- coordination/TASK_BOARD.md
- coordination/PROJECT_STATE.md
- coordination/CONTEXT_SNAPSHOT.md
- coordination/ROADMAP.md
- coordination/handoffs/{HANDOFF_FILE}.md

## Response Contract (chat)
Controller should return exactly one mode:
- `PHASE_SWITCHED_TO_<PHASE_NAME>` + handoff filename
- `STAY_IN_<PHASE_NAME>` + reason + handoff filename
