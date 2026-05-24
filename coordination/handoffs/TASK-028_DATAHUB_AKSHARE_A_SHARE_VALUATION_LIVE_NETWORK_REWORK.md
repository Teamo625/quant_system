# TASK-028 Rework: DataHub AKShare A-share Valuation Live-Network Gate

## Task ID

TASK-028

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

TASK-028 implemented the AKShare A-share one-symbol `VALUATION_SNAPSHOT` adapter and offline tests. Review found no additional blocking code-quality issue, but did not accept closure because the mandatory live-enabled smoke was `SKIP` instead of `PASS`.

Review evidence:

- `coordination/reviews/TASK-028_REVIEW.md`
- live-enabled command: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`
- observed result: `OK (skipped=1)`
- skip cause: proxy/network failure reaching `push2.eastmoney.com` through the supplemental AKShare `stock_individual_info_em` market-cap route

Integration also blocked TASK-028 because review was not accepted:

- `coordination/integrations/TASK-028_INTEGRATION.md`

Per `AGENTS.md`, a live-enabled network/proxy/DNS/TLS/upstream failure or skip cannot be accepted as closure. This handoff exists to diagnose the live blocker and apply feasible repository-level fixes before a fresh review/integration cycle.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-028_DATAHUB_AKSHARE_A_SHARE_VALUATION_SNAPSHOT_ADAPTER.md`
- `coordination/handoffs/TASK-028_DATAHUB_AKSHARE_A_SHARE_VALUATION_LIVE_NETWORK_REWORK.md`
- `coordination/reports/TASK-028_REPORT.md`
- `coordination/reviews/TASK-028_REVIEW.md`
- `coordination/integrations/TASK-028_INTEGRATION.md`

## Goal

Rework the TASK-028 valuation adapter/tests so the live-enabled smoke can reach a closure-ready result when feasible, while preserving offline determinism, source-truth behavior, and the narrow A-share one-symbol `VALUATION_SNAPSHOT` scope.

Target result:

- default tests remain offline-safe and pass
- live-enabled smoke should produce `PASS` if at least one bounded public valuation path is available
- if live-enabled smoke still `SKIP`/`FAIL`s due network/proxy/DNS/TLS/upstream availability after feasible fixes, the report must truthfully include root-cause evidence, attempted fixes, and operator action required

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-028_REPORT.md`

Suggested implementation locations:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `quant/datahub/datasets.py` only for the minimal source-truth optionality adjustment described below
- `quant/datahub/source_catalog.py` only if strict catalog assertion alignment is required
- `tests/datahub/test_akshare_a_share_valuation_snapshot_adapter.py`
- `tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`
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

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`

Identify whether the blocker is:

- environment proxy configuration
- DNS/TCP/TLS/network reachability
- upstream route availability
- AKShare route behavior
- adapter/test design that unnecessarily makes an optional supplemental route closure-blocking

Record concrete evidence in `coordination/reports/TASK-028_REPORT.md`.

### 2. Remove unnecessary dependency on the blocked supplemental route where source-truth allows

The current implementation requires `float_market_cap` from `stock_individual_info_em`, which reaches `push2.eastmoney.com`. This supplemental route caused the live `SKIP`.

Apply feasible fixes in this order:

1. Prefer a bounded, one-symbol, no-credential route that truthfully provides `float_market_cap` without full-market scraping.
2. If no bounded route is available or reliable in the current environment, make `float_market_cap` optional in `DatasetName.VALUATION_SNAPSHOT` rather than synthesizing a fake value.
3. Keep `symbol`, `market`, `trade_date`, `pe_ttm`, `pb`, `market_cap`, `source`, `ingested_at`, and `schema_version` required.
4. Preserve the existing optional status for `ps_ttm` and `dividend_yield`.

If `float_market_cap` becomes optional:

- update `quant/datahub/datasets.py`
- update focused dataset tests
- update valuation adapter tests to prove no placeholder is emitted
- update live smoke assertions so absence of `float_market_cap` is acceptable when the record still validates
- record the schema optionality change and source-truth rationale in the report so the controller can update stable-interface notes after accepted review/integration

Do not set `float_market_cap` equal to `market_cap` unless a source explicitly says they are equal for that record.

### 3. Keep bounded route behavior

The rework must remain bounded to one requested A-share symbol.

Allowed route behavior:

- continue using `stock_zh_valuation_baidu(symbol="<6-digit-code>", indicator="<metric>", period="近一年")` for required core valuation fields when available
- keep `stock_individual_info_em(symbol="<6-digit-code>")` as a supplemental route only if its failure does not block a valid source-truth record
- keep `stock_zh_valuation_comparison_em(symbol="<SH/SZ/BJ+6-digit>")` optional only
- add another bounded one-symbol public AKShare route only if it is no-credential, deterministic enough for live smoke, and does not expand beyond A-share valuation snapshot scope

Do not introduce broad full-market ingestion or full-market scraping as a live workaround. Default tests must remain offline and the rework must not create any hidden default network call.

### 4. Preserve hard-fail boundaries

The rework must not mask:

- schema/normalization bugs
- invalid symbols
- malformed payloads
- invalid dates
- invalid numeric values for emitted fields
- conflicting duplicate valuation rows
- non-serializable values

Only network/proxy/DNS/TLS/upstream/source availability failures may be classified for live `skipTest(...)`.

### 5. Update tests

Update deterministic offline tests for:

- live-blocking supplemental market-cap route unavailable but a valid source-truth record still emitted when `float_market_cap` is optional
- `float_market_cap` omitted rather than synthesized, if optionality is changed
- record validation through `DatasetRegistry.validate_record(...)`
- required core fields remain required and hard-fail if missing
- live classifier still skips true network/source availability failures
- adapter/schema failures still fail the live test

Default tests must not perform real network calls.

### 6. Mandatory live smoke rerun

Run the live smoke after rework:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`

The desired closure evidence is live-enabled `PASS`.

If it still skips/fails due network/proxy/DNS/TLS/upstream/source availability, do not claim closure. The report must include:

- exact command
- PASS/SKIP/FAIL result
- exception class/message evidence
- route(s) attempted
- repository-level fixes attempted
- why no further repository-level fix is feasible
- operator action required

## Do Not Implement

Do not implement:

- new datasets beyond `DatasetName.VALUATION_SNAPSHOT`
- HK, ETF, fund, index, policy, capital-flow, or corporate-action adapters
- broad full-market valuation ingestion
- derived feature logic, scanner filters, strategy logic, AI reports, notifications, or UI
- credentialed source behavior

## Testing Requirements

Default tests must remain offline.

Run focused tests:

`python3 -m unittest tests/datahub/test_akshare_a_share_valuation_snapshot_adapter.py`

`python3 -m unittest -v tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`

Run related regressions:

`python3 -m unittest tests/datahub/test_datasets.py`

`python3 -m unittest tests/datahub/test_source_catalog.py`

`python3 -m unittest tests/datahub/test_akshare_adapter.py`

`python3 -m unittest tests/datahub/test_source.py`

`python3 -m unittest tests/datahub/test_quality.py`

Run full DataHub discovery:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Run gated live smoke:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_valuation_snapshot_live.py`

## Acceptance Criteria

The rework is acceptable when:

- TASK-028 remains scoped to one-symbol A-share `VALUATION_SNAPSHOT`
- default tests remain offline-safe and pass
- live-enabled result is truthfully recorded
- live-enabled `PASS` is provided if a bounded public valuation route is reachable after feasible fixes
- any remaining live `SKIP`/`FAIL` includes root-cause evidence and feasible-fix evidence, not just documentation
- no placeholder valuation values are invented
- any minimal schema optionality change is justified, tested, and reported
- no future-phase module contains new logic
- updated report exists at `coordination/reports/TASK-028_REPORT.md`

## Report Path

`coordination/reports/TASK-028_REPORT.md`

## Review Path

`coordination/reviews/TASK-028_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-028_INTEGRATION.md`
