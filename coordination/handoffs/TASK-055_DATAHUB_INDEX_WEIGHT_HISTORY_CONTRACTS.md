# TASK-055: DataHub Index Weight History Contracts

## Task ID

TASK-055

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2.5: DataHub Trading-Grade Source Capability

## Context

TASK-054 has been accepted by Review and integrated. It reconciled accepted public macro/policy adapter coverage with source catalog and Phase 2.5 capability truth. Default tests remain offline-safe, and TASK-054 was offline-only with live-enabled result `SKIP` as required by its handoff.

Under `coordination/PHASE_GATE.md`, Phase 2.5 remains open because required trading-grade DataHub source capabilities still include planned or partial source-capability work. The next explicit planned required gap is `index_weight_history`: the capability matrix maps it through `DatasetName.INDEX_CONSTITUENTS`, but its source truth remains `planned` because index weight-history contract fields are not standardized.

This handoff is contract-only. It must not add source adapters, live fetches, broad collection, FeatureHub calculations, scanner ranking, strategy, backtest, portfolio, signal, risk, notification, AI, UI, automated trading, or derived trading-signal logic.

The execution window must read:

- `AGENTS.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-055_DATAHUB_INDEX_WEIGHT_HISTORY_CONTRACTS.md`
- `quant/datahub/datasets.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_datasets.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`

## Goal

Add a stable DataHub contract target for index constituent weight history so later Phase 2.5 adapter work can implement bounded source coverage against explicit weight-history source facts instead of relying on loosely optional `INDEX_CONSTITUENTS.weight` semantics.

## Required Contract Target

Create or harden a conservative DataHub dataset contract for index weight-history source facts.

The preferred canonical approach is a dedicated dataset name:

- `DatasetName.INDEX_WEIGHT_HISTORY`

If the execution window finds a narrower change is more consistent with the existing schema design, it may instead harden `DatasetName.INDEX_CONSTITUENTS`, but the resulting contract must explicitly represent index x symbol x effective-date weight history and must make the source-fact semantics testable.

The contract should include fields such as:

- `index_code`
- `symbol`
- `market`
- `effective_date`
- `weight`
- optional `weight_unit` or equivalent if needed to preserve source truth
- optional `rebalance_date`
- optional `out_date` or membership end date when truthfully available
- optional source route/category fields
- provenance fields consistent with existing contracts:
  - `source`
  - optional `source_ts`
  - `ingested_at`
  - `schema_version`

Keep required fields conservative and source-truth friendly. Optional fields are acceptable where public routes may not provide every metric.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-055_REPORT.md`

Expected implementation locations:

- `quant/datahub/datasets.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `quant/datahub/__init__.py` only if exports need adjustment
- `tests/datahub/test_datasets.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`
- optional focused new tests under `tests/datahub/`

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

### 1. Dataset registry contract

Extend DataHub dataset registry/schema/semantic-rule coverage with explicit index weight-history source-fact semantics.

Do not encode ranking, index-rebalance trading ideas, buy/sell advice, portfolio construction, risk rules, scanner logic, or derived FeatureHub indicators. This task is only about source data facts and validation.

### 2. Source capability mapping

Update `quant/datahub/source_capabilities.py` so `index_weight_history` maps to the explicit weight-history contract target.

Keep status conservative:

- Do not mark the capability `covered`.
- Use `planned` if this task only defines the contract and leaves adapter/source implementation pending.
- Use `partial` only if existing code already truthfully provides validated source coverage for the explicit weight-history contract.

Update `gap_reason` and `recommended_handoff_theme` to state whether adapter/source implementation remains pending.

### 3. Source catalog alignment

If a new dataset is added, align `quant/datahub/source_catalog.py` conservatively.

Do not imply credential-free implemented adapter coverage where none exists. If the only reliable source family remains credentialed `tushare_pro_cn_core`, keep `requires_credentials=True` source truth intact and keep the capability surfaced by planned-or-credentialed gap helpers.

### 4. Offline tests

Add deterministic tests proving:

- the weight-history contract target is registered
- the target has schema and semantic-rule coverage
- representative valid fixture records pass registry validation
- invalid required-field/type/weight examples fail validation
- `index_weight_history` has the explicit contract mapping and remains not `covered`
- credential/source-stage truth remains surfaced by source capability helpers where appropriate
- source catalog alignment remains truthful
- default tests perform no live network access

## Testing Requirements

Default tests must be offline.

Live tests are forbidden for TASK-055.

Run focused tests:

`python3 -m unittest tests/datahub/test_datasets.py`

`python3 -m unittest tests/datahub/test_source_capabilities.py`

Run source-catalog tests if `source_catalog.py` changes:

`python3 -m unittest tests/datahub/test_source_catalog.py`

Run full DataHub default tests:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

If any command cannot run, report the exact command and reason in `coordination/reports/TASK-055_REPORT.md`.

## Acceptance Criteria

The task is acceptable when:

- a stable DataHub index weight-history source-fact contract target exists
- `index_weight_history` has an explicit dataset mapping and remains conservatively classified
- deterministic offline tests cover registry/schema/semantic/source-capability/catalog behavior
- no real source adapter or live fetch logic is added
- no future-phase modules are modified
- report exists at `coordination/reports/TASK-055_REPORT.md`
- report includes files changed, tests run, default network behavior, live-enabled status, deviations, and follow-up tasks

## Report Path

`coordination/reports/TASK-055_REPORT.md`

## Review Path

`coordination/reviews/TASK-055_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-055_INTEGRATION.md`
