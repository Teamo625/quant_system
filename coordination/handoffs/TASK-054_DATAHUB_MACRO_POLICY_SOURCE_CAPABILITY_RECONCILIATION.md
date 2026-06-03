# TASK-054: DataHub Macro/Policy Source Capability Reconciliation

## Task ID

TASK-054

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2.5: DataHub Trading-Grade Source Capability

## Context

TASK-053 has been accepted by Review and integrated. It added bounded public AKShare adapter coverage for `DatasetName.SUSPENSION_RESUMPTION_EVENTS`; `a_share_suspension_resumption` is now conservatively `partial`.

Phase 2.5 remains open. The current capability matrix still reports required `planned` entries for:

- `macro_observations`
- `macro_indicator_definitions`
- `policy_documents`

These planned states appear to be driven by `macro_policy_public_sources` remaining `SourceStage.PLANNED` in `quant/datahub/source_catalog.py`, even though earlier accepted DataHub work already added public macro and policy adapters:

- TASK-024: AKShare China macro adapter for `MACRO_INDICATOR_MASTER` and `MACRO_OBSERVATIONS`
- TASK-030: public policy documents adapter for `POLICY_DOCUMENTS`

This task is a bounded reconciliation task. It must not introduce new source routes, live-network behavior, broad collection, FeatureHub, scanner, strategy, backtest, portfolio, signal, risk, notification, AI, UI, automated trading, or derived trading-signal logic.

## Required Reading

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-054_DATAHUB_MACRO_POLICY_SOURCE_CAPABILITY_RECONCILIATION.md`
- `coordination/reviews/TASK-024_REVIEW.md`
- `coordination/reviews/TASK-030_REVIEW.md`
- `quant/datahub/source_catalog.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/policy.py`
- relevant source catalog, source capability, macro adapter, and policy adapter tests under `tests/datahub/`

## Goal

Reconcile DataHub source catalog and Phase 2.5 source-capability truth for already implemented public macro and policy source coverage.

The expected outcome is that Phase 2.5 no longer treats accepted public macro/policy adapter coverage as merely `planned`. Capability statuses should be conservative and source-truth based, likely `partial` unless the execution window can justify `covered` from existing contracts, adapters, tests, and accepted review evidence.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/source_catalog.py`
- `quant/datahub/source_capabilities.py`
- focused tests under `tests/datahub/`
- `coordination/reports/TASK-054_REPORT.md`

Suggested test files:

- `tests/datahub/test_source_catalog.py`
- `tests/datahub/test_source_capabilities.py`
- existing focused macro/policy adapter tests only if needed to preserve changed expectations

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

## Implementation Requirements

### 1. Source catalog truth

Update `macro_policy_public_sources` only as needed to reflect already accepted public macro/policy adapter coverage.

The reconciliation should:

- preserve source id `macro_policy_public_sources`
- preserve no-credential behavior
- preserve `requires_live_network=True`
- keep dataset coverage limited to currently contracted/implemented macro and policy datasets unless tests prove otherwise
- update `stage`, `notes`, or related catalog metadata if `SourceStage.PLANNED` is no longer truthful after TASK-024 and TASK-030
- avoid changing unrelated source families

### 2. Source capability truth

Update only directly affected capabilities as needed:

- `macro_observations`
- `macro_indicator_definitions`
- `policy_documents`

For each updated capability:

- use `partial` when current adapter coverage is validated but remains narrow, selected-route, selected-indicator, selected-source, limited-history, or metadata-only
- do not use `covered` unless the current implementation genuinely satisfies the full trading-grade capability definition
- update `gap_reason` and `recommended_handoff_theme` to describe remaining gaps accurately
- do not alter unrelated partial capabilities, especially credentialed `index_weight_history`

### 3. Tests

Add or update deterministic offline tests proving:

- `macro_policy_public_sources` catalog stage and notes no longer imply unimplemented planned-only coverage if reconciled
- source catalog dataset coverage still includes `MACRO_INDICATOR_MASTER`, `MACRO_OBSERVATIONS`, and `POLICY_DOCUMENTS`
- `macro_observations`, `macro_indicator_definitions`, and `policy_documents` are no longer `planned` if accepted adapter evidence supports that change
- `get_capabilities_with_planned_or_credentialed_sources()` still reports genuinely planned or credentialed gaps such as `index_weight_history`
- default tests remain offline-safe

Do not add live tests for TASK-054. This task is reconciliation of already accepted source truth, not a new real-source adapter task.

## Do Not Implement

Do not implement:

- new macro or policy source adapters
- new source routes
- broad macro/policy collection
- full-history backfill
- storage refresh orchestration
- FeatureHub calculations
- scanner ranking or stock picking
- strategy, backtest, portfolio, signal, risk, notification, AI, UI, or automated trading logic

## Testing Requirements

Default tests must remain offline.

Run:

`python3 -m unittest tests/datahub/test_source_catalog.py`

`python3 -m unittest tests/datahub/test_source_capabilities.py`

Run focused regressions if expectations are touched:

`python3 -m unittest tests/datahub/test_akshare_china_macro_adapter.py`

`python3 -m unittest tests/datahub/test_policy_documents_adapter.py`

Run the full DataHub default suite:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

## Report Requirements

Write `coordination/reports/TASK-054_REPORT.md` with:

- files changed
- tests run
- default network behavior
- live-enabled result: `SKIP` because TASK-054 is offline reconciliation and live tests are forbidden
- deviations from this handoff
- remaining risks or follow-up tasks, especially any credentialed or still-planned source capability gaps
