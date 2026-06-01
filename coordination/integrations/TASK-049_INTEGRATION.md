# TASK-049 Integration (Live Route Rework)

## Task

- Task ID: `TASK-049`
- Name: DataHub AKShare A-share Major Activity Events Live Route Rework
- Original adapter handoff: `coordination/handoffs/TASK-049_DATAHUB_AKSHARE_A_SHARE_MAJOR_ACTIVITY_EVENTS_ADAPTER.md`
- Rework handoff: `coordination/handoffs/TASK-049_DATAHUB_AKSHARE_A_SHARE_MAJOR_ACTIVITY_EVENTS_LIVE_ROUTE_REWORK.md`
- Report: `coordination/reports/TASK-049_REPORT.md`
- Review: `coordination/reviews/TASK-049_REVIEW.md`

## Integration Result

- Status: `INTEGRATED / READY FOR CONTROLLER CLOSURE`
- Reviewed result: `ACCEPTED`
- Integration decision: accepted reviewed rework artifacts are integrated. The prior live skip gate is cleared by the rework evidence and integration spot-check: the live-enabled smoke now passes in the current environment.

## Inputs Checked

- `AGENTS.md`
- `coordination/CONTEXT_SNAPSHOT.md`
- `coordination/handoffs/TASK-049_DATAHUB_AKSHARE_A_SHARE_MAJOR_ACTIVITY_EVENTS_LIVE_ROUTE_REWORK.md`
- `coordination/reports/TASK-049_REPORT.md`
- `coordination/reviews/TASK-049_REVIEW.md`
- `git status --short`
- `git diff --stat`
- Focused current diff and implementation for `tests/datahub/test_akshare_a_share_major_activity_events_live.py`

`coordination/agent_runs/**` was not read; the specified report, review, status/stat, and focused code diff were sufficient for integration judgment.

## Files Integrated

Current rework artifacts:

- `tests/datahub/test_akshare_a_share_major_activity_events_live.py`
- `coordination/reports/TASK-049_REPORT.md`
- `coordination/reviews/TASK-049_REVIEW.md`
- `coordination/integrations/TASK-049_INTEGRATION.md`

Previously reviewed TASK-049 adapter/source-capability artifacts remain part of the task integration:

- `quant/datahub/adapters/akshare.py`
- `quant/datahub/adapters/__init__.py`
- `quant/datahub/__init__.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/source_catalog.py`
- `tests/datahub/test_akshare_a_share_major_activity_events_adapter.py`
- `tests/datahub/test_source_capabilities.py`
- `tests/datahub/test_source_catalog.py`

## Verification

Reviewed and accepted evidence:

- Rework changed live smoke behavior from first unavailable date causing immediate skip to bounded recent-date probing over the last 30 days.
- Default mode remains offline-safe and explicitly gated by `QUANT_SYSTEM_LIVE_TESTS=1`.
- New deterministic unit tests cover continuing after an unavailable date, returning the last unavailable error when all attempts are unavailable, and preserving hard failures for non-unavailable errors.
- Report records baseline live `SKIP` root cause, route/date diagnosis, repository fix, and post-rework live `PASS`.
- Review decision is `ACCEPTED` with no blocking findings.

Integration spot-checks run:

1. `python3 -m unittest tests/datahub/test_akshare_a_share_major_activity_events_adapter.py`
   - Result: `Ran 15 tests ... OK`

2. `python3 -m unittest -v tests/datahub/test_akshare_a_share_major_activity_events_live.py`
   - Result: `Ran 7 tests ... OK (skipped=1)`

3. `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_major_activity_events_live.py`
   - Result: `Ran 7 tests ... OK`

Full DataHub discovery was not rerun during integration; the execution report records `python3 -m unittest discover -s tests/datahub -p 'test_*.py'` passing with `Ran 759 tests ... OK (skipped=33)`.

## Conflict and Scope Check

- No integration conflicts were found in the reviewed code/test/report artifacts.
- Current rework code changes are limited to `tests/datahub/test_akshare_a_share_major_activity_events_live.py`, plus report/review/integration artifacts.
- Changes remain within Phase 2.5 DataHub source-capability scope.
- No future-phase implementation was introduced in `quant/strategies/`, `quant/backtest/`, `quant/scanner/`, `quant/portfolio/`, `quant/notification/`, `quant/ai/`, or `quant/ui/`.
- No controller-only project state files were modified by this integration pass.
- Default tests remain offline-safe; live source access remains explicitly environment-gated.

## State-Update Recommendations for Controller

- Close TASK-049 as integrated after accepted rework review.
- Record the live-enabled TASK-049 status as `PASS` after bounded recent-date probing.
- Preserve the capability truth as partial: public AKShare A-share bounded block-trade detail coverage for `DatasetName.MAJOR_ACTIVITY_EVENTS`, with public upstream availability and breadth/history limitations still noted.
- Continue Phase 2.5 sequencing through `coordination/PHASE_GATE.md` before dispatching the next executable task.
