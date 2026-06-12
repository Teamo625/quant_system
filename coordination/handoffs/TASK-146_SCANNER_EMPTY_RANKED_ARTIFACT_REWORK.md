# TASK-146 Scanner empty ranked artifact rework

## Role

5.3 Execution Window.

## Phase

Phase 4-P Scanner Personal Trading Perfection Re-Review.

## Context

TASK-146 initial execution produced `coordination/reports/TASK-146_REPORT.md`, but Review rejected Controller closure in `coordination/reviews/TASK-146_REVIEW.md`.

The Review finding is focused and blocking:

- Empty ranked scan artifacts cannot be persisted.
- `run_scan(...)` can carry `artifact_context.ranking` when a ranking config is supplied, including when the scan returns zero candidates.
- `storage.py` currently infers ranked/unranked state from candidate rows only.
- A legitimately empty ranked scan is therefore treated as unranked, rejects ranking metadata, and would produce a false downstream handoff `ranked=false`.

This violates the TASK-146 artifact contract objective because ranking reproducibility must be preserved for persisted ranked scans even when no candidate passes the filters.

This rework is a small Review rework. Do not merge it with readiness `follow_up_batches` or any ordinary hardening item.

## Objective

Fix ranked artifact persistence so ranked state is derived from explicit ranking metadata/configuration, not from the existence of ranked candidate rows.

After the rework:

- a ranked scan with zero candidates and valid ranking provenance must persist successfully
- the persisted manifest/downstream handoff must truthfully identify the artifact as ranked
- an unranked artifact must still reject unexpected ranking metadata
- malformed or incomplete ranking metadata must still fail with explicit contract/storage errors
- checksum behavior must remain tied to serialized candidate rows, including the empty-row case
- manifest serialization must remain deterministic
- readiness truth must not claim Phase 4-P closure unless the empty ranked boundary is fixed and covered

Keep all behavior local and deterministic. Do not fetch data, read warehouse state, call DataHub or FeatureHub adapters, use credentials, or implement StrategyLab, SignalEngine, BacktestEngine, portfolio, risk, AI, notification, UI, or automated trading behavior.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-146_SCANNER_EMPTY_RANKED_ARTIFACT_REWORK.md`
- `coordination/handoffs/TASK-146_SCANNER_ARTIFACT_CONTRACT_REPAIR.md`
- `coordination/reports/TASK-146_REPORT.md`
- `coordination/reviews/TASK-146_REVIEW.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/ROADMAP.md`
- `coordination/PHASE_GATE.md`
- `quant/scanner/storage.py`
- `quant/scanner/runner.py`
- `quant/scanner/contracts.py`
- `quant/scanner/personal_readiness.py`
- `tests/scanner/test_storage.py`
- `tests/scanner/test_runner.py`
- `tests/scanner/test_contracts.py`
- `tests/scanner/test_personal_readiness.py`

Read other `quant/scanner/` or `tests/scanner/` files only if needed to preserve existing Scanner behavior.

## Allowed Writes

Only:

- `quant/scanner/storage.py`
- `quant/scanner/runner.py` only if required to propagate explicit ranked artifact metadata correctly
- `quant/scanner/contracts.py` only if required to validate the ranked/unranked artifact contract cleanly
- `quant/scanner/personal_readiness.py` only if the rework discovers that readiness must remain `warn` after the fix
- `tests/scanner/test_storage.py`
- `tests/scanner/test_runner.py`
- `tests/scanner/test_contracts.py`
- `tests/scanner/test_personal_readiness.py`
- new focused files under `tests/scanner/` if they keep the boundary regression clearer
- `coordination/reports/TASK-146_REPORT.md`

Prefer the smallest storage/test change that fully addresses the Review finding.

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files other than `coordination/reports/TASK-146_REPORT.md`
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

Do not run `git add`, `git commit`, `git reset`, `git checkout`, or other git state-changing commands.

Do not fetch live data, call source adapters, read local warehouse state, use credentials, or introduce hidden network behavior.

## Implementation Requirements

The rework must:

- make the artifact ranked/unranked decision use explicit metadata when available, especially `metadata.artifact_context.ranking`
- preserve validation that ranked candidate rows require ranking provenance
- preserve validation that unranked artifacts cannot carry ranking provenance
- allow zero-candidate ranked artifacts with ranking provenance
- ensure downstream handoff `ranked` truth follows the artifact's explicit ranked state, not `any(row.rank is not None)`
- keep `content_checksum` deterministic and based only on serialized candidate rows
- keep overwrite and partial-write safety unchanged
- avoid broad contract churn unrelated to the Review finding

Regression coverage must include:

- persisting an empty ranked scan artifact through the relevant storage path
- verifying the manifest/downstream handoff records `ranked=true`
- verifying the checksum remains stable for an empty candidate-row payload
- preserving at least one negative case where unranked artifacts with ranking metadata fail

If the implementation cannot truthfully make the readiness gate closure-ready, update `quant/scanner/personal_readiness.py` to keep the relevant artifact readiness as `warn` and restore a precise follow-up item instead of over-claiming closure.

## Tests

Required default tests:

- `python3 -m unittest tests.scanner.test_storage`
- `python3 -m unittest tests.scanner.test_runner`
- `python3 -m unittest tests.scanner.test_contracts`
- `python3 -m unittest tests.scanner.test_personal_readiness`
- `python3 -m unittest discover -s tests/scanner -p 'test_*.py'`

No live tests are required or allowed. Default tests must remain offline-safe.

## Completion Report

Update `coordination/reports/TASK-146_REPORT.md` with:

- files changed in the rework
- the ranked-empty artifact fix
- manifest/downstream handoff ranked-truth behavior
- checksum/serialization behavior for empty candidate rows
- readiness-gate truth after rework
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled result as `SKIP` because this is local Scanner work
- deviations from the rework handoff
- risks or follow-up tasks
