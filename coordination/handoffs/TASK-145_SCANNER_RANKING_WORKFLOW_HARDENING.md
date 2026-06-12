# TASK-145 Scanner ranking workflow hardening

## Role

5.3 Execution Window.

## Phase

Phase 4-P Scanner Personal Trading Perfection Re-Review.

## Context

TASK-144 is closed after accepted Review Agent verification of the universe snapshot consistency rework. The accepted TASK-144 result keeps Phase 4-P inside Scanner scope, preserves default offline safety, and closes readiness batch `scanner_universe_constraints_batch_01` after the earlier universe/constraint hardening plus focused consistency rework.

Controller applied `coordination/PHASE_GATE.md` and `coordination/ROADMAP.md`. Phase 4-P remains incomplete because Scanner still lacks explicit ranking/scoring and workflow regression depth, and candidate artifact downstream provenance remains a separate contract-repair batch.

Controller read the Scanner readiness `follow_up_batches`. The next executable current-phase capability cluster is:

- batch id: `scanner_ranking_workflow_batch_01`
- items: `SCN-RANK-001`, `SCN-TEST-001`
- theme: ranking, scoring, tie-break ordering, and end-to-end offline workflow regressions

This is a two-item coherent Scanner hardening cluster. It groups ranking/scoring implementation with workflow regression tests because ordering semantics must be proven in default offline tests in the same batch. Do not merge the separate `scanner_artifact_contract_repair_batch_01` / `SCN-ART-001` item into this handoff; persisted artifact provenance and downstream handoff metadata have compatibility blast radius and remain isolated.

## Objective

Harden Scanner from filter-only candidate production into deterministic research-priority candidate ordering over caller-provided data.

Implement practical, offline-only support for:

- explicit ranking/scoring configuration over caller-provided feature values
- deterministic candidate score output and rank/order semantics
- stable tie-breaking rules that keep results reproducible across runs
- end-to-end default offline workflow regressions covering ranking, ordering, and interactions with existing universe/exclusion/constraint behavior

Keep all behavior local and deterministic. Do not fetch data, read local warehouse state, call DataHub or FeatureHub adapters, use credentials, or implement strategy/backtest, signal, portfolio, AI, notification, UI, or automated trading behavior.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-145_SCANNER_RANKING_WORKFLOW_HARDENING.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/ROADMAP.md`
- `coordination/PHASE_GATE.md`
- `coordination/reports/TASK-143_REPORT.md`
- `coordination/reviews/TASK-143_REVIEW.md`
- `coordination/reports/TASK-144_REPORT.md`
- `coordination/reviews/TASK-144_REVIEW.md`
- `quant/scanner/contracts.py`
- `quant/scanner/matching.py`
- `quant/scanner/runner.py`
- `quant/scanner/universe.py`
- `quant/scanner/personal_readiness.py`
- `tests/scanner/test_contracts.py`
- `tests/scanner/test_matching.py`
- `tests/scanner/test_runner.py`
- `tests/scanner/test_universe.py`
- `tests/scanner/test_personal_readiness.py`

Read `quant/scanner/storage.py` and `tests/scanner/test_storage.py` only if adding score/rank fields to candidate records requires serialization/validation compatibility. Do not add artifact provenance, downstream handoff metadata, manifest schema expansion, or compatibility repair beyond what is strictly required for ranking fields.

## Allowed Writes

Only:

- `quant/scanner/contracts.py`
- `quant/scanner/matching.py`
- `quant/scanner/runner.py`
- `quant/scanner/universe.py` only for minimal compatibility with ranked scan inputs if required
- `quant/scanner/personal_readiness.py`
- `quant/scanner/__init__.py` only for minimal exports
- `quant/scanner/storage.py` only for score/rank candidate-row serialization compatibility if required
- `tests/scanner/test_contracts.py`
- `tests/scanner/test_matching.py`
- `tests/scanner/test_runner.py`
- `tests/scanner/test_universe.py` only for existing universe/constraint compatibility regressions if required
- `tests/scanner/test_personal_readiness.py`
- `tests/scanner/test_storage.py` only if storage compatibility is touched
- new focused files under `tests/scanner/` if they keep coverage clearer
- `coordination/reports/TASK-145_REPORT.md`

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files other than `coordination/reports/TASK-145_REPORT.md`
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

Ranking/scoring hardening must:

- preserve existing `run_scan(...)` filter-only behavior by default where feasible, including deterministic output for callers that do not configure ranking
- add explicit ranking/scoring configuration instead of implicit feature-name conventions
- support deterministic score calculation over caller-provided feature values only
- define stable handling for ascending and descending criteria where applicable
- define clear invalid-input behavior for unknown ranking features, non-finite ranking values, duplicate ranking criteria, unsupported directions, or malformed ranking config
- produce deterministic score/rank/order semantics suitable for research candidate prioritization
- use explicit tie-breaking rules; ties must not depend on input ordering, dictionary ordering, or runtime state
- keep missing/stale/ineligible/excluded symbol handling consistent with TASK-144 behavior and ensure excluded or ineligible symbols do not receive ranks
- avoid adding strategy rules, backtest assumptions, signal state, risk scoring, portfolio sizing, or trading advice semantics

Workflow regression hardening must:

- add default offline tests for ranked multi-symbol scans over caller-provided feature rows
- cover ascending/descending ranking behavior and deterministic tie breaks
- cover interaction with existing filters, universe definition/snapshot consistency, exclusions, missing/stale policies, and market eligibility constraints
- cover invalid ranking configuration and invalid ranking data without hidden candidate promotion
- preserve candidate-list validation and storage safety for ranked rows if candidate records gain score/rank fields

Readiness update must:

- update `quant/scanner/personal_readiness.py` so `scanner_ranking_workflow_batch_01`, `SCN-RANK-001`, and `SCN-TEST-001` truthfully reflect the new implementation state
- keep `scanner_artifact_contract_repair_batch_01` / `SCN-ART-001` conservative and pending
- set the next recommended handoff batch to `scanner_artifact_contract_repair_batch_01` only if this task fully closes ranking/workflow gaps
- keep Phase 4-P closure false unless every Scanner readiness group is genuinely complete

## Tests

Required default tests:

- `python3 -m unittest tests.scanner.test_contracts`
- `python3 -m unittest tests.scanner.test_matching`
- `python3 -m unittest tests.scanner.test_runner`
- `python3 -m unittest tests.scanner.test_personal_readiness`
- `python3 -m unittest discover -s tests/scanner -p 'test_*.py'`

If storage compatibility is touched, also run:

- `python3 -m unittest tests.scanner.test_storage`

No live tests are required or allowed. Default tests must remain offline-safe.

## Completion Report

Write `coordination/reports/TASK-145_REPORT.md` with:

- files changed
- implemented ranking/scoring configuration and ordering semantics
- implemented workflow regression coverage
- readiness-gate updates
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled result as `SKIP` because this is local Scanner work
- deviations from the handoff
- risks or follow-up tasks
