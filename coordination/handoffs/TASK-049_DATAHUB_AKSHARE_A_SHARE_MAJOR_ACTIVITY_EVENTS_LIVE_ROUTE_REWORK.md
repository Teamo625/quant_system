# TASK-049 Rework: A-share Major Activity Events Live Route Gate

## Task ID

TASK-049

## Rework Handoff

`coordination/handoffs/TASK-049_DATAHUB_AKSHARE_A_SHARE_MAJOR_ACTIVITY_EVENTS_LIVE_ROUTE_REWORK.md`

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2.5: DataHub Trading-Grade Source Capability

## Context

TASK-049 implemented a bounded public AKShare A-share `DatasetName.MAJOR_ACTIVITY_EVENTS` adapter slice and deterministic offline tests. The Review Agent accepted the implementation, and the Integration Agent accepted the reviewed artifacts, but integration recorded:

- Status: `INTEGRATED_WITH_LIVE_SKIP_GATE`
- live-enabled smoke result: `SKIP`
- observed live root-cause evidence: `RuntimeError: AKShare A-share major-activity route unavailable: stock_dzjy_mrmx(start_date=20260531, end_date=20260531) -> TypeError: 'NoneType' object is not subscriptable`

Per `AGENTS.md` and `coordination/PHASE_GATE.md`, a real-source adapter task with a live-enabled network/proxy/DNS/TLS/upstream/source-availability skip cannot be counted as Done until an explicit 5.3 execution rework diagnoses the blocker, applies feasible repository fixes, writes report evidence, and receives fresh review plus integration.

## Required Reading

The execution window must read:

- `AGENTS.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-049_DATAHUB_AKSHARE_A_SHARE_MAJOR_ACTIVITY_EVENTS_ADAPTER.md`
- `coordination/handoffs/TASK-049_DATAHUB_AKSHARE_A_SHARE_MAJOR_ACTIVITY_EVENTS_LIVE_ROUTE_REWORK.md`
- `coordination/reports/TASK-049_REPORT.md`
- `coordination/reviews/TASK-049_REVIEW.md`
- `coordination/integrations/TASK-049_INTEGRATION.md`
- `quant/datahub/adapters/akshare.py`
- `tests/datahub/test_akshare_a_share_major_activity_events_adapter.py`
- `tests/datahub/test_akshare_a_share_major_activity_events_live.py`

Read broader files only if needed to implement the narrow fix or run permitted tests.

## Goal

Rework the TASK-049 major-activity adapter/tests so the live-enabled smoke reaches closure-ready evidence when feasible, while preserving offline determinism, source-truth behavior, and the narrow public A-share `MAJOR_ACTIVITY_EVENTS` scope.

Target result:

- default tests remain offline-safe and pass
- live-enabled smoke should produce `PASS` if a bounded public AKShare major-activity/block-trade route is available
- if live-enabled smoke still `SKIP`/`FAIL`s due network/proxy/DNS/TLS/upstream/source availability after feasible fixes, the report must include root-cause evidence, attempted fixes, and operator action required

## Allowed Files

The execution window may create or modify only:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-049_REPORT.md`

Suggested implementation locations:

- `quant/datahub/adapters/akshare.py`
- `tests/datahub/test_akshare_a_share_major_activity_events_adapter.py`
- `tests/datahub/test_akshare_a_share_major_activity_events_live.py`
- focused existing DataHub tests only if shared AKShare classification, source catalog, source capability, or symbol behavior changes

## Forbidden Files

The execution window must not modify:

- `coordination/PROJECT_STATE.md`
- `coordination/ROADMAP.md`
- `coordination/TASK_BOARD.md`
- `coordination/DECISIONS.md`
- `coordination/RISKS.md`
- `coordination/INTERFACES.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/reviews/**`
- `coordination/integrations/**`
- `coordination/handoffs/**`
- `quant/features/**`
- `quant/strategies/**`
- `quant/backtest/**`
- `quant/scanner/**`
- `quant/portfolio/**`
- `quant/notification/**`
- `quant/ai/**`
- `quant/ui/**`

## Rework Requirements

### 1. Reproduce and diagnose the live skip

Reproduce the current live-enabled result before changing behavior if feasible:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_major_activity_events_live.py`

Identify whether the blocker is:

- non-trading-date or invalid route date selection
- environment proxy configuration
- DNS/TCP/TLS/network reachability
- upstream route availability
- local AKShare route behavior or route-shape drift
- adapter/test design that unnecessarily depends on one route when an equivalent bounded public route exists

Record concrete evidence in `coordination/reports/TASK-049_REPORT.md`.

### 2. Try feasible bounded route resilience

Investigate the no-credential AKShare A-share block-trade/major-activity routes available in the local AKShare version. Candidate routes from the original handoff included:

- `stock_dzjy_mrmx`
- `stock_dzjy_mrtj`
- `stock_dzjy_sctj`
- `stock_dzjy_hygtj`
- `stock_dzjy_hyyybtj`
- `stock_dzjy_yybph`

Apply feasible fixes without expanding scope:

1. Preserve source identity as `akshare_cn_hk_public_family`.
2. Prefer a bounded daily detail route that can emit truthful `MAJOR_ACTIVITY_EVENTS` source facts.
3. If the current date choice is the blocker, make live smoke choose a recent valid trading date or a bounded date with known public route availability without hard-coding brittle future assumptions.
4. If adding fallback routes, keep them narrowly scoped to:
   - A-share public block-trade or major-activity records
   - `DatasetName.MAJOR_ACTIVITY_EVENTS`
   - `market=A_SHARE`
   - no credentials
   - deterministic parsing equivalent to the current source-fact contract
5. Do not add Tushare, credentialed fallback, browser scraping, cookies, tokens, or private account data.

### 3. Preserve hard-fail boundaries

The rework must not mask:

- schema/normalization bugs
- invalid symbols
- malformed payloads
- missing required source fields
- invalid dates
- invalid numeric values
- conflicting duplicate event rows
- non-serializable values
- AKShare argument/signature compatibility errors

Only genuine network/proxy/DNS/TLS/timeout/upstream/public-source availability failures may be classified for live `skipTest(...)`.

### 4. Update tests and report

Update deterministic offline tests for any fallback, date-selection, or live-classification behavior added:

- route order and fallback selection, if fallback is added
- selected fallback records still validate through `DatasetRegistry.validate_record(...)`
- default tests remain offline-safe and use injected fixtures/callables
- route/signature compatibility errors remain hard failures
- true network/source availability failures are classified only in live diagnostics
- adapter/schema/normalization errors still fail the live test

Append a rework section to `coordination/reports/TASK-049_REPORT.md` with:

- files changed
- tests run
- default network behavior
- live-enabled PASS/SKIP/FAIL result
- root-cause evidence
- repository-level fixes attempted
- deviations from handoff
- residual risks or operator action required

## Do Not Implement

Do not implement:

- new datasets beyond `DatasetName.MAJOR_ACTIVITY_EVENTS`
- broad A-share universe ingestion
- full major-activity history backfill
- storage refresh orchestration
- source catalog or capability broadening beyond what a permitted test requires
- feature calculations, scanner filters, strategy logic, AI reports, notifications, UI, or automated trading
- credentialed source behavior

## Testing Requirements

Default tests must remain offline.

Run focused tests:

`python3 -m unittest tests/datahub/test_akshare_a_share_major_activity_events_adapter.py`

`python3 -m unittest -v tests/datahub/test_akshare_a_share_major_activity_events_live.py`

Run related regressions if shared AKShare parsing, classification, source catalog, source capability, or symbol behavior changes:

`python3 -m unittest tests/datahub/test_akshare_adapter.py`

`python3 -m unittest tests/datahub/test_source.py`

`python3 -m unittest tests/datahub/test_datasets.py`

`python3 -m unittest tests/datahub/test_source_capabilities.py`

`python3 -m unittest tests/datahub/test_source_catalog.py`

Run full DataHub discovery:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Run gated live smoke:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_major_activity_events_live.py`

If any command cannot run, record the exact command and reason in `coordination/reports/TASK-049_REPORT.md`.

## Acceptance Criteria

This rework is acceptable when:

- TASK-049 remains scoped to no-credential public AKShare A-share `MAJOR_ACTIVITY_EVENTS`
- default tests remain offline-safe and pass
- live-enabled result is truthfully recorded
- live-enabled `PASS` is provided if a bounded public major-activity route is reachable after feasible fixes
- any remaining live `SKIP`/`FAIL` includes root-cause evidence, feasible-fix evidence, and operator action required
- adapter/schema/normalization and AKShare signature errors remain hard failures
- no future-phase module contains new logic
- updated report exists at `coordination/reports/TASK-049_REPORT.md`

## Report Path

`coordination/reports/TASK-049_REPORT.md`

## Review Path

`coordination/reviews/TASK-049_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-049_INTEGRATION.md`
