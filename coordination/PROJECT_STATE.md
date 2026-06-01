# Project State

Last updated by: 5.5 Controller

## Current Phase

Phase 2.5: DataHub Trading-Grade Source Capability.

## Current Implementation Scope

DataHub source-capability completion work is active.

Current implementation may target only:

- `quant/datahub/`
- `tests/datahub/`

## Repository Status

Initialized:

- governance rules
- system architecture documents
- module boundaries
- data contracts
- task protocol
- testing policy
- coordination files
- compressed context snapshot
- placeholder module directories
- first DataHub handoff
- TASK-001 through TASK-005 completed Phase 1 DataHub foundation work
- Phase 1 completed by phase gate decision
- previous pre-rescope TASK-006 through TASK-009 Phase 2 handoffs and related code were removed after owner-directed Phase 2 scope change
- Phase 2 goal changed from selected source adapters to comprehensive full-domain data-source collection coverage
- TASK-006 through TASK-011 completed Phase 2 catalog/schema/validation/source-contract foundations
- TASK-012 through TASK-024 completed the first accepted real-source DataHub slices across A-share, HK, ETF/fund NAV, index, sector, global equity, news, announcements, and China macro domains
- TASK-025 completed the local refresh metadata and `DATA_QUALITY_REPORT` baseline
- TASK-026 completed AKShare A-share `instrument_master`
- TASK-027 completed AKShare A-share `corporate_actions`
- TASK-028 completed AKShare A-share `valuation_snapshot` after live-network rework; `float_market_cap` remains optional to preserve source-truth behavior
- TASK-029 completed AKShare A-share `capital_flow_snapshot` after live-network rework; primary `stock_individual_fund_flow` remains preferred with bounded one-symbol datacenter fallback for `RPT_FUNDFLOW_SECUCODE` only when primary route is unavailable
- TASK-030 completed public policy document metadata coverage for `DatasetName.POLICY_DOCUMENTS` under source id `macro_policy_public_sources`, with accepted live-enabled PASS evidence
- TASK-031 completed AKShare ETF/fund `fund_holdings` one-fund adapter coverage after classifier rework; the previous `ssl.SSLError`/`NameError` live-unavailability blocker is closed with accepted review, integration, and live-enabled PASS evidence
- TASK-032 completed AKShare Hong Kong stock `instrument_master` one-symbol adapter coverage, with accepted review, integration, and live-enabled PASS evidence
- TASK-033 completed AKShare Hong Kong stock `corporate_actions` one-symbol dividend/corporate-action coverage, with accepted review, integration, and live-enabled PASS evidence
- TASK-034 completed AKShare Hong Kong stock `valuation_snapshot` one-symbol coverage, with accepted review, integration, minimal HK source-catalog alignment, and live-enabled PASS evidence
- TASK-035 completed AKShare `fund_profile` one-fund adapter coverage, with accepted review, integration, and live-enabled PASS evidence
- TASK-036 completed DataHub source catalog implementation reconciliation, with accepted review/integration and offline-only PASS evidence
- TASK-037 completed HKEX Hong Kong `trading_calendar` adapter coverage, with accepted review, integration, and live-enabled PASS evidence
- TASK-038 completed AKShare China ETF exchange-traded `daily_bars` coverage after live-network rework, with accepted review, integration, and live-enabled PASS evidence
- TASK-039 completed the local-only DataHub warehouse refresh runner, tying `SourceResult` fetch output to raw JSONL persistence, curated schema-validated persistence, refresh metadata, and `DATA_QUALITY_REPORT` output with accepted review/integration and offline-only PASS evidence
- Phase 2 completed by phase gate decision after TASK-039 controller closure
- Phase 3 was opened for FeatureHub with TASK-040, but no TASK-040 execution report/review/integration exists yet
- Owner clarified that the intended next priority is not full local data collection, but completing DataHub source capability so all data needed for short-term and medium/long-term quant research can be accessed on demand
- Phase 3 is paused before execution and Phase 2.5 is opened to close the trading-grade DataHub source-capability gap
- TASK-041 completed the deterministic Phase 2.5 trading-grade source capability audit and gap matrix, with accepted review/integration and offline-only PASS evidence
- TASK-041 identified required no-`DatasetName` capability gaps that needed stable DataHub contracts before adapter implementation could continue
- TASK-042 completed stable DataHub dataset contracts for required TASK-041 no-mapping gaps (`MINUTE_BARS`, `MARGIN_FINANCING_LENDING`, `FINANCIAL_STATEMENTS`, `FINANCIAL_INDICATORS`, `MAJOR_ACTIVITY_EVENTS`, and `FUND_FLOW`), with accepted review/integration and offline-only PASS evidence
- TASK-043 completed a narrow public AKShare Hong Kong `FINANCIAL_STATEMENTS` / `FINANCIAL_INDICATORS` adapter slice, moved `hk_financial_data` to `partial`, and provided accepted review/integration plus live-enabled PASS evidence
- TASK-044 completed a narrow public AKShare A-share `FINANCIAL_STATEMENTS` / `FINANCIAL_INDICATORS` adapter slice, moved `a_share_financial_statements` and `a_share_financial_indicators` to `partial`, and provided accepted review/integration plus live-enabled PASS evidence
- TASK-045 completed AKShare A-share `MARGIN_FINANCING_LENDING` one-symbol/date-slice adapter coverage after live skip/fail classifier rework; route-name-bearing AKShare argument/signature compatibility errors now remain hard failures, default tests remain offline-safe, and live-enabled rework smoke result was PASS

## Active Constraints

- Do not implement strategies.
- Do not implement scanner ranking or stock-picking logic.
- Do not implement backtest execution.
- Do not implement portfolio, signal, or risk logic.
- Do not implement AI reports.
- Do not implement notifications.
- Do not implement automated trading.
- Do not implement complex UI.
- Do not implement FeatureHub work while Phase 2.5 is active.
- Default tests must not use live network access.
- Live tests require explicit handoff permission and environment-variable gating.
- Real source adapter and real data-fetching tasks remain DataHub-owned and require a gated live smoke test when explicitly assigned; default tests must still skip it unless explicitly enabled.
- Live-enabled network/proxy/DNS/TLS/upstream failures must be routed to a 5.3 execution rework for diagnosis and feasible repository fixes, then independently reviewed before integration or controller closure.
- Execution windows must not update project state files.

## Prior Phase Gate Decision

Phase 2 remains complete for its original approved scope, but the owner has opened a new Phase 2.5 before FeatureHub execution.

Reasons:

- Current Phase 2 deliverables are valuable but intentionally narrow in many adapters (`one-symbol`, `one-fund`, selected indicators, and single-request refresh).
- The required product milestone is a complete data-source capability layer, not merely a representative source-slice layer.
- The system should be able to access all data domains required for rigorous short-term and medium/long-term quant research before FeatureHub proceeds.
- TASK-040 has not produced lifecycle artifacts, so pausing Phase 3 does not require rejecting completed implementation work.

Phase switch: YES, to Phase 2.5.

## Phase Gate Decision

TASK-045 is closed as Done.

The TASK-045 Review Agent decision is `ACCEPTED` after rework, and the Integration Agent result is `INTEGRATED / READY FOR CONTROLLER CLOSURE`. The prior live skip/fail classification blocker is closed: route-name-bearing AKShare argument/signature compatibility errors are no longer classified as live environment/source unavailable, while genuine network/proxy/DNS/TLS/timeout/upstream/source availability failures remain skippable diagnostics.

Phase 2.5 is not complete because required trading-grade source capabilities still include planned or partial DataHub source-capability work after TASK-045, including A-share company announcement coverage. Under `coordination/PHASE_GATE.md`, the controller stays in Phase 2.5 and dispatches the next 5.3 execution handoff.

Phase switch: NO.

## Next Task

`TASK-046`: DataHub AKShare A-share company announcements adapter.

Handoff:

- `coordination/handoffs/TASK-046_DATAHUB_AKSHARE_A_SHARE_COMPANY_ANNOUNCEMENTS_ADAPTER.md`

Expected lifecycle files:

- report: `coordination/reports/TASK-046_REPORT.md`
- review: `coordination/reviews/TASK-046_REVIEW.md`
- integration: `coordination/integrations/TASK-046_INTEGRATION.md`
