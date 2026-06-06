# TASK-108 Report

## files changed
- `quant/datahub/adapters/akshare.py`
- `tests/datahub/test_akshare_a_share_company_announcements_adapter.py`
- `tests/datahub/test_akshare_a_share_company_announcements_live.py`
- `coordination/reports/TASK-108_REPORT.md`

## implementation summary
- Tightened `AkshareAShareCompanyAnnouncementsAdapter` fallback truth: if the primary route is unavailable and any required fallback day is unavailable, the adapter now raises for the whole requested window instead of silently continuing with partial per-day history.
- Added offline regression coverage for:
  - fallback success across a multi-day window with deterministic date filtering and sorting;
  - fallback partial-day unavailability causing whole-window failure;
  - existing live-unavailable classifier behavior remaining strict.
- Updated the gated live smoke to assert publish-date window truth, not only schema/source/symbol provenance.

## tests run
- `python3 -m unittest tests/datahub/test_akshare_a_share_company_announcements_adapter.py` -> PASS
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_company_announcements_live.py` -> PASS (`live` smoke skipped by default)
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_company_announcements_live.py` -> PASS

## default network behavior
- Default tests remain offline-safe.
- Adapter tests use injected fetch callables / local fixtures only.
- `tests/datahub/test_akshare_a_share_company_announcements_live.py` still skips the live smoke unless `QUANT_SYSTEM_LIVE_TESTS=1`.

## live-enabled PASS/SKIP/FAIL result and root-cause evidence
- Result: PASS
- Evidence:
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_company_announcements_live.py` finished `OK` on June 6, 2026.
  - The live request window was `2025-12-09` through `2026-06-06`.
  - A direct post-test sample fetch for `600000.SH` returned `record_count=47`, `min_publish_date=2025-12-16`, `max_publish_date=2026-06-05`, `source_route=stock_individual_notice_report`.

## date-window truth
- The live smoke now derives `publish_dates` from normalized records and asserts every returned publish date is within the exact requested bounded window.
- The same live smoke also asserts at least one returned record exists inside that requested window, so the test no longer treats a bounded request as proven without window membership.

## fallback date-route behavior
- The fallback route no longer treats partial per-day availability as a successful full-window result.
- If any required fallback day is unavailable after the primary route is unavailable, the adapter raises `fallback window unavailable` with `route`, `query_day`, and `requested_window` evidence.
- Successful fallback requests still return deterministic, date-filtered, schema-valid records.

## capability truth changed
- `a_share_company_announcements` remains `partial`.
- No capability promotion or wording change was made in this rework.

## deviations
- None.

## risks/follow-up
- The fallback route is now truth-preserving but stricter: transient unavailability on one required fallback day makes the full requested window unavailable.
- Public second-route redundancy, broader long-history continuity, and full announcement-category breadth remain unproven.
