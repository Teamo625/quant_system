# TASK-140 FeatureHub valuation and flow feature expansion

## Role

5.3 Execution Window.

## Phase

Phase 3-P FeatureHub Personal Trading Perfection Re-Review.

## Context

TASK-139 is closed after accepted Review Agent verification of the FeatureHub technical-indicator core expansion and focused MACD long-window test rework. Default tests remained offline-safe, and no live evidence was required because the work was pure local FeatureHub calculation/test coverage.

Phase 3-P remains incomplete under `coordination/PHASE_GATE.md` and the FeatureHub Personal Trading Perfection Standard in `coordination/ROADMAP.md`. The accepted TASK-138 readiness gate reports `phase_closure_ready=false`, status counts `pass=0`, `warn=7`, `blocked=0`, `fail=0`, and Controller-ready follow-up batches. TASK-139 covered the first technical-indicator batch. The next coherent readiness batch is `featurehub_valuation_flow_batch_01`, covering:

- `FH-VAL-001`: expand valuation outputs to raw PE/PB/PS style values plus percentile or relative valuation features over history windows
- `FH-FLOW-001`: add capital-flow rolling change, intensity, and fund-flow feature variants beyond the single latest-main-inflow record path

This handoff is an ordinary current-phase hardening capability cluster. It intentionally groups two related FeatureHub feature-domain items because both use caller-provided historical rows, window validation, numeric normalization, and offline-only feature output semantics. Do not split these items unless implementation discovers a real contract risk that must be isolated and reported.

## Objective

Harden FeatureHub valuation and flow primitives from representative slices into a broader scanner/strategy-ready local feature set over validated DataHub-shaped caller-provided inputs.

Implement practical, deterministic, offline-only feature calculations for:

- raw valuation ratio outputs such as latest PE/PB/PS-style values where present
- valuation percentiles or relative valuation metrics over bounded history windows
- capital-flow rolling changes and windowed flow summaries
- flow intensity or normalization variants using available turnover/scale-style inputs
- fund-flow variants over caller-provided fund-flow-shaped rows where source fields exist

Keep all behavior local and deterministic. Do not fetch data, read local warehouse state, call DataHub adapters, use credentials, or implement downstream scanner/strategy/backtest behavior.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-140_FEATUREHUB_VALUATION_FLOW_EXPANSION.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/ROADMAP.md`
- `coordination/PHASE_GATE.md`
- `coordination/reports/TASK-138_REPORT.md`
- `coordination/reviews/TASK-138_REVIEW.md`
- `coordination/reports/TASK-139_REPORT.md`
- `coordination/reviews/TASK-139_REVIEW.md`
- `quant/features/valuation.py`
- `quant/features/capital_flow.py`
- `quant/features/contracts.py`
- `quant/features/personal_readiness.py`
- `tests/features/test_valuation.py`
- `tests/features/test_capital_flow.py`
- `tests/features/test_personal_readiness.py`

Read DataHub dataset definitions only if needed to confirm existing `DatasetName` enum names or source-shaped field names. Do not change DataHub files.

## Allowed Writes

Only:

- `quant/features/valuation.py`
- `quant/features/capital_flow.py`
- `quant/features/contracts.py` only if a minimal FeatureHub contract update is required for local feature records, such as accepting `DatasetName.FUND_FLOW` as an approved source dataset
- `quant/features/personal_readiness.py`
- `quant/features/__init__.py` only for minimal exports
- `tests/features/test_valuation.py`
- `tests/features/test_capital_flow.py`
- `tests/features/test_contracts.py` only for minimal contract-regression coverage if `contracts.py` changes
- `tests/features/test_personal_readiness.py`
- `coordination/reports/TASK-140_REPORT.md`

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files other than `coordination/reports/TASK-140_REPORT.md`
- `coordination/reviews/**`
- `coordination/integrations/**`
- `coordination/handoffs/**`
- `quant/datahub/**`
- `tests/datahub/**`
- `quant/scanner/**`
- `tests/scanner/**`
- `quant/strategies/**`
- `quant/backtest/**`
- `quant/portfolio/**`
- `quant/notification/**`
- `quant/ai/**`
- `quant/ui/**`

Do not implement scanner ranking, candidate selection, strategy rules, backtest execution, portfolio/signal/risk logic, AI reports, notification behavior, UI, automated trading, paid credentials, private data access, source adapters, local warehouse refreshes, or hidden network behavior.

## Implementation Requirements

Valuation hardening must:

- preserve existing earnings-yield, book-to-price, float-market-cap-ratio behavior and public API compatibility
- support raw latest valuation outputs for PE/PB and PS-style ratios when caller-provided rows contain the needed fields
- add history-aware percentile or relative valuation calculations with explicit bounded window validation
- keep row normalization deterministic by symbol, market, trade date, finite numeric coercion, duplicate-date rejection, and missing-field errors where a metric requires a field
- avoid overclaiming source completeness; this is FeatureHub calculation over caller-provided rows, not DataHub source expansion

Capital/fund-flow hardening must:

- preserve existing latest main-net-inflow, trailing main-net-inflow sum, northbound, and turnover-adjusted behavior
- add deterministic rolling change or windowed change calculations for main-flow and, where feasible, northbound or fund-flow metrics
- add intensity/normalization variants only when the required caller-provided denominator fields are present and valid
- support fund-flow-shaped caller-provided rows without calling fund sources or DataHub adapters
- keep missing optional source fields explicit: return `None` only for documented optional metrics; raise `ValueError` for required metric inputs, invalid windows, invalid numeric values, mixed symbols/markets, duplicate dates, or insufficient history

Readiness update must:

- update `quant/features/personal_readiness.py` so `featurehub_valuation_flow_batch_01` truthfully reflects the new implementation state
- remove or adjust only completed `FH-VAL-001` / `FH-FLOW-001` follow-up truth; keep later relative-feature and batch/contract/test gaps conservative
- set the next recommended handoff batch to `featurehub_relative_features_batch_01` only if this task fully closes the valuation/flow batch

## Tests

Required default tests:

- `python3 -m unittest tests.features.test_valuation`
- `python3 -m unittest tests.features.test_capital_flow`
- `python3 -m unittest tests.features.test_personal_readiness`
- `python3 -m unittest discover -s tests/features -p 'test_*.py'`

No live tests are required or allowed. Default tests must remain offline-safe.

## Completion Report

Write `coordination/reports/TASK-140_REPORT.md` with:

- files changed
- implemented valuation capabilities
- implemented capital/fund-flow capabilities
- readiness-gate updates
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled result as `SKIP` because this is local FeatureHub calculation work
- deviations from the handoff
- risks or follow-up tasks
