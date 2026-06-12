# TASK-144 Scanner universe snapshot consistency rework

## Role

5.3 Execution Window.

## Phase

Phase 4-P Scanner Personal Trading Perfection Re-Review.

## Context

TASK-144 execution implemented the first Scanner universe/constraint hardening batch and wrote `coordination/reports/TASK-144_REPORT.md`.

Review rejected Controller closure because the hardened universe composition path accepts an internally inconsistent `UniverseDefinition` plus `UniverseMembershipSnapshot` pair. Review evidence:

- `compose_universe_membership(...)` validates the definition and snapshot independently but does not call or otherwise enforce `validate_universe_membership_snapshot(...)`.
- A `UniverseDefinition` for `HK` / `hong_kong_stock` can be paired with a `CN` membership snapshot and still reach `PreparedUniverseMembership`.
- `run_scan_with_diagnostics(...)` can therefore execute against contradictory universe identity and market semantics.

This violates the TASK-144 requirement to reject inconsistent universe-family / market combinations with clear validation errors.

This handoff is a focused Review rework. Do not merge it with `scanner_ranking_workflow_batch_01`, `scanner_artifact_contract_repair_batch_01`, or any other ordinary Scanner hardening item.

## Objective

Fix the TASK-144 blocking Review finding with the smallest safe Scanner change:

- enforce definition/snapshot consistency on the hardened composition path
- reject mismatched universe family, market, preset, or definition identity where existing contracts require consistency
- add focused offline regression coverage for the mismatched-definition/snapshot path
- update the TASK-144 report with truthful rework evidence

Keep all behavior local and deterministic. Do not fetch data, read local warehouse state, call DataHub or FeatureHub adapters, use credentials, or introduce hidden network behavior.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-144_SCANNER_UNIVERSE_SNAPSHOT_CONSISTENCY_REWORK.md`
- `coordination/handoffs/TASK-144_SCANNER_UNIVERSE_CONSTRAINTS_HARDENING.md`
- `coordination/reports/TASK-144_REPORT.md`
- `coordination/reviews/TASK-144_REVIEW.md`
- `quant/scanner/universe.py`
- `quant/scanner/runner.py`
- `tests/scanner/test_universe.py`
- `tests/scanner/test_runner.py`

Read other Scanner files or tests only if needed to understand existing contracts or to place the smallest focused regression test.

## Allowed Writes

Only:

- `quant/scanner/universe.py`
- `quant/scanner/runner.py` only if required to preserve hardened runner behavior after the consistency fix
- `tests/scanner/test_universe.py`
- `tests/scanner/test_runner.py`
- new focused files under `tests/scanner/` only if clearer than extending existing tests
- `coordination/reports/TASK-144_REPORT.md`

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files other than `coordination/reports/TASK-144_REPORT.md`
- `coordination/handoffs/**`
- `coordination/reviews/**`
- `coordination/integrations/**`
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

Do not implement ranking/scoring, candidate artifact metadata repair, StrategyLab, BacktestEngine, portfolio/signal/risk logic, AI, notification, UI, automated trading, credentials, private data, live fetching, or warehouse reads.

## Implementation Requirements

- Make `compose_universe_membership(...)` reject inconsistent `UniverseDefinition` and `UniverseMembershipSnapshot` inputs before returning `PreparedUniverseMembership`.
- Prefer reusing the existing `validate_universe_membership_snapshot(...)` contract if it already captures the required cross-check.
- Preserve backward-compatible valid TASK-144 behavior for supported universe families, presets, exclusions, missing/stale feature policies, and caller-provided market eligibility constraints.
- Ensure validation errors are clear enough for callers and tests to identify the consistency problem.
- Add focused regression coverage proving at least one mismatched market/family definition-snapshot pair fails instead of reaching a prepared universe or scan execution.
- Do not broaden this rework into ordinary readiness follow-up batches.

## Tests

Required default tests:

- `python3 -m unittest tests.scanner.test_universe`
- `python3 -m unittest tests.scanner.test_runner`
- `python3 -m unittest discover -s tests/scanner -p 'test_*.py'`

No live tests are required or allowed. Default tests must remain offline-safe.

## Completion Report

Update `coordination/reports/TASK-144_REPORT.md` with:

- files changed for this rework
- how the definition/snapshot consistency defect was fixed
- regression tests added
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled result as `SKIP` because this is local Scanner work
- deviations from this rework handoff
- remaining risks or follow-up tasks
