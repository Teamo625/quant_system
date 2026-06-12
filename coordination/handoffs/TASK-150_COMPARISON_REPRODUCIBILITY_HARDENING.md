# TASK-150 Comparison workflows and reproducibility regression hardening

## Role

5.3 Execution Window.

## Phase

Phase 5 StrategyLab and BacktestEngine Personal Trading Perfection.

## Context

TASK-149 is closed after accepted Review Agent verification of local/offline replay assumptions, market rules, metrics, and report-ready output hardening. It closed Phase 5 readiness batch `strategy_backtest__personal_trading_hardening__batch_02`:

- `phase5__replay_assumptions_and_market_rules`
- `phase5__metrics_and_report_outputs`

The current local Phase 5 readiness gate now reports:

- `phase_closure_ready=false`
- status counts: `pass=5`, `warn=2`, `blocked=0`, `fail=0`
- remaining batch: `strategy_backtest__personal_trading_hardening__batch_03`

Controller read the readiness `follow_up_batches`. The next executable current-phase capability cluster is:

- batch id: `strategy_backtest__personal_trading_hardening__batch_03`
- theme: comparison workflows and reproducibility regression hardening
- follow-up items:
  - `phase5__multi_configuration_comparison`
  - `phase5__reproducibility_and_boundary_regressions`

This is a two-item coherent Phase 5 cluster. It is dispatched together because comparison workflows need deterministic regression coverage so repeated offline research runs do not depend on manual orchestration or hidden data patching.

## Objective

Add deterministic offline multi-configuration comparison workflows and broaden reproducibility regression coverage enough for repeated personal strategy research over caller-provided local inputs and already-built local replay/report objects.

The implementation must remain local/offline. It must not fetch data, read the warehouse, call DataHub/FeatureHub/Scanner, create live trading signals, or implement portfolio/signal/risk modules.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-150_COMPARISON_REPRODUCIBILITY_HARDENING.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/ROADMAP.md`
- `coordination/PHASE_GATE.md`
- `coordination/reports/TASK-147_REPORT.md`
- `coordination/reviews/TASK-147_REVIEW.md`
- `coordination/reports/TASK-148_REPORT.md`
- `coordination/reviews/TASK-148_REVIEW.md`
- `coordination/reports/TASK-149_REPORT.md`
- `coordination/reviews/TASK-149_REVIEW.md`
- `quant/backtest/`
- `quant/strategies/`
- `tests/backtest/`
- `tests/strategies/`

Read Scanner/FeatureHub/DataHub contracts only if needed to preserve accepted caller-provided input reference semantics. Do not change Scanner, FeatureHub, or DataHub files.

## Allowed Writes

Only:

- `quant/backtest/**`
- `tests/backtest/**`
- `quant/strategies/**` only if needed for compatibility with existing starter strategy metadata
- `tests/strategies/**` only if needed for that compatibility
- `coordination/reports/TASK-150_REPORT.md`

Suggested implementation areas:

- `quant/backtest/comparison.py` or similarly scoped module for deterministic comparison contracts/workflows
- `quant/backtest/contracts.py` for narrowly scoped comparison dataclasses or validation helpers if needed
- `quant/backtest/experiments.py` only if comparison must consume repeatable experiment config identity
- `quant/backtest/personal_readiness.py` for truthful readiness updates
- focused exports in `quant/backtest/__init__.py` if needed
- focused tests under `tests/backtest/`

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files other than `coordination/reports/TASK-150_REPORT.md`
- `coordination/reviews/**`
- `coordination/integrations/**`
- `coordination/handoffs/**`
- `quant/datahub/**`
- `tests/datahub/**`
- `quant/features/**`
- `tests/features/**`
- `quant/scanner/**`
- `tests/scanner/**`
- `quant/portfolio/**`
- `quant/notification/**`
- `quant/ai/**`
- `quant/ui/**`

Do not fetch live data, call source adapters, read local warehouse state, use credentials, operate browser/session state, or introduce hidden network behavior.

Do not implement production portfolio/signal/risk logic, live execution, AI reports, notifications, automated trading, or UI.

## Implementation Requirements

### Multi-Configuration Comparison

Add first-class deterministic comparison support for multiple local strategy/backtest configurations.

At minimum:

- accept caller-provided repeatable experiment configs, replay results, replay reports, normalized report payloads, or similarly local BacktestEngine objects; do not read external artifacts unless an existing safe local reference pattern is already available and validation is explicit
- provide stable comparison run identity or digest from normalized inputs
- support at least two configurations/results and reject empty, single-entry, duplicate-id, mismatched-window, mismatched-baseline-capital, or non-comparable payloads through controlled validation issues
- produce a serialization-friendly comparison summary with deterministic ordering, rank keys, metric deltas, and per-configuration summary rows
- keep comparison metrics tied to already-computed replay/report metrics; do not invent source data, adjustment factors, trading calendars, or risk/portfolio state
- make tie-breaking deterministic and documented in code/tests
- preserve backwards compatibility for existing replay, report, and experiment contracts unless a schema-safe extension is clearly justified

### Reproducibility and Boundary Regression Coverage

Broaden default offline regression coverage around repeated research runs.

At minimum:

- prove repeated comparison builds over the same normalized inputs produce identical identities, ordering, and payloads
- prove input order does not change deterministic comparison ranking except for documented tie-breakers
- cover invalid comparison configs and boundary cases such as mismatched date windows, stale or duplicated experiment ids, missing report metrics, and non-finite metric values
- cover corporate-action/source assumption propagation into comparison summaries where replay reports expose those assumptions
- cover report/reference serialization shape enough for later Controller closure decisions
- keep tests offline-safe and avoid hidden dependencies on live data, warehouse files, DataHub, FeatureHub, Scanner, credentials, browser state, or current clock time

### Readiness Update

If this task completes the selected readiness batch, update the local Phase 5 readiness gate metadata so:

- `multi_configuration_comparison_workflows` no longer overstates unresolved comparison gaps if the implementation covers them
- `offline_regression_boundaries_and_reproducibility` no longer overstates unresolved reproducibility gaps if tests cover them
- `phase_closure_ready` is marked true only if all Phase 5 readiness groups truthfully have no unresolved `warn`, `blocked`, or `fail` status

If any residual limitation remains, keep it explicit as `warn` / `blocked` with evidence and leave Phase 5 non-closure-ready.

## Tests

Required default tests:

- `python3 -m unittest discover -s tests/backtest -p 'test_*.py'`
- `python3 -m unittest discover -s tests/strategies -p 'test_*.py'` if StrategyLab compatibility files are changed

Add focused tests for:

- deterministic comparison identity and normalized output
- multi-configuration ranking and tie-breaking
- invalid/duplicate/mismatched comparison inputs
- reproducibility reruns and input-order stability
- assumption/report metric propagation
- readiness gate updates
- no hidden network, warehouse, DataHub, FeatureHub, Scanner, credential, browser/session, or current-clock dependency

A broader `python3 -m unittest discover -s tests -p 'test_*.py'` run is allowed if useful and must remain offline-safe.

No live tests are required or allowed. Default tests must be offline-safe.

## Completion Report

Write `coordination/reports/TASK-150_REPORT.md` with:

- files changed
- comparison workflow capabilities added
- reproducibility and boundary regression coverage added
- readiness gate updates, if any
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled result as `SKIP` because this is local/offline StrategyLab and BacktestEngine work
- deviations from the handoff
- risks or follow-up tasks
