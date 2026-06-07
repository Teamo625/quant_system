# TASK-125 Review

## Findings

1. Blocking: the historical-route live classifier now treats any exception message containing `fund_etf_hist_em`, `fund_lof_hist_em`, or `fund_etf_hist_sina` as environment unavailability, even when the failure is a repository-side route-signature/call-compatibility defect. In [quant/datahub/adapters/akshare.py](/Users/chenziheng/Documents/量化分析代码/quant_system/quant/datahub/adapters/akshare.py:25527), `_fetch_historical_price_rows()` catches primary/fallback exceptions and defers to `_is_fund_premium_discount_route_unavailable()`. In [quant/datahub/adapters/akshare.py](/Users/chenziheng/Documents/量化分析代码/quant_system/quant/datahub/adapters/akshare.py:26617), that classifier now returns `True` for any message containing those route-name tokens. Minimal reproduction in review: `TypeError("fund_etf_hist_em() got an unexpected keyword argument 'adjust'")` is classified as unavailable. This violates the handoff rule that route-signature/call-compatibility defects must fail, not skip, and it leaves the live-enabled truthfulness regression untested because [tests/datahub/test_akshare_fund_premium_discount_live.py](/Users/chenziheng/Documents/量化分析代码/quant_system/tests/datahub/test_akshare_fund_premium_discount_live.py:16) only covers generic contract and network cases.

## Decision

Rework required. Do not send to Controller closure yet.

## Closure Readiness

- Controller closure allowed: No.
- Default tests offline-safe: Yes. Re-ran `tests.datahub.test_source_capabilities`, `tests.datahub.test_source_catalog`, `tests.datahub.test_akshare_fund_premium_discount_adapter`, and live test with `QUANT_SYSTEM_LIVE_TESTS` unset; all passed and the live smoke remained skipped by default.
- Live-enabled result: PASS as recorded in `coordination/reports/TASK-125_REPORT.md`, but rework is still required because the new classifier can incorrectly downgrade repository-side historical-route compatibility defects into environment `SKIP`.
- Phase/scope/contract/test blockers: No phase-boundary violation found. Blocking issue is live-classifier truthfulness plus missing regression coverage for historical route `TypeError` / call-compatibility failures.

## Required Follow-up

- Narrow `_is_fund_premium_discount_route_unavailable()` so bare route/function-name tokens do not classify non-network exceptions as environment unavailability.
- Add regression coverage proving historical-route signature/call-compatibility failures remain hard failures rather than `SKIP`.
