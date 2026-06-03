# TASK-057: DataHub Tushare Index Weight Live Evidence Rework

## Task ID

TASK-057

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2.5: DataHub Trading-Grade Source Capability

## Context

TASK-056 has been accepted by Review and integrated. It added a bounded Tushare Pro adapter slice and offline/live-gated tests for:

- `DatasetName.INDEX_WEIGHT_HISTORY`

Controller closure is allowed for TASK-056, but its live-enabled result was `SKIP` because local prerequisites were missing:

- `TUSHARE_TOKEN` was not set
- local `tushare` SDK probe returned `MISSING`

The Review Agent explicitly recorded that this is not live source coverage evidence. Integration recommended keeping `index_weight_history` capability truth unchanged until a credentialed live smoke passes. Current capability truth therefore still marks `index_weight_history` as `planned`, making Phase 2.5 incomplete under the current controller state.

This task is a narrow live-evidence and prerequisite rework for the existing Tushare index-weight adapter path. It must not broaden into a new feature area.

## Goal

Diagnose and close the TASK-056 live-evidence gap where feasible.

The preferred successful outcome is:

- run the existing gated live smoke with local `tushare` SDK and `TUSHARE_TOKEN`
- obtain a live-enabled PASS for `INDEX_WEIGHT_HISTORY`
- if and only if live PASS proves real-source coverage, update `index_weight_history` capability truth conservatively from `planned` to `partial`
- write a truthful TASK-057 report for Review

If credentials are still absent, or the SDK cannot be installed/used in this environment, the execution window must report `SKIP` with exact prerequisite evidence and operator action required. Do not promote capability truth without live PASS.

## Required Reading

The execution window must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-057_DATAHUB_TUSHARE_INDEX_WEIGHT_LIVE_EVIDENCE_REWORK.md`
- `coordination/reports/TASK-056_REPORT.md`
- `coordination/reviews/TASK-056_REVIEW.md`
- `coordination/integrations/TASK-056_INTEGRATION.md`
- `quant/datahub/adapters/tushare.py`
- `quant/datahub/source_capabilities.py`
- `tests/datahub/test_tushare_index_weight_history_adapter.py`
- `tests/datahub/test_tushare_index_weight_history_live.py`

Read broader files only if needed to diagnose a concrete failure.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/adapters/tushare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `quant/datahub/source_capabilities.py`
- `tests/datahub/test_tushare_index_weight_history_adapter.py`
- `tests/datahub/test_tushare_index_weight_history_live.py`
- focused existing `tests/datahub/test_source_capabilities.py` assertions if capability truth changes
- `coordination/reports/TASK-057_REPORT.md`

## Forbidden Files

The execution window must not modify:

- `coordination/PROJECT_STATE.md`
- `coordination/ROADMAP.md`
- `coordination/TASK_BOARD.md`
- `coordination/DECISIONS.md`
- `coordination/RISKS.md`
- `coordination/INTERFACES.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/reviews/**`
- `coordination/integrations/**`
- `coordination/handoffs/**`
- `quant/features/**`
- `quant/strategies/**`
- `quant/backtest/**`
- `quant/scanner/**`
- `quant/portfolio/**`
- `quant/notification/**`
- `quant/ai/**`
- `quant/ui/**`

## Required Work

1. Verify local prerequisites for the Tushare live smoke:
   - whether `TUSHARE_TOKEN` is set
   - whether the `tushare` SDK is importable
   - whether the live test skip message reports missing prerequisites accurately

2. If the SDK is missing, attempt a repository-safe diagnosis and feasible local remediation:
   - do not commit vendored SDK files
   - do not commit credentials or private configuration
   - if dependency installation is not available or fails, record exact evidence in the report

3. Run the gated live smoke:

   `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_tushare_index_weight_history_live.py`

4. If live smoke passes:
   - verify at least one validated `DatasetName.INDEX_WEIGHT_HISTORY` record from Tushare
   - ensure default tests remain offline-safe
   - update `index_weight_history` in `quant/datahub/source_capabilities.py` to conservative `partial`
   - update focused capability tests only as needed
   - preserve remaining breadth/history/index-universe limitations in `gap_reason` and `recommended_handoff_theme`

5. If live smoke skips or fails:
   - keep `index_weight_history` as `planned`
   - distinguish credential/SDK prerequisite skip from network/proxy/DNS/TLS/upstream/source availability
   - for network/proxy/DNS/TLS/upstream/source availability failures, diagnose root cause and modify repository code/tests where feasible instead of only documenting the failure
   - keep adapter/schema/normalization/authentication/permission/quota/route signature issues as hard failures unless evidence proves they are environment-only and not repository-fixable

## Testing Requirements

Default tests must remain offline.

Run:

`python3 -m unittest tests/datahub/test_tushare_index_weight_history_adapter.py`

`python3 -m unittest -v tests/datahub/test_tushare_index_weight_history_live.py`

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_tushare_index_weight_history_live.py`

If capability truth changes, also run:

`python3 -m unittest tests/datahub/test_source_capabilities.py`

Run the full DataHub default suite unless the report gives a concrete reason it could not be run:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

## Report Requirements

Write `coordination/reports/TASK-057_REPORT.md` with:

- files changed
- tests run
- default network behavior
- live-enabled PASS/SKIP/FAIL result
- root-cause evidence for any SKIP/FAIL
- whether `index_weight_history` capability truth was changed
- deviations from this handoff
- risks or follow-up tasks

The report must explicitly state whether live source coverage is proven.
