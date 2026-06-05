# TASK-096 DataHub A-share Minute Bars Confirmed Eastmoney Live PASS Rerun

## Role

5.3 Execution Window.

## Context

TASK-096 remains open in Phase 2.5-P.

The latest Review accepted the prior verified-Eastmoney live-rerun report as truthful, but denied Controller closure:

- Controller closure allowed: NO
- Default tests offline-safe: YES
- Live-enabled result: SKIP
- Rework required: YES

The latest rerun still did not satisfy the mandatory Eastmoney live gate:

- `quote.eastmoney.com` returned `200`, proving partial Eastmoney host reachability.
- the required `push2his.eastmoney.com` minute-bars API path still ended in remote disconnect / empty reply through both the resolved system proxy path and direct `NO_PROXY='*'` access.
- Review found no new repository-side phase, contract, code, or default-test blocker beyond the live PASS gate remaining open.

## Objective

Produce fresh TASK-096 live-enabled evidence from an environment with confirmed end-to-end Eastmoney `push2his.eastmoney.com` minute-bars API reachability or a verified working proxy path for that API route.

This is a narrow live-evidence rerun. Do not broaden DataHub minute-bar behavior unless the live run exposes a repository-side defect that must be fixed inside the allowed files.

## Allowed Writes

Only:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/source_capabilities.py`
- `tests/datahub/test_akshare_a_share_minute_bars_adapter.py`
- `tests/datahub/test_akshare_a_share_minute_bars_live.py`
- `tests/datahub/test_source_capabilities.py`
- `coordination/reports/TASK-096_REPORT.md`

Expected write path if the Eastmoney minute-bars API is reachable and the live smoke passes without repository defects:

- update only `coordination/reports/TASK-096_REPORT.md` with fresh test and reachability evidence

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

1. Verify the actual Eastmoney minute-bars API path before claiming a PASS-ready environment.
   - Probe `push2his.eastmoney.com` or the exact API route used by the live smoke, not only a generic Eastmoney web host.
   - Record whether proxy environment variables are absent, unset for direct access, or intentionally configured.
   - If a proxy is used, record only the non-secret endpoint shape needed for diagnosis.
   - If direct access is used, record the relevant direct-access condition, such as `NO_PROXY='*'`.
   - Do not add hidden default network behavior.

2. Rerun the required default/offline tests.
   - Default tests must remain offline-safe.
   - The live smoke file must still skip by default unless `QUANT_SYSTEM_LIVE_TESTS=1`.
   - If the shell has `QUANT_SYSTEM_LIVE_TESTS` preset, include an explicit `env -u QUANT_SYSTEM_LIVE_TESTS ...` default-skip check.

3. Rerun the live-enabled smoke.
   - The target closure-ready result is `PASS`.
   - The live smoke must validate a bounded public historical minute-bar sample beyond a latest-only path.
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

When `QUANT_SYSTEM_LIVE_TESTS` is already set in the shell, also run:

- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_minute_bars_live.py`

## Completion Report

Update `coordination/reports/TASK-096_REPORT.md` with:

- files changed
- tests run
- default network behavior
- live environment/proxy conditions relevant to the rerun
- Eastmoney `push2his.eastmoney.com` or exact minute-bars API reachability evidence before or during the live smoke
- live-enabled `PASS`, `SKIP`, or `FAIL` result with root-cause evidence
- whether any repository code/test change was needed after the live rerun
- whether `a_share_minute_bars` capability truth changed
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

TASK-096 is closure-ready only when:

- required default tests pass and remain offline-safe
- the live smoke file remains skipped by default
- the live-enabled Eastmoney minute-bars smoke records a truthful `PASS`
- any live-discovered repository-side defect is fixed and covered within allowed files
- fresh Review Agent verification states Controller closure is allowed

A truthful `SKIP` or `FAIL` report may be reviewed, but it does not satisfy Controller closure for TASK-096 under the current Phase 2.5-P live-source rules.
