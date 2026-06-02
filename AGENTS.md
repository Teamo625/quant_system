# quant_system Agent Rules

This repository is a personal A-share, Hong Kong stock, and ETF quantitative research and signal system.

The project is intentionally built in phases. The current allowed implementation scope is DataHub Phase 2.5 source-capability work only. All other modules exist as architecture placeholders until the project owner explicitly opens their phase.

## Role Rules

### 5.5 Controller Window

The 5.5 controller window is the only role allowed to update project coordination state.

Only the controller may edit:

- `coordination/PROJECT_STATE.md`
- `coordination/ROADMAP.md`
- `coordination/TASK_BOARD.md`
- `coordination/DECISIONS.md`
- `coordination/RISKS.md`
- `coordination/INTERFACES.md`
- `coordination/CONTEXT_SNAPSHOT.md`

The controller is responsible for:

- decomposing work into handoff files
- accepting or rejecting execution results
- updating project truth after review
- keeping phase boundaries intact
- preventing scope creep into future modules
- when live-enabled source smoke fails or skips because of network, proxy, DNS, TLS, upstream, or source availability issues, dispatching an explicit execution rework and requiring a fresh review cycle before closing the task

### 5.3 Execution Window

Execution windows implement exactly one handoff at a time.

Execution windows must:

- read `AGENTS.md` first
- read the assigned file in `coordination/handoffs/`
- modify only files explicitly allowed by the handoff
- run only tests allowed by the handoff and testing policy
- write a completion report in `coordination/reports/`
- for assigned live-network failure reworks, diagnose the failure and modify allowed code/tests/report where feasible instead of only documenting the failure

Execution windows must not edit:

- `coordination/PROJECT_STATE.md`
- `coordination/ROADMAP.md`
- `coordination/TASK_BOARD.md`
- `coordination/DECISIONS.md`
- `coordination/RISKS.md`
- `coordination/INTERFACES.md`
- `coordination/CONTEXT_SNAPSHOT.md`

### Review Agent

The review agent checks whether an execution report and code changes satisfy the handoff.

The review agent should focus on:

- violations of phase scope
- hidden live network calls in default tests
- live-enabled source smoke failures or skips, including whether root-cause evidence and feasible fixes are sufficient
- incorrect data contracts
- maintainability risks
- missing or weak tests

The review agent should not introduce new implementation work unless explicitly asked.

Hard rules:

- Review conclusions must be written to `coordination/reviews/{TASK_ID}_REVIEW.md`.
- Chat replies may be brief, but the key findings, decision, closure readiness, and follow-up requirements must be recorded in the local review file.
- By default, Review is the closure gate before Controller. The review file must say whether Controller closure is allowed, whether default tests are offline-safe, what the live-enabled result is for real-source work, and whether rework is required.

### Integration Agent

The integration agent is optional and used only when explicitly requested by the controller, by a strict pipeline run, or by the project owner.

When used, the integration agent must not change architectural direction. It may only integrate accepted work and report conflicts or gaps.

Rules when used:

- Integration results must be written to `coordination/integrations/{TASK_ID}_INTEGRATION.md`.
- Chat replies may be brief, but the key integration result, conflicts, files touched, and state-update recommendations must be recorded in the local integration file.

## Phase Boundary

Current implementation phase: Phase 2.5 DataHub Trading-Grade Source Capability.

Allowed implementation target:

- `quant/datahub/`
- `tests/datahub/`

Placeholder-only modules:

- `quant/strategies/`
- `quant/backtest/`
- `quant/scanner/`
- `quant/portfolio/`
- `quant/notification/`
- `quant/ai/`
- `quant/ui/`

Do not implement scanner ranking, trading strategies, backtest execution, portfolio/signal/risk logic, AI reports, push notifications, automated trading, or complex UI until the corresponding phase is opened by the controller.

## Data and Network Rules

Default tests must not perform real network calls.

Live data tests are allowed only when:

- the test is explicitly marked as live
- an environment variable enables it
- the handoff explicitly permits it

For real-source adapter or real data-fetching tasks, live smoke coverage is mandatory even though it must remain skipped by default. Phase 2.5 tasks must build source capability, contracts, adapters, and validation without implementing scanner, strategy, signal, risk, portfolio, AI, notification, UI, or automated trading logic.

When an explicitly enabled live smoke test fails or skips due to network, proxy, DNS, TLS, upstream, or public-source availability:

- the controller must not accept or close the task solely from the failed/skipped live result
- the next step must be a handoff to a 5.3 execution window to diagnose the failure and fix repository code/tests where feasible
- the execution report must record PASS, SKIP, or FAIL truthfully with root-cause evidence and any operator action needed
- a Review Agent must independently review the rework before controller closure
- an optional Integration Agent may integrate only after the review result is accepted

No credentials, tokens, cookies, or private account data may be committed.

## Engineering Rules

- Prefer small, reviewable changes.
- Keep module boundaries explicit.
- Write interfaces before implementation when crossing module boundaries.
- Use local fixtures for default tests.
- Record stable interface changes in `coordination/INTERFACES.md`; controller only.
- Record architectural decisions in `coordination/DECISIONS.md`; controller only.
- Record material risks in `coordination/RISKS.md`; controller only.
- Refresh compressed context in `coordination/CONTEXT_SNAPSHOT.md`; controller only.

## Completion Rules

Every execution handoff must end with a report under `coordination/reports/`.

Every review must end with a review file under `coordination/reviews/`.

Every optional integration pass must end with an integration file under `coordination/integrations/`.

Naming convention:

- handoffs: `coordination/handoffs/TASK-xxx_*.md`
- reports: `coordination/reports/TASK-xxx_REPORT.md`
- reviews: `coordination/reviews/TASK-xxx_REVIEW.md`
- optional integrations: `coordination/integrations/TASK-xxx_INTEGRATION.md`

The report must include:

- files changed
- tests run
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence for real-source tasks
- deviations from the handoff
- risks or follow-up tasks
