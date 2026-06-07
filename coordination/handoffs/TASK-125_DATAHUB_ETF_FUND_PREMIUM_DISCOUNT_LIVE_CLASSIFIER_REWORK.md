# TASK-125 DataHub ETF/Fund Premium-Discount Live Classifier Rework

## Role

5.3 Execution Window.

## Phase

Phase 2.5-P DataHub Personal Trading Perfection Re-Review.

## Context

The initial TASK-125 execution added request-scoped historical ETF/fund premium-discount rows by combining historical market-price routes with NAV history. Review rejected closure because the new historical-route live classifier is too broad.

Review finding:

- `_is_fund_premium_discount_route_unavailable()` treats exception messages containing `fund_etf_hist_em`, `fund_lof_hist_em`, or `fund_etf_hist_sina` as environment/source unavailability.
- This incorrectly downgrades repository-side route-signature or call-compatibility defects, such as `TypeError("fund_etf_hist_em() got an unexpected keyword argument 'adjust'")`, into live-environment `SKIP`.
- The original handoff explicitly required route-signature and call-compatibility defects to fail rather than skip.

This rework must fix only the Review finding. Do not redo the full TASK-125 implementation or broaden scope.

## Objective

Narrow ETF/fund premium-discount live/source unavailability classification so historical route function-name tokens alone do not classify repository-side defects as environment/source unavailability, and add focused regression coverage proving historical route signature/call-compatibility failures remain hard failures.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-125_DATAHUB_ETF_FUND_PREMIUM_DISCOUNT_LIVE_CLASSIFIER_REWORK.md`
- `coordination/handoffs/TASK-125_DATAHUB_ETF_FUND_PREMIUM_DISCOUNT_BREADTH_HISTORY_HARDENING.md`
- `coordination/reports/TASK-125_REPORT.md`
- `coordination/reviews/TASK-125_REVIEW.md`
- `quant/datahub/adapters/akshare.py`
- `tests/datahub/test_akshare_fund_premium_discount_live.py`
- `tests/datahub/test_akshare_fund_premium_discount_adapter.py` only if needed for the focused regression

## Allowed Writes

Only:

- `quant/datahub/adapters/akshare.py`
- `tests/datahub/test_akshare_fund_premium_discount_live.py`
- `tests/datahub/test_akshare_fund_premium_discount_adapter.py` only if the focused classifier regression is better placed there
- `coordination/reports/TASK-125_REPORT.md`

Do not modify source capability/catalog wording unless the classifier fix reveals a direct inconsistency that must be corrected to satisfy the Review finding.

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files other than `coordination/reports/TASK-125_REPORT.md`
- `coordination/reviews/**`
- `coordination/integrations/**`
- unrelated DataHub adapters or tests
- `quant/features/**`
- `quant/scanner/**`
- `quant/strategies/**`
- `quant/backtest/**`
- `quant/portfolio/**`
- `quant/notification/**`
- `quant/ai/**`
- `quant/ui/**`

Do not use credentials, tokens, cookies, browser session state, private account data, paid sources, or hidden default live network behavior.

## Implementation Requirements

- Keep existing accepted TASK-125 ETF/fund premium-discount behavior intact.
- Narrow `_is_fund_premium_discount_route_unavailable()` so route/function-name tokens such as `fund_etf_hist_em`, `fund_lof_hist_em`, and `fund_etf_hist_sina` are not sufficient by themselves to classify an exception as environment/source unavailability.
- Ensure route-signature, unexpected keyword, missing required argument, call-compatibility, schema, payload, normalization, duplicate-conflict, and date-window defects remain hard failures.
- Preserve genuine network/proxy/DNS/TLS/upstream/source-unavailability skips where classifier evidence is specific enough.
- Add regression coverage for at least one historical-route call-compatibility failure, including the Review reproduction shape: `TypeError("fund_etf_hist_em() got an unexpected keyword argument 'adjust'")`.
- Keep default tests offline-safe and keep live tests gated behind `QUANT_SYSTEM_LIVE_TESTS=1`.

## Tests

Required offline/default tests:

- `python3 -m unittest tests.datahub.test_akshare_fund_premium_discount_adapter`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests.datahub.test_akshare_fund_premium_discount_live`

Also run any focused test file changed by this rework.

Live smoke requirement:

- Because this is a classifier rework for a real-source path, run `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests.datahub.test_akshare_fund_premium_discount_live` after the classifier fix when feasible.
- Report PASS, SKIP, or FAIL truthfully with root-cause evidence.
- If the live smoke skips because of network, proxy, DNS, TLS, upstream, or public-source availability, diagnose and fix repository code/tests where feasible instead of only documenting the skip.

## Completion Report

Update `coordination/reports/TASK-125_REPORT.md` with a rework section including:

- files changed
- classifier fix summary
- regression coverage added
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence
- confirmation that route-signature/call-compatibility defects now fail rather than skip
- deviations from this rework handoff
- risks or follow-up tasks

## Completion Criteria

The rework is complete when:

- the Review finding is directly fixed
- historical premium-discount route function-name tokens alone no longer trigger environment/source-unavailability classification
- focused regression tests prove route-signature/call-compatibility defects remain hard failures
- default tests remain offline-safe
- gated live evidence is recorded truthfully
- no inactive downstream module behavior is introduced
