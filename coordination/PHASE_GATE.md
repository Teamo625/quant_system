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
- current task report/review files
- optional current task integration file when strict workflow was used

## Completion Check (Generic)
A phase is considered complete only if all are true:

1. The phase satisfies the trading-usable completion standard in `coordination/ROADMAP.md`.
   Foundation slices, representative examples, contract-only tasks, or one-symbol/one-fund/one-route demonstrations are not enough by themselves.
2. The Controller has explicitly reviewed the phase's capability breadth, workflow depth, tests, operational constraints, and unresolved limitations against the roadmap standard.
3. All tasks labeled for the current phase are `Done`.
4. No task of the current phase remains in:
   - `Ready`
   - `In Progress`
   - `In Review`
   - `Ready to Integrate`
5. Each phase task has full lifecycle artifacts:
   - handoff
   - report
   - review
6. No phase task has review result `Rejected` or unresolved blocking findings.
7. Each review file includes closure readiness and explicitly states whether Controller closure is allowed.
8. Any real-source task with a live-enabled network/proxy/DNS/TLS/upstream failure or skip has a completed execution rework and accepted review for the diagnosis/fix before it is counted as done. Optional strict-mode integration may be required only when the controller or owner explicitly requests it.
9. Any external limitation, paid credential requirement, upstream data gap, or intentionally deferred capability has an explicit owner-approved exception. Without that exception, the phase remains incomplete.

## Trading-Usable Completion Standard

The project target is not merely to connect module skeletons. A phase may pass only when it reaches the best practical trading-usable completeness for its scope.

For controller decisions, "trading-usable" means:

- a real personal quant workflow can rely on the phase output without hidden manual patching
- the phase covers the core breadth needed for A-share, Hong Kong stock, and ETF/fund research within its module responsibility
- the phase covers both short-term and medium/long-term research needs where applicable
- outputs are validated, deterministic, documented, and consumable by downstream modules
- default tests are offline-safe and cover success, invalid input, boundary, and regression cases
- live/source-dependent capabilities have gated live evidence when the phase uses real sources
- known limitations are either fixed, blocked with root-cause evidence, or explicitly waived by the owner

Controller must treat "foundation complete" as an intermediate milestone, not as phase completion, unless the roadmap explicitly defines that phase as foundation-only.

## Controller Capability Audit

Before switching phase, Controller must write or update the phase decision narrative in `coordination/PROJECT_STATE.md` and `coordination/CONTEXT_SNAPSHOT.md` with:

- the roadmap completion standard being applied
- which required capability groups are satisfied
- which tests or live-smoke evidence prove the phase is usable
- which limitations remain and whether each is fixed, blocked, or owner-waived
- why no further current-phase expansion handoff is required

If the roadmap lacks a concrete completion checklist for the current phase, Controller must not switch phase. It must first dispatch a roadmap/completion-audit handoff or update the roadmap itself in the controller window.

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
- create/assign the next executable task in current phase that closes the highest-priority gap against the trading-usable completion standard
- update TASK_BOARD / PROJECT_STATE / CONTEXT_SNAPSHOT

If a prior phase was previously marked complete under a weaker foundation-only standard and the current phase depends on missing prior-phase capability:
- reopen or dispatch the earliest prerequisite capability-expansion task before adding more downstream work
- record the reason in PROJECT_STATE / CONTEXT_SNAPSHOT
- update AGENTS.md to the reopened phase and allowed implementation target
- move any downstream Active task back to Backlog as deferred or blocked by prerequisite hardening
- do not mark the downstream phase complete until the prerequisite gap is closed or explicitly owner-waived

## Required Outputs Per Decision
Controller must write:
- AGENTS.md when the current implementation phase or allowed implementation target changes
- coordination/TASK_BOARD.md
- coordination/PROJECT_STATE.md
- coordination/CONTEXT_SNAPSHOT.md
- coordination/ROADMAP.md
- coordination/handoffs/{HANDOFF_FILE}.md

## Response Contract (chat)
Controller should return exactly one mode:
- `PHASE_SWITCHED_TO_<PHASE_NAME>` + handoff filename
- `STAY_IN_<PHASE_NAME>` + reason + handoff filename
- `REOPENED_PRIOR_PHASE_<PHASE_NAME>` + reason + handoff filename
