# TASK-144 Scanner universe constraints hardening

## Role

5.3 Execution Window.

## Phase

Phase 4-P Scanner Personal Trading Perfection Re-Review.

## Context

TASK-143 is closed after accepted Review Agent verification of the Scanner personal trading readiness gate. The gate is local-only, default offline-safe, and reports `phase_closure_ready=false` with status counts `pass=1`, `warn=5`, `blocked=0`, `fail=0`.

Controller applied `coordination/PHASE_GATE.md` and `coordination/ROADMAP.md`. Phase 4-P remains incomplete because Scanner still lacks market-aware universe families, exclusion-list composition, missing/stale feature policies, suspension/limit-up/down eligibility, ranking/scoring, and richer artifact handoff metadata.

Controller read the TASK-143 Scanner readiness `follow_up_batches` and selected the next executable current-phase capability cluster:

- batch id: `scanner_universe_constraints_batch_01`
- items: `SCN-UNI-001`, `SCN-UNI-002`, `SCN-CONSTRAINT-001`, `SCN-CONSTRAINT-002`
- theme: universe presets, exclusion lists, missing/stale feature policies, and market-specific eligibility constraints

This is an ordinary current-phase hardening capability cluster. It groups four related Scanner input-eligibility items because they share universe validation, runner input composition, constraint policy, and offline workflow test surfaces. Do not split the items unless implementation discovers a real contract risk that must be isolated and reported.

## Objective

Harden Scanner from generic caller-provided universe bags into market-aware, deterministic scan-input eligibility over caller-provided data.

Implement practical, offline-only support for:

- explicit universe-family or preset validation for supported scan domains: A-share, Hong Kong stock, ETF/fund, sector, index, and custom watchlist
- first-class exclusion-list inputs that can remove symbols deterministically from a broader universe before filtering
- configurable missing-feature and stale-feature policies for scan execution
- caller-provided suspension, limit-up/down, and market-specific eligibility constraints

Keep all behavior local and deterministic. Do not fetch data, read local warehouse state, call DataHub or FeatureHub adapters, use credentials, or implement ranking/scoring, strategy/backtest, signal, portfolio, AI, notification, UI, or automated trading behavior.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-144_SCANNER_UNIVERSE_CONSTRAINTS_HARDENING.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/ROADMAP.md`
- `coordination/PHASE_GATE.md`
- `coordination/reports/TASK-143_REPORT.md`
- `coordination/reviews/TASK-143_REVIEW.md`
- `quant/scanner/contracts.py`
- `quant/scanner/universe.py`
- `quant/scanner/matching.py`
- `quant/scanner/runner.py`
- `quant/scanner/personal_readiness.py`
- `tests/scanner/test_contracts.py`
- `tests/scanner/test_universe.py`
- `tests/scanner/test_matching.py`
- `tests/scanner/test_runner.py`
- `tests/scanner/test_personal_readiness.py`

Read Scanner storage tests only if the implementation changes candidate-list artifact construction. Read FeatureHub or DataHub contracts only if needed to understand existing market or dataset enum names; do not change those modules.

## Allowed Writes

Only:

- `quant/scanner/contracts.py`
- `quant/scanner/universe.py`
- `quant/scanner/matching.py`
- `quant/scanner/runner.py`
- `quant/scanner/personal_readiness.py`
- `quant/scanner/__init__.py` only for minimal exports
- `tests/scanner/test_contracts.py`
- `tests/scanner/test_universe.py`
- `tests/scanner/test_matching.py`
- `tests/scanner/test_runner.py`
- `tests/scanner/test_personal_readiness.py`
- new focused files under `tests/scanner/` if they keep coverage clearer
- `coordination/reports/TASK-144_REPORT.md`

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files other than `coordination/reports/TASK-144_REPORT.md`
- `coordination/reviews/**`
- `coordination/integrations/**`
- `coordination/handoffs/**`
- `quant/datahub/**`
- `tests/datahub/**`
- `quant/features/**`
- `tests/features/**`
- `quant/strategies/**`
- `quant/backtest/**`
- `quant/portfolio/**`
- `quant/notification/**`
- `quant/ai/**`
- `quant/ui/**`

Do not fetch live data, call source adapters, read local warehouse state, use credentials, or introduce hidden network behavior.

## Implementation Requirements

Universe hardening must:

- preserve existing public Scanner contracts and validation behavior unless a minimal backward-compatible extension is necessary
- add explicit, deterministic handling for the supported universe families or presets listed in the roadmap standard
- reject unsupported or internally inconsistent universe-family / market combinations with clear validation errors
- keep custom watchlists supported
- add first-class exclusion-list composition that removes matching symbols by normalized symbol and market without mutating the original membership inputs
- keep ordering deterministic after exclusions are applied

Constraint-policy hardening must:

- preserve existing hard-failure behavior as the default where feasible
- add explicit missing-feature and stale-feature policies so callers can choose fail, exclude, or otherwise deterministic documented behavior without silent candidate promotion
- treat stale features using caller-provided as-of/trade-date metadata only; do not infer freshness from system time or external sources
- add caller-provided eligibility handling for suspended securities, limit-up/down securities, and market-specific constraints
- ensure excluded or ineligible symbols are traceable through local reason codes or deterministic metadata suitable for tests and later artifact work
- avoid ranking/scoring fields, score calculations, or research-priority ordering; the next ranking batch owns that behavior

Readiness update must:

- update `quant/scanner/personal_readiness.py` so `scanner_universe_constraints_batch_01` truthfully reflects the new implementation state
- remove or adjust only completed `SCN-UNI-001`, `SCN-UNI-002`, `SCN-CONSTRAINT-001`, and `SCN-CONSTRAINT-002` follow-up truth
- keep ranking/scoring, artifact handoff metadata, and any remaining workflow-regression gaps conservative
- set the next recommended handoff batch to `scanner_ranking_workflow_batch_01` only if this task fully closes the universe/constraints batch

## Tests

Required default tests:

- `python3 -m unittest tests.scanner.test_universe`
- `python3 -m unittest tests.scanner.test_matching`
- `python3 -m unittest tests.scanner.test_runner`
- `python3 -m unittest tests.scanner.test_personal_readiness`
- `python3 -m unittest discover -s tests/scanner -p 'test_*.py'`

No live tests are required or allowed. Default tests must remain offline-safe.

## Completion Report

Write `coordination/reports/TASK-144_REPORT.md` with:

- files changed
- implemented universe-family and exclusion-list capabilities
- implemented missing/stale feature and market-constraint capabilities
- readiness-gate updates
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled result as `SKIP` because this is local Scanner work
- deviations from the handoff
- risks or follow-up tasks
