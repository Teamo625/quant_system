# TASK-012 Rework: AKShare Live Smoke and Report Consistency

## Task ID

TASK-012

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

TASK-012 attempted to add the first narrow real-source adapter seed: AKShare A-share `daily_bars`.

The review and integration did not accept the task yet:

- Review decision: `Changes Requested`
- Integration decision: `Not Integrated (Changes Requested)`

The blocking issue is not the offline adapter contract path. Offline default tests passed during review/integration. The blocker is live smoke consistency and environment handling:

- `coordination/reports/TASK-012_REPORT.md` claimed `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest tests/datahub/test_akshare_live.py` passed.
- Review and integration reproduced the same command as `FAILED (errors=1)` due to `requests.exceptions.ProxyError` against `push2his.eastmoney.com`.
- The live smoke test currently surfaces external proxy/network unavailability as an uncategorized error instead of a clear environment skip.

The execution window must read:

- `AGENTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-012_DATAHUB_AKSHARE_LIVE_SMOKE_REWORK.md`
- `coordination/reviews/TASK-012_REVIEW.md`
- `coordination/integrations/TASK-012_INTEGRATION.md`

## Goal

Resolve the TASK-012 blocking review/integration feedback without expanding adapter scope.

The goal is to make live smoke behavior truthful and reviewable:

- default tests remain offline and skip live smoke by default
- the mandatory live smoke test still exists
- when `QUANT_SYSTEM_LIVE_TESTS=1` is set, the test either:
  - fetches a tiny live AKShare sample and validates it successfully, or
  - emits an explicit `skipTest(...)` for known environment unavailability such as missing AKShare, public network/proxy failure, timeout, DNS failure, or remote source unavailability
- the execution report must record the actual observed live-enabled result, including PASS, SKIP with reason, or FAIL with reason

## Allowed Files

The execution window may create or modify only:

- `tests/datahub/test_akshare_live.py`
- `tests/datahub/test_akshare_adapter.py` only if needed for focused regression coverage
- `quant/datahub/adapters/akshare.py` only if adapter-level exception wrapping is necessary to support clear live smoke behavior
- `coordination/reports/TASK-012_REPORT.md`

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
- any handoff file under `coordination/handoffs/**`
- `quant/features/**`
- `quant/strategies/**`
- `quant/backtest/**`
- `quant/scanner/**`
- `quant/portfolio/**`
- `quant/notification/**`
- `quant/ai/**`
- `quant/ui/**`

## Implementation Requirements

### 1. Fix live smoke environment handling

Update `tests/datahub/test_akshare_live.py` so the live-enabled test handles expected environment failures explicitly.

At minimum, known environment failures should become `self.skipTest(...)` with a clear reason, not an uncategorized unittest error:

- AKShare import missing or unusable
- public network unavailable
- proxy connection failure
- DNS/name resolution failure
- connection timeout or read timeout
- remote source temporarily unavailable or returning no usable bounded sample

Use broad enough exception handling to catch common network/client failures from AKShare dependencies, but do not hide adapter/data-contract bugs as environment skips.

Examples that should remain failures rather than skips:

- normalized records fail `DatasetRegistry.validate_record(...)`
- adapter returns malformed records after a successful fetch
- wrong dataset/source contract behavior
- unexpected assertion failures in the test

### 2. Preserve mandatory live smoke requirement

The live smoke test remains mandatory for TASK-012.

It must still:

- be skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1`
- use no credentials
- target a tiny bounded sample, such as one A-share symbol over a short historical date range
- validate any successfully fetched record through `DatasetRegistry.validate_record(...)`

A live-enabled skip is acceptable only when it clearly states an environment/source availability reason. The report must not call this PASS.

### 3. Correct the execution report

Update `coordination/reports/TASK-012_REPORT.md` so it is truthful after rework.

The report must include:

- files changed in this rework
- tests run in this rework
- default network behavior
- live smoke test implementation and live-enabled run status
- exact result of `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest tests/datahub/test_akshare_live.py` if run
- if live-enabled test skips, record the skip reason exactly enough for review
- if live-enabled test cannot be run because the environment variable is intentionally not enabled, state that explicitly
- deviations from this rework handoff
- remaining risks or follow-up tasks

Do not leave the previous incorrect claim that the live-enabled command passed if the current environment actually skipped or failed.

## Do Not Implement

Do not implement:

- new source adapters
- wider A-share dataset coverage
- batched symbol fetching
- Hong Kong stock adapters
- ETF/fund adapters
- index/sector/macro/news/announcement adapters
- local warehouse refresh orchestration
- credentials, cookies, browser automation, or private account flows
- strategy, backtest, scanner, AI, notification, UI, or automated trading logic

Do not change the TASK-012 adapter scope unless a tiny exception wrapper in `quant/datahub/adapters/akshare.py` is strictly necessary for live smoke clarity.

## Testing Requirements

Default tests must remain offline.

Run:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Run focused tests:

`python3 -m unittest tests/datahub/test_akshare_live.py`

`python3 -m unittest tests/datahub/test_akshare_adapter.py`

If adapter code is touched, also run any relevant focused adapter/source tests:

`python3 -m unittest tests/datahub/test_source.py`

Because TASK-012 is a real-source adapter task, the gated live smoke command should be run when explicitly enabled in the local environment:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest tests/datahub/test_akshare_live.py`

If this environment cannot reach the public source or proxy, the command should complete as a clear skip instead of an uncategorized error, and the report must record that skip.

## Acceptance Criteria

The rework is acceptable when:

- `tests/datahub/test_akshare_live.py` no longer fails with an uncategorized `ProxyError` when `QUANT_SYSTEM_LIVE_TESTS=1` but public network/proxy is unavailable
- live-enabled environment unavailability is represented as an explicit skip with a clear reason
- successful live fetches still validate at least one normalized record through `DatasetRegistry.validate_record(...)`
- adapter/data-contract bugs still fail rather than being hidden as skips
- default test discovery remains offline and passes with the live smoke skipped by default
- `coordination/reports/TASK-012_REPORT.md` accurately records the current observed live-enabled outcome
- no forbidden files or future-phase modules are modified

## Report Path

`coordination/reports/TASK-012_REPORT.md`

## Review Path

`coordination/reviews/TASK-012_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-012_INTEGRATION.md`

## Out of Scope

Everything outside TASK-012 live smoke/report consistency rework is out of scope.
