# TASK-042: DataHub Missing Source Dataset Contracts

## Task ID

TASK-042

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2.5: DataHub Trading-Grade Source Capability

## Context

TASK-041 completed the deterministic DataHub trading-grade source capability audit and was accepted by Review and Integration. The audit intentionally identified required Phase 2.5 capabilities that still have no stable `DatasetName` mapping.

Per the TASK-041 integration recommendation, the next executable task should define missing stable contracts before adapter work. This task is contract-only: it must not add live source fetching, broad collection, feature calculation, scanning, strategy, backtest, portfolio, signal, AI, notification, UI, or automated trading logic.

The execution window must read:

- `AGENTS.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-042_DATAHUB_MISSING_SOURCE_DATASET_CONTRACTS.md`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/datasets.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_datasets.py`

## Goal

Add stable DataHub dataset contracts for required TASK-041 capabilities that currently have no `DatasetName` mapping, so later Phase 2.5 adapter handoffs can target explicit contracts.

This task should close the contract gap only. It should not fetch data or implement source adapters.

## Required Contract Targets

Add or update canonical contracts for these required capability gaps from TASK-041:

- `a_share_minute_bars`
- `a_share_margin_financing_and_lending`
- `a_share_financial_statements`
- `a_share_financial_indicators`
- `a_share_major_activity_events`
- `hk_financial_data`
- `fund_flow`

The optional `hk_minute_bars` capability may remain without a dataset mapping in this task unless the implementation can map it to a generic minute-bar contract without widening scope.

Suggested new `DatasetName` contracts:

- `MINUTE_BARS`
- `MARGIN_FINANCING_LENDING`
- `FINANCIAL_STATEMENTS`
- `FINANCIAL_INDICATORS`
- `MAJOR_ACTIVITY_EVENTS`
- `FUND_FLOW`

Use generic cross-market contracts where appropriate, especially for financial statements and indicators, with explicit `market` fields so A-share and Hong Kong financial capability mappings do not require duplicate schemas.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-042_REPORT.md`

Expected implementation locations:

- `quant/datahub/datasets.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/__init__.py` only if exports need adjustment
- `quant/datahub/source_catalog.py` only if source-catalog dataset coverage must be aligned with the new contracts
- `tests/datahub/test_datasets.py`
- `tests/datahub/test_source_capabilities.py`
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

### 1. Dataset registry contracts

Extend `DatasetName`, `DatasetRegistry` metadata, schemas, and semantic-rule coverage for the required new contracts.

Each schema must include stable provenance fields consistent with existing contracts:

- `source`
- optional `source_ts`
- `ingested_at`
- `schema_version`

Keep required fields conservative and source-truth friendly. Optional fields are acceptable where public or credentialed sources may not provide every metric.

### 2. Source capability mapping

Update `quant/datahub/source_capabilities.py` so the required capability gaps listed above have stable `dataset_mappings`.

After this task, `get_capabilities_without_dataset_mapping()` may still include optional `hk_minute_bars`, but it should not include required capabilities unless the report explains a deliberate deferral.

Status values should remain conservative:

- Do not mark a capability `covered` merely because a contract exists.
- Use `planned` or `partial` where adapter/source implementation remains pending.
- Update `gap_reason` and `recommended_handoff_theme` to reflect that the contract is now defined but source adapter work remains.

### 3. Source catalog alignment

If new dataset contracts are added to source family coverage, keep source families at their existing truthful stages and credential requirements. Do not imply implemented adapter coverage where none exists.

### 4. Offline tests

Add deterministic tests proving:

- the new dataset names are registered
- each new dataset has a schema and semantic-rule entry
- representative valid fixture records pass registry validation
- invalid required-field or type examples fail validation
- TASK-041 required no-mapping capabilities now have dataset mappings, except any explicitly deferred optional capability
- default tests perform no live network access

### 5. Scope boundaries

Do not implement:

- source adapters
- live source calls
- broad live downloading
- full-market collection
- full-history backfill
- scheduler/orchestration/retry framework
- feature calculations
- scanner ranking or stock picking
- strategy, backtest, portfolio, signal, risk, notification, AI, UI, or automated trading logic

## Testing Requirements

Default tests must be offline.

Live tests are forbidden for TASK-042.

Run focused tests:

`python3 -m unittest tests/datahub/test_datasets.py`

`python3 -m unittest tests/datahub/test_source_capabilities.py`

Run source-catalog tests if `source_catalog.py` changes:

`python3 -m unittest tests/datahub/test_source_catalog.py`

Run full DataHub default tests:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

If any command cannot run, report the exact command and reason in `coordination/reports/TASK-042_REPORT.md`.

## Acceptance Criteria

The task is acceptable when:

- stable dataset contracts exist for the required TASK-041 no-mapping capability gaps
- required capabilities listed in this handoff have `DatasetName` mappings in the source-capability audit
- tests validate new registry/schema/semantic behavior without live network access
- no real source adapter or live fetch logic is added
- no future-phase modules are modified
- report exists at `coordination/reports/TASK-042_REPORT.md`
- report includes files changed, tests run, default network behavior, live-enabled status, deviations, and follow-up tasks

## Report Path

`coordination/reports/TASK-042_REPORT.md`

## Review Path

`coordination/reviews/TASK-042_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-042_INTEGRATION.md`
