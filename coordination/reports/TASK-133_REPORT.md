# TASK-133 Report

- files changed
  - `quant/datahub/adapters/akshare.py`
  - `quant/datahub/source_capabilities.py`
  - `quant/datahub/source_catalog.py`
  - `tests/datahub/test_akshare_a_share_major_activity_events_adapter.py`
  - `tests/datahub/test_akshare_a_share_major_activity_events_live.py`
  - `tests/datahub/test_source_capabilities.py`
  - `tests/datahub/test_source_catalog.py`

- implementation summary by capability
  - `a_share_major_activity_events`
    - Expanded `AkshareAShareMajorActivityEventsAdapter` beyond block-trade detail/summary to also normalize symbol-bounded insider holding-change rows from `stock_share_hold_change_sse`, `stock_share_hold_change_szse`, and `stock_share_hold_change_bse`.
    - Added insider event normalization for `event_type="insider_holding_change"` with signed direction, absolute volume, optional value from average price, summary/source_ts handling, and route-specific event ids.
    - Extended major-activity live/unavailable classifiers to recognize SSE/SZSE/BSE route/network failures.
    - Tightened capability/catalog truth to state that current public proof now includes exchange-specific insider holding-change routes while remaining `partial`.
  - `a_share_financial_indicators`
    - No adapter or contract change.
    - Preserved accepted TASK-107 behavior and wording.
  - `a_share_company_announcements`
    - No adapter or contract change.
    - Preserved accepted TASK-108 behavior and wording.

- tests run
  - `python3 -m unittest tests.datahub.test_akshare_a_share_major_activity_events_adapter`
  - `python3 -m unittest tests.datahub.test_akshare_a_share_major_activity_events_live`
  - `python3 -m unittest tests.datahub.test_source_capabilities tests.datahub.test_source_catalog`
  - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest tests.datahub.test_akshare_a_share_major_activity_events_live -v`

- default network behavior
  - Default unit tests remain offline-safe.
  - Live network access is still gated behind `QUANT_SYSTEM_LIVE_TESTS=1`.
  - The new insider-holding-change path is only exercised in offline fixtures by default; no hidden live call was added to default tests.

- live-enabled PASS/SKIP/FAIL result and root-cause evidence
  - PASS: `a_share_major_activity_events` existing block-trade path.
    - Evidence: recent live bounded sample succeeded for `2026-06-09..2026-06-11` with `record_count=576` and routes `stock_dzjy_mrmx`, `stock_dzjy_mrtj`; sample first record was `000601.SZ` block-trade data from `stock_dzjy_mrmx`.
    - Matching test: `test_live_akshare_a_share_major_activity_events_smoke`.
  - PASS: `a_share_major_activity_events` new insider-holding-change path.
    - Evidence: live symbol-bounded sample for `symbols=('001308.SZ',)` and `2024-09-01..2024-09-30` returned `record_count=4`, all `event_type="insider_holding_change"`, route `stock_share_hold_change_szse`; sample record `event_date=2024-09-02`, `participant=凌斌`, `direction=buy`.
    - Matching test: `test_live_akshare_a_share_insider_holding_change_smoke`.
  - No new live-routed code path was changed for `a_share_financial_indicators` or `a_share_company_announcements`.

- deviations
  - None.

- risks/follow-up
  - `a_share_major_activity_events` should remain `partial`; this task adds insider holding-change breadth but does not prove a second no-credential source family or full long-history continuity across all activity taxonomies.
  - Insider holding-change support is currently bounded and symbol-driven; no unbounded full-market insider event collection path was added.
  - TASK-133 did not expand `a_share_financial_indicators` or `a_share_company_announcements`; those capabilities still need future re-review work if stronger redundancy/history proof is required.
