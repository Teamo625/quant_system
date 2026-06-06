# TASK-117 DataHub Hong Kong Financial Live Classifier Rework

## Role

5.3 Execution Window.

## Context

TASK-117 initial execution strengthened Hong Kong `DatasetName.FINANCIAL_STATEMENTS` / `DatasetName.FINANCIAL_INDICATORS` source truth and reported live-enabled PASS evidence. Review rejected controller closure because the HK financial live-unavailability classifiers still treat route-name-bearing repository defects as environment `SKIP`.

Blocking review finding:

- `tests/datahub/test_akshare_hk_financial_data_live.py` `_is_live_environment_unavailable()` treats messages containing `stock_financial_hk_report_em` or `stock_financial_hk_analysis_indicator_em` as environment-unavailable.
- `quant/datahub/adapters/akshare.py` has the same classifier weakness for HK financial data.
- Independent review repro showed route-signature/schema/payload defects containing those route names return `True`, violating the original handoff requirement that route-signature, argument, schema, payload, and normalization defects remain hard failures.

This is a focused rework only. Do not redo TASK-117's broader HK financial implementation unless required to fix this classifier defect.

## Objective

Narrow the HK financial live/source-unavailability classifiers so only genuine network/proxy/DNS/TLS/upstream/public-source availability failures can become `SKIP` / source-unavailable, while repository-side route-signature, argument, schema, payload, contract, and normalization defects remain hard failures even when the exception message contains an AKShare route name.

## Required Reads

Execution must read:

- `AGENTS.md`
- `coordination/handoffs/TASK-117_DATAHUB_HK_FINANCIAL_BREADTH_HISTORY_HARDENING.md`
- `coordination/handoffs/TASK-117_DATAHUB_HK_FINANCIAL_LIVE_CLASSIFIER_REWORK.md`
- `coordination/reports/TASK-117_REPORT.md`
- `coordination/reviews/TASK-117_REVIEW.md`
- `quant/datahub/adapters/akshare.py`
- `tests/datahub/test_akshare_hk_financial_data_live.py`
- `tests/datahub/test_akshare_hk_financial_data_adapter.py`

Read other DataHub files only if needed to understand the classifier helper already used by these files.

## Allowed Writes

Only:

- `quant/datahub/adapters/akshare.py`
- `tests/datahub/test_akshare_hk_financial_data_live.py`
- `tests/datahub/test_akshare_hk_financial_data_adapter.py`
- `coordination/reports/TASK-117_REPORT.md`

If a tightly related shared DataHub test must change, document the exact reason in the report. Do not touch source-capability or source-catalog wording in this rework unless the classifier fix proves an existing TASK-117 claim false.

## Forbidden Changes

Do not modify:

- `AGENTS.md`
- controller-owned coordination files other than `coordination/reports/TASK-117_REPORT.md`
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

- Fix both classifier paths identified by Review:
  - the HK financial classifier in `quant/datahub/adapters/akshare.py`
  - `_is_live_environment_unavailable()` in `tests/datahub/test_akshare_hk_financial_data_live.py`
- Classify only genuine environment/source availability conditions as unavailable, such as network timeout, proxy error, DNS/name-resolution failure, connection reset/refused, SSL/TLS transport failure, HTTP upstream availability errors, remote disconnects, and explicitly empty/unavailable public-source responses where the adapter already treats the route as unavailable.
- Do not classify merely because an exception message contains:
  - `stock_financial_hk_report_em`
  - `stock_financial_hk_analysis_indicator_em`
  - `Eastmoney`
  - `AKShare`
  - a provider or route name without a genuine availability symptom
- Ensure these examples remain hard failures, not skips/source-unavailable:
  - route-name-bearing `TypeError` / signature / argument compatibility errors
  - route-name-bearing schema or missing-column errors
  - route-name-bearing payload-shape errors
  - route-name-bearing normalization or contract validation errors
  - route-name-bearing `ValueError` / `RuntimeError` messages that describe repository-side parsing or validation defects
- Preserve existing genuine network/upstream skip behavior for live smokes.
- Keep all default tests offline-safe and preserve `QUANT_SYSTEM_LIVE_TESTS=1` gating.
- Do not promote `hk_financial_data` or change capability status as part of this classifier-only rework.

## Required Tests

Run:

- `python3 -m unittest tests/datahub/test_akshare_hk_financial_data_adapter.py`
- `env -u QUANT_SYSTEM_LIVE_TESTS python3 -m unittest -v tests/datahub/test_akshare_hk_financial_data_live.py`
- `QUANT_SYSTEM_LIVE_TESTS=1 python3 -m unittest -v tests/datahub/test_akshare_hk_financial_data_live.py`

Also run any narrower targeted test command used while developing the classifier regressions, and report it.

Default live smoke behavior must remain skipped unless `QUANT_SYSTEM_LIVE_TESTS=1` is set.

If the live-enabled smoke fails or skips because of network/proxy/DNS/TLS/upstream/source availability, diagnose the root cause and fix repository code/tests where feasible. Report PASS, SKIP, or FAIL truthfully with root-cause evidence; do not convert repository-side classifier defects into environment SKIP.

## Completion Report

Update `coordination/reports/TASK-117_REPORT.md` with a rework section that includes:

- files changed by this rework
- exact classifier behavior changed
- regression coverage proving route-name-bearing repository defects fail rather than skip
- tests run with PASS/SKIP/FAIL
- default network behavior
- live-enabled PASS/SKIP/FAIL result and root-cause evidence
- deviations from this rework handoff
- risks or follow-up tasks

## Completion Criteria

The rework is complete when:

- both HK financial classifiers no longer downgrade route-name-bearing signature/argument/schema/payload/normalization defects to environment `SKIP`;
- regression tests prove the classifier distinction;
- default tests remain offline-safe;
- live-enabled evidence is rerun and truthfully reported;
- TASK-117 remains within DataHub Phase 2.5-P scope with no downstream or paid/private changes.
