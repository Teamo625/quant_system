# TASK-096 DataHub A-share Minute Bars Live PASS Rerun

## Role

5.3 Execution Window.

## Context

TASK-096 remains open in Phase 2.5-P.

The latest Review accepted the focused retention rework scope:

- the fixed `10` calendar-day guard for public `1`-minute history was removed
- `1`-minute retention now prefers latest-5-trade-date resolution and falls back conservatively only when trade-date resolution is unavailable
- offline holiday / long-closure regression coverage was added
- default tests remained offline-safe

However, Controller closure is still not allowed because the live-enabled Eastmoney smoke remained `SKIP` from the local proxy/connectivity environment:

- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_minute_bars_live.py` reproduced `ProxyError` against `push2his.eastmoney.com`
- Review found no additional repository-side defect, but Phase 2.5-P real-source closure still requires fresh live evidence from an environment that can reach Eastmoney or a working configured proxy path

## Objective

Rerun TASK-096 from a live-capable environment and produce truthful live-enabled evidence for A-share `DatasetName.MINUTE_BARS` public Eastmoney/AKShare coverage.

This handoff is a narrow live-evidence rerun. Do not broaden DataHub minute-bar behavior unless the live run reveals a repository-side defect that must be fixed inside the allowed files.

## Allowed Writes

Only:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/source_capabilities.py`
- `tests/datahub/test_akshare_a_share_minute_bars_adapter.py`
- `tests/datahub/test_akshare_a_share_minute_bars_live.py`
- `tests/datahub/test_source_capabilities.py`
- `coordination/reports/TASK-096_REPORT.md`

Expected write path if live reaches Eastmoney and passes without code defects:

- update only `coordination/reports/TASK-096_REPORT.md` with fresh test evidence

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

## Required Work

1. Confirm the live environment can reach Eastmoney or has a working proxy path.
   - The prior blocked environment used `http://127.0.0.1:7892` and reproduced `ProxyError`.
   - If local proxy variables are present, record whether they are used or unset for the run.
   - Do not commit secrets, credentials, cookies, or private network configuration.

2. Rerun the required default/offline tests.
   - Default tests must remain offline-safe.
   - The live smoke file must still skip by default unless `QUANT_SYSTEM_LIVE_TESTS=1`.

3. Rerun the live-enabled smoke.
   - The target closure-ready result is `PASS`.
   - The live smoke should validate a bounded public historical minute-bar sample beyond a latest-only path.
   - If the result is `SKIP` or `FAIL`, diagnose the root cause and make feasible repository code/test/report fixes inside allowed files.
   - If the root cause remains network, proxy, DNS, TLS, upstream availability, or public-source availability, report it truthfully and do not claim Controller closure readiness.

4. Preserve capability truth and scope.
   - Keep `a_share_minute_bars` conservative unless the rerun and any necessary code fix prove stronger public-source breadth.
   - Do not synthesize bars, sessions, historical continuity, adjusted values, or liquidity fields.
   - Preserve bounded requests, symbol validation, deterministic sorting, duplicate handling, and `DatasetRegistry.validate_record(DatasetName.MINUTE_BARS, ...)` compatibility.

## Required Tests

Run:

- `python3 -m unittest tests/datahub/test_akshare_a_share_minute_bars_adapter.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`
- `python3 -m unittest -v tests/datahub/test_akshare_a_share_minute_bars_live.py`
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_minute_bars_live.py`

## Completion Report

Update `coordination/reports/TASK-096_REPORT.md` with:

- files changed
- tests run
- default network behavior
- live environment/proxy conditions relevant to the rerun
- live-enabled `PASS`, `SKIP`, or `FAIL` result with root-cause evidence
- whether any repository code/test change was needed after the live rerun
- whether `a_share_minute_bars` capability truth changed
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

TASK-096 is closure-ready only when:

- required default tests pass and remain offline-safe
- the live smoke file remains skipped by default
- the live-enabled Eastmoney smoke records a truthful `PASS`
- any live-discovered repository-side defect is fixed and covered within allowed files
- fresh Review Agent verification states Controller closure is allowed

A truthful `SKIP` or `FAIL` report may be reviewed, but it does not satisfy Controller closure for TASK-096 under the current Phase 2.5-P live-source rules.
