# Task Protocol

This project uses separated agent roles to keep a large project controlled and reviewable.

## Roles

### 5.5 Controller

The controller is the planning and state authority.

Responsibilities:

- maintain project state
- maintain compressed context snapshots
- update roadmap and task board
- create handoff files
- decide whether work is accepted
- record architecture decisions and risks
- open or close project phases

The controller is the only role allowed to edit coordination state files.

### 5.3 Execution Window

Execution windows are implementation workers.

Responsibilities:

- read `AGENTS.md`
- read one assigned handoff
- implement only the assigned scope
- run allowed tests
- write one report in `coordination/reports/`

Execution windows must not update project truth files.

They may use `coordination/CONTEXT_SNAPSHOT.md` as a quick-start summary, but must verify task-specific details against the assigned handoff and authoritative coordination files.

### Review Agent

The review agent checks implementation against the handoff and project rules.

Review output should include:

- blocking findings
- non-blocking findings
- test gaps
- phase-boundary concerns
- accept or reject recommendation

Review conclusions must be written to `coordination/reviews/{TASK_ID}_REVIEW.md`. Chat replies may be brief, but key conclusions must be persisted in the local review file.

### Integration Agent

The integration agent applies accepted work to the main project line when instructed.

Integration must preserve controller state and report unresolved conflicts.

Integration results must be written to `coordination/integrations/{TASK_ID}_INTEGRATION.md`. Chat replies may be brief, but key conclusions must be persisted in the local integration file.

## Standard Workflow

1. Controller creates or updates a handoff file in `coordination/handoffs/`.
2. User opens a fresh 5.3 execution window.
3. Execution window reads `AGENTS.md` and the handoff.
4. Execution window implements the assigned scope.
5. Execution window runs allowed tests.
6. Execution window writes a report in `coordination/reports/`.
7. Review agent reviews changed files and report.
8. Review agent writes a review file in `coordination/reviews/`.
9. Integration agent integrates accepted work when instructed.
10. Integration agent writes an integration file in `coordination/integrations/`.
11. Controller updates project state, task board, decisions, risks, and interfaces when appropriate.

Lifecycle:

`handoff -> execution report -> review file -> integration file -> controller state update`

## Live Network Failure Rework

If a real-source adapter or real data-fetching task has a live-enabled smoke result that fails or skips because of network, proxy, DNS, TLS, upstream, or public-source availability, the project must use the normal separated-role lifecycle rather than closing the issue inside the controller window.

Required flow:

1. Controller keeps the task open and writes an explicit rework handoff.
2. A 5.3 execution window diagnoses the failure and modifies only the files allowed by the rework handoff.
3. The execution report records root-cause evidence, the fix made or why no repository-level fix is feasible, and the exact live-enabled PASS/SKIP/FAIL result.
4. Review Agent independently reviews the rework and decides Accepted, Changes Requested, or Rejected.
5. Integration Agent integrates only after accepted review.
6. Controller updates project truth only after review/integration artifacts exist.

The controller must not treat a live-enabled network skip as task completion unless that skip has been diagnosed by execution, accepted by review, and integrated according to the handoff.

## Naming Convention

- handoffs: `coordination/handoffs/TASK-xxx_*.md`
- reports: `coordination/reports/TASK-xxx_REPORT.md`
- reviews: `coordination/reviews/TASK-xxx_REVIEW.md`
- integrations: `coordination/integrations/TASK-xxx_INTEGRATION.md`

## Handoff File Template

Each handoff should include:

- task id
- title
- owner role
- status
- context
- goal
- allowed files
- forbidden files
- implementation requirements
- testing requirements
- acceptance criteria
- report path
- review path
- integration path
- out-of-scope items

## Report File Template

Each execution report should include:

- task id
- summary
- files changed
- tests run
- network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence for real-source tasks
- deviations from handoff
- risks
- suggested follow-ups

## Review File Template

Each review file should include:

- task id
- reviewed handoff path
- reviewed report path
- reviewed files or change summary
- blocking findings
- non-blocking findings
- test gaps
- live-source failure diagnosis and whether feasible fixes were made for real-source tasks
- phase-boundary concerns
- recommendation: accept, reject, or request changes
- required follow-ups

## Integration File Template

Each integration file should include:

- task id
- reviewed handoff path
- reviewed report path
- reviewed review path
- integration decision
- files integrated or intentionally left unchanged
- conflicts or gaps
- controller state update recommendations
- risks or follow-up tasks

## State Discipline

`PROJECT_STATE.md`, `ROADMAP.md`, and `TASK_BOARD.md` describe project truth. They must not be treated as scratchpads.

Execution windows may read them but must not modify them.

`coordination/CONTEXT_SNAPSHOT.md` is a controller-maintained compressed summary for single-role continuation windows. It is useful for fast context recovery, but it is not a replacement for authoritative project state, task board, roadmap, interfaces, decisions, risks, or handoff files.
