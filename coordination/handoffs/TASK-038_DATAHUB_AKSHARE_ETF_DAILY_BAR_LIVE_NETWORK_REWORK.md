# TASK-038 Rework: DataHub AKShare ETF Daily Bar Live-Network Gate

## Task ID

TASK-038

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

TASK-038 implemented the AKShare-backed China ETF `DatasetName.DAILY_BARS` adapter and deterministic offline tests. The initial execution report records a live-enabled PASS, and the Review Agent accepted the implementation. However, the independent review live-enabled smoke skipped in the reviewer environment because of proxy/network unavailability to the Eastmoney historical quote host.

Review evidence:

- `coordination/reviews/TASK-038_REVIEW.md`
- live-enabled command: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_etf_daily_bar_live.py`
- observed reviewer result: `OK (skipped=1)`
- skip cause: proxy/network unavailability reaching `push2his.eastmoney.com`

Integration recorded that the implementation is present and accepted, but explicitly deferred final controller closure to the AGENTS.md live-smoke gate:

- `coordination/integrations/TASK-038_INTEGRATION.md`

Per `AGENTS.md` and `coordination/PHASE_GATE.md`, a live-enabled network/proxy/DNS/TLS/upstream failure or skip cannot be counted as closed without an explicit 5.3 rework, fresh review, and integration. This handoff exists to diagnose the live blocker and apply feasible repository-level fixes before final closure.

The execution window must read:

- `AGENTS.md`
- `docs/02_MODULE_BOUNDARIES.md`
- `docs/03_DATA_CONTRACTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-038_DATAHUB_AKSHARE_ETF_DAILY_BAR_ADAPTER.md`
- `coordination/handoffs/TASK-038_DATAHUB_AKSHARE_ETF_DAILY_BAR_LIVE_NETWORK_REWORK.md`
- `coordination/reports/TASK-038_REPORT.md`
- `coordination/reviews/TASK-038_REVIEW.md`
- `coordination/integrations/TASK-038_INTEGRATION.md`

## Goal

Rework the TASK-038 ETF daily-bar adapter/tests so the live-enabled smoke can reach a closure-ready result when feasible, while preserving offline determinism, source-truth behavior, and the narrow one-ETF `DAILY_BARS` scope.

Target result:

- default tests remain offline-safe and pass
- live-enabled smoke should produce `PASS` if a bounded public ETF daily-bar path is available
- if live-enabled smoke still `SKIP`/`FAIL`s due network/proxy/DNS/TLS/upstream availability after feasible fixes, the report must truthfully include root-cause evidence, attempted fixes, and operator action required

## Allowed Files

The execution window may create or modify:

- `quant/datahub/**`
- `tests/datahub/**`
- `coordination/reports/TASK-038_REPORT.md`

Suggested implementation locations:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `quant/datahub/source_catalog.py` only if strict source-catalog assertion alignment is required
- `tests/datahub/test_akshare_etf_daily_bar_adapter.py`
- `tests/datahub/test_akshare_etf_daily_bar_live.py`
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

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_etf_daily_bar_live.py`

Identify whether the blocker is:

- environment proxy configuration
- DNS/TCP/TLS/network reachability
- upstream route availability
- AKShare route behavior
- adapter/test design that unnecessarily depends on one host when an equivalent bounded route exists

Record concrete evidence in `coordination/reports/TASK-038_REPORT.md`.

### 2. Try feasible bounded route resilience

The current live skip was observed while reaching the AKShare ETF historical daily route host:

- AKShare route: `fund_etf_hist_em`
- observed upstream host: `push2his.eastmoney.com`

Apply feasible fixes without expanding scope:

1. Preserve the existing AKShare route as the preferred route when available.
2. Investigate whether the local AKShare version exposes another bounded, one-ETF, no-credential ETF historical bar route or parameterization that can provide the same `DAILY_BARS` fields.
3. If adding a fallback, keep it narrowly scoped to:
   - one requested China ETF symbol
   - `DatasetName.DAILY_BARS`
   - `market=ETF_CN`
   - no credentials
   - deterministic parsing equivalent to the existing daily-bar contract
4. Keep source identity as `akshare_cn_hk_public_family` unless the implemented source family truly changes. Do not add a new source id in this rework.
5. Do not implement broad ETF universe ingestion, non-ETF fund bars, LOF bars, fund NAV/profile/holdings changes, or full-market scraping as a workaround.

### 3. Preserve hard-fail boundaries

The rework must not mask:

- schema/normalization bugs
- invalid ETF symbols
- malformed payloads
- missing required OHLCV/amount fields
- invalid dates
- invalid numeric values for emitted fields
- conflicting duplicate daily-bar rows
- non-serializable values

Only network/proxy/DNS/TLS/upstream/source availability failures may be classified for live `skipTest(...)`.

### 4. Update tests

Update deterministic offline tests for any fallback or live-classification behavior added:

- route order and fallback selection, if a fallback is added
- fallback parsing still returns records compatible with `DatasetRegistry.validate_record(...)`
- default tests remain offline-safe and use injected fixtures/callables
- primary-route contract failures remain hard failures
- true network/source availability failures are classified only in live diagnostics
- adapter/schema/normalization errors still fail the live test

If no code change is feasible, add or refine tests only when they improve the distinction between source unavailability and adapter defects.

### 5. Mandatory live smoke rerun

Run the live smoke after rework:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_etf_daily_bar_live.py`

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

- new datasets beyond `DatasetName.DAILY_BARS`
- broad ETF or fund universe ingestion
- non-ETF fund daily bars
- LOF or money-market fund adapters
- ETF/fund capital flow
- fund profile, NAV, or holdings changes
- storage refresh orchestration
- derived feature logic, scanner filters, strategy logic, AI reports, notifications, UI, or automated trading
- credentialed source behavior

## Testing Requirements

Default tests must remain offline.

Run focused tests:

`python3 -m unittest tests/datahub/test_akshare_etf_daily_bar_adapter.py`

`python3 -m unittest -v tests/datahub/test_akshare_etf_daily_bar_live.py`

Run related regressions:

`python3 -m unittest tests/datahub/test_source_catalog.py`

`python3 -m unittest tests/datahub/test_akshare_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_hk_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_fund_nav_adapter.py`

`python3 -m unittest tests/datahub/test_source.py`

Run full DataHub discovery:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Run gated live smoke:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_etf_daily_bar_live.py`

## Acceptance Criteria

The rework is acceptable when:

- TASK-038 remains scoped to one-symbol China ETF `DAILY_BARS`
- default tests remain offline-safe and pass
- live-enabled result is truthfully recorded
- live-enabled `PASS` is provided if a bounded public ETF daily-bar route is reachable after feasible fixes
- any remaining live `SKIP`/`FAIL` includes root-cause evidence and feasible-fix evidence, not just documentation
- no placeholder price/volume values are invented
- no future-phase module contains new logic
- updated report exists at `coordination/reports/TASK-038_REPORT.md`

## Report Path

`coordination/reports/TASK-038_REPORT.md`

## Review Path

`coordination/reviews/TASK-038_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-038_INTEGRATION.md`
