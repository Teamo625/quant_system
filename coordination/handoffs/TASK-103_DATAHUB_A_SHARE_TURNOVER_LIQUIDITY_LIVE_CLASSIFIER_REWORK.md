# TASK-103 DataHub A-share Turnover/Liquidity Live Classifier Rework

## Role

5.3 Execution Window.

## Context

TASK-103 initial execution added a dedicated A-share turnover/liquidity contract/profile and reported a live-enabled `SKIP` caused by upstream/public-route unavailability from `stock_zh_a_hist`.

Review rejected Controller closure because the dedicated turnover/liquidity live smoke can mask repository-side route/signature defects as environment `SKIP`.

Review finding to address:

- `tests/datahub/test_akshare_a_share_turnover_liquidity_live.py` treats any exception chain mentioning `stock_zh_a_hist` as environment-unavailable and converts that classification to `skipTest`.
- This is too broad. AKShare route-signature/call-compatibility failures such as `TypeError("stock_zh_a_hist() got an unexpected keyword argument 'foo'")` must fail, not skip.
- `coordination/reports/TASK-103_REPORT.md` is not yet accurate where it says the classifier keeps contract failures non-skip.

Phase 2.5-P remains active. TASK-103 must not be closed, marked Done, or sent to Integration until a fresh Review Agent accepts this rework and explicitly allows Controller closure.

## Objective

Narrow the dedicated A-share turnover/liquidity live-environment classifier so only genuine network/proxy/DNS/TLS/upstream/source availability failures may skip, while route-signature, request/contract, schema, normalization, duplicate-conflict, and repository-side defects fail.

This is a focused rework of the Review finding only. Do not reopen broader turnover/liquidity contract design unless the classifier fix exposes a directly related defect that must be fixed to keep tests truthful.

## Allowed Writes

Only:

- `tests/datahub/test_akshare_a_share_turnover_liquidity_live.py`
- `coordination/reports/TASK-103_REPORT.md`

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files except `coordination/reports/TASK-103_REPORT.md`
- `coordination/reviews/**`
- `coordination/integrations/**`
- `coordination/agent_runs/**`
- `quant/datahub/datasets.py`
- `quant/datahub/source_catalog.py`
- `quant/datahub/source_capabilities.py`
- `quant/datahub/adapters/akshare.py`
- unrelated DataHub adapters or tests
- `quant/features/`
- `quant/scanner/`
- `quant/strategies/`
- `quant/backtest/`
- `quant/portfolio/`
- `quant/notification/`
- `quant/ai/`
- `quant/ui/`

Do not use credentials, cookies, tokens, browser session state, paid APIs, private account data, or unbounded crawling.

Do not run `git add`, `git commit`, `git reset`, `git checkout`, or other git state-changing commands.

## Implementation Requirements

- Read `AGENTS.md` first, then this handoff.
- Keep the turnover/liquidity live smoke explicitly gated by `QUANT_SYSTEM_LIVE_TESTS=1` and skipped by default.
- Remove route-name-only skip behavior for `stock_zh_a_hist`.
- Ensure AKShare route-signature/call-compatibility defects fail, including messages such as:
  - `unexpected keyword argument`
  - `missing required positional argument`
  - `takes ... positional arguments`
  - `got multiple values for argument`
  - `TypeError` from route invocation or request construction
- Preserve skips only for narrowly identified environment or upstream/source availability cases such as network connectivity, proxy, DNS, TLS/SSL, timeout, connection reset/refused, HTTP upstream availability, empty/unavailable source windows, or explicit source unavailable responses.
- Add focused offline regression coverage inside the live test module proving `stock_zh_a_hist()` signature errors are not classified as environment skips.
- Keep or add coverage proving clear network/upstream availability examples still classify as unavailable.
- Do not promote `a_share_turnover_liquidity`, alter source capabilities, alter schema fields, or change adapter normalization unless the classifier fix reveals an unavoidable directly related truthfulness defect.

## Tests

Required default/offline tests:

- `python3 -m unittest tests/datahub/test_akshare_a_share_turnover_liquidity_live.py`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_turnover_liquidity_live.py`

Required regression/compatibility tests:

- `python3 -m unittest tests/datahub/test_akshare_a_share_turnover_liquidity_adapter.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`

Live smoke requirement:

- Run `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_turnover_liquidity_live.py`.
- Report PASS, SKIP, or FAIL truthfully.
- If the live-enabled smoke skips because of network, proxy, DNS, TLS, upstream, or public-source availability, diagnose and modify the allowed live test/report where feasible instead of only documenting the skip.
- If it fails because of route-signature/call-compatibility, schema, contract, normalization, or repository-side defects, keep it as FAIL and record evidence. Do not downgrade it to SKIP.

## Completion Report

Update `coordination/reports/TASK-103_REPORT.md` with:

- files changed in the rework
- classifier behavior before and after
- regression evidence that `stock_zh_a_hist` route-signature/call-compatibility defects no longer become `SKIP`
- tests run
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence after this rework
- confirmation that TASK-103 contract/source-capability truth was not broadened by this rework
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

The rework is complete when:

- The Review Agent's classifier blocker is directly fixed.
- Default tests remain offline-safe.
- Dedicated turnover/liquidity live smoke remains gated by `QUANT_SYSTEM_LIVE_TESTS=1`.
- Route-signature/call-compatibility defects on `stock_zh_a_hist` fail instead of skip.
- Real network/proxy/DNS/TLS/upstream/source availability issues may still skip with clear evidence.
- `coordination/reports/TASK-103_REPORT.md` truthfully records the rework and test evidence.
- No inactive downstream module behavior is introduced.
