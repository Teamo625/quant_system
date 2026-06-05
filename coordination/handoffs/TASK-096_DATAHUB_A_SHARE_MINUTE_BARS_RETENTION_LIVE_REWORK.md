# TASK-096 DataHub A-share Minute Bars Retention and Live Rework

## Role

5.3 Execution Window.

## Context

TASK-096 initial Review returned `REWORK REQUIRED`.

Review findings:

- The adapter added a fixed `10` calendar-day guard for public `1`-minute history, but the execution report says the inspected upstream `stock_zh_a_hist_min_em(period='1')` route uses `ndays=5` trading days. A calendar-day guard can reject still-reachable data around long exchange closures before any fetch attempt.
- Offline tests only covered a clearly stale window and did not protect the holiday / long-closure regression.
- The live-enabled smoke still skipped because Eastmoney was unreachable through the local proxy / network path, so TASK-096 cannot close under the Phase 2.5-P live-smoke rules.

Phase 2.5-P remains active. TASK-096 must stay open and must not enter Integration until a fresh Review accepts the rework.

## Objective

Rework TASK-096 narrowly so A-share `DatasetName.MINUTE_BARS` `1`-minute retention handling is source-backed and trading-day-aware, and so the Eastmoney live-enabled smoke skip is diagnosed and rerun with truthful evidence.

Do not broaden this task beyond the reviewed blocker. Preserve existing caller-provided multi-symbol bounded minute-bar behavior and the conservative `a_share_minute_bars` capability truth unless source-backed implementation plus live evidence justify a change.

## Allowed Writes

Only:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/source_capabilities.py`
- `tests/datahub/test_akshare_a_share_minute_bars_adapter.py`
- `tests/datahub/test_akshare_a_share_minute_bars_live.py`
- `tests/datahub/test_source_capabilities.py`
- `coordination/reports/TASK-096_REPORT.md`

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files except `coordination/reports/TASK-096_REPORT.md`
- `coordination/reviews/**`
- `coordination/integrations/**`
- `quant/datahub/datasets.py`
- `quant/datahub/source_catalog.py`
- unrelated DataHub adapters or tests
- `quant/features/`
- `quant/scanner/`
- `quant/strategies/`
- `quant/backtest/`
- `quant/portfolio/`
- `quant/notification/`
- `quant/ai/`
- `quant/ui/`

Do not use credentials, cookies, tokens, browser session state, paid APIs, or private account data.

## Required Rework

1. Replace the fixed `10` calendar-day `1`-minute history guard with source-backed retention handling.
   - Prefer trading-day-aware logic aligned with the inspected upstream `ndays=5` trading-day behavior.
   - If a reliable trading-calendar helper is already available inside allowed code paths, use it without expanding scope.
   - If no suitable calendar helper is available within allowed writes, use a conservative source-backed rule that does not reject potentially reachable `5`-trading-day data during weekends or long exchange closures before attempting the primary route.
   - Do not synthesize bars, sessions, adjusted values, or continuity.

2. Add offline regression coverage for the reviewed failure mode.
   - Include a holiday / long-closure-style span where more than `10` calendar days can still fall within the upstream-reported `5` trading-day retention behavior.
   - Keep the clearly stale-window rejection test.
   - Prove unsupported fallback routes are not used to pretend they can satisfy old bounded historical windows.

3. Rework live smoke handling for the Eastmoney connectivity skip.
   - Keep the live smoke skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1`.
   - Rerun `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_minute_bars_live.py`.
   - If the environment can reach Eastmoney, the live smoke should validate a bounded public historical minute-bar sample beyond a latest-only path.
   - If the smoke still skips or fails due to proxy, DNS, TLS, upstream, or public-source availability, diagnose the root cause and make feasible repository code/test/report fixes within allowed files. Report `PASS`, `SKIP`, or `FAIL` truthfully and do not claim Controller closure readiness from an unresolved network/source skip.

4. Preserve phase and contract boundaries.
   - Do not promote `a_share_minute_bars` unless the reworked behavior and live evidence prove stronger personal trading breadth.
   - Keep `DatasetRegistry.validate_record(DatasetName.MINUTE_BARS, ...)` compatibility.
   - Preserve symbol validation, bounded requests, deterministic sorting, and duplicate handling by at least `(symbol, bar_time, interval, source)`.

## Required Tests

Run:

- `python3 -m unittest tests/datahub/test_akshare_a_share_minute_bars_adapter.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`
- `python3 -m unittest -v tests/datahub/test_akshare_a_share_minute_bars_live.py`
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_minute_bars_live.py`

Default tests must remain offline-safe. The live smoke file must remain skipped by default.

## Completion Report

Update `coordination/reports/TASK-096_REPORT.md` with:

- files changed
- tests run
- default network behavior
- exact retention rule used for public `1`-minute history and why it is source-backed
- offline regression evidence for holiday / long-closure retention behavior
- source routes investigated or changed
- live-enabled `PASS`, `SKIP`, or `FAIL` result with root-cause evidence
- whether `a_share_minute_bars` capability truth changed
- deviations from this rework handoff
- risks or follow-up tasks

## Completion Criteria

The rework is complete only when:

- the reviewed fixed-calendar retention blocker is removed or replaced with source-backed behavior
- offline tests cover the holiday / long-closure regression risk
- default tests remain offline-safe and live tests remain explicitly gated
- the live-enabled smoke is rerun and truthfully reported with root-cause evidence
- TASK-096 remains within DataHub Phase 2.5-P boundaries
