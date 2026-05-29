# Context Snapshot

Last updated by: 5.5 Controller
Last updated after: TASK-035 closure and TASK-036 dispatch

## Project Role and Scope

This repository is a phased personal quantitative research and signal system focused on A-shares, Hong Kong stocks, ETFs/funds, indices, sectors/concepts, macro data, and policy/news/announcement data.

The only implementation area currently open is DataHub:

- `quant/datahub/`
- `tests/datahub/`

Future modules remain placeholder-only until their phases are explicitly opened by the controller:

- `quant/features/`
- `quant/strategies/`
- `quant/backtest/`
- `quant/scanner/`
- `quant/portfolio/`
- `quant/notification/`
- `quant/ai/`
- `quant/ui/`

Default tests must remain offline. For any Phase 2 task that implements a real source adapter or real data-fetching behavior, an explicitly gated live smoke test is mandatory. Live smoke tests must be skipped by default and enabled only by `QUANT_SYSTEM_LIVE_TESTS=1` plus explicit handoff permission.

If a live-enabled smoke fails or skips because of network, proxy, DNS, TLS, upstream, or public-source availability, the controller must keep the task open, dispatch a 5.3 execution rework for diagnosis and feasible code/test/report fixes, and require fresh Review Agent acceptance plus integration before closure.

## Current Phase

Current phase: Phase 2 - DataHub Comprehensive Source Collection.

Phase 2 is not complete.

## Completed Work

### Phase 0

`PHASE-0-INIT` completed the initial coordination baseline.

### Phase 1

Phase 1 completed foundational DataHub preparation:

- `TASK-001`: package skeleton and architecture placeholders
- `TASK-002`: local storage baseline
- `TASK-003`: provider and contract baseline
- `TASK-004`: adjustment/trading-calendar foundations
- `TASK-005`: DataHub quality/reporting baseline

### Phase 2

The original selected-adapter TASK-006 through TASK-009 line was removed after the owner expanded Phase 2 to comprehensive source collection.

Completed Phase 2 tasks after the rescope:

- `TASK-006`: DataHub comprehensive source catalog
- `TASK-007`: expanded domain schema contracts
- `TASK-008`: expanded contract semantic validation
- `TASK-009`: explicit semantic validation rules
- `TASK-010`: semantic rule integrity checks
- `TASK-011`: source adapter contract foundation
- `TASK-012`: AKShare A-share daily bar adapter
- `TASK-013`: AKShare A-share trading calendar adapter
- `TASK-014`: AKShare Hong Kong daily bar adapter
- `TASK-015`: AKShare ETF/fund NAV snapshot adapter
- `TASK-016`: AKShare China index daily bar adapter
- `TASK-017`: AKShare sector daily bar adapter with live-network rework closure and live-enabled PASS evidence
- `TASK-018`: AKShare sector master adapter with live duplicate rework closure and live-enabled PASS evidence
- `TASK-019`: AKShare sector membership adapter with live evidence + live PASS rework closure
- `TASK-020`: AKShare index constituents adapter with live-enabled PASS evidence
- `TASK-021`: AKShare global equity snapshot adapter with live-route rework closure and live-enabled PASS evidence
- `TASK-022`: AKShare news events adapter with live-enabled PASS evidence
- `TASK-023`: HKEX company announcements adapter with symbol-filter rework closure and live-enabled PASS evidence
- `TASK-024`: AKShare China macro adapter with `is_preliminary` rework closure and live-enabled PASS evidence
- `TASK-025`: local refresh metadata and `DATA_QUALITY_REPORT` baseline with offline-only PASS evidence
- `TASK-026`: AKShare A-share `instrument_master` adapter with live-enabled PASS evidence
- `TASK-027`: AKShare A-share `corporate_actions` dividend/corporate-action slice with live-enabled PASS evidence
- `TASK-028`: AKShare A-share `valuation_snapshot` adapter with live-network rework closure and live-enabled PASS evidence; `float_market_cap` is optional to preserve source-truth behavior
- `TASK-029`: AKShare A-share `capital_flow_snapshot` adapter with live-network rework closure and live-enabled PASS evidence; primary AKShare route remains preferred, with bounded one-symbol datacenter fallback only for source/network unavailability
- `TASK-030`: public `POLICY_DOCUMENTS` adapter under `macro_policy_public_sources` with live-enabled PASS evidence
- `TASK-031`: AKShare ETF/fund `FUND_HOLDINGS` one-fund adapter with classifier rework closure and live-enabled PASS evidence
- `TASK-032`: AKShare Hong Kong stock `INSTRUMENT_MASTER` one-symbol adapter with live-enabled PASS evidence
- `TASK-033`: AKShare Hong Kong stock `CORPORATE_ACTIONS` one-symbol dividend/corporate-action adapter with live-enabled PASS evidence
- `TASK-034`: AKShare Hong Kong stock `VALUATION_SNAPSHOT` one-symbol adapter with minimal HK source-catalog alignment and live-enabled PASS evidence
- `TASK-035`: AKShare `FUND_PROFILE` one-fund adapter under `akshare_cn_hk_public_family` with live-enabled PASS evidence

## Active Task

Active task: `TASK-036` - DataHub source catalog implementation reconciliation.

Handoff:

- `coordination/handoffs/TASK-036_DATAHUB_SOURCE_CATALOG_RECONCILIATION.md`

Expected report:

- `coordination/reports/TASK-036_REPORT.md`

Expected review:

- `coordination/reviews/TASK-036_REVIEW.md`

Expected integration:

- `coordination/integrations/TASK-036_INTEGRATION.md`

TASK-036 scope focus:

- reconcile `quant/datahub/source_catalog.py` with accepted DataHub implementation coverage through TASK-035
- ensure AKShare `INDEX_CONSTITUENTS` coverage from TASK-020 is represented in dataset and `INDEX_DATA` stable coverage
- ensure AKShare A-share `CORPORATE_ACTIONS` coverage from TASK-027 is represented in `A_SHARE_FULL_DATA` stable coverage
- preserve accepted HK valuation and fund profile catalog coverage from TASK-034 and TASK-035
- add or update focused offline tests in `tests/datahub/test_source_catalog.py`
- preserve default tests as offline-safe
- do not add live tests or run `QUANT_SYSTEM_LIVE_TESTS=1`; TASK-036 is catalog-only and offline
- do not implement adapters, route changes, storage orchestration, schema changes, or broad source claims
- do not expand to non-DataHub modules

## Phase Gate Decision

After TASK-035 review/integration results, Phase 2 remains open.

Reason: TASK-035 is accepted, integrated, and counted Done, but Phase 2 still has required DataHub source coverage and catalog-maintenance work beyond TASK-035. The next executable gap is reconciling the DataHub source catalog with accepted implementation coverage before further adapter expansion.

Controller action taken:

- Phase remains Phase 2.
- TASK-035 is closed as Done.
- TASK-036 source catalog implementation reconciliation was dispatched as the next executable task.

Phase switch: NO.

## Coordination Notes

Controller-owned files remain the source of truth for phase and task state:

- `coordination/PROJECT_STATE.md`
- `coordination/ROADMAP.md`
- `coordination/TASK_BOARD.md`
- `coordination/CONTEXT_SNAPSHOT.md`

Execution windows must not modify controller-owned files. They should only follow the active handoff and write the required report.

For real-source adapter work, execution windows must keep default tests offline, provide mandatory gated live smoke evidence, and diagnose/fix live blockers within the handoff's allowed files where feasible before review and integration.

For TASK-036 specifically, no live smoke is required or allowed because the handoff is catalog-only and offline.
