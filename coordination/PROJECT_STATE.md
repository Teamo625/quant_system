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
- TASK-001 DataHub foundation skeleton
- TASK-001 review accepted
- TASK-001 integration accepted
- TASK-002 DataHub schema contracts
- TASK-002 review accepted
- TASK-002 integration accepted
- TASK-003 DataHub local storage IO
- TASK-003 review accepted
- TASK-003 integration accepted
- TASK-004 DataHub offline fixture validation
- TASK-004 review accepted
- TASK-004 integration accepted
- TASK-005 DataHub schema type validation
- TASK-005 review accepted
- TASK-005 integration accepted
- Phase 1 completed by phase gate decision
- previous pre-rescope TASK-006 through TASK-009 Phase 2 handoffs and related code were removed after owner-directed Phase 2 scope change
- Phase 2 goal changed from selected source adapters to comprehensive full-domain data-source collection coverage
- TASK-006 DataHub comprehensive source catalog
- TASK-006 review accepted
- TASK-006 integration accepted
- TASK-007 DataHub expanded domain schema contracts
- TASK-007 review accepted
- TASK-007 integration accepted
- TASK-008 DataHub expanded contract semantic validation
- TASK-008 review accepted
- TASK-008 integration accepted
- TASK-009 DataHub explicit semantic validation rules
- TASK-009 review accepted
- TASK-009 integration accepted
- TASK-010 DataHub semantic rule integrity checks
- TASK-010 review accepted
- TASK-010 integration accepted
- TASK-011 DataHub source adapter contract foundation
- TASK-011 review accepted
- TASK-011 integration accepted
- TASK-012 AKShare A-share daily bar adapter
- TASK-012 review accepted
- TASK-012 integration accepted
- TASK-013 AKShare A-share trading calendar adapter
- TASK-013 review accepted
- TASK-013 integration accepted
- TASK-014 AKShare Hong Kong daily bar adapter
- TASK-014 live-network evidence rework completed
- TASK-014 review accepted
- TASK-014 integration accepted
- TASK-015 AKShare ETF/fund NAV snapshot adapter
- TASK-015 review accepted
- TASK-015 integration accepted
- TASK-016 AKShare index daily bar adapter
- TASK-016 review accepted
- TASK-016 integration accepted
- TASK-017 AKShare sector daily bar adapter
- TASK-017 live-network evidence and live PASS reworks completed
- TASK-017 review accepted
- TASK-017 integration accepted
- TASK-018 AKShare sector master adapter
- TASK-018 live duplicate rework completed
- TASK-018 review accepted
- TASK-018 integration accepted
- TASK-019 AKShare sector membership adapter
- TASK-019 live evidence rework completed
- TASK-019 live PASS rework completed
- TASK-019 review accepted
- TASK-019 integration accepted
- TASK-020 AKShare index constituents adapter
- TASK-020 review accepted
- TASK-020 integration accepted
- TASK-021 AKShare global equity snapshot adapter handoff dispatched
- TASK-021 implementation report submitted
- TASK-021 review requested changes because live-enabled smoke skipped with `ProxyError` to `72.push2.eastmoney.com`
- TASK-021 integration blocked because review was not accepted
- TASK-021 live-network rework handoff dispatched
- TASK-021 live-network rework report submitted with live-enabled PASS evidence, but fresh review still requested changes after reproducing `KeyError: 'data'` inside `akshare.stock_us_spot`
- TASK-021 integration remained blocked because review was not accepted, despite integration-side live-enabled rerun eventually passing
- TASK-021 Sina KeyError live-route stability rework handoff dispatched
- TASK-021 Sina KeyError live-route stability rework completed with live-enabled PASS evidence
- TASK-021 review accepted
- TASK-021 integration accepted
- TASK-022 AKShare news events adapter handoff dispatched
- TASK-022 AKShare news events adapter
- TASK-022 review accepted
- TASK-022 integration accepted
- TASK-023 HKEX company announcements adapter handoff dispatched
- TASK-023 implementation report submitted with live-enabled PASS evidence
- TASK-023 review requested rework because requested `symbols` filters accepted prefix-polluted invalid forms such as `foo700` and `A700.HK`
- TASK-023 integration blocked because review was not accepted
- TASK-023 symbol filter rework handoff dispatched
- TASK-023 symbol filter rework completed with offline/default/live-enabled PASS evidence
- TASK-023 review accepted
- TASK-023 integration accepted
- TASK-024 AKShare China macro adapter handoff dispatched
- TASK-024 implementation report submitted with live-enabled PASS evidence
- TASK-024 review requested rework because `AkshareChinaMacroAdapter` inferred optional `is_preliminary` from numeric source fields such as `初值` / `预告`
- TASK-024 integration blocked because review was not accepted
- TASK-024 `is_preliminary` rework handoff dispatched
- TASK-024 `is_preliminary` rework completed with offline/default/live-enabled PASS evidence
- TASK-024 review accepted
- TASK-024 integration accepted
- TASK-025 DataHub local refresh metadata and quality baseline handoff dispatched
- TASK-025 local refresh metadata and quality baseline completed with offline-only PASS evidence
- TASK-025 review accepted
- TASK-025 integration accepted
- TASK-026 AKShare A-share instrument master adapter handoff dispatched
- TASK-026 implementation report submitted with live-enabled PASS evidence
- TASK-026 review accepted
- TASK-026 integration accepted
- TASK-027 AKShare A-share corporate actions adapter handoff dispatched
- TASK-027 implementation report submitted with live-enabled PASS evidence
- TASK-027 review accepted
- TASK-027 integration accepted
- TASK-027 closed by controller after phase-gate review
- TASK-028 AKShare A-share valuation snapshot adapter handoff dispatched
- TASK-028 implementation report submitted with offline/default PASS evidence, but mandatory live-enabled smoke skipped due proxy/network unavailability reaching `push2.eastmoney.com`
- TASK-028 review requested changes because live-enabled `PASS` gate was not met
- TASK-028 integration blocked because review was not accepted
- TASK-028 live-network rework handoff dispatched
- TASK-028 live-network rework completed with live-enabled PASS evidence
- TASK-028 review accepted
- TASK-028 integration accepted
- TASK-028 closed by controller after phase-gate review
- TASK-029 AKShare A-share capital flow snapshot adapter handoff dispatched

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

- TASK-028 is closure-ready and integrated, but Phase 2 contains additional required source coverage beyond TASK-028.
- Remaining Phase 2 required coverage is still incomplete across:
  - A-share data expansion, continuing with TASK-029 for `CAPITAL_FLOW_SNAPSHOT` capital-flow records
  - additional index/global expansion beyond the first slice
  - policy source adapters
  - additional A-share/HK/ETF-fund expansion slices
  - additional local raw/normalized refresh metadata and data-quality behaviors beyond the TASK-025 baseline
- Therefore the current phase cannot switch under `coordination/PHASE_GATE.md`.

Phase switch: NO.

## Next Task

`TASK-029`: DataHub AKShare A-share capital flow snapshot adapter.

Handoff:

- `coordination/handoffs/TASK-029_DATAHUB_AKSHARE_A_SHARE_CAPITAL_FLOW_SNAPSHOT_ADAPTER.md`

Expected lifecycle files:

- report: `coordination/reports/TASK-029_REPORT.md`
- review: `coordination/reviews/TASK-029_REVIEW.md`
- integration: `coordination/integrations/TASK-029_INTEGRATION.md`
