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

## Completion Check (Generic)
A phase is considered complete only if all are true:

1. The phase satisfies the Personal Trading Perfection Standard in `coordination/ROADMAP.md`.
   Foundation slices, representative examples, contract-only tasks, one-symbol/one-fund/one-route demonstrations, or `partial` capability states are not enough by themselves.
2. The Controller has explicitly reviewed the phase's capability breadth, workflow depth, tests, operational constraints, unresolved limitations, and public-source/no-paid completeness against the roadmap standard.
3. All tasks labeled for the current phase are `Done`.
4. No task of the current phase remains in:
   - `Ready`
   - `In Progress`
   - `In Review`
5. Each phase task has full lifecycle artifacts:
   - handoff
   - report
   - review
6. No phase task has review result `Rejected` or unresolved blocking findings.
7. Each review file includes closure readiness and explicitly states whether Controller closure is allowed.
8. Any real-source task with a live-enabled network/proxy/DNS/TLS/upstream failure or skip has a completed execution rework and accepted review for the diagnosis/fix before it is counted as done.
9. Any external limitation, paid credential requirement, upstream data gap, or intentionally deferred capability has an explicit owner-approved exception. Without that exception, the phase remains incomplete.
10. The phase has no unresolved `fail`, no unexplained `partial`, and no silent public-source limitation in the Controller decision matrix.
11. Paid/private data requirements are outside the current required implementation scope only when they are explicitly recorded as `blocked` and the owner has accepted the public-source/no-paid perfection scope for the phase.

## Personal Trading Perfection Standard

The project target is not merely to connect module skeletons. A phase may pass only when it reaches the strongest practical public-source completeness for personal quantitative trading use within its module responsibility.

For controller decisions, "personally trading-perfect" means:

- a real personal quant workflow can rely on the phase output without hidden manual patching
- the phase covers the full practical public-source breadth needed for A-share, Hong Kong stock, ETF/fund, index, sector, macro/policy, and downstream personal research workflows within its module responsibility
- the phase covers both short-term and medium/long-term research needs where applicable
- outputs are validated, deterministic, documented, and consumable by downstream modules
- default tests are offline-safe and cover success, invalid input, boundary, and regression cases
- live/source-dependent capabilities have gated live evidence when the phase uses real sources
- known limitations are either fixed, classified as `warn` / `blocked` with root-cause evidence, or explicitly waived by the owner
- no `partial` capability is treated as complete without an explicit owner-accepted explanation and follow-up disposition
- no phase can close from only representative, foundational, narrow, or demo-grade coverage

Controller must treat "foundation complete" as an intermediate milestone, not as phase completion. Historical foundation-complete phases must be re-reviewed under this standard before downstream work may rely on them as complete.

## Controller Capability Audit

Before switching phase, Controller must write or update the phase decision narrative in `coordination/PROJECT_STATE.md` and `coordination/CONTEXT_SNAPSHOT.md` with:

- the roadmap completion standard being applied
- which required capability groups are satisfied
- which tests or live-smoke evidence prove the phase is usable
- which limitations remain and whether each is fixed, `warn`, `blocked`, or owner-waived
- why every public-source feasible capability has reached the strongest practical personal-use completeness
- why any remaining `partial` state is not being treated as completion
- why no further current-phase expansion handoff is required

If the roadmap lacks a concrete completion checklist for the current phase, Controller must not switch phase. It must first dispatch a roadmap/completion-audit handoff or update the roadmap itself in the controller window.

## Task Granularity Policy

Default Controller handoffs should cover a coherent capability cluster, not one narrow capability item. For ordinary current-phase hardening, the preferred handoff size is 2-6 related capability or follow-up items that share a domain, disposition, source family, data contract theme, or workflow depth.

Controller should split work into a single-item or very small handoff only when batching would reduce safety or clarity, including:

- Review rework
- live FAIL/SKIP diagnosis or source-availability repair
- paid credential or owner-waiver blockers
- cross-phase or inactive-module boundaries
- multiple unrelated domains with no common implementation surface
- schema or contract changes with high blast-radius risk

When the phase is not complete, Controller should prefer DataHub readiness `follow_up_batches` as the next dispatch source. If `follow_up_batches` is unavailable, Controller should merge adjacent `follow_up_queue` items that are same-domain, same-disposition, or same-theme into a coherent cluster.

If Controller dispatches a single ordinary hardening item while compatible follow-up items remain, it must record the reason batching is not appropriate in `coordination/PROJECT_STATE.md` and `coordination/CONTEXT_SNAPSHOT.md`.

Historical handoffs, reports, reviews, and task-board entries are not rewritten for this policy. Current Active work is not forcibly expanded; this policy applies to new Controller dispatches after the current task closes.

## Branching Rule
If phase complete:
- switch PROJECT_STATE current phase to next phase
- update ROADMAP status:
  - current phase -> `Personal Trading Perfection Complete`
  - next phase -> `In progress`
- set first next-phase task to `Ready`
- create next-phase handoff file
- update CONTEXT_SNAPSHOT

If phase not complete:
- stay in current phase
- create/assign the next executable capability cluster in current phase that closes the highest-priority gap against the Personal Trading Perfection Standard
- update TASK_BOARD / PROJECT_STATE / CONTEXT_SNAPSHOT

If a prior phase was previously marked complete under a weaker foundation-only, representative, or trading-usable-partial standard and the current phase depends on missing prior-phase capability:
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
