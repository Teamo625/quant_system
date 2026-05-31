# Context Snapshot

Last updated by: 5.5 Controller
Last updated after: TASK-043 controller closure and TASK-044 dispatch

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

Completed Phase 2.5 work:

- `TASK-041`: deterministic trading-grade source capability audit and gap matrix under `quant/datahub/source_capabilities.py`
- `TASK-042`: stable DataHub dataset contracts for required TASK-041 no-mapping capability gaps
- `TASK-043`: narrow public AKShare Hong Kong `FINANCIAL_STATEMENTS` / `FINANCIAL_INDICATORS` adapter slice

TASK-041 review result:

- `coordination/reviews/TASK-041_REVIEW.md`
- Decision: ACCEPTED
- Independent verification: DataHub default suite passed (`Ran 639 tests ... OK (skipped=25)`)
- No blocking findings

TASK-041 integration result:

- `coordination/integrations/TASK-041_INTEGRATION.md`
- Result: INTEGRATED / READY FOR CONTROLLER CLOSURE
- No conflicts or scope violations
- No live tests were introduced or run; live status remained `SKIP` because the handoff forbade live tests

TASK-041 follow-up queue after TASK-042:

- required capabilities that had no stable `DatasetName` mapping now have contracts and mappings
- affected capability areas include A-share minute bars, margin financing/securities lending, financial statements, financial indicators, major activity events, Hong Kong financial data, and fund flow
- optional HK minute bars may remain a later feasibility item

TASK-042 review result:

- `coordination/reviews/TASK-042_REVIEW.md`
- Decision: ACCEPTED
- Independent verification: DataHub default suite passed (`Ran 642 tests ... OK (skipped=25)`)
- No blocking findings

TASK-042 integration result:

- `coordination/integrations/TASK-042_INTEGRATION.md`
- Result: INTEGRATED / READY FOR CONTROLLER CLOSURE
- No conflicts or scope violations
- No live tests were introduced or run; live status remained `SKIP` because the handoff forbade live tests

TASK-042 closed the required no-`DatasetName` contract gap by adding contracts and mappings for:

- `MINUTE_BARS`
- `MARGIN_FINANCING_LENDING`
- `FINANCIAL_STATEMENTS`
- `FINANCIAL_INDICATORS`
- `MAJOR_ACTIVITY_EVENTS`
- `FUND_FLOW`

Remaining Phase 2.5 work is adapter/source-capability implementation for planned or partial capabilities. Optional `hk_minute_bars` remains a later feasibility item.

TASK-043 review result:

- `coordination/reviews/TASK-043_REVIEW.md`
- Decision: ACCEPTED
- Independent verification: focused offline tests, source capability tests, default gated live test skip path, and live-enabled HK financial smoke all passed
- No blocking findings

TASK-043 integration result:

- `coordination/integrations/TASK-043_INTEGRATION.md`
- Result: INTEGRATED / READY FOR CONTROLLER CLOSURE
- No conflicts or scope violations
- Default tests remain offline-safe
- Live-enabled TASK-043 smoke result was PASS, so no live-network rework gate is required

TASK-043 added `AkshareHKFinancialDataAdapter` for one requested HK symbol under source `akshare_cn_hk_public_family`, supporting:

- `DatasetName.FINANCIAL_STATEMENTS`
- `DatasetName.FINANCIAL_INDICATORS`

It updated `hk_financial_data` from `planned` to `partial`, preserving breadth/history limitations in the capability truth.

## Active Task

Active task: `TASK-044` - DataHub AKShare A-share financial data adapter.

Handoff:

- `coordination/handoffs/TASK-044_DATAHUB_AKSHARE_A_SHARE_FINANCIAL_DATA_ADAPTER.md`

Expected report:

- `coordination/reports/TASK-044_REPORT.md`

Expected review:

- `coordination/reviews/TASK-044_REVIEW.md`

Expected integration:

- `coordination/integrations/TASK-044_INTEGRATION.md`

TASK-044 scope focus:

- implement a narrow AKShare-backed A-share financial data adapter for one requested A-share stock symbol
- produce validated `FINANCIAL_STATEMENTS` and `FINANCIAL_INDICATORS` records under `market=A_SHARE` and `source=akshare_cn_hk_public_family`
- keep the task public-source only: no Tushare, credentials, cookies, tokens, private account data, browser scraping, or cross-source fallback
- add deterministic offline adapter tests and a gated live smoke skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1`
- if live-enabled smoke fails or skips due to network/proxy/DNS/TLS/upstream/source availability, the execution report must include root-cause evidence and feasible fixes attempted, and controller closure will require live-rework review/integration gates
- do not implement broad A-share universe ingestion, full financial history backfill, Hong Kong financial adapters, FeatureHub, scanner, strategy, backtest, portfolio, signal, risk, notification, AI, UI, or automated trading logic

## Phase Decision

After TASK-039 review/integration results, Phase 2 was controller-closed as Done and Phase 3 was initially opened with TASK-040.

Owner clarification changed the next priority before TASK-040 execution: the project should complete DataHub source capability before moving into FeatureHub. Current Phase 2 source slices are useful but not a complete trading-grade source-capability layer.

Previous controller action:

- Phase 2 remains Completed for its original scope.
- Phase 3 is returned to Planned/blocked status before TASK-040 execution.
- Phase 2.5 is opened as In progress.
- TASK-040 FeatureHub foundation contracts remains available as a blocked Phase 3 backlog task.

Previous controller action:

- TASK-041 is closed as Done.
- Phase 2.5 remains In progress because TASK-041 identified required source-capability contract gaps.
- TASK-042 DataHub missing source dataset contracts is dispatched as the next Phase 2.5 task.

Phase switch: NO.

Current controller action:

- TASK-043 is closed as Done.
- Phase 2.5 remains In progress because TASK-043 only closed a narrow HK public-source financial slice; planned or partial source-capability implementation remains.
- TASK-044 DataHub AKShare A-share financial data adapter is dispatched as the next Phase 2.5 task.

Phase switch: NO.

## Coordination Notes

Controller-owned files remain the source of truth for phase and task state:

- `coordination/PROJECT_STATE.md`
- `coordination/ROADMAP.md`
- `coordination/TASK_BOARD.md`
- `coordination/CONTEXT_SNAPSHOT.md`

Execution windows must not modify controller-owned files. They should only follow the active handoff and write the required report.

For TASK-044 specifically, the implementation must remain a narrow DataHub public-source A-share financial data adapter slice. It may add adapter code, exports, source-capability truth updates, focused source-catalog alignment, offline tests, a gated live smoke, and the required execution report, but it must not use credentials or private account data, implement broad A-share universe ingestion, full financial history backfill, Hong Kong financial adapters, FeatureHub, scanner, strategy, backtest, signal, risk, notification, AI, UI, or automated trading logic.
