# TASK-108 Review

## Findings

1. Blocking: the live smoke does not assert date-window truth, so it does not satisfy the handoff's mandatory live requirement for publish-time/window behavior. The test builds a bounded request but only checks schema, source, market, route, symbol format, and timestamp format, without verifying the returned record date falls inside the requested window. See [tests/datahub/test_akshare_a_share_company_announcements_live.py](/Users/chenziheng/Documents/量化分析代码/quant_system/tests/datahub/test_akshare_a_share_company_announcements_live.py:135) and [tests/datahub/test_akshare_a_share_company_announcements_live.py](/Users/chenziheng/Documents/量化分析代码/quant_system/tests/datahub/test_akshare_a_share_company_announcements_live.py:160).

2. Blocking: the fallback date-route path can silently return partial history for a requested window. When the primary route is unavailable, per-day fallback failures classified as upstream/network unavailability are skipped with `continue`, and the adapter only raises if every fallback day fails. That means a multi-day request can succeed with missing days while the implementation and report claim bounded date-window hardening. See [quant/datahub/adapters/akshare.py](/Users/chenziheng/Documents/量化分析代码/quant_system/quant/datahub/adapters/akshare.py:13463).

## Decision

Rework required before Controller closure.

## Closure Readiness

- Controller closure allowed: No
- Default tests offline-safe: Yes
- Live-enabled result: PASS
- Live-enabled rework required: Yes
- Phase/scope/contract/test blockers: Yes

Reason:
- No phase-scope violation found; changes stay within `quant/datahub/` and `tests/datahub/`.
- Independent verification passed for:
  - `python3 -m unittest tests/datahub/test_akshare_a_share_company_announcements_adapter.py`
  - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_company_announcements_live.py`
  - `python3 -m unittest tests/datahub/test_source_capabilities.py`
  - `python3 -m unittest tests/datahub/test_datasets.py`
  - `python3 -m unittest tests/datahub/test_hkex_company_announcements_adapter.py`
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_company_announcements_live.py`
- Despite live PASS, the task is not closure-ready because the mandatory live date-window assertion is missing and fallback history truth can still be overstated under partial per-day upstream failures.

## Required Follow-up

- Add live assertions that validate returned announcement dates are within the requested bounded window.
- Rework fallback handling so partial per-day upstream unavailability is surfaced as failure/unavailability for the requested window, or narrow the claimed fallback/date-window truth and add regression coverage proving that behavior explicitly.
