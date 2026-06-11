# TASK-128 Review

## Findings

- `tests/datahub/test_akshare_sector_live.py:120` still catches any `ValueError` from the live sector daily-bar smoke and downgrades it into `empty_results`/`skip`. This handoff materially changed the sector daily-bar adapter, and the handoff explicitly requires repository-side schema/contract/normalization/date-window defects to fail rather than skip. As written, adapter-side regressions such as duplicate-conflict handling, normalization failures, or window-filter defects can still be masked as environment unavailability, so the live PASS evidence is not closure-grade.

## Decision

- Rejected pending a focused live-smoke classifier rework for `sector_daily_bars`.
- Independent verification run by Review:
  - default/offline suites passed
  - default live-gated suites skipped as expected without `QUANT_SYSTEM_LIVE_TESTS=1`
  - live-enabled sector daily-bar and sector-membership suites both passed in the current environment

## Closure Status

- decision: rejected_or_blocked
- controller_closure_allowed: no
- default_tests_offline_safe: yes
- live_enabled_result: PASS
- rework_required: yes

## Closure Readiness

- Controller closure: no.
- Default tests are offline-safe: yes.
- Live-enabled result: PASS, but the changed `sector_daily_bars` live smoke still masks repository-side `ValueError` defects as skip and needs rework.
- Blocking items: no phase/scope violation found; the blocker is live-smoke classifier truthfulness in `tests/datahub/test_akshare_sector_live.py`.
