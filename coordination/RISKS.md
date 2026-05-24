# Risks

Only the 5.5 controller may update this file.

## RISK-001: Data Source Instability

Severity: High

Description:

Market data sources may change schemas, rate limits, availability, or licensing constraints.

Mitigation:

Use adapter boundaries, local caching, schema validation, and optional live tests.

## RISK-002: Scope Creep Into Strategy Work

Severity: High

Description:

It is tempting to add scans, indicators, strategies, and AI explanations before DataHub is stable.

Mitigation:

Enforce module boundaries and reject handoffs that implement future-phase logic.

## RISK-003: Hidden Network Access in Tests

Severity: Medium

Description:

Tests may accidentally call external APIs and become flaky or rate-limited.

Mitigation:

Default tests must be offline. Live tests require `QUANT_SYSTEM_LIVE_TESTS=1` and handoff permission.

## RISK-004: Contract Drift

Severity: Medium

Description:

Downstream modules may assume fields or semantics that DataHub does not guarantee.

Mitigation:

Maintain `docs/03_DATA_CONTRACTS.md` and record stable interfaces in `coordination/INTERFACES.md`.

## RISK-005: Expanded Phase 2 Source Scope

Severity: High

Description:

Changing Phase 2 from selected sources to full data-source collection substantially increases scope, provider instability exposure, licensing uncertainty, and implementation time.

Mitigation:

Start with a code-level source catalog and coverage matrix, split adapter implementation into bounded handoffs, keep default tests offline, and require explicit gating for live source checks.

## RISK-006: Comprehensive Data Domain Contract Gaps

Severity: High

Description:

The expanded Phase 2 scope includes macroeconomic, policy, news, announcement, sector, global equity, fund, and index data domains that are not fully represented by the current stable `DatasetName` contracts.

Mitigation:

TASK-006 must make missing stable contracts explicit in the source catalog. Follow-up handoffs should add schema contracts before implementing broad ingestion for domains that are not yet modeled.

## RISK-007: Live Smoke Network Failure Misclassification

Severity: High

Description:

Live-enabled source smoke tests can fail or skip because of proxy configuration, DNS/TCP/TLS reachability, public-source instability, upstream schema changes, or adapter bugs. If those outcomes are accepted without diagnosis, the project may record false confidence in a source adapter.

Mitigation:

Every similar live-network failure must be routed through a 5.3 execution rework for diagnosis and feasible code/test/report fixes, then independently reviewed before integration or controller closure.
