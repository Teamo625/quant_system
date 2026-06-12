# TASK-149 Replay assumptions, market rules, metrics, and report-output hardening

## Role

5.3 Execution Window.

## Phase

Phase 5 StrategyLab and BacktestEngine Personal Trading Perfection.

## Context

TASK-148 is closed after accepted Review Agent verification of the focused experiment-id/content validation and starter output-intent metadata truth rework. It closed the first Phase 5 readiness hardening batch:

- batch id: `strategy_backtest__personal_trading_hardening__batch_01`
- items:
  - `phase5__strategy_definition_and_starter_library`
  - `phase5__parameter_versioning_and_experiment_config`

Controller rechecked the current Phase 5 readiness gate after TASK-148. It now reports `phase_closure_ready=false`, status counts `pass=3`, `warn=4`, `blocked=0`, `fail=0`, and two remaining coherent follow-up batches.

The next executable current-phase capability cluster is:

- batch id: `strategy_backtest__personal_trading_hardening__batch_02`
- theme: replay assumption, market-calendar, and execution-model hardening
- follow-up items:
  - `phase5__replay_assumptions_and_market_rules`
  - `phase5__metrics_and_report_outputs`

This is a two-item coherent Phase 5 cluster. It is dispatched together because execution assumptions and evaluation outputs must be hardened together: metrics and report-ready summaries should reflect explicit replay semantics rather than implicit simplifications.

## Objective

Harden BacktestEngine replay assumptions and result outputs enough for repeatable personal offline strategy research over caller-provided local inputs.

The implementation must remain local/offline. It must not fetch data, read the warehouse, infer missing upstream source data, create live trading signals, or implement portfolio/signal/risk modules.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-149_REPLAY_ASSUMPTIONS_METRICS_HARDENING.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/ROADMAP.md`
- `coordination/PHASE_GATE.md`
- `coordination/reports/TASK-147_REPORT.md`
- `coordination/reviews/TASK-147_REVIEW.md`
- `coordination/reports/TASK-148_REPORT.md`
- `coordination/reviews/TASK-148_REVIEW.md`
- `quant/backtest/`
- `tests/backtest/`

Read `quant/strategies/` or `tests/strategies/` only if needed to preserve starter-strategy to replay assumptions or report-output compatibility. Do not change Scanner, FeatureHub, or DataHub files.

## Allowed Writes

Only:

- `quant/backtest/**`
- `tests/backtest/**`
- `quant/strategies/**` only if needed for compatibility with existing starter strategy replay output metadata
- `tests/strategies/**` only if needed for that StrategyLab compatibility
- `coordination/reports/TASK-149_REPORT.md`

Suggested implementation areas:

- `quant/backtest/contracts.py`
- `quant/backtest/replay.py`
- `quant/backtest/experiments.py`
- `quant/backtest/personal_readiness.py`
- focused exports in `quant/backtest/__init__.py` if needed
- `quant/backtest/README.md` if replay/report assumptions are documented there
- focused tests under `tests/backtest/`

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files other than `coordination/reports/TASK-149_REPORT.md`
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

### Replay Assumptions and Market Rules

Extend or harden the local replay model so its assumptions are explicit, deterministic, validated, and test-covered.

At minimum:

- make market-calendar behavior explicit for caller-provided sessions, including date-window boundaries, missing bars, non-trading dates, and suspended/no-trade dates represented by absent or unusable bars
- make corporate-action/source assumptions explicit, especially whether replay expects adjusted or unadjusted prices and how that assumption is recorded in config/results
- preserve caller-provided data ownership: do not compute adjustment factors, query trading calendars, or fetch bars
- keep transaction cost and slippage assumptions finite, deterministic, and validated
- keep fill rules explicit, including same-day close or any supported alternative, rejected missing/unusable bars, insufficient cash, insufficient position, and deterministic position/cash carry-forward
- provide structured assumption metadata in replay config/result output so metrics and reports can state the replay semantics used

### Metrics and Report-Ready Outputs

Expand result outputs from the current basic replay summary into deterministic, report-ready personal research summaries.

At minimum:

- compute or expose a broader metric set beyond ending equity / total return / max drawdown, such as realized/unrealized PnL, win/loss counts or rates where determinable, exposure/turnover-style summaries, trade counts, rejected-intent counts, cash/position end-state facts, and date coverage
- keep metric definitions deterministic and clearly tied to replay assumptions
- add a serialization-friendly report summary object or normalized report payload suitable for later comparison workflows
- validate artifact/report references if such fields exist; do not write persistent artifacts unless the local BacktestEngine already has a safe pattern for doing so
- preserve backwards compatibility for existing replay summary fields and tests unless the handoff explicitly justifies a schema-safe extension

### Readiness Update

If this task completes the selected TASK-147/TASK-148 readiness batch, update the local Phase 5 readiness gate metadata where appropriate so the covered replay-assumption and metrics/report-output groups no longer overstate unresolved gaps.

Do not mark Phase 5 closure-ready unless every remaining TASK-147/TASK-148 follow-up batch is also complete and the readiness gate truthfully reports no unresolved `warn`, `blocked`, or `fail` items.

## Tests

Required default tests:

- `python3 -m unittest discover -s tests/backtest -p 'test_*.py'`

Run strategy tests too if StrategyLab compatibility files are changed:

- `python3 -m unittest discover -s tests/strategies -p 'test_*.py'`

Add focused tests for:

- market-calendar and date-window assumptions over caller-provided bars
- missing-bar / suspended-or-no-trade behavior
- corporate-action adjusted/unadjusted price assumption metadata
- cost, slippage, fill, cash, and position edge cases
- metric/report output determinism and serialization shape
- invalid config, non-finite numeric assumptions, and artifact/report reference validation where applicable
- no hidden network, warehouse, DataHub, FeatureHub, Scanner, or credential dependency

A broader `python3 -m unittest discover -s tests -p 'test_*.py'` run is allowed if useful and must remain offline-safe.

No live tests are required or allowed. Default tests must be offline-safe.

## Completion Report

Write `coordination/reports/TASK-149_REPORT.md` with:

- files changed
- replay assumptions and market-rule behavior added or clarified
- metrics/report-output capabilities added
- readiness gate updates, if any
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled result as `SKIP` because this is local/offline StrategyLab/BacktestEngine work
- deviations from the handoff
- risks or follow-up tasks
