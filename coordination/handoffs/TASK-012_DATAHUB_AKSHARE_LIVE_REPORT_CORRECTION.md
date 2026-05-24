# TASK-012 Rework: AKShare Live Smoke Report Correction

## Task ID

TASK-012

## Owner Role

5.3 execution window

## Status

Ready

## Phase

Phase 2: DataHub Comprehensive Source Collection

## Context

TASK-012 is still not accepted.

The latest rework fixed the live smoke code behavior, but review and integration still requested changes because the execution report does not record the live-enabled skip evidence precisely enough.

Latest decisions:

- Review decision: `Changes Requested`
- Integration decision: `Not Integrated (Changes Requested)`

What is already fixed:

- `tests/datahub/test_akshare_live.py` now converts known external environment failures into explicit `skipTest(...)` reasons.
- Default tests remain offline.
- Live-enabled smoke no longer fails with an uncategorized `ProxyError` in the reviewed environment.

Remaining blocker:

- `coordination/reports/TASK-012_REPORT.md` records the live-enabled command as `Ran 1 test`, `OK`, but review/integration observed `OK (skipped=1)`.
- The report does not include the actual skip reason text.

Integration recorded the observed skip reason in summary form:

- `live AKShare source unavailable in current environment ... ProxyError ... push2his.eastmoney.com ...`

The execution window must read:

- `AGENTS.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-012_DATAHUB_AKSHARE_LIVE_REPORT_CORRECTION.md`
- `coordination/reviews/TASK-012_REVIEW.md`
- `coordination/integrations/TASK-012_INTEGRATION.md`
- `coordination/reports/TASK-012_REPORT.md`

## Goal

Correct the TASK-012 execution report so it truthfully records the current live-enabled smoke result and skip reason.

This is a report-only cleanup handoff. Do not change adapter or test code unless the local report-only correction is impossible, which is not expected.

## Allowed Files

The execution window may modify only:

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
- `coordination/handoffs/**`
- `quant/**`
- `tests/**`
- `docs/**`

## Implementation Requirements

Update `coordination/reports/TASK-012_REPORT.md` to include the exact live-enabled result with enough evidence for review.

At minimum, the report must state:

- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest tests/datahub/test_akshare_live.py` or the exact live-enabled command actually run
- observed result: `Ran 1 test`, `OK (skipped=1)` if the current environment still skips
- the skip reason text, including that the live AKShare source is unavailable in the current environment and the relevant `ProxyError` / `push2his.eastmoney.com` detail when applicable
- the distinction between:
  - default live test skip because `QUANT_SYSTEM_LIVE_TESTS` is not set
  - live-enabled environment/source skip because public AKShare/Eastmoney access is unavailable

Do not claim live-enabled PASS unless the command actually fetches and validates a live record with no skip.

If the local run now succeeds instead of skipping, record the actual PASS result and say that review/integration previously observed `OK (skipped=1)` due to proxy/source unavailability.

## Testing Requirements

Because this handoff is report-only, code tests are not required unless the execution window chooses to re-run commands to capture current evidence.

Recommended evidence command:

`QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_live.py`

If run, record the observed result in `coordination/reports/TASK-012_REPORT.md`.

Do not modify test or adapter code in this handoff.

## Acceptance Criteria

The handoff is acceptable when:

- `coordination/reports/TASK-012_REPORT.md` clearly records live-enabled `OK (skipped=1)` and skip reason when the environment skips
- the report no longer states or implies that the live-enabled command passed if it actually skipped
- no files other than `coordination/reports/TASK-012_REPORT.md` are modified
- no future-phase modules are touched

## Report Path

`coordination/reports/TASK-012_REPORT.md`

## Review Path

`coordination/reviews/TASK-012_REVIEW.md`

## Integration Path

`coordination/integrations/TASK-012_INTEGRATION.md`

## Out of Scope

Everything except correcting TASK-012 report evidence is out of scope.
