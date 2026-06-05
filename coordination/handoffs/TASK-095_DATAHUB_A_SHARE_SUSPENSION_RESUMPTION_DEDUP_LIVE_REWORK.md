# TASK-095 DataHub A-share Suspension/Resumption Deduplication and Live Coverage Rework

## Role

5.3 Execution Window.

## Context

The first TASK-095 execution attempted to harden A-share `DatasetName.SUSPENSION_RESUMPTION_EVENTS` breadth and taxonomy by adding supplemental Baidu trade-notify suspension/resumption evidence alongside the existing Eastmoney suspension-table path.

The Review Agent rejected the result. Controller closure is not allowed, Integration is not entered, and TASK-095 remains active.

Review findings to address:

- Supplemental Baidu resumption rows can duplicate a primary Eastmoney resumption event when both routes describe the same logical event.
- Offline coverage is missing for primary-plus-supplemental overlapping resumption deduplication.
- The live smoke reports PASS but does not specifically assert the new Baidu-backed resumption path or Baidu/Eastmoney overlap handling.

This rework stays inside Phase 2.5-P DataHub Personal Trading Perfection Re-Review. It must not reopen FeatureHub, Scanner, StrategyLab, BacktestEngine, portfolio, signal, risk, AI, notification, UI, or automated trading work.

## Objective

Fix TASK-095 so overlapping Eastmoney and Baidu rows produce one logical resumption event, not duplicate normalized records, while keeping source-truth behavior conservative and regression-tested.

Strengthen the live smoke only where feasible and stable enough: it should assert Baidu-backed resumption behavior or overlap handling when the public source sample exposes those rows, and otherwise report the limitation truthfully without making default tests live.

## Allowed Writes

Only:

- `quant/datahub/adapters/akshare.py`
- `tests/datahub/test_akshare_a_share_suspension_resumption_adapter.py`
- `tests/datahub/test_akshare_a_share_suspension_resumption_live.py`
- `coordination/reports/TASK-095_REPORT.md`

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination state files
- `quant/datahub/source_capabilities.py`, unless you first stop and report why Review findings cannot be fixed without capability metadata changes
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

Do not use credentials, cookies, browser session state, private account data, or paid/private APIs.

Do not implement downstream feature calculation, scanner ranking, strategy/backtest logic, portfolio/signal/risk, AI reports, notification, UI, or automated trading.

Do not run `git add`, `git commit`, `git reset`, `git checkout`, or any other git state-changing command.

## Implementation Requirements

- Reuse the existing AKShare A-share suspension/resumption adapter and `DatasetName.SUSPENSION_RESUMPTION_EVENTS` schema.
- Preserve the existing bounded request behavior. Do not add broad universe collection, full-history backfill, scheduler logic, or cross-source orchestration.
- Preserve deterministic symbol validation, date validation, sorting, injectable clock behavior, schema validation, and default-offline live test gating.
- Fix overlap behavior so supplemental Baidu resumption evidence does not create a second normalized resumption event when the primary route already yields the same logical resumption event.
- Treat the logical duplicate identity for the Review finding as at least `symbol + start_date + resume_date` for resumption rows. If the implementation uses a broader or narrower identity, justify it in `TASK-095_REPORT.md` and prove the reviewed duplicate case is fixed.
- Prefer merging supplemental source evidence into the existing logical event only when this can be done without inventing source truth. If merging would make provenance ambiguous, suppress the supplemental duplicate and keep the primary event.
- Do not infer resumption events, exact end dates, or taxonomy from absent rows, latest trading status, stock names, or generic text that does not expose exact source truth.
- Keep route-name-bearing AKShare argument/signature compatibility errors as hard failures under the existing DataHub live-failure classification policy.
- Keep `a_share_suspension_resumption` conservative. This rework is not a capability-promotion task.

## Required Offline Tests

Run:

- `python3 -m unittest tests/datahub/test_akshare_a_share_suspension_resumption_adapter.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_suspension_resumption_live.py`

Add an offline regression test that reproduces the Review finding:

- one Eastmoney primary row and one Baidu supplemental row describe the same symbol, suspension start date, and resume date
- adapter output contains exactly one logical `resumption` record for that event
- normalized records still validate against `DatasetName.SUSPENSION_RESUMPTION_EVENTS`

## Required Live-Enabled Smoke

Run:

- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_suspension_resumption_live.py`

Strengthen live coverage if feasible:

- assert a Baidu-backed exact `resumption` sample when the date/sample selected by the live test exposes source-backed `复牌时间`
- assert overlap behavior when the live-selected sample has the same symbol/start/resume dates across Eastmoney and Baidu
- if the public source does not expose such a stable overlap at runtime, keep the live smoke deterministic and report the live limitation explicitly rather than adding flaky source assumptions

If the live-enabled smoke fails or skips because of network, proxy, DNS, TLS, upstream, or public-source availability, diagnose the root cause and modify allowed code/tests/report where feasible. Report PASS, SKIP, or FAIL truthfully with evidence.

## Completion Report

Update `coordination/reports/TASK-095_REPORT.md` with:

- files changed
- Review findings addressed
- tests run
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence
- the duplicate identity used for Eastmoney/Baidu overlap handling
- offline regression evidence for the reviewed duplicate case
- live smoke assertion added, or the source-availability reason it could not be added safely
- capability truth changes, if any
- remaining public-source limitations
- deviations from this rework handoff
- risks or follow-up tasks

## Completion Criteria

The rework is complete only when:

- the Review Agent's duplicate resumption finding is fixed
- an offline regression test protects primary-plus-supplemental overlapping resumption deduplication
- default tests remain offline-safe and the live test file skips without `QUANT_SYSTEM_LIVE_TESTS=1`
- a live-enabled smoke is attempted and truthfully reported
- live coverage is strengthened where feasible without source flakiness or hidden default network calls
- TASK-095 report records the rework evidence clearly enough for a fresh Review Agent pass
