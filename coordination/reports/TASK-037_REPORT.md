# TASK-037 Execution Report

## Task
- TASK ID: `TASK-037`
- Handoff: `coordination/handoffs/TASK-037_DATAHUB_HKEX_HK_TRADING_CALENDAR_ADAPTER.md`
- Role: 5.3 Execution Window

## Files Changed
- `quant/datahub/adapters/hkex.py`
  - Added `HkexHKTradingCalendarAdapter` for `DatasetName.TRADING_CALENDAR` (`market=HK`, `source=hkex_disclosure_and_calendar_family`).
  - Added no-credential live route to HKEX iCal feed (`/News/HKEX-Calendar/Subscribe-Calendar?sc_lang=en`).
  - Added normalization for ICS/DataFrame-like/list[Mapping]/list[date-like] payloads.
  - Added deterministic sorting, deduplication, date filtering, previous/next trade-date derivation, schema metadata stamping, and explicit error handling.
  - Added ICS unfolding/event parsing and HK holiday / half-day extraction logic for session typing.
- `quant/datahub/adapters/__init__.py`
  - Exported `HkexHKTradingCalendarAdapter`.
- `quant/datahub/__init__.py`
  - Exported `HkexHKTradingCalendarAdapter`.
- `tests/datahub/test_hkex_hk_trading_calendar_adapter.py`
  - Added deterministic offline adapter tests covering contract compliance, normalization, filtering, sorting/deduplication, previous/next linkage, and failure boundaries.
- `tests/datahub/test_hkex_hk_trading_calendar_live.py`
  - Added default-skipped live smoke (`QUANT_SYSTEM_LIVE_TESTS=1` gated) with network-environment skip classifier and schema validation assertions.
- `coordination/reports/TASK-037_REPORT.md`

## Tests Run
- `python3 -m unittest tests/datahub/test_hkex_hk_trading_calendar_adapter.py`
  - PASS (`Ran 15 tests`).
- `python3 -m unittest -v tests/datahub/test_hkex_hk_trading_calendar_live.py`
  - PASS with default skip (`Ran 3 tests`, `skipped=1`, live test skipped by env gate).
- `python3 -m unittest tests/datahub/test_akshare_calendar_adapter.py`
  - PASS (`Ran 11 tests`).
- `python3 -m unittest tests/datahub/test_hkex_company_announcements_adapter.py`
  - PASS (`Ran 19 tests`).
- `python3 -m unittest tests/datahub/test_source.py`
  - PASS (`Ran 20 tests`).
- `python3 -m unittest discover -s tests/datahub -p 'test_*.py'`
  - PASS (`Ran 598 tests`, `skipped=24`).
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_hkex_hk_trading_calendar_live.py`
  - PASS (`Ran 3 tests`, live smoke PASS).

## Default Network Behavior
- Default test path remains offline-safe.
- Offline adapter tests inject fixture payloads and do not require network.
- Live smoke test is explicitly gated by `QUANT_SYSTEM_LIVE_TESTS=1` and skipped by default.

## Live-Enabled Result (Mandatory)
- Result: **PASS**
- Command: `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_hkex_hk_trading_calendar_live.py`
- Evidence:
  - `test_live_hkex_hk_trading_calendar_smoke ... ok`
  - Suite summary: `Ran 3 tests ... OK`

## Deviations From Handoff
- None.

## Risks / Follow-up
- Current implementation is intentionally narrow and market-calendar-focused.
- Session typing for half-day relies on HKEX iCal event summary token matching (`"half-day trading day"`); if HKEX wording changes, affected records will fall back to `session_type="full"` while remaining schema-valid.
