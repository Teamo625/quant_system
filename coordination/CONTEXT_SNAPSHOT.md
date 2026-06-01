# Context Snapshot

Last updated by: 5.5 Controller
Last updated after: TASK-049 controller closure and TASK-050 dispatch

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
- `TASK-044`: narrow public AKShare A-share `FINANCIAL_STATEMENTS` / `FINANCIAL_INDICATORS` adapter slice
- `TASK-045`: narrow public AKShare A-share `MARGIN_FINANCING_LENDING` adapter slice, including live skip/fail classifier rework
- `TASK-046`: narrow public AKShare A-share `COMPANY_ANNOUNCEMENTS` adapter slice
- `TASK-047`: dedicated DataHub `LIMIT_UP_DOWN_EVENTS` source-fact contract for A-share limit-up/down capability
- `TASK-048`: narrow public AKShare A-share `LIMIT_UP_DOWN_EVENTS` adapter slice
- `TASK-049`: narrow public AKShare A-share `MAJOR_ACTIVITY_EVENTS` adapter slice, including live-route rework closure

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

TASK-044 review result:

- `coordination/reviews/TASK-044_REVIEW.md`
- Decision: ACCEPTED
- Independent verification: focused offline tests, source capability/catalog tests, default gated live test skip path, full DataHub default suite, and live-enabled A-share financial smoke all passed
- No blocking findings

TASK-044 integration result:

- `coordination/integrations/TASK-044_INTEGRATION.md`
- Result: INTEGRATED / READY FOR CONTROLLER CLOSURE
- No conflicts or scope violations
- Default tests remain offline-safe
- Live-enabled TASK-044 smoke result was PASS, so no live-network rework gate is required

TASK-044 added `AkshareAShareFinancialDataAdapter` for one requested A-share symbol under source `akshare_cn_hk_public_family`, supporting:

- `DatasetName.FINANCIAL_STATEMENTS`
- `DatasetName.FINANCIAL_INDICATORS`

It updated `a_share_financial_statements` and `a_share_financial_indicators` from `planned` to `partial`, preserving breadth/history limitations in the capability truth.

TASK-045 execution report:

- `coordination/reports/TASK-045_REPORT.md`
- Reported implementation of a narrow AKShare A-share `MARGIN_FINANCING_LENDING` adapter slice, then rework to tighten live skip/fail classification

TASK-045 review result:

- `coordination/reviews/TASK-045_REVIEW.md`
- Decision: ACCEPTED
- Independent verification: focused adapter tests, default gated live path, live-enabled smoke, shared AKShare regression, and full DataHub default suite passed
- No blocking findings or follow-up requirements remain

TASK-045 integration result:

- `coordination/integrations/TASK-045_INTEGRATION.md`
- Result: INTEGRATED / READY FOR CONTROLLER CLOSURE
- No conflicts or scope violations
- Default tests remain offline-safe
- Live-enabled TASK-045 rework smoke result was PASS, so no live-network rework gate remains

TASK-045 added public AKShare A-share `MARGIN_FINANCING_LENDING` coverage under source `akshare_cn_hk_public_family` and left `a_share_margin_financing_and_lending` as `partial`, preserving breadth/history limitations in the capability truth.

The TASK-045 rework removed route-name-only unavailable tokens from classifier surfaces so route-name-bearing AKShare argument/signature compatibility errors remain hard failures rather than live skips.

TASK-046 review result:

- `coordination/reviews/TASK-046_REVIEW.md`
- Decision: ACCEPTED
- Independent verification: focused offline adapter tests, default gated live skip path, source capability/catalog tests, full DataHub default suite, and live-enabled A-share company-announcement smoke all passed
- No blocking findings

TASK-046 integration result:

- `coordination/integrations/TASK-046_INTEGRATION.md`
- Result: INTEGRATED / READY FOR CONTROLLER CLOSURE
- No conflicts or scope violations
- Default tests remain offline-safe
- Live-enabled TASK-046 smoke result was PASS, so no live-network rework gate is required

TASK-046 added public AKShare A-share `COMPANY_ANNOUNCEMENTS` coverage under source `akshare_cn_hk_public_family` and left `a_share_company_announcements` as `partial`, preserving breadth/history limitations in the capability truth.

TASK-047 review result:

- `coordination/reviews/TASK-047_REVIEW.md`
- Decision: ACCEPTED
- Independent verification: focused dataset, source capability, source catalog, and full DataHub default tests passed
- No blocking findings

TASK-047 integration result:

- `coordination/integrations/TASK-047_INTEGRATION.md`
- Result: INTEGRATED / READY FOR CONTROLLER CLOSURE
- No conflicts or scope violations
- Default tests remain offline-safe
- No live-enabled test was required because TASK-047 was contract-only and live tests were forbidden by handoff

TASK-047 added a stable `DatasetName.LIMIT_UP_DOWN_EVENTS` contract for A-share limit-up/down source facts. It kept `a_share_limit_up_down` conservatively non-covered/planned so adapter/source implementation remains open.

TASK-048 review result:

- `coordination/reviews/TASK-048_REVIEW.md`
- Decision: ACCEPTED
- Independent verification: focused adapter tests, default gated live skip path, live-enabled smoke, source capability tests, and full DataHub default tests passed
- No blocking findings

TASK-048 integration result:

- `coordination/integrations/TASK-048_INTEGRATION.md`
- Result: INTEGRATED / READY FOR CONTROLLER CLOSURE
- No conflicts or scope violations
- Default tests remain offline-safe
- Live-enabled TASK-048 smoke result was PASS, so no live-network rework gate is required

TASK-048 added public AKShare A-share `LIMIT_UP_DOWN_EVENTS` coverage under source `akshare_cn_hk_public_family` and left `a_share_limit_up_down` as `partial`, preserving breadth/history limitations in the capability truth.

TASK-049 review result:

- `coordination/reviews/TASK-049_REVIEW.md`
- Decision: ACCEPTED
- Independent verification after live-route rework: focused adapter tests, default gated live path, and live-enabled smoke passed
- Rework diagnosis: prior `SKIP` came from first-date selection/control flow against AKShare `stock_dzjy_mrmx`, not adapter contract logic
- No blocking findings remain

TASK-049 integration result:

- `coordination/integrations/TASK-049_INTEGRATION.md`
- Result: INTEGRATED / READY FOR CONTROLLER CLOSURE
- Reviewed result: ACCEPTED
- No conflicts or scope violations
- Default tests remain offline-safe
- Live-enabled rework smoke result was PASS: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_major_activity_events_live.py` -> `Ran 7 tests ... OK`

## Active Task

Active task: `TASK-050` - DataHub AKShare A-share minute bars adapter.

Handoff:

- `coordination/handoffs/TASK-050_DATAHUB_AKSHARE_A_SHARE_MINUTE_BARS_ADAPTER.md`

Expected report:

- `coordination/reports/TASK-050_REPORT.md`

Expected review:

- `coordination/reviews/TASK-050_REVIEW.md`

Expected integration:

- `coordination/integrations/TASK-050_INTEGRATION.md`

TASK-050 scope focus:

- implement a narrow no-credential public AKShare A-share `MINUTE_BARS` adapter slice if local route shape supports it
- use candidate public route names such as `stock_zh_a_hist_min_em` or `stock_zh_a_minute`, but verify route shape with deterministic fixtures
- support one requested A-share symbol and bounded minute-bar request parameters only
- preserve source-fact OHLCV semantics only; do not encode derived features, scanner ranking, buy/sell advice, trading signals, or strategy rules
- keep default tests offline-safe and update deterministic tests for any route/timestamp/classification behavior
- add and run a gated live smoke with `QUANT_SYSTEM_LIVE_TESTS=1`
- update `coordination/reports/TASK-050_REPORT.md` with files changed, tests run, default network behavior, live-enabled PASS/SKIP/FAIL truth, root-cause evidence if applicable, deviations, and residual risks
- do not add broad collection, FeatureHub, scanner, strategy, backtest, portfolio, signal, risk, notification, AI, UI, automated trading, or derived trading-signal logic

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

Previous controller action:

- TASK-043 is closed as Done.
- Phase 2.5 remains In progress because TASK-043 only closed a narrow HK public-source financial slice; planned or partial source-capability implementation remains.
- TASK-044 DataHub AKShare A-share financial data adapter is dispatched as the next Phase 2.5 task.

Phase switch: NO.

Previous controller action:

- TASK-045 is closed as Done after accepted rework review and integration.
- Phase 2.5 remains In progress because planned or partial DataHub source-capability work remains after TASK-045.
- TASK-046 DataHub AKShare A-share company announcements adapter is dispatched as the next 5.3 execution handoff.

Phase switch: NO.

Previous controller action:

- TASK-046 is closed as Done after accepted review and integration.
- Phase 2.5 remains In progress because required planned or partial DataHub source-capability work remains after TASK-046.
- TASK-047 DataHub A-share limit-up/down contracts is dispatched as the next 5.3 execution handoff.

Phase switch: NO.

Previous controller action:

- TASK-047 is closed as Done after accepted review and integration.
- Phase 2.5 remains In progress because `a_share_limit_up_down` has a stable contract but still lacks implemented bounded public-source adapter coverage.
- TASK-048 DataHub AKShare A-share limit-up/down adapter is dispatched as the next 5.3 execution handoff.

Phase switch: NO.

Previous controller action:

- TASK-048 is closed as Done after accepted review and integration.
- Phase 2.5 remains In progress because required planned or partial DataHub source-capability work remains after TASK-048; `a_share_major_activity_events` has a stable contract but no implemented public-source adapter coverage yet.
- TASK-049 DataHub AKShare A-share major activity events adapter is dispatched as the next 5.3 execution handoff.

Phase switch: NO.

Current controller action:

- TASK-049 is closed as Done after accepted live-route rework review and integration.
- Phase 2.5 remains In progress because required planned or partial DataHub source-capability work remains; `a_share_minute_bars` has a stable contract but no implemented adapter coverage.
- TASK-050 DataHub AKShare A-share minute bars adapter is dispatched as the next 5.3 execution handoff.

Phase switch: NO.

## Coordination Notes

Controller-owned files remain the source of truth for phase and task state:

- `coordination/PROJECT_STATE.md`
- `coordination/ROADMAP.md`
- `coordination/TASK_BOARD.md`
- `coordination/CONTEXT_SNAPSHOT.md`

Execution windows must not modify controller-owned files. They should only follow the active handoff and write the required report.

For active TASK-050 specifically, execution must stay limited to a narrow no-credential AKShare public-source `MINUTE_BARS` adapter slice, deterministic offline tests, and the gated live smoke. It must not add credentials or private account data, broad collection, FeatureHub, scanner, strategy, backtest, signal, risk, notification, AI, UI, automated trading, or derived trading-signal logic.
