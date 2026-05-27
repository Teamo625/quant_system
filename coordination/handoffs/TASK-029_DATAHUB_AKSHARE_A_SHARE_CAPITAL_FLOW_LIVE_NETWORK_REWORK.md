# TASK-029 Rework: DataHub AKShare A-share Capital Flow Live-Network Gate

## Task ID

TASK-029

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

TASK-029 implemented the AKShare A-share one-symbol `CAPITAL_FLOW_SNAPSHOT` adapter and offline tests. Review found no additional blocking code-quality issue, but did not accept closure because the mandatory live-enabled smoke was `SKIP` instead of `PASS`.

Review evidence:

- `coordination/reviews/TASK-029_REVIEW.md`
- live-enabled command: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py`
- observed result: `OK (skipped=1)`
- skip cause: proxy/network failure reaching `push2his.eastmoney.com` through the primary AKShare `stock_individual_fund_flow` route

Integration also blocked TASK-029 because review was not accepted:

- `coordination/integrations/TASK-029_INTEGRATION.md`

Per `AGENTS.md`, a live-enabled network/proxy/DNS/TLS/upstream failure or skip cannot be accepted as closure. This handoff exists to diagnose the live blocker and apply feasible repository-level fixes before a fresh review/integration cycle.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-029_DATAHUB_AKSHARE_A_SHARE_CAPITAL_FLOW_SNAPSHOT_ADAPTER.md`
- `coordination/handoffs/TASK-029_DATAHUB_AKSHARE_A_SHARE_CAPITAL_FLOW_LIVE_NETWORK_REWORK.md`
- `coordination/reports/TASK-029_REPORT.md`
- `coordination/reviews/TASK-029_REVIEW.md`
- `coordination/integrations/TASK-029_INTEGRATION.md`

## Goal

Rework the TASK-029 capital-flow adapter/tests so the live-enabled smoke can reach a closure-ready result when feasible, while preserving offline determinism, source-truth behavior, and the narrow A-share one-symbol `CAPITAL_FLOW_SNAPSHOT` scope.

Target result:

- default tests remain offline-safe and pass
- live-enabled smoke should produce `PASS` if a bounded public capital-flow path is available
- if live-enabled smoke still `SKIP`/`FAIL`s due network/proxy/DNS/TLS/upstream availability after feasible fixes, the report must truthfully include root-cause evidence, attempted fixes, and operator action required

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-029_REPORT.md`

Suggested implementation locations:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `quant/datahub/datasets.py` only for minimal source-truth optionality already opened by TASK-029
- `quant/datahub/source_catalog.py` only if strict catalog assertion alignment is required
- `tests/datahub/test_akshare_a_share_capital_flow_snapshot_adapter.py`
- `tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py`
- `tests/datahub/test_datasets.py` only if schema optionality changes
- `tests/datahub/test_source_catalog.py` only if source-catalog expectations change

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

### 1. Reproduce and diagnose the live blocker

Reproduce the current live-enabled result before changing behavior if feasible:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py`

Identify whether the blocker is:

- environment proxy configuration
- DNS/TCP/TLS/network reachability
- upstream route availability
- AKShare route behavior
- adapter/test design that unnecessarily depends on one host when an equivalent bounded route exists

Record concrete evidence in `coordination/reports/TASK-029_REPORT.md`.

### 2. Try feasible bounded primary-route resilience

The current live blocker is on the primary route that supplies required `main_net_inflow`:

- `akshare.stock_individual_fund_flow(stock="<6-digit-code>", market="<sh|sz|bj>")`
- upstream host observed in failure: `push2his.eastmoney.com`

Apply feasible fixes without expanding scope:

1. Preserve the existing AKShare primary route as the preferred route when available.
2. Investigate whether AKShare or a direct Eastmoney-equivalent one-symbol endpoint can provide the same daily capital-flow fields through a bounded route and an alternate stable host.
3. If adding a direct fallback, keep it narrowly scoped to:
   - one requested A-share symbol
   - `main_net_inflow` and existing optional capital-flow fields only
   - no credentials
   - deterministic parsing equivalent to the existing route contract
4. Keep source identity as `akshare_cn_hk_public_family` unless the implemented source family truly changes. Do not add a new source id in this rework.
5. Keep `main_net_inflow` required unless there is a controller-approved schema task in the future. A capital-flow record without a truthful main-flow field is not useful for this slice.

Do not use broad full-market fund-flow ranking routes as a live workaround. Do not implement full-market capital-flow ingestion.

### 3. Preserve source-truth optionality from TASK-029

The initial TASK-029 implementation already made these fields optional:

- `net_inflow`
- `northbound_net_buy`
- `turnover_rate`

This rework should preserve that source-truth behavior unless a clear bug is found.

Do not synthesize missing values. In particular:

- do not compute `net_inflow` from order-size buckets unless the source explicitly defines that computation as total net inflow
- do not fabricate `northbound_net_buy`
- do not fabricate `turnover_rate`

Contract or normalization failures for emitted fields must remain hard failures. Environment/source unavailability may be classified for live skip diagnostics, but must not mask adapter bugs.

### 4. Preserve hard-fail boundaries

The rework must not mask:

- schema/normalization bugs
- invalid symbols
- malformed payloads
- missing required `main_net_inflow`
- invalid dates
- invalid numeric values for emitted fields
- conflicting duplicate capital-flow rows
- non-serializable values

Only network/proxy/DNS/TLS/upstream/source availability failures may be classified for live `skipTest(...)`.

### 5. Update tests

Update deterministic offline tests for any fallback behavior added:

- route order and fallback selection
- alternate host or alternate bounded route parsing
- fallback still returns records compatible with `DatasetRegistry.validate_record(...)`
- default tests remain offline-safe and use injected fixtures/callables
- primary-route contract failures remain hard failures
- true network/source availability failures are classified only in live diagnostics

Update live smoke only as needed:

- live smoke should pass when a bounded primary or fallback capital-flow path returns a valid record
- live smoke may skip only when all bounded source paths are unavailable due environment/source issues
- adapter/schema/normalization errors must still fail the live test

### 6. Mandatory live smoke rerun

Run the live smoke after rework:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py`

The desired closure evidence is live-enabled `PASS`.

If it still skips/fails due network/proxy/DNS/TLS/upstream/source availability, do not claim closure. The report must include:

- exact command
- PASS/SKIP/FAIL result
- exception class/message evidence
- route(s) attempted
- repository-level fixes attempted
- why no further repository-level fix is feasible without violating scope
- operator action required

## Do Not Implement

Do not implement:

- new datasets beyond `DatasetName.CAPITAL_FLOW_SNAPSHOT`
- HK, ETF, fund, index, policy, valuation, or corporate-action adapters
- broad full-market capital-flow ingestion
- derived feature logic, scanner filters, strategy logic, AI reports, notifications, or UI
- credentialed source behavior

## Testing Requirements

Default tests must remain offline.

Run focused tests:

`python3 -m unittest tests/datahub/test_akshare_a_share_capital_flow_snapshot_adapter.py`

`python3 -m unittest -v tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py`

Run related regressions:

`python3 -m unittest tests/datahub/test_datasets.py`

`python3 -m unittest tests/datahub/test_source_catalog.py`

`python3 -m unittest tests/datahub/test_akshare_adapter.py`

`python3 -m unittest tests/datahub/test_source.py`

`python3 -m unittest tests/datahub/test_quality.py`

Run full DataHub discovery:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Run gated live smoke:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py`

## Acceptance Criteria

The rework is acceptable when:

- TASK-029 remains scoped to one-symbol A-share `CAPITAL_FLOW_SNAPSHOT`
- default tests remain offline-safe and pass
- live-enabled result is truthfully recorded
- live-enabled `PASS` is provided if a bounded public capital-flow route is reachable after feasible fixes
- any remaining live `SKIP`/`FAIL` includes root-cause evidence and feasible-fix evidence, not just documentation
- no placeholder capital-flow values are invented
- no future-phase module contains new logic
- updated report exists at `coordination/reports/TASK-029_REPORT.md`

## Report Path

`coordination/reports/TASK-029_REPORT.md`

## Review Path

`coordination/reviews/TASK-029_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-029_INTEGRATION.md`
