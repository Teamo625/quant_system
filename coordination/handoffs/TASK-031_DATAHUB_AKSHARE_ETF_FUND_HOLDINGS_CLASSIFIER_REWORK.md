# TASK-031: DataHub AKShare ETF/Fund Holdings Classifier Rework

## Task ID

TASK-031

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

TASK-031 implemented an AKShare-backed one-fund ETF/fund holdings adapter for `DatasetName.FUND_HOLDINGS`, but review did not accept closure.

Review blocker:

- `AkshareETFFundHoldingsAdapter._is_fund_holdings_network_unavailable(...)` references `ssl.SSLError`, but `ssl` is not imported in `quant/datahub/adapters/akshare.py`.
- Direct review reproduction with `OSError(111, "connection refused")` raised `NameError: name 'ssl' is not defined`.
- Current live test coverage duplicates a local helper and does not directly exercise the adapter-side classifier path, allowing this defect to slip through.

Integration result:

- `coordination/integrations/TASK-031_INTEGRATION.md` is `NOT INTEGRATED`.
- TASK-031 must not be closed until this rework receives a fresh accepted review and successful integration.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-031_DATAHUB_AKSHARE_ETF_FUND_HOLDINGS_CLASSIFIER_REWORK.md`
- `coordination/reviews/TASK-031_REVIEW.md`
- `coordination/integrations/TASK-031_INTEGRATION.md`

## Goal

Fix the ETF/fund holdings adapter-side network/source-unavailability classifier so it cannot raise `NameError`, and add deterministic test coverage that directly exercises the adapter classifier path.

## Allowed Files

The execution window may create or modify:

- `quant/datahub/adapters/akshare.py`
- `tests/datahub/test_akshare_fund_holdings_adapter.py`
- `tests/datahub/test_akshare_fund_holdings_live.py`
- `coordination/reports/TASK-031_REPORT.md`

Only touch additional `quant/datahub/**` or `tests/datahub/**` files if strictly required by the classifier fix.

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

## Required Fixes

### 1. Fix the classifier crash

Update `AkshareETFFundHoldingsAdapter._is_fund_holdings_network_unavailable(...)` so it handles TLS/network exception classification without raising `NameError`.

Acceptable approaches include:

- import `ssl` at module scope and keep the existing `ssl.SSLError` check
- or replace the direct `ssl.SSLError` reference with an equivalent safe name/module/message check

The classifier must still classify network/proxy/DNS/TLS/upstream/source availability failures as environment/source-unavailable and keep contract/normalization failures as non-network errors.

### 2. Add direct deterministic test coverage

Add or adjust tests so the adapter-side classifier is directly exercised.

Required coverage:

- `AkshareETFFundHoldingsAdapter()._is_fund_holdings_network_unavailable(OSError(111, ...))` returns `True` and does not raise
- a non-network contract/normalization exception such as `ValueError("Invalid report_date value")` returns `False`
- at least one TLS-style or exception-name-based case is covered if practical

Avoid relying only on a duplicate helper in `tests/datahub/test_akshare_fund_holdings_live.py`. The test should call the adapter classifier itself or route through a fetch path that invokes it deterministically.

### 3. Preserve existing TASK-031 behavior

Do not change the accepted business scope of the adapter:

- keep scope limited to one-fund `DatasetName.FUND_HOLDINGS`
- keep source id `akshare_cn_hk_public_family`
- keep default tests offline-safe
- do not add fund profile, full-fund universe ingestion, all-fund holdings ingestion, feature engineering, scanner logic, strategy logic, AI reports, notification, UI, or any future-phase logic

## Testing Requirements

Run focused tests:

`python3 -m unittest tests/datahub/test_akshare_fund_holdings_adapter.py`

`python3 -m unittest -v tests/datahub/test_akshare_fund_holdings_live.py`

Run targeted reproduction or an equivalent unit test proving this no longer raises:

`python3 - <<'PY'
from quant.datahub.adapters.akshare import AkshareETFFundHoldingsAdapter
adapter = AkshareETFFundHoldingsAdapter()
print(adapter._is_fund_holdings_network_unavailable(OSError(111, "connection refused")))
print(adapter._is_fund_holdings_network_unavailable(ValueError("Invalid report_date value")))
PY`

Run related regressions:

`python3 -m unittest tests/datahub/test_akshare_fund_nav_adapter.py`

`python3 -m unittest tests/datahub/test_datasets.py`

`python3 -m unittest tests/datahub/test_source.py`

`python3 -m unittest tests/datahub/test_source_catalog.py`

Run full default DataHub discovery if feasible:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Run mandatory gated live smoke:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_fund_holdings_live.py`

If live-enabled run fails/skips due to network/proxy/DNS/TLS/upstream/source availability, the report must include root-cause evidence and feasible repository-level fixes attempted. Controller closure will require fresh review and integration.

## Acceptance Criteria

The rework is acceptable when:

- the `ssl`/classifier `NameError` blocker is fixed
- deterministic tests directly exercise the adapter-side classifier path
- default tests remain offline-safe
- existing `FUND_HOLDINGS` adapter contract/scope remains intact
- live-enabled smoke result is truthfully recorded
- no future-phase module contains new logic
- updated report exists at `coordination/reports/TASK-031_REPORT.md`

## Report Path

`coordination/reports/TASK-031_REPORT.md`

## Review Path

`coordination/reviews/TASK-031_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-031_INTEGRATION.md`

## Out of Scope

Everything outside the TASK-031 classifier fix, direct classifier coverage, and necessary verification/report update is out of scope.
