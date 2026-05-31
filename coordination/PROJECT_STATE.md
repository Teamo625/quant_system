# Project State

Last updated by: 5.5 Controller

## Current Phase

Phase 3: FeatureHub.

## Current Implementation Scope

FeatureHub foundation work is active.

Current implementation may target only:

- `quant/features/`

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
- Phase 3 opened for FeatureHub, starting with contract primitives only

## Active Constraints

- Do not implement strategies.
- Do not implement scanner ranking or stock-picking logic.
- Do not implement backtest execution.
- Do not implement portfolio, signal, or risk logic.
- Do not implement AI reports.
- Do not implement notifications.
- Do not implement automated trading.
- Do not implement complex UI.
- Do not fetch live market data from FeatureHub; FeatureHub must consume DataHub contracts and local outputs.
- Default tests must not use live network access.
- Live tests require explicit handoff permission and environment-variable gating.
- Real source adapter and real data-fetching tasks remain DataHub-owned and require a gated live smoke test when explicitly assigned; default tests must still skip it unless explicitly enabled.
- Live-enabled network/proxy/DNS/TLS/upstream failures must be routed to a 5.3 execution rework for diagnosis and feasible repository fixes, then independently reviewed before integration or controller closure.
- Execution windows must not update project state files.

## Phase Gate Decision

Phase 2 is complete. Phase 3 is now open.

Reasons:

- TASK-039 is counted Done after accepted review and integration.
- TASK-039 closes the remaining explicit local warehouse gap by adding a local one-request runner for raw persistence, curated schema validation/persistence, refresh metadata, and data quality report output.
- TASK-006 through TASK-039 now cover Phase 2's approved DataHub catalog, stable contracts, semantic validation, source adapter slices, live-smoke closure requirements, local persistence, refresh metadata, and quality checks.
- No concrete Phase 2 task remains in Ready, In Progress, In Review, or Ready to Integrate.
- Remaining DataHub expansion ideas are future blocked extensions, not active Phase 2 lifecycle tasks.
- Therefore the current phase switches under `coordination/PHASE_GATE.md`.

Phase switch: YES.

## Next Task

`TASK-040`: FeatureHub foundation contracts.

Handoff:

- `coordination/handoffs/TASK-040_FEATUREHUB_FOUNDATION_CONTRACTS.md`

Expected lifecycle files:

- report: `coordination/reports/TASK-040_REPORT.md`
- review: `coordination/reviews/TASK-040_REVIEW.md`
- integration: `coordination/integrations/TASK-040_INTEGRATION.md`
