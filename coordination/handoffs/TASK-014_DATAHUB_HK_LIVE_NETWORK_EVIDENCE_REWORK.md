# TASK-014 Rework: Diagnose and Fix HK Live Smoke Connectivity

## Task ID

TASK-014

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

TASK-014 attempted to add the AKShare Hong Kong `daily_bars` adapter.

The adapter implementation and offline tests are broadly in shape, but TASK-014 is not accepted yet:

- Review decision: `Changes Requested`
- Integration decision: `Not Integrated (Changes Requested)`

The review blocker is live smoke reliability and evidence quality:

- Review observed `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_live.py` as `OK (skipped=1)` due to `ProxyError` against `33.push2his.eastmoney.com`.
- Review required a root-cause analysis for the live connectivity failure, not just a skip record.
- Integration later observed the same live-enabled command passing, which suggests environment/source reachability changed, but the accepted review still requires diagnosis and a durable fix where possible.

The owner clarified that this rework must not be report-only: the execution window must analyze the live-network failure cause and fix it within the repository when feasible.

The owner also clarified the forward rule for similar cases: live-enabled network/source failures must be handled by the separated roles. Execution performs diagnosis and feasible modifications, Review Agent independently reviews the rework, and Integration Agent integrates only after acceptance. The controller must not close this class of blocker from a controller-only judgment.

The execution window must read:

- `AGENTS.md`
- `docs/05_TESTING_POLICY.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-014_DATAHUB_HK_LIVE_NETWORK_EVIDENCE_REWORK.md`
- `coordination/reviews/TASK-014_REVIEW.md`
- `coordination/integrations/TASK-014_INTEGRATION.md`
- `coordination/reports/TASK-014_REPORT.md`

## Goal

Resolve the TASK-014 blocking feedback by diagnosing the HK live smoke connectivity failure and fixing the adapter/live-smoke path where feasible.

The expected outcome is not merely documenting the failure. The execution window should determine why the HK live smoke hit `ProxyError` and make the TASK-014 live smoke path more robust or correct, while preserving deterministic offline tests.

## Allowed Files

The execution window may create or modify only:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py` only if exports need adjustment
- `quant/datahub/__init__.py` only if exports need adjustment
- `tests/datahub/test_akshare_hk_live.py`
- `tests/datahub/test_akshare_hk_adapter.py`
- `coordination/reports/TASK-014_REPORT.md`

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

## Implementation Requirements

### 1. Diagnose the live-network failure

Run safe diagnostics and record conclusions in `coordination/reports/TASK-014_REPORT.md`.

At minimum, diagnose:

- relevant proxy environment variables, with any sensitive values redacted
- DNS resolution for `33.push2his.eastmoney.com`
- TCP connectivity to `33.push2his.eastmoney.com:443`
- TLS/HTTPS behavior for `33.push2his.eastmoney.com:443`
- whether AKShare HK historical data currently routes through Eastmoney/push2his for this adapter
- whether the failure appears to be:
  - adapter implementation bug
  - AKShare function/parameter/symbol mismatch
  - local proxy configuration issue
  - network policy issue
  - transient upstream/source availability issue

Do not commit credentials, tokens, cookies, private proxy secrets, or private account data.

### 2. Fix the live-smoke path where feasible

After diagnosis, make a repository-level fix if the failure can be mitigated by code or test changes.

Examples of acceptable fixes:

- correct AKShare HK function parameters or symbol conversion if the live call was malformed
- add a supported alternate public AKShare HK historical function fallback if the primary function or endpoint is unstable
- adjust the live smoke to use a more reliable liquid HK symbol/date window while preserving contract validation
- improve environment-unavailable classification only if it remains necessary, but do not stop at skip handling when a real fix is possible
- add offline tests covering any fallback or corrected behavior

If the root cause is external and not fixable in repository code, the execution window must still:

- explain why it is not fixable in repo code
- keep the live smoke as an explicit skip for that environment
- provide a concrete operator action, such as proxy/network policy correction
- record whether the live-enabled command now passes, skips, or fails

### 3. Preserve live smoke semantics

The mandatory live smoke test must remain:

- skipped by default unless `QUANT_SYSTEM_LIVE_TESTS=1`
- credential-free
- bounded to a tiny HK stock sample
- validating at least one successful live record through `DatasetRegistry.validate_record(...)`
- failing for adapter/data-contract bugs
- skipping only for clearly diagnosed external environment/source unavailability

Do not turn real data-contract failures into skips.

### 4. Correct the execution report

Update `coordination/reports/TASK-014_REPORT.md` with:

- files changed in this rework
- diagnostic commands and conclusions
- root-cause attribution
- fix implemented, or a precise explanation why no repo-level fix was possible
- exact default live-test command result
- exact live-enabled command result:
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_live.py`
- if live-enabled passes, record the successful test case and validation path
- if live-enabled skips, record the exact skip reason and why this is external/unfixable in repo code
- offline/focused tests run after any code changes
- deviations and follow-up risks

## Do Not Implement

Do not implement:

- new source adapters
- HK instrument master, corporate actions, valuation, capital flow, announcements, or full-market ingestion jobs
- ETF/fund adapters
- index adapters
- sector/concept adapters
- macro/policy/news adapters
- raw/normalized warehouse refresh orchestration
- credentials, cookies, browser automation, or private account flows
- strategy, backtest, scanner, AI, notification, UI, or automated trading logic

## Testing Requirements

Run the key live command:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_live.py`

Run default live-test gate command:

`python3 -m unittest -v tests/datahub/test_akshare_hk_live.py`

If code or tests are changed, run focused offline tests:

`python3 -m unittest tests/datahub/test_akshare_hk_adapter.py`

If shared AKShare adapter helpers are changed, also run relevant existing focused tests:

`python3 -m unittest tests/datahub/test_akshare_adapter.py`

`python3 -m unittest tests/datahub/test_akshare_calendar_adapter.py`

Run the default DataHub suite if code changes are non-trivial:

`python3 -m unittest discover -s tests/datahub -p 'test_*.py'`

Record all commands and results in `coordination/reports/TASK-014_REPORT.md`.

## Acceptance Criteria

The rework is acceptable when:

- the report includes a clear live-network root-cause analysis
- the execution window implements a repository-level fix when feasible
- if no repository-level fix is feasible, the report explains why and gives concrete operator action
- the live-enabled command result is recorded truthfully as PASS, SKIP, or FAIL
- the mandatory live smoke remains skipped by default and gated by `QUANT_SYSTEM_LIVE_TESTS=1`
- successful live fetches still validate normalized records through `DatasetRegistry.validate_record(...)`
- adapter/data-contract bugs still fail rather than being hidden as skips
- no future-phase modules are touched

## Report Path

`coordination/reports/TASK-014_REPORT.md`

## Review Path

`coordination/reviews/TASK-014_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-014_INTEGRATION.md`

## Out of Scope

Everything outside TASK-014 HK live-smoke diagnosis/fix and narrowly related report/test/adapter updates is out of scope.
