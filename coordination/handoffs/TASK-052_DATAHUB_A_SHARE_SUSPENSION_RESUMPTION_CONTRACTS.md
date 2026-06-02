# TASK-052: DataHub A-share Suspension/Resumption Contracts

## Task ID

TASK-052

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2.5: DataHub Trading-Grade Source Capability

## Context

TASK-051 has been accepted by Review and closed by Controller. It added a narrow no-credential public AKShare ETF/fund `FUND_FLOW` adapter slice under `akshare_cn_hk_public_family`, with default offline-safe tests and live-enabled PASS evidence. TASK-051 has no local integration artifact; closure proceeds through the Review gate because strict integration was not required by `coordination/PHASE_GATE.md`.

Under `coordination/PHASE_GATE.md`, Phase 2.5 remains open because required trading-grade DataHub source capabilities still include planned or partial source-capability work. The current capability matrix marks `a_share_suspension_resumption` as required and partial. It is currently mapped through generic `DatasetName.CORPORATE_ACTIONS`, and the capability truth states that suspension taxonomy and historical completeness are not guaranteed by contracts.

This handoff is contract-only. It must not add source adapters, live fetches, broad collection, feature calculation, scanner ranking, strategy, backtest, portfolio, signal, risk, notification, AI, UI, automated trading, or derived trading-signal logic.

The execution window must read:

- `AGENTS.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-052_DATAHUB_A_SHARE_SUSPENSION_RESUMPTION_CONTRACTS.md`
- `quant/datahub/datasets.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_datasets.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`

## Goal

Add a stable DataHub contract target for A-share suspension/resumption source facts so later Phase 2.5 adapter work can implement bounded public-source coverage against an explicit schema instead of overloading `CORPORATE_ACTIONS`.

## Required Contract Target

Create a conservative DataHub dataset contract for A-share suspension and resumption events. The execution window may choose the exact enum name, but the preferred canonical name is:

- `DatasetName.SUSPENSION_RESUMPTION_EVENTS`

The contract should represent source facts, not trading signals. It may include fields such as:

- `symbol`
- `market`
- `event_date`
- `event_type` or equivalent source-fact classification such as suspension, resumption, temporary suspension, or continued suspension
- optional `start_date`
- optional `end_date`
- optional `reason`
- optional `raw_status`
- optional source-provided exchange or board metadata
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
- `coordination/reports/TASK-052_REPORT.md`

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

Extend DataHub dataset registry/schema/semantic-rule coverage with a dedicated suspension/resumption source-fact contract.

Do not encode buy/sell advice, ranking, stock-picking, strategy triggers, risk rules, alert logic, or derived FeatureHub indicators. This task is only about source data facts and validation.

### 2. Source capability mapping

Update `quant/datahub/source_capabilities.py` so `a_share_suspension_resumption` maps to the new dedicated contract instead of only `DatasetName.CORPORATE_ACTIONS`.

Keep status conservative:

- Do not mark the capability `covered`.
- Use `planned` if this task only defines the contract and leaves source adapters pending.
- Use `partial` only if existing code already truthfully provides validated source coverage for the new contract.

Update `gap_reason` and `recommended_handoff_theme` to state that the contract exists but adapter/source implementation remains pending.

### 3. Source catalog alignment

If the new dataset is added to a source family, keep source stage and credential truth unchanged. Do not imply implemented adapter coverage where none exists.

For public AKShare follow-up readiness, it is acceptable to list the new dataset under `akshare_cn_hk_public_family` only if catalog wording clearly remains source-capability/catalog coverage, not broad implemented ingestion.

### 4. Offline tests

Add deterministic tests proving:

- the new dataset name is registered
- the new dataset has a schema and semantic-rule coverage
- representative valid fixture records pass registry validation
- invalid required-field or type examples fail validation
- `a_share_suspension_resumption` has the dedicated dataset mapping and remains not `covered`
- source catalog alignment remains truthful
- default tests perform no live network access

## Testing Requirements

Default tests must be offline.

Live tests are forbidden for TASK-052.

Run focused tests:

`python3 -m unittest tests/datahub/test_datasets.py`

`python3 -m unittest tests/datahub/test_source_capabilities.py`

Run source-catalog tests if `source_catalog.py` changes:

`python3 -m unittest tests/datahub/test_source_catalog.py`

Run full DataHub default tests:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

If any command cannot run, report the exact command and reason in `coordination/reports/TASK-052_REPORT.md`.

## Acceptance Criteria

The task is acceptable when:

- a stable DataHub suspension/resumption source-fact contract exists
- `a_share_suspension_resumption` has an explicit dedicated dataset mapping and remains conservatively classified
- deterministic offline tests cover registry/schema/semantic/source-capability/catalog behavior
- no real source adapter or live fetch logic is added
- no future-phase modules are modified
- report exists at `coordination/reports/TASK-052_REPORT.md`
- report includes files changed, tests run, default network behavior, live-enabled status, deviations, and follow-up tasks

## Report Path

`coordination/reports/TASK-052_REPORT.md`

## Review Path

`coordination/reviews/TASK-052_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-052_INTEGRATION.md`
