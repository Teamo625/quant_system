# TASK-128 DataHub Sector Daily-Bar Live Classifier Rework

## Role

5.3 Execution Window.

## Phase

Phase 2.5-P DataHub Personal Trading Perfection Re-Review.

## Context

TASK-128 original execution reported successful sector/concept cluster hardening and live-enabled PASS evidence. Review rejected closure because the changed `sector_daily_bars` live smoke still catches broad `ValueError` failures and can downgrade repository-side defects into environment/source `SKIP`.

Review finding:

- `tests/datahub/test_akshare_sector_live.py:120` catches any `ValueError` from the live sector daily-bar smoke and maps it to `empty_results` / skip.
- The original handoff explicitly required repository-side schema, contract, normalization, duplicate-conflict, route-signature, call-compatibility, unbounded-fetch, and date-window defects to fail rather than skip.
- The live-enabled daily-bar and membership suites passed in the current environment, and default tests were offline-safe, but the daily-bar live classifier is not closure-grade.

This rework must stay focused on that Review blocker only. Do not merge with readiness `follow_up_batches` or ordinary sector/concept hardening items.

## Objective

Tighten the sector daily-bar live-smoke classifier so repository-side `ValueError` defects fail clearly instead of being reported as environment/source unavailability.

The rework is complete only when the live daily-bar smoke can still truthfully skip genuine network/proxy/DNS/TLS/upstream/source availability problems, while route/schema/normalization/date-window/duplicate-conflict and other repository-side defects remain hard failures.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-128_DATAHUB_SECTOR_DAILY_BAR_LIVE_CLASSIFIER_REWORK.md`
- `coordination/handoffs/TASK-128_DATAHUB_SECTOR_CONCEPT_CLUSTER_HARDENING.md`
- `coordination/reports/TASK-128_REPORT.md`
- `coordination/reviews/TASK-128_REVIEW.md`
- `tests/datahub/test_akshare_sector_live.py`
- `tests/datahub/test_akshare_sector_adapter.py` only as needed to understand sector daily-bar failure messages
- `quant/datahub/adapters/akshare.py` only as needed to understand the exceptions raised by the sector daily-bar adapter

## Allowed Writes

Only:

- `tests/datahub/test_akshare_sector_live.py`
- `tests/datahub/test_akshare_sector_adapter.py` only if a focused offline regression is needed to prove the classifier boundary
- `coordination/reports/TASK-128_REPORT.md`

Do not modify production adapter code unless the live classifier investigation proves the Review blocker cannot be fixed in tests alone and the repository-side exception taxonomy itself is defective. If that happens, stop and document the blocker in the report instead of broadening the task.

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files other than `coordination/reports/TASK-128_REPORT.md`
- `coordination/reviews/**`
- `coordination/integrations/**`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- unrelated DataHub adapters or tests
- `quant/features/**`
- `quant/scanner/**`
- `quant/strategies/**`
- `quant/backtest/**`
- `quant/portfolio/**`
- `quant/notification/**`
- `quant/ai/**`
- `quant/ui/**`

Do not use credentials, tokens, cookies, browser session state, private account data, paid sources, or hidden default live network behavior.

Do not implement new sector/concept capability breadth, FeatureHub features, Scanner logic, strategy/backtest logic, portfolio/signal/risk, AI reports, notification, UI, or automated trading.

## Implementation Requirements

- Replace the broad `ValueError` skip behavior in the sector daily-bar live smoke with narrow classification.
- Genuine environment/source availability failures may still skip only when the exception evidence clearly indicates network, proxy, DNS, TLS, upstream disconnect/timeout, source unavailability, or a source-wide no-data response.
- Repository-side defects must fail, including but not limited to:
  - normalization errors
  - unsupported or malformed sector identifier handling defects
  - duplicate-conflict errors
  - schema/contract errors
  - route-signature or call-compatibility errors
  - unbounded-fetch defects
  - requested-window filtering defects
  - mixed-success partial-output defects
- Preserve `QUANT_SYSTEM_LIVE_TESTS` gating. Default tests must remain offline-safe and skipped by default when the environment variable is unset.
- Keep the rework minimal. Do not alter capability status, source-catalog wording, or sector adapter behavior unless the Review blocker cannot be fixed without broadening scope.

## Tests

Required offline/default tests:

- `python3 -m unittest tests.datahub.test_akshare_sector_adapter`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_sector_live`

Run any focused offline regression test added or changed by this rework.

Live smoke requirement:

- Run `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_sector_live`.
- Report PASS, SKIP, or FAIL truthfully with root-cause evidence.
- If the live smoke skips because of network, proxy, DNS, TLS, upstream, or public-source availability, diagnose the root cause and fix repository code/tests where feasible before reporting the result.

Optional compatibility check if touched or useful:

- `python3 -m unittest tests.datahub.test_source_capabilities`
- `python3 -m unittest tests.datahub.test_source_catalog`

## Completion Report

Update `coordination/reports/TASK-128_REPORT.md` with a rework section including:

- files changed
- implementation summary focused on the live classifier boundary
- exact Review finding addressed
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled sector daily-bar PASS/SKIP/FAIL result with root-cause evidence
- confirmation that membership/history behavior was not changed, unless explicitly unavoidable
- deviations from this rework handoff
- residual risks or follow-up tasks

## Completion Criteria

The rework is complete when:

- Broad `ValueError` catch-and-skip behavior no longer masks repository-side sector daily-bar defects.
- Default tests remain offline-safe.
- The sector daily-bar live smoke remains gated and has truthful PASS/SKIP/FAIL evidence.
- `coordination/reports/TASK-128_REPORT.md` records the rework outcome.
- No inactive downstream module behavior or ordinary readiness hardening is introduced.
