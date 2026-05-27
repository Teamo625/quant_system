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
- TASK-031 initial AKShare ETF/fund holdings adapter report submitted with live-enabled PASS evidence, but review requested changes because the adapter-side network-unavailable classifier can raise `NameError` due missing `ssl` import and lacks direct deterministic coverage
- TASK-031 integration blocked because review was not accepted
- TASK-031 ETF/fund holdings classifier rework handoff dispatched

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

- TASK-031 is not closure-ready: review requested changes and integration is blocked.
- The blocker is in the live-network/source-unavailability classification boundary for the ETF/fund holdings adapter.
- Phase 2 still contains required source coverage beyond TASK-031 after this rework closes.
- Therefore the current phase cannot switch under `coordination/PHASE_GATE.md`.

Phase switch: NO.

## Next Task

`TASK-031`: DataHub AKShare ETF/fund holdings classifier rework.

Handoff:

- `coordination/handoffs/TASK-031_DATAHUB_AKSHARE_ETF_FUND_HOLDINGS_CLASSIFIER_REWORK.md`

Expected lifecycle files:

- report: `coordination/reports/TASK-031_REPORT.md`
- review: `coordination/reviews/TASK-031_REVIEW.md`
- integration: `coordination/integrations/TASK-031_INTEGRATION.md`
