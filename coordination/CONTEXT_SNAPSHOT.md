# Context Snapshot

Last updated by: 5.5 Controller
Last updated after: owner opened Phase 2.5 and dispatched TASK-041

## Project Role and Scope

This repository is a phased personal quantitative research and signal system focused on A-shares, Hong Kong stocks, ETFs/funds, indices, sectors/concepts, macro data, and policy/news/announcement data.

Phase 2 DataHub comprehensive source collection is complete for its original approved scope.

The owner clarified that the next milestone is not collecting all market data locally. The next milestone is completing DataHub source capability so the system can access all data domains needed for rigorous short-term and medium/long-term quant research when requested.

The only implementation area currently open is DataHub Phase 2.5 source-capability work:

- `quant/datahub/`
- `tests/datahub/`

Modules still placeholder-only until their phases are explicitly opened by the controller:

- `quant/features/` (paused until Phase 3 is reopened)
- `quant/strategies/`
- `quant/backtest/`
- `quant/scanner/`
- `quant/portfolio/`
- `quant/notification/`
- `quant/ai/`
- `quant/ui/`

FeatureHub TASK-040 was dispatched after Phase 2, but it has no report/review/integration artifacts. It is now paused and moved back to the Phase 3 backlog.

Default tests must remain offline. Live data tests are allowed only when explicitly marked, environment-gated, and permitted by a handoff. Real-source adapter work remains DataHub-owned and still requires gated live smoke evidence when such work is explicitly reopened by the controller.

If a live-enabled smoke fails or skips because of network, proxy, DNS, TLS, upstream, or public-source availability, the controller must keep the task open, dispatch a 5.3 execution rework for diagnosis and feasible code/test/report fixes, and require fresh Review Agent acceptance plus integration before closure.

## Current Phase

Current phase: Phase 2.5 - DataHub Trading-Grade Source Capability.

Phase 2.5 is not complete.

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

## Phase 2.5

Phase 2.5 was opened after owner clarification.

Purpose:

- define and close the gap between current Phase 2 narrow source slices and a complete trading-grade source-capability layer
- ensure DataHub can access all data domains needed for short-term and medium/long-term quant research
- avoid requiring all data to be collected locally during this phase

Important distinction:

- In scope: source capability, contracts, adapter readiness, coverage/gap metadata, offline tests, gated live smokes when explicitly assigned
- Out of scope: broad full-market collection, full-history backfill, FeatureHub calculations, scanner ranking, strategy/backtest/signal/risk/portfolio/AI/notification/UI/automated trading

## Active Task

Active task: `TASK-041` - DataHub trading-grade source capability audit.

Handoff:

- `coordination/handoffs/TASK-041_DATAHUB_TRADING_GRADE_SOURCE_CAPABILITY_AUDIT.md`

Expected report:

- `coordination/reports/TASK-041_REPORT.md`

Expected review:

- `coordination/reviews/TASK-041_REVIEW.md`

Expected integration:

- `coordination/integrations/TASK-041_INTEGRATION.md`

TASK-041 scope focus:

- add a deterministic DataHub source-capability audit/gap matrix
- represent short-term and medium/long-term quant data requirements
- map capabilities to current `DatasetName` contracts and source catalog entries where applicable
- mark capabilities as covered, partial, missing, or planned
- expose helper functions for missing/partial/no-contract/planned-or-credentialed gaps
- add deterministic offline tests under `tests/datahub/`
- do not collect full-market or full-history data locally
- do not implement scanner, strategy, backtest, portfolio, signal, risk, notification, AI, UI, or automated trading logic
- do not perform live network calls; live tests are forbidden for TASK-041

## Phase Decision

After TASK-039 review/integration results, Phase 2 was controller-closed as Done and Phase 3 was initially opened with TASK-040.

Owner clarification changed the next priority before TASK-040 execution: the project should complete DataHub source capability before moving into FeatureHub. Current Phase 2 source slices are useful but not a complete trading-grade source-capability layer.

Controller action taken:

- Phase 2 remains Completed for its original scope.
- Phase 3 is returned to Planned/blocked status before TASK-040 execution.
- Phase 2.5 is opened as In progress.
- TASK-041 DataHub trading-grade source capability audit is dispatched as the first Phase 2.5 task.
- TASK-040 FeatureHub foundation contracts remains available as a blocked Phase 3 backlog task.

Phase switch: YES, to Phase 2.5.

## Coordination Notes

Controller-owned files remain the source of truth for phase and task state:

- `coordination/PROJECT_STATE.md`
- `coordination/ROADMAP.md`
- `coordination/TASK_BOARD.md`
- `coordination/CONTEXT_SNAPSHOT.md`

Execution windows must not modify controller-owned files. They should only follow the active handoff and write the required report.

For TASK-041 specifically, the implementation must remain a DataHub capability audit. It may add deterministic source-capability metadata and tests, but it must not fetch live data, collect all market data locally, compute features, or cross into scanner/strategy/backtest/signal/UI phases.
