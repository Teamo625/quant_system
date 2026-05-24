# Architecture Decisions

Only the 5.5 controller may update this file.

## ADR-0001: DataHub Is the First Implemented Module

Status: Accepted

Decision:

The project will implement DataHub before any feature, scanner, strategy, backtest, signal, notification, AI, or UI logic.

Reason:

All downstream modules require reliable, normalized, locally stored data. Implementing downstream logic before DataHub would create duplicate data access and unstable assumptions.

## ADR-0002: Default Tests Must Be Offline

Status: Accepted

Decision:

Default tests must not perform live network calls. Live source tests require an explicit environment variable and handoff permission.

Reason:

Market data sources can be unstable, rate-limited, or credentialed. Offline tests keep development deterministic.

## ADR-0003: Controller Owns Project Truth

Status: Accepted

Decision:

Only the 5.5 controller may update coordination state files.

Reason:

The project is large enough that uncontrolled state edits would cause phase drift and conflicting task ownership.

## ADR-0004: Phase 2 Requires Full Data-Source Collection Coverage

Status: Accepted

Decision:

Phase 2 will target full DataHub source collection coverage for the current product scope instead of only selected source adapters.

Reason:

The project owner wants DataHub to become a complete upstream data foundation before opening downstream feature, scanner, strategy, backtest, signal, notification, AI, or UI phases. Selected adapters are not sufficient if downstream modules later require broad market, reference, valuation, capital-flow, corporate-action, and calendar coverage.

## ADR-0005: Phase 2 Coverage Domains Are Comprehensive

Status: Accepted

Decision:

Phase 2 source coverage must include A-share full data, Hong Kong stock full data, ETF and fund full data, index data, concise global equity market data, industry and concept sector data, global and China macroeconomic data, and policy, news, and announcement data.

Reason:

Downstream research, scanning, backtesting, signal, risk, and report phases need a broad upstream data base. The DataHub catalog must therefore track both existing stable dataset contracts and planned data domains that still require future schema work.

## ADR-0006: Real Source Tasks Require Gated Live Smoke Tests

Status: Accepted

Decision:

Every Phase 2 task that implements a real source adapter or real data-fetching behavior must include a live smoke test. The live smoke test must be explicitly gated by `QUANT_SYSTEM_LIVE_TESTS=1`, skipped by default, credential-free unless a future controller-approved handoff explicitly opens a credentialed source, and documented in the execution report.

Reason:

Offline fixtures prove contracts and normalization, but they cannot prove that a real public data source still works. Gated live smoke tests keep default validation deterministic while forcing each real-source task to demonstrate that the adapter can reach and parse a tiny bounded live sample when explicitly enabled.

## ADR-0007: Live Network Failures Require Execution Rework and Independent Review

Status: Accepted

Decision:

When a live-enabled smoke test for a real source adapter or real data-fetching task fails or skips because of network, proxy, DNS, TLS, upstream, or public-source availability, the controller must keep the task open and dispatch an explicit execution rework. The execution window must diagnose the failure and modify allowed repository code/tests/report where a fix is feasible. The rework must then be independently reviewed and integrated through the normal review/integration lifecycle before the controller can close the task.

Reason:

Live source failures can be caused by local environment, upstream changes, adapter bugs, symbol/parameter mistakes, or test design issues. Keeping diagnosis, modification, review, and integration in separate roles prevents the controller from accidentally accepting an unverified skip, preserves accountability, and keeps live-source evidence reviewable for future source adapters.
