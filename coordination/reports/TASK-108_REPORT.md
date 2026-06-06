# TASK-108 Report

## files changed
- `quant/datahub/adapters/akshare.py`
- `quant/datahub/datasets.py`
- `quant/datahub/source_capabilities.py`
- `tests/datahub/test_akshare_a_share_company_announcements_adapter.py`
- `tests/datahub/test_akshare_a_share_company_announcements_live.py`
- `tests/datahub/test_datasets.py`
- `tests/datahub/test_source_capabilities.py`
- `coordination/reports/TASK-108_REPORT.md`

## implementation summary
- Hardened `AkshareAShareCompanyAnnouncementsAdapter` from one-symbol fetches to caller-provided bounded multi-symbol requests.
- Added explicit request guardrail `max_symbols_per_request` and kept bounded date-window enforcement via `max_route_days`.
- Added optional `source_route` truth to `DatasetName.COMPANY_ANNOUNCEMENTS` and emit route-backed values from A-share normalization:
  - `stock_individual_notice_report`
  - `stock_notice_report`
- Preserved hard-failure behavior for signature/payload/schema/normalization defects.
- Tightened live-unavailable classification so provider/route tokens alone no longer downgrade repository-side defects into environment `SKIP`.
- Kept `a_share_company_announcements` capability conservative at `partial` while updating wording to reflect bounded multi-symbol/date-window coverage plus remaining gaps.

## tests run
- `python3 -m unittest tests/datahub/test_akshare_a_share_company_announcements_adapter.py` -> PASS
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_company_announcements_live.py` -> PASS (`live` smoke skipped by default)
- `python3 -m unittest tests/datahub/test_source_capabilities.py` -> PASS
- `python3 -m unittest tests/datahub/test_datasets.py` -> PASS
- `python3 -m unittest tests/datahub/test_hkex_company_announcements_adapter.py` -> PASS
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_company_announcements_live.py` -> PASS

## default network behavior
- Default tests remain offline-safe.
- Adapter tests use injected fetch callables / local fixtures only.
- `tests/datahub/test_akshare_a_share_company_announcements_live.py` still skips the live smoke unless `QUANT_SYSTEM_LIVE_TESTS=1`.
- Shared contract regression coverage for HKEX remained offline-only.

## live-enabled PASS/SKIP/FAIL result and root-cause evidence
- Result: PASS
- Evidence:
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_company_announcements_live.py` finished `OK`.
  - Direct post-test sample fetch for `600000.SH`, `start_date=today-179d`, `end_date=today` returned `record_count=47`.
  - First live normalized record observed:
    - `symbol=600000.SH`
    - `market=A_SHARE`
    - `source=akshare_cn_hk_public_family`
    - `source_route=stock_individual_notice_report`
    - `publish_time=2025-12-16T00:00:00`
  - Live assertions validated `DatasetRegistry` schema compatibility, canonical A-share symbol format, `publish_time`, `market`, `source`, and `source_route`.

## capability truth changed
- `a_share_company_announcements` remains `partial`.
- Status was not promoted to `covered`.

## source route coverage and known limitations
- Proven in this task:
  - caller-provided bounded multi-symbol requests
  - bounded date-window filtering
  - explicit `source_route` provenance for primary and fallback AKShare routes
  - route-aware classifier truthfulness
- Still not proven:
  - full announcement category breadth
  - broader long-history continuity
  - public second-route redundancy beyond the currently bounded AKShare path
  - full-market / full-history collection

## deviations
- None.
- Extra validation run: `tests/datahub/test_hkex_company_announcements_adapter.py` because the shared `COMPANY_ANNOUNCEMENTS` contract gained a new optional field.

## risks/follow-up
- Fallback route remains date-based and filtered after fetch; it is bounded but not a full-history backfill mechanism.
- Distinct route provenance is now explicit, but cross-route redundancy reconciliation is still not proven enough to promote the capability.
- If AKShare changes route argument names or payload columns again, the adapter will fail hard by design rather than silently downgrade to environment `SKIP`.
