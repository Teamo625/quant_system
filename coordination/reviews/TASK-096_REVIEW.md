# TASK-096 Review

## Findings

1. `quant/datahub/adapters/akshare.py:321` and `quant/datahub/adapters/akshare.py:882` add a fixed `10`-calendar-day guard for public `1`-minute history, but the execution report itself records that upstream `stock_zh_a_hist_min_em(period='1')` is retained by `ndays=5` trading days, not calendar days. Around long exchange closures this can reject still-reachable data before any fetch attempt, so the adapter now hard-codes a narrower contract than the inspected public route actually guarantees. `tests/datahub/test_akshare_a_share_minute_bars_adapter.py:265` only covers a clearly stale window and does not protect against this holiday-span regression. Rework this to use trading-day-aware retention logic or another source-backed rule.

## Decision

Decision: REWORK REQUIRED.

Independent verification:
- `python3 -m unittest tests/datahub/test_akshare_a_share_minute_bars_adapter.py` -> PASS
- `python3 -m unittest tests/datahub/test_source_capabilities.py` -> PASS
- `python3 -m unittest -v tests/datahub/test_akshare_a_share_minute_bars_live.py` -> OK (`skipped=1` in the current environment)
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_minute_bars_live.py` -> OK (`skipped=1`)

## Closure Readiness

- Controller closure allowed: No
- Default tests offline-safe: Yes
- Live-enabled result: SKIP
- SKIP/FAIL rework required: Yes
- Phase/scope/contract/test blockers: Yes

Reason:
- The `1`-minute retention guard is not aligned with the reported upstream trading-day retention behavior.
- Live-enabled smoke still skipped on Eastmoney proxy/connectivity failure, so this task is not closure-ready under the Phase 2.5-P live-smoke rules.

## Required Follow-up

- Replace the fixed `10`-calendar-day `1`-minute guard with source-backed trading-day-aware retention handling, then add offline regression coverage for holiday/long-closure spans.
- Dispatch the required live-network rework path for the Eastmoney connectivity skip and rerun the gated live smoke from a reachable environment before controller closure.
