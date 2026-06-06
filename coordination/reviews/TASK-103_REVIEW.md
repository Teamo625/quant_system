# TASK-103 Review

- Decision: REWORK REQUIRED

- Findings
  1. High - `tests/datahub/test_akshare_a_share_turnover_liquidity_live.py:31-80` treats any exception chain mentioning `stock_zh_a_hist` as environment-unavailable and `tests/datahub/test_akshare_a_share_turnover_liquidity_live.py:119-128` converts that to `skipTest`. This violates the handoff rule that route-name/signature compatibility defects must fail rather than skip. Independent repro in review: wrapping `TypeError("stock_zh_a_hist() got an unexpected keyword argument 'foo'")` inside the live-test exception chain returns `True`, so a repository-side call/signature defect would be downgraded to `SKIP`. The northbound classifier already shows the expected pattern in `tests/datahub/test_akshare_a_share_northbound_flow_live.py:17-30` and `tests/datahub/test_akshare_a_share_northbound_flow_live.py:81-87,124-132`. Because of this, `coordination/reports/TASK-103_REPORT.md:45-50` is not yet accurate when it says the live classifier only skips network/upstream conditions.

- Notes
  - No phase/scope violation found. Changes stay within `quant/datahub/` and `tests/datahub/`.
  - Independent offline/default verification passed:
    - `python3 -m unittest tests/datahub/test_datasets.py`
    - `python3 -m unittest tests/datahub/test_source_catalog.py`
    - `python3 -m unittest tests/datahub/test_source_capabilities.py`
    - `python3 -m unittest tests/datahub/test_akshare_adapter.py`
    - `python3 -m unittest tests/datahub/test_akshare_a_share_capital_flow_snapshot_adapter.py`
    - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_capital_flow_snapshot_live.py`
    - `python3 -m unittest tests/datahub/test_akshare_a_share_turnover_liquidity_adapter.py`
    - `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_turnover_liquidity_live.py`
  - Independent live-enabled rerun still produced truthful upstream-unavailable `SKIP` in the current environment:
    - `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_turnover_liquidity_live.py`
    - observed skip evidence: `ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))`

## Closure Readiness

- Controller closure allowed: No.
- Default tests offline-safe: Yes.
- Live-enabled result: SKIP.
- Rework required after live result: Yes. The current skip classifier can hide repository-side route/signature failures, so the live gate is not reliable enough for closure yet.
- Phase/scope/contract/test blockers: Yes. Blocking item is the turnover/liquidity live-classifier/test-path defect above and the corresponding inaccurate report claim. No separate phase-scope blocker found.

- Required follow-up
  1. Narrow `tests/datahub/test_akshare_a_share_turnover_liquidity_live.py` so `TypeError` and route-signature/call-compatibility failures remain FAIL, matching the accepted northbound/minute-bars policy.
  2. Add a regression test that proves a `stock_zh_a_hist()` signature error is not classified as environment-unavailable.
  3. Update `coordination/reports/TASK-103_REPORT.md` after the classifier behavior is corrected.
