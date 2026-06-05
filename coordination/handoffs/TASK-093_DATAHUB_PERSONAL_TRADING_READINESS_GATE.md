# TASK-093: DataHub Personal Trading Perfection Re-Review Gate

Role: 5.3 Execution Window

## Context

The owner has reopened DataHub before FeatureHub resumes because all historical phase completion decisions must now be re-reviewed against the Personal Trading Perfection Standard. Phase 2.5 Core is useful historical no-paid source-capability progress, but it is not final personal trading completion until the public-source/no-paid perfection re-review passes.

Current substage:

- Phase 2.5-P DataHub Personal Trading Perfection Re-Review

Locked owner decisions:

- Paid/private data is not included for now.
- `index_weight_history` remains blocked/planned unless the owner later provides paid Tushare credentials and explicitly reopens that scope.
- The re-review universe is all historical DataHub phases and all existing DataHub domains.
- TASK-093 is reused as this DataHub task; the previous FeatureHub TASK-093 handoff is deferred and no longer active.

## Objective

Build the first deterministic DataHub perfection re-review gate for personal quant trading use.

The gate must cover historical DataHub Phase 1, Phase 2, Phase 2.5, and Phase 2.5-P work, plus all existing DataHub domains:

- A-share
- Hong Kong stock
- ETF/fund
- index
- sector/concept
- macro/policy
- local storage
- refresh metadata
- quality reports
- source-health diagnostics

The output must be a pass/fail/gap matrix that tells Controller exactly which DataHub gaps must be hardened before FeatureHub resumes. Any `partial`, foundation-only, representative, one-symbol/one-fund/one-route, contract-only, or narrow-smoke capability must not be treated as phase completion.

## Allowed Writes

Modify only:

- `quant/datahub/personal_readiness.py`
- `quant/datahub/__init__.py` only if export wiring is needed
- `tests/datahub/test_personal_readiness.py`
- `coordination/reports/TASK-093_REPORT.md`

## Forbidden

- Do not modify `quant/features/`, `tests/features/`, Scanner, StrategyLab, BacktestEngine, PortfolioMonitor, SignalEngine, RiskEngine, AI, UI, notification, automated trading, or downstream modules.
- Do not implement FeatureHub indicators, scanner ranking, trading strategies, backtest execution, signal logic, risk logic, portfolio logic, AI reports, notifications, UI, or automated trading.
- Do not add paid credentials, private tokens, cookies, or private account data.
- Do not add live tests for this task.
- Do not perform real network calls in default tests or task implementation.
- Do not change DataHub source adapters in this first gate task.
- Do not edit controller-owned coordination state files.

## Implementation Requirements

Add a deterministic personal-perfection re-review model with stable categories:

- `pass`
- `warn`
- `blocked`
- `fail`

The re-review gate must be offline-first and derive its conclusions from repository-local truth such as existing DataHub contracts, source capability metadata, source catalog mappings, storage/refresh/quality helpers, source-health diagnostics, historical phase/task status, and deterministic fixtures or static metadata.

For each domain, include checks for:

- whether historical Phase 1/2/2.5 claims are foundation-only, partial, representative, or final-ready under the new standard
- required dataset contracts or source-fact contracts
- adapter/source mapping evidence where discoverable from existing local metadata
- source capability status and limitations
- local storage and refresh path readiness where relevant
- quality report path readiness where relevant
- source-health or failure-diagnostic evidence where relevant
- known public-source limitations, classified explicitly as `warn` or `blocked` instead of silently passing

Required treatment:

- `index_weight_history` must remain `blocked` because paid/private Tushare credential evidence is intentionally excluded for now.
- Public-source breadth, history, taxonomy, or freshness limitations must become visible as `warn` or `fail` depending on whether they prevent personal trading readiness.
- Any capability currently marked or effectively behaving as `partial` must be surfaced and must not count as phase completion unless it has an explicit owner-accepted disposition.
- Missing local contracts, missing source mappings, missing diagnostic paths, or inconsistent status truth must become `fail`.
- The final summary must include counts by status and a Controller-ready follow-up list.

The implementation should keep the gate small, deterministic, and reviewable. Prefer clear data classes or small immutable structures over ad hoc dictionaries when that improves readability.

## Tests

Run:

- `python3 -m unittest tests/datahub/test_personal_readiness.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`
- `python3 -m unittest tests/datahub/test_source_catalog.py`

Do not run live-enabled tests for TASK-093.

Default tests must be offline-safe.

## Report Requirements

Write `coordination/reports/TASK-093_REPORT.md` with:

- files changed
- perfection re-review model summary
- domains covered
- pass/warn/blocked/fail matrix summary
- Controller-ready follow-up recommendations
- tests run
- default network behavior
- live-enabled result: `SKIP`, because TASK-093 forbids live tests
- deviations from the handoff
- risks or follow-up tasks
