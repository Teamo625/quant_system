# Context Snapshot

Last updated by: 5.5 Controller
Last updated after: TASK-039 closure, Phase 2 completion, and TASK-040 dispatch

## Project Role and Scope

This repository is a phased personal quantitative research and signal system focused on A-shares, Hong Kong stocks, ETFs/funds, indices, sectors/concepts, macro data, and policy/news/announcement data.

Phase 2 DataHub comprehensive source collection is complete for the current approved scope.

The only implementation area currently open is FeatureHub:

- `quant/features/`
- `tests/features/`

Modules still placeholder-only until their phases are explicitly opened by the controller:

- `quant/strategies/`
- `quant/backtest/`
- `quant/scanner/`
- `quant/portfolio/`
- `quant/notification/`
- `quant/ai/`
- `quant/ui/`

DataHub implementation is no longer the active phase, but its stable contracts and local outputs are the approved upstream dependency for FeatureHub. FeatureHub must not fetch live market data or bypass DataHub contracts.

Default tests must remain offline. Live data tests are allowed only when explicitly marked, environment-gated, and permitted by a handoff. Real-source adapter work remains DataHub-owned and still requires gated live smoke evidence when such work is explicitly reopened by the controller.

If a live-enabled smoke fails or skips because of network, proxy, DNS, TLS, upstream, or public-source availability, the controller must keep the task open, dispatch a 5.3 execution rework for diagnosis and feasible code/test/report fixes, and require fresh Review Agent acceptance plus integration before closure.

## Current Phase

Current phase: Phase 3 - FeatureHub.

Phase 3 is not complete.

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

Phase 2 is complete after TASK-039.

Completed Phase 2 work:

- `TASK-006` through `TASK-011`: comprehensive DataHub source catalog, expanded dataset/schema contracts, semantic validation, rule integrity checks, and source adapter contract foundation
- `TASK-012` through `TASK-024`: first accepted real-source slices across A-share, HK, ETF/fund NAV, index, sector, global equity, news, announcements, and China macro domains, including required live-smoke evidence and rework closure where needed
- `TASK-025`: local refresh metadata and `DATA_QUALITY_REPORT` baseline
- `TASK-026` through `TASK-035`: additional A-share, HK, ETF/fund, policy, valuation, capital-flow, corporate-action, instrument-master, holdings, and fund-profile slices with accepted review/integration and live evidence where required
- `TASK-036`: source catalog implementation reconciliation
- `TASK-037`: HKEX Hong Kong `TRADING_CALENDAR` adapter
- `TASK-038`: AKShare China ETF exchange-traded `DAILY_BARS` adapter after live-network rework
- `TASK-039`: local-only DataHub warehouse refresh runner tying `SourceResult` fetch output to raw JSONL persistence, curated schema-validated persistence, refresh metadata, and `DATA_QUALITY_REPORT` output

TASK-039 review result:

- `coordination/reviews/TASK-039_REVIEW.md`
- Decision: ACCEPTED
- Independent verification: full DataHub default suite passed (`Ran 631 tests ... OK (skipped=25)`)
- No blocking findings

TASK-039 integration result:

- `coordination/integrations/TASK-039_INTEGRATION.md`
- Result: INTEGRATED / READY FOR CONTROLLER CLOSURE
- No conflicts or scope violations
- Default tests remain offline-safe
- No live-enabled test was required because TASK-039 was local-only

## Active Task

Active task: `TASK-040` - FeatureHub foundation contracts.

Handoff:

- `coordination/handoffs/TASK-040_FEATUREHUB_FOUNDATION_CONTRACTS.md`

Expected report:

- `coordination/reports/TASK-040_REPORT.md`

Expected review:

- `coordination/reviews/TASK-040_REVIEW.md`

Expected integration:

- `coordination/integrations/TASK-040_INTEGRATION.md`

TASK-040 scope focus:

- open `quant/features/` for Phase 3 implementation
- add a minimal importable FeatureHub package and contract module
- define typed primitives for future feature output records
- validate required fields, feature names, source dataset references, value types, and schema version
- add deterministic offline tests under `tests/features/`
- do not implement real feature calculations
- do not implement scanner, strategy, backtest, portfolio, signal, risk, notification, AI, UI, or automated trading logic
- do not change DataHub implementation files
- do not perform live network calls

## Phase Gate Decision

After TASK-039 review/integration results, Phase 2 is controller-closed as Done and Phase 3 is opened.

Reason: TASK-039 is accepted, integrated, and counted Done. It closes the remaining explicit Phase 2 local warehouse gap by adding local raw/curated persistence, refresh metadata, and quality report output around existing DataHub source contracts. TASK-006 through TASK-039 now cover the approved Phase 2 catalog, contracts, source slices, live-smoke governance, local persistence, metadata, and quality requirements. No concrete Phase 2 task remains Ready, In Progress, In Review, or Ready to Integrate. Remaining DataHub expansion ideas are future blocked extensions, not active Phase 2 lifecycle tasks.

Controller action taken:

- Phase 2 marked Completed.
- Phase 3 marked In progress.
- TASK-039 closed as Done.
- TASK-040 FeatureHub foundation contracts dispatched as the first Phase 3 task.

Phase switch: YES.

## Coordination Notes

Controller-owned files remain the source of truth for phase and task state:

- `coordination/PROJECT_STATE.md`
- `coordination/ROADMAP.md`
- `coordination/TASK_BOARD.md`
- `coordination/CONTEXT_SNAPSHOT.md`

Execution windows must not modify controller-owned files. They should only follow the active handoff and write the required report.

For TASK-040 specifically, the implementation must remain a FeatureHub contract foundation. It may reference DataHub dataset names as contract inputs if useful, but it must not alter `quant/datahub/**`, fetch live data, compute real indicators, or cross into scanner/strategy/backtest/signal/UI phases.
