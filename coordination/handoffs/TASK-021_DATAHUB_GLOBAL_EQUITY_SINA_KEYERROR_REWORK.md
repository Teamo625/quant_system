# TASK-021: DataHub Global Equity Sina KeyError Rework

## Task ID

TASK-021

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

TASK-021 remains open.

The first live-network rework improved the `GLOBAL_EQUITY_SNAPSHOT` adapter and report, but the latest review still records:

- `coordination/reviews/TASK-021_REVIEW.md`
- decision: `CHANGES REQUIRED (NOT CLOSURE-READY)`
- blocking evidence: live-enabled review reproduction failed with `KeyError: 'data'` inside `akshare.stock_us_spot` / `akshare/stock/stock_us_sina.py`

The latest integration file records:

- `coordination/integrations/TASK-021_INTEGRATION.md`
- decision: `Not Integrated (Blocked)`
- integration-side live-enabled rerun eventually passed, but integration could not proceed because the review file is still not accepted

Per `AGENTS.md` and `coordination/PHASE_GATE.md`, controller cannot close TASK-021 until the rework has fresh review acceptance and integration acceptance.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-021_DATAHUB_AKSHARE_GLOBAL_EQUITY_SNAPSHOT_ADAPTER.md`
- `coordination/handoffs/TASK-021_DATAHUB_GLOBAL_EQUITY_LIVE_NETWORK_REWORK.md`
- `coordination/handoffs/TASK-021_DATAHUB_GLOBAL_EQUITY_SINA_KEYERROR_REWORK.md`
- `coordination/reports/TASK-021_REPORT.md`
- `coordination/reviews/TASK-021_REVIEW.md`
- `coordination/integrations/TASK-021_INTEGRATION.md`

## Goal

Resolve the review-blocking live route instability around `akshare.stock_us_spot` raising `KeyError: 'data'`, strengthen deterministic coverage for that branch, and update `coordination/reports/TASK-021_REPORT.md` with fresh evidence.

The preferred closure outcome remains live-enabled `PASS`:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_global_equity_snapshot_live.py`

If the live route still skips or fails because all public upstream routes are unavailable or unstable, the report must truthfully record the result, root-cause evidence, feasible repository-level fixes attempted, and why no further repository-level fix is available.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-021_REPORT.md`

Suggested implementation locations:

- `quant/datahub/adapters/akshare.py`
- `tests/datahub/test_akshare_global_equity_snapshot_adapter.py`
- `tests/datahub/test_akshare_global_equity_snapshot_live.py`

Only touch exports or catalog files if a real implementation change requires it:

- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_source_catalog.py`

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

### 1. Diagnose and handle `stock_us_spot` upstream failure

Reproduce or account for the review failure:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_global_equity_snapshot_live.py`

Investigate the adapter route chain around:

- primary route: `stock_us_spot_em`
- fallback route: `stock_us_spot`
- observed review error: `KeyError: 'data'` inside AKShare Sina implementation

Implement feasible repository-level handling so an upstream route-internal payload failure such as `KeyError: 'data'` is not confused with a DataHub contract-normalization bug.

### 2. Preserve strict contract failures

Do not broadly swallow parsing or validation errors.

The adapter must still hard-fail when:

- a matched target row has malformed required fields
- a normalized record violates `DatasetRegistry` expectations
- duplicate records conflict for the same canonical key
- the code has a DataHub contract bug rather than an upstream route availability issue

### 3. Improve deterministic offline coverage

Add or update tests that cover:

- `stock_us_spot` or fallback callable raising `KeyError("data")`
- route-level diagnostics when fallback routes are exhausted
- the difference between upstream route-internal failure and target-row contract failure
- live test classification if route-level upstream failures remain environment/source availability issues
- report/lifecycle evidence consistency, where practical through tested behavior rather than brittle text assertions

Default tests must remain fully offline.

### 4. Fresh evidence and report update

Update `coordination/reports/TASK-021_REPORT.md` to include:

- files changed in this second rework
- tests run
- default network behavior
- live-enabled `PASS`/`SKIP`/`FAIL` result
- exact root-cause evidence for any live non-PASS
- what was changed to address the review-blocking `KeyError: 'data'`
- deviations, risks, and operator action if still needed

## Testing Requirements

Run:

`python3 -m unittest tests/datahub/test_akshare_global_equity_snapshot_adapter.py`

`python3 -m unittest -v tests/datahub/test_akshare_global_equity_snapshot_live.py`

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Run related regressions if shared AKShare adapter behavior is touched:

`python3 -m unittest tests/datahub/test_akshare_index_constituents_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_index_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_hk_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_fund_nav_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_adapter.py`

Run the live-enabled smoke:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_global_equity_snapshot_live.py`

## Acceptance Criteria

The rework is acceptable for review when:

- TASK-021 remains scoped to `DatasetName.GLOBAL_EQUITY_SNAPSHOT`
- default tests remain offline-safe
- deterministic tests cover the `KeyError: 'data'` fallback-route branch or equivalent route-internal upstream failure
- target-row contract failures still hard-fail
- live-enabled result is recorded truthfully
- live-enabled `PASS` is achieved, or live non-PASS includes concrete route-level root-cause evidence and attempted feasible fixes for reviewer judgment
- no future-phase module contains new logic
- `coordination/reports/TASK-021_REPORT.md` is updated with this rework result

## Report Path

`coordination/reports/TASK-021_REPORT.md`

## Review Path

`coordination/reviews/TASK-021_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-021_INTEGRATION.md`

## Out of Scope

Everything outside a narrow DataHub `GLOBAL_EQUITY_SNAPSHOT` live-route stability rework and tests is out of scope.
