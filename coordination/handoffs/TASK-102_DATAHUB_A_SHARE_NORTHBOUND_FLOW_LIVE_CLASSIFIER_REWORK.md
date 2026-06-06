# TASK-102 DataHub A-share Northbound-Flow Live Classifier Rework

## Role

5.3 Execution Window.

## Context

TASK-102 initial execution added a dedicated A-share northbound-flow contract/profile and reported live-enabled PASS evidence, but the Review Agent rejected closure because the new dedicated northbound live smoke can mask repository-side route/signature defects as environment `SKIP`.

Review finding to address:

- `tests/datahub/test_akshare_a_share_northbound_flow_live.py` classifies any exception message containing `eastmoney`, `stock_hsgt_individual_em`, or `em_hsgt` as environment-unavailable, then converts that classification into `SKIP`.
- This is too broad. AKShare route-signature/call-compatibility failures such as `unexpected keyword argument` for `stock_hsgt_individual_em` must fail, not skip.

Phase 2.5-P remains active. TASK-102 must not be closed, marked Done, or sent to Integration until a fresh Review Agent accepts the rework and explicitly allows Controller closure.

## Objective

Narrow the dedicated A-share northbound-flow live-environment classifier so only genuine network/proxy/DNS/TLS/upstream/source availability failures may skip, while route-signature, request/contract, schema, normalization, duplicate-conflict, and repository-side defects fail.

This is a focused rework of the Review finding only. Do not reopen broader northbound contract design unless the classifier fix exposes a directly related defect that must be fixed to keep tests truthful.

## Allowed Writes

Only:

- `tests/datahub/test_akshare_a_share_northbound_flow_live.py`
- `coordination/reports/TASK-102_REPORT.md`

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files except `coordination/reports/TASK-102_REPORT.md`
- `coordination/reviews/**`
- `coordination/integrations/**`
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

## Implementation Requirements

- Read `AGENTS.md` first, then this handoff.
- Keep the current dedicated northbound live smoke explicitly gated by `QUANT_SYSTEM_LIVE_TESTS=1` and skipped by default.
- Remove route-name-only skip behavior for `eastmoney`, `stock_hsgt_individual_em`, and `em_hsgt`.
- Ensure AKShare route-signature/call-compatibility defects fail, including messages such as:
  - `unexpected keyword argument`
  - `missing required positional argument`
  - `takes ... positional arguments`
  - `got multiple values for argument`
  - `TypeError` from route invocation or request construction
- Preserve skips only for narrowly identified environment or upstream/source availability cases such as network connectivity, proxy, DNS, TLS/SSL, timeout, connection reset/refused, HTTP upstream availability, empty/unavailable source windows, or explicit source unavailable responses.
- Add focused offline regression coverage inside the live test module, if practical, proving route-signature examples are not classified as environment skips while real network/upstream availability examples still are.
- Do not promote `a_share_northbound_flow`, alter source capabilities, alter schema fields, or change adapter normalization unless the classifier fix reveals an unavoidable directly related truthfulness defect.

## Tests

Required default/offline tests:

- `python3 -m unittest tests/datahub/test_akshare_a_share_northbound_flow_live.py`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_a_share_northbound_flow_live.py`

Required regression/compatibility tests:

- `python3 -m unittest tests/datahub/test_akshare_a_share_northbound_flow_adapter.py`
- `python3 -m unittest tests/datahub/test_source_capabilities.py`

Live smoke requirement:

- Run `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_a_share_northbound_flow_live.py`.
- Report PASS, SKIP, or FAIL truthfully.
- If the live-enabled smoke skips because of network, proxy, DNS, TLS, upstream, or public-source availability, diagnose and modify the allowed live test/report where feasible instead of only documenting the skip.
- If it fails because of route-signature/call-compatibility, schema, contract, normalization, or repository-side defects, keep it as FAIL and record evidence. Do not downgrade it to SKIP.

## Completion Report

Update `coordination/reports/TASK-102_REPORT.md` with:

- files changed
- tests run
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence after this rework
- explicit explanation of the narrowed classifier policy
- regression evidence that route-signature/call-compatibility defects no longer become `SKIP`
- confirmation that TASK-102 contract/source-capability truth was not broadened by this rework
- deviations from this handoff
- risks or follow-up tasks

## Completion Criteria

The rework is complete when:

- The Review Agent's classifier blocker is directly fixed.
- Default tests remain offline-safe.
- Dedicated northbound live smoke remains gated by `QUANT_SYSTEM_LIVE_TESTS=1`.
- Route-signature/call-compatibility defects on `stock_hsgt_individual_em` fail instead of skip.
- Real network/proxy/DNS/TLS/upstream/source availability issues may still skip with clear evidence.
- `coordination/reports/TASK-102_REPORT.md` truthfully records the rework and test evidence.
