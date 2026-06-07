# quant_system Agent Rules

This repository is a personal A-share, Hong Kong stock, and ETF quantitative research and signal system.

The project is intentionally built in phases. The current allowed implementation scope is Phase 2.5-P DataHub Personal Trading Perfection Re-Review only. Downstream modules remain inactive until the controller explicitly reopens their phase after prerequisite hardening.

Global phase closure standard: every phase must reach the strongest practical public-source/no-paid completeness for personal quantitative trading use before it can be treated as finally complete. Foundation slices, partial capabilities, representative examples, one-symbol/one-fund/one-route demos, contract-only work, or narrow smoke paths may close individual tasks, but must not close a phase. Paid/private data requirements are outside the current required implementation scope only when explicitly recorded as blocked and accepted by the owner.

## Role Rules

### Agent Pipeline Invocation

When the project owner asks to run the agent pipeline, the active assistant must invoke the local runner:

- `python3 tools/run_agent_pipeline.py ...`

Do not manually simulate the pipeline in the current app conversation. Do not directly perform Execution, Review, or Controller work for a pipeline run unless the owner explicitly asks for a one-off manual intervention instead of running the pipeline.

Pipeline child roles must not run `git add`, `git commit`, `git reset`, `git checkout`, or other git state-changing commands. Git checkpoint commits are owned by `tools/run_agent_pipeline.py` after a task has fully completed Execution -> Review -> Controller.

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
- updating this `AGENTS.md` phase boundary whenever the controller opens a new implementation phase
- keeping phase boundaries intact
- preventing scope creep into future modules
- enforcing the Personal Trading Perfection Standard in `coordination/ROADMAP.md` and `coordination/PHASE_GATE.md`
- rejecting phase closure based only on foundation, partial, representative, narrow, or demo-grade completion
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

- `AGENTS.md`
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
- attempts to treat partial, foundation-only, representative, or demo-grade work as phase-complete

The review agent should not introduce new implementation work unless explicitly asked.

Hard rules:

- Review conclusions must be written to `coordination/reviews/{TASK_ID}_REVIEW.md`.
- Chat replies may be brief, but the key findings, decision, closure readiness, and follow-up requirements must be recorded in the local review file.
- By default, Review is the closure gate before Controller. The review file must say whether Controller closure is allowed, whether default tests are offline-safe, what the live-enabled result is for real-source work, and whether rework is required.

### Integration Agent

The Integration Agent is retired. New pipeline runs must use:

`handoff -> Execution -> Review -> Controller`

Do not dispatch, simulate, or require an Integration Agent for new work. Historical integration files under `coordination/integrations/` remain archival evidence only and are not part of the active workflow.

## Phase Boundary

Current implementation phase: Phase 2.5-P DataHub Personal Trading Perfection Re-Review.

Allowed implementation target:

- `quant/datahub/`
- `tests/datahub/`

Inactive modules until their phase is reopened by the controller:

- `quant/features/`
- `quant/scanner/`
- `quant/strategies/`
- `quant/backtest/`
- `quant/portfolio/`
- `quant/notification/`
- `quant/ai/`
- `quant/ui/`

Do not implement FeatureHub indicators, scanner ranking, trading strategies, backtest execution, portfolio/signal/risk logic, AI reports, push notifications, automated trading, or complex UI until the corresponding phase or sub-scope is reopened by the controller. In the current Phase 2.5-P scope, DataHub work must be limited to personal trading perfection re-review gates and explicitly dispatched hardening handoffs across existing DataHub domains; an audit-only or re-review handoff must not change DataHub source adapters unless the handoff explicitly allows it.

All current and future phases, including historically completed foundation phases, must be re-reviewed against the Personal Trading Perfection Standard before downstream phases may rely on them as final. The current TASK-093 gate is the DataHub entry point for that re-review.

## Data and Network Rules

Default tests must not perform real network calls.

Live data tests are allowed only when:

- the test is explicitly marked as live
- an environment variable enables it
- the handoff explicitly permits it

For real-source adapter or real data-fetching tasks, live smoke coverage is mandatory even though it must remain skipped by default. Phase 2.5-P tasks must audit or harden DataHub personal trading perfection without implementing FeatureHub, Scanner, StrategyLab, BacktestEngine, signal, risk, portfolio, AI, notification, UI, or automated trading logic. Paid or private-credential requirements must be classified as blocked unless the owner explicitly provides credentials and opens that scope.

When an explicitly enabled live smoke test fails or skips due to network, proxy, DNS, TLS, upstream, or public-source availability:

- the controller must not accept or close the task solely from the failed/skipped live result
- the next step must be a handoff to a 5.3 execution window to diagnose the failure and fix repository code/tests where feasible
- the execution report must record PASS, SKIP, or FAIL truthfully with root-cause evidence and any operator action needed
- a Review Agent must independently review the rework before controller closure
- controller closure may proceed directly after Review acceptance

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

Integration passes are retired and must not be required for new work.

Naming convention:

- handoffs: `coordination/handoffs/TASK-xxx_*.md`
- reports: `coordination/reports/TASK-xxx_REPORT.md`
- reviews: `coordination/reviews/TASK-xxx_REVIEW.md`
- historical integrations: `coordination/integrations/TASK-xxx_INTEGRATION.md` (archival only)

The report must include:

- files changed
- tests run
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence for real-source tasks
- deviations from the handoff
- risks or follow-up tasks
