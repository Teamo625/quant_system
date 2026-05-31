# Project State

Last updated by: 5.5 Controller

## Current Phase

Phase 2: DataHub Comprehensive Source Collection.

## Current Implementation Scope

DataHub comprehensive source coverage and local warehouse work is active.

Current implementation may target only:

- `quant/datahub/`

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

## Active Constraints

- Do not implement strategies.
- Do not implement AI reports.
- Do not implement notifications.
- Do not implement automated trading.
- Do not implement complex UI.
- Default tests must not use live network access.
- Live tests require explicit handoff permission and environment-variable gating.
- Real source adapter and real data-fetching tasks must include a gated live smoke test; default tests must still skip it unless explicitly enabled.
- Live-enabled network/proxy/DNS/TLS/upstream failures must be routed to a 5.3 execution rework for diagnosis and feasible repository fixes, then independently reviewed before integration or controller closure.
- Execution windows must not update project state files.

## Phase Gate Decision

Phase 2 is not complete.

Reasons:

- TASK-038 is now counted Done after accepted rework review and integration.
- TASK-038 closure records live-enabled PASS evidence after diagnosing the prior proxy/network skip to `push2his.eastmoney.com` and adding a bounded Sina fallback for classified ETF daily-bar source unavailability.
- Phase 2 still contains required local-warehouse work beyond source adapter slices.
- Roadmap Phase 2 requires raw and normalized local persistence, refresh metadata, and data quality checks for collected datasets. Existing storage and quality helpers are present, but there is no narrow local runner that ties `SourceResult` fetch output to raw/curated persistence plus refresh metadata and `DATA_QUALITY_REPORT` output.
- Therefore the current phase cannot switch under `coordination/PHASE_GATE.md`.

Phase switch: NO.

## Next Task

`TASK-039`: DataHub local warehouse refresh runner.

Handoff:

- `coordination/handoffs/TASK-039_DATAHUB_LOCAL_WAREHOUSE_REFRESH_RUNNER.md`

Expected lifecycle files:

- report: `coordination/reports/TASK-039_REPORT.md`
- review: `coordination/reviews/TASK-039_REVIEW.md`
- integration: `coordination/integrations/TASK-039_INTEGRATION.md`
