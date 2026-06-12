# TASK-145 Scanner ranking normalization rework

## Role

5.3 Execution Window.

## Phase

Phase 4-P Scanner Personal Trading Perfection Re-Review.

## Context

TASK-145 implemented Scanner ranking workflow hardening and wrote `coordination/reports/TASK-145_REPORT.md`.

Review rejected Controller closure in `coordination/reviews/TASK-145_REVIEW.md` because a focused ranking-config normalization defect remains:

- `validate_scan_ranking_config(...)` accepts dataclass `RankingCriterion` items inside a mapping payload.
- `_normalize_ranking_config(...)` then treats each mapping-payload criterion as subscriptable mapping data.
- A caller using `run_scan(..., ranking={"criteria": (RankingCriterion(...),)})` receives a raw `TypeError: 'RankingCriterion' object is not subscriptable` instead of accepted normalization or a controlled `InvalidScanRankingConfigError`.
- Existing tests cover pure dataclass config and pure dict config, but not mixed mapping-plus-dataclass ranking input.

This is a focused Review rework. Do not merge it with `scanner_artifact_contract_repair_batch_01`, readiness `follow_up_batches`, or any ordinary Scanner hardening item.

## Objective

Fix the ranking-config normalization/contract gap identified by Review with the smallest safe Scanner change.

The rework must ensure mixed mapping-plus-dataclass ranking input is handled deterministically:

- either normalize accepted `RankingCriterion` items inside mapping payloads into `ScanRankingConfig`, or reject them with `InvalidScanRankingConfigError`
- do not allow raw `TypeError`, `KeyError`, attribute errors, or other uncontrolled exceptions to escape for this input shape
- preserve accepted pure dataclass ranking config behavior
- preserve accepted pure mapping ranking config behavior
- preserve current ranking score/order semantics unless the focused fix requires a minimal compatibility adjustment

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-145_SCANNER_RANKING_WORKFLOW_HARDENING.md`
- `coordination/handoffs/TASK-145_SCANNER_RANKING_NORMALIZATION_REWORK.md`
- `coordination/reports/TASK-145_REPORT.md`
- `coordination/reviews/TASK-145_REVIEW.md`
- `quant/scanner/contracts.py`
- `quant/scanner/runner.py`
- `tests/scanner/test_runner.py`

Read other Scanner files only if the focused fix exposes a direct compatibility need. Do not inspect `coordination/agent_runs/**`.

## Allowed Writes

Only:

- `quant/scanner/runner.py`
- `tests/scanner/test_runner.py`
- `coordination/reports/TASK-145_REPORT.md`

If the focused fix proves that the correct minimal behavior requires a contract-level validation adjustment, Execution may also write:

- `quant/scanner/contracts.py`
- `tests/scanner/test_contracts.py`

Do not update readiness state unless the existing TASK-145 report is factually wrong after the rework; if any report wording is updated, keep it limited to the normalization rework evidence.

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

Do not fetch live data, call source adapters, read local warehouse state, use credentials, introduce hidden network behavior, implement artifact provenance repair, or implement strategy/backtest/signal/portfolio/risk/AI/notification/UI/automated trading logic.

## Implementation Requirements

The rework must:

- address the exact Review finding for mapping ranking payloads whose `criteria` sequence contains `RankingCriterion` dataclass items
- add a default offline regression test that would fail on the reviewed defect
- prove the mixed input shape no longer escapes a raw `TypeError`
- preserve current invalid ranking config behavior for malformed mapping criteria
- keep excluded/ineligible/missing/stale behavior unchanged
- keep all behavior local over caller-provided data

## Tests

Required default tests:

- `python3 -m unittest tests.scanner.test_runner`
- `python3 -m unittest discover -s tests/scanner -p 'test_*.py'`

If contract files are touched, also run:

- `python3 -m unittest tests.scanner.test_contracts`

No live tests are required or allowed. Default tests must remain offline-safe.

## Completion Report

Update `coordination/reports/TASK-145_REPORT.md` with a focused rework section that includes:

- files changed for the rework
- the ranking normalization behavior chosen for mixed mapping-plus-dataclass input
- regression coverage added
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled result as `SKIP` because this is local Scanner work
- deviations from this rework handoff
- remaining risks or follow-up tasks
