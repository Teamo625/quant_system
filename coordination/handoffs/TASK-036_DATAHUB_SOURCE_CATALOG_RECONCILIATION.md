# TASK-036: DataHub Source Catalog Implementation Reconciliation

## Task ID

TASK-036

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

TASK-035 has been accepted and integrated. It completed bounded AKShare `FUND_PROFILE` coverage for one requested China public fund record under source id `akshare_cn_hk_public_family`, with deterministic offline tests and live-enabled PASS evidence.

Phase 2 remains open. Before dispatching another data-source adapter, the source catalog should be reconciled with accepted Phase 2 implementation truth through TASK-035. Several accepted adapters now exist, but the default source catalog and its focused tests do not yet assert every implemented narrow coverage slice consistently.

This task must perform only source-catalog reconciliation for accepted DataHub implementation coverage. It must not implement a new source adapter or broaden source claims beyond completed, reviewed work.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-036_DATAHUB_SOURCE_CATALOG_RECONCILIATION.md`

## Goal

Reconcile `quant/datahub/source_catalog.py` and focused source-catalog tests so the DataHub catalog accurately reflects accepted implementation coverage through TASK-035, while preserving default offline-only behavior.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/source_catalog.py`
- `tests/datahub/test_source_catalog.py`
- `coordination/reports/TASK-036_REPORT.md`

Do not modify adapter implementations unless a failing catalog test proves a purely import/export-level correction is required. If such a correction is necessary, stop and report the blocker instead of expanding this handoff.

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
- `quant/datahub/adapters/**`
- `quant/features/**`
- `quant/strategies/**`
- `quant/backtest/**`
- `quant/scanner/**`
- `quant/portfolio/**`
- `quant/notification/**`
- `quant/ai/**`
- `quant/ui/**`

## Implementation Requirements

### 1. Reconcile accepted AKShare source coverage

Update only catalog coverage that is backed by accepted, integrated Phase 2 work through TASK-035.

At minimum, verify and align:

- `akshare_cn_hk_public_family.dataset_coverage` includes `DatasetName.INDEX_CONSTITUENTS`, because TASK-020 implemented and integrated the AKShare index constituents adapter.
- `InformationDomain.INDEX_DATA` stable datasets for `akshare_cn_hk_public_family` include both:
  - `DatasetName.INDEX_DAILY_BARS`
  - `DatasetName.INDEX_CONSTITUENTS`
- `InformationDomain.A_SHARE_FULL_DATA` stable datasets for `akshare_cn_hk_public_family` include `DatasetName.CORPORATE_ACTIONS`, because TASK-027 implemented and integrated the AKShare A-share corporate-actions slice.
- Existing accepted coverage from TASK-034 and TASK-035 remains present:
  - HK stock valuation remains listed under `InformationDomain.HK_STOCK_FULL_DATA`
  - fund profile remains listed under `InformationDomain.ETF_FUND_FULL_DATA`

Keep all changes minimal and source-truth based.

### 2. Do not add unimplemented broad claims

Do not add catalog claims for coverage that has not been implemented and accepted.

Specifically do not add:

- fund scale or fund flow datasets
- HK capital-flow coverage
- HK exchange trading-calendar coverage beyond the existing generic source-family planning entry
- ETF-specific profile adapter claims beyond the accepted bounded `FUND_PROFILE` support
- full-market ingestion claims where only one-symbol or bounded-slice adapters exist
- any future-phase module capability

### 3. Focused offline tests

Update or add deterministic tests in `tests/datahub/test_source_catalog.py` proving:

- `build_default_source_catalog().sources_for_dataset(DatasetName.INDEX_CONSTITUENTS)` includes `akshare_cn_hk_public_family`
- `stable_datasets_for_information_domain(InformationDomain.INDEX_DATA)` includes `DatasetName.INDEX_CONSTITUENTS`
- `stable_datasets_for_information_domain(InformationDomain.A_SHARE_FULL_DATA)` includes `DatasetName.CORPORATE_ACTIONS`
- existing assertions for `DatasetName.FUND_PROFILE`, HK valuation, macro, policy, news, announcements, and quality coverage still pass
- catalog helper behavior remains offline-only under the existing socket guard

The test changes must not import AKShare, instantiate live adapters, or call network routes.

### 4. No live smoke required

This is a catalog-only offline reconciliation task. It does not implement a real source adapter or real data-fetching behavior.

Do not add or run live tests for TASK-036.

## Do Not Implement

Do not implement:

- new adapters
- adapter route changes
- storage refresh orchestration
- schema contract changes
- live smoke tests
- broad source ingestion
- strategies, scanner logic, features, AI reports, notifications, UI, or automated trading

## Testing Requirements

Default tests must remain offline.

Run:

`python3 -m unittest tests/datahub/test_source_catalog.py`

Run related default regressions:

`python3 -m unittest tests/datahub/test_datasets.py`

`python3 -m unittest tests/datahub/test_source.py`

Run the full DataHub default suite if changes remain small and runtime is acceptable:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Do not run `QUANT_SYSTEM_LIVE_TESTS=1` for this task.

## Acceptance Criteria

The task is acceptable when:

- source catalog coverage accurately reflects accepted implementation through TASK-035
- no unimplemented broad source claims are added
- focused source-catalog tests prove the reconciled coverage
- default tests remain offline-safe
- no live tests are added or run
- no future-phase module contains new logic
- report exists at `coordination/reports/TASK-036_REPORT.md`

## Report Path

`coordination/reports/TASK-036_REPORT.md`

## Review Path

`coordination/reviews/TASK-036_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-036_INTEGRATION.md`

## Out of Scope

Everything outside DataHub source-catalog reconciliation and focused offline tests is out of scope.
