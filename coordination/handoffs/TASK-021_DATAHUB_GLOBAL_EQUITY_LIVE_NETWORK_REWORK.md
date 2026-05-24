# TASK-021: DataHub Global Equity Live Network Rework

## Task ID

TASK-021

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

TASK-021 implemented the AKShare-backed `DatasetName.GLOBAL_EQUITY_SNAPSHOT` adapter and offline tests, but review did not accept closure.

Review result:

- `coordination/reviews/TASK-021_REVIEW.md`
- decision: `CHANGES REQUIRED (NOT CLOSURE-READY)`
- blocking reason: live-enabled smoke remained `SKIP`
- evidence: `ProxyError` / `RemoteDisconnected` to `72.push2.eastmoney.com:443`

Integration result:

- `coordination/integrations/TASK-021_INTEGRATION.md`
- decision: `Not Integrated (Blocked)`

Per `AGENTS.md`, a real-source task with live-enabled network/proxy/DNS/TLS/upstream/source failure or skip cannot be closed from the skip alone. This handoff is the required 5.3 execution rework for diagnosis and feasible repository-level fixes before a fresh review and integration cycle.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-021_DATAHUB_AKSHARE_GLOBAL_EQUITY_SNAPSHOT_ADAPTER.md`
- `coordination/handoffs/TASK-021_DATAHUB_GLOBAL_EQUITY_LIVE_NETWORK_REWORK.md`
- `coordination/reports/TASK-021_REPORT.md`
- `coordination/reviews/TASK-021_REVIEW.md`
- `coordination/integrations/TASK-021_INTEGRATION.md`

## Goal

Diagnose the live-enabled `GLOBAL_EQUITY_SNAPSHOT` smoke skip, implement feasible repository-level fixes, and produce fresh evidence for `TASK-021`.

The preferred closure outcome is a live-enabled `PASS` for:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_global_equity_snapshot_live.py`

If the environment still cannot reach any no-credential public source after feasible fixes, the report must truthfully record `SKIP` or `FAIL` with root-cause evidence, attempted fixes, and concrete operator action. Do not hide a live-source failure behind default test success.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-021_REPORT.md`

Suggested implementation locations:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py` only if exports need correction
- `quant/datahub/__init__.py` only if exports need correction
- `tests/datahub/test_akshare_global_equity_snapshot_adapter.py`
- `tests/datahub/test_akshare_global_equity_snapshot_live.py`
- `tests/datahub/test_source_catalog.py` only if strict source-catalog expectations change

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

### 1. Diagnose the live skip

Reproduce and inspect:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_global_equity_snapshot_live.py`

Record in the report:

- exact live-enabled result: `PASS`, `SKIP`, or `FAIL`
- exception class and key upstream endpoint/domain when a network/source skip occurs
- whether the failure occurs before adapter parsing or during adapter normalization
- whether default tests remain offline-safe

### 2. Attempt feasible repository-level fixes

Review the current `AkshareGlobalEquitySnapshotAdapter` live route and implement feasible improvements, such as:

- add a bounded fallback to another no-credential AKShare route if available in the installed AKShare version
- make route selection explicit and testable without adding live calls to default tests
- broaden live smoke candidates only within the existing `GLOBAL_EQUITY_SNAPSHOT` scope
- improve live test diagnostics so route/domain failures are easy to distinguish from contract failures
- keep contract/normalization failures as test failures, not skips

Do not require credentials, cookies, private account data, or manual browser session state.

### 3. Preserve TASK-021 contract boundaries

The rework must remain limited to:

- `DatasetName.GLOBAL_EQUITY_SNAPSHOT`
- source family `akshare_cn_hk_public_family`
- DataHub implementation and tests

Do not expand into macro, news, policy, announcement, strategy, scanner, UI, or other future-phase modules.

### 4. Offline regression coverage

Add or update deterministic offline tests for any repository-level fix, especially:

- fallback route order and route selection
- network-unavailable fallback behavior
- live diagnostics classification boundaries
- contract failures remaining hard failures

Default tests must not perform real network calls.

## Testing Requirements

Run:

`python3 -m unittest tests/datahub/test_akshare_global_equity_snapshot_adapter.py`

`python3 -m unittest -v tests/datahub/test_akshare_global_equity_snapshot_live.py`

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Run related regressions if shared AKShare adapter code is touched:

`python3 -m unittest tests/datahub/test_akshare_index_constituents_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_index_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_hk_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_fund_nav_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_adapter.py`

Run the live-enabled smoke:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_global_equity_snapshot_live.py`

If this live-enabled command still skips or fails due to network/proxy/DNS/TLS/upstream/source availability, the report must include root-cause evidence and state what repository-level fixes were attempted or why no further repository-level fix is feasible.

## Acceptance Criteria

The rework is acceptable for review when:

- TASK-021 remains scoped to `DatasetName.GLOBAL_EQUITY_SNAPSHOT`
- default tests remain offline-safe
- any implemented fallback/diagnostic change has deterministic offline coverage
- live-enabled result is recorded truthfully
- live-enabled `PASS` is achieved, or live `SKIP`/`FAIL` contains concrete root-cause evidence and attempted feasible fixes for reviewer judgment
- no future-phase module contains new logic
- `coordination/reports/TASK-021_REPORT.md` is updated with the rework result

## Report Path

`coordination/reports/TASK-021_REPORT.md`

## Review Path

`coordination/reviews/TASK-021_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-021_INTEGRATION.md`

## Out of Scope

Everything outside a narrow DataHub `GLOBAL_EQUITY_SNAPSHOT` live-network rework and tests is out of scope.
